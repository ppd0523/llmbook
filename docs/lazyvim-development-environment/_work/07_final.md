---
title: LazyVim으로 다중 언어 개발 환경 구축하기
version: 1.0
status: final
owner: agent
updated: 2026-07-22
target_reader: 터미널, Git, vi 기초를 알고 LazyVim은 처음인 개발자
topic: Linux와 WSL에서 LazyVim 기반 JavaScript·TypeScript·Python·Rust 환경 구축
---

# LazyVim으로 다중 언어 개발 환경 구축하기

이 기준 원고는 Linux와 WSL의 Linux shell에서 LazyVim을 설치하고 JavaScript,
TypeScript, Python, Rust의 LSP, formatter, debugger를 연결하는 방법을 설명한다.
운영체제 자체의 설치와 language 문법은 다루지 않는다. 내용은 2026-07-22의 공식 문서와
LazyVim Starter를 기준으로 검토했다.

## 학습 목표

이 자료를 마치면 독자는 다음을 할 수 있다.

1. 기존 Neovim 구성을 복구 가능하게 백업하고 LazyVim을 설치한다.
2. LazyVim, lazy.nvim, LazyExtras, Mason, LSP, formatter, DAP의 역할을 구분한다.
3. vtsls, Pyright, Ruff, rust-analyzer를 각 언어 buffer에 연결한다.
4. Prettier, Ruff, rustfmt로 source를 format하고 owner 충돌을 피한다.
5. js-debug-adapter, debugpy, CodeLLDB로 breakpoint debugging을 시작한다.
6. Health check와 상태 창으로 고장 난 계층을 찾는다.
7. 설정과 `lazy-lock.json`을 Git으로 관리하고 plugin revision을 복원한다.

## 필요한 선행지식

- Shell에서 command를 실행하고 directory를 이동할 수 있다.
- Git clone, status, add, commit을 사용할 수 있다.
- vi의 Normal/Insert mode와 저장·종료를 알고 있다.
- 실제로 사용할 언어의 runtime과 package manager가 설치되어 있다.

## 1. 개발 환경의 계층

LazyVim 화면이 열린 것과 개발 기능이 동작하는 것은 다르다. TypeScript definition
이동은 다음 경로를 지난다.

```text
LazyVim keymap
-> Neovim LSP client
-> vtsls process
-> project source와 tsconfig.json
-> definition 응답
```

전체 환경은 다섯 계층으로 나눈다.

| 계층 | 구성 요소 | 확인 방법 |
|---|---|---|
| 편집기 | Neovim | `nvim --version`, `:checkhealth` |
| plugin 구성 | lazy.nvim, LazyVim, extras | `:Lazy`, `:LazyExtras` |
| 도구 관리자 | Mason | `:Mason`, `:MasonLog` |
| 외부 process | server, formatter, adapter | `:LspInfo`, `:ConformInfo`, DAP session |
| 프로젝트 | source, runtime, manifest, config | project command와 root file |

lazy.nvim은 plugin manager, LazyVim은 기본 plugin spec과 설정, Starter는 사용자가 소유할
config template다. Mason은 LSP server, formatter, DAP adapter 같은 external tool을
Neovim data directory에 설치한다.

DAP debugging에는 client plugin, adapter executable, launch configuration이 모두
필요하다. DAP UI가 열린 사실만으로 debug session이 시작된 것은 아니다.

## 2. 사전 점검과 설치

2026-07-22 기준 LazyVim은 LuaJIT build Neovim 0.11.2 이상, Git 2.19 이상, Treesitter용
C compiler를 요구한다. Mason은 Unix에서 Git, curl 또는 wget, unzip, GNU tar, gzip이
필요하다.

```console
$ nvim --version | head -n 1
$ git --version
$ command -v cc curl unzip tar gzip
```

기존 config, plugin data, state, cache가 있으면 각각 겹치지 않는 이름으로 백업한다.

```console
$ mv ~/.config/nvim ~/.config/nvim.bak
$ mv ~/.local/share/nvim ~/.local/share/nvim.bak
$ mv ~/.local/state/nvim ~/.local/state/nvim.bak
$ mv ~/.cache/nvim ~/.cache/nvim.bak
```

