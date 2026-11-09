---
title: 퇴고 결과
status: complete
owner: agent
target_reader: Hermes Agent를 Discord 중심으로 처음 운영하는 사용자
topic: Hermes Agent 운영 가이드
---

# 퇴고 결과

- “queue”는 message queue, background session, Kanban의 세 의미로 분리해 쓴다.
- profile, workspace, sandbox의 차이는 별도 표로 보인다.
- 지시 우선순위를 단순 서열로 단정하지 않고 책임 위치와 conflict resolution 절차로
  설명한다.
- 여러 Discord bot이 같은 대화를 공유하는 구조 대신, 사용자→orchestrator→Kanban
  구조를 기본안으로 둔다.
- model 추천에는 기준 날짜와 교체 가능한 family 기준을 붙인다.
- destructive 작업, secret, 외부 전송의 승인 조건은 task template에 포함한다.
- 모든 장에서 provider와 model, profile과 session, delegation과 Kanban 표기를 통일한다.
- 2장 앞부분은 Discord 초심자를 위해 server, bot, DM, server channel, regular text
  channel, thread, mention, free-response channel, shared channel, slash command의 정의와
  Hermes routing·session 동작을 장소와 동작으로 나눠 설명한다. regular channel이 별도
  Discord UI 유형이 아님을 명시한다.
- interrupt는 running tool의 강제 종료가 아니라 tool-result 경계의 redirect 동작으로
  설명한다.
- top-level delegation의 비동기 결과 전달과 session·process 수명에 묶인 한계를
  분리해 설명하고 `/goal` 절을 둔다.
- Kanban review 요청·수정 요청 흐름과 Discord bot-to-bot topology 비지원 경고를
  다룬다.
- model 장은 provider 제약 → slot → task tier → acceptance suite → 적용 시점과
  fallback 순서로 구성한다.
- 핵심 장마다 확인 문제를 두고 8장에 read-only 첫날 연습을 둔다.
- 한글 설명을 우선하고 command·config key·검색에 필요한 원문 용어는 유지한다.
- 9장은 Hermes 번들 `claude-code` 스킬을 기준으로 하며 one-shot과 `tmux` 대화형
  실행의 선택 조건을 먼저 설명한다.
- `claude -p`의 `--max-turns` 미완료 오류 위험 때문에 print mode는 짧고 단순하며
  도구 왕복 수가 예상 가능한 작업에만 사용한다.
- Hermes session, `tmux` session, Claude Code session, workspace를 별도 상태로 나누고
  시작 보고에 이름·path·branch를 남기게 한다.
- 상태 확인 요청과 Claude Code 후속 입력을 분리하고, permission dialog 위에 일반
  문장을 보내지 않도록 화면별 행동표를 둔다.
- Hermes approval과 Claude Code permission을 두 승인 경계로 설명하고, 영구 permission
  rule과 bypass mode를 자동 승인하지 않게 한다.
- 읽기 전용 Worked Example, 정상 종료, 긴급 중단, 이름 기반 resume, Hermes의 독립
  diff·test 검증을 하나의 운영 흐름으로 연결한다.
- index에는 한국어 설명·원문 병기·명령어 표기 원칙과 용어집 진입 링크가 있다.
- gateway, tool, toolset, skill, MCP, system prompt, snapshot, turn, run, handle,
  dispatcher, handoff, worktree, concurrency, aggregator, acceptance suite, prompt cache,
  context compression, allowlist, write guard, side effect, prompt injection은 각 장의
  첫 등장에서 정의한다.
- 제목은 한국어 중심으로 쓰고, 검색에 필요한 원어는 첫 정의나 괄호에 남긴다.
- 10장 용어집은 가장 혼동하기 쉬운 여섯 쌍과 범주별 정의·비교·공식 출처를
  한곳에서 찾게 한다.
