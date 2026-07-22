---
title: NixOS-WSL 개발 환경을 Git으로 복원하기
version: 1.5
status: final
owner: agent
updated: 2026-07-22
target_reader: 터미널과 언어별 버전 관리에는 익숙하지만 Nix는 처음인 시니어 개발자
topic: Flake와 독립 실행형 Home Manager를 이용한 이식 가능한 NixOS 개발 환경
---

# NixOS-WSL 개발 환경을 Git으로 복원하기

이 기준 원고는 NixOS/Nixpkgs 26.05, Home Manager 26.05, NVM 0.40.4를 기준으로 한다. 시스템과 사용자 설정을 한 Flake 저장소에서 관리하되 독립 실행형 Home Manager로 수명 주기를 분리하고, Python·Node.js·Rust 버전은 각 프로젝트 파일에 맡긴다.

## 1. NixOS, Flake, Home Manager, dotfiles의 역할

### 학습 목표

이 장을 마치면 다음을 할 수 있다.

1. NixOS와 Nix 패키지 관리자의 역할을 구분한다.
2. Flake와 `flake.lock`이 무엇을 고정하는지 설명한다.
3. 시스템 설정, 사용자 설정, 프로젝트 설정의 소유자를 결정한다.

### 필요한 선행지식

Git 저장소, 셸 초기화 파일, `nvm`이나 `uv` 같은 버전 관리 도구에 대한 경험이면 충분하다. Nix 문법은 필요하지 않다.

### 1.1 먼저 해결할 문제

기존 개발 환경을 새 머신에서 복원한다고 생각해 보자. `apt install` 목록과 `.zshrc`만 Git에 넣으면 도구 버전, OS 정책, 파일 배치가 느슨하다. 반대로 Python과 Node.js까지 모두 Nix 패키지로 고정하면 기존 프로젝트의 `.python-version`과 `.nvmrc` 흐름이 사라진다.

이 자료는 재현성이 필요한 경계를 세 단계로 나눈다.

```text
호스트: NixOS
  └── 사용자: standalone Home Manager
        └── 프로젝트: uv / nvm / rustup
```

아래 계층은 위 계층이 제공한 도구를 사용하지만, 위 계층이 아래 계층의 버전까지 대신 결정하지 않는다.

### 1.2 Nix와 NixOS

Nix는 입력을 바탕으로 패키지와 설정 결과를 `/nix/store`의 불변 경로에 만든다. 같은 프로그램의 여러 버전이 서로 다른 Store 경로에 공존할 수 있고, 프로필은 어떤 결과를 현재 사용할지 가리킨다.

NixOS는 이 모델을 운영체제 전체에 적용한다. 사용자 계정, 서비스, 기본 셸, 커널 매개변수 같은 시스템 상태를 Nix 모듈로 선언하고 하나의 시스템 세대로 만든다. 실패하면 이전 세대로 돌아갈 수 있다.

NixOS-WSL도 NixOS다. 다만 커널, 가상화, Windows 연동은 WSL이 제공하므로 실제 하드웨어 NixOS와 호스트 모듈은 같을 수 없다.

### 1.3 Flake는 저장소의 공개 인터페이스다

Flake는 두 질문에 답한다.

- `inputs`: 이 구성이 참조하는 외부 소스는 무엇인가?
- `outputs`: 이 저장소에서 빌드하거나 적용할 수 있는 결과는 무엇인가?

예제 출력은 다음처럼 읽는다.

```text
nixosConfigurations.wsl    → WSL 호스트 시스템
nixosConfigurations.native → 실제 하드웨어 시스템
homeConfigurations.nixos   → nixos 사용자의 홈 프로필
```

`flake.nix`가 입력 URL과 출력 구조를 선언하면 `flake.lock`은 각 입력의 실제 리비전과 해시를 기록한다. `package.json`과 lockfile의 관계에 가깝지만, 잠금 대상이 애플리케이션 의존성이 아니라 Nixpkgs·Home Manager·NixOS-WSL 같은 구성 입력이라는 점이 다르다.

복원할 때는 커밋된 `flake.lock`을 그대로 사용한다. `nix flake update`는 복원 명령이 아니라 의도적인 업그레이드 명령이다.

### 1.4 standalone Home Manager

Home Manager는 Nix 모듈로 사용자 패키지, 환경 변수, 셸, dotfiles를 관리한다. NixOS 모듈로 통합할 수도 있지만 이 자료는 독립 실행형을 선택한다.

```console
$ sudo nixos-rebuild switch --flake .#wsl
$ home-manager switch --flake .#nixos
```

두 전환을 분리하면 다음 성질을 얻는다.

- 사용자 설정 변경에 루트 권한이 필요 없다.
- 사용자 프로필을 시스템보다 자주 변경할 수 있다.
- 동일한 `homeConfigurations.nixos`를 WSL과 네이티브 NixOS에서 재사용할 수 있다.
- 시스템 세대와 홈 프로필 세대를 따로 롤백할 수 있다.

대신 전환 명령이 두 개다. 이 비용은 시스템과 사용자의 수명 주기를 분리하기 위한 의도적인 선택이다.

### 1.5 dotfiles는 데이터다

dotfiles는 프로그램이 읽는 설정 원본이다. Home Manager와 경쟁하는 별도 계층이 아니다. 예를 들어 Neovim의 `init.lua`는 저장소의 `dotfiles/nvim/init.lua`에 두고 Home Manager가 `~/.config/nvim/init.lua`로 연결한다.

반면 zsh, Git, Starship처럼 Home Manager에 안정적인 전용 모듈이 있으면 Nix 옵션으로 표현한다. 기준은 다음과 같다.

- 전용 모듈이 설치와 통합을 함께 처리하면 모듈을 사용한다.
- 애플리케이션 고유 언어로 작성된 큰 설정은 `dotfiles/`에 둔다.
- Home Manager가 만든 결과 파일을 직접 수정하지 않는다. 원본 모듈이나 dotfile을 고치고 다시 전환한다.

### 1.6 소유권을 결정하는 질문

| 질문 | 그렇다면 |
|---|---|
| 부팅이나 모든 사용자에게 영향을 주는가? | NixOS 시스템 모듈 |
| `$HOME` 안에서 끝나고 일반 사용자 권한으로 바꿀 수 있는가? | Home Manager |
| 프로그램이 직접 읽는 설정 내용인가? | dotfiles, Home Manager가 배치 |
| Nix 외부 입력의 리비전인가? | `flake.lock` |
| 특정 프로젝트가 요구하는 언어 버전인가? | 프로젝트 버전 파일 |
| 토큰이나 개인 키인가? | 이 저장소 밖의 비밀 관리 체계 |

### 1.7 상태 버전은 업데이트 버전이 아니다

`system.stateVersion`과 `home.stateVersion`은 설치 당시의 데이터 형식과 기본 동작을 보존하는 호환 기준이다. NixOS나 Home Manager를 업데이트한다고 함께 올리지 않는다. 기존 설치를 구성 저장소에 편입할 때는 기존 값을 유지한다.

### 직접 확인

다음 항목의 소유자를 각각 결정해 보자.

1. WSL의 기본 사용자와 로그인 셸
2. Neovim의 `init.lua`
3. Python 3.13을 요구하는 프로젝트
4. Home Manager 릴리스 브랜치의 실제 Git 커밋
5. npm 인증 토큰

정답은 순서대로 NixOS, dotfiles/Home Manager, uv 프로젝트, `flake.lock`, 저장소 밖의 비밀 관리다.

### 요약

- NixOS는 호스트 상태를, Home Manager는 사용자 상태를 관리한다.
- Flake는 입력과 출력의 진입점이고 `flake.lock`이 실제 입력 리비전을 고정한다.
- dotfiles는 프로그램 설정 데이터이며 Home Manager가 배치한다.
- 언어 런타임은 프로젝트 파일이 결정한다.
- 상태 버전은 릴리스 번호처럼 올리지 않는다.

### 추가 읽을거리

