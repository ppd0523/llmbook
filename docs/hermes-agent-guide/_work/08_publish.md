---
title: 최종 산출물 구성과 출판 검수
version: 1.4
status: complete
owner: agent
updated: 2026-09-02
target_reader: Hermes Agent를 Discord 중심으로 처음 운영하는 사용자
topic: Hermes Agent 운영 가이드
---

# 최종 산출물 구성과 출판 검수

## 산출 계획

- 기준 원고: `docs/hermes-agent-guide/_work/07_final.md`
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
- [x] 외부 참고 자료는 Hermes 공식 문서로 연결했다.
- [x] 게시 chapter에 작업 메모나 미검증 표시가 없다.
- [x] MkDocs strict build가 성공했다.

## 결론

2026-07-30에 MkDocs Material 9.7.6과 MkDocs 1.6.1로
`python -m mkdocs build --strict`를 실행해 성공했다. 배포 가능한 Markdown 책으로
판단한다.

2026-07-31에 Discord 용어와 session 설명을 보강한 버전 1.1도 같은 strict build로
다시 검증해 성공했다. 버전 1.2는 2026-08-11 퇴고와 공식 문서 재검증을 반영했다.
MkDocs Material 9.7.6과 MkDocs 1.6.1로 strict build를 다시 실행해 성공했으며, 내부
상대 링크와 게시 구조를 함께 확인했다.

버전 1.3은 2026-08-30에 Claude Code 대화형 세션 운영 9장과 갱신한 목차를 추가했다.
MkDocs Material 9.7.6과 MkDocs 1.6.1로 strict build를 실행해 성공했으며, 8장→9장과
목차→9장의 상대 링크, 제목 계층, code fence 렌더링을 함께 확인했다.

버전 1.4는 2026-09-02에 본문 첫 등장 용어 설명과 10장 용어집을 추가했다. MkDocs
Material 9.7.6과 MkDocs 1.6.1로 strict build를 실행해 성공했다. 목차→10장과
9장→10장의 상대 링크, 문서별 단일 H1, code fence, 게시 원고의 미검증 표시 부재를
함께 확인했다.
