---
title: 조사 노트
version: 1.3
status: complete
owner: agent
updated: 2026-08-30
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
| [Configuring Models](https://hermes-agent.nousresearch.com/docs/user-guide/configuring-models) | main·auxiliary model slot, picker, 적용 시점 |
| [AI Providers](https://hermes-agent.nousresearch.com/docs/integrations/providers) | provider 종류와 설정 표면 |
| [Fallback Providers](https://hermes-agent.nousresearch.com/docs/user-guide/features/fallback-providers/) | key rotation, primary fallback, auxiliary fallback |
| [Model Catalog](https://hermes-agent.nousresearch.com/docs/reference/model-catalog) | live catalog, cache, bundled snapshot과 picker 동작 |
| [Security](https://hermes-agent.nousresearch.com/docs/user-guide/security/) | authorization, approval, file write guard, sandbox |
| [Bundled Claude Code Skill](https://hermes-agent.nousresearch.com/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-claude-code) | `claude -p`와 `tmux` 대화형 운영, 화면 캡처·후속 입력·복구 |
| [Built-in Tools Reference](https://hermes-agent.nousresearch.com/docs/reference/tools-reference/) | `terminal`과 background `process`의 책임 |
| [Claude Code CLI Reference](https://code.claude.com/docs/en/cli-usage) | interactive·print mode, named session, resume·continue |
| [Claude Code Interactive Mode](https://code.claude.com/docs/en/interactive-mode) | 작업 중 message queue, interrupt, keyboard 동작 |
| [Claude Code Permissions](https://code.claude.com/docs/en/permissions) | permission mode, 영구 rule, bypass 경고 |
| [tmux Getting Started](https://github.com/tmux/tmux/wiki/Getting-Started) | session·pane, `send-keys`, `capture-pane` 명령 의미 |

1~8장의 버전 의존 정보는 2026-08-11, 9장의 Hermes·Claude Code·tmux 정보는
2026-08-30에 확인했다. 모델 catalog와 명령은 빠르게 바뀔 수 있으므로 본문은 live
`/model` picker와 공식 model catalog를 최종 기준으로 안내한다.

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
| tmux session | 대화형 terminal process와 화면을 이름 아래 유지하는 단위 | Claude Code 대화 history 자체와 다르다 |
| Claude Code session | Claude Code의 대화 history·checkpoint·작업 상태 | Hermes session이나 tmux process와 다르다 |

## 핵심 판단

- plain message의 기본 동작은 바쁜 session interrupt다. 안전한 후속 입력은 `/queue`,
  실행 중 방향 수정은 `/steer`, 독립 작업은 `/background`로 구분한다.
- interrupt는 실행 중 도구를 강제 종료하는 동작이 아니다. 현재 도구 결과 경계에서
  보정하고 이미 나온 응답과 완료된 tool call을 유지한다.
- profile은 장기 identity와 state 격리, delegation은 짧은 fresh-context 병렬화,
  Kanban은 restart를 견디는 역할 간 handoff에 사용한다.
- top-level delegation은 handle을 즉시 반환하고 결과를 나중에 전달할 수 있지만 소유
  session reset이나 Hermes process restart를 견디는 durable execution은 아니다.
- 지시 충돌은 모델이 알아서 우선순위를 추론하게 두지 않는다. 정체성은 `SOUL.md`,
  project 규칙은 `.hermes.md` 또는 `AGENTS.md`, 사용자 취향은 `USER.md`, 현재 task는
  prompt나 Kanban body에 둔다.
- provider는 접근 경로이고 model은 작업 품질을 결정한다. 장기 역할은 profile별 main
  model, 반복적인 side job은 auxiliary, 짧은 child 작업은 delegation model로 분리한다.
- Discord 권한은 최소 allowlist를 유지한다. profile을 나눠도 같은 OS user의 local
  filesystem 접근은 자동 격리되지 않는다.
- 짧고 단순한 한 번의 Claude Code 작업은 `claude -p`, 여러 차례 관찰·후속 지시가
  필요한 작업은 `tmux` 기반 대화형 세션을 우선 검토한다. 이 가이드에서는 print mode를
  tool-use turn 수가 예상 가능한 작업으로 제한한다.
- Hermes session, `tmux` session, Claude Code session, workspace를 각각 이름과 path로
  기록하고, 입력 전에 pane 상태를 확인한다.
- Hermes terminal 승인을 통과해도 Claude Code의 permission·trust 선택은 별도 승인으로
  다룬다. 영구 rule과 bypass mode는 자동 선택하지 않는다.

## 검증 결과

- 공식 문서에서 사용한 모든 slash command와 config key를 확인했다.
- Kanban dispatcher가 gateway 안에서 기본 실행되고, gateway가 없으면 ready task가
  대기한다는 점을 확인했다.
- Discord의 기본 `group_sessions_per_user: true`, server mention 요구, auto-thread
  동작을 확인했다.
- Kanban의 `request-review`, `request-changes` 흐름과 agent tool·human CLI 표면을
  확인했다.
- live model catalog가 picker에서 갱신되고 장애 시 cache 또는 설치본 snapshot으로
  fallback하는 동작을 확인했다.
- 모델 예시는 current catalog와 Configuring Models 문서에서 최소한만 사용하고, 영구
  순위 대신 acceptance suite와 작업 tier를 본문 중심으로 삼았다.
- 코드 실행 예제는 없고, shell·YAML 예제는 문법과 공식 명령 reference를 대조했다.
- 번들 `claude-code` 스킬이 one-shot에는 print mode, multi-turn에는 `tmux` orchestration을
  권장하고 `capture-pane`과 `send-keys`를 운영 표면으로 사용하는 점을 확인했다.
- 작성 환경에는 `tmux`가 없어 command를 직접 실행하지 못했으며, 번들 스킬과 tmux 공식
  wiki에서 `new-session`, `send-keys -l`, `capture-pane -p`의 형식을 교차 확인했다.
- Claude Code가 작업 중 받은 일반 message를 queue하고, `--continue`는 현재 directory의
  최근 session을, `--resume`은 ID나 이름으로 지정한 session을 재개하는 점을 확인했다.
- print mode의 `--max-turns`가 tool-use round trip을 제한하고, 한도에 도달하면 정상
  결과 없이 `error_max_turns`로 끝날 수 있음을 확인했다. 깊은 thinking이 필요한 복잡한
  작업은 도구 왕복 수를 예측하기 어려우므로 대화형 실행 대상으로 분류했다.
- Claude Code의 permission rule 일부는 repository에 영구 저장될 수 있고 bypass mode는
  격리 환경에서만 사용하라는 공식 경고를 확인했다.
