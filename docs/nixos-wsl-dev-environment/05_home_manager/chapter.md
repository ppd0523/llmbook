# 5. 독립 실행형 Home Manager 구성

## 학습 목표

1. 사용자 패키지와 설정을 시스템에서 독립적으로 적용한다.
2. Home Manager 모듈과 dotfiles를 적절히 나눈다.
3. 고정된 NVM 소스와 쓰기 가능한 Node 설치 영역을 함께 구성한다.
4. direnv와 nix-direnv를 설치해 프로젝트 개발 셸 자동화를 준비한다.
5. LazyVim 공통 기반과 프로젝트별 플러그인 설정의 경계를 나눈다.

## 5.1 사용자 프로필의 진입점

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

이 파일은 짧은 발췌가 아니라 다음 전체 내용으로 구성한다. 따라서 본문의 설명과
복제해 사용하는 예제가 정확히 같은 설정을 가리킨다.

파일: `modules/home/programs.nix` (전체)

```nix
{ ... }:
{
  programs = {
    git = {
      enable = true;
      settings = {
        init.defaultBranch = "main";
        core.editor = "nvim";
        pull.rebase = false;
      };
    };

    bat = {
      enable = true;
      config = {
        style = "plain";
        pager = "less -FR";
      };
    };

    zsh = {
      enable = true;
      enableCompletion = true;
      autosuggestion.enable = true;
      syntaxHighlighting.enable = true;

      history = {
        size = 100000;
        save = 100000;
        share = true;
      };

      shellAliases = {
        cat = "bat";
        grep = "rg";
        ll = "ls -alh";
      };
    };

    starship = {
      enable = true;
      enableZshIntegration = true;
      settings.add_newline = false;
    };

    fzf = {
      enable = true;
      enableZshIntegration = true;
    };

    autojump = {
      enable = true;
      enableZshIntegration = true;
    };

    # Load each project's Nix development shell when entering its directory.
    direnv = {
      enable = true;
      enableZshIntegration = true;
      nix-direnv.enable = true;
    };
  };
}
```

각 선언은 단순히 실행 파일만 설치하는 것이 아니라 사용자 설정과 셸 연결까지 함께
관리한다.

| 선언 | Home Manager가 관리하는 내용 | 사용 시 확인할 점 |
|---|---|---|
| `git` | Git 설치, 기본 브랜치 `main`, Neovim 편집기, merge 방식의 pull 정책 | 개인 이름·이메일과 credential은 머신별 또는 별도 비밀 설정으로 둔다. |
| `bat` | `bat` 설치, 장식 없는 출력, 짧은 출력에서는 종료되는 `less -FR` pager | Nixpkgs의 명령 이름은 Ubuntu의 `batcat`이 아니라 `bat`다. |
| `zsh` | completion, 자동 제안, syntax highlighting, 공유 history, 공통 alias | history 파일은 생성 상태이므로 구성 저장소에 커밋하지 않는다. |
| `starship` | 프롬프트 설치와 zsh 초기화, 프롬프트 앞 빈 줄 제거 | 별도 `eval` 명령을 `.zshrc`에 중복해서 넣지 않는다. |
| `fzf` | fuzzy finder 설치와 zsh 키 바인딩·completion 연결 | Home Manager가 생성한 초기화 코드를 사용한다. |
| `autojump` | 방문 디렉터리 기반 이동 도구와 zsh 연결 | 방문 기록 데이터는 머신별 생성 상태다. |
| `direnv` | direnv 설치, zsh hook, nix-direnv 구현 연결 | `.envrc`는 저장소별로 내용을 검토한 뒤 `direnv allow`한다. |

`enableZshIntegration = true`는 해당 도구의 zsh 초기화 코드를 Home Manager가 생성하게
한다. 따라서 Starship, fzf, Autojump, direnv를 위한 `eval`이나 `source` 명령을 수동
`.zshrc`에 다시 작성하지 않는다. 수동 설정과 생성 설정을 함께 두면 hook이 중복
등록되거나 실행 순서가 달라질 수 있다.

zsh의 `history.size`는 현재 셸이 메모리에 보관하는 항목 수이고 `history.save`는 history
파일에 저장할 항목 수다. `share = true`는 여러 zsh 세션의 history를 공유한다. 반면
`shellAliases`는 선언적 설정이므로 Git으로 복원된다. 예제는 Ubuntu에서 익숙한 사용
흐름을 유지하려고 `cat`을 `bat`, `grep`을 `rg`에 연결한다.

