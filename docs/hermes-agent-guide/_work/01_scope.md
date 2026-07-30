---
title: 작성 범위 정의
version: 1.0
status: complete
owner: agent
updated: 2026-07-30
target_reader: Hermes Agent를 Discord 중심으로 처음 운영하는 사용자
topic: Hermes Agent 운영 가이드
---

# 작성 범위 정의

## 주제와 중심 질문

- 다룰 주제: Hermes Agent의 기능, Discord 사용법, 프로필, 작업 큐, 다중 에이전트,
  provider·model 선택, 보안과 장애 대응
- 중심 질문: Hermes가 어떤 상태와 실행 단위를 가지는지 이해하고, 작업에 맞는 실행
  방식과 에이전트를 안전하게 선택하려면 어떻게 해야 하는가?
- 해결할 문제: 일반 메시지, `/background`, delegation, Kanban, cron을 구분하지 못해
  작업을 중단하거나 잃는 문제와 여러 프로필의 지시·기억·작업 공간이 섞이는 문제

## 독자 상태 진단

- 기준 독자: 터미널 명령을 복사해 실행할 수 있지만 Hermes의 동작 방식은 모르는 사용자
- 알고 있다고 가정하는 지식: Discord의 채널·스레드·멘션, 파일과 디렉터리의 기본 개념
- 모른다고 가정하는 개념: 세션 키, gateway, profile, toolset, delegation, Kanban,
  auxiliary model, fallback
- 우선 학습 목적: 실무 운영과 문제 해결
- 실패 가능 지점: 프로필을 sandbox로 오해하기, 바쁜 에이전트에게 평문을 보내 실행을
  중단하기, background 작업에 현재 대화 맥락이 전달된다고 가정하기, 동일 bot token을
  여러 profile에 재사용하기

## 학습 목표

이 자료를 읽은 뒤 독자는 다음을 할 수 있어야 한다.

1. 대화, background, delegation, Kanban, cron 중 작업에 맞는 실행 단위를 선택한다.
2. Discord에서 작업을 중단하지 않고 수정·큐잉·병렬 실행한다.
3. `SOUL.md`, project context, memory, 현재 지시의 책임을 분리한다.
4. 역할별 profile과 고유 gateway를 구성하고 Kanban으로 협업시킨다.
5. main·auxiliary·delegation·fallback model을 비용과 품질에 맞게 배치한다.
6. 권한, 승인, 작업 공간, 비용을 점검하고 흔한 장애를 진단한다.

## 포함 범위

- Hermes의 주요 도구와 상태 단위
- Discord session, thread, 명령, interrupt·queue·steer
- profile 생성·복제·설명·gateway 운영
- persistent memory와 context file의 책임
- background, delegation, Kanban, cron의 선택 기준
- 역할형 다중 에이전트 구성과 handoff 규칙
- provider·model·auxiliary·fallback 선택 전략
- allowlist, command approval, workspace와 sandbox 주의사항
- 복사해 사용할 수 있는 지시 템플릿과 운영 점검표

## 제외 범위

- Hermes 설치 전 과정을 운영체제별로 반복 설명
- Discord Developer Portal의 모든 화면을 단계별로 재현
- 특정 provider의 가격표 또는 영구적인 모델 순위
- Hermes 내부 코드 구조와 plugin 개발
- 모든 slash command와 config key의 완전한 reference

## 최종 산출물

- 기준 원고: `docs/hermes-agent-guide/_work/07_final.md`
- 최종 형식: MkDocs 챕터형 Markdown
- 최종 경로: `docs/hermes-agent-guide/`
- 책 폴더명: `hermes-agent-guide`
- 챕터 수: 8장과 `index.md`
- 파일명 규칙: `NN-<chapter-slug>.md`
- 보조 형식: 없음
- 검증: MkDocs strict build, 내부 링크 검사, 공식 문서와 명령 대조
- 기준 시점: 2026-07-30

## 성공 기준

- 독자가 새 작업을 어느 Discord thread와 어떤 실행 단위에 넣을지 판단할 수 있다.
- 여러 메시지를 보내도 실행 중 작업을 의도치 않게 취소하지 않는다.
- 역할별 profile의 상태·도구·작업 공간·model을 분리한다.
- 충돌하는 지시를 발견하면 책임 위치를 찾아 한곳에서 정리한다.
- 장기 작업을 Kanban에 넣고 의존성과 완료 기준을 기록한다.
- 모델 이름이 바뀌어도 품질·속도·비용·privacy 기준으로 대안을 선택한다.
