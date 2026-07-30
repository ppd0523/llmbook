# 프로필·기억·지시를 분리하기

profile은 장기간 유지할 agent의 역할과 상태를 나누는 단위다. coding assistant와
personal assistant가 서로 다른 key, model, memory, skill, Discord bot을 가져야 한다면
profile을 나눈다. 단순히 대화 주제만 바꾸려면 새 session으로 충분하다.

## profile을 만들 기준

다음 중 하나라도 지속적으로 달라야 하면 별도 profile이 유용하다.

- agent의 역할과 communication style
- 사용하는 API key와 monthly budget
- 허용할 toolset과 skill
- 기본 project directory
- 기억해야 할 사용자·project 정보
- main model과 reasoning level
- Discord bot identity와 접근 사용자
- cron schedule과 proactive notification

일회성 작업, 같은 역할의 새 주제, history만 지우면 되는 대화에는 profile을 늘리지
않는다. profile이 많아지면 gateway, token, model cost, update와 관찰 대상도 늘어난다.

## 생성과 확인

```console
hermes profile create coder
coder setup
coder config set terminal.cwd /absolute/path/to/project
coder doctor
coder gateway install
coder gateway start
```

alias를 쓰지 않으려면 모든 command에 profile을 명시할 수 있다.

```console
hermes -p coder doctor
hermes -p coder chat
hermes -p coder gateway status
```

기존 profile의 config, credential, SOUL, skill을 출발점으로 삼으려면 clone을 사용한다.

```console
hermes profile create researcher --clone-from coder
```

clone 뒤에는 복사된 bot token과 권한을 그대로 쓰지 말고 새 역할에 맞게 검토한다.
각 profile gateway는 고유한 Discord bot token을 사용해야 한다. 같은 token을 두
profile에 넣으면 Hermes의 token lock이 두 번째 gateway를 막는다.

```console
hermes profile list
hermes profile show coder
hermes profile describe coder --text "Implements and tests code in the assigned project."
```

description은 사람이 profile을 이해하는 label일 뿐 아니라 Kanban decomposer가 적절한
assignee를 고를 때도 사용한다.

## profile, workspace, sandbox를 함께 설정한다

profile을 만들었다고 project 밖 접근이 막히지 않는다. 최소한 기본 작업 directory를
절대 경로로 고정한다.

```yaml
terminal:
  backend: local
  cwd: /srv/projects/acme
```

untrusted repository나 destructive tool을 다루는 profile은 local 대신 격리 backend를
검토한다.

```yaml
terminal:
  backend: docker
  docker_image: python:3.12-slim
```

profile은 “어떤 agent인가”, workspace는 “어디서 시작하는가”, sandbox는 “어디까지
접근 가능한가”를 결정한다. 세 가지를 각각 설정해야 한다.

## 지시는 목적에 맞는 위치에 둔다

지시 충돌을 막는 가장 좋은 방법은 모든 규칙을 한 파일에 쌓는 것이 아니라 책임을
분리하는 것이다.

| 정보 | 둘 위치 | 예 |
|---|---|---|
| 전역 정체성과 말투 | profile의 `SOUL.md` | 직설적이되 불확실성은 명시한다 |
| 사용자 취향 | `USER.md` memory | 답변은 한국어, command는 원문 유지 |
| 환경·workflow 사실 | `MEMORY.md` | CI는 GitHub Actions, package manager는 pnpm |
| project 규칙 | `.hermes.md` 또는 `AGENTS.md` | architecture, test command, 금지 path |
| 현재 작업 | Discord prompt | 이번 수정 범위, 산출물, 완료 조건 |
| 여러 agent의 작업 | Kanban task body·comment | assignee, dependency, handoff, retry 정보 |
| 임시한 말투 | `/personality` | 이번 session만 teacher mode |

`SOUL.md`는 identity와 style에 집중한다. repository path, port, build command 같은
project 정보는 project context에 둔다. Hermes는 project root에서 `.hermes.md` →
`AGENTS.md` → `CLAUDE.md` → `.cursorrules` 순서로 첫 일치 종류를 선택한다. 비슷한
규칙 파일을 여러 형식으로 중복하면 모두 합쳐질 것이라고 기대하면 안 된다.

상세 탐색 규칙은
[Context Files](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files/)에
정리되어 있다.

## memory의 용도와 한계

기본 persistent memory에는 두 종류가 있다.

- `USER.md`: 이름, timezone, communication preference, skill level 같은 사용자 정보
- `MEMORY.md`: 환경, convention, tool quirk, 완료된 작업처럼 agent가 기억할 사실

memory는 session 시작 시 system prompt에 snapshot으로 들어간다. session 도중 memory를
고쳐도 현재 prompt의 frozen snapshot은 즉시 바뀌지 않는다. 새 규칙을 확실히 적용하려면
새 session을 시작한다.

다음 정보는 memory에 저장하지 않는다.

- API key, password, access token
- 긴 log, raw dataset, source code 전체
- 한 번만 쓸 임시 path와 task detail
- 이미 `SOUL.md`나 project context에 있는 중복 지시
- 아직 확인되지 않은 추측

## 지시가 충돌할 때

충돌을 발견하면 더 강한 문구를 덧붙이는 방식으로 해결하지 않는다. 다음 순서로
정리한다.

1. 현재 작업을 멈추면 손실이 큰지 확인하고 필요하면 `/queue`로 정정 사항을 보낸다.
2. 충돌한 두 지시의 실제 위치를 찾는다. `SOUL.md`, context file, memory, session
   history, Kanban comment를 구분한다.
3. 장기 규칙과 이번 task 예외를 나눈다.
4. 같은 범위의 규칙은 한곳만 진실의 원본으로 남긴다.
5. 현재 prompt에 “이번 작업에서는 X가 Y를 대체한다”와 유효 범위를 명시한다.
6. `SOUL.md`, context, memory를 바꿨다면 `/new`로 새 session에서 다시 시작한다.
7. agent에게 적용된 규칙과 불확실한 충돌을 작업 전에 짧게 restate하라고 요청한다.

예:

```text
현재 우선 조건:
- 이번 작업에서만 output language는 영어다.
- repository의 AGENTS.md에 있는 test와 formatting 규칙은 계속 적용한다.
- 기존 대화의 “migration도 수정 가능” 지시는 철회한다.
- migration 변경이 필요하면 작업하지 말고 이유와 대안을 보고한다.
먼저 이 조건을 한 문단으로 다시 확인한 뒤 진행해 줘.
```

Hermes 자체의 safety block, tool restriction, 실제 filesystem 권한은 prompt로 해제할 수
없다. 반대로 `SOUL.md`의 “project 밖 파일을 보지 마”는 행동 지침이지 sandbox 보장이
아니다.

## profile 변경의 적용 시점

- `config.yaml`의 main model 변경은 새 session에 적용한다.
- `/model`은 현재 session에서 즉시 바꾸지만 prompt cache가 reset될 수 있다.
- `SOUL.md`와 memory 변경은 새 session에서 가장 명확하게 적용된다.
- gateway credential과 Discord routing 변경 뒤에는 gateway를 restart한다.
- dashboard의 profile switcher는 편집 대상을 고른다. “Set as active”는 이후 CLI와
  gateway의 sticky default를 바꾼다.

[Profiles 공식 문서](https://hermes-agent.nousresearch.com/docs/user-guide/profiles/)의
경고처럼 profile은 상태 경계이지 security boundary가 아니다.

[← 2장](./02-discord-operations.md) · [목차](./index.md) ·
[4장: 작업을 실행하고 큐잉하기 →](./04-task-execution-and-queues.md)
