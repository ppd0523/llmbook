---
title: 평면 회전과 2관절 역기구학 기준 원고 확정
status: final
owner: agent
updated: 2026-09-22
target_reader: 고등학교 수준의 행렬·삼각함수를 아는 로보틱스 입문자
topic: 2관절 평면 매니퓰레이터의 역기구학
---

# 기준 원고 확정

> 이 파일은 이전에 챕터 본문을 복제한 사본을 담고 있었다. 본문이 개정되는 동안 사본은 갱신되지 않아 서로 다른 판이 되었고, 이름과 프런트매터 때문에 사본이 기준 원고로 오인될 수 있었다. [adr/0001](../../../../adr/0001-chapter-body-is-the-canonical-manuscript.md)의 정의에 따라 사본을 지우고 확정 기록만 남긴다. 기준 원고는 아래 목록의 챕터 본문이며 사라진 내용은 없다.

## 기준 원고의 위치

이 책은 MkDocs 챕터형이므로 챕터 본문이 곧 기준 원고이자 최종 산출물이다. 이 기록은 이 챕터 하나의 확정 기록이다.

## 확정 목록

- 챕터 본문: `docs/robotics-kinematics-foundations/01-planar-kinematics.md`
- 책 진입점: `docs/robotics-kinematics-foundations/index.md`
- 챕터 자산: `docs/robotics-kinematics-foundations/assets/planar-kinematics/`

## 확정 조건 점검

확정 시점(2026-09-22) 기준으로 다음을 확인했다.

- 문서마다 `#` 제목 하나, 제목 계층 건너뜀 없음.
- 챕터 파일명 slug와 첫 번째 `#` 제목이 같은 주제를 가리킨다.
- 내부 링크는 대상 `.md` 상대 경로다.
- 코드블록에 언어 식별자가 있다.
- 본문에 내부 메모와 `TODO`, `검증 필요`, `출처 필요` 표시가 없다.
- `python -m mkdocs build --strict` 통과.

## 2026-11-09 재확정

`.guide/` 개정(자료 유형, 연습문제 피드백, 독자 검증)에 맞춘 개정 후 다시 확인했다. 개정 내용은 `06_revision.md` 8절, 기술 재검증은 `05_review.md` 10절에 있다.

- 자료 유형: 개념형. 챕터 골격이 `.guide/03_outline.md`의 개념형 흐름과 맞다.
- 모든 연습문제에 `??? note "정답 확인"` 블록으로 정답과 근거가 있다.
- 독자 검증을 별도 서브에이전트로 수행했고 결과를 처리했다.
- `python -m mkdocs build --strict` 통과(uv, Python 3.14). 생성 HTML에서 정답 블록의 목록·수식과 새 표가 정상 렌더링되는 것을 확인했다.
- 본문에 `TODO`, `검증 필요`, `출처 필요` 표시가 없다.
- 남은 제한: HTML 실습은 실행하지 않았다. 브라우저 화면 검수는 하지 않았다.

## 2026-11-09 2차 재확정

절 역할·과제 기준([adr/0007](../../../../adr/0007-material-type-is-chapter-focus-section-role-is-single.md))에 맞춘 퇴고 후 다시 확인했다. 내용은 `06_revision.md` 9절과 `05_review.md` 11절에 있다.

- 개념 절과 절차 절이 분리되어 있다(4.4 신설).
- 연습문제 8개가 절 순서와 난이도 순으로 놓였고, 모두 정답과 근거가 있다.
- 정답 블록을 지운 사본으로 독자 검증을 다시 수행했다.
- `python -m mkdocs build --strict` 통과(uv, Python 3.14).
- 남은 제한: HTML 실습은 실행하지 않았다. 브라우저 화면 검수는 하지 않았다.

- 3차 퇴고(2026-11-09): 남은 독자 지적을 반영했다(`06_revision.md` 10절). `python -m mkdocs build --strict` 통과.
