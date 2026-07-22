---
title: LazyVim 개발 환경 구축 가이드 작성 범위
version: 1.0
status: reviewed
owner: agent
updated: 2026-07-22
target_reader: 터미널, Git, vi 기초를 알고 LazyVim은 처음인 개발자
topic: Linux와 WSL에서 LazyVim 기반 다중 언어 개발 환경 구축
---

# LazyVim 개발 환경 구축 가이드 작성 범위

## 1. 주제

- 다룰 주제: Linux와 WSL의 터미널에서 LazyVim을 설치하고 JavaScript, TypeScript, Python, Rust용 편집·분석·포매팅·디버깅 환경을 구성한다.
- 중심 질문: LazyVim을 처음 쓰는 개발자가 네 언어의 LSP, 포매터, 디버거를 설치하고 각 계층의 문제를 스스로 진단하려면 무엇을 어떤 순서로 구성해야 하는가?
- 이 자료가 해결하는 문제: 플러그인, 외부 실행 파일, 프로젝트 의존성의 역할을 구분하지 못해 설치는 되었지만 LSP·포매터·디버거가 동작하지 않는 문제를 줄인다.
- 이 자료가 다루는 기술 영역: Neovim, LazyVim, lazy.nvim, LazyExtras, Mason, Language Server Protocol(LSP), conform.nvim, Debug Adapter Protocol(DAP), nvim-dap, vtsls, Pyright, Ruff, rust-analyzer, Prettier, ESLint, debugpy, js-debug-adapter, CodeLLDB.

## 2. 독자 상태 진단

### 2.1 숙련도

- 초심자: LazyVim의 구성 파일과 플러그인 관리 방식은 처음이다.
- 일부 지식이 있는 중급자: 터미널 명령, Git 저장소, vi의 모드와 기본 이동·편집은 사용할 수 있다.
- 실무 경험이 있는 중급자: 언어별 패키지 관리자나 가상환경을 사용해 본 독자도 포함하지만 필수로 가정하지 않는다.
- 전문가: 플러그인 내부 API를 직접 확장하려는 사용자는 주 대상이 아니다.
- 이 자료에서 기준으로 삼을 독자 수준: 터미널·Git·vi 입문을 마친 LazyVim 초심자.

### 2.2 선행지식

- 반드시 알고 있어야 하는 개념: 셸에서 명령 실행, 경로 이동, 파일 복사·이름 변경, Git clone·status·add·commit, vi의 Normal/Insert 모드와 저장·종료.
- 알고 있으면 좋은 개념: 각 언어의 패키지 관리자, Python 가상환경, JSON과 Lua 테이블 문법.
- 모른다고 가정할 개념: lazy.nvim plugin spec, LazyExtras, Mason의 설치 경로, LSP client/server, formatter 선택, DAP adapter/configuration/session.
- 이 자료에서 새로 설명할 개념: LazyVim 구성 계층, 언어별 extra, 외부 도구 탐색 경로, 프로젝트 루트, format-on-save, debugger adapter와 launch configuration의 관계.

### 2.3 경험 수준

- 이론 학습 경험: 프로토콜의 상세 사양은 요구하지 않는다.
- 구현 경험: 네 언어 중 하나 이상으로 작은 프로그램을 실행한 경험을 권장한다.
- 실험/측정 경험: 명령 출력과 `:checkhealth` 결과를 비교하는 수준부터 설명한다.
- 디버깅 경험: breakpoint와 step over의 의미는 짧게 다시 설명한다.
- 논문/표준 문서 독해 경험: 요구하지 않는다.

### 2.4 학습 목적

