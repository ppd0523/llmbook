# 5. 빌드, 적용, 업데이트, 롤백

## 학습 목표

1. 검증과 활성화를 분리하여 변경을 안전하게 적용한다.
2. NixOS와 Home Manager 변경을 올바른 순서로 전환한다.
3. generation 롤백과 Git 되돌리기의 차이를 이해한다.

## 5.1 최초 bootstrap

기존 매뉴얼의 Flake는 잠긴 Home Manager CLI를 app으로 노출한다. 아직
`home-manager` 명령이 없을 때 한 번 사용한다.

```console
$ cd ~/.config/nixos
$ nix run .#home-manager -- build --flake .#nixos
$ nix run .#home-manager -- switch --flake .#nixos
```

이 명령은 외부의 임의 최신 버전이 아니라 같은 저장소의 `flake.lock`에 기록된
Home Manager input을 사용한다. 첫 activation 후에는
`programs.home-manager.enable = true`가 CLI를 사용자 프로필에 유지한다.

```console
$ home-manager --version
```

## 5.2 build와 switch

평상시에는 먼저 build한다.

```console
$ home-manager build --flake .#nixos
```

`build`는 모듈을 평가하고 필요한 package와 Home Manager generation을 빌드하지만
현재 사용자 환경을 활성화하지 않는다. 문법 오류, 없는 옵션, package build 실패를
현재 환경을 바꾸기 전에 찾을 수 있다.

성공한 뒤 전환한다.

```console
$ home-manager switch --flake .#nixos
```

`switch`는 새 generation을 현재 사용자 프로필에 등록하고, 관리 파일과 shell 설정을
활성화한다. activation 단계에서 기존 파일 충돌이 발견되면 전환은 중단된다.

## 5.3 변경 범위별 표준 절차

### Home Manager 파일만 변경

```console
$ git diff -- modules/home dotfiles
$ home-manager build --flake .#nixos
$ home-manager switch --flake .#nixos
```

### NixOS 파일만 변경

```console
$ git diff -- hosts modules/nixos
$ sudo nixos-rebuild build --flake .#wsl
$ sudo nixos-rebuild switch --flake .#wsl
```

### 두 계층 또는 flake.lock 변경

```console
$ sudo nixos-rebuild build --flake .#wsl
$ home-manager build --flake .#nixos

$ sudo nixos-rebuild switch --flake .#wsl
$ home-manager switch --flake .#nixos
```

두 build를 먼저 완료한 다음 NixOS를 먼저 적용한다. 사용자 계정, 로그인 shell,
system package나 service처럼 Home Manager가 전제로 삼는 시스템 환경이 먼저
준비되기 때문이다.

## 5.4 적용 후 확인

변경한 기능을 직접 확인한다.

```console
$ command -v rg
$ git config --global --get init.defaultBranch
$ type starship
$ direnv version
$ echo "$EDITOR"
```

shell 초기화와 session variable은 현재 실행 중인 shell에 자동으로 역주입되지 않을
수 있다. zsh를 관리한다면 새 shell을 시작한다.

```console
$ exec zsh
```

WSL 로그인 환경 전체를 확인해야 한다면 현재 terminal만 닫는 것보다 PowerShell에서
배포판을 종료한 뒤 다시 시작하는 편이 확실하다.

```powershell
wsl --terminate NixOS
wsl -d NixOS
```

## 5.5 Git commit

build와 실제 동작 확인이 끝난 뒤 commit한다.

```console
$ git status --short
$ git diff
$ git add flake.nix flake.lock modules dotfiles
$ git commit -m "Update Home Manager configuration"
```

모든 경로를 무조건 add하지 말고 이번 변경에 속한 파일을 검토하여 추가한다. 비밀,
history, cache, 머신별 상태가 섞이지 않았는지 확인한다.

## 5.6 generation 확인

standalone Home Manager는 NixOS와 별도 generation 이력을 가진다.

```console
$ home-manager generations
```

목록은 생성 시각, generation id와 Nix Store 경로를 보여 준다. 현재 설정에 문제가
생겼다면 직전 generation으로 돌아간다.

```console
$ home-manager switch --rollback
```

이 명령은 직전 Home Manager generation을 선택해 활성화한다. NixOS 시스템은 바뀌지
않는다.

시스템 변경만 되돌리려면 별도의 NixOS rollback을 사용한다.

```console
$ sudo nixos-rebuild switch --rollback
```

## 5.7 generation 롤백과 Git 되돌리기

generation 롤백과 Git 되돌리기는 서로 대체하지 않는다.

