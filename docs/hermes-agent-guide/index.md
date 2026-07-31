---
title: Hermes Agent 실전 운영 가이드
version: 1.1
updated: 2026-07-31
---

# Hermes Agent 실전 운영 가이드

Hermes Agent는 대화만 하는 bot이 아니다. 파일과 terminal을 다루고, web과 browser를
사용하며, 기억·예약 작업·하위 agent·여러 역할의 작업 queue를 운영할 수 있는
개인용 agent runtime이다. 강력한 만큼 “어느 대화가 어떤 상태를 공유하는가”와
“지금 보낸 메시지가 실행 중인 작업을 중단하는가”를 먼저 알아야 안전하게 쓸 수 있다.

이 가이드는 Hermes를 Discord에서 주로 지시하는 초심자를 대상으로 한다. 설치 화면을
나열하기보다 실제 운영에서 중요한 session, profile, workspace, queue, provider,
model의 경계를 설명한다.

내용은 2026-07-30의 [Hermes Agent 공식 문서](https://hermes-agent.nousresearch.com/docs/)를
기준으로 확인했다. Hermes는 빠르게 바뀌므로 설치된 버전의 `/help`, `/model`,
`hermes --help`와 공식 문서가 이 가이드보다 우선한다.

## 이 가이드로 할 수 있는 일

- Discord에서 새 작업을 독립된 thread와 session으로 시작한다.
- 실행 중인 작업을 취소하지 않고 `/queue`와 `/steer`로 후속 지시를 보낸다.
- foreground, background, delegation, Kanban, cron 중 알맞은 실행 방식을 고른다.
- 역할별 profile에 성격, memory, tool, workspace, model을 분리한다.
- 여러 specialist agent를 Kanban의 dependency와 handoff로 운영한다.
- main·auxiliary·delegation·fallback model을 품질, 속도, 비용에 맞게 배치한다.
- Discord 접근 권한과 command approval을 최소 권한으로 설정한다.

## 먼저 기억할 다섯 문장

1. 새 목적의 일은 새 Discord thread 또는 `/new` session에서 시작한다.
2. agent가 일하는 중 평문을 보내면 기본적으로 현재 실행이 중단될 수 있으므로
   `/queue` 또는 `/steer`를 쓴다.
3. profile은 기억과 설정을 나누지만 filesystem을 격리하는 sandbox는 아니다.
4. 잠깐 병렬로 조사할 때는 delegation, 재시작을 견디는 역할 간 작업은 Kanban을 쓴다.
5. model 이름보다 작업의 실패 비용, tool-use 정확도, latency, token cost를 먼저 본다.

## 읽는 순서

1. [Hermes를 이해하는 운영 모델](./01-mental-model.md)
2. [Discord에서 안전하게 지시하기](./02-discord-operations.md)
3. [프로필·기억·지시를 분리하기](./03-profiles-and-instructions.md)
4. [작업을 실행하고 큐잉하기](./04-task-execution-and-queues.md)
5. [여러 에이전트를 함께 운영하기](./05-multi-agent-operations.md)
6. [작업에 맞는 provider와 model 고르기](./06-provider-and-model-selection.md)
7. [보안·비용·신뢰성 운영](./07-security-cost-reliability.md)
8. [운영 레시피와 문제 해결](./08-recipes-and-troubleshooting.md)

[1장: Hermes를 이해하는 운영 모델 →](./01-mental-model.md)
