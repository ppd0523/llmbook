# 3. 패키지와 프로그램 설정

## 학습 목표

1. `home.packages`와 `programs.*`의 차이를 구분한다.
2. Git, zsh, Starship, direnv를 선언적으로 구성한다.
3. 환경 변수와 `PATH`를 Home Manager로 관리한다.

## 3.1 패키지만 설치할 때

별도 설정이 필요 없는 CLI는 `home.packages`에 둔다.

```nix
{ pkgs, ... }:
{
  home.packages = with pkgs; [
    ripgrep
    fd
    bat
  ];
}
```

적용 후 실행 파일은 사용자 프로필에 나타난다.

```console
$ home-manager build --flake .#nixos
$ home-manager switch --flake .#nixos
$ rg --version
$ fd --version
$ bat --version
```

`home.packages`는 패키지를 설치하지만 프로그램 설정 파일이나 shell hook까지 자동으로
작성하지는 않는다.

## 3.2 프로그램 모듈을 우선할 때

Home Manager에 `programs.<name>` 모듈이 있다면 그 옵션을 먼저 검토한다. 프로그램
모듈은 보통 다음 작업을 함께 수행한다.

- 알맞은 패키지 설치
- 설정 파일 생성
- shell completion이나 hook 연결
- systemd user service가 필요하면 unit 생성

예를 들어 `programs.bat.enable = true;`는 `bat` 패키지를 직접 목록에 넣는 것보다
설정 의도를 분명히 표현한다.

```nix
programs.bat = {
  enable = true;
  config = {
    style = "plain";
    pager = "less -FR";
  };
};
```

같은 패키지를 `home.packages`와 프로그램 모듈 양쪽에 중복 선언할 필요는 없다.

## 3.3 Git 설정

Home Manager 26.05에서는 `programs.git.settings`에 `git-config` 구조를 그대로
표현할 수 있다.

```nix
programs.git = {
  enable = true;
  settings = {
    init.defaultBranch = "main";
    core.editor = "nvim";
    pull.rebase = false;
  };
};
```

적용 결과를 확인한다.

```console
$ git config --global --get init.defaultBranch
main
$ git config --global --get core.editor
nvim
```

사용자 이름과 이메일은 비밀은 아니지만 조직·머신마다 달라질 수 있다. 모든 머신에서
같아야 할 때만 공통 모듈에 넣는다. 업무용과 개인용 identity를 나눠야 한다면
`programs.git.includes` 또는 저장소별 Git 설정을 사용한다. credential, access token,
SSH 개인 키는 평문 Nix 파일에 넣지 않는다.

## 3.4 zsh 설정

기존 예제의 zsh 설정은 completion, history, alias를 함께 관리한다.

```nix
programs.zsh = {
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
```

이 선언은 사용자의 zsh 설정을 관리하지만 로그인 shell 선택은 NixOS 책임이다. 기존
예제는 NixOS 모듈에서 다음을 별도로 선언한다.

```nix
programs.zsh.enable = true;
users.users.${username}.shell = pkgs.zsh;
```

현재 로그인 shell을 확인한다.

```console
$ getent passwd "$USER" | cut -d: -f7
/run/current-system/sw/bin/zsh
```

Home Manager 설정을 적용했는데 현재 shell이 바뀌지 않았다면 `exec zsh`로 새 세션을
시작할 수 있다. 지속적인 로그인 shell 변경은 NixOS 설정에서 해결한다.

## 3.5 Starship과 shell 통합

```nix
programs.starship = {
  enable = true;
  enableZshIntegration = true;
  settings.add_newline = false;
};
```

`enableZshIntegration = true`는 Home Manager가 필요한 초기화 코드를 생성하게 한다.
따라서 수동 `.zshrc`에 `eval "$(starship init zsh)"`를 다시 넣지 않는다. 같은 hook을
두 경로에서 등록하면 중복 실행이나 초기화 순서 문제가 생긴다.

## 3.6 direnv와 nix-direnv

```nix
programs.direnv = {
  enable = true;
  enableZshIntegration = true;
  nix-direnv.enable = true;
};
```

각 옵션의 책임은 다음과 같다.

