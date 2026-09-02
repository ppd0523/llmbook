---
title: 출판 전 최종 원고
version: 1.4
status: complete
owner: agent
updated: 2026-09-02
target_reader: Hermes Agent를 Discord 중심으로 처음 운영하는 사용자
topic: Hermes Agent 운영 가이드
---

# 출판 전 최종 원고

최종 원고는 `docs/hermes-agent-guide/index.md`와
`01-mental-model.md`부터 `10-glossary.md`까지의 chapter
Markdown으로 분리했다. 이 파일에는 중복 본문을 두지 않고 출판 단위와 검수 기준만
기록한다.

최종 원고는 다음 기준을 만족한다.

- 1~8장은 2026-08-11의 Hermes 공식 문서, 9장은 2026-08-30의 Hermes·Claude Code·tmux
  공식 문서를 기준으로 한다.
- 초심자가 먼저 알아야 할 execution unit과 Discord interrupt 동작을 앞부분에 둔다.
- profile, context, queue, multi-agent, model, security를 독립된 장으로 설명한다.
- 모든 명령 예제는 official CLI·slash command reference와 대조했다.
- 특정 model을 영구적인 최선으로 단정하지 않고 task 기준과 live picker를 함께 안내한다.
- Discord 용어를 모르는 독자도 DM, regular channel, thread, mention과 Hermes session의
  관계를 설명할 수 있게 한다.
- 비동기 실행과 내구성 실행을 구분하고, Kanban review·handoff가 관찰 가능하게 남도록
  안내한다.
- 각 핵심 장의 확인 문제와 첫날 연습으로 학습 결과를 점검한다.
- Claude Code 운영은 실행 방식 선택, 세 겹 상태, 화면 확인, 승인, 중단·복구, 독립
  검증을 하나의 반복 가능한 절차로 제시한다.
- `claude -p`는 `--max-turns` 미완료 오류를 고려해 짧고 단순한 작업에만 사용하도록
  범위를 제한한다.
- 독자의 선행지식이 아닌 운영 용어는 처음 등장할 때 한국어 정의와 필요한 원어·약어를
  제시하고, 이후 같은 표기를 사용한다.
- 10장 용어집은 본문의 첫 설명을 대신하지 않으며 혼동하기 쉬운 개념 비교와 빠른
  검색을 제공한다.
- 내부 작업 메모와 미검증 표시는 게시 chapter에 포함하지 않는다.