| 작업 | 바꾸는 것 | 목적 |
|---|---|---|
| `home-manager switch --rollback` | 현재 활성 사용자 generation | 즉시 실행 환경 복구 |
| `nixos-rebuild switch --rollback` | 현재 활성 시스템 generation | 즉시 시스템 복구 |
| Git revert 또는 수정 commit | 다음 build에 들어갈 선언 원본 | 재발 방지와 이력 보존 |

generation만 롤백하고 Git의 잘못된 선언을 그대로 두면 다음 `switch`에서 문제가 다시
나타난다. 긴급 복구 후 구성 파일을 수정하거나 문제 commit을 되돌리고 다시 build한다.

```console
$ home-manager switch --rollback
$ git diff
# 구성 수정
$ home-manager build --flake .#nixos
$ home-manager switch --flake .#nixos
$ git commit
```

## 5.8 input 업데이트

복원과 업데이트를 구분한다.

- 복원: 저장소에 커밋된 `flake.lock`을 그대로 사용한다.
- 업데이트: 의도적으로 input revision을 바꾸고 diff와 release note를 검토한다.

업데이트 절차:

```console
$ cd ~/.config/nixos
$ nix flake update
$ git diff -- flake.lock
$ nix fmt
$ sudo nixos-rebuild build --flake .#wsl
$ home-manager build --flake .#nixos
$ sudo nixos-rebuild switch --flake .#wsl
$ home-manager switch --flake .#nixos
$ git add flake.lock
$ git commit -m "Update Nix inputs"
```

`home-manager switch` 자체는 Flake input을 자동으로 최신화하지 않는다. lock을
갱신하지 않으면 같은 source revision을 계속 사용한다.

## 5.9 release 업그레이드

26.05에서 다음 stable release로 이동할 때 다음을 함께 검토한다.

```nix
nixpkgs.url = "github:NixOS/nixpkgs/nixos-새버전";
home-manager.url =
  "github:nix-community/home-manager/release-새버전";
```

Home Manager stable release는 대응하는 Nixpkgs release와 맞춘다. branch를 바꾼 뒤
lock을 갱신하고 NixOS와 Home Manager 양쪽을 build한다.

기존 home의 다음 값은 자동으로 올리지 않는다.

```nix
home.stateVersion = "26.05";
```

새 release note의 state version 변경을 읽고 데이터 이동이나 설정 마이그레이션이
필요한지 확인한 경우에만 별도로 변경한다.

## 5.10 NixOS 모듈 방식과 비교

Home Manager를 NixOS 모듈로 통합하면 대략 다음 구조가 된다.

```nix
{
  imports = [
    home-manager.nixosModules.home-manager
  ];

  home-manager = {
    useGlobalPkgs = true;
    useUserPackages = true;
    extraSpecialArgs = { inherit inputs username; };
    users.${username} = import ./modules/home;
  };
}
```

이 방식에서는 `nixos-rebuild`가 시스템과 사용자 설정을 함께 build하고 전환한다.

```console
$ sudo nixos-rebuild switch --flake .#wsl
```

두 방식의 차이는 다음과 같다.

| standalone | NixOS 모듈 |
|---|---|
| 사용자 설정을 `home-manager`로 독립 전환 | `nixos-rebuild` 한 번으로 함께 전환 |
| 사용자별 generation과 롤백 | NixOS generation과 함께 관리 |
| 사용자 변경에 `sudo`가 필요 없음 | 시스템 rebuild 권한 필요 |
| 비 NixOS Linux에도 같은 구조를 적용하기 쉬움 | NixOS 시스템 구성에 종속 |

현재 프로젝트는 사용자 환경을 WSL과 native NixOS에서 재사용하고 시스템과 독립적으로
수정하기 위해 standalone 방식을 유지한다. 두 방식을 한 구성에 동시에 적용하지
않는다.

## 요약

- `build`로 먼저 검증하고 성공한 구성만 `switch`한다.
- 두 계층을 변경하면 양쪽을 build한 뒤 NixOS, Home Manager 순으로 적용한다.
- generation 롤백은 현재 상태를 복구하고 Git 수정은 다음 build를 바로잡는다.
- input update와 새 머신 restore를 같은 절차로 취급하지 않는다.
- release branch를 올려도 `home.stateVersion`은 자동으로 올리지 않는다.

## 공식 참고 자료

- [standalone Flake 설정](https://nix-community.github.io/home-manager/nix-flakes/standalone.html)
- [Home Manager 릴리스 업그레이드](https://nix-community.github.io/home-manager/usage/upgrading.html)
- [Home Manager 25.11 이후 rollback 동작](https://nix-community.github.io/home-manager/release-notes/rl-2511.html)

[← 4장](./04-dotfiles.md) · [목차](./index.md) · [6장: 문제 해결 →](./06-troubleshooting.md)
