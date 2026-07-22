# 2. 설치와 첫 실행

## 학습 목표

1. 기존 Neovim 환경을 덮어쓰지 않고 백업한다.
2. 공식 LazyVim Starter를 설치하고 첫 plugin 동기화를 완료한다.
3. 정상 baseline을 health check로 확인한다.
4. 새 환경이 실패했을 때 이전 환경으로 rollback한다.

## 2.1 설치 경로

Linux와 WSL의 Neovim은 기본적으로 다음 XDG 경로를 사용한다.

| 종류 | 기본 경로 | 저장 내용 |
|---|---|---|
| config | `~/.config/nvim` | 사용자가 관리하는 Lua 설정 |
| data | `~/.local/share/nvim` | plugin과 Mason package |
| state | `~/.local/state/nvim` | log와 session state |
| cache | `~/.cache/nvim` | 다시 생성할 수 있는 cache |

정확한 경로는 Neovim 안에서 확인할 수 있다.

```vim
:lua print(vim.fn.stdpath("config"))
:lua print(vim.fn.stdpath("data"))
:lua print(vim.fn.stdpath("state"))
:lua print(vim.fn.stdpath("cache"))
```

WSL에서도 이 경로는 WSL 사용자의 Linux home 아래에 있어야 한다. Windows의
`%LOCALAPPDATA%\nvim`은 Windows native Neovim의 별도 설정이다.

## 2.2 기존 환경 확인

이름을 바꿀 대상과 backup 경로가 이미 존재하는지 먼저 확인한다.

```console
$ ls -ld \
    ~/.config/nvim ~/.config/nvim.bak \
    ~/.local/share/nvim ~/.local/share/nvim.bak \
    ~/.local/state/nvim ~/.local/state/nvim.bak \
    ~/.cache/nvim ~/.cache/nvim.bak
```

`No such file or directory`는 원본이나 backup이 없다는 뜻이므로 해당 항목은 이동하지
않아도 된다. 기존 `.bak`이 있다면 날짜가 붙은 다른 이름을 정한다. 아래 명령으로 기존
backup을 덮어쓰지 않는다.

## 2.3 기존 config와 state 백업

존재하는 경로만 이동한다.

```console
$ mv ~/.config/nvim ~/.config/nvim.bak
$ mv ~/.local/share/nvim ~/.local/share/nvim.bak
$ mv ~/.local/state/nvim ~/.local/state/nvim.bak
$ mv ~/.cache/nvim ~/.cache/nvim.bak
```

Config만이 아니라 data와 state를 함께 분리하는 이유는 이전 plugin checkout과 cache가
새 LazyVim 구성에 섞이지 않게 하기 위해서다. 새 환경이 완전히 정상이라고 확인하기
전에는 backup을 삭제하지 않는다.

## 2.4 공식 Starter 설치

공식 repository를 config 경로에 clone한다.

```console
$ git clone https://github.com/LazyVim/starter ~/.config/nvim
```

Starter의 Git history를 그대로 자신의 설정 history로 쓰지는 않는다. clone 대상이
정확한지 확인한 뒤 template의 `.git` directory만 제거한다.

```console
$ git -C ~/.config/nvim remote -v
origin  https://github.com/LazyVim/starter (fetch)
origin  https://github.com/LazyVim/starter (push)
$ rm -rf ~/.config/nvim/.git
```

이 명령은 `~/.config/nvim/.git`만 제거한다. 상위 directory나 다른 repository를
대상으로 바꾸지 않는다.

## 2.5 첫 실행

```console
$ nvim
```

첫 실행에서 `lua/config/lazy.lua`가 lazy.nvim을 bootstrap하고, lazy.nvim이 LazyVim과
기본 plugin을 내려받는다. Network와 Git 접근이 필요하다. 동기화가 끝날 때까지 기다린
뒤 error notification이 없는지 확인한다.

LazyVim의 기본 `<leader>`는 Space다. Space를 누르면 which-key가 가능한 다음 key를
표시한다. 처음에는 다음 key만 기억하면 충분하다.

