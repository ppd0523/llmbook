# 운영 레시피와 문제 해결

처음부터 많은 profile과 model을 만들지 않는다. 한 개의 안전한 Discord assistant로
session과 queue를 익힌 뒤, 반복되는 역할만 profile과 Kanban으로 분리한다.

## 레시피 1: 개인용 Discord assistant

목표는 한 bot으로 research, file 작업, reminder를 하되 대화가 서로 섞이지 않게 하는
것이다.

1. Discord allowlist에 자신만 넣는다.
2. server의 `#hermes` channel에서 mention하면 auto-thread가 만들어지는 기본값을 쓴다.
3. 작업 하나당 thread 하나를 쓴다.
4. busy input mode는 `queue`로 둔다.
5. 일반 작업은 foreground, 5분 이상 독립 작업은 `/background`로 보낸다.
6. 반복 reminder는 `/cron`, 오래 남겨야 할 project work는 Kanban으로 옮긴다.
7. 주 1회 `/usage`, gateway status, cron list를 확인한다.

권장 시작 설정:

```yaml
group_sessions_per_user: true

display:
  busy_input_mode: queue
  tool_progress: new

approvals:
  mode: smart
  cron_mode: deny
```

## 레시피 2: coding team

profile은 `orchestrator`, `coder`, `reviewer` 세 개로 시작한다.

- orchestrator: 요구사항을 acceptance criterion과 task graph로 바꾼다.
- coder: task별 worktree에서 구현하고 test한다.
- reviewer: 다른 model family로 diff, test, security risk를 검토한다.

작업 흐름:

```text
요청
  → orchestrator가 구현 task 생성
  → coder가 worktree에서 수정·test·handoff
  → reviewer가 parent result와 diff 검토
  → 문제가 있으면 comment와 follow-up task
  → 사람이 merge·deploy 승인
```

orchestrator에게 보낼 지시:

```text
이 요구사항을 Kanban으로 운영해.
1. 구현과 review를 별도 task로 만든다.
2. review는 구현 완료 뒤 ready가 되게 dependency를 연결한다.
3. 구현은 task 전용 Git worktree를 쓴다.
4. coder는 변경 파일, test, open risk를 handoff한다.
5. reviewer는 요구사항 충족, regression, security를 독립 확인한다.
6. merge, push, deploy는 하지 말고 승인 대기 상태로 끝낸다.
```

## 레시피 3: research와 writing pipeline

`researcher-a`, `researcher-b`, `writer`, `fact-checker`를 사용한다. 두 researcher에게
같은 질문을 중복시키기보다 source 범위나 관점을 나눈다.

- researcher-a: official·primary source, 현재 사실과 날짜
- researcher-b: 반대 evidence, limitation, historical comparison
- writer: 두 handoff만 사용해 독자 맞춤 draft
- fact-checker: claim마다 source와 날짜를 다시 확인

Kanban body에 source policy를 넣는다.

```text
Primary sources first.
Every time-sensitive claim must include source URL and checked date.
Separate verified facts, inference, and unknowns.
Do not quote more than necessary.
Do not publish; return a Markdown draft for approval.
```

writer task는 두 research task를 parent로, fact-check task는 writer를 parent로 둔다.

## 레시피 4: model cost를 단계적으로 줄이기

1. main model을 바꾸지 않고 `/usage` baseline을 모은다.
2. title generation과 web extraction을 fast auxiliary model로 옮긴다.
3. compression을 fast model로 옮기고 constraint 보존을 test한다.
4. delegation의 단순 research·formatting을 중간 tier로 낮춘다.
5. 실패율, retry, human correction이 늘지 않았는지 비교한다.
6. 그 뒤에만 high-volume profile의 main model을 조정한다.

한 번에 모두 바꾸면 어느 변경이 품질 저하를 만들었는지 알 수 없다.

## 증상별 진단

