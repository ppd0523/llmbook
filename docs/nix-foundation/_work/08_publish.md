---
title: 최종 산출물 구성과 출판 변환 검수
version: 0.1
status: final
owner: agent
updated: 2026-08-19
target_reader: Nix 입문자
topic: Nix 첫걸음 출판 검수
---

# 최종 산출물 구성과 출판 변환 검수

## 1. 최종 산출물 계획

- 기준 원고 Markdown: `docs/nix-foundation/index.md` 및 8개 챕터
- 최종 산출물 형식: MkDocs 챕터형 Markdown 학습자료
- 최종 산출물 경로: `docs/nix-foundation/`
- MkDocs 책 폴더명: `nix-foundation`
- 챕터 파일명 규칙: `NN-<chapter-slug>.md`
- 내부 작업 산출물: `docs/nix-foundation/_work/`
- 구성 도구: MkDocs 1.6.1
- 검증 명령: `.venv/bin/mkdocs build --strict --theme mkdocs`
- 검증 일시: 2026-08-19

## 2. 산출 결과

| 형식 | 파일 또는 구조 | 상태 | 비고 |
|---|---|---|---|
| Chapter Markdown | `index.md`, `01-*.md`부터 `08-*.md` | 통과 | 실제 최종 산출물 |
| Markdown 기준 원고 | `_work/07_final.md` | 통과 | 챕터형 기준 원고 인덱스 |
| HTML 렌더링 검증 | 임시 MkDocs site | 통과 | 2026-08-19 표준 MkDocs theme에서 strict build 성공 |

## 3. 검수 결과

- [x] `01_scope.md`의 최종 산출물 형식과 실제 결과가 일치한다.
- [x] 챕터 파일이 책 폴더 바로 아래에 있고 두 자리 번호와 kebab-case를 사용한다.
- [x] 책 진입점 `index.md`와 모든 챕터가 존재한다.
- [x] 장 사이 링크는 상대 `.md` 경로로 작성되어 있다.
- [x] 각 최종 문서에는 `#` 제목이 하나만 있고 제목 계층을 건너뛰지 않는다.
- [x] 모든 코드 블록에 언어 식별자가 있고 fence가 올바르게 닫힌다.
- [x] 최종 챕터에는 내부 작업 메모, `TODO`, `검증 필요`, `출처 필요`가 없다.
- [x] `_work/`는 `mkdocs.yml`의 `exclude_docs` 규칙으로 게시 대상에서 제외된다.
- [x] 표준 MkDocs theme에서 `mkdocs build --strict`가 성공했다.

## 4. 환경 주의

현재 저장소에 설치된 Material for MkDocs theme에는 `partials/language.html` 템플릿이 없어, 원본 theme으로는 문서 렌더링 전 단계에서 build가 중단된다. 이는 이번 Markdown 변경과 무관한 의존성 상태다. 문서 구조·내부 링크 검증은 MkDocs 1.6.1의 표준 theme에서 strict build로 통과했다. 실제 Material 배포 전에는 theme 의존성을 복구한 뒤 원본 `mkdocs.yml`로 다시 build한다.
