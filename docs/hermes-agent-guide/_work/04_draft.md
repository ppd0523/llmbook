---
title: 초고 기록
version: 1.0
status: complete
owner: agent
updated: 2026-07-30
target_reader: Hermes Agent를 Discord 중심으로 처음 운영하는 사용자
topic: Hermes Agent 운영 가이드
---

# 초고 기록

초고는 `03_outline.md`의 8장 구조로 작성했다. 설명의 중심을 기능 나열보다 실행 단위
선택에 두었다.

초고에서 사용한 대표 시나리오는 다음과 같다.

- Discord thread에서 coding task를 시작하고 `/queue`와 `/steer`로 후속 지시를 보낸다.
- `coder`, `researcher`, `writer`, `orchestrator` profile을 만들고 Kanban dependency로
  research 두 건 뒤 writing을 시작한다.
- main model은 tool-use 품질을 우선하고 title·compression·approval은 저비용
  auxiliary model로 분리한다.
- 상충 지시를 `SOUL.md`, `AGENTS.md`, `USER.md`, task prompt의 책임으로 다시 배치한다.

기술적으로 불확실한 항목은 공식 문서와 대조한 뒤 최종 원고에서 제거하거나 날짜
조건을 붙였다. 특정 model의 가격과 절대 순위는 포함하지 않았다.
