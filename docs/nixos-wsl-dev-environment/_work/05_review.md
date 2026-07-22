---
title: 기술 검증
version: 0.8
status: complete
owner: agent
updated: 2026-07-22
target_reader: 터미널과 언어별 버전 관리에는 익숙하지만 Nix는 처음인 시니어 개발자
topic: Flake와 독립 실행형 Home Manager를 이용한 이식 가능한 NixOS 개발 환경
---

# 기술 검증

## 1. 검증 대상

- NixOS, Flake, 독립 실행형 Home Manager, dotfiles, 프로젝트 저장소의 소유권 경계
- Flake 출력, NixOS·Home Manager 모듈, NVM zsh 훅, direnv·nix-direnv 연결
- Home Manager의 최소 LazyVim 기반과 프로젝트별 `.lazy.lua`, `.lazy-lock.json` 분리
- uv, NVM, rustup이 제공하는 LSP·formatter를 Neovim의 프로젝트 PATH에서 찾는 흐름
- NixOS, Nix, NixOS-WSL, Home Manager, lazy.nvim, LazyVim, Neovim, direnv,
  nix-direnv, uv, NVM, rustup의 공식 문서와 공식 소스

## 2. 주요 검토 결과

| 항목 | 발견한 문제 | 반영한 결정 | 상태 |
|---|---|---|---|
| 최초 시작 | clone할 GitHub 저장소와 Git이 이미 있다고 가정 | WSL 설치, 빈 저장소, SSH, 채널 기반 Git bootstrap, 첫 push 순으로 분리 | 반영 |
| GitHub Flake 입력 | 비인증 `github:` fetch가 REST API 403을 낼 수 있음 | 최초 Git은 `nix-shell -p git openssh`, Flake 갱신 토큰은 별도 설명 | 반영 |
| 구성 소유권 | 시스템과 사용자 설정이 한 출력에 섞일 수 있음 | NixOS host와 standalone Home Manager 출력을 분리 | 반영 |
| 외부 언어 관리자 | 다운로드한 ELF가 NixOS 로더를 찾지 못할 수 있음 | `nix-ld`의 역할과 한계를 명시 | 반영 |
| LazyVim 언어 설정 | 모든 언어 extra를 전역으로 켜면 프로젝트 요구사항을 표현하기 어려움 | Home Manager는 최소 기반, 프로젝트는 `.lazy.lua` 소유 | 반영 |
| LazyVim 재현성 | spec만 커밋하면 플러그인 리비전이 고정되지 않음 | 각 프로젝트가 `.lazy-lock.json`도 커밋 | 반영 |
| LazyVim 격리 | lock만 나누고 checkout을 공유하면 서로 다른 리비전이 충돌할 수 있음 | 프로젝트 절대 경로 hash로 plugin root도 분리 | 반영 |
| LazyVim 신뢰 | `.envrc` 승인만으로 `.lazy.lua`까지 승인된다고 오해할 수 있음 | direnv 승인과 Neovim `vim.secure.read()` 신뢰 절차를 분리 | 반영 |
| LSP 소유권 | Mason과 언어 lock이 서로 다른 LSP를 설치할 수 있음 | Mason을 끄고 uv·npm·rustup이 제공한 실행 파일만 사용 | 반영 |
| Neovim 경로 충돌 | `programs.neovim`이 만든 `init.lua`를 비재귀 `xdg.configFile."nvim"` 부모 링크 안에 추가하면서 `outside $HOME` 오류 발생 | 부모 링크를 제거하고 `init.lua` 생성과 `lua/`·`stylua.toml`·기본 lock 링크의 소유권을 분리 | 반영·평가 완료 |
| 기본 LazyVim lock | Nix Store 링크는 `lazy-lock.json`을 쓸 수 없음 | 기본 lock 파일 하나만 Git 작업 트리의 out-of-store 링크로 연결 | 반영·평가 완료 |
| 코드 블록의 파일 문맥 | 3.1절 이후 일부 구조·Nix·Lua·TOML 블록은 경로 없이 내용만 제시됨 | 디렉터리 구조에는 기준 경로를, 파일 내용에는 경로와 전체/일부 여부를 명시 | 반영 |
| 5.2장과 companion 예제 | 축약한 `programs.nix` 블록에서 bat·history·alias·zsh 통합·direnv가 보이지 않음 | 실제 asset 전체를 본문에 그대로 싣고 프로그램별 효과와 생성 상태를 설명 | 반영 |

## 3. 출처 확인

