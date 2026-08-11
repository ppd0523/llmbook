---
title: 기술 및 구조 검토
version: 1.2
status: complete
owner: agent
updated: 2026-08-11
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

## 구조 검토

- 기능 소개 뒤 바로 Discord를 배치해 첫 사용자가 실수하기 쉬운 interrupt를 먼저 다룬다.
- profile과 queue를 분리해 “누가 하는가”와 “얼마나 오래 남는가”를 구분한다.
- 다중 agent 장은 profile 수를 늘리는 방법보다 role contract와 handoff를 강조한다.
- 모델 장은 이름보다 slot과 선택 기준을 먼저 설명한다.
- 각 장 끝에 다음 장 링크와 실행 가능한 점검 항목을 둔다.
- 초심자가 Discord 용어를 안다고 가정하지 않고 장소·동작·Hermes 처리 방식을 먼저
  정의한다.
- 1~7장에 확인 문제, 8장에 첫날 연습을 추가해 읽기만 하는 자료가 되지 않게 한다.

## 남은 위험

- Hermes는 활발히 개발 중이므로 slash command, model catalog, default 값이 바뀔 수 있다.
  문서 첫머리와 참고 자료에 확인 날짜를 표시한다.
- provider별 가격과 quota는 외부 상태라 고정하지 않는다. `/usage`와 provider dashboard를
  운영 기준으로 사용한다.
