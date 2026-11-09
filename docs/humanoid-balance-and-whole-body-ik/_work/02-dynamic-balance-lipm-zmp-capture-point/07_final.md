---
title: 휴머노이드 동적 균형의 기초: LIPM, ZMP와 캡처 포인트 기준 원고 확정
status: final
owner: agent
target_reader: 1~5단계를 마친 로보틱스 입문자
topic: LIPM, ZMP, CoP, 캡처 포인트
---

# 기준 원고 확정

## 기준 원고의 위치

이 책은 MkDocs 챕터형이므로 챕터 본문이 곧 기준 원고이자 최종 산출물이다. 이 기록은 이 챕터 하나의 확정 기록이다. 본문은 이 파일에 복제하지 않는다([adr/0001](../../../../adr/0001-chapter-body-is-the-canonical-manuscript.md)).

## 확정 목록

- 챕터 본문: `docs/humanoid-balance-and-whole-body-ik/02-dynamic-balance-lipm-zmp-capture-point.md`
- 책 진입점: `docs/humanoid-balance-and-whole-body-ik/index.md`
- 챕터 자산: `docs/humanoid-balance-and-whole-body-ik/assets/dynamic-balance-lipm-zmp-capture-point/`

## 확정 조건 점검

확정 조건으로 다음을 확인했다.

- 문서마다 `#` 제목 하나, 제목 계층 건너뜀 없음.
- 챕터 파일명 slug와 첫 번째 `#` 제목이 같은 주제를 가리킨다.
- 내부 링크는 대상 `.md` 상대 경로다.
- 코드블록에 언어 식별자가 있다.
- 본문에 내부 메모와 `TODO`, `검증 필요`, `출처 필요` 표시가 없다.
- `python -m mkdocs build --strict` 통과.
