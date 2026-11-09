---
title: 3D 회전과 강체변환 기준 원고 확정
status: final
owner: agent
target_reader: 1단계를 마친 로보틱스 입문자
topic: 3D 회전행렬과 동차변환
---

# 기준 원고 확정

## 기준 원고의 위치

이 책은 MkDocs 챕터형이므로 챕터 본문이 곧 기준 원고이자 최종 산출물이다([adr/0001](../../../../adr/0001-chapter-body-is-the-canonical-manuscript.md)). 이 기록은 이 챕터 하나의 확정 기록이다.

## 확정 목록

- 챕터 본문: `docs/robotics-kinematics-foundations/02-spatial-transformations.md`
- 책 진입점: `docs/robotics-kinematics-foundations/index.md`
- 챕터 자산: `docs/robotics-kinematics-foundations/assets/spatial-transformations/`

## 확정 조건 점검

- 자료 유형: 개념형. 챕터 골격이 `.guide/03_outline.md`의 개념형 흐름과 맞다.
- 개념 절과 절차 소단원(회전행렬인지 판정하는 순서)이 분리되어 있다.
- 연습문제 10개가 절 순서대로 놓였고, 모두 `??? note "정답 확인"` 블록으로 정답과 근거가 있다.
- 독자 검증을 별도 서브에이전트로 수행했다. 조건과 결과는 `06_revision.md` 1절, 기술 검증은 `05_review.md`에 있다.
- 문서마다 `#` 제목 하나, 제목 계층 건너뜀 없음.
- 챕터 파일명 slug와 첫 번째 `#` 제목이 같은 주제를 가리킨다.
- 내부 링크는 대상 `.md` 상대 경로다.
- 코드블록에 언어 식별자가 있다.
- 본문에 내부 메모와 `TODO`, `검증 필요`, `출처 필요` 표시가 없다.
- `python -m mkdocs build --strict` 통과(uv, Python 3.14).

## 확정 시점에 남은 제한

- HTML 실습은 브라우저에서 실행하지 않았다. 독자 검증에서 소스 대조와 Node.js 계산만 했다.
- 현재 본문은 브라우저 화면으로 검수하지 않았다.
