---
title: 자코비안과 수치 역기구학 기준 원고 확정
status: final
owner: agent
updated: 2026-09-22
target_reader: 1~3단계를 마친 로보틱스 입문자
topic: 자코비안과 반복 수치 역기구학
---

# 기준 원고 확정

> 이 파일은 이전에 챕터 본문을 복제한 사본을 담고 있었다. 본문이 개정되는 동안 사본은 갱신되지 않아 서로 다른 판이 되었고, 이름과 프런트매터 때문에 사본이 기준 원고로 오인될 수 있었다. [adr/0001](../../../../adr/0001-chapter-body-is-the-canonical-manuscript.md)의 정의에 따라 사본을 지우고 확정 기록만 남긴다. 기준 원고는 아래 목록의 챕터 본문이며 사라진 내용은 없다.

## 기준 원고의 위치

이 책은 MkDocs 챕터형이므로 챕터 본문이 곧 기준 원고이자 최종 산출물이다. 이 기록은 이 챕터 하나의 확정 기록이다.

## 확정 목록

- 챕터 본문: `docs/robotics-manipulator-kinematics/02-jacobian-numerical-inverse-kinematics.md`
- 책 진입점: `docs/robotics-manipulator-kinematics/index.md`
- 챕터 자산: `docs/robotics-manipulator-kinematics/assets/jacobian-numerical-inverse-kinematics/`

## 확정 조건 점검

확정 시점(2026-09-22) 기준으로 다음을 확인했다.

- 문서마다 `#` 제목 하나, 제목 계층 건너뜀 없음.
- 챕터 파일명 slug와 첫 번째 `#` 제목이 같은 주제를 가리킨다.
- 내부 링크는 대상 `.md` 상대 경로다.
- 코드블록에 언어 식별자가 있다.
- 본문에 내부 메모와 `TODO`, `검증 필요`, `출처 필요` 표시가 없다.
- `python -m mkdocs build --strict` 통과.
