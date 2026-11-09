---
title: 최종 산출물 구성과 출판 검수
status: complete
owner: agent
target_reader: EDSDK를 처음 접하는 기술 담당자
topic: Canon EDSDK 기능 중심 카메라 제어
---

# 최종 산출물 구성과 출판 검수

## 산출물

- 형식: MkDocs 챕터형 Markdown
- 경로: `docs/canon-edsdk-guide/`
- 진입점: `docs/canon-edsdk-guide/index.md`
- 챕터: `01-`부터 `06-`까지 6개 Markdown 파일
- 내부 작업 기록: `docs/canon-edsdk-guide/_work/`

## 검수 항목

- `docs/index.md`에 책 링크가 있다.
- 각 챕터의 제목 계층은 `#`에서 시작하며 한 문서에 `#` 제목 하나만 사용한다.
- 모든 내부 링크는 대상 `.md` 파일을 가리킨다.
- `_work/`는 `mkdocs.yml`의 제외 규칙에 의해 게시 대상에서 제외된다.
- 최종 본문에는 내부 메모, TODO, 검증 필요 표기가 없다.
- 현재 저장소에서 `python -m mkdocs build --strict`가 통과한다(MkDocs 1.6.1, Material 9.7.6, uv와 Python 3.14로 실행). strict build는 게시 대상 `index.md`와 6개 챕터의 내부 링크 경고를 오류로 처리한다. 실제 카메라와 화면 검수는 이 빌드에 포함되지 않는다.
