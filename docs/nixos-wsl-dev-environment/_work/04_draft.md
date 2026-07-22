---
title: NixOS-WSL 개발 환경 구축 초고
version: 0.5
status: draft
owner: agent
updated: 2026-07-22
target_reader: 터미널과 언어별 버전 관리에는 익숙하지만 Nix는 처음인 시니어 개발자
topic: Flake와 독립 실행형 Home Manager를 이용한 이식 가능한 NixOS 개발 환경
---

# NixOS-WSL 개발 환경 구축 초고

## 1. 문제 제기

새 PC에서 `git clone` 한 번으로 예전 개발 환경을 복원하려면 무엇을 Git에 넣고 무엇을 런타임 도구에 맡길지 먼저 결정해야 한다. 모든 것을 Nix 패키지로 만들면 재현성은 높지만 기존 `.nvmrc`, `.python-version`, `rust-toolchain.toml` 중심의 프로젝트 흐름과 충돌한다. 반대로 설치 스크립트만 모아 두면 OS와 사용자 설정이 섞이고, 시간이 지난 뒤 같은 결과를 보장하기 어렵다.

이 자료는 다음 경계를 사용한다.

- NixOS는 호스트 차원의 상태를 관리한다.
- Flake는 외부 입력의 버전과 빌드 가능한 출력의 진입점을 정의한다.
- 독립 실행형 Home Manager는 일반 사용자 권한으로 홈 디렉터리의 패키지와 설정을 관리한다.
- dotfiles는 Neovim 같은 애플리케이션이 읽는 설정 데이터이고, Home Manager가 배치한다.
- Nix는 `uv`, `nvm`, `rustup` 도구 자체를 고정한다.
- Python, Node.js, Rust 툴체인 버전은 각 프로젝트 파일이 결정한다.

이 경계의 목적은 모든 바이트를 Nix로 소유하는 것이 아니다. 호스트와 사용자 프로필은 선언적으로 복구하면서도 언어별 프로젝트는 그 생태계의 표준 워크플로를 유지하는 데 있다.

## 2. 직관적 예시

한 저장소를 네 층으로 읽으면 역할이 선명해진다.

```text
flake.nix
├── hosts/wsl/               # WSL이라는 호스트의 NixOS 설정
├── hosts/native/            # 실제 하드웨어에 종속된 NixOS 설정
├── modules/nixos/           # 두 호스트가 공유하는 시스템 정책
├── modules/home/            # 어느 NixOS 호스트에서도 재사용할 사용자 프로필
└── dotfiles/                # 프로그램이 직접 읽는 설정 데이터
```

`nixos-rebuild`는 `nixosConfigurations` 중 하나를 선택해 시스템 세대를 만든다. `home-manager`는 별도의 `homeConfigurations`를 선택해 사용자 프로필 세대를 만든다. 두 명령이 같은 Flake를 읽더라도 수명 주기와 권한은 분리된다.

다음 질문으로 소유자를 고를 수 있다.

1. 부팅, 사용자 계정, 기본 셸, 동적 로더처럼 호스트 전체에 영향을 주는가? NixOS가 소유한다.
2. 사용자 패키지, 셸 설정, 에디터 설정처럼 `$HOME`에서 끝나는가? Home Manager가 소유한다.
3. 외부 저장소의 어느 리비전을 쓸지 정하는가? `flake.lock`이 소유한다.
4. 특정 프로젝트가 요구하는 언어 버전인가? 프로젝트 버전 파일이 소유한다.
5. 프로그램이 직접 읽는 설정 내용인가? dotfiles이고 Home Manager가 목적지에 연결한다.

## 3. 핵심 개념

### 3.1 Nix와 NixOS

Nix는 패키지 관리자이자 빌드 시스템이다. 입력을 명시하고 결과를 `/nix/store`에 불변 경로로 만든다. NixOS는 Nix 모듈로 운영체제 전체 설정을 계산하고, 결과를 부팅 가능한 세대로 만든 Linux 배포판이다.