- `programs.direnv.enable`: direnv 패키지와 사용자 설정
- `enableZshIntegration`: zsh에서 디렉터리 변경 hook 등록
- `nix-direnv.enable`: Nix 개발 환경을 효율적으로 불러오는 구현 연결

프로젝트별 `.envrc`는 Home Manager 저장소가 아니라 해당 프로젝트가 소유한다.

```sh
use flake
```

`.envrc`는 shell 코드를 실행하므로 내용을 검토한 뒤 프로젝트에서 한 번 승인한다.

```console
$ direnv allow
```

## 3.7 하나의 programs 모듈로 합치기

작은 설정은 다음처럼 한 파일에서 시작할 수 있다. 기존 매뉴얼의
[`programs.nix`](../nixos-wsl-dev-environment/assets/example-config/modules/home/programs.nix)도
같은 구조를 사용한다.

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

    direnv = {
      enable = true;
      enableZshIntegration = true;
      nix-direnv.enable = true;
    };
  };
}
```

이 파일을 `modules/home/programs.nix`로 두고 진입 모듈에서 import한다.

## 3.8 환경 변수

로그인 세션에서 사용할 정적 변수는 `home.sessionVariables`에 둔다.

```nix
home.sessionVariables = {
  EDITOR = "nvim";
  VISUAL = "nvim";
};
```

Home Manager 옵션 문서는 session variable의 적용 순서를 보장하지 않는다. 따라서
한 변수가 다른 session variable의 runtime 값에 의존하는 선언은 피한다.

```nix
# 피해야 할 예
home.sessionVariables = {
  TOOL_HOME = "$HOME/.local/share/tool";
  TOOL_CACHE = "$TOOL_HOME/cache";
};
```

같은 값을 Nix에서 조립해야 한다면 `let` binding이나 이미 계산된 Nix 값을 사용한다.

```nix
let
  toolHome = "$HOME/.local/share/tool";
in
{
  home.sessionVariables = {
    TOOL_HOME = toolHome;
    TOOL_CACHE = "${toolHome}/cache";
  };
}
```

프로젝트마다 달라지는 환경 변수와 비밀 토큰은 전역 `home.sessionVariables`에 두지
않는다. 프로젝트의 개발 shell이나 별도 비밀 관리 도구를 사용한다.

## 3.9 사용자 PATH

사용자 실행 파일 디렉터리를 앞에 추가하려면 `home.sessionPath`를 사용한다.

```nix
home.sessionPath = [
  "$HOME/.local/bin"
];
```

`$HOME`은 생성된 shell 코드에서 확장된다. `~`는 같은 방식으로 확장되지 않을 수
있으므로 HOME 기반 경로를 사용한다.

새 session 변수와 PATH는 현재 실행 중인 shell에 자동으로 역주입되지 않는다.
`switch` 뒤 새 로그인 shell을 시작하거나 WSL 세션을 다시 연다.

## 3.10 옵션 찾기

프로그램을 추가하기 전에 공식 옵션 검색에서 다음 순서로 확인한다.

1. `programs.<name>.enable`이 있는가?
2. 필요한 설정을 표현하는 `settings`, `config`, `extraConfig` 옵션이 있는가?
3. 사용 중인 shell의 integration 옵션이 있는가?
4. 전용 모듈로 표현할 수 없는 파일만 dotfiles로 둘 것인가?

[Home Manager 옵션 검색](https://nix-community.github.io/home-manager/options.html)은
옵션의 타입, 기본값, 선언 파일과 예제를 제공한다.

## 요약

- 단순 도구는 `home.packages`, 설정과 통합이 있는 도구는 `programs.*`를 우선한다.
- Home Manager의 zsh 설정과 NixOS의 로그인 shell 설정은 책임이 다르다.
- 자동 생성되는 shell hook을 수동 dotfile에 중복 선언하지 않는다.
- 전역 환경과 프로젝트 환경, 공개 설정과 비밀을 구분한다.

[← 2장](./02-configuration-structure.md) · [목차](./index.md) · [4장: Home Manager 옵션과 dotfiles →](./04-dotfiles.md)
