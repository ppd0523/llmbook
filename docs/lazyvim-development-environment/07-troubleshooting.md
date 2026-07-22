# 7. 운영과 문제 해결

## 학습 목표

1. Update와 restore가 바꾸는 범위를 구분한다.
2. 같은 진단 순서로 LSP, formatter, DAP 문제를 좁힌다.
3. WSL에서만 발생하는 path, file system, clipboard 문제를 식별한다.
4. 전체 data 삭제 전에 더 작은 복구 단위를 선택한다.

## 7.1 정상 상태를 먼저 기록한다

문제가 생긴 뒤 처음으로 상태를 보면 무엇이 달라졌는지 알기 어렵다. 네 언어 smoke test가
성공한 시점에 다음 정보를 기록한다.

```console
$ nvim --version | head -n 1
$ git -C ~/.config/nvim rev-parse HEAD
$ git -C ~/.config/nvim status --short
```

Neovim 안에서는 `:Lazy`의 plugin 상태와 `:Mason`의 package 목록을 확인한다.
`lazy-lock.json`과 config를 commit해 알려진 정상 상태를 만든다.

## 7.2 Plugin update와 restore

Plugin을 update하려면 다음 command를 사용한다.

```vim
:Lazy update
```

Update 후 `lazy-lock.json`이 바뀐다. 바로 commit하지 말고 JavaScript/TypeScript, Python,
Rust smoke test를 다시 수행한다. 문제가 없다면 diff와 함께 commit한다.

```console
$ cd ~/.config/nvim
$ git diff -- lazy-lock.json
$ git add lazy-lock.json
$ git commit -m "Update Neovim plugins"
```

Lockfile revision으로 plugin을 되돌릴 때는 다음 command를 사용한다.

```vim
:Lazy restore
```

먼저 Git에서 원하는 `lazy-lock.json` revision을 복원한 뒤 `:Lazy restore`를 실행한다.
이 command는 Mason package, language runtime, project dependency를 되돌리지 않는다.

## 7.3 Mason update의 범위

```vim
:MasonUpdate
:Mason
```

`MasonUpdate`는 package registry 정보를 갱신한다. 실제 package 상태와 update 가능 여부는
Mason UI에서 확인한다. Mason package update는 `lazy-lock.json`에 기록되지 않으므로
plugin update와 같은 rollback 단위를 갖지 않는다.

팀에서 exact external tool version이 필요하면 Mason의 mutable 설치만으로 충분하지 않다.
Project tool manager, container, system package manifest, Nix 등의 별도 version policy를
사용한다.

## 7.4 고정된 진단 순서

증상이 무엇이든 다음 순서를 유지한다.

```text
1. Neovim과 OS prerequisite
2. LazyVim plugin과 extra
3. Mason package와 external executable
4. Filetype와 project root
5. Project runtime과 config
6. LSP, formatter 또는 DAP session
```

앞 단계가 실패하면 뒤 단계의 설정을 바꾸지 않는다. 예를 들어 `ruff` executable이
없는데 Python LSP option부터 수정하면 원인과 변경 사항이 동시에 늘어난다.

## 7.5 계층별 command

| 계층 | command | 확인하는 것 |
|---|---|---|
| 편집기 | `nvim --version` | LazyVim 최소 version과 LuaJIT build |
| 전체 health | `:checkhealth` | provider, Treesitter, clipboard 등 |
| LazyVim | `:LazyHealth` | LazyVim과 관련 plugin health |
| Plugin | `:Lazy` | 설치, load, error, revision |
| Extra | `:LazyExtras` | 활성화한 기능 묶음 |
| Mason health | `:checkhealth mason` | downloader와 archive utility |
| Mason package | `:Mason` | external tool 설치 상태 |
| Mason log | `:MasonLog` | download와 install error |
| Filetype | `:set filetype?` | buffer가 예상 언어로 감지되었는지 |
| LSP | `:LspInfo` 또는 `<leader>cl` | active client, root, command |
| Formatter | `:ConformInfo` | 선택된 formatter와 availability |
| Message | `:messages` | 최근 Lua, LSP, DAP error |
| Rust | `:checkhealth rustaceanvim` | Cargo, rust-analyzer, parser, conflict |

## 7.6 LSP가 동작하지 않을 때

`gd`, `K`, rename이 동작하지 않으면 다음 질문에 순서대로 답한다.

