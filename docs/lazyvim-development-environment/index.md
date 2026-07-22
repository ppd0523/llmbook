---
title: LazyVim으로 다중 언어 개발 환경 구축하기
version: 1.0
updated: 2026-07-22
---

# LazyVim으로 다중 언어 개발 환경 구축하기

이 가이드는 터미널, Git, vi의 기본 조작을 알고 있지만 LazyVim은 처음인 개발자를
위한 실전 안내서다. Linux와 Windows Subsystem for Linux(WSL)의 Linux shell에서
LazyVim을 설치하고 JavaScript, TypeScript, Python, Rust의 Language Server
Protocol(LSP), formatter, debugger를 연결한다.

운영체제나 WSL 자체를 설치하는 방법은 다루지 않는다. 두 환경에서 공통으로 실행할 수
있는 절차를 중심으로 설명하고, WSL의 경로·clipboard·실행 파일 혼용처럼 특정
환경에서만 생기는 문제는 별도 주의사항으로 표시한다.

내용은 2026-07-22의 공식 LazyVim 문서와 Starter를 기준으로 검토했다. 이 날짜의
LazyVim은 LuaJIT으로 빌드한 Neovim 0.11.2 이상과 Git 2.19 이상을 요구한다. 실제로
설치되는 plugin revision은 첫 실행에서 생성되는 `lazy-lock.json`이 고정한다.

## 완성 후 할 수 있는 일

- 기존 Neovim 환경을 복구할 수 있게 백업하고 LazyVim을 설치한다.
- LazyVim, lazy.nvim, LazyExtras, Mason의 역할을 구분한다.
- vtsls, Pyright, Ruff, rust-analyzer가 buffer에 연결되었는지 확인한다.
- Prettier, Ruff, rustfmt로 format source를 선택하고 충돌을 피한다.
- js-debug-adapter, debugpy, CodeLLDB로 breakpoint debugging을 시작한다.
- health check와 상태 창을 이용해 plugin, external tool, project 설정 중 고장 난 계층을 찾는다.
- 설정과 `lazy-lock.json`을 Git으로 관리하고 알려진 plugin revision으로 복원한다.

## 읽는 순서

1. [LazyVim 개발 환경의 구조](./01-architecture.md)
2. [설치와 첫 실행](./02-installation.md)
3. [공통 설정과 plugin 관리](./03-configuration.md)
4. [JavaScript와 TypeScript](./04-javascript-typescript.md)
5. [Python](./05-python.md)
6. [Rust](./06-rust.md)
7. [운영과 문제 해결](./07-troubleshooting.md)

## 이 가이드의 도구 선택

| 언어 | LSP·분석 | formatter | debugger adapter |
|---|---|---|---|
| JavaScript·TypeScript | vtsls, ESLint language server | Prettier | js-debug-adapter |
| Python | Pyright, Ruff server | Ruff formatter | debugpy |
| Rust | rust-analyzer, rustaceanvim | rustfmt | CodeLLDB |

Mason은 편집기에서 사용하는 외부 도구를 간편하게 설치한다. 반면 application runtime,
library, project lockfile과 `package.json`, `pyproject.toml`, `Cargo.toml`은 각 프로젝트가
소유한다. 이 경계를 유지해야 편집기 설정이 프로젝트 의존성 관리자를 대신하지 않는다.

## 함께 제공하는 예제

[완성된 LazyVim 설정](./assets/example-config/README.md)은 공식 Starter에 이 가이드의
extras와 도구 정책을 반영한 예제다. 본문에서는 각 파일을 직접 작성하는 이유를 먼저
설명하므로, 처음 읽을 때는 1장부터 순서대로 진행하는 편이 좋다.

[1장: LazyVim 개발 환경의 구조 →](./01-architecture.md)
