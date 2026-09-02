---
title: 기술 및 구조 검토
version: 1.4
status: complete
owner: agent
updated: 2026-09-02
target_reader: Hermes Agent를 Discord 중심으로 처음 운영하는 사용자
topic: Hermes Agent 운영 가이드
---

# 기술 및 구조 검토

## 기술 검토

| 항목 | 결과 | 반영 |
|---|---|---|
| Discord 기본 응답 | server channel은 mention 필요, DM은 불필요 | 2장에 반영 |
| session 격리 | 기본값은 channel 안에서도 user별 분리 | 2장에 반영 |
| busy input | plain message는 기본 interrupt | `/queue`·`/steer` 우선 안내 |
| interrupt 경계 | running tool은 끝나고 보정은 다음 tool-result boundary에 반영 | 즉시 강제 종료로 오해하는 표현 수정 |
| background | 현재 chat history를 받지 않는 별도 session | prompt self-contained 원칙 추가 |
| profile | state 격리지만 sandbox 아님 | 3장과 7장에서 반복 경고 |
| SOUL 변경 | 새 session에서 명확히 적용 | conflict 절차에 `/new` 추가 |
| delegation | child는 fresh context, toolset을 확대할 수 없음 | 4장과 5장에 반영 |
| delegation 수명 | top-level 결과는 비동기 전달되지만 session reset·process restart에 내구성 없음 | Kanban과 선택 기준 수정 |
| Kanban | profile 공유 durable DB, gateway dispatcher 기본 | 4장과 5장에 반영 |
| Kanban review | request-review·request-changes로 구현과 검토 상태 분리 | 4장에 예시 추가 |
| model switch | session 중 변경 시 prompt cache reset | 6장 비용 주의에 반영 |
| model catalog | live manifest, cache, bundled snapshot 순으로 picker 후보 제공 | 고정 모델 순위 제거 |
| cron workdir | project context를 받으려면 absolute workdir 필요 | 4장에 반영 |
| Claude Code 실행 방식 | one-shot은 `claude -p`, multi-turn은 번들 스킬이 `tmux` 권장 | 9장 선택표에 반영 |
| print mode turn limit | `--max-turns` 도달 시 미완료 오류로 종료하며 복잡한 작업은 tool-use turn 수 예측이 어려움 | 짧고 단순한 작업으로 사용 범위 제한 |
| 대화형 상태 | Hermes, `tmux`, Claude Code, workspace는 서로 다른 수명과 식별자를 가짐 | 세 겹 상태 그림과 시작 보고 추가 |
| Claude Code busy input | 작업 중 일반 message는 내부 queue에 들어갈 수 있음 | 화면 확인 뒤 한 번만 전달하도록 수정 |
| session 재개 | `--continue`는 current directory의 최근 대화, `--resume`은 이름·ID 지정 | 이름 있는 session을 기본으로 사용 |
| permission | 일부 영구 승인은 repository rule로 저장되고 bypass는 격리 환경용 | 이중 승인과 자동 승인 금지 반영 |
| nested 완료 검증 | Claude Code 요약만으로 diff·test 성공을 보장할 수 없음 | Hermes 독립 검증 절차 추가 |

## 구조 검토

- 기능 소개 뒤 바로 Discord를 배치해 첫 사용자가 실수하기 쉬운 interrupt를 먼저 다룬다.
- profile과 queue를 분리해 “누가 하는가”와 “얼마나 오래 남는가”를 구분한다.
- 다중 agent 장은 profile 수를 늘리는 방법보다 role contract와 handoff를 강조한다.
- 모델 장은 이름보다 slot과 선택 기준을 먼저 설명한다.
- 각 장 끝에 다음 장 링크와 실행 가능한 점검 항목을 둔다.
- 초심자가 Discord 용어를 안다고 가정하지 않고 장소·동작·Hermes 처리 방식을 먼저
  정의한다.
- 1~7장에 확인 문제, 8장에 첫날 연습을 추가해 읽기만 하는 자료가 되지 않게 한다.
- 9장은 기존 session·workspace·approval 개념을 Claude Code 운영 절차에 적용하고,
  시작부터 복구까지 한 장 안에서 독립적으로 수행할 수 있게 한다.
- tool·toolset·skill·MCP, session ID·session key, credential pool·fallback,
  snapshot·checkpoint의 경계를 공식 문서와 대조했다.
- 용어집을 본문 정의의 대체물이 아닌 빠른 참조로 두고, 각 핵심 용어는 실제 사용 장의
  첫 등장에서도 한 문장으로 설명한다.
- 같은 영어 단어가 여러 층에서 다른 뜻을 가질 때 Hermes·`tmux`·Claude Code처럼
  대상을 앞에 붙이고, 명령어·설정 키만 원문 표기를 유지한다.

## 남은 위험

- Hermes는 활발히 개발 중이므로 slash command, model catalog, default 값이 바뀔 수 있다.
  문서 첫머리와 참고 자료에 확인 날짜를 표시한다.
- provider별 가격과 quota는 외부 상태라 고정하지 않는다. `/usage`와 provider dashboard를
  운영 기준으로 사용한다.
- Hermes와 Claude Code의 CLI·permission 동작은 빠르게 바뀔 수 있으므로 9장에 확인
  날짜를 표시하고 설치 버전의 `/help`와 `claude --help`를 최종 기준으로 둔다.
