# 2. Flake와 모듈 구조 읽기

## 학습 목표

1. `homeConfigurations` output과 `home-manager --flake` 인자의 관계를 설명한다.
2. 사용자 진입 모듈과 프로그램별 모듈을 분리한다.
3. Flake input에서 모듈로 값을 전달하는 방법을 이해한다.

## 2.1 기존 저장소 구조

기존 매뉴얼의 [예제 구성 저장소](../nixos-wsl-dev-environment/assets/example-config/README.md)는
시스템과 사용자 설정을 한 저장소에 두되 output을 분리한다.

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
평가에 사용된다.

## 2.3 homeConfigurations output

기존 예제 [`flake.nix`](../nixos-wsl-dev-environment/assets/example-config/flake.nix)의
핵심 output은 다음과 같다.

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

NixOS output인 `nixosConfigurations.wsl`은 별도 명령으로 선택한다.

```console
$ sudo nixos-rebuild build --flake .#wsl
```

## 2.4 homeManagerConfiguration의 인자

| 인자 | 역할 |
|---|---|
| `pkgs` | `home.packages`와 프로그램 모듈이 사용할 package set |
| `modules` | 합성할 Home Manager 모듈 목록 |
| `extraSpecialArgs` | Flake 외부에서 모듈 함수로 전달할 추가 값 |

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

Flake input처럼 모듈 그래프 바깥에서 들어오는 값은 `extraSpecialArgs`로 전달한다.
모든 모듈이 모든 인자를 선언할 필요는 없으며, 실제로 사용하는 값만 함수 인자에
적는다.

## 2.5 사용자 진입 모듈

[`modules/home/default.nix`](../nixos-wsl-dev-environment/assets/example-config/modules/home/default.nix)는
사용자 환경의 진입점이다.

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

`programs.home-manager.enable = true`는 최초 bootstrap 후 `home-manager` CLI를
사용자 프로필에서 계속 관리한다.

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
분리하면 충돌 원인을 찾기 쉽다.

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

적용할 사용자가 `alice`라면 그 사용자 세션에서 실행한다.

```console
$ home-manager switch --flake .#alice
```

한 사용자의 Home Manager를 다른 사용자나 root로 실행하지 않는다. 사용자별 홈 경로,
프로필과 파일 소유권이 어긋날 수 있다.

## 2.8 변경 파일을 Git에 추가해야 하는 이유

Git 저장소를 Flake 경로로 평가하면 추적되지 않은 새 파일이 source에 포함되지 않는다.
새 모듈을 만들고 `imports`에 추가했다면 build 전에 상태를 확인한다.

```console
$ git status --short
$ git add modules/home/new-program.nix
$ home-manager build --flake .#nixos
```

기존 추적 파일의 수정은 dirty tree로 평가할 수 있지만, 새 파일은 먼저 index에
추가해야 한다. commit은 build 검증 뒤에 해도 된다.

## 요약

- `homeConfigurations.<name>`이 `home-manager --flake .#<name>`의 선택 대상이다.
- 시스템 host 이름과 Home Manager 사용자 output 이름을 구분한다.
- `extraSpecialArgs`는 Flake input과 사용자 이름 같은 외부 값을 모듈에 전달한다.
- 진입 모듈은 identity와 imports를, 하위 모듈은 기능별 설정을 맡는다.
- Flake가 참조하는 새 파일은 build 전에 Git에 추가한다.

[← 1장](./01-mental-model.md) · [목차](./index.md) · [3장: 패키지와 프로그램 설정 →](./03-packages-and-programs.md)