| 주장 | 1차 출처 | 확인 결과 |
|---|---|---|
| standalone Home Manager 사용과 옵션 | Home Manager 공식 문서·모듈 소스 | 사용 구조와 일치 |
| `.nvmrc`, `.python-version`, `rust-toolchain.toml` 동작 | NVM, uv, rustup 공식 문서 | 프로젝트 파일의 책임과 일치 |
| lazy.nvim의 `local_spec`, `root`, `lockfile` 옵션 | lazy.nvim 공식 구성 문서와 소스 | 프로젝트 spec·lock·cache 분리 가능 |
| `.lazy.lua` 로드 시 신뢰 확인 | lazy.nvim 소스와 Neovim `vim.secure.read()`·`:trust` 문서 | 별도 신뢰 절차 필요 |
| Python, TypeScript, Rust extra | LazyVim 공식 extra 문서 | 프로젝트별 import 이름과 일치 |
| direnv와 nix-direnv | 각 프로젝트의 공식 문서 | `.envrc`의 `use flake` 흐름과 일치 |

## 4. 정적·출판 검증

2026-07-22에 다음 검사를 실행했다.

- Markdown 20개: UTF-8 읽기, 코드 펜스 짝, 상대 링크 대상 검사
- 최종 챕터 9개: 코드 블록 밖 H1이 각각 하나인지 검사
- JSON 6개와 TOML 4개: Python 표준 파서로 구문 검사
- Nix 파일 12개: 괄호·대괄호·중괄호 개수 정적 대조
- `git diff --check`: 공백 오류 검사
- MkDocs strict build: 내부 링크와 내비게이션을 포함한 사이트 빌드
- 3.1절부터 9장까지: 디렉터리 구조의 `경로:`와 Nix·Lua·TOML·zsh·`.envrc` 내용 블록의 `파일:` 표기 전수 검사
- 5.2장의 Nix 코드 블록과 `assets/example-config/modules/home/programs.nix`의 텍스트 일치 검사

결과는 모두 통과했다. 기본 lock과 세 프로젝트의 초기 `.lazy-lock.json`은 유효한 빈
JSON 객체이며, 최초 `:Lazy sync`가 실제 플러그인 리비전을 기록하도록 문서화했다.
8장과 9장의 코드 블록은 실행 명령 또는 진단 흐름이며 파일 내용 블록이 아님을 확인했다.

수정된 `assets/example-config/modules/home/lazyvim.nix`를 사용한 standalone Home Manager
구성은 사용자 NixOS-WSL 환경에서 정상 평가되었다. 기존
`Error installing file '.config/nvim/init.lua' outside $HOME` 오류가 제거됨을 확인했다.

## 5. 실행하지 못한 검증

작성 호스트에는 Nix, NixOS-WSL, Neovim, Lua 실행기가 없다. Home Manager 평가는 사용자
NixOS-WSL에서 확인했으며 다음은 실제 NixOS-WSL 또는 네이티브 NixOS에서 추가로
확인해야 한다.

- `nix flake check`, `nixos-rebuild build`, 수정 구성의 Home Manager `switch`
- Home Manager가 제공한 lazy.nvim에서 `require("lazy")`가 로드되는지
- `.lazy.lua` 신뢰 프롬프트, 프로젝트별 plugin root와 `.lazy-lock.json` 선택
- uv·NVM·rustup으로 설치한 basedpyright, Ruff, vtsls, Prettier, rust-analyzer 연결

문서는 상태를 변경하는 `switch` 전에 `build`를 수행하도록 구성했다. LazyVim 예제도
빈 lock을 커밋한 뒤 실제 환경에서 `:Lazy sync`, `:LazyHealth`, `:LspInfo`로 확인하도록
구성했다.

## 6. 남은 위험

- 예제는 `~/.config/nixos`를 고정 clone 위치로 사용한다. 다른 위치를 선택하면
  `lua/`, `stylua.toml`, 기본 lock의 `mkOutOfStoreSymlink` 대상도 바꿔야 한다.
- 프로젝트별 plugin root는 격리를 얻는 대신 같은 플러그인의 디스크 캐시를 중복한다.
- Mason을 비활성화했으므로 LSP, formatter, DAP가 필요하면 프로젝트 의존성 또는
  툴체인 파일에 명시해야 한다.
- 실제 네이티브 NixOS 시스템 복원에는 각 장비의 하드웨어와 부트 정책 검토가 필요하다.

## 7. 검증 결론

- 최종 문서와 예제의 시스템·사용자·프로젝트 책임 경계가 일치한다.
- 분리한 Neovim 경로 소유권은 사용자 NixOS-WSL의 Home Manager 평가를 통과했다.
- 프로젝트는 `.lazy.lua`와 `.lazy-lock.json`을 함께 커밋하며, direnv는 환경 활성화만
  담당한다.
- 정적 검사와 MkDocs strict build는 통과했다.
- 전체 NixOS build와 Neovim 실행 검증은 실제 NixOS 환경의 후속 검증 항목으로 명시했다.
