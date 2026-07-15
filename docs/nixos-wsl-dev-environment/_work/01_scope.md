---
title: 작성 범위 정의
version: 1.1
status: final
owner: agent
updated: 2026-07-15
target_reader: 터미널 기반 개발 환경에 익숙하지만 Nix 생태계는 처음인 시니어 개발자
topic: NixOS-WSL과 네이티브 NixOS에서 재현 가능한 개발 환경 구축
---

# 작성 범위 정의

## 1. 주제

- 다룰 주제: NixOS-WSL과 네이티브 NixOS에서 공통으로 사용할 수 있는 선언적 개발 환경 구축
- 중심 질문: 하나의 Git 저장소에서 시스템 설정과 사용자 설정을 분리하면서 NixOS-WSL과 네이티브 NixOS의 개발 환경을 어떻게 재현하는가?
- 이 자료가 해결하는 문제: 새 NixOS 환경에서 수동 설치와 dotfile 복사를 반복하지 않고, 저장소 복제와 최소한의 적용 명령으로 이전 개발 환경을 복원한다.
- 이 자료가 다루는 기술 영역: Nix, Nixpkgs, NixOS 모듈, Flake, NixOS-WSL, 독립 실행형 Home Manager, dotfiles, 언어별 툴체인 관리자

## 2. 독자 상태 진단

### 2.1 숙련도

- 초심자: Nix 생태계에 대해서는 초심자다.
- 일부 지식이 있는 중급자: 해당 없음
- 실무 경험이 있는 중급자: Ubuntu, Windows WSL, macOS 터미널과 개발 환경 구성에는 높은 숙련도가 있다.
- 전문가: Git, Node.js, Python, uv, nvm 등 개발 및 버전 관리 도구를 실무에서 깊이 사용했다.
- 이 자료에서 기준으로 삼을 독자 수준: 개발 환경에는 숙련됐지만 Nix의 용어, 평가 모델, 모듈 시스템은 처음 접하는 시니어 개발자

### 2.2 선행지식

- 반드시 알고 있어야 하는 개념: 셸 명령, Git 저장소, 환경 변수, 패키지 관리자, 사용자와 시스템 설정의 차이
- 알고 있으면 좋은 개념: WSL 배포판 관리, dotfiles, 언어별 잠금 파일, systemd
- 모른다고 가정할 개념: Nix 표현식, derivation, Nix Store, generation, NixOS module, Flake input/output, Home Manager module
- 이 자료에서 새로 설명할 개념: Nix의 선언적 모델, Flake와 잠금 파일, NixOS와 Home Manager의 책임 분리, 호스트별 모듈 합성, 세대 기반 롤백

### 2.3 경험 수준

- 이론 학습 경험: 일반적인 운영체제와 개발 도구의 구성 개념을 이해한다.
- 구현 경험: 여러 언어와 CLI 도구를 이용해 개발 환경을 직접 구성한 경험이 많다.
- 실험/측정 경험: 명령 실행 결과와 로그를 확인할 수 있다.
- 디버깅 경험: PATH, 셸 초기화, 버전 충돌 문제를 진단할 수 있다.
- 논문/표준 문서 독해 경험: 공식 기술 문서를 읽고 적용할 수 있다.

### 2.4 학습 목적

- 개념 이해: NixOS, Flake, Home Manager, dotfiles의 역할과 경계를 구분한다.
- 문제 풀이: 평가 오류, 충돌, 버전 고정과 PATH 문제의 원인을 찾는다.
- 구현: 복제 가능한 Flake 기반 구성 저장소를 직접 만든다.
- 설계: 공통 설정, 호스트 설정, 사용자 설정, 프로그램별 dotfiles를 분리한다.
- 디버깅: 빌드, 적용, 업데이트, 롤백 과정의 실패 지점을 구분한다.
- 논문/기술문서 독해: NixOS와 Home Manager 공식 옵션 문서를 찾아 읽는다.
- 실무 적용: 새 NixOS-WSL 또는 네이티브 NixOS에 기존 개발 환경을 복원한다.
- 이 자료에서 우선할 학습 목적: 설계, 구현, 복원, 운영 순으로 우선한다.

### 2.5 실패 가능 지점

- 헷갈릴 용어: Nix와 NixOS, package와 module, Flake와 Home Manager, 선언적 설정과 dotfiles
- 생략하면 안 되는 배경: Nix Store의 불변성, `flake.lock`의 역할, `stateVersion`의 의미, 시스템과 사용자 활성화의 차이
- 수식에서 막힐 지점: 수식은 사용하지 않는다.
- 코드에서 막힐 지점: Nix 함수 인자, 속성 집합, `imports`, `specialArgs`, 동적 속성 이름
- 추상 개념과 실제 사례가 연결되지 않을 지점: 어느 패키지와 설정을 NixOS 또는 Home Manager에 둘지 판단하는 기준

## 3. 대상 독자

- 전공/배경: Ubuntu, Windows WSL, macOS의 터미널 환경에 익숙한 시니어 개발자
- 알고 있다고 가정하는 지식: Git, 셸, PATH, Node.js, Python, uv, nvm, 일반적인 패키지 및 버전 관리
- 모를 가능성이 높은 지식: Nix 언어, Nixpkgs, NixOS 모듈, Flake, Home Manager
- 독자가 원하는 결과: Git 저장소를 복제한 뒤 최소 명령으로 동일한 사용자 개발 환경을 복원한다.
- 독자가 자주 막힐 지점: Nix 구성 계층의 책임 혼합, 잠금 파일과 상태 버전 혼동, 사용자 셸과 Home Manager 활성화 순서

