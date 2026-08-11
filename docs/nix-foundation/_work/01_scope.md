---
title: 작성 범위 정의
version: 0.2
status: final
owner: agent
updated: 2026-08-11
target_reader: Nix를 처음 배우는 개발자와 NixOS·Home Manager 입문자
topic: Nix 기초 학습자료 퇴고
---

# 작성 범위 정의

## 1. 주제

- 다룰 주제: Nix, Nixpkgs, Flake, Store, 개발 셸, module, NixOS, Home Manager의 기초
- 중심 질문: Nix 설정과 명령을 입력·평가·실현·활성화의 흐름과 책임 계층으로 어떻게 안전하게 읽고 적용하는가?
- 이 자료가 해결하는 문제: 비슷한 명령과 설정 위치를 혼동해 원치 않는 시스템·사용자·프로젝트 변경을 하는 문제
- 이 자료가 다루는 기술 영역: Nix 2.34, NixOS/Nixpkgs 26.05, Home Manager 26.05

## 2. 독자 상태 진단

### 2.1 숙련도

- 기준 독자 수준: Nix 지식은 없지만 터미널, 패키지, 환경 변수와 Git의 기본 사용법은 아는 초심 개발자

### 2.2 선행지식

- 반드시 알고 있어야 하는 개념: 파일·디렉터리, 터미널, 편집기, Git의 변경 확인
- 모른다고 가정할 개념: Nix 표현식, Store, derivation, closure, Flake, module, generation
- 처음 등장할 때 설명할 새 용어: Nixpkgs, installable, profile, evaluation, realisation, activation, option, `stateVersion`

### 2.3 학습 목적

- 우선할 학습 목적: 개념 이해와 안전한 명령·설정 적용
- 실패 가능 지점: `nix shell`과 `nix develop`의 혼동, `build`와 `switch`의 혼동, Git source와 Store 결과의 혼동, NixOS와 Home Manager option의 혼동

## 3. 학습 목표

이 자료를 읽은 뒤 독자는 다음을 할 수 있어야 한다.

1. 작업의 소유 범위에 따라 NixOS, Home Manager, 프로젝트 Flake, `nix shell`을 선택한다.
2. Store 결과, generation, source 이력을 구분하고 안전한 검증·롤백 흐름을 설명한다.
3. Nix 코드와 module option을 읽고, 공식 문서에서 현재 release의 정의를 확인한다.

## 4. 범위

- 반드시 포함할 내용: 기존 8개 장의 개념 흐름, 실행 가능한 명령 예제, 연습과 문제 해결 기준
- 제외할 내용: NixOS 설치, 패키지 제작 심화, overlay, cross compilation, secret 도구의 선택과 운영
- 최종 산출물: MkDocs 챕터형 Markdown 학습자료

## 5. 최종 산출물 형식

- 기준 원고 형식: Markdown
- 기준 원고 경로: `docs/nix-foundation/_work/07_final.md`
- 내부 작업 산출물 위치: `docs/nix-foundation/_work/`
- 최종 산출물 경로: `docs/nix-foundation/index.md`, `docs/nix-foundation/01-ecosystem-and-mental-model.md`부터 `08-troubleshooting-and-next-steps.md`
- MkDocs 책 폴더명: `nix-foundation`
- 챕터 파일명 규칙: `NN-<chapter-slug>.md`
- 사용할 빌드 도구: MkDocs

## 6. 성공 기준

- 독자는 임시 도구, 프로젝트 개발 환경, 사용자 설정, 시스템 설정의 소유 계층을 구분한다.
- 독자는 `build`, `test`, `switch`가 현재 상태에 미치는 영향을 구분한다.
- 모든 새 용어는 처음 등장한 장에서 필요성·정의·적용 맥락을 제공한다.
- 최종 문서에는 내부 메모나 미검증 표시가 없다.

## 7. 품질 점검

- [x] 중심 질문이 하나로 정리되어 있다.
- [x] 독자 숙련도와 선행지식이 명시되어 있다.
- [x] 학습 목표가 행동 중심으로 작성되어 있다.
- [x] 포함 범위와 제외 범위가 분리되어 있다.
- [x] 최종 산출물 형식과 경로가 명시되어 있다.
