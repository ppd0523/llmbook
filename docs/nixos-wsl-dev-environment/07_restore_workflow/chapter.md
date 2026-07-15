# 7. Git clone에서 완전한 환경까지

이 장은 2장에서 원본 구성 저장소를 만들고 `flake.lock`까지 push한 뒤, 두 번째 컴퓨터나 재설치한 환경에 복원하는 절차다. 개인 구성 저장소가 아직 없다면 clone을 시도하지 말고 먼저 [2장의 최초 생성 절차](../02_install_nixos_wsl/chapter.md)를 완료한다.

## 학습 목표

1. 잠긴 구성 저장소를 새 NixOS-WSL에 적용한다.
2. 네이티브 NixOS에서 사용자 프로필만 독립적으로 복원한다.
3. 실제 하드웨어 시스템 설정을 안전하게 저장소에 편입한다.

## 7.1 무엇이 “한 번의 clone으로 복원”되는가

OS 이미지 등록, 초기 암호, 저장소 접근 자격 증명은 Git 바깥의 bootstrap이다. 특히 Private 저장소는 새 컴퓨터의 공개 키를 GitHub에 등록해야 clone할 수 있다. 그 뒤의 선언 상태는 한 저장소 clone에서 복원한다.

```text
bootstrap
  Windows WSL 등록 + 암호 + 저장소 접근

Git 저장소
  시스템 선언 + 사용자 선언 + dotfiles + flake.lock

파생 상태
  /nix/store 결과 + Home Manager 세대 + 언어 런타임/의존성
```

언어 런타임 캐시는 Git에 넣지 않지만 프로젝트 파일을 기준으로 다시 받을 수 있다.

## 7.2 새 NixOS-WSL 전체 복원

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

이 명령은 2.6절과 같은 채널 기반 bootstrap이다. `<nixpkgs>`를 찾지 못하면 2.6절의 root 채널 경로를 명시한다. `github:` Flake 주소로 Git을 가져오면 REST API rate limit에 걸릴 수 있고, `git+https:`는 아직 없는 외부 Git을 요구하므로 이 단계에서는 사용하지 않는다.

Private 저장소라면 2.7절과 같은 방법으로 이 WSL 인스턴스의 SSH 공개 키를 GitHub에 등록하고 `ssh -T git@github.com`을 확인한다. SSH 개인 키는 구성 저장소에서 복원하지 않는다. 인증 준비 후 clone하고, 아래 최초 적용이 끝날 때까지 임시 셸을 유지한다.

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

Home Manager도 먼저 build한 뒤 최초 적용한다.

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

## 7.3 프로젝트 복원

개발 환경과 프로젝트 저장소는 별도다. 각 프로젝트를 clone한 뒤 해당 생태계의 잠금 명령을 사용한다.

```console
# Python
$ git clone <python-project-url>
$ cd python-project
$ uv sync --frozen

# Node.js
$ git clone <node-project-url>
$ cd node-project
$ npm ci

# Rust
$ git clone <rust-project-url>
$ cd rust-project
$ cargo build --locked
```

Node 프로젝트는 디렉터리 진입 시 NVM 훅이 먼저 `.nvmrc`를 처리한다.

## 7.4 네이티브 NixOS에서 사용자 환경만 복원

대상 네이티브 NixOS의 사용자 이름과 예제의 `username`이 같다면 시스템 설정을 건드리지 않고 Home Manager만 적용할 수 있다.

```console
$ git clone <repository-url> ~/.config/nixos
$ cd ~/.config/nixos
$ nix run .#home-manager -- switch --flake .#nixos
```

이 경로는 기존 부트로더, 파일시스템, 네트워크 설정을 그대로 둔다. 사용자 도구와 dotfiles만 필요할 때 가장 안전하다.

사용자 이름이 다르면 `flake.nix`의 `username`과 `home.homeDirectory`가 일치하도록 자신의 저장소에 별도 Home Manager 출력을 추가한다. 여러 사용자를 지원하려면 출력 이름을 `user@host` 형태로 늘릴 수 있다.

## 7.5 네이티브 시스템 설정까지 관리

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

## 7.6 성공 기준

- `nixos-rebuild build --flake .#wsl` 또는 `.#native`가 성공한다.
- `nix run .#home-manager -- build --flake .#nixos`가 성공한다.
- 로그인 셸이 zsh다.
- 지정한 사용자 도구가 PATH에서 발견된다.
- Neovim 설정이 `~/.config/nvim`에 배치된다.
- `.nvmrc`, `.python-version`, `rust-toolchain.toml`이 각각 런타임을 선택한다.
- clone 후 `flake.lock`에 변경이 생기지 않는다.

## 직접 확인

복원 직후 다음을 실행한다.

```console
$ git status --short
$ readlink -f ~/.config/nvim/init.lua
$ home-manager generations
$ sudo nixos-rebuild list-generations
```

단순 복원 뒤 구성 저장소가 깨끗해야 한다. 잠금 파일이나 모듈이 변경되었다면 복원 과정에 업데이트 작업이 섞인 것이다.

## 요약

- bootstrap과 Git으로 복원되는 선언 상태를 구분한다.
- WSL은 시스템 적용 후 Home Manager를 적용한다.
- 네이티브 NixOS에서는 사용자 프로필만 먼저 적용할 수 있다.
- 네이티브 시스템 출력에는 해당 호스트의 하드웨어 모듈과 기존 상태 버전이 필요하다.
- 프로젝트는 언어별 버전 파일과 lockfile에서 다시 만든다.

[← 6장](../06_language_toolchains/chapter.md) · [목차](../index.md) · [8장: 운영과 문제 해결 →](../08_operations_and_troubleshooting/chapter.md)
