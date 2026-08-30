---
title: 구성 설계
version: 1.3
status: complete
owner: agent
updated: 2026-08-30
target_reader: Hermes Agent를 Discord 중심으로 처음 운영하는 사용자
topic: Hermes Agent 운영 가이드
---

# 구성 설계

1. mental model과 기능 지도
   - 대화 표면, agent core, tool, state, execution unit
   - 가능한 동작과 하지 못하는 보장
2. Discord 운영
   - server·DM·regular channel·thread·mention의 선행 정의
   - Discord 위치와 Hermes session의 차이
   - 핵심 slash command
   - interrupt·queue·steer
   - 좋은 task instruction
3. profile과 context
   - profile 책임과 생성
   - `SOUL.md`, context file, memory
   - 지시 충돌을 예방하는 placement
4. 실행 방식과 queue
   - foreground, background, delegation, goal, Kanban, cron
   - durability·context·human-in-the-loop 비교
   - 비동기 delegation과 durable execution의 차이
5. 여러 agent 운영
   - orchestrator와 specialist
   - Kanban dependency와 structured handoff
   - workspace 충돌 예방
6. provider와 model
   - provider 선택
   - task별 model tier와 acceptance suite
   - main·auxiliary·delegation·fallback 구성
7. security·cost·reliability
   - Discord authorization, approval, sandbox
   - token·context·fallback·monitoring
8. 운영 recipe와 troubleshooting
   - 개인 assistant, coding team, research pipeline
   - 첫날 연습, 증상별 진단표와 checklist
9. Claude Code 대화형 세션 운영
   - `claude -p`와 `tmux` 대화형 실행 선택
   - Hermes·`tmux`·Claude Code session과 workspace 경계
   - 화면 확인, 후속 입력, 이중 승인, 중단·재개, 독립 검증

각 핵심 장 끝에는 독자가 상태·명령·안전 경계를 스스로 설명하는 확인 문제를 둔다.

설명 흐름은 “무엇인가 → Discord에서 어떻게 쓰는가 → 상태를 어떻게 분리하는가 →
작업을 어떻게 전달하는가 → 비용과 안전을 어떻게 통제하는가” 순서다.
9장은 이 개념을 외부 coding agent를 운영하는 하나의 완결된 실습에 적용한다.
