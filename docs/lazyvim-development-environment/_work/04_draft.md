---
title: LazyVim 개발 환경 구축 가이드 초고
version: 0.1
status: draft
owner: agent
updated: 2026-07-22
target_reader: 터미널, Git, vi 기초를 알고 LazyVim은 처음인 개발자
topic: Linux와 WSL에서 LazyVim 기반 다중 언어 개발 환경 구축
---

# LazyVim 개발 환경 구축 가이드 초고

## 1. 문제 제기

LazyVim을 설치해 화면이 열리는 것과 개발 환경이 완성되는 것은 다르다. 코드 이동은 language server, 포매팅은 formatter, 디버깅은 debug adapter라는 별도 process가 담당한다. Neovim plugin은 이 process를 실행하고 결과를 화면에 연결한다.

초심자가 자주 만나는 문제는 다음과 같다.

- `:Lazy`에는 plugin이 보이는데 definition 이동이 되지 않는다.
- 저장해도 코드가 포매팅되지 않거나 두 formatter가 서로 다른 결과를 만든다.
- breakpoint를 만들 수는 있지만 debug session은 시작하지 않는다.
- WSL에서 Windows Neovim과 Linux tool이 섞인다.

이 자료는 각 문제를 하나의 “설치 실패”로 보지 않고 plugin, external executable, project root, project runtime 계층으로 나누어 진단한다.

## 2. 직관적 예시

TypeScript 파일에서 `gd`를 눌러 definition으로 이동한다고 가정한다.

```text
키 입력
-> LazyVim의 LSP keymap
-> Neovim LSP client
-> vtsls process
-> tsconfig.json과 source tree 분석
-> 위치 응답
```

이 흐름에서 plugin이 설치되어도 `vtsls` executable이 없으면 요청을 보낼 server가 없다. executable이 있어도 잘못된 디렉터리에서 Neovim을 열면 project root를 찾지 못할 수 있다. 따라서 `:Lazy`, `:Mason`, `:LspInfo`는 서로 다른 계층을 검사한다.

## 3. 공통 기반

### 3.1 사전 조건

2026-07-22 기준 공식 LazyVim 요구사항은 LuaJIT으로 빌드한 Neovim 0.11.2 이상, Git 2.19 이상, Treesitter용 C compiler다. Mason을 사용하려면 Unix 환경에서 Git, curl 또는 wget, unzip, GNU tar, gzip이 필요하다.

```console
$ nvim --version | head -n 1
$ git --version
$ command -v cc
$ command -v curl
$ command -v unzip
$ command -v tar
$ command -v gzip
```

이 자료는 OS package 설치 방법을 다루지 않는다. 명령이 없거나 Neovim version이 낮으면 해당 배포판의 공식 package 문서 또는 Neovim 공식 설치 문서에서 먼저 해결한다.

### 3.2 기존 설정 백업

공식 설치 문서는 config뿐 아니라 data, state, cache도 함께 백업하기를 권한다. 이전 config와 plugin cache가 섞이지 않게 하기 위해서다.

```console
$ mv ~/.config/nvim ~/.config/nvim.bak
$ mv ~/.local/share/nvim ~/.local/share/nvim.bak
$ mv ~/.local/state/nvim ~/.local/state/nvim.bak
$ mv ~/.cache/nvim ~/.cache/nvim.bak
```

존재하는 `.bak`을 덮어쓰지 않도록 실제 실행 전 경로를 확인해야 한다.

### 3.3 starter 설치

```console
$ git clone https://github.com/LazyVim/starter ~/.config/nvim
$ rm -rf ~/.config/nvim/.git
$ nvim
```

첫 실행은 lazy.nvim과 plugin을 내려받기 때문에 network가 필요하다. 동기화가 끝나면 `:LazyHealth`, `:checkhealth`, `:checkhealth mason`을 실행한다.

### 3.4 구성 파일의 역할

```text
~/.config/nvim/
├── init.lua
├── lazy-lock.json
├── stylua.toml
└── lua/
    ├── config/
    │   ├── lazy.lua
    │   ├── options.lua
    │   ├── keymaps.lua
    │   └── autocmds.lua
    └── plugins/
        └── languages.lua
```

- `init.lua`: `config.lazy`를 호출하는 entrypoint다.
- `lazy.lua`: lazy.nvim을 bootstrap하고 LazyVim과 extras, 사용자 plugin spec을 불러온다.
- `options.lua`: LazyVim이 시작되기 전에 global option과 feature selector를 정한다.
- `plugins/*.lua`: plugin 추가·override를 위한 table을 반환한다.
- `lazy-lock.json`: plugin Git revision을 기록하며 Git에 commit한다.

### 3.5 채택할 extras

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

언어 extra보다 `dap.core`를 먼저 import한다. 언어 extra의 DAP spec은 optional이므로 DAP core plugin이 있을 때만 구성에 합쳐진다. 사용자 override는 extras 뒤에 import해 마지막으로 병합한다.

### 3.6 도구 정책

`options.lua`에는 자료에서 선택한 기본값을 명시한다.