공식 Starter를 clone하고 template의 Git metadata만 제거한다.

```console
$ git clone https://github.com/LazyVim/starter ~/.config/nvim
$ git -C ~/.config/nvim remote -v
$ rm -rf ~/.config/nvim/.git
$ nvim
```

첫 동기화가 끝나면 다음을 확인한다.

```vim
:LazyHealth
:checkhealth
:checkhealth mason
```

Optional provider warning보다 plugin download, Treesitter compiler, Mason archive utility의
필수 error를 먼저 본다.

WSL에서는 `command -v nvim node python3 git`로 Linux binary가 선택되었는지 확인한다.
Windows native Neovim과 WSL Neovim의 config와 data를 섞지 않는다. Linux tool로 작업할
project는 `/mnt/c`보다 `/home/<user>/projects`에 둘 때 file scan과 watcher 성능에
유리하다.

## 3. 공통 LazyVim 설정

완성 directory는 다음과 같다.

```text
~/.config/nvim/
├── init.lua
├── lazy-lock.json
├── stylua.toml
└── lua/
    ├── config/
    │   ├── autocmds.lua
    │   ├── keymaps.lua
    │   ├── lazy.lua
    │   └── options.lua
    └── plugins/
        └── languages.lua
```

`init.lua`는 `require("config.lazy")`만 호출한다. `lazy.lua`의 plugin spec에는 다음
extras를 사용자 override보다 먼저 import한다.

```lua
spec = {
  { "LazyVim/LazyVim", import = "lazyvim.plugins" },
  { import = "lazyvim.plugins.extras.dap.core" },
  { import = "lazyvim.plugins.extras.lang.typescript" },
  { import = "lazyvim.plugins.extras.formatting.prettier" },
  { import = "lazyvim.plugins.extras.linting.eslint" },
  { import = "lazyvim.plugins.extras.lang.python" },
  { import = "lazyvim.plugins.extras.lang.rust" },
  { import = "plugins" },
}
```

`options.lua`에는 도구 선택을 명시한다.

```lua
vim.g.lazyvim_ts_lsp = "vtsls"
vim.g.lazyvim_prettier_needs_config = true
vim.g.lazyvim_eslint_auto_format = false
vim.g.lazyvim_python_lsp = "pyright"
vim.g.lazyvim_python_ruff = "ruff"
vim.g.lazyvim_rust_diagnostics = "rust-analyzer"
```

ESLint는 diagnostics와 code action, Prettier는 JS/TS formatting을 소유한다. Python은
Pyright가 type/navigation, Ruff가 lint/format을 담당한다.

`plugins/languages.lua`는 Mason package와 Python formatter를 명시한다.

```lua
return {
  {
    "mason-org/mason.nvim",
    opts = {
      ensure_installed = {
        "codelldb",
        "debugpy",
        "eslint-lsp",
        "js-debug-adapter",
        "prettier",
        "pyright",
        "ruff",
        "vtsls",
      },
    },
  },
  {
    "stevearc/conform.nvim",
    opts = {
      formatters_by_ft = {
        python = { "ruff_format" },
      },
    },
  },
}
```

Rust의 rust-analyzer와 rustfmt는 project toolchain과 맞게 rustup component로 설치한다.
Neovim에서 `:Lazy sync`, `:MasonUpdate`, `:Mason`을 실행하고 8개 Mason package의 설치
상태를 확인한다.

## 4. JavaScript와 TypeScript

구성은 vtsls, ESLint language server, Prettier, js-debug-adapter로 나눈다. Project를
준비한다.

```console
$ mkdir lazyvim-ts-smoke
$ cd lazyvim-ts-smoke
$ npm init -y
$ npm install --save-dev typescript tsx prettier eslint
$ npx tsc --init
$ npm init @eslint/config@latest
```

`.prettierrc.json`을 만든다.

```json
{
  "semi": true,
  "singleQuote": true
}
```

TypeScript current-file debug가 project-local `tsx`를 찾도록 smoke test에서는 PATH를
임시로 확장한다.

```console
$ PATH="$PWD/node_modules/.bin:$PATH" nvim .
```

TypeScript file에서 다음을 확인한다.

