# 3. 저장소 구조와 Flake 설계

## 학습 목표

1. 시스템, 사용자, dotfiles를 디렉터리로 분리한다.
2. 하나의 Flake에서 NixOS와 standalone Home Manager 출력을 만든다.
3. `flake.lock`과 Git 추적 상태가 재현성에 미치는 영향을 설명한다.

## 3.1 목표 구조

```text
.
├── flake.nix
├── flake.lock
├── hosts
│   ├── native
│   │   ├── default.nix
│   │   └── hardware-configuration.nix
│   └── wsl
│       └── default.nix
├── modules
│   ├── home
│   │   ├── default.nix
│   │   ├── lazyvim.nix
│   │   ├── nvm.nix
│   │   └── programs.nix
│   └── nixos
│       └── common.nix
└── dotfiles
    └── nvim
        ├── init.lua
        └── lua
            ├── config
            └── plugins
```

디렉터리 이름은 장식이 아니라 의존 방향을 나타낸다.

- `hosts/`: 특정 호스트만 알아야 하는 설정
- `modules/nixos/`: 여러 NixOS 호스트가 공유하는 시스템 정책
- `modules/home/`: 호스트 종류와 무관한 사용자 프로필
- `dotfiles/`: 애플리케이션 설정 원본

사용자 모듈이 `hosts/wsl`을 import하면 이 경계가 무너진다. 호스트가 사용자 모듈을 선택할 수는 있지만 사용자 모듈은 호스트 구현을 몰라야 한다.

## 3.2 Flake 입력

예제는 네 입력을 사용한다.

```nix
inputs = {
  nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  nixos-wsl = {
    url = "github:nix-community/NixOS-WSL/main";
    inputs.nixpkgs.follows = "nixpkgs";
  };

  home-manager = {
    url = "github:nix-community/home-manager/release-26.05";
    inputs.nixpkgs.follows = "nixpkgs";
  };

  nvm-src = {
    url = "github:nvm-sh/nvm/v0.40.4";
    flake = false;
  };
};
```

`follows = "nixpkgs"`는 NixOS-WSL과 Home Manager가 최상위와 같은 Nixpkgs 입력을 보게 한다. NVM 저장소는 Flake가 아니므로 `flake = false`로 소스 트리만 잠근다.

## 3.3 공통 NixOS 생성 함수

```nix
let
  system = "x86_64-linux";
  username = "nixos";
  lib = nixpkgs.lib;

  mkNixos = modules:
    lib.nixosSystem {
      inherit system;
      specialArgs = { inherit inputs username; };
      modules = [ ./modules/nixos/common.nix ] ++ modules;
    };
in
{
  # outputs
}
```

`mkNixos`는 공통 시스템 모듈을 항상 포함하고 호스트별 모듈을 뒤에 더한다. `specialArgs`는 `inputs`와 `username`을 각 모듈의 함수 인자로 전달한다.

사용자 이름을 한 곳에서 정하면 WSL 기본 사용자, NixOS 계정, Home Manager 출력의 이름을 맞추기 쉽다. 이미 설치된 WSL의 사용자 이름 변경은 단순 문자열 수정이 아니므로 9장의 마이그레이션 절차를 사용한다.

## 3.4 시스템 출력

```nix
nixosConfigurations = {
  wsl = mkNixos [
    nixos-wsl.nixosModules.default
    ./hosts/wsl
  ];
}
// lib.optionalAttrs (builtins.pathExists nativeHardware) {
  native = mkNixos [ ./hosts/native ];
};
```

WSL 출력에는 공식 `nixosModules.default`와 WSL 호스트 모듈을 넣는다. 네이티브 출력은 실제 `hardware-configuration.nix`가 있을 때만 노출한다. 템플릿을 실수로 실제 하드웨어에 적용하지 않기 위한 안전장치다.

## 3.5 독립 실행형 Home Manager 출력

```nix
homeConfigurations.${username} =
  home-manager.lib.homeManagerConfiguration {
    pkgs = nixpkgs.legacyPackages.${system};
    extraSpecialArgs = { inherit inputs username; };
    modules = [ ./modules/home ];
  };
```

이 출력은 `nixosConfigurations` 안에 들어가지 않는다. 그래서 `nixos-rebuild`와 독립적으로 다음처럼 선택한다.

```console
$ home-manager switch --flake .#nixos
```

최초 bootstrap도 잠긴 Home Manager 입력을 사용하도록 같은 Flake가 `apps.x86_64-linux.home-manager`를 노출한다.

```nix
apps.${system}.home-manager = {
  type = "app";
  program = "${home-manager.packages.${system}.default}/bin/home-manager";
};
```

따라서 아직 CLI가 없어도 외부 브랜치의 최신 상태를 다시 조회하지 않고 `nix run .#home-manager -- ...`로 잠긴 버전을 실행할 수 있다.

## 3.6 `flake.lock`을 만드는 시점

2장에서 제공 예제를 자신의 새 저장소로 초기화할 때 한 번 실행한다. 예제 파일은 `nix flake lock` 전에 Git에 추가해야 한다.

```console
$ git add .
$ nix flake lock
$ git add flake.lock
$ git commit -m "Create NixOS and Home Manager configuration"
```

이후 새 머신 복원에서는 잠금 파일을 생성하지 않는다. `git clone`으로 받은 값을 그대로 사용한다.

### Git에 추가하지 않으면 보이지 않는 파일

Git 저장소를 Flake로 평가할 때 새 파일이 추적되지 않으면 Nix의 입력 소스에서 빠질 수 있다.

```console
$ git status --short
?? modules/home/new-tool.nix
$ git add modules/home/new-tool.nix
$ nix flake show
```

네이티브 `hardware-configuration.nix`도 마찬가지다. 복사만 하고 `git add`하지 않으면 조건부 `native` 출력이 나타나지 않는다.

## 3.7 전체 예제

- [완성된 `flake.nix`](../assets/example-config/flake.nix)
- [예제 저장소 README](../assets/example-config/README.md)
- [예제 `.gitignore`](../assets/example-config/.gitignore)

개인 정보와 비밀은 예제에 넣지 않는다. 공개 가능한 Git 이름·이메일은 Home Manager에 추가할 수 있지만 토큰, SSH 개인 키, 레지스트리 인증 값은 별도 비밀 관리가 필요하다.

## 직접 확인

```console
$ nix flake show
```

하드웨어 파일이 없는 템플릿에서는 `nixosConfigurations.wsl`과 `homeConfigurations.nixos`가 핵심 출력이다. 네이티브 하드웨어 파일을 추적한 뒤에는 `nixosConfigurations.native`도 나타나야 한다.

## 요약

- 호스트, 공통 시스템, 사용자, dotfiles를 별도 디렉터리로 둔다.
- Flake는 하나지만 시스템 출력과 홈 출력은 독립적이다.
- NVM 소스도 non-Flake 입력으로 잠글 수 있다.
- 자신의 구성 저장소에는 `flake.lock`을 반드시 커밋한다.
- 새 Nix 파일은 평가 전에 Git에 추가한다.

## 추가 읽을거리

- [Flake 명령과 저장소 구조](https://nix.dev/manual/nix/latest/command-ref/new-cli/nix3-flake.html)
- [Nix에서 로컬 파일 다루기](https://nix.dev/tutorials/working-with-local-files.html)
- [NixOS-WSL Flake 예제](https://nix-community.github.io/NixOS-WSL/how-to/nix-flakes.html)

[← 2장](../02_install_nixos_wsl/chapter.md) · [목차](../index.md) · [4장: 시스템 설정 →](../04_system_configuration/chapter.md)
