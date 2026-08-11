---
title: 수정 기록
version: 1.2
status: complete
owner: agent
updated: 2026-08-11
target_reader: Hermes Agent를 Discord 중심으로 처음 운영하는 사용자
topic: Hermes Agent 운영 가이드
---

# 수정 기록

- “queue”를 message queue, background session, Kanban의 세 의미로 분리했다.
- profile, workspace, sandbox의 차이를 별도 표로 만들었다.
- 지시 우선순위를 단순 서열로 단정하지 않고 책임 위치와 conflict resolution 절차로
  설명했다.
- multiple Discord bot이 같은 대화를 공유하도록 하는 대신, 사용자→orchestrator→Kanban
  구조를 기본안으로 정했다.
- model 추천에 기준 날짜와 교체 가능한 family 기준을 붙였다.
- destructive 작업, secret, 외부 전송의 승인 조건을 task template에 포함했다.
- 모든 장에서 provider와 model, profile과 session, delegation과 Kanban 표기를 통일했다.
- 2026-07-31: Discord 초심자를 위해 server, bot, DM, server channel, regular text
  channel, thread, mention, free-response channel, shared channel, slash command의 정의와
  Hermes routing·session 동작을 2장 앞부분에 추가했다.
- 2026-08-11: Discord 용어를 장소와 동작으로 나눠 넓은 표를 제거하고, regular
  channel이 별도 Discord UI 유형이 아님을 명확히 했다.
- interrupt를 running tool의 강제 종료로 오해할 수 있는 문장을 tool-result 경계의
  redirect 동작으로 바로잡았다.
- top-level delegation의 비동기 결과 전달과 session·process 수명에 묶인 한계를
  분리해 설명하고 `/goal` 절을 추가했다.
- Kanban review 요청·수정 요청 흐름과 Discord bot-to-bot topology 비지원 경고를
  추가했다.
- model 장을 고정 후보 목록에서 provider 제약 → slot → task tier → acceptance suite →
  적용 시점과 fallback 순서로 재작성했다.
- 핵심 장마다 확인 문제를 넣고 8장에 read-only 첫날 연습을 추가했다.
- 한글 설명을 우선하고 command·config key·검색에 필요한 원문 용어는 유지했다.