1. `:set filetype?`가 `typescript`다.
2. `:LspInfo`에 vtsls와 필요한 경우 ESLint가 attach된다.
3. `gd`, `K`, `<leader>cr`이 동작한다.
4. Type error를 만들면 vtsls diagnostic이 보인다.
5. `:ConformInfo`에 Prettier가 available하다.
6. `<leader>cf`와 저장 시 formatting이 같은 결과를 만든다.

Debug할 줄에서 `<leader>db`, `<leader>dc`, `Launch file`을 선택한다. TypeScript에는
PATH에서 찾을 수 있는 `tsx` 또는 `ts-node`가 필요하다. Project별 command가 있으면
`.vscode/launch.json`에 `pwa-node` configuration을 commit한다. JavaScript file은
Node.js가 직접 실행하므로 같은 extra와 keymap을 사용하되 TypeScript runtime은 필요
없다.

## 5. Python

Python은 Pyright, Ruff, debugpy로 나눈다. Project와 `.venv`를 준비한다.

```console
$ mkdir lazyvim-python-smoke
$ cd lazyvim-python-smoke
$ python3 -m venv .venv
$ source .venv/bin/activate
$ nvim .
```

WSL에서는 Windows에서 만든 virtual environment를 재사용하지 않고 WSL 안에서 새로
만든다. 이미 Neovim을 연 경우 `<leader>cv` 또는 `:VenvSelect`로 `.venv`를 선택한다.

`pyproject.toml`에 Ruff policy를 기록한다.

```toml
[tool.ruff]
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I"]
```

Python file에서 다음을 확인한다.

1. `:LspInfo`에 Pyright와 Ruff가 attach된다.
2. Type error와 unused import가 서로 다른 diagnostic source로 나타난다.
3. `:ConformInfo`에 `ruff_format`이 available하다.
4. `<leader>cf`가 source를 format한다.
5. `<leader>db`, `<leader>dc`, `Launch file`로 breakpoint에 정지한다.

Mason의 `debugpy-adapter`를 실행하는 Python과 application을 실행하는 project
`.venv/bin/python`은 역할이 다르다. Adapter가 설치되어도 project interpreter가 틀리면
`ModuleNotFoundError`가 날 수 있다.

## 6. Rust

Rust는 rustaceanvim과 rust-analyzer, rustfmt, CodeLLDB로 나눈다. Toolchain component와
project를 준비한다.

```console
$ rustup component add rust-analyzer rustfmt
$ cargo new lazyvim-rust-smoke
$ cd lazyvim-rust-smoke
$ cargo build
$ nvim .
```

Rust extra는 generic nvim-lspconfig의 rust_analyzer를 끄고 rustaceanvim이 lifecycle을
소유하게 한다. 별도 `rust_analyzer = {}` 설정을 다시 추가하지 않는다.

Rust file에서 다음을 확인한다.

1. `:checkhealth rustaceanvim`이 Cargo, rust-analyzer, parser를 찾는다.
2. `:LspInfo`에 rust-analyzer가 attach된다.
3. `gd`, `K`, `<leader>ca`가 동작한다.
4. `rustfmt --version`이 성공하고 `<leader>cf`가 source를 format한다.
5. `:Mason`과 `vim.fn.exepath("codelldb")`가 adapter를 찾는다.
6. `<leader>db`, `<leader>dr`에서 Cargo target을 선택해 breakpoint에 정지한다.

Rust formatting은 conform.nvim에 external formatter가 표시되지 않아도 rust-analyzer의
LSP formatting으로 fallback할 수 있다. 실제 format 결과, LSP attach, rustfmt component를
함께 확인한다.

오래된 Linux에서 CodeLLDB가 shared library error로 시작되지 않으면 plugin보다 host의
glibc와 binary compatibility를 먼저 확인한다. Attach debugging은 Linux `ptrace` policy에
막힐 수 있으므로 launch debugging이 정상인지 먼저 비교한다.

## 7. 운영과 문제 해결

Plugin update는 `:Lazy update`, lockfile revision 복원은 `:Lazy restore`를 사용한다.
`lazy-lock.json`은 plugin revision만 고정하고 Mason package나 language runtime은 고정하지
않는다. Update 후 네 언어 smoke test를 수행한 뒤 lockfile diff를 commit한다.

