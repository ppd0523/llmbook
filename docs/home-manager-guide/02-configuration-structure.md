# 2. Flake와 모듈 구조 읽기

## 학습 목표

1. `homeConfigurations` output과 `home-manager --flake` 인자의 관계를 설명한다.
2. 사용자 진입 모듈과 프로그램별 모듈을 분리한다.
3. Flake input에서 모듈로 값을 전달하는 방법을 이해한다.

## 2.1 기존 저장소 구조

NixOS-WSL 매뉴얼의 [예제 구성](../nixos-wsl-dev-environment/assets/example-config/README.md)은
시스템과 사용자 설정을 한 저장소에 두되 output을 분리한다. `dotfiles/`에는 Neovim 설정 원본이
있다.

```text
~/.config/nixos/
├── flake.nix
├── flake.lock
├── hosts/
│   ├── wsl/
│   └── native/
├── modules/
│   ├── nixos/
│   │   └── common.nix
│   └── home/
│       ├── default.nix
│       ├── programs.nix
│       ├── lazyvim.nix
│       └── nvm.nix
└── dotfiles/
```

시스템과 사용자 파일을 같은 Git commit으로 복원할 수 있지만, 적용과 롤백은
독립적이다.

## 2.2 Home Manager input

`flake.nix`에는 Nixpkgs와 Home Manager input이 있다.

```nix
inputs = {
  nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  home-manager = {
    url = "github:nix-community/home-manager/release-26.05";
    inputs.nixpkgs.follows = "nixpkgs";
  };
};
```

`follows = "nixpkgs"`는 Home Manager가 별도 Nixpkgs revision을 잠그지 않고 이
Flake의 `nixpkgs` input을 따르게 한다. stable 구성에서는 Nixpkgs `nixos-26.05`와
Home Manager `release-26.05`처럼 대응하는 release를 사용한다.

실제 commit은 URL 문자열만으로 정해지지 않는다. `flake.lock`에 기록된 revision이
평가에 사용된다. `follows`는 같은 Nixpkgs source를 쓰게 하지만, release 조합 자체의
호환성을 보장하지는 않는다. stable release끼리를 맞추고, lock을 갱신할 때 두 계층을
함께 build한다.

## 2.3 homeConfigurations output

예제 구성의 [`flake.nix`](../nixos-wsl-dev-environment/assets/example-config/flake.nix)에서
Home Manager output 부분만 옮기면 다음과 같다.

```nix
homeConfigurations.${username} =
  home-manager.lib.homeManagerConfiguration {
    pkgs = nixpkgs.legacyPackages.${system};
    extraSpecialArgs = { inherit inputs username; };
    modules = [ ./modules/home ];
  };
```

예제에서 `username = "nixos";`이므로 결과는 다음 attribute가 된다.

```text
homeConfigurations.nixos
```

따라서 명령의 `#nixos`는 host 이름이 아니라 Home Manager output 이름이다.

```console
$ home-manager build --flake .#nixos
```

`--flake 경로#attribute` 형식에서:

- `.`은 현재 디렉터리의 Flake다.
- `nixos`는 `homeConfigurations` 아래의 attribute다.
- 현재 디렉터리가 아니라면 `~/.config/nixos#nixos`처럼 경로를 명시한다.
- `#attribute`를 생략하면 CLI가 로그인 사용자 이름으로 `homeConfigurations`를 찾는다.
  사용자 이름과 output 이름이 다르면 실패하므로 이 가이드는 항상 `#nixos`를 적는다.

NixOS output인 `nixosConfigurations.wsl`은 별도 명령으로 선택한다.

```console
$ sudo nixos-rebuild build --flake .#wsl
```

## 2.4 homeManagerConfiguration의 인자

| 인자 | 역할 |
|---|---|
| `pkgs` | `home.packages`와 프로그램 모듈이 사용할 package set |
| `modules` | 합성할 Home Manager 모듈 목록 |
| `extraSpecialArgs` | 모듈 시스템이 기본으로 주지 않는 값을 `flake.nix`에서 모듈 함수로 넘긴다 |