| key | 동작 |
|---|---|
| `<leader><space>` | project root에서 file 찾기 |
| `<leader>/` | project root에서 text 검색 |
| `<leader>e` | file explorer 열기 |
| `<leader>l` | Lazy plugin 창 열기 |
| `<leader>cm` | Mason 창 열기 |
| `<leader>cf` | 현재 buffer format |
| `<leader>cl` | 현재 LSP 구성 확인 |

표의 `<leader>cf`는 Space, `c`, `f`를 차례로 누른다는 뜻이다.

## 2.6 정상 baseline 확인

Neovim command line에서 다음 검사를 실행한다.

```vim
:LazyHealth
:checkhealth
:checkhealth mason
```

`:LazyHealth`는 LazyVim plugin을 load하고 관련 상태를 검사한다. `:checkhealth`는
Neovim provider, Treesitter, clipboard 등 전체 health를 보여 준다. `:checkhealth mason`은
download와 압축 해제에 필요한 external command를 검사한다.

모든 optional provider가 `OK`일 필요는 없다. 사용하지 않는 Ruby나 Perl provider의
warning보다 다음 항목을 우선한다.

- Neovim과 lazy.nvim이 error 없이 시작한다.
- Git과 network를 통해 plugin을 내려받았다.
- C compiler와 Treesitter 관련 필수 error가 없다.
- Mason이 Git, curl/wget, unzip, tar, gzip을 찾는다.
- `:Lazy`의 failed plugin 수가 0이다.

## 2.7 Nerd Font와 깨진 icon

Nerd Font는 LazyVim의 필수 요구사항이 아니라 선택 사항이다. 문자 대신 빈 사각형이나
폭이 어긋난 icon이 보이면 Neovim plugin보다 terminal font 설정을 먼저 확인한다.
Font 변경은 운영체제와 terminal emulator마다 다르므로 이 가이드에서는 다루지 않는다.

## 2.8 Rollback

새 config를 보존할 필요가 없다면 먼저 이름을 바꿔 둔다. 그 뒤 이전 backup을 원래
경로로 되돌린다.

```console
$ mv ~/.config/nvim ~/.config/nvim.lazyvim-test
$ mv ~/.local/share/nvim ~/.local/share/nvim.lazyvim-test
$ mv ~/.local/state/nvim ~/.local/state/nvim.lazyvim-test
$ mv ~/.cache/nvim ~/.cache/nvim.lazyvim-test
$ mv ~/.config/nvim.bak ~/.config/nvim
$ mv ~/.local/share/nvim.bak ~/.local/share/nvim
$ mv ~/.local/state/nvim.bak ~/.local/state/nvim
$ mv ~/.cache/nvim.bak ~/.cache/nvim
```

실제로 존재하는 경로만 이동한다. 새 환경을 삭제하지 않고 이름을 바꾸므로 필요한 파일을
나중에 비교할 수 있다.

## 2.9 확인 문제

1. `~/.config/nvim`과 `~/.local/share/nvim`에는 각각 무엇이 저장되는가?
2. 첫 실행 전에 data directory도 백업하는 이유는 무엇인가?
3. `:LazyHealth`가 성공했지만 Python LSP가 없을 수 있는 이유는 무엇인가?

## 요약

- config, data, state, cache는 서로 다른 역할을 하며 모두 rollback 대상이 될 수 있다.
- 공식 Starter를 clone한 뒤 template의 `.git`만 제거한다.
- 첫 실행의 성공 기준은 화면 모양이 아니라 health check와 failed plugin 0개다.
- Optional provider warning과 실제로 사용할 기능의 error를 구분한다.
- Backup은 네 언어 smoke test가 끝날 때까지 보존한다.

## 추가 읽을거리

- [LazyVim 공식 설치 문서](https://www.lazyvim.org/installation)
- [LazyVim 기본 keymap](https://www.lazyvim.org/keymaps)

[← 1장](./01-architecture.md) · [목차](./index.md) · [3장: 공통 설정과 plugin 관리 →](./03-configuration.md)