문제는 항상 다음 순서로 좁힌다.

```text
Neovim prerequisite
-> LazyVim plugin과 extra
-> Mason package와 executable
-> filetype와 project root
-> project runtime과 config
-> LSP, formatter, DAP session
```

| 증상 | 핵심 검사 |
|---|---|
| `gd` 무반응 | filetype, `:LspInfo`, server executable, root |
| Format 무반응 | `:ConformInfo`, project config, autoformat toggle |
| Format 결과 반복 변경 | formatter owner 중복 |
| DAP UI만 열림 | adapter executable과 launch configuration |
| Python import error | project `.venv` interpreter |
| Rust debug target 없음 | project root와 `cargo build` |
| WSL에서 전반적으로 느림 | Windows binary 혼용과 `/mnt/c` 위치 |

Clipboard가 동작하지 않으면 `:checkhealth`의 clipboard section을 확인한다. Neovim은
지원되는 terminal에서 OSC 52를 사용할 수 있으며 WSL용 clipboard provider도 공식
도움말에 제시한다.

전체 data directory를 즉시 지우지 않는다. Neovim 재시작, package 하나 재설치, lockfile
restore, plugin cache 재생성 순서로 복구 범위를 넓힌다. Clean bootstrap이 필요해도 data,
state, cache를 삭제하지 말고 다른 이름으로 이동해 비교 가능하게 보존한다.

## 8. 연습문제

1. `:Lazy`는 정상인데 `vim.fn.exepath("pyright-langserver")`가 빈 문자열이다. 어느 계층을 검사해야 하는가?
2. TypeScript 저장 때 quote style이 반복해서 바뀐다. Formatter ownership을 어떻게 정리해야 하는가?
3. Python adapter는 시작하지만 module import가 실패한다. 어떤 Python path를 확인해야 하는가?
4. Rust Debuggables가 비어 있고 `cargo build`도 실패한다. CodeLLDB보다 무엇을 먼저 고쳐야 하는가?
5. Git의 이전 lockfile과 `:Lazy restore`로 plugin revision을 되돌리는 절차를 작성하라.

## 9. 요약

- LazyVim plugin, external tool, project dependency는 서로 다른 소유권과 검증 방법을 가진다.
- Extras는 언어별 기본 연결을 제공하고 Mason은 편집기용 executable을 설치한다.
- JS/TS는 vtsls·Prettier·js-debug, Python은 Pyright·Ruff·debugpy, Rust는 rust-analyzer·rustfmt·CodeLLDB를 사용한다.
- LSP는 attach와 root, formatter는 availability와 owner, DAP는 adapter와 configuration을 확인한다.
- WSL에서는 Linux binary와 Linux file system을 기준으로 환경을 일관되게 유지한다.

## 10. 참고문헌

- LazyVim, [Installation](https://www.lazyvim.org/installation), 2026-07-22 확인.
- LazyVim, [TypeScript extra](https://www.lazyvim.org/extras/lang/typescript), 2026-07-22 확인.
- LazyVim, [Python extra](https://www.lazyvim.org/extras/lang/python), 2026-07-22 확인.
- LazyVim, [Rust extra](https://www.lazyvim.org/extras/lang/rust), 2026-07-22 확인.
- LazyVim, [DAP Core](https://www.lazyvim.org/extras/dap/core), 2026-07-22 확인.
- LazyVim, [Formatting](https://www.lazyvim.org/plugins/formatting), 2026-07-22 확인.
- mason-org, [mason.nvim](https://github.com/mason-org/mason.nvim), 2026-07-22 확인.
- folke, [lazy.nvim Lockfile](https://lazy.folke.io/usage/lockfile), 2026-07-22 확인.
- Astral, [Ruff Editor Integration](https://docs.astral.sh/ruff/editors/), 2026-07-22 확인.
- Rust project, [rustup Components](https://rust-lang.github.io/rustup/concepts/components.html), 2026-07-22 확인.
- Neovim, [Provider and Clipboard](https://neovim.io/doc/user/provider.html), 2026-07-22 확인.
- Microsoft, [Working across file systems](https://learn.microsoft.com/windows/wsl/filesystems), 2026-07-22 확인.
