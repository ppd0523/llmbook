---
title: 수정 기록
version: 1.0
status: complete
owner: agent
updated: 2026-07-30
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