Home Manager 모듈은 인자 집합을 받는 함수다. 모듈 시스템은 `config`, `lib`, `pkgs` 같은
인자를 기본으로 넘기고, `extraSpecialArgs`에 넣은 값이 여기에 더해진다.
`extraSpecialArgs = { inherit inputs username; };` 때문에 모듈은 다음처럼 값을 받을 수
있다.

```nix
{
  inputs,
  username,
  pkgs,
  ...
}:
{
  # ...
}
```

Flake input처럼 모듈 바깥에서 들어오는 값은 `extraSpecialArgs`로 전달한다. 모든 모듈이
모든 인자를 선언할 필요는 없다. 실제로 사용하는 값만 적고, 나머지는 `...`가 받아
무시한다. 반대로 모듈이 선언한 인자를 아무도 넘기지 않으면 평가 단계에서 오류가 난다.

## 2.5 사용자 진입 모듈

[`modules/home/default.nix`](../nixos-wsl-dev-environment/assets/example-config/modules/home/default.nix)는
사용자 환경의 진입점이다. 아래는 구조를 보이려고 줄인 발췌다. 실제 파일에는 uv·rustup과
빌드 도구 패키지, `home.sessionPath`, Rust 관련 환경 변수가 더 있다.

```nix
{
  pkgs,
  username,
  ...
}:
{
  imports = [
    ./programs.nix
    ./lazyvim.nix
    ./nvm.nix
  ];

  home = {
    inherit username;
    homeDirectory = "/home/${username}";
    stateVersion = "26.05";

    packages = with pkgs; [
      tree
      ripgrep
    ];

    sessionVariables = {
      EDITOR = "nvim";
      VISUAL = "nvim";
    };
  };

  programs.home-manager.enable = true;
}
```

`programs.home-manager.enable = true`는 최초 bootstrap(5.1절, `home-manager` 명령이
아직 없을 때 Flake에서 CLI를 한 번 실행하는 단계) 후 `home-manager` CLI를 사용자
프로필에서 계속 관리한다.

## 2.6 모듈을 나누는 기준

처음부터 파일을 지나치게 잘게 나눌 필요는 없다. 다음 시점에 분리한다.

- 한 프로그램 설정이 독립적으로 읽힐 만큼 커졌다.
- 특정 기능을 다른 사용자도 import해야 한다.
- 설정의 변경 주기나 책임자가 다르다.
- dotfile 원본과 함께 이동해야 한다.

권장하는 작은 구조는 다음과 같다.

```text
modules/home/
├── default.nix       # 사용자·경로·stateVersion·imports
├── packages.nix      # 단순 CLI 패키지와 환경 변수
└── programs.nix      # Git, shell, prompt, direnv
```

`default.nix`에 모든 설정을 모아도 동작은 같지만, 공통 진입점과 프로그램 세부 설정을
분리하면 충돌 원인을 찾기 쉽다. 예제 구성은 아직 `packages.nix`를 따로 두지 않고
`default.nix`의 `home.packages`에 패키지를 둔다. 이 가이드의 실습도 그 구조를 그대로
쓴다.

## 2.7 여러 사용자로 확장

각 사용자는 서로 다른 `homeConfigurations` output을 가진다.

```nix
let
  system = "x86_64-linux";
  pkgs = nixpkgs.legacyPackages.${system};

  mkHome = username:
    home-manager.lib.homeManagerConfiguration {
      inherit pkgs;
      extraSpecialArgs = { inherit inputs username; };
      modules = [ ./modules/home ];
    };
in
{
  homeConfigurations = {
    nixos = mkHome "nixos";
    alice = mkHome "alice";
  };
}
```

Home Manager는 사용자 계정을 만들지 않는다. `alice` 계정은 먼저 NixOS 모듈의
`users.users.alice`로 만들고 `nixos-rebuild switch`해야 한다. 예제 구성의
`modules/nixos/common.nix`는 `username` 한 명만 만든다. 적용할 사용자가 `alice`라면 그
사용자 세션에서 실행한다.