direnv는 디렉터리 진입 시 프로젝트의 `.envrc`를 실행하고, nix-direnv는 그 안의
`use flake`가 만든 개발 환경을 캐시한다. 이 파일은 통합 기능을 켜는 역할만 하며,
프로젝트별 `.envrc`와 `flake.nix`는 각 프로젝트 저장소가 소유한다. 승인 절차와
`devShell` 사용법은 [7장](../07_nix_develop/chapter.md)에서 다룬다.

Neovim과 LazyVim은 책임이 더 크므로 별도
[Home Manager 모듈](../assets/example-config/modules/home/lazyvim.nix)로 분리한다.
이 모듈은 Neovim, Nixpkgs가 고정한 `lazy.nvim`, `fd`, `tree-sitter`와 공통
dotfiles 링크만 제공한다. Python·TypeScript·Rust extra는 사용자 전체에 설치하지
않고 각 프로젝트의 `.lazy.lua`가 선택한다.

## 5.3 dotfiles 배치

Neovim 설정은 Git 저장소의 Lua 원본을 유지하되, `~/.config/nvim` 전체를 한 소유자에게
넘기지 않는다. `programs.neovim.plugins`와 `initLua`를 사용하면 Home Manager가
`~/.config/nvim/init.lua`를 생성한다. 동시에 `xdg.configFile."nvim"`으로 부모 디렉터리
전체를 링크하면 Home Manager가 링크 내부에 `init.lua`를 설치하려고 하므로 다음 오류로
빌드가 중단된다.

```text
Error installing file '.config/nvim/init.lua' outside $HOME
```

예제는 `init.lua`, 사용자 Lua 설정, 쓰기 가능한 lock 파일의 소유권을 분리한다.

파일: `modules/home/lazyvim.nix` (Neovim 설정 배치 부분)

```nix
let
  nvimSource = "${config.home.homeDirectory}/.config/nixos/dotfiles/nvim";
in
{
  programs.neovim = {
    enable = true;
    plugins = [ pkgs.vimPlugins.lazy-nvim ];

    # Home Manager가 ~/.config/nvim/init.lua를 생성한다.
    initLua = builtins.readFile ../../dotfiles/nvim/init.lua;
  };

  xdg.enable = true;
  xdg.configFile = {
    "nvim/lua".source =
      config.lib.file.mkOutOfStoreSymlink "${nvimSource}/lua";
    "nvim/stylua.toml".source =
      config.lib.file.mkOutOfStoreSymlink "${nvimSource}/stylua.toml";
    "nvim/lazy-lock.json".source =
      config.lib.file.mkOutOfStoreSymlink "${nvimSource}/lazy-lock.json";
  };
}
```

`~/.config/nvim`은 이제 심볼릭 링크가 아닌 일반 디렉터리다. 그 안에서 Home Manager는
생성된 `init.lua`를 소유하고, `lua/`, `stylua.toml`, `lazy-lock.json`은 각각 Git 작업
트리로 연결한다. [Neovim `init.lua` 원본](../assets/example-config/dotfiles/nvim/init.lua)을
변경하면 `builtins.readFile` 결과가 달라지므로 Home Manager를 다시 build하고 switch해야
한다. 반면 out-of-store 링크인 `lua/`의 파일과 `stylua.toml` 변경은 작업 트리에 바로
반영된다.

프로젝트 밖에서 LazyVim을 실행하면
[기본 `lazy-lock.json`](../assets/example-config/dotfiles/nvim/lazy-lock.json)에 플러그인
리비전을 쓴다. 파일 단위 out-of-store 링크이므로 LazyVim이 쓸 수 있고 Git으로도
추적된다. `~/.config/nixos`가 이 책에서 정한 clone 위치이므로 저장소를 다른 위치에
둘 경우 `nvimSource`도 함께 바꾼다. 프로젝트 안에서는 해당 프로젝트의
`.lazy-lock.json`과 별도 플러그인 캐시를 사용한다. 프로젝트별 `.lazy.lua`, 신뢰 확인,
LSP 구성은 [7장](../07_nix_develop/chapter.md)에서 실습한다.

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
| `init.lua`를 `$HOME` 밖에 설치한다는 Home Manager build 오류 | `programs.neovim`의 `init.lua`와 `xdg.configFile."nvim"` 부모 링크 충돌 | 부모 링크를 제거하고 예제처럼 `lua/`, `stylua.toml`, `lazy-lock.json`만 연결 |
| LazyVim 기본 lock을 쓸 수 없음 | `lazy-lock.json`이 Nix Store 링크이거나 개별 링크가 누락됨 | 파일 단위 out-of-store 링크와 `nvimSource`의 clone 위치 확인 |

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
