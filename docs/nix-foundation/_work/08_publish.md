---
title: 최종 산출물 구성과 출판 변환 검수
version: 0.1
status: final
owner: agent
updated: 2026-08-30
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
- 검증 명령: `uv run --with mkdocs-material==9.7.6 mkdocs build --strict`
- 검증 일시: 2026-08-30

## 2. 산출 결과

| 형식 | 파일 또는 구조 | 상태 | 비고 |
|---|---|---|---|
| Chapter Markdown | `index.md`, `01-*.md`부터 `08-*.md` | 통과 | 실제 최종 산출물 |
| Markdown 기준 원고 | `_work/07_final.md` | 통과 | 챕터형 기준 원고 인덱스 |
| HTML 렌더링 검증 | MkDocs site | 통과 | Material for MkDocs 9.7.6에서 strict build 성공 |

## 3. 검수 결과

- [x] `01_scope.md`의 최종 산출물 형식과 실제 결과가 일치한다.
- [x] 챕터 파일이 책 폴더 바로 아래에 있고 두 자리 번호와 kebab-case를 사용한다.
- [x] 책 진입점 `index.md`와 모든 챕터가 존재한다.
- [x] 장 사이 링크는 상대 `.md` 경로로 작성되어 있다.
- [x] 각 최종 문서에는 `#` 제목이 하나만 있고 제목 계층을 건너뛰지 않는다.
- [x] 모든 코드 블록에 언어 식별자가 있고 fence가 올바르게 닫힌다.
- [x] 최종 챕터에는 내부 작업 메모, `TODO`, `검증 필요`, `출처 필요`가 없다.
- [x] `_work/`는 `mkdocs.yml`의 `exclude_docs` 규칙으로 게시 대상에서 제외된다.
- [x] 저장소의 Material theme 설정으로 `mkdocs build --strict`가 성공했다.

## 4. 환경 주의

저장소의 `requirements.txt`와 같은 Material for MkDocs 9.7.6을 임시 `uv` 환경에
설치해 원본 `mkdocs.yml`을 변경하지 않고 검증했다. 문서 구조, 내부 링크, 탐색 구성과
Material 렌더링이 모두 strict build를 통과했다.
