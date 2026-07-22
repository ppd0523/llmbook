---
title: 최종 산출물 구성과 출판 변환 검수
version: 1.8
status: complete
owner: agent
updated: 2026-07-22
target_reader: 터미널과 언어별 버전 관리에는 익숙하지만 Nix는 처음인 시니어 개발자
topic: Flake와 독립 실행형 Home Manager를 이용한 이식 가능한 NixOS 개발 환경
---

# 최종 산출물 구성과 출판 변환 검수

## 1. 최종 산출물

- 목차: `index.md`
- 본문: 9개 챕터의 `chapter.md`
- 기준 원고: `_work/07_final.md`
- 복제 가능한 사용자·시스템 구성: `assets/example-config/`
- Python·Node.js·Rust 프로젝트 환경: `assets/example-dev-shell/`
- 사이트 구성: 저장소 루트의 `mkdocs.yml`

## 2. 공통 검수

- [x] `index.md`의 목차가 9개 장에 연결된다.
- [x] 각 챕터에 코드 블록 밖 H1이 하나만 있다.
- [x] Markdown 코드 펜스가 모두 짝을 이룬다.
- [x] 깨진 상대 링크가 없다.
- [x] 최종 사용자 문서에 미완료 작업 표지가 없다.
- [x] 시스템, 사용자, 프로젝트 설정의 소유권 표와 예제가 일치한다.
- [x] `.envrc`와 `.lazy.lua`의 별도 신뢰 절차가 복원·운영 장에도 연결된다.
- [x] 3.1절 이후 구조·파일 내용 코드 블록마다 기준 루트, 경로, 전체/일부 여부가 표시된다.
- [x] 5.2장의 `programs.nix` 전체 코드가 companion asset과 일치한다.
- [x] MkDocs strict build가 통과한다.

## 3. 예제 구성 검수

- [x] `modules/home/lazyvim.nix`가 Neovim, lazy.nvim, 공통 요구사항만 제공한다.
- [x] 공통 Neovim 설정에서 Mason을 비활성화한다.
- [x] 프로젝트 `.lazy.lua`가 Python, TypeScript, Rust extra를 각각 선택한다.
- [x] 세 프로젝트 모두 `.lazy-lock.json`을 추적 대상으로 제공한다.
- [x] 프로젝트별 plugin root와 lockfile 경로가 함께 분리된다.
- [x] Python은 uv, Node.js는 NVM, Rust는 rustup이 언어 버전을 소유한다.
- [x] `flake.nix`는 언어 런타임을 중복 선언하지 않고 네이티브 의존성만 제공한다.
- [x] `.direnv`, `.venv`, `node_modules`, `target` 등 생성 상태는 Git에서 제외한다.
- [x] JSON, TOML, Nix 괄호 정적 검사가 통과한다.

## 4. 출판 검사 결과

| 검사 | 결과 |
|---|---|
| Markdown | 20개 UTF-8 읽기·코드 펜스·상대 링크 통과 |
| Chapter | 9개 H1 구조 통과 |
| JSON | 5개 파싱 통과 |
| TOML | 4개 파싱 통과 |
| Nix | 12개 괄호 수 정적 검사 통과 |
| Git diff | `git diff --check` 통과 |
| MkDocs | strict build 통과 |

## 5. 실행 환경 한계

작성 호스트에는 Nix와 Neovim이 없어 Flake 평가, NixOS·Home Manager build, Lua runtime
검증은 수행하지 않았다. 이 범위와 실제 환경에서 실행할 명령은 `_work/05_review.md`와
본문의 각 실습에 남겼다. 상태를 바꾸는 전환보다 `build`를 먼저 수행하며, 프로젝트
플러그인은 최초 `:Lazy sync` 후 생성된 `.lazy-lock.json` diff를 검토한다.

## 6. 최종 결론

- 배포 대상은 `index.md`, 9개 챕터, 두 예제 asset 디렉터리다.
- Home Manager는 최소 LazyVim 기반을, 각 프로젝트는 `.lazy.lua`와
  `.lazy-lock.json`을 소유하는 최종 구조로 정리했다.
- Markdown 사이트는 MkDocs strict build 기준으로 출판 가능하다.
- NixOS와 Neovim 실행 검증은 실제 대상 환경에서 완료해야 한다.