따라서 `pkgs.ripgrep`은 패키지 선택이고, `programs.zsh.enable = true`나 `users.users.nixos.shell = pkgs.zsh`는 시스템 상태 선언이다. NixOS-WSL도 NixOS 모듈을 사용하지만 커널과 가상화 계층은 Windows WSL이 제공한다.

### 3.2 Flake

Flake는 저장소의 공개 인터페이스다. `inputs`에는 Nixpkgs, Home Manager, NixOS-WSL, NVM 소스가 들어가고 `outputs`에는 `nixosConfigurations.wsl`, `homeConfigurations.nixos`처럼 사용자가 선택할 결과가 들어간다.

`flake.nix`가 의도를 선언한다면 `flake.lock`은 각 입력이 실제로 가리키는 리비전을 기록한다. 복원 재현성은 `flake.lock`을 Git에 커밋했을 때 생긴다. 새 복제본에서 임의로 `nix flake update`를 실행하는 것은 복원이 아니라 업그레이드다.

Flake가 Git 저장소를 입력으로 읽을 때 추적되지 않은 새 파일은 보이지 않을 수 있다. 새 모듈이나 네이티브 호스트의 `hardware-configuration.nix`를 추가했다면 평가 전에 `git add` 해야 한다.

### 3.3 독립 실행형 Home Manager

Home Manager는 Nix 모듈 문법으로 사용자 환경을 선언한다. NixOS 모듈로 통합할 수도 있지만 여기서는 독립 실행형으로 사용한다. 이 선택은 시스템 전환과 사용자 전환을 분리하고, 동일한 `homeConfigurations.nixos`를 NixOS-WSL과 네이티브 NixOS에서 그대로 적용하게 해 준다.

독립 실행형의 비용은 전환 명령이 두 개라는 점이다.

```console
$ sudo nixos-rebuild switch --flake .#wsl
$ home-manager switch --flake .#nixos
```

이 중 첫 번째만 루트 권한이 필요하다. 사용자 설정을 바꿀 때 시스템 전체를 다시 빌드하지 않아도 된다는 장점이 더 크다.

### 3.4 dotfiles

dotfiles는 별도의 배포 도구가 아니라 프로그램 설정의 원본이다. 예제의 `dotfiles/nvim/init.lua`는 Home Manager가 읽어 `~/.config/nvim/init.lua`를 생성하고, `lua/`와 쓰기 가능한 lock 파일은 경로별로 연결한다. 셸 설정처럼 Home Manager 옵션이 충분히 표현력 있는 경우에는 별도 `.zshrc`를 복사하지 않고 `programs.zsh` 모듈을 사용한다.

판단 기준은 다음과 같다.

- Home Manager에 안정적인 전용 옵션이 있으면 모듈을 우선한다.
- 프로그램 고유 언어로 작성된 큰 설정은 `dotfiles/`에 둔다.
- Home Manager가 생성한 파일을 직접 편집하지 않는다. 원본 Nix 모듈이나 dotfile을 고치고 다시 전환한다.

### 3.5 세 가지 버전 관리자

`uv`, `nvm`, `rustup`은 모두 프로젝트별 언어 버전을 다루지만 구현 방식은 다르다.

| 계층 | Python | Node.js | Rust |
|---|---|---|---|
| Nix/Flake가 고정 | `uv` | `nvm` 스크립트 | `rustup` |
| 프로젝트가 고정 | `.python-version` | `.nvmrc` | `rust-toolchain.toml` |
| 의존성 잠금 | `uv.lock` | npm 계열 lockfile | `Cargo.lock` |
| 런타임 저장 위치 | uv 관리 디렉터리 | `$NVM_DIR/versions` | `$RUSTUP_HOME/toolchains` |

