---
title: NixOS에서 standalone Home Manager 운영하기
version: 1.0
updated: 2026-07-23
baseline: NixOS 26.05, Home Manager 26.05
---

# NixOS에서 standalone Home Manager 운영하기

이 가이드는 [NixOS-WSL 개발 환경 매뉴얼](../nixos-wsl-dev-environment/index.md)을 따라
NixOS와 Home Manager 설치를 마친 사용자가 사용자 환경을 직접 수정하고 안전하게
운영하도록 돕는 후속 자료다.

본문은 기존 예제와 같은 Flake 기반 standalone 방식을 사용한다. NixOS 설정은
`nixos-rebuild`, 사용자 설정은 `home-manager`가 각각 담당한다. Home Manager를
NixOS 모듈로 통합하는 방식은 차이를 판단할 수 있을 정도로만 비교한다.

## 이 가이드에서 만드는 것

- `home.packages`로 관리하는 사용자 패키지
- Git, zsh, Starship, direnv처럼 설정까지 함께 관리하는 프로그램
- 로그인 환경 변수와 사용자 `PATH`
- Home Manager 옵션과 기존 dotfiles를 함께 사용하는 구조
- 변경을 적용하기 전에 검증하는 `build` → `switch` 작업 흐름
- Home Manager generation과 Git을 이용한 복구 절차

Neovim 전체 구성, NVM·uv·rustup 사용법과 프로젝트별 개발 셸은 기존
[NixOS-WSL 개발 환경 매뉴얼](../nixos-wsl-dev-environment/index.md)에서 다룬다.
SSH 개인 키, API 토큰 같은 비밀정보를 저장하는 방법은 이 가이드의 범위가 아니다.

## 전제 조건

- NixOS가 설치되어 있다.
- 기존 매뉴얼의 예제 구성은 `~/.config/nixos`에 있다.
- `flake.lock`이 Git에 커밋되어 있다.
- 다음 두 명령이 성공한다.

  ```console
  $ sudo nixos-rebuild build --flake ~/.config/nixos#wsl
  $ home-manager build --flake ~/.config/nixos#nixos
  ```

여기서 `wsl`은 NixOS host output이고 `nixos`는 Home Manager 사용자 output이다.
자신의 Flake에서 이름을 바꿨다면 이후 명령에서도 같은 이름으로 바꾼다.

## 표준 명령

| 변경 대상 | 검증 | 적용 |
|---|---|---|
| NixOS 시스템 | `sudo nixos-rebuild build --flake .#wsl` | `sudo nixos-rebuild switch --flake .#wsl` |
| Home Manager 사용자 환경 | `home-manager build --flake .#nixos` | `home-manager switch --flake .#nixos` |
| 두 계층 또는 `flake.lock` | 두 `build` 명령 모두 | NixOS를 먼저, Home Manager를 나중에 `switch` |

모든 명령은 특별한 설명이 없으면 다음 디렉터리에서 실행한다.

```console
$ cd ~/.config/nixos
```

## 읽는 순서

1. [Home Manager의 역할과 경계](./01-mental-model.md)
2. [Flake와 모듈 구조 읽기](./02-configuration-structure.md)
3. [패키지와 프로그램 설정](./03-packages-and-programs.md)
4. [Home Manager 옵션과 dotfiles 함께 사용하기](./04-dotfiles.md)
5. [빌드, 적용, 업데이트, 롤백](./05-apply-and-rollback.md)
6. [문제 해결](./06-troubleshooting.md)

## 버전 정책

예제는 NixOS/Nixpkgs 26.05와 Home Manager 26.05를 기준으로 한다. 실제 소스
리비전은 `flake.lock`이 고정한다. 새 릴리스로 이동할 때는 Nixpkgs와 Home Manager의
release branch를 함께 갱신하지만, `home.stateVersion`은 릴리스 번호를 따라 자동으로
올리지 않는다.

Home Manager 공식 문서도 stable Nixpkgs와 대응하는 Home Manager release를 사용하고,
기존 home의 `stateVersion`은 마이그레이션을 검토하기 전까지 유지하도록 안내한다.

## 공식 참고 자료

- [Home Manager Flake 사용 방식](https://nix-community.github.io/home-manager/nix-flakes.html)
- [standalone Flake 설정](https://nix-community.github.io/home-manager/nix-flakes/standalone.html)
- [Home Manager 옵션 검색](https://nix-community.github.io/home-manager/options.html)
- [Home Manager 릴리스 업그레이드](https://nix-community.github.io/home-manager/usage/upgrading.html)

[문서 목록으로 돌아가기](../index.md)
