---
title: 기술 및 구조 검토
version: 1.0
status: complete
owner: agent
updated: 2026-07-30
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
| background | 현재 chat history를 받지 않는 별도 session | prompt self-contained 원칙 추가 |
| profile | state 격리지만 sandbox 아님 | 3장과 7장에서 반복 경고 |
| SOUL 변경 | 새 session에서 명확히 적용 | conflict 절차에 `/new` 추가 |
| delegation | child는 fresh context, toolset을 확대할 수 없음 | 4장과 5장에 반영 |
| Kanban | profile 공유 durable DB, gateway dispatcher 기본 | 4장과 5장에 반영 |
| model switch | session 중 변경 시 prompt cache reset | 6장 비용 주의에 반영 |
| cron workdir | project context를 받으려면 absolute workdir 필요 | 4장에 반영 |

## 구조 검토

- 기능 소개 뒤 바로 Discord를 배치해 첫 사용자가 실수하기 쉬운 interrupt를 먼저 다룬다.
- profile과 queue를 분리해 “누가 하는가”와 “얼마나 오래 남는가”를 구분한다.
- 다중 agent 장은 profile 수를 늘리는 방법보다 role contract와 handoff를 강조한다.
- 모델 장은 이름보다 slot과 선택 기준을 먼저 설명한다.
- 각 장 끝에 다음 장 링크와 실행 가능한 점검 항목을 둔다.

## 남은 위험

- Hermes는 활발히 개발 중이므로 slash command, model catalog, default 값이 바뀔 수 있다.
  문서 첫머리와 참고 자료에 확인 날짜를 표시한다.
- provider별 가격과 quota는 외부 상태라 고정하지 않는다. `/usage`와 provider dashboard를
  운영 기준으로 사용한다.