- 개념 이해: LazyVim, plugin, external tool, project dependency의 경계를 설명한다.
- 문제 풀이: 증상을 plugin → executable → project root → runtime 순서로 좁힌다.
- 구현: 재사용 가능한 Lua 설정을 작성한다.
- 설계: formatter와 linter의 중복 책임을 피하고 도구 소유권을 정한다.
- 디버깅: LSP, formatter, DAP의 상태를 각각 확인한다.
- 논문/기술문서 독해: 공식 문서에서 extra의 실제 구성과 요구사항을 찾는다.
- 실무 적용: 설정과 `lazy-lock.json`을 Git으로 관리하고 복원한다.
- 이 자료에서 우선할 학습 목적: 구현, 디버깅, 실무 적용.

### 2.5 실패 가능 지점

- 헷갈릴 용어: LazyVim과 lazy.nvim, plugin과 Mason package, LSP와 linter, debugger plugin과 debug adapter.
- 생략하면 안 되는 배경: Neovim은 실행한 셸의 `PATH`를 상속하며 plugin만 설치해도 외부 실행 파일이 자동으로 생기는 것은 아니다.
- 수식에서 막힐 지점: 수식은 사용하지 않는다.
- 코드에서 막힐 지점: Lua 파일이 table을 반환해야 하는 위치, extra import 순서, project-local executable 탐색, `.venv` 선택.
- 추상 개념과 실제 사례가 연결되지 않을 지점: `:Lazy`에는 plugin이 보이지만 `:LspInfo`에 client가 없는 상황, DAP UI는 열리지만 session이 시작되지 않는 상황.

## 3. 대상 독자

- 전공/배경: Linux 또는 WSL에서 터미널 기반 개발을 시작하려는 소프트웨어 개발자.
- 알고 있다고 가정하는 지식: 터미널, Git, vi 기초와 자신이 사용할 언어의 프로그램 실행 방법.
- 모를 가능성이 높은 지식: Neovim Lua 구성, LazyVim Extras, Mason, LSP/DAP의 계층 구조.
- 독자가 원하는 결과: 네 언어에서 코드 탐색, 진단, 자동 포매팅, breakpoint 디버깅이 동작하는 하나의 LazyVim 설정.
- 독자가 자주 막힐 지점: 오래된 Neovim, 누락된 압축 도구, 잘못된 `PATH`, 프로젝트 루트 밖에서 실행, Python 가상환경 불일치, TypeScript runtime 누락, Rust component 누락, WSL의 Windows/Linux 실행 파일 혼용.

## 4. 학습 목표

이 자료를 읽은 뒤 독자는 다음을 할 수 있어야 한다.

1. 현재 Neovim 구성을 복구 가능하게 백업하고 LazyVim Starter를 설치할 수 있다.
2. LazyVim, lazy.nvim, LazyExtras, Mason, LSP, formatter, DAP의 역할과 설치 위치를 설명할 수 있다.
3. JavaScript와 TypeScript에 vtsls, Prettier, ESLint, js-debug-adapter를 연결하고 각 기능을 확인할 수 있다.
4. Python에 Pyright, Ruff, debugpy를 연결하고 `.venv` interpreter를 선택해 디버깅할 수 있다.
5. Rust에 rust-analyzer, rustfmt, CodeLLDB를 연결하고 Cargo target을 디버깅할 수 있다.
6. `:LazyHealth`, `:checkhealth`, `:Mason`, `:LspInfo`, `:ConformInfo`와 DAP 상태를 이용해 고장 계층을 판별할 수 있다.
7. 설정 파일과 `lazy-lock.json`을 Git으로 관리하고 다른 환경에서 plugin revision을 복원할 수 있다.

## 5. 포함 범위

- 반드시 포함할 내용: 설치 전 점검과 백업, 첫 실행, 구성 디렉터리, plugin spec, extras, Mason, 공통 키맵, 네 언어의 LSP·formatter·debugger, 검증 절차, 업데이트·복원·롤백, 계층별 문제 해결.
- 선택적으로 포함할 내용: ESLint 진단과 Prettier 포매팅 책임 분리, `.vscode/launch.json` 재사용, WSL clipboard와 파일 시스템 성능 주의사항.
- 예제/실습에 포함할 내용: 공식 starter 기반 완성 설정, 언어별 최소 프로젝트 점검, 정의 이동, 진단 발생, 저장 시 포매팅, breakpoint와 step 동작 확인.
- 수식/코드/그림으로 다룰 내용: Lua 설정, 셸 명령, JSON launch configuration, 구성 계층 표와 진단 순서.