NVM은 실행 파일 하나가 아니라 현재 셸의 `PATH`를 바꾸는 셸 함수다. 그래서 Nix Store의 읽기 전용 소스를 통째로 `$NVM_DIR`로 사용하면 Node 버전을 설치할 수 없다. 예제는 고정한 `nvm.sh` 등 세 파일만 연결하고, 부모 디렉터리를 쓰기 가능하게 남긴다.

## 4. 형식화

### 4.1 적용 순서

```text
Windows에 WSL과 NixOS-WSL 등록
  → GitHub에 빈 구성 저장소 생성과 SSH 인증
  → 제공 예제를 로컬 Git 저장소로 초기화
  → 첫 flake.lock 생성
  → WSL 시스템 build
  → WSL 시스템 switch
  → Home Manager 최초 bootstrap/switch
  → 첫 commit과 GitHub push
  → 새 zsh 세션
  → 프로젝트 clone
  → uv sync / 디렉터리 진입 시 nvm / cargo 실행 시 rustup
```

시스템을 먼저 전환하는 이유는 `programs.nix-ld.enable = true`와 zsh 기본 셸을 준비하기 위해서다. NVM, uv, rustup이 내려받는 일반 Linux 바이너리는 전통적인 동적 로더 경로를 기대할 수 있는데 NixOS는 기본적으로 그 경로를 제공하지 않는다. `nix-ld`는 이 혼합형 워크플로를 위한 호환 계층이다.

### 4.2 저장소 구조

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
│   │   ├── nvm.nix
│   │   └── programs.nix
│   └── nixos
│       └── common.nix
└── dotfiles
    └── nvim
        └── init.lua
