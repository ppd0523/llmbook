# 5. 빌드, 적용, 업데이트, 롤백

## 학습 목표

1. 검증과 활성화를 분리하여 변경을 안전하게 적용한다.
2. NixOS와 Home Manager 변경을 올바른 순서로 전환한다.
3. generation 롤백과 Git 되돌리기의 차이를 이해한다.

## 5.1 최초 bootstrap

예제 구성의 Flake는 잠긴 Home Manager CLI를 app으로 노출한다. 아직
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

build가 성공하면 현재 디렉터리에 `result` 링크가 생긴다. 이 링크는 build한 generation을
가리키는 확인용 링크이며 현재 사용자 환경이 아니다.

```console
$ ls -l result
lrwxrwxrwx 1 nixos users 67 ... result -> /nix/store/<hash>-home-manager-generation
$ ls result/home-path/bin | head
$ ls -la result/home-files/.config
```

`home-path/bin`에는 새 프로필에 들어갈 실행 파일이, `home-files`에는 홈 디렉터리에
연결될 관리 파일이 있다. `switch` 전에 여기서 바꾼 내용을 먼저 확인할 수 있다. `result`는
다음 build에서 새 결과를 가리키도록 바뀌며 Git에 넣지 않는다. 예제 구성의 `.gitignore`가
`result`와 `result-*`를 이미 제외한다.

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

`switch`는 이미 실행 중인 shell을 바꾸지 않는다. 무엇을 바꿨는지에 따라 확인 방법이
다르다([3장](./03-packages-and-programs.md)의 3.10절).

- alias, 프롬프트, shell hook: 같은 터미널에서 `exec zsh`
- `home.sessionVariables`, `home.sessionPath`: 새 터미널 탭에서 WSL을 연다
- 로그인 shell이나 로그인 환경 전체: PowerShell에서 배포판을 종료한 뒤 다시 시작한다

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

```text
2026-11-02 12:09 : id 6 -> /nix/store/<hash>-home-manager-generation (current)
2026-10-20 17:56 : id 5 -> /nix/store/<hash>-home-manager-generation
```

목록은 최신 generation부터 생성 시각, generation id와 Nix Store 경로를 보여 주고, 활성
generation에 `(current)`를 붙인다. 현재 설정에 문제가 생겼다면 직전 generation으로
돌아간다.

```console
$ home-manager switch --rollback
```

이 명령은 새 generation을 만들지 않고 직전 Home Manager generation을 다시 활성화한다.
목록의 가장 새 generation은 남아 있고 `(current)` 표시만 옮겨 간다. NixOS 시스템은
바뀌지 않는다. 이 옵션은 Home Manager 25.11에서 추가되었으므로, 더 오래된 lock을 사용하는
구성은 해당 release의 rollback 절차를 확인한다.

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
$ git add modules/home/고친-파일.nix
$ git commit
```

## 5.8 input 업데이트

복원과 업데이트를 구분한다.

- 복원: 저장소에 커밋된 `flake.lock`을 그대로 사용한다.
- 업데이트: 의도적으로 input revision을 바꾸고 diff와 release note를 검토한다.

업데이트 절차:

```console
$ cd ~/.config/nixos
$ nix flake update nixpkgs home-manager
$ git diff -- flake.lock
$ sudo nixos-rebuild build --flake .#wsl
$ home-manager build --flake .#nixos
$ sudo nixos-rebuild switch --flake .#wsl
$ home-manager switch --flake .#nixos
$ git add flake.lock
$ git commit -m "Update Nix inputs"
```

`home-manager switch` 자체는 Flake input을 자동으로 최신화하지 않는다. lock을
갱신하지 않으면 같은 source revision을 계속 사용한다. 모든 input을 의도적으로
갱신할 때만 인자 없이 `nix flake update`를 실행한다. input 이름을 지정하면 review할
lock diff의 범위를 줄일 수 있다.

NixOS-WSL 매뉴얼 README의 정기 업데이트 절차는 인자 없이 모든 input을 한 번에 갱신한다.
이 가이드는 Home Manager 변경을 따로 검토하려고 범위를 좁힌다. 이렇게 하면 `nixos-wsl`과
`nvm-src` input은 갱신되지 않으므로, WSL 통합 기능을 고칠 때나 정기 점검 때
`nix flake update nixos-wsl`처럼 이름을 지정해 따로 갱신한다.

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

예제 구성은 사용자 환경을 WSL과 native NixOS에서 재사용하고 시스템과 독립적으로
수정하기 위해 standalone 방식을 쓴다. 두 방식을 한 구성에 동시에 적용하지
않는다.

## 실습 과제

예제 구성의 `~/.config/nixos`에서 진행한다. 과제 2는 일부러 이전 환경으로 돌아가므로
열린 터미널을 하나 더 둔 상태에서 한다.

1. `home.packages`에 `hello`를 추가하고 build한다. `switch` 전에 `result`가 가리키는
   generation에 `hello`가 있는지 확인한 뒤 `switch`하고, `home-manager generations`에서
   새 generation이 `(current)`가 되었는지 확인한다.
2. 과제 1의 `switch` 직후 `home-manager switch --rollback`을 실행한다. generation 목록과
   `command -v hello`가 어떻게 달라지는지 확인한다. 그다음 Git 작업 트리에서 `hello`
   추가가 아직 남아 있는지 보고, 다음 `switch`에서 무슨 일이 생길지 예측한다.
3. `nix flake update home-manager`를 실행하고 `git diff -- flake.lock`에서 어떤 input의
   항목이 바뀌었는지 확인한다. 이번에는 업데이트하지 않기로 하고 lock을 되돌린다.

??? note "기대 결과 확인"
    1번: `ls result/home-path/bin/hello`가 경로를 출력한다. `switch` 뒤
    `home-manager generations`의 첫 줄이 id가 하나 늘어난 새 generation이고 끝에
    `(current)`가 붙는다. `hello`를 실행하면 `Hello, world!`가 나온다.

    2번: rollback 뒤 목록의 첫 줄(가장 새 generation)은 그대로 있지만 `(current)`가 그
    아래 직전 generation으로 옮겨 간다. `command -v hello`는 아무것도 출력하지 않는다.
    `git diff`에는 `hello` 추가가 그대로 남아 있으므로, 이대로 다시 `switch`하면 `hello`가
    돌아온다. generation 롤백은 활성 환경만 바꾸고 선언 원본은 바꾸지 않는다. 과제를
    정리하려면 `git restore modules/home/default.nix` 뒤 build와 `switch`를 한다.

    3번: `git diff -- flake.lock`에서 `home-manager` 노드의 `lastModified`, `narHash`,
    `rev`만 바뀐다(이미 최신이면 diff가 없다). `git restore flake.lock`로 되돌리고
    `git status --short flake.lock`이 아무것도 출력하지 않는지 확인한다.

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
