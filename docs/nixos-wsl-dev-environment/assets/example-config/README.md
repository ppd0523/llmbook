# 이식 가능한 NixOS 개발 환경

이 저장소는 NixOS 호스트 설정과 standalone Home Manager 사용자 프로필을 분리한다.
NixOS-WSL을 대상으로 하며, 같은 사용자 프로필을 native NixOS에도 적용할 수 있다.

## 첫 머신: 설정 저장소 만들기

이 디렉터리는 기존 개인 저장소가 아니라 템플릿이다. 첫 머신에서 README, license,
`.gitignore` 없이 빈 GitHub 저장소를 만들고, 이 디렉터리를 `~/.config/nixos`로 복사한
뒤 초기화한다.

```console
$ sudo nix-channel --update
$ nix-shell -p git openssh
$ cd ~/.config/nixos
$ git init -b main
$ git config --local user.name "<your-name>"
$ git config --local user.email "<your-email>"
$ git remote add origin git@github.com:<github-user>/nixos-config.git
$ git add .
$ nix --extra-experimental-features "nix-command flakes" flake lock
$ git add flake.lock
$ sudo nixos-rebuild build \
    --option experimental-features "nix-command flakes" \
    --flake .#wsl
$ sudo nixos-rebuild switch \
    --option experimental-features "nix-command flakes" \
    --flake .#wsl
$ nix run .#home-manager -- build --flake .#nixos
$ nix run .#home-manager -- switch --flake .#nixos
$ exec zsh
$ git commit -m "Bootstrap NixOS-WSL environment"
$ git push -u origin main
$ exit
```

첫 push 전에 GitHub SSH 인증을 설정하고 시험한다. WSL 설치와 SSH 키 설정을 포함해
처음부터 진행하는 전체 절차는 안내서의 [2장](../../02-install-nixos-wsl.md)에 있다.

처음의 channel 업데이트는 NixOS-WSL이 권장하는 이미지 부트스트랩 단계일 뿐이며,
rebuild 자체는 잠긴 Flake 입력을 사용한다.

## 이후 머신: commit된 저장소 복원

private 저장소라면 clone 명령을 실행하기 전에 새 머신의 SSH 공개 키를 GitHub에
등록한다. SSH 개인 키는 절대 이 저장소에서 복원하지 않는다.

```console
$ sudo nix-channel --update
$ nix-shell -p git openssh
$ git clone <your-repository-url> ~/.config/nixos
$ cd ~/.config/nixos
$ test -f flake.lock
$ sudo nixos-rebuild build \
    --option experimental-features "nix-command flakes" \
    --flake .#wsl
$ sudo nixos-rebuild switch \
    --option experimental-features "nix-command flakes" \
    --flake .#wsl
$ nix run .#home-manager -- build --flake .#nixos
$ nix run .#home-manager -- switch --flake .#nixos
$ exec zsh
$ exit
```

복원 중에는 `nix flake lock`이나 `nix flake update`를 실행하지 않는다. 복원하는
저장소에는 첫 머신에서 commit한 `flake.lock`이 이미 들어 있어야 한다.

부트스트랩은 `sudo nix-channel --update` 뒤에 channel 기반 legacy `nix-shell`을
의도적으로 사용한다. `github:` Flake URL은 GitHub의 인증 없는 REST API 한도를 소진할
수 있고, `git+https:` Flake URL은 초기 이미지에 아직 없는 외부 `git` 실행 파일을
요구한다. 이후 첫 `nix flake lock`이 API rate-limit 오류를 보고하면 한도가 초기화될
때까지 기다리거나 Nix의 `access-tokens` 옵션으로 GitHub 토큰을 전달한다. 그 토큰은
절대 commit하지 않는다.

## LazyVim과 프로젝트 로컬 플러그인

`modules/home/lazyvim.nix`는 Neovim, lazy.nvim, 공유 LazyVim 요구 사항만 설치하고,
lazy.nvim의 신뢰된 프로젝트 로컬 spec 지원을 켠다. 각 애플리케이션 저장소는 언어
extras를 `.lazy.lua`에, 확정된 플러그인 revision을 `.lazy-lock.json`에 직접 둔다.
`:Lazy sync`를 한 번 실행하고 채워진 lock 파일을 commit한다. 언어별 전체 변형은
[프로젝트 개발 셸 예제](../example-dev-shell/README.md)에 있다.

생성되는 `~/.config/nvim/init.lua`는 Home Manager가 소유한다. 따라서 이 설정은
`~/.config/nvim` 디렉터리 전체를 링크하지 않고, Git으로 관리하는 `lua/` 하위 트리,
`stylua.toml`, 쓰기 가능한 기본 `lazy-lock.json`을 각각 링크한다. 상위 디렉터리를
링크하면 `programs.neovim`이 생성하는 `init.lua`와 충돌해 Home Manager 빌드가
`outside $HOME` 오류로 실패한다.

프로젝트 디렉터리는 격리된 플러그인 캐시도 따로 갖는다. 언어 런타임과 LSP 실행
파일은 direnv가 그 프로젝트의 개발 셸을 불러온 뒤 uv, NVM/npm, rustup에서 가져온다.

## 정기 업데이트

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

## Native NixOS

대상 호스트에서 생성된 하드웨어 모듈을 `hosts/native/hardware-configuration.nix`로
복사해 Git에 추가하고, 그 호스트의 원래 `system.stateVersion`을 유지한다. 그러면
flake가 `nixosConfigurations.native`를 노출한다. switch하기 전에 그 호스트의
bootloader, networking, graphics 등 머신 정책도 기존 NixOS 설정에서 옮겨 온다. 이
템플릿의 native 모듈만으로는 완전한 하드웨어 설치 프로필이 되지 않는다.