1. `:set filetype?`가 기대한 언어인가?
2. `:Lazy`에서 language extra의 plugin이 설치되고 load 가능한가?
3. `:Mason` 또는 rustup에서 language server가 설치되었는가?
4. `vim.fn.exepath()`가 server executable 경로를 반환하는가?
5. `:LspInfo`에 client가 있고 현재 buffer에 attach되었는가?
6. Client가 선택한 root가 `package.json`, `pyproject.toml`, `Cargo.toml`이 있는 project인가?
7. Project manifest와 dependency restore가 정상인가?

대표 executable 확인 예시는 다음과 같다.

```vim
:lua print(vim.fn.exepath("vtsls"))
:lua print(vim.fn.exepath("pyright-langserver"))
:lua print(vim.fn.exepath("ruff"))
:lua print(vim.fn.exepath("rust-analyzer"))
```

Rust는 Mason보다 rustup component와 shell PATH를 먼저 확인한다.

## 7.7 Formatting이 동작하지 않을 때

`<leader>cf`와 저장 시 format을 분리해서 확인한다.

1. `<leader>cf` 수동 format은 동작하는가?
2. `:ConformInfo`에 선택된 formatter가 available한가?
3. Prettier project에 config file이 있는가?
4. Python project에서 `ruff_format`이 보이는가?
5. Rust는 rustfmt와 LSP formatting이 가능한가?
6. `<leader>uF` 또는 `<leader>uf`로 autoformat을 꺼 두지 않았는가?
7. 같은 filetype에 여러 formatter가 순차 실행되지 않는가?

수동 format은 되지만 저장 시에만 안 되면 external executable보다 autoformat toggle과
buffer-local option을 먼저 본다.

Format 결과가 저장할 때마다 앞뒤로 바뀌면 owner가 둘 이상일 가능성이 높다. 이
가이드의 JS/TS policy는 ESLint auto-format을 끄고 Prettier 하나만 문서 formatter로
사용한다.

## 7.8 Debugging이 동작하지 않을 때

DAP 문제는 client, adapter, configuration, program의 네 단계로 나눈다.

1. `<leader>db`가 breakpoint를 표시하는가?
2. `:Mason`에 해당 adapter가 설치되었는가?
3. `vim.fn.exepath()`가 adapter executable을 찾는가?
4. `<leader>dc` 또는 Rust `<leader>dr`에 실행할 configuration이 있는가?
5. Program runtime과 build가 debugger 없이도 성공하는가?
6. Project path와 source map이 실제 file을 가리키는가?
7. `:messages`에 adapter process error가 있는가?

| 언어 | adapter 확인 | project 확인 |
|---|---|---|
| JS·TS | `js-debug-adapter` | Node.js, `tsx`/`ts-node`, source map |
| Python | `debugpy-adapter` | `.venv` interpreter와 import |
| Rust | `codelldb` | `cargo build`, selected Cargo target |

DAP UI만 열리고 program이 실행되지 않으면 UI layout을 수정하지 않는다. Adapter와
configuration부터 확인한다.

## 7.9 WSL에서만 생길 수 있는 문제

### Windows와 Linux binary 혼용

```console
$ command -v nvim git node npm python3 cargo
$ file "$(command -v nvim)"
```

Windows `.exe`와 Linux Mason package를 한 Neovim process에서 섞지 않는다. WSL에서는
config, data, project runtime을 모두 WSL Linux 환경에 둔다.

### `/mnt/c` project 성능

Microsoft는 Linux command line 도구로 작업할 때 WSL Linux file system에 file을 두는
것을 권장한다. Search, file watcher, node_modules, Cargo build가 느리면 project를
`/home/<user>/projects` 아래에 두고 비교한다.

### Clipboard

System clipboard가 동작하지 않으면 전체 health check를 실행하고 결과의 clipboard
section을 찾는다.

```vim
:checkhealth
```

Neovim은 terminal이 지원하면 OSC 52 provider를 자동 감지할 수 있다. WSL에서는
`clip.exe`와 PowerShell을 사용하는 provider도 공식 도움말에 제시되어 있다. Clipboard
문제는 LazyVim language plugin과 무관하므로 LSP나 Mason 설정을 바꾸지 않는다.

## 7.10 Linux distribution 특이 문제

- 오래된 glibc에서는 Mason이 받은 CodeLLDB binary가 시작되지 않을 수 있다.
- Wayland와 X11은 사용할 수 있는 clipboard command가 다르다.
- 매우 오래된 distribution repository는 LazyVim 최소 Neovim version보다 낮을 수 있다.
- Corporate proxy나 custom certificate가 GitHub download를 막으면 plugin과 Mason install이 모두 실패할 수 있다.

이 문제는 특정 plugin option으로 우회하기 전에 process error와 health output으로 먼저
확인한다. 운영체제 package 교체와 보안 정책 변경은 해당 환경의 공식 지침을 따른다.

