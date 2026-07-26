---
title: 작성 범위 정의
version: 1.0
status: final
owner: agent
updated: 2026-07-24
target_reader: Nix 기초는 알지만 Flake는 처음인 개발자
topic: Nix Flake의 입출력과 재현 가능한 개발 워크플로
---

# 작성 범위 정의

## 1. 주제

- 다룰 주제: Nix Flake의 구조, 입력 잠금, 개발 셸, 패키지, 앱, 검사와 운영
- 중심 질문: `flake.nix` 하나를 어떻게 읽고 확장하여 재현 가능한 개발 환경과 실행 가능한 패키지를 만드는가?
- 이 자료가 해결하는 문제: 복사해 온 Flake를 이해하지 못한 채 수정하거나, `flake.lock`과 출력 스키마를 혼동하여 빌드·실행·업데이트에 실패하는 문제
- 이 자료가 다루는 기술 영역: Nix 2.34, Nixpkgs 26.05, Flake input/output, `devShells`, `packages`, `apps`, `checks`, `formatter`

## 2. 독자 상태 진단

### 2.1 숙련도

- 초심자: Flake에 대해서는 초심자다.
- 일부 지식이 있는 중급자: Nix Store와 선언적 패키지 관리의 목적을 알고 간단한 Nix 속성 집합을 읽을 수 있다.
- 실무 경험이 있는 중급자: Git, 셸, 언어별 패키지 관리자와 잠금 파일을 사용해 봤다.
- 전문가: 해당 없음
- 이 자료에서 기준으로 삼을 독자 수준: Nix 기초는 알지만 Flake를 처음 직접 작성하는 개발자

### 2.2 선행지식

- 반드시 알고 있어야 하는 개념: 터미널 명령, Git 저장소, 환경 변수, 패키지와 실행 파일의 차이
- 알고 있으면 좋은 개념: Nix 속성 집합, 함수, `let ... in`, Nix Store
- 모른다고 가정할 개념: Flake reference, input, output schema, `flake.lock`, installable
- 이 자료에서 새로 설명할 개념: 입력 고정, 시스템별 출력, 개발 셸, 패키지와 앱의 차이, 검사 출력

### 2.3 경험 수준

- 이론 학습 경험: 일반적인 개발 환경과 의존성 잠금 개념을 이해한다.
- 구현 경험: 작은 CLI 프로젝트를 실행해 본 경험이 있다.
- 실험/측정 경험: 명령 출력과 종료 상태를 확인할 수 있다.
- 디버깅 경험: PATH와 잘못된 파일명 같은 기본 오류를 추적할 수 있다.
- 논문/표준 문서 독해 경험: 필수로 가정하지 않는다.

### 2.4 학습 목적

- 개념 이해: `flake.nix`, `flake.lock`, input, output의 관계를 설명한다.
- 문제 풀이: 명령이 찾는 출력 경로를 추적한다.
- 구현: `cowsay`가 들어 있는 개발 셸과 실행 가능한 패키지를 만든다.
- 설계: 시스템별 중복을 줄이고 검증 가능한 출력 구조를 설계한다.
- 디버깅: 평가, 빌드, 실행, 잠금 갱신 오류를 구분한다.
- 논문/기술문서 독해: Nix reference manual에서 명령별 출력 탐색 규칙을 찾는다.
- 실무 적용: 작은 프로젝트에 Flake를 도입하고 잠금 파일을 검토해 커밋한다.
- 이 자료에서 우선할 학습 목적: 구현, 개념 이해, 디버깅 순으로 우선한다.

### 2.5 실패 가능 지점

- 헷갈릴 용어: Nix와 Nixpkgs, 패키지와 앱, `nix shell`과 `nix develop`, input URL과 잠긴 revision
- 생략하면 안 되는 배경: Flake 기능의 실험적 상태, Git 추적 파일 규칙, 시스템별 출력 경로
- 수식에서 막힐 지점: 수식은 사용하지 않는다.
- 코드에서 막힐 지점: `outputs` 함수 인자, 동적 속성 이름 `${system}`, 셸 문자열의 `${...}` 이스케이프
- 추상 개념과 실제 사례가 연결되지 않을 지점: 출력 속성과 `nix build`·`nix run`·`nix develop` 명령의 대응

## 3. 대상 독자

- 전공/배경: 터미널 기반 개발 환경을 사용하는 개발자
- 알고 있다고 가정하는 지식: Git, 셸, 패키지 관리자, 간단한 Nix 표현식
- 모를 가능성이 높은 지식: Flake 출력 스키마와 잠금 파일 운영
- 독자가 원하는 결과: 작은 프로젝트 Flake를 직접 만들고 안전하게 갱신한다.
- 독자가 자주 막힐 지점: 시스템 이름 하드코딩, 잘못된 출력 이름, 커밋되지 않은 파일, 무분별한 lock 갱신

