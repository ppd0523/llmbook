---
title: 최종 산출물 구성과 출판 검수
version: 1.0
status: complete
owner: agent
updated: 2026-08-12
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

- `docs/index.md`에 책 링크를 추가했다.
- 각 챕터의 제목 계층은 `#`에서 시작하며 한 문서에 `#` 제목 하나만 사용한다.
- 모든 내부 링크는 대상 `.md` 파일을 가리킨다.
- `_work/`는 `mkdocs.yml`의 제외 규칙에 의해 게시 대상에서 제외된다.
- 최종 본문에는 내부 메모, TODO, 검증 필요 표기가 없다.
- `mkdocs build --strict`와 번들 Python의 `-m mkdocs build --strict`를 시도했으나, 이 작업 환경에는 MkDocs 명령과 Python 모듈이 설치되어 있지 않아 실행하지 못했다. 로컬 Markdown 링크 검사는 7개 게시 대상 파일에서 통과했다. 배포 전 MkDocs가 설치된 환경에서 strict build를 다시 실행한다.
