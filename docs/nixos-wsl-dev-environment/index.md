---
title: NixOS-WSL 개발 환경을 Git으로 복원하기
version: 1.3
updated: 2026-07-20
---

# NixOS-WSL 개발 환경을 Git으로 복원하기

이 자료는 Linux·macOS·WSL 터미널과 언어별 버전 관리에는 익숙하지만 Nix는 처음인 개발자를 위한 실전 안내서다. NixOS-WSL의 시스템 설정과 독립 실행형 Home Manager의 사용자 설정을 하나의 Flake 저장소에 두고, 같은 사용자 환경을 네이티브 NixOS에서도 복원한다.

예제의 버전 기준은 NixOS/Nixpkgs 26.05, Home Manager 26.05, NVM 0.40.4다. 외부 입력의 실제 커밋은 각자의 `flake.lock`이 고정한다.

## 완성 후 얻는 것

- WSL 호스트 설정과 사용자 설정이 분리된 Nix Flake
- Git, tree, bat, ripgrep, Neovim, zsh, Starship, fzf, Autojump, direnv, nix-direnv를 복원하는 Home Manager 프로필
- Nix가 고정한 uv, NVM, rustup
- 프로젝트가 고정한 Python, Node.js, Rust 툴체인
- `nix develop`과 direnv로 자동 활성화되는 프로젝트별 개발 환경
- 네이티브 NixOS에서도 그대로 적용할 수 있는 사용자 프로필
- 빌드 후 전환, 업데이트, 세대 롤백을 포함한 운영 절차

Docker 구성은 이 자료의 범위에서 제외한다.

## 읽는 순서

1. [역할과 경계](./01_mental_model/chapter.md)
2. [처음부터 NixOS-WSL과 구성 저장소 만들기](./02_install_nixos_wsl/chapter.md)
3. [저장소 구조와 Flake](./03_repository_architecture/chapter.md)
4. [시스템 설정 분리](./04_system_configuration/chapter.md)
5. [독립 실행형 Home Manager](./05_home_manager/chapter.md)
6. [언어별 툴체인](./06_language_toolchains/chapter.md)
7. [`nix develop`과 direnv](./07_nix_develop/chapter.md)
8. [Git 복원 워크플로](./07_restore_workflow/chapter.md)
9. [업데이트와 문제 해결](./08_operations_and_troubleshooting/chapter.md)

## 어느 시작 경로를 사용할까

- **개인 구성 저장소가 아직 없다:** 2장에서 WSL 설치, GitHub 빈 저장소 생성, SSH 인증, 예제 복사, 첫 `flake.lock`과 push까지 진행한다.
- **이전에 만든 구성 저장소가 있다:** 새 컴퓨터에서는 8장으로 이동해 커밋된 `flake.lock`을 그대로 clone하고 복원한다.

첫 번째 경로는 원본 저장소를 만드는 일회성 초기화이고, 두 번째 경로가 이후 반복해서 사용할 복원 워크플로다.

## 함께 제공하는 예제

[전체 예제 구성](./assets/example-config/README.md)은 본문 코드의 완성본이다. 개인 저장소가 없는 첫 컴퓨터에서는 2장의 순서대로 예제를 `~/.config/nixos`에 복사하고, 로컬 Git 저장소와 원격 GitHub 저장소를 연결한 뒤 `flake.lock`을 생성해 커밋한다. 이 자료에 포함된 예제 자체에는 잠금 파일과 실제 하드웨어 설정이 없다. 둘은 사용자의 저장소와 호스트에 종속되기 때문이다.

프로젝트별 `nix develop` 실습에는 별도의 [개발 셸 예제](./assets/example-dev-shell/README.md)를 사용한다. 시스템 구성 Flake와 프로젝트 Flake는 책임과 저장소가 다르므로 예제도 분리했다.

## 가장 중요한 경계

| 대상 | 소유자 | Git에 넣는 대표 파일 |
|---|---|---|
| 사용자 계정, 기본 셸, Nix 기능, 동적 로더 | NixOS | `hosts/`, `modules/nixos/` |
| 사용자 패키지와 `$HOME` 설정 | standalone Home Manager | `modules/home/` |
| Neovim 같은 프로그램의 설정 데이터 | dotfiles, Home Manager가 배치 | `dotfiles/` |
| Nixpkgs·Home Manager·NVM 소스 리비전 | Flake lock | `flake.nix`, `flake.lock` |
| Python 버전과 의존성 | uv 프로젝트 | `.python-version`, `pyproject.toml`, `uv.lock` |
| Node.js 버전과 의존성 | NVM과 프로젝트 패키지 관리자 | `.nvmrc`, lockfile |
| Rust 툴체인과 의존성 | rustup과 Cargo | `rust-toolchain.toml`, `Cargo.lock` |
| 프로젝트별 Nix 도구와 네이티브 라이브러리 | 프로젝트 `devShell` | `flake.nix`, `flake.lock`, `.envrc` |

[1장: 역할과 경계 →](./01_mental_model/chapter.md)
