# 작업을 실행하고 큐잉하기

Hermes에서 “큐에 넣는다”는 말은 세 가지를 뜻할 수 있다. `/queue`는 같은 세션의 다음
차례, `/background`는 별도 비동기 세션, Kanban은 여러 프로필이 공유하는 내구성 작업
큐다. 여기에 위임(delegation), 지속 목표, cron까지 구분해야 작업의 수명과 결과
전달 방식을 예측할 수 있다.

## 선택표

| 질문 | 그렇다면 |
|---|---|
| 현재 답변 뒤 바로 이어서 할 일인가? | `/queue` |
| 현재 실행을 취소하지 않고 보정할 내용인가? | `/steer` |
| main chat과 독립적으로 한 번 실행하면 되는가? | `/background` |
| 요청한 대화가 결과를 받아 종합할 짧은 subtask인가? | delegation |
| 완료까지 여러 turn을 자동 반복해야 하는 한 목표인가? | `/goal` |
| restart 후에도 남고 역할 간 전달·comment·retry가 필요한가? | Kanban |
| 정해진 시각이나 주기로 다시 실행해야 하는가? | cron |

## `/queue`: 같은 세션의 다음 실행 차례

```text
/queue 이 작업이 끝나면 변경된 파일 목록과 test 결과를 요약해 줘.
```

실행 차례(turn)는 사용자 입력 하나를 받아 에이전트가 응답을 마칠 때까지의 단위다.
현재 실행(run)은 그대로 끝나고 대기시킨 프롬프트가 다음 사용자 차례로 실행된다. 이전
결과를 이어받아야 하는 순차 작업에 적합하다. 서버 전체에 남는 내구성 작업 보드는
아니므로 게이트웨이나 세션 수명보다 오래 보존해야 하는 업무에는 쓰지 않는다.

## `/steer`: 현재 실행의 방향 수정

```text
/steer 성능보다 backward compatibility를 우선해. public API signature는 바꾸지 마.
```

현재 tool 하나가 끝난 뒤 note가 agent context에 들어간다. 새 turn을 만들지 않고 현재
계획을 보정한다. 이미 실행 중인 destructive command를 되돌리는 stop button은 아니므로
긴급 중단에는 `/stop`을 쓴다.

## `/background`: 주 대화를 비우는 독립 작업

```text
/background repository /srv/app에서 전체 test suite를 실행하고 실패를 원인별로 묶어 줘.
파일은 수정하지 말고 결과만 이 channel로 보내.
```

background는 같은 프로필의 모델, 제공자, 도구 모음을 쓰지만 별도 세션이고 현재 대화
이력을 받지 않는다. 프롬프트만 읽어도 이해되게 작성한다. 결과는 요청한 chat으로
돌아온다.

## 위임: 새 맥락의 하위 에이전트에게 맡기기

사용자는 자연어로 병렬화를 요청할 수 있다.

```text
공식 source만 사용해 세 경쟁사의 가격, security certification, API 제한을 각각
독립 subagent에게 병렬 조사시킨 뒤 하나의 비교표로 합쳐 줘.
각 subagent에게 회사명, 확인 날짜, 필요한 표의 열을 모두 전달해.
```

위임된 하위 에이전트는 부모의 대화를 모른다. 전달받은 `goal`과 `context`만 사용하므로
경로, 오류, 완료 조건을 명시해야 한다. 하위 에이전트는 부모의 활성 도구 모음을
물려받지만 권한을 스스로 확대하지 못하며, 사용자에게 질문하거나 공유 기억에 쓰는
등의 일부 동작은 제한된다.

위임(delegation)은 부모 에이전트가 대화 이력을 공유하지 않는 하위 에이전트에게 한시적
하위 작업을 맡기고 최종 요약을 돌려받는 실행 방식이다. 다음 조건에서 좋다.

