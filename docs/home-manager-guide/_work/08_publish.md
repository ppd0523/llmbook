---
title: Home Manager 가이드 출판 검수
updated: 2026-08-11
---

# 최종 산출물 검수

## 산출물

- 형식: MkDocs 챕터형 Markdown
- 경로: `docs/home-manager-guide/`
- 진입점: `index.md`
- 챕터: `01-mental-model.md`부터 `06-troubleshooting.md`

## 검수 항목

- [x] 챕터 파일명과 `#` 제목이 같은 주제를 가리킨다.
- [x] 모든 내부 링크는 상대 `.md` 경로다.
- [x] 코드 블록에 언어 식별자를 붙였다.
- [x] 최종 챕터에 내부 메모와 미검증 표시가 없다.
- [x] 외부 기술 근거는 Home Manager와 Nix 공식 문서 링크로 제공한다.

`mkdocs build --strict`는 현재 Windows 실행 환경에 MkDocs 실행 파일이 없어 수행하지
못했다. 대신 최종 챕터의 상대 Markdown 링크, 제목 계층, 공백 오류를 정적으로
검사했다.

변환 산출물은 요청되지 않았으므로 PDF·HTML 별도 변환 검수는 수행하지 않았다.