```lua
vim.g.lazyvim_ts_lsp = "vtsls"
vim.g.lazyvim_prettier_needs_config = true
vim.g.lazyvim_eslint_auto_format = false
vim.g.lazyvim_python_lsp = "pyright"
vim.g.lazyvim_python_ruff = "ruff"
vim.g.lazyvim_rust_diagnostics = "rust-analyzer"
```

ESLint는 diagnostics와 code action, Prettier는 formatting을 담당한다. Python은 Pyright가 type/navigation, Ruff가 lint/format을 담당한다.

`languages.lua`는 Mason package와 Python formatter를 명시한다.

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

rust-analyzer와 rustfmt는 Rust toolchain version에 맞춰 rustup component로 설치한다. Mason의 `lazy-lock.json`은 Mason package version을 잠그지 않는다는 점을 별도로 설명한다.

## 4. JavaScript와 TypeScript

### 4.1 역할

| 기능 | 도구 | 설치/연결 |
|---|---|---|
| navigation과 type diagnostics | vtsls | TypeScript extra와 Mason |
| source formatting | Prettier | Prettier extra와 conform.nvim |
| lint diagnostics와 code action | ESLint language server | ESLint extra와 Mason |
| debugging | js-debug-adapter | DAP core와 TypeScript extra |
| TypeScript 직접 실행 | tsx 또는 ts-node | 프로젝트 dev dependency |

### 4.2 프로젝트 준비

```console
$ mkdir lazyvim-ts-smoke
$ cd lazyvim-ts-smoke
$ npm init -y
$ npm install --save-dev typescript tsx prettier eslint
$ npx tsc --init
$ npm init @eslint/config@latest
```

프로젝트에 Prettier 설정을 만든다. `vim.g.lazyvim_prettier_needs_config = true`이므로 config가 없는 project에서는 의도적으로 Prettier를 실행하지 않는다.

```json
{
  "semi": true,
  "singleQuote": true
}
```

### 4.3 검증

프로젝트 root에서 `nvim .`을 실행한다. TypeScript current-file debug의 기본 구성이
`tsx` 또는 `ts-node`를 `PATH`에서 찾으므로, smoke test에서는 project-local binary를
임시로 노출한다. 팀 프로젝트에서는 같은 효과를 내는 direnv 설정이나
`.vscode/launch.json`을 commit한다.

```console
$ PATH="$PWD/node_modules/.bin:$PATH" nvim .
```

1. `.ts` 파일에서 `:set filetype?`가 `typescript`인지 확인한다.
2. `:LspInfo`에서 vtsls가 attach되었는지 확인한다.
3. symbol 위에서 `K`, `gd`, `<leader>cr`을 사용한다.
4. `:ConformInfo`에서 prettier가 available인지 확인한다.
5. `<leader>cf`로 format하고 저장 후 결과가 유지되는지 확인한다.
6. 실행할 줄에 `<leader>db`, `<leader>dc`를 누르고 `Launch file`을 선택한다.

TypeScript launch는 PATH의 `tsx`를 우선하고 없으면 `ts-node`를 찾으므로 둘 중 하나를 project dependency로 제공한다. JavaScript는 Node.js가 파일을 직접 실행한다.

## 5. Python

### 5.1 역할

| 기능 | 도구 | 설치/연결 |
|---|---|---|
| type/navigation | Pyright | Python extra와 Mason |
| lint, import 정리, format | Ruff | Python extra, Mason, conform.nvim |
| virtual environment 선택 | venv-selector.nvim | Python extra |
| debugging | debugpy와 nvim-dap-python | DAP core, Python extra, Mason |

### 5.2 프로젝트 준비

```console
$ mkdir lazyvim-python-smoke
$ cd lazyvim-python-smoke
$ python3 -m venv .venv
$ source .venv/bin/activate
$ nvim .
```

Neovim을 활성화된 environment에서 시작하면 shell PATH와 project interpreter를 맞추기 쉽다. 이미 실행한 뒤에는 `<leader>cv` 또는 `:VenvSelect`로 `.venv`를 선택한다.

### 5.3 검증

1. `:LspInfo`에서 pyright와 ruff가 attach되었는지 확인한다.
2. 의도적인 type error를 만들고 Pyright diagnostic을 확인한다.
3. import 순서나 quote를 흐트러뜨리고 `<leader>cf`를 실행한다.
4. `:ConformInfo`에서 `ruff_format`이 available인지 확인한다.
5. `<leader>db`, `<leader>dc`로 `Launch file`을 선택한다.
6. test function에서는 `<leader>dPt`, class에서는 `<leader>dPc`를 사용할 수 있다.

debugpy adapter를 실행하는 Python과 실제 program을 실행하는 project Python은 역할이 다르다. adapter가 설치되어도 project interpreter가 틀리면 import error가 날 수 있다.

## 6. Rust

### 6.1 역할

| 기능 | 도구 | 설치/연결 |
|---|---|---|
| navigation, diagnostics | rust-analyzer와 rustaceanvim | rustup component와 Rust extra |
| formatting | rustfmt | rustup component, LSP/conform fallback |
| debugging | CodeLLDB | DAP core, Rust extra, Mason |

### 6.2 toolchain과 project 준비