## 4. 학습 목표

이 자료를 읽은 뒤 독자는 다음을 할 수 있어야 한다.

1. `flake.nix`의 `inputs`와 `outputs`, `flake.lock`의 역할을 설명할 수 있다.
2. `nix flake show` 결과에서 `nix develop`, `nix build`, `nix run`이 선택할 출력을 찾을 수 있다.
3. Nixpkgs의 `cowsay`를 제공하는 `devShells.<system>.default`를 작성할 수 있다.
4. `writeShellApplication`으로 패키지를 만들고 `apps`에서 실행할 수 있다.
5. `formatter`와 `checks`를 추가하고 `nix fmt`, `nix flake check`로 검증할 수 있다.
6. `flake.lock` 변경을 diff로 검토하고 전체 또는 특정 input만 갱신할 수 있다.
7. 평가·빌드·실행·잠금 오류를 단계별로 진단할 수 있다.

## 5. 포함 범위

- 반드시 포함할 내용: Flake의 현재 상태, input/output, lock file, system 축, 개발 셸, 패키지, 앱, formatter, checks, 업데이트와 문제 해결
- 선택적으로 포함할 내용: NixOS·Home Manager Flake와 일반 프로젝트 Flake의 연결점
- 예제/실습에 포함할 내용: Nixpkgs 26.05의 `cowsay`, `nixfmt`, `writeShellApplication`, 네 시스템 출력, 실행 검사
- 수식/코드/그림으로 다룰 내용: 입력에서 출력과 명령으로 이어지는 흐름, 완성형 `flake.nix`, 명령별 출력 탐색 표

## 6. 제외 범위

- 다루지 않을 내용: Nix 설치 전체 과정, Nix 언어 입문 전체, NixOS 설치, 자체 컴파일 derivation, overlay, binary cache, 원격 builder
- 다음 장으로 넘길 내용: NixOS와 Home Manager 모듈의 완전한 구성
- 심화 자료로 분리할 내용: flake-parts, 크로스 컴파일, content-addressed derivation
- 독자의 선행지식으로 가정할 내용: Git 기본 명령과 셸에서 디렉터리를 이동하는 방법

## 7. 최종 산출물 형식

- 기준 원고 형식: Markdown
- 기준 원고 경로: `docs/nix-flakes/_work/07_final.md`
- 내부 작업 산출물 위치: `docs/nix-flakes/_work/`
- 최종 산출물 형식: MkDocs 챕터형 Markdown 학습자료
- 최종 산출물 경로: `docs/nix-flakes/`
- 챕터 수: 6
- MkDocs 책 폴더명 `<book-slug>`: `nix-flakes`
- 챕터 파일명 규칙: `NN-<chapter-slug>.md`
- 챕터 파일 배치: 책 폴더 바로 아래
- 단일 파일명: 해당 없음
- 보조 배포 형식: `assets/flake-greeter/` 완성형 예제
- 사용할 빌드 도구: MkDocs Material 9.7.6
- 수식 지원 필요 여부: 불필요
- 코드 실행/검증 필요 여부: 필요
- 인터랙티브 요소 필요 여부: 불필요
- 인쇄 가능성 필요 여부: 불필요
- 모바일 가독성 필요 여부: 필요

## 8. 성공 기준

- 독자가 풀 수 있어야 하는 문제: 주어진 명령이 선택하는 Flake 출력 경로를 찾고 잘못된 출력명을 수정한다.
- 설명 없이 수행할 수 있어야 하는 작업: `cowsay` 개발 셸을 만들고 종합 예제를 빌드·실행·검사한다.
- 독자가 구분할 수 있어야 하는 개념: input URL과 잠긴 revision, package와 app, 임시 shell과 프로젝트 dev shell
- 독자가 피할 수 있어야 하는 흔한 오류: 시스템 축 누락, `flake.lock` 미커밋, 전체 input의 무의식적 갱신, Git 미추적 소스 누락

## 9. 품질 점검

- [x] 중심 질문이 하나로 정리되어 있다.
- [x] 독자 숙련도가 명시되어 있다.
- [x] 독자의 선행지식과 모른다고 가정할 개념이 분리되어 있다.
- [x] 학습 목적이 명시되어 있다.
- [x] 대상 독자의 선행지식이 명시되어 있다.
- [x] 학습 목표가 행동 중심으로 작성되어 있다.
- [x] 포함 범위와 제외 범위가 분리되어 있다.
- [x] 기준 원고 형식이 Markdown으로 명시되어 있다.
- [x] 최종 산출물 형식과 경로가 명시되어 있다.
- [x] MkDocs 책 폴더명과 챕터 파일명 규칙이 명시되어 있다.
- [x] 내부 작업 산출물 위치가 `_work/`로 분리되어 있다.
- [x] 최종 실습 과제의 방향이 드러난다.
