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

**사용자 프로필**은 한 사용자의 `PATH`에 들어가는 Nix 패키지 묶음이다. standalone
Home Manager는 `switch`할 때 `home.packages`를 이 프로필에 넣으며, 실행 파일은 보통
`~/.nix-profile/bin` 아래에 보인다(Nix 설정에 따라 `~/.local/state/nix/profile/bin`).

```console
$ home-manager build --flake .#nixos
$ home-manager switch --flake .#nixos
$ command -v rg
/home/nixos/.nix-profile/bin/rg
$ fd --version
$ bat --version
```

`build`가 성공하면 현재 디렉터리에 build 결과를 가리키는 `result` 링크가 생기고,
`switch` 전에도 `result/home-path/bin`에서 새로 들어갈 실행 파일을 볼 수 있다. 자세한
구조는 5.2절에서 다룬다.

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

Home Manager는 Git 설정을 `~/.config/git/config`에 만든다. 홈에 예전 `~/.gitconfig`가
남아 있으면 Git은 두 파일을 모두 읽고 `~/.gitconfig`의 값을 나중에 적용하므로, 충돌 오류
없이 Home Manager 설정이 가려질 수 있다. 위 확인 명령의 값이 다르게 나오면
`git config --global --show-origin --get core.editor`로 값이 어느 파일에서 왔는지 본다.

## 3.4 zsh 설정

예제 구성의 zsh 설정은 completion, history, alias를 함께 관리한다.

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

이 선언은 사용자의 zsh 설정을 관리하지만 로그인 shell 선택은 NixOS 책임이다. 예제
구성은 NixOS 모듈 `modules/nixos/common.nix`에서 다음을 별도로 선언한다.

```nix
programs.zsh.enable = true;
users.users.${username}.shell = pkgs.zsh;
```

현재 로그인 shell을 확인한다.

```console
$ getent passwd "$USER" | cut -d: -f7
/run/current-system/sw/bin/zsh
```

**로그인 shell**은 터미널을 새로 열 때 계정 정보에 따라 처음 실행되는 shell이다. 위
결과가 bash처럼 zsh가 아닌 shell이면 Home Manager의 zsh 설정은 터미널을 열어도 쓰이지
않는다. 그때는 Home Manager가 아니라 NixOS 설정을 고친다. 로그인 shell은 zsh인데 설정
변경만 반영되지 않았다면 3.10절을 본다.

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

작은 설정은 다음처럼 한 파일에서 시작할 수 있다. 예제 구성의
[`programs.nix`](../nixos-wsl-dev-environment/assets/example-config/modules/home/programs.nix)는
같은 구조에 zsh history, fzf, autojump 설정을 더한 것이다.

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

다른 변수의 값이 필요하면 shell이 아니라 Nix 평가 단계에서 문자열을 조립한다. 공식
옵션 설명이 권하는 방법은 모듈 인자 `config`로 이미 선언한 값을 읽는 것이다.

```nix
{ config, ... }:
{
  home.sessionVariables = {
    TOOL_HOME = "$HOME/.local/share/tool";
    TOOL_CACHE = "${config.home.sessionVariables.TOOL_HOME}/cache";
  };
}
```

Nix의 `${...}`는 평가할 때 치환되므로 Home Manager가 생성하는 shell 스크립트(3.10절)에는
완성된 문자열이 들어간다. `$HOME`은 Nix 문자열 보간이 아니므로 그대로 남아 shell이
확장한다.

```sh
export TOOL_CACHE="$HOME/.local/share/tool/cache"
export TOOL_HOME="$HOME/.local/share/tool"
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
있으므로 HOME 기반 경로를 사용한다. `home.sessionPath`에 넣은 경로는 `PATH` 앞에
추가된다. 시스템 패키지와 같은 이름의 실행 파일을 넣는다면, 어떤 실행 파일이 먼저
선택되는지 `command -v <명령>`으로 확인한다.

## 3.10 새 설정이 보이는 시점

zsh는 시작할 때 두 종류의 설정 파일을 읽는다. `.zshenv`는 모든 zsh가 먼저 읽고,
`.zshrc`는 터미널처럼 사람이 입력하는 shell이 이어서 읽는다. 예제 구성에서는 1.5절의
`stateVersion` 규칙에 따라 두 파일이 `~/.config/zsh` 아래에 생기고, 홈의 `~/.zshenv`는
`~/.config/zsh/.zshenv`를 불러오는 한 줄만 가진다.

| 파일 | 담는 것 |
|---|---|
| `~/.config/zsh/.zshenv` | session 변수와 `PATH`(아래 스크립트를 불러옴) |
| `~/.config/zsh/.zshrc` | alias, completion, 프롬프트, fzf·direnv 같은 shell hook |

Home Manager는 `home.sessionVariables`와 `home.sessionPath`를 `hm-session-vars.sh`라는
스크립트로 만들고, `.zshenv`가 이 스크립트를 불러온다. 이 스크립트는 첫 줄에서 한 세션에
한 번만 실행되도록 막는다.

```sh
# Only source this once.
if [ -n "${__HM_SESS_VARS_SOURCED-}" ]; then return; fi
export __HM_SESS_VARS_SOURCED=1
```

`__HM_SESS_VARS_SOURCED`는 환경 변수라서 자식 프로세스로 상속된다. 그래서 같은
터미널에서 `exec zsh`로 shell만 바꾸면 alias나 프롬프트처럼 `.zshrc`가 정하는 설정은
새로 읽지만, 새로 추가한 session 변수와 `PATH`는 보이지 않는다.

| 바꾼 것 | 확인하는 방법 | 이유 |
|---|---|---|
| alias, completion, 프롬프트, shell hook | 같은 터미널에서 `exec zsh` | 새 zsh가 `.zshrc`를 다시 읽는다 |
| `home.sessionVariables`, `home.sessionPath` | 새 터미널 탭에서 WSL을 연다 | 새 탭은 기존 shell의 환경 변수를 물려받지 않으므로 가드 변수도 없다 |
| NixOS 변경을 포함한 로그인 환경 전체 | PowerShell에서 `wsl --terminate NixOS` 뒤 다시 연다 | 배포판 안의 모든 프로세스와 user service가 끝나고 처음부터 다시 시작한다 |

새 탭을 열 수 없을 때는 `unset __HM_SESS_VARS_SOURCED && exec zsh`로 스크립트를 다시
실행하게 할 수 있다. 이 방법은 `PATH` 앞에 같은 디렉터리를 한 번 더 붙이므로 확인용으로만
쓴다.

## 3.11 옵션 찾기

프로그램을 추가하기 전에 공식 옵션 검색에서 다음 순서로 확인한다.

1. `programs.<name>.enable`이 있는가?
2. 필요한 설정을 표현하는 `settings`, `config`, `extraConfig` 옵션이 있는가?
3. 사용 중인 shell의 integration 옵션이 있는가?
4. 전용 모듈로 표현할 수 없는 파일만 dotfiles로 둘 것인가?

[Home Manager 옵션 검색](https://nix-community.github.io/home-manager/options.html)은
옵션의 타입, 기본값, 선언 파일과 예제를 제공한다.

## 실습 과제

예제 구성의 `~/.config/nixos`에서 진행한다. 각 과제는 파일 수정 → `home-manager build
--flake .#nixos` → `home-manager switch --flake .#nixos` → 확인 순서로 한다. 과제를
마친 뒤 남기고 싶지 않은 변경은 `git restore`로 되돌리고 다시 `switch`한다.