```

`hardware-configuration.nix`는 네이티브 호스트에만 존재한다. WSL과 공유해서는 안 된다. 반면 `modules/home`은 호스트 종류를 알 필요가 없어야 한다.

### 4.3 상태 버전과 릴리스 버전

`system.stateVersion`과 `home.stateVersion`은 설치 당시의 데이터 형식 호환 기준이다. 패키지를 26.11이나 그 이후로 업데이트한다고 함께 올리는 버전 번호가 아니다. 기존 설치를 저장소에 편입할 때는 원래 값을 보존한다.

Nixpkgs와 Home Manager 릴리스 브랜치는 함께 맞춘다. 예제는 2026년 7월 기준 안정 릴리스인 NixOS 26.05와 Home Manager `release-26.05`를 사용한다.

## 5. Worked Example

### 5.1 Windows에서 WSL과 NixOS-WSL 등록

WSL 자체가 없다면 관리자 PowerShell에서 `wsl --install --no-distribution`으로 기능만 설치하고 Windows를 재시작한다. `wsl --update` 후, WSL 2.4.4 이상에서는 NixOS-WSL 릴리스의 `nixos.wsl` 파일을 내려받아 다음과 같이 등록한다.

```powershell
wsl --version
wsl --install --from-file .\nixos.wsl --name NixOS
wsl -d NixOS
```

구형 WSL에서는 공식 문서의 `wsl --import` 절차를 사용한다. 처음 들어온 뒤 `passwd`로 `nixos` 사용자의 암호를 정한다. 예제는 NixOS-WSL 기본 사용자 이름인 `nixos`를 유지해 첫 전환을 단순화한다.

현재 NixOS-WSL 설치 문서가 안내하는 이미지 초기화 단계로 채널 메타데이터를 한 번 갱신한다.

```console
$ sudo nix-channel --update
```

이 채널은 이어지는 Flake 빌드의 버전을 결정하지 않는다. 새 시스템은 커밋된 `flake.lock`의 입력을 사용하며, 이후 복원과 업데이트 절차도 Flake만 사용한다.

### 5.2 최초 구성 저장소와 잠금 파일 생성

첫 컴퓨터에는 clone할 개인 구성 저장소가 없다. GitHub에서 `nixos-config` 같은 이름의 빈 저장소를 만들되 README, `.gitignore`, license로 초기화하지 않는다. Private 저장소를 기본으로 권장하며 어떤 공개 범위이든 토큰과 SSH 개인 키는 커밋하지 않는다.

초기 이미지에 Git과 OpenSSH를 영구 설치하는 대신 앞에서 갱신한 NixOS 채널로 임시 셸을 연다.

```console
$ nix-shell -p git openssh
```

`github:` Flake fetcher는 비인증 GitHub REST API 한도에 걸릴 수 있다. 이를 피하려고 Git 없는 시점에 `git+https:` fetcher를 사용하면 외부 `git` 실행 파일을 찾지 못한다. 따라서 기존 `nix-shell` 사용은 최종 구성 방식이 아니라 순환 의존을 피하기 위한 bootstrap 예외다. `<nixpkgs>`를 찾지 못하면 `/nix/var/nix/profiles/per-user/root/channels/nixos`를 `-I nixpkgs=...`로 지정한다.

`ssh-keygen -t ed25519`로 키를 만들고 공개 키만 GitHub 계정에 등록한 뒤 `ssh -T git@github.com`으로 확인한다. 제공 예제를 `~/.config/nixos`로 복사하고 로컬 저장소를 초기화한다.

```console
$ cd ~/.config/nixos
$ git init -b main
$ git config --local user.name "<git-user-name>"
$ git config --local user.email "<git-email>"
$ git remote add origin git@github.com:<github-user>/nixos-config.git
$ git add .
```

원본 저장소를 만드는 첫 회에만 잠금 파일을 생성한다. 새 파일은 Flake 평가 전에 Git에 추가한다.

```console
$ nix --extra-experimental-features "nix-command flakes" flake lock
$ git add flake.lock
```

이 단계에서 `API rate limit exceeded`가 계속되면 SSH 키가 아니라 Nix GitHub fetcher 인증 문제다. 한도 초기화를 기다리거나 `--option access-tokens "github.com=$GITHUB_TOKEN"`을 이번 명령에만 전달하고 토큰은 저장소에 넣지 않는다.

시스템과 Home Manager build·switch가 성공한 뒤 `git commit`과 `git push -u origin main`을 실행한다. 두 번째 컴퓨터부터는 커밋된 저장소를 clone하며 `nix flake lock`을 실행하지 않는다.

### 5.3 시스템 빌드와 전환

먼저 결과를 빌드해 평가·빌드 오류를 확인하고, 성공한 결과만 현재 세대로 전환한다.

```console
$ sudo nixos-rebuild build \
    --option experimental-features "nix-command flakes" \
    --flake .#wsl
$ sudo nixos-rebuild switch \
    --option experimental-features "nix-command flakes" \
    --flake .#wsl