```console
$ home-manager switch --flake .#alice
```

한 사용자의 Home Manager를 다른 사용자나 root로 실행하지 않는다. 사용자별 홈 경로,
프로필과 파일 소유권이 어긋날 수 있다.

## 2.8 변경 파일을 Git에 추가해야 하는 이유

Git 저장소를 Flake 경로로 평가하면 추적되지 않은 새 파일이 source에 포함되지 않는다.
새 모듈을 만들고 `imports`에 추가했다면 build 전에 staging 상태를 확인한다.

```console
$ git status --short
$ git add modules/home/new-program.nix
$ home-manager build --flake .#nixos
```

기존 추적 파일의 수정은 dirty tree로 평가할 수 있지만, 새 파일은 먼저 index에
추가해야 한다. commit은 build 검증 뒤에 해도 된다. 이 규칙은 Git 저장소에 있는 local
Flake에 적용된다. 다른 `path:` source나 Git이 아닌 디렉터리를 평가할 때는 source를
포함하는 방식이 달라질 수 있으므로, 이 가이드의 예제처럼 Git 저장소를 기준으로
작업하는 편이 가장 예측 가능하다.

## 연습문제

1. 어떤 Flake에 다음 output이 있다. NixOS 시스템과 Home Manager 사용자 환경을 각각
   activation 없이 검증하는 명령을 쓴다. 현재 디렉터리는 이 Flake의 루트다.

   ```nix
   nixosConfigurations.desk = lib.nixosSystem { /* ... */ };
   homeConfigurations.dev = home-manager.lib.homeManagerConfiguration { /* ... */ };
   ```

2. 1번 Flake에서 `--flake .` 처럼 attribute 없이 `home-manager build`를 실행했더니
   output을 찾지 못했다. 로그인 사용자 이름은 `dev`가 아니라 `kim`이다. 왜 실패했는가?
3. `modules/home/fonts.nix`를 새로 만들고 `default.nix`의 `imports`에 추가했다.
   `home-manager build`가 이 파일을 찾지 못한다. 가장 먼저 확인할 명령과 해결 명령은
   무엇인가?
4. 어떤 모듈의 첫 줄이 `{ inputs, pkgs, ... }:`이다. `flake.nix`의
   `extraSpecialArgs`에서 `inputs`를 지우면 무엇이 달라지는가?

??? note "정답 확인"
    1번: `sudo nixos-rebuild build --flake .#desk`와 `home-manager build --flake .#dev`.
    `#` 뒤의 이름은 각 namespace(`nixosConfigurations`, `homeConfigurations`) 아래의
    attribute다.

    2번: attribute를 생략하면 CLI가 현재 사용자 이름을 골라 `homeConfigurations.kim`을
    찾는다. 이 Flake에는 `dev`만 있으므로 `.#dev`를 명시해야 한다.

    3번: `git status --short`에서 파일이 `??`(추적되지 않음)로 보이는지 확인하고
    `git add modules/home/fonts.nix` 뒤 다시 build한다. Git 저장소인 local Flake는
    추적되지 않은 새 파일을 평가 source에 넣지 않는다. commit은 build 검증 뒤에 해도 된다.

    4번: 그 모듈 함수가 요구하는 `inputs` 인자를 받을 곳이 없어져 평가 단계에서 실패한다.
    Flake input처럼 모듈 그래프 바깥의 값은 `extraSpecialArgs`로만 들어온다.

## 요약

- `homeConfigurations.<name>`이 `home-manager --flake .#<name>`의 선택 대상이다.
- 시스템 host 이름과 Home Manager 사용자 output 이름을 구분한다.
- `extraSpecialArgs`는 Flake input과 사용자 이름 같은 외부 값을 모듈에 전달한다.
- 진입 모듈은 identity와 imports를, 하위 모듈은 기능별 설정을 맡는다.
- Flake가 참조하는 새 파일은 build 전에 Git에 추가한다.

[← 1장](./01-mental-model.md) · [목차](./index.md) · [3장: 패키지와 프로그램 설정 →](./03-packages-and-programs.md)
