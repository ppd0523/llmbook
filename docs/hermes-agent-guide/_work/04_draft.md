---
title: 초고 기록
version: 1.3
status: complete
owner: agent
updated: 2026-08-30
target_reader: Hermes Agent를 Discord 중심으로 처음 운영하는 사용자
topic: Hermes Agent 운영 가이드
---

# 초고 기록

초고는 `03_outline.md`의 9장 구조로 작성했다. 설명의 중심을 기능 나열보다 실행 단위
선택에 두었다.

초고에서 사용한 대표 시나리오는 다음과 같다.

- Discord thread에서 coding task를 시작하고 `/queue`와 `/steer`로 후속 지시를 보낸다.
- `coder`, `researcher`, `writer`, `orchestrator` profile을 만들고 Kanban dependency로
  research 두 건 뒤 writing을 시작한다.
- main model은 tool-use 품질을 우선하고 title·compression·approval은 저비용
  auxiliary model로 분리한다.
- 상충 지시를 `SOUL.md`, `AGENTS.md`, `USER.md`, task prompt의 책임으로 다시 배치한다.
- Hermes가 이름 있는 `tmux` 안에서 Claude Code를 시작하고, pane을 읽은 뒤에만 후속
  입력을 보내며, 완료 후 diff와 test를 별도로 검증한다.

기술적으로 불확실한 항목은 공식 문서와 대조한 뒤 최종 원고에서 제거하거나 날짜
조건을 붙였다. 특정 model의 가격과 절대 순위는 포함하지 않았다.

2026-08-11 퇴고에서는 Discord 용어를 넓은 표에서 장소와 동작별 정의로 다시 구성하고,
실행 방식의 수명과 완료 결과가 돌아오는 위치를 중심으로 예시를 보강했다. model 장은
제품명 중심 추천에서 provider 제약, slot, task tier, acceptance suite 순서로 재작성했다.

2026-08-30 확장에서는 Claude Code 대화형 세션을 새 9장으로 분리했다. one-shot과
multi-turn 선택부터 시작해 세 겹의 session 상태, 시작 지시 템플릿, 화면별 행동, 이중
승인, 읽기 전용 Worked Example, 중단·복구·독립 검증 순서로 초고를 구성했다.
`claude -p`는 `--max-turns` 도달 시 미완료 오류가 될 수 있으므로 짧고 단순하며 도구
왕복 수가 예상 가능한 작업에만 사용하도록 범위를 좁혔다.