1. `modules/home/default.nix`의 `home.packages`에 `jq`를 추가한다. `switch` 전에
   `ls result/home-path/bin/jq`로 build 결과에 실행 파일이 들어 있는지 먼저 확인하고,
   `switch` 뒤 `command -v jq`로 사용자 프로필에서 찾아지는지 확인한다.
2. `home.sessionVariables`에 `HM_PRACTICE = "hello";`를 추가한다. `switch`한
   터미널에서 `exec zsh` 뒤 `printenv HM_PRACTICE`를 실행하고, 새 터미널 탭에서 다시
   실행해 두 결과를 비교한다.
3. 업무용 저장소에서만 다른 Git 설정을 쓰도록 `programs.git.includes`에
   `{ path = "~/.config/git/work"; condition = "gitdir:~/work/"; }`를 추가하고,
   `git config --global --get-regexp '^includeif\.'`로 조건부 include가 생겼는지
   확인한다. 이 `~`는 shell이 아니라 Git이 직접 홈 디렉터리로 바꾸므로 3.9절의 규칙과
   충돌하지 않는다. include 대상 파일이 아직 없으면 Git은 그 include를 건너뛴다.
4. 예제 구성의 `programs.nix`에서 fzf가 zsh에 연결되어 있는지 생성된
   `~/.config/zsh/.zshrc`로 확인한다. 그다음 zsh 초기화 코드에 `source <(fzf --zsh)`를 손으로 한 번 더 넣으면
   안 되는 이유를 3.5절의 원칙으로 설명한다.

??? note "기대 결과 확인"
    1번: `ls result/home-path/bin/jq`가 `result/home-path/bin/jq`를 출력한다. 아직
    `switch` 전이므로 `command -v jq`는 아무것도 출력하지 않을 수 있다. `switch` 뒤에는
    `/home/nixos/.nix-profile/bin/jq`처럼 사용자 프로필 아래 경로가 나온다. 사용자 프로필
    위치는 Nix 설정에 따라 `~/.local/state/nix/profile`일 수도 있다.

    2번: `switch`한 터미널에서는 `exec zsh` 뒤에도 빈 줄이 나오고, 새 탭에서는
    `hello`가 나온다. 같은 터미널에서는 `__HM_SESS_VARS_SOURCED`가 상속되어
    `hm-session-vars.sh`가 다시 실행되지 않기 때문이다(3.10절). `PAGER`처럼 NixOS가 이미
    기본값(`less`)을 정하는 변수로 같은 실험을 하면 기존 터미널에서 옛 값이 보여 차이를
    구분하기 어렵다.

    3번: 다음 명령이 조건부 include 한 줄을 출력한다.

    ```console
    $ git config --global --get-regexp '^includeif\.'
    includeif.gitdir:~/work/.path ~/.config/git/work
    ```

    4번: `grep fzf ~/.config/zsh/.zshrc`가 `source <(/nix/store/...-fzf-.../bin/fzf --zsh)`
    같은 줄을 보여 준다. `~/.zshrc`는 없으므로 그 경로로 찾으면 파일이 없다는 오류가
    난다. `enableZshIntegration = true`가 이미 hook을 만들었으므로 손으로 한 번 더 넣으면
    같은 초기화가 두 번 실행된다.

## 요약

- 단순 도구는 `home.packages`, 설정과 통합이 있는 도구는 `programs.*`를 우선한다.
- Home Manager의 zsh 설정과 NixOS의 로그인 shell 설정은 책임이 다르다.
- 자동 생성되는 shell hook을 수동 dotfile에 중복 선언하지 않는다.
- 새 session 변수와 `PATH`는 같은 터미널의 `exec zsh`가 아니라 새 터미널 세션에서
  확인한다.
- 전역 환경과 프로젝트 환경, 공개 설정과 비밀을 구분한다.

[← 2장](./02-configuration-structure.md) · [목차](./index.md) · [4장: Home Manager 옵션과 dotfiles →](./04-dotfiles.md)