## 6. 제외 범위

- 다루지 않을 내용: Linux 배포판 또는 WSL 설치, 셸·터미널 에뮬레이터 구성, 운영체제 패키지 관리자 사용법, Git과 vi 입문, 각 언어 문법.
- 다음 장으로 넘길 내용: React·Next.js·Deno·Bun, Django·FastAPI, embedded Rust 등 framework별 설정.
- 심화 자료로 분리할 내용: Nix/Home Manager를 이용한 선언형 설치, container·SSH remote debugging, custom DAP adapter 작성, plugin 성능 프로파일링, 테스트 러너 통합.
- 독자의 선행지식으로 가정할 내용: Node.js/npm, Python 3/venv, Rust/rustup 중 실제 사용할 언어의 runtime 설치. 본문은 확인 명령과 필요한 component만 제시한다.
- 운영체제 경계: 공통 절차는 Linux 사용자 공간에서 수행한다. WSL의 Windows 실행 파일 혼용, `/mnt/c` 성능, clipboard provider처럼 특정 환경에서만 발생하는 문제만 별도 주의사항으로 언급한다.

## 7. 최종 산출물 형식

- 기준 원고 형식: Markdown
- 기준 원고 경로: `docs/lazyvim-development-environment/_work/07_final.md`
- 내부 작업 산출물 위치: `docs/lazyvim-development-environment/_work/`
- 최종 산출물 형식: MkDocs 챕터형 Markdown 학습자료
- 최종 산출물 경로: `docs/lazyvim-development-environment/`
- 챕터 수: 7
- MkDocs 책 폴더명 `<book-slug>`: `lazyvim-development-environment`
- 챕터 파일명 규칙: `NN-<chapter-slug>.md`
- 챕터 파일 배치: 책 폴더 바로 아래
- 단일 파일명: 해당 없음
- 보조 배포 형식: 실행 가능한 예제 설정 디렉터리
- 사용할 빌드 도구: MkDocs Material 9.7.6
- 수식 지원 필요 여부: 없음
- 코드 실행/검증 필요 여부: Lua 정적 검증, 링크 검사, MkDocs strict build 필요. 실제 plugin download와 언어별 debugger session은 독자 환경 의존 항목으로 분리한다.
- 인터랙티브 요소 필요 여부: 없음
- 인쇄 가능성 필요 여부: 필수 아님
- 모바일 가독성 필요 여부: 표 너비와 코드 길이를 제한하는 수준으로 고려

## 8. 성공 기준

- 독자가 풀 수 있어야 하는 문제: “plugin은 설치되었지만 LSP가 붙지 않는다”, “저장해도 포매팅되지 않는다”, “breakpoint가 무시된다”를 서로 다른 계층의 문제로 분류한다.
- 설명 없이 수행할 수 있어야 하는 작업: 새 프로젝트에서 Neovim을 열고 LSP 연결, formatter, debugger adapter 상태를 확인한다.
- 독자가 구분할 수 있어야 하는 개념: plugin revision과 Mason package version, language server와 formatter, DAP adapter와 launch configuration, global editor tool과 project dependency.
- 독자가 피할 수 있어야 하는 흔한 오류: 기존 구성 덮어쓰기, 여러 formatter의 중복 실행, Windows와 WSL binary 혼용, 프로젝트 root 밖 실행, `.venv` 미선택, Rust component 누락.

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
- [x] 책 폴더명과 챕터 파일명 규칙이 명시되어 있다.
- [x] 내부 작업 산출물 위치가 `_work/`로 분리되어 있다.
- [x] 최종 실습 과제의 방향이 드러난다.