- [Nix Flakes 개념](https://nix.dev/concepts/flakes.html)
- [Home Manager 소개](https://nix-community.github.io/home-manager/introduction.html)
- [Home Manager 설치 방식](https://nix-community.github.io/home-manager/installation.html)
- [NixOS `stateVersion` FAQ](https://wiki.nixos.org/wiki/FAQ/When_do_I_update_stateVersion)

## 2. 처음부터 NixOS-WSL과 구성 저장소 만들기

이 장은 GitHub 계정만 있고 구성 저장소, SSH 키, NixOS-WSL이 모두 없는 첫 컴퓨터에서 시작한다. 여기서 만든 원본 저장소를 이후 컴퓨터가 clone한다.

### 학습 목표

1. Windows에 WSL과 NixOS-WSL을 처음 설치한다.
2. GitHub에 빈 구성 저장소를 만들고 SSH 접근을 설정한다.
3. 제공 예제를 Git 저장소로 초기화하고 첫 `flake.lock`을 만든다.
4. 시스템과 Home Manager를 적용한 뒤 첫 커밋을 push한다.

### 2.1 첫 컴퓨터의 순서

```text
Windows에 WSL 설치
  → NixOS-WSL 등록
  → GitHub 빈 저장소와 SSH 인증 생성
  → 제공 예제를 ~/.config/nixos로 복사
  → git init과 flake.lock 생성
  → 시스템과 Home Manager build·switch
  → 첫 commit과 push
```

### 2.2 WSL과 NixOS-WSL 설치

WSL이 전혀 없다면 관리자 PowerShell에서 배포판 없이 기능부터 설치하고 Windows를 재시작한다.

```powershell
wsl --install --no-distribution
wsl --update
wsl --version
```

NixOS-WSL 릴리스에서 `nixos.wsl`을 내려받는다. WSL 2.4.4 이상은 다음처럼 등록한다.

```powershell
wsl --install --from-file .\nixos.wsl --name NixOS
wsl -d NixOS
```

구형 WSL은 `wsl --import NixOS $env:USERPROFILE\NixOS .\nixos.wsl --version 2`를 사용한다. 가능하면 WSL부터 업데이트한다.

### 2.3 초기 사용자와 이미지 bootstrap

NixOS-WSL의 기본 `nixos` 사용자 암호를 정하고 첫 rebuild용 채널 메타데이터를 갱신한다.

```console
$ passwd
$ sudo nix-channel --update
```

채널 갱신은 이미지 bootstrap일 뿐이다. 이후 시스템 입력은 개인 저장소의 `flake.lock`이 결정한다.

### 2.4 GitHub에 빈 원격 저장소 만들기

GitHub에서 `nixos-config` 같은 이름으로 새 저장소를 만든다. 기존 로컬 예제를 push할 것이므로 README, `.gitignore`, license를 선택하지 않고 비워 둔다. 처음에는 Private을 권장하지만 새 컴퓨터마다 clone 전에 인증이 필요하다. Public을 선택하면 이메일과 호스트 정보가 공개 가능한지 검토한다. 어느 쪽이든 토큰과 SSH 개인 키는 커밋하지 않는다.

원격 URL은 `git@github.com:<github-user>/nixos-config.git` 형태다.

### 2.5 임시 Git·OpenSSH와 SSH 인증

앞에서 갱신한 NixOS 채널로 임시 셸을 열고 첫 push가 끝날 때까지 유지한다.

```console
$ nix-shell -p git openssh
$ ssh-keygen -t ed25519 -C "<github-email>"
$ clip.exe < ~/.ssh/id_ed25519.pub
$ ssh -T git@github.com
```

`<nixpkgs>`를 찾지 못하면 `-I nixpkgs=/nix/var/nix/profiles/per-user/root/channels/nixos`를 추가한다. `github:` fetcher는 비인증 GitHub REST API 한도에 걸릴 수 있고, `git+https:` fetcher는 아직 없는 외부 Git을 요구하므로 최초 Git bootstrap에는 둘 다 사용하지 않는다. 기존 `nix-shell`은 일회성 bootstrap일 뿐 최종 구성은 계속 Flake가 소유한다.

공개 키만 GitHub의 **Settings → SSH and GPG keys**에 Authentication Key로 등록한다. 첫 연결의 host key fingerprint는 GitHub 공식 목록과 비교한다. 인증 성공 메시지가 나와도 GitHub가 SSH 셸을 제공하지 않아 테스트 명령은 종료 코드 1을 반환할 수 있다.

### 2.6 예제 복사와 Git 초기화

안내서를 내려받은 루트를 `<guide-root>`라고 하면 예제를 복사한다.

```console
$ mkdir -p ~/.config
$ cp -R <guide-root>/nixos-wsl-dev-environment/assets/example-config \
    ~/.config/nixos
$ cd ~/.config/nixos
$ git init -b main
$ git config --local user.name "<git-user-name>"
$ git config --local user.email "<git-email>"
$ git remote add origin git@github.com:<github-user>/nixos-config.git
$ git add .
```

예제의 기본 사용자 이름은 초기 WSL 사용자와 같은 `nixos`다. 첫 적용에서는 바꾸지 않는다.

### 2.7 첫 잠금 파일, 빌드, 적용

첫 원본 저장소에서만 잠금 파일을 만들고 즉시 Git에 추가한다. 로컬 Git Flake는 추적되지 않은 파일을 평가에서 제외할 수 있다.

```console
$ nix --extra-experimental-features "nix-command flakes" flake lock
$ git add flake.lock
$ nix --extra-experimental-features "nix-command flakes" flake show
$ sudo nixos-rebuild build \
    --option experimental-features "nix-command flakes" \
    --flake .#wsl
$ sudo nixos-rebuild switch \
    --option experimental-features "nix-command flakes" \
    --flake .#wsl
$ nix run .#home-manager -- build --flake .#nixos
$ nix run .#home-manager -- switch --flake .#nixos
```

첫 `flake lock`에서 `API rate limit exceeded`가 계속되면 SSH 인증 문제가 아니다. 한도 초기화를 기다리거나 `--option access-tokens "github.com=$GITHUB_TOKEN"`을 이 명령에만 전달하고 토큰은 저장소에 넣지 않는다.

### 2.8 첫 커밋과 push

staged 파일에 비밀이 없는지 확인한 뒤 원격으로 보낸다.

```console
$ git status --short
$ git diff --cached --stat
$ git commit -m "Bootstrap NixOS-WSL environment"
$ git push -u origin main
$ exit
```

GitHub에 `flake.nix`, `flake.lock`, `hosts/`, `modules/`, `dotfiles/`가 보이면 원본 저장소가 준비된 것이다. 이후 컴퓨터에서는 저장소를 clone하고 커밋된 `flake.lock`을 그대로 사용한다.

### 흔한 오류

| 증상 | 원인 | 해결 |
|---|---|---|
| `--no-distribution` 또는 `--from-file`을 인식하지 못함 | Windows/WSL이 오래됨 | WSL 업데이트 또는 공식 구형 설치/import 절차 사용 |
| `Permission denied (publickey)` | 공개 키 등록 또는 키 선택 오류 | 공개 키 등록과 `ssh -T git@github.com` 재확인 |
| push가 `non-fast-forward`로 거부됨 | 원격을 README 등으로 초기화함 | 첫 원격은 비워 두거나 기존 커밋을 의도적으로 병합 |
| Flake가 새 파일을 찾지 못함 | Git 미추적 파일 | `git add` 후 재평가 |

### 요약

- 첫 컴퓨터에서는 clone이 아니라 빈 GitHub 원격부터 만든다.
- 임시 Git·OpenSSH로 SSH 인증하고 예제를 로컬 저장소로 초기화한다.
- `flake.lock`은 원본 저장소에서 생성·커밋하고 이후 복원에서는 갱신하지 않는다.
- build 성공 후 적용하고 첫 커밋을 push한다.

### 추가 읽을거리

- [Microsoft WSL 설치](https://learn.microsoft.com/windows/wsl/install)
- [NixOS-WSL 공식 설치 문서](https://nix-community.github.io/NixOS-WSL/install.html)
- [기존 로컬 코드를 GitHub에 추가하기](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github)
- [GitHub SSH 연결 시험](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/testing-your-ssh-connection?platform=linux)

## 3. 저장소 구조와 Flake 설계

### 학습 목표

1. 시스템, 사용자, dotfiles를 디렉터리로 분리한다.
2. 하나의 Flake에서 NixOS와 standalone Home Manager 출력을 만든다.
3. `flake.lock`과 Git 추적 상태가 재현성에 미치는 영향을 설명한다.

### 3.1 목표 구조

이 장에서 `파일:`로 표시하는 상대 경로는 별도 설명이 없으면 구성 저장소 루트인
`~/.config/nixos`를 기준으로 한다.

경로: `~/.config/nixos/` (구성 저장소 루트의 디렉터리 구조)

```text
~/.config/nixos
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

### 3.2 Flake 입력

예제는 네 입력을 사용한다.

파일: `~/.config/nixos/flake.nix` (`inputs` 부분)

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

### 3.3 공통 NixOS 생성 함수

파일: `flake.nix` (`outputs`의 `let` 바인딩 일부)

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

사용자 이름을 한 곳에서 정하면 WSL 기본 사용자, NixOS 계정, Home Manager 출력의 이름을 맞추기 쉽다. 이미 설치된 WSL의 사용자 이름 변경은 단순 문자열 수정이 아니므로 8장의 마이그레이션 절차를 사용한다.

### 3.4 시스템 출력

파일: `flake.nix` (`nixosConfigurations` 부분)

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

### 3.5 독립 실행형 Home Manager 출력

파일: `flake.nix` (`homeConfigurations` 부분)

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

파일: `flake.nix` (`apps.${system}.home-manager` 부분)

```nix
apps.${system}.home-manager = {
  type = "app";
  program = "${home-manager.packages.${system}.default}/bin/home-manager";
};
```

따라서 아직 CLI가 없어도 외부 브랜치의 최신 상태를 다시 조회하지 않고 `nix run .#home-manager -- ...`로 잠긴 버전을 실행할 수 있다.

### 3.6 `flake.lock`을 만드는 시점

2장에서 제공 예제를 자신의 새 저장소로 초기화할 때 한 번 실행한다. 예제 파일은 잠금 생성 전에 Git에 추가한다.

```console
$ git add .
$ nix flake lock
$ git add flake.lock
$ git commit -m "Create NixOS and Home Manager configuration"
```

이후 새 머신 복원에서는 잠금 파일을 생성하지 않는다. `git clone`으로 받은 값을 그대로 사용한다.

#### Git에 추가하지 않으면 보이지 않는 파일

Git 저장소를 Flake로 평가할 때 새 파일이 추적되지 않으면 Nix의 입력 소스에서 빠질 수 있다.

```console
$ git status --short
?? modules/home/new-tool.nix
$ git add modules/home/new-tool.nix
$ nix flake show
```

네이티브 `hardware-configuration.nix`도 마찬가지다. 복사만 하고 `git add`하지 않으면 조건부 `native` 출력이 나타나지 않는다.

### 3.7 전체 예제

- [완성된 `flake.nix`](../assets/example-config/flake.nix)
- [예제 저장소 README](../assets/example-config/README.md)
- [예제 `.gitignore`](../assets/example-config/.gitignore)

개인 정보와 비밀은 예제에 넣지 않는다. 공개 가능한 Git 이름·이메일은 Home Manager에 추가할 수 있지만 토큰, SSH 개인 키, 레지스트리 인증 값은 별도 비밀 관리가 필요하다.

### 직접 확인

```console
$ nix flake show
```

하드웨어 파일이 없는 템플릿에서는 `nixosConfigurations.wsl`과 `homeConfigurations.nixos`가 핵심 출력이다. 네이티브 하드웨어 파일을 추적한 뒤에는 `nixosConfigurations.native`도 나타나야 한다.

### 요약

- 호스트, 공통 시스템, 사용자, dotfiles를 별도 디렉터리로 둔다.
- Flake는 하나지만 시스템 출력과 홈 출력은 독립적이다.
- NVM 소스도 non-Flake 입력으로 잠글 수 있다.
- 자신의 구성 저장소에는 `flake.lock`을 반드시 커밋한다.
- 새 Nix 파일은 평가 전에 Git에 추가한다.

### 추가 읽을거리

- [Flake 명령과 저장소 구조](https://nix.dev/manual/nix/latest/command-ref/new-cli/nix3-flake.html)
- [Nix에서 로컬 파일 다루기](https://nix.dev/tutorials/working-with-local-files.html)
- [NixOS-WSL Flake 예제](https://nix-community.github.io/NixOS-WSL/how-to/nix-flakes.html)

## 4. WSL과 네이티브 시스템 설정 분리

### 학습 목표

1. 공통 NixOS 정책과 호스트별 설정을 분리한다.
2. 외부 언어 런타임을 위한 `nix-ld`의 역할과 한계를 이해한다.
3. WSL 호스트를 build한 뒤 안전하게 switch한다.

### 4.1 공통 시스템 모듈

[예제 `modules/nixos/common.nix`](../assets/example-config/modules/nixos/common.nix)는 호스트 종류와 무관한 최소 정책만 둔다.

파일: `modules/nixos/common.nix` (핵심 내용)

```nix
{
  pkgs,
  username,
  ...
}:
{
  nix.settings.experimental-features = [
    "nix-command"
    "flakes"
  ];

  programs.nix-ld.enable = true;
  programs.zsh.enable = true;

  users.users.${username} = {
    isNormalUser = true;
    extraGroups = [ "wheel" ];
    shell = pkgs.zsh;
  };
}
```

각 선언의 이유는 다음과 같다.

- `nix-command`, `flakes`: bootstrap 이후 추가 CLI 플래그 없이 Flake 명령 사용
- `programs.zsh.enable`: zsh를 유효한 로그인 셸로 시스템에 등록
- 사용자 선언: 계정, 관리자 그룹, 기본 셸을 호스트 상태로 관리
- `programs.nix-ld.enable`: 일반 Linux 동적 로더 경로를 기대하는 외부 바이너리 지원

### 4.2 왜 `nix-ld`가 필요한가

NixOS에는 일반 배포판의 `/lib64/ld-linux-x86-64.so.2` 경로가 기본으로 존재하지 않는다. Nixpkgs가 빌드한 패키지는 이 구조에 맞게 패치되지만, NVM·uv·rustup 같은 도구가 업스트림에서 내려받은 바이너리는 전통적인 Linux 경로를 기대할 수 있다.

`nix-ld`는 이 바이너리가 기대하는 동적 로더 경로와 라이브러리 집합을 제공한다. 이 자료처럼 “버전 관리자 자체는 Nix, 런타임은 업스트림 도구”인 혼합 설계에서 실용적인 호환 계층이다.

모든 네이티브 의존성을 자동으로 해결하는 만능 계층은 아니다. 특정 Python wheel이나 Node 네이티브 애드온이 추가 라이브러리를 요구하면 `programs.nix-ld.libraries`를 보강하거나 해당 개발 라이브러리를 Nix 셸로 제공해야 한다.

### 4.3 WSL 호스트 모듈

파일: `hosts/wsl/default.nix` (핵심 내용)

```nix
{ username, ... }:
{
  networking.hostName = "nixos-wsl";

  wsl = {
    enable = true;
    defaultUser = username;
    interop.includePath = false;
  };

  system.stateVersion = "26.05";
}
```

`wsl.interop.includePath = false`는 Windows PATH를 Linux PATH에 자동으로 합치지 않는다. 동일한 명령 이름의 Windows 프로그램이 먼저 선택되는 일을 막아 개발 셸의 재현성을 높인다. 대신 `code.exe`, `powershell.exe` 같은 Windows 명령을 이름만으로 실행하는 편의는 줄어든다.

Windows PATH 연동이 더 중요하면 이 값을 `true`로 바꿀 수 있다. 이 선택은 Nix 재현성의 필수 조건이 아니라 팀의 interop 정책이다.

### 4.4 네이티브 호스트 모듈

파일: `hosts/native/default.nix` (핵심 내용)

```nix
{ ... }:
{
  imports = [ ./hardware-configuration.nix ];
  networking.hostName = "nixos-native";
  system.stateVersion = "26.05";
}
```

`hardware-configuration.nix`에는 파일시스템, 블록 장치, 커널 모듈처럼 실제 머신에서 생성된 정보가 들어간다. WSL 파일로 대체하거나 다른 머신의 파일을 그대로 복사하지 않는다.

기존 네이티브 NixOS를 편입한다면 `system.stateVersion`도 그 호스트의 기존 값을 유지한다. 26.05는 26.05로 새로 설치한 시스템의 예시일 뿐이다.

### 4.5 build 후 switch

WSL 저장소 루트에서 먼저 결과만 빌드한다. 첫 전환 전에는 아직 시스템의 Flake 설정이 활성화되지 않았을 수 있으므로 일회성 Nix 옵션을 함께 전달한다.

```console
$ sudo nixos-rebuild build \
    --option experimental-features "nix-command flakes" \
    --flake .#wsl
```

빌드가 성공해야 현재 시스템을 바꾼다.

```console
$ sudo nixos-rebuild switch \
    --option experimental-features "nix-command flakes" \
    --flake .#wsl
```

이 전환 뒤에는 `nix.settings.experimental-features`가 시스템에 적용되므로 이후 명령에서 `--option`을 생략한다. 기본 셸 변경은 현재 셸 프로세스를 바꾸지 않는다. Windows PowerShell에서 배포판을 종료하고 다시 연다.

```powershell
wsl --terminate NixOS
wsl -d NixOS
```

다시 들어온 뒤 확인한다.

```console
$ echo $SHELL
/run/current-system/sw/bin/zsh
$ nix config show experimental-features
$ test -e /lib64/ld-linux-x86-64.so.2 && echo nix-ld:ok
```

### 흔한 오류

| 증상 | 원인 | 해결 |
|---|---|---|
| `wsl` 옵션을 찾지 못함 | 공식 NixOS-WSL 모듈 누락 | Flake modules에 `nixos-wsl.nixosModules.default` 추가 |
| 새 셸이 bash로 유지됨 | 현재 로그인 세션이 전환 전부터 실행 중 | 배포판 종료 후 다시 시작 |
| 다운로드한 바이너리가 `No such file`로 실패 | 동적 로더 경로가 없음 | `nix-ld` 적용 여부와 interpreter 확인 |
| Windows 명령이 PATH에서 사라짐 | `interop.includePath = false` | 명시 경로 사용 또는 정책을 `true`로 변경 |

### 요약

- 계정, 기본 셸, Flake 기능, 동적 로더는 시스템 설정이다.
- WSL 옵션과 실제 하드웨어 설정은 별도 호스트 모듈에 둔다.
- 외부 런타임은 `nix-ld`가 필요할 수 있지만 추가 네이티브 라이브러리는 별도다.
- 항상 build를 성공시킨 뒤 switch한다.

### 추가 읽을거리

- [NixOS-WSL 옵션](https://nix-community.github.io/NixOS-WSL/options.html)
- [nix-ld 설명](https://github.com/nix-community/nix-ld)
- [NixOS 안정판 매뉴얼](https://nixos.org/manual/nixos/stable/)

## 5. 독립 실행형 Home Manager 구성

### 학습 목표

1. 사용자 패키지와 설정을 시스템에서 독립적으로 적용한다.
2. Home Manager 모듈과 dotfiles를 적절히 나눈다.
3. 고정된 NVM 소스와 쓰기 가능한 Node 설치 영역을 함께 구성한다.

### 5.1 사용자 프로필의 진입점

[예제 `modules/home/default.nix`](../assets/example-config/modules/home/default.nix)는 사용자 환경의 공통 진입점이다.

파일: `modules/home/default.nix` (핵심 내용)

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
      uv
      rustup
      curl
      unzip
      gcc
      pkg-config
    ];

    sessionPath = [
      "$HOME/.local/bin"
      "$HOME/.cargo/bin"
    ];
  };

  programs.home-manager.enable = true;
}
```

`uv`와 `rustup`은 Nixpkgs의 잠긴 리비전에서 설치된다. Python, `rustc`, Cargo는 직접 패키지 목록에 넣지 않는다. `gcc`와 `pkg-config`는 프로젝트가 네이티브 확장을 빌드할 때 필요한 일반 지원 도구다.

`programs.home-manager.enable = true`는 최초 bootstrap 이후 `home-manager` CLI 자체를 관리되는 사용자 프로필에 유지한다.

### 5.2 프로그램 전용 모듈 사용

[예제 `programs.nix`](../assets/example-config/modules/home/programs.nix)는 다음 프로그램을 선언한다.

- Git
- bat
- zsh
- Starship
- fzf
- Autojump

대표적인 형태는 다음과 같다.

파일: `modules/home/programs.nix` (프로그램 선언 일부)

```nix
programs = {
  git = {
    enable = true;
    settings = {
      init.defaultBranch = "main";
      core.editor = "nvim";
      pull.rebase = false;
    };
  };

  zsh = {
    enable = true;
    enableCompletion = true;
    autosuggestion.enable = true;
    syntaxHighlighting.enable = true;
  };

  starship.enable = true;
  fzf.enable = true;
  autojump.enable = true;
};
```

Home Manager 모듈은 패키지 설치와 셸 통합을 함께 처리한다. 예를 들어 `enableZshIntegration = true`는 필요한 초기화 코드를 생성하므로 `.zshrc`에 같은 코드를 다시 쓰지 않는다.

Nixpkgs의 bat 실행 파일 이름은 Ubuntu의 `batcat`이 아니라 `bat`다. 예제는 익숙한 `cat` 사용을 위해 `cat = "bat"` 별칭을 추가한다.

Neovim과 LazyVim은 `lazyvim.nix`로 분리한다. 이 모듈은 Neovim, Nixpkgs가
고정한 lazy.nvim, 공통 요구사항과 dotfiles 링크만 제공한다. 언어별 extra는 각
프로젝트의 `.lazy.lua`가 선택한다.

### 5.3 dotfiles 배치

Neovim 설정은 Lua 원본을 유지한다. 프로젝트 밖의 LazyVim 기본 구성은 plugin
리비전을 `lazy-lock.json`에 쓰므로 설정 디렉터리를 Git 작업 트리의 쓰기 가능한
링크로 둔다.

파일: `modules/home/lazyvim.nix` (Neovim dotfiles 링크 부분)

```nix
xdg.enable = true;
xdg.configFile."nvim".source = config.lib.file.mkOutOfStoreSymlink
  "${config.home.homeDirectory}/.config/nixos/dotfiles/nvim";
```

이 선언은 저장소의 [Neovim 설정](../assets/example-config/dotfiles/nvim/init.lua)을
`~/.config/nvim`에 연결한다. clone 위치를 바꾸면 링크 대상도 바꾼다. Neovim 설정과
기본 `lazy-lock.json`은 링크 대상인 Git 작업 트리에서 검토하고 커밋한다. 프로젝트
안에서는 해당 저장소의 `.lazy-lock.json`을 사용한다.

큰 Neovim 구성을 여러 파일로 나눠도 `dotfiles/nvim/` 디렉터리 전체를 그대로 관리할 수 있다.

### 5.4 NVM은 일반 패키지와 다르다

NVM은 독립 실행 파일이 아니라 현재 셸의 함수와 환경을 바꾸는 스크립트다. 또한 `$NVM_DIR/versions` 아래에 Node.js를 내려받아야 한다.

Flake 입력 전체를 `$NVM_DIR`에 심볼릭 링크하면 디렉터리가 Nix Store를 가리켜 읽기 전용이 된다. 예제는 이 문제를 다음처럼 푼다.

```text
Nix Store의 고정 소스
  ├── nvm.sh ─────────────┐
  ├── nvm-exec ──────────┼→ ~/.local/share/nvm/의 개별 링크
  └── bash_completion ───┘

쓰기 가능한 사용자 상태
  └── ~/.local/share/nvm/versions/node/...
```

[전체 `nvm.nix`](../assets/example-config/modules/home/nvm.nix)의 파일 선언은 다음과 같다.

파일: `modules/home/nvm.nix` (NVM 파일 배치 부분)

```nix
let
  nvmRoot = ".local/share/nvm";
in
{
  home.file."${nvmRoot}/nvm.sh".source =
    inputs.nvm-src.outPath + "/nvm.sh";

  home.file."${nvmRoot}/nvm-exec" = {
    source = inputs.nvm-src.outPath + "/nvm-exec";
    executable = true;
  };

  home.file."${nvmRoot}/bash_completion".source =
    inputs.nvm-src.outPath + "/bash_completion";
}
```

### 5.5 `.nvmrc` 자동 설치와 전환

zsh 초기화에서 NVM을 source한 뒤 `chpwd` 훅을 등록한다. 알고리즘은 다음과 같다.

```text
셸 시작 또는 디렉터리 변경
  → 상위 방향으로 가장 가까운 .nvmrc 탐색
  → 요청 버전이 미설치면 nvm install
  → 설치되어 있고 현재 버전과 다르면 nvm use
  → .nvmrc 영역을 벗어나면 nvm deactivate
```

핵심 코드는 다음과 같다.

파일: `modules/home/nvm.nix` (`programs.zsh.initContent` 안의 함수 일부)

```zsh
load-nvmrc() {
  local nvmrc_path requested_version installed_version
  nvmrc_path="$(nvm_find_nvmrc)"

  if [[ -n "$nvmrc_path" ]]; then
    requested_version="$(command cat "$nvmrc_path")"
    installed_version="$(nvm version "$requested_version")"

    if [[ "$installed_version" == "N/A" ]]; then
      nvm install
    elif [[ "$(nvm current)" != "$installed_version" ]]; then
      nvm use --silent
    fi
  else
    nvm deactivate --silent >/dev/null 2>&1 || true
  fi
}
```

이 동작은 프로젝트 디렉터리 진입만으로 네트워크 다운로드를 일으킬 수 있다. 자동 설치가 불편한 환경에서는 `nvm install` 부분을 안내 메시지로 바꾸고 수동 설치 정책을 사용한다.

### 5.6 최초 적용

시스템 설정을 먼저 적용한 뒤 로컬 Flake가 노출한 Home Manager 앱을 한 번 사용한다. 이 앱은 저장소의 `flake.lock`에 기록된 Home Manager 입력을 사용한다.

```console
$ cd ~/.config/nixos
$ nix run .#home-manager -- switch --flake .#nixos
```

이후부터는 관리된 CLI를 쓴다.

```console
$ home-manager build --flake .#nixos
$ home-manager switch --flake .#nixos
```

새 zsh 세션에서 확인한다.

```console
$ type nvm
nvm is a shell function
$ uv --version
$ rustup --version
$ git --version
$ bat --version
$ rg --version
$ nvim --version
$ starship --version
```

### 흔한 오류

| 증상 | 원인 | 해결 |
|---|---|---|
| 기존 `.zshrc` 또는 Neovim 디렉터리 충돌 | Home Manager가 관리할 위치에 수동 파일 존재 | 기존 파일을 백업하고 원본을 모듈/dotfiles로 이동 |
| `nvm`이 명령이 아님 | zsh 초기화가 적용되지 않음 | `echo $SHELL`, 생성된 `.zshrc`, 새 로그인 세션 확인 |
| NVM이 Node를 설치하지 못함 | `$NVM_DIR` 전체가 읽기 전용 링크 | 개별 스크립트만 링크하고 부모 디렉터리를 쓰기 가능하게 유지 |
| `home-manager` 명령이 없음 | 최초 bootstrap 전 | `nix run ...release-26.05 -- switch ...` 실행 |

### 요약

- standalone Home Manager는 시스템과 별도로 사용자 프로필을 전환한다.
- 전용 모듈은 설치와 셸 통합을 함께 처리한다.
- 큰 애플리케이션 설정은 dotfiles 원본을 Home Manager가 배치한다.
- NVM 스크립트는 고정하되 Node 설치 디렉터리는 쓰기 가능해야 한다.
- 최초 bootstrap 뒤에는 Home Manager가 자신의 CLI도 관리한다.

### 추가 읽을거리

- [Home Manager standalone 설치](https://nix-community.github.io/home-manager/installation/standalone.html)
- [Home Manager 옵션](https://nix-community.github.io/home-manager/options.html)
- [NVM 공식 저장소](https://github.com/nvm-sh/nvm)

## 6. uv, NVM, rustup으로 프로젝트 툴체인 관리

### 학습 목표

1. 도구 버전, 언어 런타임 버전, 프로젝트 의존성 잠금을 구분한다.
2. Python, Node.js, Rust 프로젝트를 각 생태계의 표준 파일로 복원한다.
3. Nix 입력 업데이트가 언어 도구에 미치는 영향을 예측한다.

### 6.1 세 층의 버전

| 계층 | Python | Node.js | Rust |
|---|---|---|---|
| Nix/Flake가 고정 | uv 패키지 | NVM 0.40.4 소스 | rustup 패키지 |
| 프로젝트가 고정 | `.python-version` | `.nvmrc` | `rust-toolchain.toml` |
| 의존성을 고정 | `uv.lock` | `package-lock.json` 등 | `Cargo.lock` |

Nixpkgs 입력의 리비전이 uv와 rustup 패키지 버전을 결정한다. NVM은 별도 Flake 입력의 태그와 잠금 리비전이 결정한다. 하지만 이 도구가 내려받는 Python, Node.js, Rust 툴체인은 각 프로젝트 파일의 책임이다.

이 설계는 Nix가 모든 언어 패키지를 대신 관리하는 방식보다 재현성 범위가 좁다. 대신 기존 프로젝트의 표준 파일과 CI 흐름을 유지한다.

### 6.2 Python과 uv

uv는 시스템에 적합한 Python이 없으면 관리형 Python을 자동으로 내려받을 수 있다. `.python-version`은 기본 Python 요청을, `pyproject.toml`은 프로젝트 요구사항을, `uv.lock`은 해결된 의존성을 기록한다.

새 프로젝트에서 정확한 Python 패치 버전을 선택하는 예시는 다음과 같다.

```console
$ uv python install 3.13.7
$ uv python pin 3.13.7
$ uv init
$ uv add httpx
$ git add .python-version pyproject.toml uv.lock
```

복원할 때는 잠금 파일을 수정하지 않도록 `--frozen`을 사용한다.

```console
$ uv sync --frozen
$ uv run python --version
Python 3.13.7
```

마이너 버전만 기록할 수도 있지만 정확한 패치 버전은 의도를 더 분명히 한다. uv 릴리스가 제공하는 다운로드 가능 Python 목록도 uv 버전에 묶이므로, 새 Python 패치가 필요하면 Nix 입력의 uv 업데이트 여부도 함께 확인한다.

### 6.3 Node.js와 NVM

NVM은 `.nvmrc`의 값을 읽어 Node.js를 설치하고 현재 셸의 PATH를 바꾼다. 새 프로젝트에서는 현재 지원되는 LTS를 선택한 뒤 실제 버전 문자열을 저장한다.

```console
$ nvm install --lts
$ node --version > .nvmrc
$ cat .nvmrc
v24.x.y
$ git add .nvmrc package.json package-lock.json
```

`lts/*`나 `24` 같은 별칭을 `.nvmrc`에 넣으면 나중에 설치할 때 더 최신 패치로 해석될 수 있다. 정확한 복원이 목표라면 `node --version`이 출력한 `vMAJOR.MINOR.PATCH`를 커밋한다.

다른 머신에서는 디렉터리에 들어올 때 zsh 훅이 버전을 설치·선택한다. 의존성은 별도로 잠금 파일에서 복원한다.

```console
$ cd project
$ node --version
$ npm ci
```

pnpm이나 Yarn을 사용한다면 해당 패키지 관리자의 lockfile과 Corepack 정책을 프로젝트에 기록한다. NVM은 Node 런타임만 관리한다.

### 6.4 Rust와 rustup

rustup은 `rustc`와 Cargo 앞의 프록시로 동작하며 디렉터리의 `rust-toolchain.toml`을 보고 툴체인을 선택한다.

파일: 프로젝트 루트의 `rust-toolchain.toml` (전체 예시)

```toml
[toolchain]
channel = "1.88.0"
profile = "minimal"
components = ["clippy", "rustfmt"]
```

파일과 의존성 잠금을 함께 커밋한다.

```console
$ git add rust-toolchain.toml Cargo.toml Cargo.lock
$ cargo build --locked
$ rustc --version
```

예제 사용자 프로필은 `RUSTUP_AUTO_INSTALL=1`을 설정하므로 지정 툴체인이 없으면 rustup 프록시가 설치할 수 있다. 자동 네트워크 사용을 원하지 않으면 `RUSTUP_AUTO_INSTALL=0`으로 바꾸고 다음을 명시적으로 실행한다.

```console
$ rustup toolchain install 1.88.0 \
    --profile minimal \
    --component clippy \
    --component rustfmt
```

### 6.5 프로젝트 복원 명령의 의미

```text
uv sync --frozen
  → Python 요청 확인
  → 필요한 관리형 Python 준비
  → uv.lock 그대로 환경 동기화

cd Node 프로젝트
  → .nvmrc 확인
  → 필요한 Node 설치/선택
  → npm ci로 package-lock.json 그대로 설치

cargo build --locked
  → rust-toolchain.toml의 툴체인 선택
  → Cargo.lock 변경 없이 빌드
```

Nix는 이 과정의 도구를 제공하지만 프로젝트 의존성 다운로드까지 Nix Store에 넣지는 않는다. 따라서 언어별 캐시와 설치 상태는 삭제 후 다시 만들 수 있는 파생 상태로 취급한다.

### 6.6 네이티브 라이브러리가 필요한 프로젝트

`gcc`와 `pkg-config`만으로 모든 C 라이브러리가 생기지는 않는다. OpenSSL, SQLite, PostgreSQL 헤더처럼 프로젝트별 네이티브 의존성이 필요하면 두 선택지가 있다.

1. 공통 개발 머신 전체에 필요하면 Home Manager 패키지에 추가한다.
2. 특정 프로젝트에만 필요하면 프로젝트의 `devShell`을 별도 Flake 출력으로 만든다.

이 자료의 전역 Flake는 범용 사용자 도구까지만 다룬다. 프로젝트별 `devShell`은 해당 프로젝트 저장소가 소유하는 편이 경계를 지키기 쉽다.

### 6.7 direnv와 LazyVim을 이용한 세 언어 실전 환경

Home Manager는 Neovim, lazy.nvim, 최소 LazyVim 기반, uv, NVM, rustup, direnv,
nix-direnv를 제공한다. 프로젝트는 `.lazy.lua`와 `.lazy-lock.json`으로 언어 extra와
plugin 리비전을 소유한다. `flake.nix`는 언어 런타임을 중복 설치하지 않고 OpenSSL이나
`pkg-config` 같은 네이티브 의존성만 제공한다. `.envrc`는 한 줄이다.

파일: 프로젝트 루트의 `.envrc` (전체)

```bash
use flake
```

Python devShell은 `.venv/bin`, Node.js devShell은 `node_modules/.bin`을 PATH 앞에
둔다. Rust는 `rust-toolchain.toml`에 `rust-analyzer` component를 포함한다.

```text
Python  .python-version + uv.lock        -> .venv/bin/basedpyright, ruff
Node.js .nvmrc + package-lock.json       -> node_modules/.bin/vtsls
Rust    rust-toolchain.toml + Cargo.lock -> rustup proxy의 rust-analyzer
```

Mason은 Home Manager의 공통 LazyVim 정책에서 끈다. 각 프로젝트는 필요한 extra만
선택한다. 예를 들어 Python 저장소의 `.lazy.lua`는 다음과 같다.

파일: Python 프로젝트 루트의 `.lazy.lua` (전체)

```lua
vim.g.lazyvim_python_lsp = "basedpyright"
vim.g.lazyvim_python_ruff = "ruff"

return {
  { import = "lazyvim.plugins.extras.lang.python" },
  { import = "lazyvim.plugins.extras.test.core" },
}
```

lazy.nvim의 `local_spec = true`는 현재 디렉터리부터 상위로 `.lazy.lua`를 찾는다.
예제는 프로젝트 경로 hash로 plugin root를 분리하고 프로젝트 루트의
`.lazy-lock.json`을 사용한다. 따라서 프로젝트별 plugin 구성과 checkout 리비전이
서로 충돌하지 않는다.

최초에는 `nix develop`로 수동 검증한 뒤 direnv를 승인한다.

```console
$ nix flake lock
$ nix develop
$ command -v <runtime> <language-server>
$ nvim .
# .lazy.lua 신뢰 확인 후 :Lazy sync, :LazyHealth, :LspInfo
$ exit
$ less .envrc
$ less .lazy.lua
$ direnv allow
```

`direnv allow`는 `.envrc`만 승인한다. `.lazy.lua`는 Neovim의 `vim.secure.read()`가
별도로 확인하고 내용 hash를 trust DB에 저장한다. 두 파일 모두 실행 가능한 코드이므로
clone한 뒤 각각 검토한다.

완성 예제는 [Python](../assets/example-dev-shell/python/flake.nix),
[Node.js](../assets/example-dev-shell/nodejs/flake.nix),
[Rust](../assets/example-dev-shell/rust/flake.nix) 디렉터리에 있다. 각 저장소는
`flake.lock`, 언어별 lock, `.lazy.lua`, `.lazy-lock.json`을 커밋하고 `.direnv`,
`.venv`, `node_modules`, `target`과 plugin cache는 제외한다.

### 흔한 오류

| 증상 | 원인 | 해결 |
|---|---|---|
| `.nvmrc`가 있는데 매번 다른 패치 설치 | 별칭 또는 메이저만 기록 | 정확한 `node --version` 값을 커밋 |
| `uv sync`가 lock을 변경 | 복원과 갱신을 구분하지 않음 | CI·복원에서는 `uv sync --frozen` 사용 |
| `cargo build`가 다른 툴체인 사용 | 툴체인 파일 누락 또는 상위 override | `rustup show`, `rust-toolchain.toml` 위치 확인 |
| 네이티브 패키지 빌드 실패 | 시스템 라이브러리/헤더 누락 | 프로젝트 `devShell` 또는 필요한 Nix 패키지 추가 |
| `.lazy.lua`가 적용되지 않음 | Neovim trust 거부 또는 파일 변경 | 내용을 검토하고 `:trust`, Neovim 재실행 |
| `.lazy-lock.json`이 비어 있음 | 아직 `:Lazy sync`를 실행하지 않음 | 프로젝트에서 동기화 후 lock diff를 커밋 |

### 요약

- Nix는 버전 관리자 자체를, 프로젝트 파일은 런타임을 고정한다.
- 언어 버전 파일과 의존성 lockfile은 서로 다른 책임을 가진다.
- 정확한 패치 버전을 기록해야 시간에 따른 별칭 이동을 피할 수 있다.
- 프로젝트별 네이티브 의존성은 프로젝트 `devShell`로 분리하는 편이 좋다.
- 프로젝트별 LazyVim extra와 plugin 리비전은 `.lazy.lua`, `.lazy-lock.json`이 소유한다.

### 추가 읽을거리

- [uv Python 버전](https://docs.astral.sh/uv/concepts/python-versions/)
- [uv 프로젝트 동기화](https://docs.astral.sh/uv/concepts/projects/sync/)
- [NVM `.nvmrc` 사용법](https://github.com/nvm-sh/nvm#nvmrc)
- [rustup 툴체인 override](https://rust-lang.github.io/rustup/overrides.html)
- [rustup 환경 변수](https://rust-lang.github.io/rustup/environment-variables.html)

## 7. Git clone에서 완전한 환경까지

이 장은 2장에서 원본 구성 저장소와 `flake.lock`을 push한 뒤 두 번째 컴퓨터나 재설치 환경에 복원하는 절차다. 개인 구성 저장소가 아직 없다면 먼저 2장의 최초 생성 절차를 완료한다.

### 학습 목표

1. 잠긴 구성 저장소를 새 NixOS-WSL에 적용한다.
2. 네이티브 NixOS에서 사용자 프로필만 독립적으로 복원한다.
3. 실제 하드웨어 시스템 설정을 안전하게 저장소에 편입한다.

### 7.1 무엇이 “한 번의 clone으로 복원”되는가

OS 이미지 등록, 초기 암호, 저장소 접근 자격 증명은 Git 바깥의 bootstrap이다. 특히 Private 저장소는 새 컴퓨터의 공개 키를 GitHub에 등록해야 한다. 그 뒤의 선언 상태는 한 저장소 clone에서 복원한다.

```text
bootstrap
  Windows WSL 등록 + 암호 + 저장소 접근

Git 저장소
  시스템 선언 + 사용자 선언 + dotfiles + flake.lock

파생 상태
  /nix/store 결과 + Home Manager 세대 + 언어 런타임/의존성
```

언어 런타임 캐시는 Git에 넣지 않지만 프로젝트 파일을 기준으로 다시 받을 수 있다.

### 7.2 새 NixOS-WSL 전체 복원

Windows에서 NixOS-WSL을 등록하고 들어온다.

```powershell
wsl --install --from-file .\nixos.wsl --name NixOS
wsl -d NixOS
```

WSL 안에서 초기 준비를 하고 임시 Git·OpenSSH 셸을 연다.

```console
$ passwd
$ sudo nix-channel --update
$ nix-shell -p git openssh
```

이 단계는 채널 기반 bootstrap이다. `github:` Flake URL의 REST API 한도와 `git+https:`의 외부 Git 선행 요구를 모두 피한다. Private 저장소라면 2.7절과 같은 방법으로 이 WSL 인스턴스의 SSH 공개 키를 GitHub에 등록하고 `ssh -T git@github.com`을 확인한다. SSH 개인 키는 구성 저장소에서 복원하지 않는다.

```console
$ git clone <repository-url> ~/.config/nixos
$ cd ~/.config/nixos
```

잠금 파일이 있는지 확인하고 시스템을 build한 뒤 전환한다.

```console
$ test -f flake.lock
$ sudo nixos-rebuild build \
    --option experimental-features "nix-command flakes" \
    --flake .#wsl
$ sudo nixos-rebuild switch \
    --option experimental-features "nix-command flakes" \
    --flake .#wsl
```

Home Manager를 최초 적용한다.

```console
$ nix run .#home-manager -- build --flake .#nixos
$ nix run .#home-manager -- switch --flake .#nixos
$ exit  # 임시 Nix 셸 종료
$ exit  # NixOS-WSL 세션 종료
```

Windows에서 배포판을 다시 시작한다.

```powershell
wsl --terminate NixOS
wsl -d NixOS
```

사용자 환경을 확인한다.

```console
$ echo $SHELL
$ type nvm
$ uv --version
$ rustup --version
$ git --version
$ nvim --version
```

### 7.3 프로젝트 복원

개발 환경과 프로젝트 저장소는 별도다. 각 프로젝트를 clone한 뒤 해당 생태계의 잠금 명령을 사용한다.

```console
## Python
$ git clone <python-project-url>
$ cd python-project
$ uv sync --frozen

## Node.js
$ git clone <node-project-url>
$ cd node-project
$ npm ci

## Rust
$ git clone <rust-project-url>
$ cd rust-project
$ cargo build --locked
```

Node 프로젝트는 디렉터리 진입 시 NVM 훅이 먼저 `.nvmrc`를 처리한다.

### 7.4 네이티브 NixOS에서 사용자 환경만 복원

대상 네이티브 NixOS의 사용자 이름과 예제의 `username`이 같다면 시스템 설정을 건드리지 않고 Home Manager만 적용할 수 있다.

```console
$ git clone <repository-url> ~/.config/nixos
$ cd ~/.config/nixos
$ nix run .#home-manager -- switch --flake .#nixos
```

이 경로는 기존 부트로더, 파일시스템, 네트워크 설정을 그대로 둔다. 사용자 도구와 dotfiles만 필요할 때 가장 안전하다.

사용자 이름이 다르면 `flake.nix`의 `username`과 `home.homeDirectory`가 일치하도록 자신의 저장소에 별도 Home Manager 출력을 추가한다. 여러 사용자를 지원하려면 출력 이름을 `user@host` 형태로 늘릴 수 있다.

### 7.5 네이티브 시스템 설정까지 관리

실제 네이티브 호스트에서 생성된 파일을 복사한다.

```console
$ cd ~/.config/nixos
$ cp /etc/nixos/hardware-configuration.nix \
    hosts/native/hardware-configuration.nix
$ git add hosts/native/hardware-configuration.nix
```

기존 `/etc/nixos/configuration.nix`의 `system.stateVersion`을 확인해 `hosts/native/default.nix`에 같은 값으로 기록한다. 부트로더, 그래픽, 네트워크 같은 기존 정책도 검토해 `hosts/native`로 옮긴다.

이제 조건부 출력이 나타나는지 확인한다.

```console
$ nix flake show
$ sudo nixos-rebuild build --flake .#native
```

빌드 결과를 검토한 뒤에만 전환한다.

```console
$ sudo nixos-rebuild switch --flake .#native
```

하드웨어 모듈은 비밀 파일은 아니지만 호스트 구조를 노출할 수 있다. 공개 저장소에 둘지 조직의 위협 모델에 따라 판단한다.

### 7.6 성공 기준

- `nixos-rebuild build --flake .#wsl` 또는 `.#native`가 성공한다.
- `home-manager build --flake .#nixos`가 성공한다.
- 로그인 셸이 zsh다.
- 지정한 사용자 도구가 PATH에서 발견된다.
- Neovim 설정이 `~/.config/nvim`에 배치된다.
- `.nvmrc`, `.python-version`, `rust-toolchain.toml`이 각각 런타임을 선택한다.
- clone 후 `flake.lock`에 변경이 생기지 않는다.

### 직접 확인

복원 직후 다음을 실행한다.

```console
$ git status --short
$ readlink -f ~/.config/nvim/init.lua
$ home-manager generations
$ sudo nixos-rebuild list-generations
```

단순 복원 뒤 구성 저장소가 깨끗해야 한다. 잠금 파일이나 모듈이 변경되었다면 복원 과정에 업데이트 작업이 섞인 것이다.

### 요약

- bootstrap과 Git으로 복원되는 선언 상태를 구분한다.
- WSL은 시스템 적용 후 Home Manager를 적용한다.
- 네이티브 NixOS에서는 사용자 프로필만 먼저 적용할 수 있다.
- 네이티브 시스템 출력에는 해당 호스트의 하드웨어 모듈과 기존 상태 버전이 필요하다.
- 프로젝트는 언어별 버전 파일·lockfile과 `.lazy.lua`·`.lazy-lock.json`에서 다시 만든다.

## 8. 업데이트, 롤백, 문제 해결

### 학습 목표

1. 복원과 업데이트를 서로 다른 절차로 운영한다.
2. 시스템, 사용자, 프로젝트 중 실패한 계층을 식별한다.
3. NixOS와 Home Manager 세대를 독립적으로 롤백한다.

### 8.1 안전한 업데이트 루틴

복원에서는 `flake.lock`을 유지하지만 업데이트에서는 의도적으로 바꾼다.

```console
$ cd ~/.config/nixos
$ nix flake update
$ git diff -- flake.lock
$ nix fmt
$ sudo nixos-rebuild build --flake .#wsl
$ home-manager build --flake .#nixos
```

두 빌드가 성공한 뒤 전환한다.

```console
$ sudo nixos-rebuild switch --flake .#wsl
$ home-manager switch --flake .#nixos
```

동작을 확인한 뒤 잠금 파일을 커밋한다.

```console
$ git add flake.lock
$ git commit -m "Update Nix inputs"
```

이 커밋은 Nixpkgs, Home Manager, NixOS-WSL 입력의 변경을 하나의 검토 단위로 만든다. 특정 입력만 갱신하려면 사용 중인 Nix의 `nix flake update --help`에서 입력별 문법을 먼저 확인한다. Nix CLI 버전에 따라 이 문법이 달라질 수 있다.

프로젝트 plugin은 별도 저장소에서 `:Lazy update` 후 `.lazy-lock.json` diff를
검토·커밋한다. 복원과 롤백에서는 커밋된 lock을 되돌리고 `:Lazy restore`를 실행한다.

### 8.2 롤백 단위

시스템 전환이 문제라면 NixOS 세대를 되돌린다.

```console
$ sudo nixos-rebuild switch --rollback
```

사용자 설정만 문제라면 Home Manager 세대를 확인하고 직전 세대로 전환한다.

```console
$ home-manager generations
$ home-manager switch --rollback
```

Git의 `flake.lock`도 문제가 생기기 전 커밋으로 되돌려야 다음 rebuild가 같은 상태를 유지한다. 세대 롤백은 현재 실행 상태를 바꾸고, Git 되돌리기는 다음 빌드의 입력을 바꾼다. 둘은 목적이 다르다.

프로젝트의 `.nvmrc`, `.python-version`, `rust-toolchain.toml` 변경은 NixOS 세대 롤백 대상이 아니다. 프로젝트 Git 이력과 언어별 설치 상태를 확인한다.

### 8.3 계층별 진단 순서

```text
명령 자체가 없거나 로그인 셸이 다름
  → NixOS / Home Manager 적용 상태

도구는 있지만 런타임 선택이 다름
  → .nvmrc / .python-version / rust-toolchain.toml

런타임은 맞지만 빌드가 실패
  → 프로젝트 lockfile / 네이티브 라이브러리
```

처음부터 `nixos-rebuild`를 반복하기보다 실패한 소유권 계층에서 시작한다.

### 8.4 오류 표

| 증상 | 원인 | 확인 | 해결 |
|---|---|---|---|
| 새 `.nix` 파일을 찾지 못함 | Git 미추적 파일은 Flake 입력에서 빠짐 | `git status --short` | `git add` 후 다시 build |
| `home-manager`가 기존 파일과 충돌 | 관리 대상에 수동 파일 존재 | 오류가 지목한 경로 | 백업 후 모듈/dotfiles로 원본 이동 |
| `nvm: command not found` | zsh 초기화 또는 로그인 셸 문제 | `echo $SHELL`, `type nvm` | WSL 재시작, `nvm.nix` 적용 확인 |
| `.nvmrc` 버전이 설치되지 않음 | 훅 미실행 또는 값이 유효하지 않음 | `nvm_find_nvmrc`, `nvm install` | 파일 내용과 NVM 출력 확인 |
| Python/Node/Rust 바이너리가 실행되지 않음 | 동적 로더 또는 공유 라이브러리 누락 | 오류의 interpreter/library | `nix-ld`와 추가 라이브러리 검토 |
| `native` 출력이 없음 | 하드웨어 파일 부재 또는 Git 미추적 | `git ls-files hosts/native` | 파일 복사 후 `git add` |
| 복원 직후 `flake.lock` 변경 | 복원 중 update 실행 | `git diff flake.lock` | 잠긴 커밋으로 되돌리고 다시 build |
| Windows 명령이 이름으로 실행되지 않음 | Windows PATH 제외 정책 | `wsl.interop.includePath` | 명시 경로 또는 옵션 변경 |

### 8.5 사용자 이름 변경

이미 설치된 NixOS-WSL에서 기본 사용자 이름을 바꿀 때는 일반 `switch`를 사용하지 않는다. 공식 절차의 핵심은 다음과 같다.

1. `flake.nix`의 `username`, NixOS 사용자 선언, `wsl.defaultUser`, Home Manager 홈 경로를 새 이름에 맞춘다.
2. WSL 안에서 부팅 세대를 만든다.

   ```console
   $ sudo nixos-rebuild boot --flake .#wsl
   ```

3. 셸을 나간 뒤 PowerShell에서 배포판을 종료한다.

   ```powershell
   wsl --terminate NixOS
   wsl -d NixOS --user root exit
   wsl --terminate NixOS
   wsl -d NixOS
   ```

4. 새 사용자로 들어온 뒤 Home Manager 출력을 적용한다.

공식 문서는 기존 WSL 사용자를 변경할 때 `nixos-rebuild switch`가 새 계정을 잘못 구성할 수 있다고 경고한다. 사용자 이름은 가능하면 저장소를 처음 만들 때 확정한다.

### 8.6 릴리스 업그레이드

26.05에서 다음 NixOS 릴리스로 이동할 때는 다음을 함께 검토한다.

- `nixpkgs.url`의 브랜치
- Home Manager의 대응 `release-YY.MM` 브랜치
- NixOS-WSL 릴리스 노트
- NixOS와 Home Manager 릴리스 노트
- 폐기되거나 이름이 바뀐 옵션

`system.stateVersion`과 `home.stateVersion`은 자동으로 올리지 않는다. 릴리스 브랜치와 상태 버전은 서로 다른 개념이다.

### 8.7 비밀과 개인 데이터

다음 값은 평문 구성 저장소에 넣지 않는다.

- SSH 개인 키
- Git 호스팅 토큰
- npm·PyPI 인증 토큰
- 클라우드 자격 증명
- 조직 내부 인증서의 개인 키

이 자료는 비밀 관리 체계를 포함하지 않는다. 초기에는 복원 후 별도로 배치하고, 필요해지면 sops-nix나 agenix 같은 도구를 별도 위협 모델과 함께 설계한다.

### 8.8 운영 체크리스트

#### 평상시 변경

1. Nix 또는 dotfile 원본 수정
2. `nix fmt`
3. 시스템 변경이면 `nixos-rebuild build`
4. 사용자 변경이면 `home-manager build`
5. 성공한 계층만 `switch`
6. 동작 확인 후 Git 커밋

#### 새 머신 복원

1. 잠긴 저장소 clone
2. 시스템 build/switch
3. Home Manager bootstrap/switch
4. 새 로그인 셸
5. 프로젝트 clone과 언어별 locked restore

#### 문제 발생

1. 시스템·사용자·프로젝트 중 소유 계층 식별
2. 현재 Git diff와 잠금 파일 확인
3. 해당 계층의 세대 또는 프로젝트 커밋 롤백
4. build로 수정 검증 후 switch

### 요약

- update는 잠금 파일을 바꾸고, restore는 잠금 파일을 유지한다.
- 시스템과 Home Manager는 독립적으로 빌드하고 롤백한다.
- 오류는 소유권 계층부터 찾는다.
- 기존 WSL 사용자 이름 변경에는 `boot`와 WSL 재시작 절차가 필요하다.
- 비밀은 평문 Flake나 dotfiles에 넣지 않는다.

### 추가 읽을거리

- [NixOS-WSL 사용자 이름 변경](https://nix-community.github.io/NixOS-WSL/how-to/change-username.html)
- [NixOS-WSL 복구 셸](https://nix-community.github.io/NixOS-WSL/troubleshooting/recovery-shell.html)
- [NixOS 안정판 매뉴얼](https://nixos.org/manual/nixos/stable/)
- [Home Manager 매뉴얼](https://nix-community.github.io/home-manager/)