```

`build`는 현재 실행 환경을 바꾸지 않는다. `switch`가 성공하면 Flake 지원, zsh 기본 셸, `nix-ld`가 시스템 설정에 반영된다. WSL 세션을 종료했다가 다시 열어 로그인 셸을 확인한다.

### 5.4 Home Manager 최초 적용

아직 `home-manager` 명령이 프로필에 없으므로 고정한 릴리스의 Flake를 한 번 실행한다.

```console
$ cd ~/.config/nixos
$ nix run .#home-manager -- switch --flake .#nixos
```

구성의 `programs.home-manager.enable = true`가 이후 사용할 CLI를 프로필에 넣는다. 다음부터는 짧은 명령을 사용한다.

```console
$ home-manager build --flake .#nixos
$ home-manager switch --flake .#nixos
```

### 5.5 도구 확인

새 zsh 세션에서 다음을 확인한다.

```console
$ echo $SHELL
/run/current-system/sw/bin/zsh
$ git --version
$ tree --version
$ bat --version
$ rg --version
$ nvim --version
$ uv --version
$ type nvm
nvm is a shell function
$ rustup --version
$ starship --version
$ fzf --version
$ autojump --version
```

Ubuntu의 실행 파일 이름 `batcat`과 달리 Nixpkgs 패키지는 `bat`를 제공한다.

### 5.6 프로젝트별 런타임

Python 프로젝트는 `.python-version`, `pyproject.toml`, `uv.lock`을 커밋한다.

```console
$ uv python pin 3.13
$ uv sync
$ uv run python --version
```

Node 프로젝트는 `.nvmrc`와 사용하는 패키지 관리자의 lockfile을 커밋한다.

```console
$ printf '24\n' > .nvmrc
$ cd .. && cd -
Found '.nvmrc' ...
Downloading and installing node v24...
$ node --version
```

예제 zsh 훅은 디렉터리 진입 시 가장 가까운 `.nvmrc`를 찾는다. 버전이 없으면 `nvm install`, 이미 있으면 `nvm use --silent`를 실행하고, `.nvmrc` 영역을 벗어나면 활성 버전을 해제한다.

Rust 프로젝트는 `rust-toolchain.toml`과 `Cargo.lock`을 커밋한다.

```toml
[toolchain]
channel = "1.88.0"
profile = "minimal"
components = ["clippy", "rustfmt"]
```

```console
$ cargo build --locked
```

`RUSTUP_AUTO_INSTALL=1`이므로 프로젝트가 요구한 툴체인이 없을 때 rustup 프록시가 설치할 수 있다. 네트워크 사용을 명시적으로 통제하려면 `RUSTUP_AUTO_INSTALL=0`으로 바꾸고 `rustup toolchain install`을 수동 실행한다.

### 5.7 nix develop, direnv, LazyVim 연결

Home Manager는 `nvim`, lazy.nvim, 최소 LazyVim 기반, uv, NVM, rustup, direnv,
nix-direnv를 제공한다. Python·TypeScript·Rust extra는 전역 설정에서 제외한다.
프로젝트는 `.lazy.lua`와 `.lazy-lock.json`으로 plugin을 선택·고정하고, 네이티브
라이브러리를 `flake.nix`에 선언하며 `.envrc`에서 `use flake`를 호출한다.

```console
$ nix flake lock
$ nix develop
$ command -v <language-runtime> <language-server>
$ nvim .
```

Python devShell은 `.venv/bin`, Node.js devShell은 `node_modules/.bin`을 PATH 앞에
둔다. Rust는 `rust-toolchain.toml`의 `rust-analyzer` component와 rustup proxy를
사용한다. Mason은 공통으로 끄고 각 `.lazy.lua`가 필요한 언어 extra만 켠다.
plugin root도 프로젝트 경로 hash로 분리해 서로 다른 lock 리비전이 충돌하지 않게 한다.

수동 진입이 성공한 뒤 `.envrc`를 읽고 승인한다.

```console
$ exit
$ less .envrc
$ less .lazy.lua
$ direnv allow
$ nvim .
```

`.envrc` 승인은 direnv에, `.lazy.lua` 승인은 Neovim trust DB에 따로 저장된다.
Neovim에서는 `:Lazy sync`, `:LazyHealth`, `:checkhealth vim.lsp`, `:LspInfo`로
확인한다. 생성된 프로젝트 `.lazy-lock.json`을 언어 lock 파일과 함께 커밋한다.

### 5.8 네이티브 NixOS에서 사용자 환경 복원

네이티브 NixOS에서도 사용자 이름과 홈 경로가 `nixos`라면 시스템과 무관하게 다음만으로 같은 사용자 환경을 적용할 수 있다.

```console
$ git clone <repository-url> ~/.config/nixos
$ cd ~/.config/nixos
$ nix run .#home-manager -- switch --flake .#nixos
```

네이티브 시스템 설정도 저장소에서 관리하려면 해당 호스트에서 생성된 하드웨어 모듈을 복사한다.

```console
$ cp /etc/nixos/hardware-configuration.nix \
    ~/.config/nixos/hosts/native/hardware-configuration.nix