| 증상 | 먼저 볼 것 | 흔한 원인 | 조치 |
|---|---|---|---|
| bot이 online인데 답하지 않음 | gateway log, `/start` | Message Content Intent, allowlist 없음 | intent·access policy 확인 후 restart |
| channel message를 무시함 | mention, allowed channel | server channel은 기본 mention 필요 | `@bot` 또는 전용 free-response channel |
| thread에서 여러 bot이 동시에 답함 | `thread_require_mention` | 참여한 bot이 thread message에 계속 응답 | multi-bot thread에서 `true` |
| 새 message 뒤 기존 작업이 사라짐 | busy input mode | 평문이 default interrupt | `/queue`, `/steer`, `busy_input_mode: queue` |
| background가 맥락을 모름 | background prompt | 별도 session이라 history 없음 | path·입력·출력·완료 조건 재작성 |
| profile이 다른 project를 수정함 | `terminal.cwd`, backend | profile을 sandbox로 오해 | 절대 cwd와 container·remote isolation |
| `SOUL.md` 수정이 안 보임 | session 시작 시점 | 기존 session prompt 사용 | `/new`, 필요하면 gateway restart |
| 서로 다른 사용자의 대화가 섞임 | `group_sessions_per_user` | shared room session 사용 | 기본값 `true` 복구 |
| Kanban task가 ready에서 멈춤 | gateway status, dispatcher | gateway 중지, 잘못된 assignee | gateway 시작, profile·description 확인 |
| task가 반복 block됨 | comment와 dependency | 입력·capability·workspace 미해결 | 원인 해결 후 unblock |
| 여러 coder 변경이 충돌함 | workspace와 branch | 같은 tree·resource 공유 | task별 worktree와 owner 지정 |
| `/model`에 provider가 없음 | credential | 아직 인증하지 않음 | terminal에서 `hermes model` |
| model 변경 후 비용 급증 | `/usage`, context | prompt cache reset, 긴 history | 새 session에서 model 선택 |
| slash command가 계속 바뀜 | gateway config | 같은 app을 여러 gateway가 등록 | primary 한 곳만 registration |
| cron이 project 규칙을 모름 | job workdir | repo 밖에서 실행 | absolute `--workdir` 설정 |
| dangerous command가 cron에서 막힘 | approval log | `cron_mode: deny` | read-only workflow로 수정, 좁은 API 사용 |

## 작업 시작 전 30초 점검

- 이 일은 기존 session의 후속인가, 새 thread가 필요한가?
- 현재 agent가 바쁜가? 평문 대신 `/queue`나 `/steer`가 필요한가?
- foreground, background, delegation, Kanban, cron 중 어느 수명이 필요한가?
- profile과 `terminal.cwd`가 맞는가?
- 입력과 source of truth가 명시되어 있는가?
- output 형식과 완료 조건이 관찰 가능한가?
- 삭제, 외부 전송, deploy, secret 접근의 승인선이 있는가?
- 병렬 task가 같은 file·branch·database를 공유하지 않는가?
- 이 task의 실패 비용에 main model이 충분한가?
- 완료 뒤 file·test·URL·risk handoff를 요구했는가?

## 매주 운영 점검

```console
hermes profile list
hermes gateway status
hermes kanban diagnostics
hermes kanban list
hermes cron list
hermes approvals suggest
hermes doctor
```

profile별 gateway는 profile alias나 `-p`로 각각 확인한다. `approvals suggest`는
proposal을 읽는 용도로 먼저 실행하고, permanent allowlist 반영은 별도로 판단한다.

## 참고 자료

- [Hermes Agent Documentation](https://hermes-agent.nousresearch.com/docs/)
- [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord/)
- [Slash Commands Reference](https://hermes-agent.nousresearch.com/docs/reference/slash-commands/)
- [Profiles](https://hermes-agent.nousresearch.com/docs/user-guide/profiles/)
- [Context Files](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files/)
- [Subagent Delegation](https://hermes-agent.nousresearch.com/docs/user-guide/features/delegation)
- [Kanban](https://hermes-agent.nousresearch.com/docs/user-guide/features/kanban)
- [Scheduled Tasks](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron/)
- [Configuring Models](https://hermes-agent.nousresearch.com/docs/user-guide/configuring-models)
- [AI Providers](https://hermes-agent.nousresearch.com/docs/integrations/providers)
- [Security](https://hermes-agent.nousresearch.com/docs/user-guide/security/)

[← 7장](./07-security-cost-reliability.md) · [목차](./index.md)
