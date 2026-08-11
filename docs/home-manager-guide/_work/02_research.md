---
title: Home Manager 가이드 기술 조사
updated: 2026-08-11
---

# 기술 근거

| 주장 | 검증 결과 | 출처 |
|---|---|---|
| standalone은 시스템과 독립적으로 home을 관리하려는 NixOS 사용자에게 권장되는 Flake 사용 방식이다. | 확인 | [Home Manager Flakes](https://nix-community.github.io/home-manager/nix-flakes.html) |
| `extraSpecialArgs`의 각 값은 Home Manager 모듈 함수의 인자가 된다. | 확인 | [Standalone setup](https://nix-community.github.io/home-manager/nix-flakes/standalone.html) |
| Flake input은 `flake.lock`이 고정하며, `nix flake update`로 명시적으로 갱신한다. | 확인 | [Updating](https://nix-community.github.io/home-manager/usage/updating.html), [Nix reference](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-flake-update.html) |
| `home.stateVersion`은 호환되지 않는 기본 동작을 선택하는 값이며 올릴 때 수동 마이그레이션이 필요할 수 있다. | 확인 | [`home.stateVersion`](https://nix-community.github.io/home-manager/options/home-manager/home.html) |
| `home.sessionVariables`는 서로의 runtime 값을 참조하면 순서가 보장되지 않는다. | 확인 | [`home.sessionVariables`](https://nix-community.github.io/home-manager/options/home-manager/home.html) |
| `home.sessionPath`의 `$HOME`은 shell에서 확장되지만 `~`은 그대로 남을 수 있다. | 확인 | [`home.sessionPath`](https://nix-community.github.io/home-manager/options/home-manager/home.html) |
| 일반 파일 source는 store를 거치며, `mkOutOfStoreSymlink`는 store 밖의 live path를 가리킨다. | 확인 | [Dotfile 안전 전환](https://nix-community.github.io/home-manager/usage/dotfiles.html) |
| 기존 파일 충돌은 activation 전에 중단되며, `-b`와 `force`에는 데이터 손실 위험이 있다. | 확인 | [Dotfile 안전 전환](https://nix-community.github.io/home-manager/usage/dotfiles.html) |
| `recursive = true`인 디렉터리 source와 일반 파일 target이 겹치면 재귀 링크 쪽이 유지된다. | 확인 | [Dotfile 안전 전환](https://nix-community.github.io/home-manager/usage/dotfiles.html) |
| `home-manager switch --rollback`은 25.11에서 추가되었다. | 확인 | [25.11 release notes](https://nix-community.github.io/home-manager/release-notes/rl-2511.html) |

## 위험 요소

- Flake 지원은 Home Manager 문서에서 experimental로 표시된다. 명령이나 옵션은 사용하는 lock의 release와 맞춰 확인해야 한다.
- 이 자료의 `wsl`, `nixos`는 예제 output 이름이다. 독자는 자신의 `flake.nix`에 정의한 이름을 사용해야 한다.
- Git 저장소 기반 local Flake에서 새 파일은 staging하지 않으면 평가 source에 포함되지 않는다. 이 저장소의 예제 구성을 기준으로 검증했다.