```console
$ rustup component add rust-analyzer rustfmt clippy
$ cargo new lazyvim-rust-smoke
$ cd lazyvim-rust-smoke
$ nvim .
```

Rust extra는 일반 nvim-lspconfig의 rust_analyzer를 끄고 rustaceanvim이 server를 소유하게 한다. 중복 client를 직접 추가하지 않는다.

### 6.3 검증

1. `:checkhealth rustaceanvim`으로 Cargo, rust-analyzer, parser를 확인한다.
2. `:LspInfo`와 `K`, `gd`로 LSP를 확인한다.
3. `<leader>cf`로 rustfmt 결과를 확인한다.
4. `:Mason`에서 codelldb 설치 상태를 확인한다.
5. `<leader>dr`의 Rust Debuggables에서 Cargo target을 선택하고 breakpoint 정지를 확인한다.

CodeLLDB 공식 binary는 Linux에서 glibc 2.18 이상을 요구한다. 오래된 배포판에서 adapter가 시작되지 않는 문제는 LazyVim plugin 문제가 아니라 binary/platform compatibility 문제로 분류한다.

Rust는 conform.nvim 전용 formatter 대신 rust-analyzer의 LSP formatting으로 fallback할
수 있다. 따라서 `:ConformInfo`에 Rust formatter가 표시되지 않아도 `<leader>cf`가
동작할 수 있다. `rustfmt --version`과 LSP attach 상태를 함께 확인한다.

## 7. 공통 문제 해결

### 7.1 고정된 진단 순서

```text
Neovim/OS prerequisite
-> LazyVim plugin load
-> Mason external executable
-> filetype와 project root
-> project runtime/config
-> LSP/formatter/DAP session
```

| 계층 | 확인 | 답하는 질문 |
|---|---|---|
| baseline | `nvim --version`, `:checkhealth` | host가 요구사항을 만족하는가? |
| LazyVim | `:LazyHealth`, `:Lazy`, `:LazyExtras` | plugin과 extra가 load되었는가? |
| external tool | `:Mason`, `:MasonLog`, `:checkhealth mason` | server/formatter/adapter가 설치되었는가? |
| LSP | `:set filetype?`, `:LspInfo` | 올바른 server가 buffer에 attach되었는가? |
| formatter | `:ConformInfo` | 선택된 formatter가 available한가? |
| debugger | adapter 설치, launch choice, `:messages` | adapter와 configuration이 모두 있는가? |

### 7.2 대표 증상

- `gd` 무반응: filetype, root, LSP attach, server executable 순으로 본다.
- format 무반응: autoformat toggle, `:ConformInfo`, project config, formatter conflict 순으로 본다.
- DAP UI만 열림: UI와 session은 별개다. adapter executable과 launch configuration을 확인한다.
- Python import error: selected `.venv`와 DAP program interpreter를 확인한다.
- Rust adapter 종료: CodeLLDB 설치와 host glibc, Cargo build 성공 여부를 확인한다.
- WSL에서 이상한 executable 사용: `command -v nvim node python3`로 Linux path인지 확인한다.

### 7.3 WSL 전용 주의사항

- Linux toolchain으로 개발할 project는 `/home/<user>/...`에 두는 편이 `/mnt/c/...`보다 file scan과 watch 성능에 유리하다.
- Windows PATH가 WSL PATH에 합쳐질 수 있으므로 `.exe`가 선택되지 않았는지 확인한다.
- system clipboard가 동작하지 않으면 `:checkhealth`의 clipboard section을 먼저 확인한다. 최신 Neovim은 terminal이 지원하면 OSC 52를 사용할 수 있고 WSL용 provider를 별도로 지정할 수도 있다.

## 8. 운영

- config를 Git 저장소로 만들고 `lazy-lock.json`을 commit한다.
- plugin update는 `:Lazy update`, lock 기준 복원은 `:Lazy restore`를 사용한다.
- update 후 네 언어 smoke test를 수행하고 문제가 생기면 lockfile diff를 검토한다.
- Mason registry와 package update는 plugin lock과 별도다. `:MasonUpdate`와 `:Mason`에서 관리한다.
- 원인을 모르는 상태에서 data directory 전체를 지우지 않는다. config, plugin cache, Mason package, project dependency 중 어느 계층인지 먼저 구분한다.

## 9. 직접 해보기

1. TypeScript project에서 vtsls를 중지시킨 뒤 `:LspInfo`와 Mason 상태로 원인을 찾아 복구한다.
2. Python project를 `.venv` 활성화 전후로 열어 interpreter와 diagnostic 변화를 기록한다.
3. Rust에서 rust-analyzer component를 제거했을 때 health 결과가 어느 계층을 가리키는지 설명한다.
4. `lazy-lock.json`을 commit한 뒤 plugin update와 restore 전후의 revision을 비교한다.

## 10. 초고 점검

- [x] 처음부터 끝까지 읽을 수 있는 형태다.
- [x] 주요 개념이 빠지지 않았다.
- [x] runtime 환경에서만 확인 가능한 항목을 분리했다.
- [x] 문장 다듬기보다 구조 완성을 우선했다.
