---
title: 조사 노트
version: 1.0
status: complete
owner: agent
updated: 2026-07-30
target_reader: Hermes Agent를 Discord 중심으로 처음 운영하는 사용자
topic: Hermes Agent 운영 가이드
---

# 조사 노트

## 핵심 출처

| 공식 문서 | 사용할 내용 |
|---|---|
| [Features Overview](https://hermes-agent.nousresearch.com/docs/user-guide/features/overview) | 도구, memory, context, automation의 전체 범위 |
| [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord/) | session, thread, mention, allowlist, model picker, attachment |
| [Slash Commands](https://hermes-agent.nousresearch.com/docs/reference/slash-commands/) | `/queue`, `/steer`, `/background`, `/model`, 상태·복구 명령 |
| [Profiles](https://hermes-agent.nousresearch.com/docs/user-guide/profiles/) | profile 격리 범위, 고유 token, gateway, workspace와 sandbox 차이 |
| [Context Files](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files/) | `SOUL.md`, `.hermes.md`, `AGENTS.md`, 우선 탐색 순서 |
| [Persistent Memory](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory/) | `MEMORY.md`, `USER.md`, session 시작 시 snapshot |
| [Subagent Delegation](https://hermes-agent.nousresearch.com/docs/user-guide/features/delegation) | fresh context, inherited tools, concurrency와 제약 |
| [Kanban](https://hermes-agent.nousresearch.com/docs/user-guide/features/kanban) | durable task board, dispatcher, dependency, handoff |
| [Scheduled Tasks](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron/) | cron과 workdir, skill, headless approval |
| [Configuring Models](https://hermes-agent.nousresearch.com/docs/user-guide/configuring-models) | main·auxiliary model slot과 적용 시점 |
| [AI Providers](https://hermes-agent.nousresearch.com/docs/integrations/providers) | provider 종류와 설정 표면 |
| [Fallback Providers](https://hermes-agent.nousresearch.com/docs/user-guide/features/fallback-providers/) | key rotation, primary fallback, auxiliary fallback |
| [Security](https://hermes-agent.nousresearch.com/docs/user-guide/security/) | authorization, approval, file write guard, sandbox |

모든 버전 의존 정보는 2026-07-30에 확인했다. 모델 catalog와 명령은 빠르게 바뀔 수
있으므로 본문은 live `/model` picker와 공식 model catalog를 최종 기준으로 안내한다.

## 핵심 용어

| 용어 | 한 문장 정의 | 혼동 주의 |
|---|---|---|
| session | 한 대화의 history와 실행 상태를 묶는 단위 | Discord channel 전체와 항상 같지 않다 |
| gateway | Discord 등 메시징 입력을 Hermes 실행으로 연결하는 장기 실행 process | profile마다 별도 process와 token을 쓴다 |
| profile | config, key, SOUL, memory, session, skill, cron을 분리한 Hermes home | filesystem sandbox가 아니다 |
| workspace | terminal과 file tool이 작업을 시작하는 directory | profile home과 별개다 |
| delegation | 부모가 fresh-context child agent에게 일시적 subtask를 맡기는 실행 | durable queue가 아니다 |
| Kanban | 여러 named profile이 공유하는 durable task board | 대화 message queue와 다르다 |
| provider | model API 인증·routing을 제공하는 서비스 | model 자체와 구분한다 |
| auxiliary model | title, compression, vision, approval 같은 side job 전용 model | main model과 독립 지정 가능 |

## 핵심 판단

- plain message의 기본 동작은 바쁜 session interrupt다. 안전한 후속 입력은 `/queue`,
  실행 중 방향 수정은 `/steer`, 독립 작업은 `/background`로 구분한다.
- profile은 장기 identity와 state 격리, delegation은 짧은 fresh-context 병렬화,
  Kanban은 restart를 견디는 역할 간 handoff에 사용한다.
- 지시 충돌은 모델이 알아서 우선순위를 추론하게 두지 않는다. 정체성은 `SOUL.md`,
  project 규칙은 `.hermes.md` 또는 `AGENTS.md`, 사용자 취향은 `USER.md`, 현재 task는
  prompt나 Kanban body에 둔다.
- provider는 접근 경로이고 model은 작업 품질을 결정한다. 장기 역할은 profile별 main
  model, 반복적인 side job은 auxiliary, 짧은 child 작업은 delegation model로 분리한다.
- Discord 권한은 최소 allowlist를 유지한다. profile을 나눠도 같은 OS user의 local
  filesystem 접근은 자동 격리되지 않는다.

## 검증 결과

- 공식 문서에서 사용한 모든 slash command와 config key를 확인했다.
- Kanban dispatcher가 gateway 안에서 기본 실행되고, gateway가 없으면 ready task가
  대기한다는 점을 확인했다.
- Discord의 기본 `group_sessions_per_user: true`, server mention 요구, auto-thread
  동작을 확인했다.
- 모델 예시는 공식 Nous Portal·Configuring Models 문서의 2026년 catalog를 사용하되
  영구 순위로 표현하지 않기로 했다.
- 코드 실행 예제는 없고, shell·YAML 예제는 문법과 공식 명령 reference를 대조했다.