## 4. 학습 목표

이 자료를 읽은 뒤 독자는 다음을 할 수 있어야 한다.

1. Nix, NixOS, Flake, Home Manager, dotfiles의 역할을 설명하고 설정 항목을 올바른 계층에 배치할 수 있다.
2. 공통 NixOS 모듈과 WSL·네이티브 호스트 모듈을 분리할 수 있다.
3. 독립 실행형 Home Manager로 공통 사용자 개발 환경과 dotfiles를 구성할 수 있다.
4. uv, nvm, rustup 자체는 Home Manager로 관리하고 프로젝트별 언어 버전은 각 도구의 파일로 고정할 수 있다.
5. 첫 컴퓨터에서 GitHub 구성 저장소를 생성하고, 이후 새 환경에서는 이를 복제해 시스템과 사용자 구성을 순서대로 적용할 수 있다.
6. `flake.lock`을 의도적으로 갱신하고 NixOS 및 Home Manager 세대를 롤백할 수 있다.
7. 같은 사용자 환경을 NixOS-WSL과 네이티브 NixOS에서 재사용할 수 있다.

## 5. 포함 범위

- 반드시 포함할 내용: Nix 생태계의 최소 개념, WSL과 NixOS-WSL 최초 설치, GitHub 빈 저장소와 SSH 인증 생성, Flake 구조, 독립 실행형 Home Manager, NixOS와 사용자 구성 분리, 호스트별 모듈, 복원, 업데이트, 롤백, 문제 해결
- 선택적으로 포함할 내용: `nix flake check`를 이용한 정적 확인, Git에 커밋할 파일과 런타임 상태의 구분
- 예제/실습에 포함할 내용: `git`, `tree`, `bat`, `ripgrep`, Neovim, zsh, Starship, fzf, autojump, uv, nvm, rustup의 설치와 기본 설정
- 수식/코드/그림으로 다룰 내용: 완성형 저장소 트리, Flake 입출력 구조, NixOS 모듈, Home Manager 모듈, dotfile 배치, 복원 명령
- 언어 버전 관리 원칙: uv는 Python, nvm은 Node.js, rustup은 Rust 툴체인을 프로젝트 파일에 따라 설치하고 전환한다.

## 6. 제외 범위

- 다루지 않을 내용: Docker, GUI 데스크톱, 비밀키와 SSH 개인키 배포, macOS 또는 비-NixOS Linux의 실제 구성
- 다음 장으로 넘길 내용: sops-nix 등 비밀 관리, CI에서의 Nix 빌드, 원격 빌더와 바이너리 캐시
- 심화 자료로 분리할 내용: 자체 패키지 derivation 작성, overlay 설계, flake-parts, 크로스 컴파일
- 독자의 선행지식으로 가정할 내용: Git 기본 명령, zsh 문법, 각 언어의 프로젝트 및 잠금 파일 기본 사용법

## 7. 최종 산출물 형식

- 기준 원고 형식: Markdown
- 기준 원고 경로: `nixos-wsl-dev-environment/_work/07_final.md`
- 내부 작업 산출물 위치: `nixos-wsl-dev-environment/_work/`
- 최종 산출물 형식: 챕터형 Markdown 학습자료
- 최종 산출물 경로: `nixos-wsl-dev-environment/`
- 챕터 수: 8
- 챕터 폴더 구조: `01_mental_model`부터 `08_operations_and_troubleshooting`까지 번호 순서로 구성
- 단일 파일명: 해당 없음
- 보조 배포 형식: `assets/example-config/`에 완성형 예제 구성 저장소 제공
- 사용할 빌드 도구: 별도 출판 변환 없음
- 수식 지원 필요 여부: 불필요
- 코드 실행/검증 필요 여부: 필요. 가능한 범위에서 Nix 평가와 명령 구문을 검증하고 실행 불가능한 환경 제약은 내부 검증 기록에 남긴다.
- 인터랙티브 요소 필요 여부: 불필요
- 인쇄 가능성 필요 여부: 불필요
- 모바일 가독성 필요 여부: 기본 Markdown 가독성 확보

## 8. 성공 기준

- 독자가 풀 수 있어야 하는 문제: 주어진 설정을 NixOS, Flake, Home Manager, dotfiles 중 어느 계층에 둘지 판단한다.
- 설명 없이 수행할 수 있어야 하는 작업: 제공 예제를 자신의 GitHub 저장소로 초기화하고, 사용자명과 호스트에 맞게 수정한 뒤 시스템 및 사용자 구성을 적용한다.
- 독자가 구분할 수 있어야 하는 개념: 시스템 상태와 사용자 상태, 입력 잠금과 상태 버전, 패키지 설치와 프로젝트 툴체인 설치
- 독자가 피할 수 있어야 하는 흔한 오류: 루트에서 Home Manager 실행, 평문 비밀 커밋, `stateVersion`의 무분별한 변경, 두 계층에서 같은 설정 중복 관리

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
- [x] 내부 작업 산출물 위치가 `<자료폴더>/_work/`로 분리되어 있다.
- [x] 최종 연습문제 또는 실습 과제의 방향이 드러난다.
