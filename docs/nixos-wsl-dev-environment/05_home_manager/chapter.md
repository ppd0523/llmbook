# 5. 독립 실행형 Home Manager 구성

## 학습 목표

1. 사용자 패키지와 설정을 시스템에서 독립적으로 적용한다.
2. Home Manager 모듈과 dotfiles를 적절히 나눈다.
3. 고정된 NVM 소스와 쓰기 가능한 Node 설치 영역을 함께 구성한다.
4. direnv와 nix-direnv를 설치해 프로젝트 개발 셸 자동화를 준비한다.
5. LazyVim 공통 기반과 프로젝트별 플러그인 설정의 경계를 나눈다.

## 5.1 사용자 프로필의 진입점

[예제 `modules/home/default.nix`](../assets/example-config/modules/home/default.nix)는 사용자 환경의 공통 진입점이다.

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

`uv`와 `rustup`은 Nixpkgs의 잠긴 리비전에서 설치된다. Python, `rustc`, Cargo는 직접
패키지 목록에 넣지 않는다. `gcc`와 `pkg-config`는 프로젝트가 네이티브 확장을 빌드할
때 필요한 일반 지원 도구다.

`programs.home-manager.enable = true`는 최초 bootstrap 이후 `home-manager` CLI 자체를 관리되는 사용자 프로필에 유지한다.

## 5.2 프로그램 전용 모듈 사용

[예제 `programs.nix`](../assets/example-config/modules/home/programs.nix)는 다음 프로그램을 선언한다.

- Git
- bat
- zsh
- Starship
- fzf
- Autojump
- direnv와 nix-direnv

대표적인 형태는 다음과 같다.

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

direnv도 같은 방식으로 zsh 훅과 nix-direnv 연동을 선언한다. 실제 프로젝트의 `.envrc` 승인과 `devShell` 사용법은 [7장](../07_nix_develop/chapter.md)에서 다룬다.

Nixpkgs의 bat 실행 파일 이름은 Ubuntu의 `batcat`이 아니라 `bat`다. 예제는 익숙한 `cat` 사용을 위해 `cat = "bat"` 별칭을 추가한다.

Neovim과 LazyVim은 책임이 더 크므로 별도
[Home Manager 모듈](../assets/example-config/modules/home/lazyvim.nix)로 분리한다.
이 모듈은 Neovim, Nixpkgs가 고정한 `lazy.nvim`, `fd`, `tree-sitter`와 공통
dotfiles 링크만 제공한다. Python·TypeScript·Rust extra는 사용자 전체에 설치하지
않고 각 프로젝트의 `.lazy.lua`가 선택한다.

## 5.3 dotfiles 배치

Neovim 설정은 Lua 원본을 유지한다. 프로젝트 밖에서 사용하는 LazyVim 공통 구성은
플러그인 버전을 `lazy-lock.json`에 기록하므로 `~/.config/nvim`이 쓸 수 있는
디렉터리여야 한다.
따라서 일반적인 Nix Store 링크 대신 저장소를 가리키는 out-of-store 링크를 사용한다.

```nix
xdg.enable = true;
xdg.configFile."nvim".source = config.lib.file.mkOutOfStoreSymlink
  "${config.home.homeDirectory}/.config/nixos/dotfiles/nvim";
```

이 선언은 저장소의 [Neovim 설정](../assets/example-config/dotfiles/nvim/init.lua)을
`~/.config/nvim`에 연결한다. `~/.config/nixos`가 이 책에서 정한 clone 위치이므로,
저장소를 다른 위치에 둘 경우 문자열도 함께 바꿔야 한다. 링크 자체는 Home Manager가
관리하지만 링크 대상은 Git 작업 트리다. 따라서 Neovim 설정은
`~/.config/nvim`이 아니라 `~/.config/nixos/dotfiles/nvim`의 Git 변경으로 검토하고
커밋한다.

큰 Neovim 구성을 여러 파일로 나눠도 `dotfiles/nvim/` 디렉터리 전체를 그대로 관리할 수
있다. 프로젝트 밖에서 LazyVim을 실행해 생성한 기본 `lazy-lock.json`은 구성 저장소에
커밋한다. 프로젝트 안에서는 그 프로젝트의 `.lazy-lock.json`과 별도 플러그인 캐시를
사용한다. 프로젝트별 `.lazy.lua`, 신뢰 확인, LSP 구성은
[7장](../07_nix_develop/chapter.md)에서 실습한다.

## 5.4 NVM은 일반 패키지와 다르다

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

## 5.5 `.nvmrc` 자동 설치와 전환

zsh 초기화에서 NVM을 source한 뒤 `chpwd` 훅을 등록한다. 알고리즘은 다음과 같다.

```text
셸 시작 또는 디렉터리 변경
  → 상위 방향으로 가장 가까운 .nvmrc 탐색
  → 요청 버전이 미설치면 nvm install
  → 설치되어 있고 현재 버전과 다르면 nvm use
  → .nvmrc 영역을 벗어나면 nvm deactivate
```

핵심 코드는 다음과 같다.

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

## 5.6 최초 적용

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
$ direnv version
```

## 흔한 오류

| 증상 | 원인 | 해결 |
|---|---|---|
| 기존 `.zshrc` 또는 Neovim 디렉터리 충돌 | Home Manager가 관리할 위치에 수동 파일 존재 | 기존 파일을 백업하고 원본을 모듈/dotfiles로 이동 |
| `nvm`이 명령이 아님 | zsh 초기화가 적용되지 않음 | `echo $SHELL`, 생성된 `.zshrc`, 새 로그인 세션 확인 |
| NVM이 Node를 설치하지 못함 | `$NVM_DIR` 전체가 읽기 전용 링크 | 개별 스크립트만 링크하고 부모 디렉터리를 쓰기 가능하게 유지 |
| `home-manager` 명령이 없음 | 최초 bootstrap 전 | `nix run ...release-26.05 -- switch ...` 실행 |
| LazyVim 기본 lock을 쓸 수 없음 | Neovim 디렉터리가 Nix Store 링크 | `lazyvim.nix`의 out-of-store 링크와 고정 clone 위치 확인 |

## 요약

- standalone Home Manager는 시스템과 별도로 사용자 프로필을 전환한다.
- 전용 모듈은 설치와 셸 통합을 함께 처리한다.
- 큰 애플리케이션 설정은 dotfiles 원본을 Home Manager가 배치한다.
- NVM 스크립트는 고정하되 Node 설치 디렉터리는 쓰기 가능해야 한다.
- direnv와 nix-direnv는 프로젝트별 Nix 개발 환경을 자동으로 불러온다.
- LazyVim 공통 기반은 Home Manager, 언어별 extra와 plugin lock은 프로젝트가 관리한다.
- 최초 bootstrap 뒤에는 Home Manager가 자신의 CLI도 관리한다.

## 추가 읽을거리

- [Home Manager standalone 설치](https://nix-community.github.io/home-manager/installation/standalone.html)
- [Home Manager 옵션](https://nix-community.github.io/home-manager/options.html)
- [NVM 공식 저장소](https://github.com/nvm-sh/nvm)
- [LazyVim 설치와 구성 구조](https://www.lazyvim.org/installation)
- [lazy.nvim configuration](https://lazy.folke.io/configuration)

[← 4장](../04_system_configuration/chapter.md) · [목차](../index.md) · [6장: 언어별 툴체인 →](../06_language_toolchains/chapter.md)