- 서로 독립적인 research나 review를 동시에 할 수 있다.
- 중간 tool output이 부모 context를 오염시키지 않아야 한다.
- fresh perspective가 필요하다.
- 최종 summary만 부모가 받아 종합하면 된다.

최상위 `delegate_task`는 실행을 추적할 식별자(handle)를 즉시 돌려주고 완료 결과를 나중에 원래 대화로
보낼 수 있다. 일반 후속 메시지는 진행 중인 child를 취소하지 않지만 `/stop`, 소유
세션의 종료·초기화, Hermes process 재시작은 진행 중 실행을 취소하거나 상태를 알 수
없게 만들 수 있다. 즉, “비동기”이지만 “재시작을 견디는 내구성 작업”은 아니다.

재시작을 견뎌야 하거나, 사람이 중간 comment를 달거나, 이름 있는 specialist가 이어서
작업해야 하면 Kanban으로 올린다. 자세한 제약은
[Subagent Delegation](https://hermes-agent.nousresearch.com/docs/user-guide/features/delegation)을
참조한다.

## `/goal`: 한 목표를 여러 차례 자동 계속하기

```text
/goal 인증 오류를 재현하고 최소 수정과 regression test까지 완료해.
```

`/goal`은 한 세션에서 완료 조건을 향해 여러 차례 자동으로 계속할 때 쓴다. 각 차례가
끝날 때 보조 모델이 목표 완료 여부를 판단하고, 미완료라면 다음 차례를 시작한다.
`/goal status`, `/goal pause`, `/goal resume`, `/goal clear`로 상태를 제어한다.

지속 목표는 내구성 작업 큐가 아니다. 다른 프로필에 넘길 일, 사람이 검토해야 할 일,
재시작 뒤에도 감사 이력과 재시도가 남아야 할 일은 Kanban task로 만든다. 목표 문장에는
“완료”를 판정할 수 있는 테스트·파일·보고서 같은 증거를 반드시 넣는다.

## Kanban: 재시작 뒤에도 남는 작업 큐

Kanban은 여러 프로필이 공유하는 내구성 작업 보드다. 프로필과 독립적으로 호스트의
보드 데이터베이스에 작업, 상태, 의존 관계, 댓글, 실행 시도, 인계 기록을 저장한다.

### Kanban에서 쓰는 말

- **보드(board)**: 작업과 상태 이력을 담는 전체 작업판이다.
- **작업(task)**: 목표, 입력, 담당자, 완료 조건을 담은 실행 단위다.
- **담당자(assignee)**: 해당 작업을 실행할 프로필 또는 worker lane이다.
- **의존 관계(dependency)**: 먼저 끝나야 하는 부모 작업과 그 결과를 기다리는 자식
  작업의 선후 관계다.
- **디스패처(dispatcher)**: 실행 가능한 작업을 찾아 담당 프로필의 worker process를
  시작하는 게이트웨이 내부 반복 실행부다.
- **인계(handoff)**: 다음 작업자나 검토자가 재조사하지 않도록 남기는 결과와 검증
  증거다.
- **heartbeat**: 긴 작업이 멈추지 않고 진행 중임을 보드에 알리는 생존 신호다.
- **재시도(retry)**: 실패 원인을 보완한 뒤 같은 작업을 다시 실행하는 시도다.

기본 보드를 시작하는 최소 흐름은 다음과 같다.

```console
hermes kanban init
hermes gateway start
hermes kanban create "Research API authentication options" --assignee researcher
hermes kanban watch
```

Discord에서도 같은 board를 다룬다.

```text
/kanban create "Research API authentication options" --assignee researcher
/kanban list
/kanban show t_abcd
/kanban comment t_abcd "Use the 2026 API, not the legacy endpoint."
```

gateway에서 만든 task는 그 chat이 terminal event를 구독하므로 complete, blocked,
crashed 같은 결과가 같은 곳으로 돌아온다. 기본 dispatcher는 gateway 안에서
주기적으로 ready task를 찾아 worker profile을 실행한다. gateway가 멈추면 task는
사라지지 않고 ready 상태에서 기다린다.

### 좋은 Kanban task

title 하나만 쓰지 말고 body에 다음 내용을 둔다.

```text
Goal:
Inputs and source of truth:
Scope:
Out of scope:
Deliverables:
Verification:
Dependencies:
Approval boundary:
Handoff metadata:
```

worker가 완료할 때는 다음 profile이 다시 조사하지 않도록 structured handoff를 남긴다.

- 무엇을 바꿨는가
- 어떤 file·URL·artifact가 결과인가
- 무엇으로 검증했는가
- 실패하면 어떻게 retry·unblock하는가
- 어떤 risk를 의도적으로 남겼는가

검토가 필요한 task는 구현자가 바로 최종 완료로 닫지 않고 review를 요청할 수 있다.

```console
hermes kanban request-review t_abcd --reviewer reviewer \
  --summary "Implementation complete; tests pass."
```

reviewer는 승인하면 complete하고, 수정이 필요하면 `request-changes`로 요구사항을
구체적으로 돌려보낸다. 이렇게 하면 “구현 완료”와 “검토 승인”이 같은 상태로 섞이지
않는다.

task 간 선후 관계는 parent link로 표현한다. child는 모든 parent가 done이 된 뒤
`ready`가 된다.

```console
hermes kanban create "Research North America" --assignee researcher-na
hermes kanban create "Research Europe" --assignee researcher-eu
hermes kanban create "Write comparison" --assignee writer --parent t_na --parent t_eu
```

실제 ID를 변수처럼 추측해 쓰지 말고 create 결과를 복사한다. 전체 명령은
[Kanban 공식 문서](https://hermes-agent.nousresearch.com/docs/user-guide/features/kanban)에
있다.

## cron: 시간이 작업을 시작하게 한다

cron은 정해진 시각이나 주기에 명령을 실행하는 시간 기반 스케줄러다. 반복 업무는
대화에서 매번 요청하지 말고 cron job으로 만든다.

```console
hermes cron create "every 1d at 09:00" \
  "공식 status page와 어제의 incident를 확인해 운영 요약을 작성한다." \
  --workdir /absolute/path/to/ops-repo
```

cron job에 `workdir`가 없으면 project의 `AGENTS.md`가 자동으로 적용될 것이라고 기대하면
안 된다. project context와 file tool이 필요하면 존재하는 절대 경로를 지정한다.
unattended task의 destructive command는 기본 `approvals.cron_mode: deny`에서 막힌다.
안전 때문에 막힌 command를 무조건 auto-approve하기보다 job을 read-only로 설계하거나
좁은 API를 제공한다.

## 작업이 막혔을 때

- 현재 run에 정보만 보태려면 `/steer`를 쓴다.
- Kanban worker가 질문을 남겼다면 task에 comment하고 unblock한다.
- dependency가 안 끝났다면 강제 완료하지 말고 parent 상태를 고친다.
- 같은 원인으로 반복 block되면 입력, 기능, 작업 공간, 담당자가 맞는지
  수정한 뒤 retry한다.
- 단순히 느리다는 이유로 같은 task를 중복 생성하지 않는다. automation에서는
  idempotency key를 사용한다.

## 4장 확인 문제

- `/background`와 delegation은 모두 비동기로 보일 수 있는데, 각각 누가 결과를
  종합하는가?
- 실행 중인 작업에 제약을 추가하는 일과 다음 작업을 예약하는 일은 어떤 명령으로
  구분하는가?
- 재시작 뒤에도 작업 본문·의존성·검토 이력이 남아야 한다면 무엇을 써야 하는가?

[← 3장](./03-profiles-and-instructions.md) · [목차](./index.md) ·
[5장: 여러 에이전트를 함께 운영하기 →](./05-multi-agent-operations.md)
