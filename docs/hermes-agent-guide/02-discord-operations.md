# Discord에서 안전하게 지시하기

Discord는 편리하지만 message가 언제 새 turn이 되고 언제 실행 중 agent를 중단하는지
모르면 작업을 잃기 쉽다. 가장 안전한 기본 운영법은 “작업 하나당 thread 하나,
후속 작업은 `/queue`, 실행 중 보정은 `/steer`”다.

## DM, channel, thread의 session

기본 동작은 다음과 같다.

- DM에서는 모든 message에 응답하며 DM별 session을 사용한다.
- server channel에서는 bot을 `@mention`해야 응답한다.
- regular channel의 mention은 기본적으로 새 thread를 만들고, 그 thread가 독립된
  session namespace가 된다.
- bot이 이미 참여한 thread에서는 기본적으로 다시 mention하지 않아도 응답한다.
- 같은 shared channel에서도 `group_sessions_per_user: true`가 기본이므로 사용자별
  transcript가 분리된다.

따라서 서로 다른 목적의 작업을 같은 thread에 계속 쌓지 않는다. 기존 history가 도움이
되지 않는 새 목적이라면 새 thread를 만들거나 `/new meaningful-name`을 사용한다.

여러 bot이 같은 thread에 있는 경우에는 각 bot이 모든 message에 반응하지 않도록
다음 설정을 고려한다.

```yaml
discord:
  require_mention: true
  thread_require_mention: true
```

Discord routing의 상세 동작은
[Discord 공식 가이드](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord/)에서
확인할 수 있다.

## 실행 중 message가 하는 일

기본 busy-input mode는 `interrupt`다. agent가 tool을 사용하는 동안 평문을 보내면 현재
operation을 멈추고 새 message를 처리할 수 있다. 실행 중 command가 종료되고 남은
tool call이 취소될 수 있으므로, 단순한 추가 설명도 평문으로 보내지 않는 편이 안전하다.

| 의도 | 사용할 명령 | 결과 |
|---|---|---|
| 현재 일이 끝난 뒤 다음 요청 실행 | `/queue <prompt>` 또는 `/q <prompt>` | 다음 turn까지 대기 |
| 현재 일을 멈추지 않고 방향 보정 | `/steer <prompt>` | 다음 tool call 뒤 현재 run에 주입 |
| 현재 일을 취소 | `/stop` | agent와 background process 중단 |
| 독립 작업을 동시에 실행 | `/background <prompt>` | 별도 session에서 실행 후 결과 전송 |

예:

```text
/steer 수정 범위는 src/auth/로 제한하고 migration은 건드리지 마.
```

```text
/queue 현재 수정이 끝나면 diff를 검토하고 관련 test 결과를 표로 요약해 줘.
```

평문 입력의 기본 동작 자체를 바꾸려면 profile의 `config.yaml`에 설정한다.

```yaml
display:
  busy_input_mode: queue  # queue | steer | interrupt
```

공유 server나 mobile 중심 운영에는 `queue`가 보수적인 기본값이다. 즉시 대화하며 방향을
자주 바꾸는 개인 개발 환경에는 `steer`가 편리하다.

## `/background`에 모든 맥락을 다시 적는다

background session은 main chat과 독립적이다. model, provider, toolset 설정은
이어받지만 현재 대화 history는 모른다. 다음처럼 “아까 말한 repository”라고 보내면
필요한 path와 완료 기준을 알 수 없다.

나쁜 예:

```text
/background 아까 이야기한 경쟁사도 같이 조사해 줘.
```

좋은 예:

```text
/background
목표: Acme, Beta, Gamma의 2026년 공개 가격을 비교한다.
자료: 각 회사의 공식 pricing page만 사용한다.
출력: 회사, plan, 월 가격, 제한, source URL 열이 있는 Markdown 표.
완료 조건: 세 회사 모두 확인하고 확인 날짜를 적는다.
금지: 로그인, 구매, 문의 form 제출.
```

background task는 끝나면 요청한 같은 chat으로 결과가 돌아온다. process restart를
견뎌야 하거나 사람이 중간에 comment해야 하는 일에는 Kanban을 쓴다.

## 자주 쓰는 slash command

| 명령 | 용도 |
|---|---|
| `/new [name]`, `/reset` | 새 history와 session 시작 |
| `/status` | session과 최근 실행 요약 |
| `/model` | 이미 설정한 provider·model 선택 |
| `/usage` | token, 추정 비용, context 상태 |
| `/queue`, `/steer`, `/stop` | busy agent 제어 |
| `/background` | 독립 비동기 작업 |
| `/agents` | 실행 중 agent와 task 조회 |
| `/diff [session|all]` | Git 변경 확인 |
| `/rollback` | filesystem checkpoint 조회·복구 |
| `/sessions`, `/resume` | 과거 session 검색·재개 |
| `/compress` | 긴 history 요약 |
| `/sethome` | cron과 알림을 받을 home channel 지정 |
| `/kanban ...` | durable board 조회·변경 |

전체 명령과 설치 버전의 정확한 형식은
[Slash Commands Reference](https://hermes-agent.nousresearch.com/docs/reference/slash-commands/)와
Discord의 `/` autocomplete로 확인한다. `/model`은 이미 인증한 provider만 바꿀 수 있다.
새 credential 등록은 server terminal에서 `hermes model`로 한다.

## 잘 실행되는 지시의 구조

긴 문장 하나보다 다음 일곱 필드를 쓰면 결과와 검증이 안정적이다.

```text
목표:
현재 상태와 입력:
작업 범위:
금지사항:
산출물:
검증:
승인이 필요한 행동:
```

예:

```text
목표: login API의 간헐적인 500 오류 원인을 찾고 수정한다.
현재 상태와 입력: repository는 /srv/acme-api, 오류 log는 첨부 파일에 있다.
작업 범위: src/auth와 관련 test. 먼저 재현한 뒤 최소 수정한다.
금지사항: production 접속, database migration 변경, dependency major update.
산출물: 수정된 파일, 원인 설명, 재현과 검증 command.
검증: 기존 test와 새 regression test를 실행한다.
승인이 필요한 행동: 외부 전송, deploy, secret 접근, 데이터 삭제 전에는 멈춰 묻는다.
```

모호한 표현을 줄인다. “잘 정리해 줘” 대신 파일 형식, 표의 열, 길이, 대상 독자,
source 기준, 완료 조건을 쓴다. destructive action이 아닌 작은 구현 판단은 스스로
선택하되, 선택과 이유를 결과에 기록하라고 지시하면 불필요한 왕복을 줄일 수 있다.

## 공유 Discord의 안전한 기본값

- `DISCORD_ALLOWED_USERS` 또는 `DISCORD_ALLOWED_ROLES`를 반드시 둔다.
- 자유 응답 channel은 전용 bot channel에만 지정한다.
- shared channel에서는 `group_sessions_per_user: true`를 유지한다.
- 일반 사용자에게 허용할 slash command를 제한하고 `/whoami`로 확인한다.
- attachment는 authorized user가 올린 것만 처리하되, secret이나 private data는
  task prompt에 직접 붙이지 않는다.
- progress가 너무 많으면 `display.tool_progress`를 `new` 또는 `off`로 낮춘다.

[← 1장](./01-mental-model.md) · [목차](./index.md) ·
[3장: 프로필·기억·지시를 분리하기 →](./03-profiles-and-instructions.md)