$ cd ~/.config/nixos
$ git add hosts/native/hardware-configuration.nix
$ sudo nixos-rebuild build --flake .#native
$ sudo nixos-rebuild switch --flake .#native
```

기존 네이티브 설치에서는 `hosts/native/default.nix`의 `system.stateVersion`을 기존 `/etc/nixos/configuration.nix` 값으로 바꾼다. 부트로더, 파일시스템, 그래픽, 네트워크 같은 호스트 정책은 `hosts/native`에 추가하고 `modules/home`에는 넣지 않는다.

## 6. 직접 해보기

1. GitHub에 빈 저장소를 만들고 예제 구성을 로컬 저장소로 초기화한 뒤 `flake.lock`을 생성해 첫 push를 한다.
2. `modules/home/programs.nix`에 Git 사용자 이름과 이메일을 추가하되 공개 저장소에 넣어도 되는 값인지 판단한다.
3. Neovim 설정 한 줄을 바꾸고 `home-manager build`와 `switch`의 차이를 확인한다.
4. Python, Node, Rust 테스트 프로젝트를 만들고 각 버전 파일을 커밋한 뒤 새 셸에서 자동 선택을 검증한다.
5. 세 프로젝트에서 `nix develop`과 direnv가 같은 LSP 경로를 제공하는지 확인하고 `:LspInfo`와 비교한다.
6. `nix flake update` 전후의 `flake.lock` diff를 읽고, 빌드 성공 뒤에만 커밋한다.

## 7. 흔한 오류

| 오류 | 원인 | 확인 방법 | 해결 방법 |
|---|---|---|---|
| 새 `.nix` 파일을 찾지 못함 | Git Flake가 추적하지 않는 파일 | `git status --short` | `git add` 후 다시 평가 |
| `home-manager: command not found` | 최초 bootstrap 전이거나 CLI 옵션 누락 | `nix profile list` | 공식 릴리스 Flake로 한 번 실행하고 `programs.home-manager.enable` 확인 |
| `nvm: command not found` | 로그인 셸이 zsh가 아니거나 초기화 실패 | `echo $SHELL`, `type nvm` | 시스템 전환 뒤 WSL 재시작, `~/.zshrc` 생성 결과 확인 |
| Node/Python/Rust 바이너리가 실행되지 않음 | 일반 ELF 바이너리가 NixOS 동적 로더를 찾지 못함 | 오류의 interpreter 경로 확인 | `programs.nix-ld.enable = true` 적용, 필요한 라이브러리 추가 |
| Home Manager가 기존 파일과 충돌 | 관리 대상 위치에 수동 파일이 있음 | 오류가 지목한 경로 확인 | 파일을 백업·삭제하고 원본을 모듈/dotfiles로 옮김 |
| `native` 출력이 없음 | 하드웨어 모듈이 없거나 Git에 미추적 | `git ls-files hosts/native` | 생성 파일을 복사하고 `git add` |
| 업데이트 뒤 문제가 생김 | 입력 리비전과 시스템/홈 세대가 함께 변경됨 | `git diff flake.lock`, 세대 목록 | 잠금 파일을 되돌리거나 NixOS/Home Manager 세대 롤백 |

사용자 이름을 `nixos`에서 바꾸는 작업은 별도 마이그레이션이다. NixOS-WSL 공식 문서에 따라 `wsl.defaultUser`와 사용자 선언을 함께 바꾸고, 이 경우 `nixos-rebuild switch`가 아니라 `nixos-rebuild boot`를 사용한 뒤 Windows에서 배포판을 종료하고 다시 시작한다.

## 8. 실제 적용

### 8.1 복원과 업데이트를 구분한다

복원 절차는 커밋된 `flake.lock`을 그대로 사용한다.

```console
$ git clone <repository-url> ~/.config/nixos
$ sudo nixos-rebuild switch --flake ~/.config/nixos#wsl
$ home-manager switch --flake ~/.config/nixos#nixos
```

업데이트는 의도적인 유지보수 작업이다.

```console
$ nix flake update
$ nix fmt
$ sudo nixos-rebuild build --flake .#wsl
$ home-manager build --flake .#nixos
$ sudo nixos-rebuild switch --flake .#wsl
$ home-manager switch --flake .#nixos
$ git add flake.lock
$ git commit -m "Update Nix inputs"
```

### 8.2 롤백 단위를 나눈다

시스템과 홈 프로필이 분리되어 있으므로 실패 범위도 분리된다.

```console
$ sudo nixos-rebuild switch --rollback
$ home-manager generations
$ home-manager switch --rollback
```

프로젝트 런타임 문제는 Nix 세대보다 먼저 프로젝트 파일과 언어별 상태를 확인한다. 예를 들어 `.nvmrc` 변경은 시스템 롤백 대상이 아니다.

### 8.3 비밀은 저장소 밖에 둔다

토큰, SSH 개인 키, `.npmrc` 인증 값은 평문 Nix 파일이나 dotfiles에 커밋하지 않는다. 이 자료는 비밀 관리 체계를 포함하지 않는다. 초기에는 수동 프로비저닝을 사용하고, 필요해지면 sops-nix나 agenix 같은 별도 설계를 도입한다.

## 9. 요약

- NixOS는 호스트, standalone Home Manager는 사용자, dotfiles는 프로그램 설정 데이터를 담당한다.
- Flake는 이들을 한 저장소의 명명된 출력으로 묶고 `flake.lock`이 외부 입력 리비전을 고정한다.
- `uv`, `nvm`, `rustup`만 Nix가 고정하고 언어 툴체인은 프로젝트 파일이 고정한다.
- WSL과 네이티브 NixOS는 사용자 모듈을 공유하지만 하드웨어와 호스트 정책은 공유하지 않는다.
- 복원은 잠금 파일을 유지하는 작업이고 업데이트는 잠금 파일을 의도적으로 바꾸는 작업이다.

## 10. 출처

- [NixOS 26.05 발표](https://nixos.org/blog/announcements/2026/nixos-2605/)
- [Nix Flakes 개념](https://nix.dev/concepts/flakes.html)
- [Nix Flake 명령 참조](https://nix.dev/manual/nix/latest/command-ref/new-cli/nix3-flake.html)
- [Nix와 로컬 파일](https://nix.dev/tutorials/working-with-local-files.html)
- [NixOS-WSL 설치](https://nix-community.github.io/NixOS-WSL/install.html)
- [NixOS-WSL Flake 사용](https://nix-community.github.io/NixOS-WSL/how-to/nix-flakes.html)
- [Home Manager 독립 실행형 설치](https://nix-community.github.io/home-manager/installation/standalone.html)
- [Home Manager 소개](https://nix-community.github.io/home-manager/introduction.html)
- [Nix-ld](https://wiki.nixos.org/wiki/Nix-ld)
- [NVM 공식 저장소](https://github.com/nvm-sh/nvm)
- [uv Python 버전](https://docs.astral.sh/uv/concepts/python-versions/)
- [rustup 툴체인 오버라이드](https://rust-lang.github.io/rustup/overrides.html)

## 11. TODO

- [ ] Nix 구문 및 Home Manager 옵션 정적 검토
- [ ] Windows 호스트에서 가능한 Markdown/링크 검사
- [ ] 초고를 8개 장으로 분할
- [ ] 검토 지적 반영과 최종 배포 기록 작성

## 12. 초고 자가 점검

- [x] 문제, 개념, 예제, 복원, 운영 흐름이 처음부터 끝까지 이어진다.
- [x] Nix를 모르는 독자가 기존 버전 관리자 개념과 연결할 수 있다.
- [x] OS, 사용자, 프로젝트의 소유권 경계를 명시했다.
- [x] 복원과 업데이트를 구분했다.
- [ ] 실제 NixOS 환경에서 평가 및 빌드 검증이 필요하다.
