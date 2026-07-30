# 여러 에이전트를 함께 운영하기

여러 agent 운영의 목표는 bot 수를 늘리는 것이 아니라 서로 다른 책임과 상태를
분리하는 것이다. 가장 관리하기 쉬운 기본 구조는 사용자가 orchestrator 한 곳에
요청하고, orchestrator가 Kanban에 specialist task를 만들며, specialist가 structured
handoff를 남기는 방식이다.

```text
사용자
  │
  ▼
orchestrator profile
  │  task 생성·dependency·검수
  ▼
공유 Kanban board
  ├─ researcher profile
  ├─ coder profile
  ├─ reviewer profile
  └─ writer profile
```

각 bot이 Discord에서 서로에게 mention을 보내 대화하게 만들면 message loop, 중복 실행,
context 손실, 비용 폭증을 통제하기 어렵다. agent 간 protocol은 Discord transcript보다
Kanban task, comment, dependency, result metadata처럼 구조화된 상태로 만든다.

## 역할은 겹치지 않게 설계한다

처음에는 네 역할이면 충분하다.

| profile | 책임 | 하지 않을 일 |
|---|---|---|
| `orchestrator` | task 분해, assignee 선택, dependency, 결과 검수 | 직접 구현 |
| `researcher` | source 수집, 사실 확인, evidence 정리 | 최종 주장 확정, 코드 수정 |
| `coder` | 구현, test, artifact 생성 | 요구사항 임의 확대, deploy |
| `reviewer` | 독립 검토, 위험·누락·regression 확인 | 원 구현을 몰래 다시 작성 |

문서 생산이 많다면 `writer`, 운영 automation이 많다면 `ops`를 추가한다. 역할 둘이 같은
최종 파일을 동시에 수정하게 하지 않는다. 한 artifact에는 한 명의 owner를 두고 다른
agent는 comment나 review task로 의견을 준다.

각 profile의 routing description은 짧고 관찰 가능하게 쓴다.

```console
hermes profile describe researcher --text \
  "Finds current primary sources and returns claims, dates, URLs, and uncertainty. Does not edit product code."

hermes profile describe coder --text \
  "Implements scoped repository changes, runs tests, and reports files and verification. Does not deploy."
```

“똑똑한 assistant”처럼 추상적인 description은 decomposer가 선택 근거로 쓰기 어렵다.

## profile마다 별도 상태와 gateway를 둔다

```console
hermes profile create orchestrator
hermes profile create researcher --clone-from orchestrator
hermes profile create coder --clone-from orchestrator
hermes profile create reviewer --clone-from orchestrator
```

clone은 시작점을 빠르게 만들지만 clone 이후 다음을 profile별로 다시 점검한다.

- 고유한 Discord bot token
- allowlist와 slash command admin
- `SOUL.md`와 `USER.md`
- toolset과 skill
- `terminal.cwd`와 terminal backend
- main·auxiliary·delegation model
- monthly cost·rate limit
- gateway service와 home channel

각 profile은 별도 gateway process를 실행한다.

```console
orchestrator gateway install
researcher gateway install
coder gateway install
reviewer gateway install

orchestrator gateway start
researcher gateway start
coder gateway start
reviewer gateway start
```

같은 Discord application을 여러 gateway가 공유하면 global slash command registration이
서로 덮일 수 있다. 불가피하게 공유한다면 하나만 command registration owner로 남기고
나머지는 `slash_commands: false`로 설정한다. 일반 운영에서는 profile마다 고유 bot
application과 token을 쓰는 편이 명확하다.

## orchestrator에는 routing tool만 준다

orchestrator가 모든 tool과 production credential을 가지면 specialist를 나눈 효과가
작아진다. 가능하면 Kanban, gateway status, 필요한 memory처럼 routing에 필요한
toolset만 준다. 구현 tool을 제거하면 orchestrator가 task를 직접 처리해 병목이 되는
문제를 구조적으로 줄일 수 있다.

