---
title: Home Manager 가이드 기술 조사
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
| activation 충돌 오류는 `Existing file '...' would be clobbered`이고, 내용이 같은 기존 파일은 경고 후 건너뛴다. `-b` 백업이 이미 있으면 `... would be clobbered by backing up ...`로 중단하고, HM이 소유하지 않은 symlink는 백업하지 않는다. | 확인 | Home Manager 26.05 소스 `modules/files/check-link-targets.sh` |
| `hm-session-vars.sh`는 `__HM_SESS_VARS_SOURCED`로 세션당 한 번만 실행되며, 관리하는 zsh는 `~/.zshenv`에서 이 파일을 불러온다. | 확인 | 26.05 build 결과의 `home-path/etc/profile.d/hm-session-vars.sh`, `home-files/.zshenv` |
| 같은 target 두 번 선언은 평가 단계의 `Conflicting managed target files` 오류다. 부모 디렉터리가 out-of-store link이거나 부모 source에 없는 하위 파일을 다른 선언이 만들면 build가 `Error installing file '...' outside $HOME`로 실패하고, source에 있으면 하위 선언이 무시된다(build 로그에 `conflicts with recursively symlinked file`). | 확인 | 26.05 `modules/files.nix`와 build 실험 |
| `nix flake show`는 `homeConfigurations`를 `unknown`으로만 표시한다. 이름 목록은 `nix eval .#homeConfigurations --apply builtins.attrNames`로 본다. | 확인 | Nix 2.34.7 실행 결과 |
| 추적되지 않은 파일을 import하면 Nix 2.34는 `Path '...' in the repository "..." is not tracked by Git.`을 출력한다. | 확인 | Nix 2.34.7 실행 결과 |
| `home-manager` CLI는 `-L`(`--print-build-logs`)와 `--show-trace`를 받는다. | 확인 | Home Manager 26.05 `home-manager/home-manager` |
| `programs.zsh.dotDir` 기본값은 `xdg.enable`이고 `stateVersion >= "26.05"`일 때 `~/.config/zsh`, 아니면 홈이다. 이때 `~/.zshenv`는 `~/.config/zsh/.zshenv`를 source하는 한 줄이다. 낮은 `stateVersion`에서는 기본값 변경 예정 경고를 낸다. | 확인 | 26.05 `modules/programs/zsh/default.nix`, build 결과, 검증 기기의 실제 홈 |
| `xdg.enable`은 XDG 디렉터리 환경 변수를 설정한다. `xdg.configFile`은 이 옵션 없이도 `~/.config` 아래에 배치된다. | 확인 | 26.05 `modules/misc/xdg.nix`, build 결과 |
| NixOS는 시스템 전체에 `PAGER="less"`를 설정한다. | 확인 | 검증 기기의 `/etc/set-environment` |
| Git은 `~/.config/git/config` 다음에 `~/.gitconfig`를 읽으므로 같은 키는 `~/.gitconfig`가 이긴다. | 확인 | [git-config FILES](https://git-scm.com/docs/git-config#FILES) |

## 위험 요소

- Flake 지원은 Home Manager 문서에서 experimental로 표시된다. 명령이나 옵션은 사용하는 lock의 release와 맞춰 확인해야 한다.
- 이 자료의 `wsl`, `nixos`는 예제 output 이름이다. 독자는 자신의 `flake.nix`에 정의한 이름을 사용해야 한다.
- Git 저장소 기반 local Flake에서 새 파일은 staging하지 않으면 평가 source에 포함되지 않는다. 이 저장소의 예제 구성을 기준으로 검증했다.
- 오류 문구는 Home Manager 26.05(release branch rev `3cd22efe`)와 Nix 2.34.7 기준이다. 다른 버전에서는 문구가 다를 수 있어 6장에 버전을 적었다.
