---
title: 최종 산출물 구성과 출판 검수
status: complete
owner: agent
target_reader: Hermes Agent를 Discord 중심으로 처음 운영하는 사용자
topic: Hermes Agent 운영 가이드
---

# 최종 산출물 구성과 출판 검수

## 산출 계획

- 기준 원고: 챕터 본문 `docs/hermes-agent-guide/NN-<chapter-slug>.md` (`_work/07_final.md`는 확정 기록)
- 형식: MkDocs 챕터형 Markdown
- 최종 경로: `docs/hermes-agent-guide/`
- 파일: `index.md`, `01-mental-model.md`부터
  `10-glossary.md`
- 구성 도구: MkDocs Material
- 검증 명령: `python -m mkdocs build --strict`

## 검수 항목

- [x] 책 폴더와 chapter 파일이 kebab-case 규칙을 따른다.
- [x] 내부 작업 파일은 `_work/`에 분리했다.
- [x] 사이트와 책의 `index.md`에서 진입할 수 있다.
- [x] 제목 계층과 chapter 간 상대 링크를 점검했다.
- [x] shell·YAML code fence에 언어를 표시했다.
- [x] 외부 참고 자료는 Hermes·Claude Code 공식 문서와 tmux 공식 wiki로 연결했다.
- [x] 게시 chapter에 작업 메모나 미검증 표시가 없다.
- [x] MkDocs strict build가 성공했다.

## 결론

현재 저장소에서 `python -m mkdocs build --strict`가 MkDocs 1.6.1과 MkDocs Material
9.7.6(uv, Python 3.14)으로 성공한다. 목차→9장·10장, 8장→9장, 9장→10장의 상대 링크,
문서별 단일 H1, code fence의 언어 표시, 게시 원고의 미검증 표시 부재를 현재 본문에서
확인했다. 렌더링된 화면은 브라우저로 검수하지 않았다. 배포 가능한 Markdown 책으로
판단한다.
