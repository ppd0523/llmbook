---
title: Home Manager 가이드 출판 검수
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
- [x] 1~6장의 정답 블록이 `<details class="note">`로 접혀 렌더링되고, 블록 안의 코드 블록도 표시된다.

`python -m mkdocs build --strict`는 현재 저장소에서 통과한다(uv와 Python 3.14,
`requirements.txt`로 실행). 이 빌드는 링크와 문서 구조를 확인할 뿐이다. 본문 명령의
실행 검증 범위는 `05_review.md`에 있다.

최종 산출물은 MkDocs 책만 둔다. PDF·HTML 별도 변환은 만들지 않으므로 변환 검수도 하지 않는다.