## 7.11 작은 단위부터 복구하기

다음 순서로 복구 범위를 넓힌다.

1. Buffer를 다시 열거나 Neovim을 project root에서 재시작한다.
2. 문제 package 하나를 Mason UI에서 재설치한다.
3. Git에서 이전 config/lockfile을 가져와 `:Lazy restore`한다.
4. Plugin cache만 별도 이름으로 이동해 다시 동기화한다.
5. 마지막 수단으로 data, state, cache 전체를 별도 이름으로 이동해 clean bootstrap한다.

전체 reset이 필요해도 즉시 삭제하지 않고 이름을 바꿔 보존한다.

```console
$ mv ~/.local/share/nvim ~/.local/share/nvim.reset-backup
$ mv ~/.local/state/nvim ~/.local/state/nvim.reset-backup
$ mv ~/.cache/nvim ~/.cache/nvim.reset-backup
$ nvim
```

`reset-backup` 경로가 이미 있다면 다른 고유한 이름을 사용한다. Config인
`~/.config/nvim`은 그대로 두므로 lazy.nvim이 lockfile과 spec을 기준으로 data를 다시
만든다. 원인을 찾은 뒤에만 backup 정리 여부를 결정한다.

## 7.12 최종 점검표

### 공통

- [ ] Neovim이 0.11.2 이상이며 LuaJIT build다.
- [ ] `:LazyHealth`와 필요한 `:checkhealth` 항목에 필수 error가 없다.
- [ ] Mason package 8개가 설치되었다.
- [ ] `lazy-lock.json`과 Lua config가 Git에 commit되었다.

### JavaScript·TypeScript

- [ ] vtsls가 JS와 TS buffer에 attach된다.
- [ ] ESLint diagnostic과 code action이 project config를 읽는다.
- [ ] Prettier가 project config가 있을 때 format한다.
- [ ] JavaScript와 TypeScript breakpoint에서 정지한다.

### Python

- [ ] Pyright와 Ruff가 attach된다.
- [ ] Project `.venv`가 선택된다.
- [ ] `ruff_format`이 source를 format한다.
- [ ] Debug 대상이 project interpreter로 실행된다.

### Rust

- [ ] rust-analyzer와 rustfmt component가 active toolchain에 있다.
- [ ] rustaceanvim health check가 통과한다.
- [ ] `<leader>cf`가 rustfmt 결과를 만든다.
- [ ] Rust Debuggables에서 Cargo target을 선택하고 breakpoint에 정지한다.

## 7.13 최종 연습문제

1. `:Lazy`는 정상인데 `vim.fn.exepath("pyright-langserver")`가 빈 문자열이다. 어느 계층의 문제이며 다음 두 검사는 무엇인가?
2. TypeScript 저장 때 quote가 작은따옴표와 큰따옴표 사이를 반복한다. 어떤 ownership 원칙으로 해결해야 하는가?
3. Python breakpoint는 작동하지만 project module import가 실패한다. Adapter와 program interpreter 중 무엇을 먼저 확인해야 하는가?
4. Rust `<leader>dr` 목록이 비어 있고 `cargo build`도 실패한다. CodeLLDB를 재설치하기 전에 무엇을 고쳐야 하는가?
5. Plugin update 뒤 문제가 생겼다. Git과 `:Lazy restore`를 사용해 알려진 revision으로 돌아가는 절차를 작성하라.

## 요약

- Plugin update와 Mason package update는 서로 다른 변경 단위다.
- 문제는 prerequisite부터 session까지 같은 순서로 좁힌다.
- LSP는 attach와 root, formatter는 availability와 owner, DAP는 adapter와 configuration을 본다.
- WSL에서는 Linux binary, Linux file system, clipboard provider 경계를 확인한다.
- 전체 data를 지우기 전에 package, lockfile, plugin cache 순서로 작은 복구를 시도한다.

## 추가 읽을거리

- [LazyVim 설치와 health check](https://www.lazyvim.org/installation)
- [LazyVim LSP 구성](https://www.lazyvim.org/plugins/lsp)
- [LazyVim formatting](https://www.lazyvim.org/plugins/formatting)
- [LazyVim DAP core](https://www.lazyvim.org/extras/dap/core)
- [Mason commands와 requirements](https://github.com/mason-org/mason.nvim)
- [lazy.nvim lockfile](https://lazy.folke.io/usage/lockfile)
- [Neovim clipboard provider](https://neovim.io/doc/user/provider.html)

[← 6장](./06-rust.md) · [목차](./index.md)
