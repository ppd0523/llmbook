# 보안·비용·신뢰성 운영

Discord에 연결한 Hermes는 authorized user의 말에 따라 terminal과 file tool을 실행할
수 있다. 일반 chat bot의 권한 모델로 운영하면 안 된다. 누가 말할 수 있는지, 어떤
command가 승인 대상인지, 어느 filesystem과 network에 접근하는지, 얼마까지 지출할지를
각각 제한한다.

## Discord 접근은 fail-closed로 시작한다

가장 작은 allowlist를 쓴다.

```dotenv
DISCORD_BOT_TOKEN=replace-with-secret
DISCORD_ALLOWED_USERS=111222333444555666
```

team이 role로 관리된다면 `DISCORD_ALLOWED_ROLES`를 쓸 수 있다. `ALLOW_ALL` 계열은
terminal 접근이 없는 폐쇄형 test bot이 아니라면 피한다. bot token과 API key는
Discord message, Kanban body, log snippet, repository에 넣지 않는다.

허용된 사용자 중에서도 admin과 regular user의 slash command 권한을 나눈다. regular
user에게 model switch, destructive session reset, admin integration command가
필요한지 검토한다. 각 사용자는 `/whoami`로 자신의 scope와 tier를 확인한다.

## command approval을 끄지 않는다

기본 smart approval은 low-risk command를 auxiliary model로 평가하고 위험하거나
불확실한 경우 거부·확인을 요청한다.

```yaml
approvals:
  mode: smart       # smart | manual | off
  timeout: 300
  cron_mode: deny
```

- `smart`: 일반 운영의 기본값
- `manual`: 위험 pattern마다 사람이 판단해야 하는 고위험 환경
- `off`: safety prompt를 끄므로 격리된 disposable environment에서만 검토

“Always approve”를 습관적으로 누르면 allowlist가 넓어진다. `hermes config edit`와
`hermes approvals suggest`의 read-only proposal로 누적 규칙을 주기적으로 검토한다.
recursive delete, force push, system service 변경, credential edit 같은 destructive
class는 반복 작업이어도 영구 허용하지 않는 편이 안전하다.

## profile과 write guard의 한계를 안다

profile은 sandbox가 아니다. 또한 Hermes의 protected-path와 write-safe-root 검사는
주로 `write_file`과 `patch`에 적용된다. local terminal command는 같은 OS user 권한으로
동작할 수 있으므로 untrusted prompt나 repository를 강하게 격리하려면 container·remote
backend가 필요하다.

운영 경계는 다음 순서로 강해진다.

1. task prompt의 금지사항
2. profile의 toolset 제한
3. command approval과 deny pattern
4. filesystem write-safe-root
5. Docker·SSH·cloud sandbox
6. 별도 OS account·host·network policy

상위 항목은 model의 협조에 의존하고, 아래로 갈수록 실제 execution boundary에 가깝다.

## 외부 side effect에는 명시적 승인선을 둔다

다음 행동은 task instruction에 “실행 전 멈춰 확인”이라고 적는다.

- email, Discord post, issue·PR comment처럼 타인에게 message 전송
- purchase, subscription, booking, form submit
- deploy, release, production restart
- 데이터 삭제·migration·permission 변경
- secret·private document 접근
- public repository push나 force operation

draft 작성과 실제 전송을 별도 task로 나누면 승인 지점이 명확해진다. Kanban에서는
draft task를 done으로 만들고 승인 뒤 publish task를 unblock한다.

## 비용을 관찰 가능한 값으로 만든다

비용은 model 단가뿐 아니라 context 재전송, reasoning token, 실패 retry, subagent 수,
web·browser tool 사용에서 발생한다.

- `/usage`로 session token과 추정 비용을 확인한다.
- 긴 session을 주제별 thread로 나눠 불필요한 history를 줄인다.
- `/compress` 뒤 중요한 constraint가 남았는지 확인한다.
- main model switch는 prompt cache를 reset할 수 있으므로 왕복을 줄인다.
- title, compression, approval, web extract는 auxiliary model로 옮긴다.
- 병렬 agent 수와 task별 retry·runtime limit를 제한한다.
- cron과 Kanban automation에는 명확한 budget과 idempotency key를 둔다.
- profile별 provider account·key를 분리하면 역할별 usage를 추적하기 쉽다.

가장 싼 model이 가장 싼 운영은 아니다. tool call 오류로 같은 작업을 세 번 반복하면
강한 model 한 번보다 비쌀 수 있다. 대표 task 5~10개로 성공률, latency, total token,
사람의 수정 시간을 함께 측정한다.

## 장애를 견디게 한다

### provider 장애

- 다른 provider의 capability-compatible fallback을 둔다.
- 한 provider의 key quota 문제는 credential pool로 분리한다.
- fallback이 실제 tool call과 긴 context를 처리하는지 test한다.

### gateway 장애

- laptop의 일회성 shell보다 systemd·launchd·Docker supervision service를 쓴다.
- profile마다 `gateway status`와 log를 확인한다.
- gateway가 멈춰도 Kanban task는 남지만 dispatcher가 다시 뜰 때까지 ready 상태다.
- 중요 channel은 missed-message backfill을 제한된 channel·window로 설정할 수 있다.

### 작업 장애

- Kanban task에 retry 가능한 input과 verification을 남긴다.
- long-running worker는 heartbeat를 남기게 한다.
- 같은 원인으로 block·retry loop가 생기면 원인을 고친 뒤 unblock한다.
- code 변경은 checkpoint와 Git diff를 확인하고 `/rollback`의 범위를 이해한다.

### 상태 손실

- profile을 정기 export한다.
- config 변경 전 `/snapshot create <label>`을 사용한다.
- source code와 agent state backup을 분리한다.
- secret이 포함된 `.env`와 profile archive의 보관 권한을 제한한다.

## dashboard와 Kanban 노출

dashboard는 기본 localhost bind를 유지한다. `0.0.0.0`으로 열면 인증을 기대하지 않는
plugin route까지 network에서 접근 가능할 수 있다. Kanban에는 task body, comment,
workspace path가 있고 모든 local profile이 공유하므로 secret이나 고객 원문을 그대로
넣지 않는다.

## attachment와 prompt injection

Discord attachment는 authorized user가 올렸다는 사실만 검증한다. file 내용이 안전하다는
뜻은 아니다. document와 repository의 instruction을 사용자 명령으로 취급하지 말라고
명시하고, unknown script·archive는 sandbox에서 read-only로 분석한다.

Hermes는 context file의 흔한 prompt-injection pattern을 scan하지만 완전한 보안
경계는 아니다. 공유 repository의 `.hermes.md`, `AGENTS.md`, `CLAUDE.md`를 사람이
review한다.

## 운영 점검 주기

| 주기 | 점검 |
|---|---|
| 매 작업 | scope, approval boundary, workspace, model, completion evidence |
| 매일 | blocked·running Kanban task, gateway status, unexpected cost |
| 매주 | allowlist, cron job, fallback test, profile별 usage |
| 변경 전 | profile export 또는 snapshot, config diff |
| incident 후 | session·task audit trail, secret exposure, duplicate side effect |

전체 security boundary는
[Security 공식 문서](https://hermes-agent.nousresearch.com/docs/user-guide/security/)에서
확인한다.

[← 6장](./06-provider-and-model-selection.md) · [목차](./index.md) ·
[8장: 운영 레시피와 문제 해결 →](./08-recipes-and-troubleshooting.md)