반대로 worker가 다른 task를 임의 생성하거나 unrelated task를 바꾸지 않도록 역할
contract를 둔다. dispatcher가 시작한 Kanban worker에는 자신의 task를 읽고
complete·block·heartbeat·comment할 lifecycle guidance가 자동으로 주입된다.

## dependency로 순서, profile로 책임을 표현한다

예를 들어 두 지역 조사를 병렬 실행하고 writer가 합치며 reviewer가 마지막에 검토하는
pipeline은 다음 graph다.

```text
research-na ─┐
             ├─> writer ─> reviewer
research-eu ─┘
```

```console
hermes kanban create "Research North America market" --assignee researcher
hermes kanban create "Research Europe market" --assignee researcher
hermes kanban create "Write market comparison" --assignee writer \
  --parent t_na --parent t_eu
hermes kanban create "Review claims and citations" --assignee reviewer \
  --parent t_write
```

실제 `t_na`, `t_eu`, `t_write` 대신 앞 command가 반환한 task ID를 사용한다. parent가
done 되기 전 child를 강제로 ready로 만들면 빠르기는 해도 handoff가 빠진 상태로
실행될 수 있다.

## handoff를 결과의 일부로 본다

작업 완료 summary에 “done”만 남기지 않는다.

```text
Summary:
- 결론 또는 변경 내용

Artifacts:
- 파일 path, branch, URL, report

Verification:
- 실행한 test와 결과
- source 확인 날짜

Decisions:
- 선택한 대안과 제외한 대안

Open risks:
- 해결하지 않은 문제와 영향

Next agent:
- 다음 작업에 필요한 입력과 주의사항
```

다음 worker는 parent task의 handoff와 comment를 읽고 시작한다. raw log, secret,
긴 transcript를 metadata에 넣지 말고 artifact path와 요약을 남긴다.

## workspace 충돌을 막는다

두 coder가 같은 working tree를 동시에 수정하면 한쪽의 uncommitted change를 덮거나
검증 결과를 섞을 수 있다.

- 읽기 전용 research는 같은 directory를 공유할 수 있다.
- code 변경은 task별 Git worktree 또는 scratch workspace를 쓴다.
- database, port, build cache처럼 filesystem 밖의 resource도 task별로 분리한다.
- 하나의 branch와 deploy environment에는 한 번에 한 owner만 둔다.
- reviewer는 가능하면 구현과 분리된 clean workspace에서 결과를 검증한다.

Kanban task는 `scratch`, `worktree`, `dir:<path>` 같은 workspace 종류를 지정할 수 있다.
repository 변경에는 worktree를 우선 검토한다.

```console
hermes kanban create "Implement auth retry" \
  --assignee coder \
  --workspace worktree \
  --branch auth-retry
```

## concurrency와 비용을 함께 제한한다

동시에 실행 가능한 agent 수를 늘리면 wall-clock time은 줄 수 있지만 API rate limit,
token cost, CPU·memory, shared test resource 경쟁이 늘어난다.

처음에는 다음처럼 보수적으로 시작한다.

- orchestrator 1
- 동시에 실행하는 researcher 2
- repository별 coder 1
- result가 나온 뒤 reviewer 1
- delegation concurrency 기본값을 유지하고 실제 quota를 관찰

task 분해가 너무 잘면 main context 절약보다 handoff overhead가 더 커진다. 독립적으로
완료하고 검증할 수 있는 단위만 나눈다.

## 다중 agent의 공유 범위

profile의 memory와 session은 분리되지만 Kanban board는 의도적으로 profile 간 공유다.
board의 task body, comment, workspace path를 모든 profile이 볼 수 있다고 가정한다.
서로 다른 고객이나 security domain을 강하게 나눠야 한다면 tenant label만 믿지 말고
별도 OS account, host, container 또는 board와 credential boundary를 설계한다.

[← 4장](./04-task-execution-and-queues.md) · [목차](./index.md) ·
[6장: 작업에 맞는 provider와 model 고르기 →](./06-provider-and-model-selection.md)
