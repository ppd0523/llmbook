# 3. 공통 설정과 plugin 관리

## 학습 목표

1. Starter의 구성 파일이 load되는 순서를 설명한다.
2. 필요한 LazyVim extras를 선언적으로 활성화한다.
3. Mason package와 formatter policy를 하나의 plugin spec에 기록한다.
4. plugin lock과 external tool version의 경계를 설명한다.

## 3.1 완성할 directory 구조

이 장을 마치면 `~/.config/nvim`은 다음 구조가 된다.

```text
~/.config/nvim/
├── init.lua
├── lazy-lock.json              # 첫 동기화 후 생성
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

LazyVim은 `lua/config/` 아래의 정해진 파일을 적절한 시점에 자동으로 load한다. 이 파일을
`init.lua`에서 다시 `require`하지 않는다. `lua/plugins/*.lua`의 모든 파일도 plugin
spec으로 자동 import된다.

## 3.2 Entrypoint 유지

공식 Starter의 `init.lua`는 bootstrap module 하나만 호출한다.

파일: `~/.config/nvim/init.lua`

```lua
-- Bootstrap lazy.nvim, LazyVim, and your plugins.
require("config.lazy")
```

여기에 언어 설정을 직접 계속 추가하지 않는다. 시작 순서를 다루는 `lazy.lua`, 일반
option을 다루는 `options.lua`, plugin override를 다루는 `plugins/*.lua`로 책임을 나눈다.

## 3.3 Extras 선언

`lua/config/lazy.lua`의 `spec`을 다음 순서로 구성한다. Bootstrap 전체는
[예제 `lazy.lua`](./assets/example-config/lua/config/lazy.lua)에서 확인할 수 있다.

파일(일부): `~/.config/nvim/lua/config/lazy.lua`

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

순서에는 다음 의도가 있다.

1. LazyVim core plugin spec을 먼저 가져온다.
2. DAP client와 UI를 활성화한다.
3. 언어와 formatter/linter extra를 합친다.
4. 사용자의 `plugins/*.lua`를 마지막에 합쳐 앞의 option을 override할 수 있게 한다.

`dap.core`가 없으면 언어 extra 안의 optional DAP spec이 활성화되지 않는다. 반대로
`dap.core`만 켜면 UI와 공통 keymap은 생기지만 언어별 adapter 설정은 생기지 않는다.

`:LazyExtras`에서 같은 extras를 대화형으로 켤 수도 있다. 이 가이드는 선택 결과가
code review에서 바로 보이도록 import를 직접 기록한다. 두 방식을 섞어 같은 extra를
중복 관리하지 않는다.

## 3.4 언어별 기본 선택 명시

공식 extra의 기본값도 [예제 `options.lua`](./assets/example-config/lua/config/options.lua)에
명시해 이 설정의 정책을 한눈에 볼 수 있게 한다.

파일(일부): `~/.config/nvim/lua/config/options.lua`

```lua
vim.g.lazyvim_ts_lsp = "vtsls"
vim.g.lazyvim_prettier_needs_config = true
vim.g.lazyvim_eslint_auto_format = false

vim.g.lazyvim_python_lsp = "pyright"
vim.g.lazyvim_python_ruff = "ruff"

vim.g.lazyvim_rust_diagnostics = "rust-analyzer"
```

`lazyvim_prettier_needs_config = true`는 Prettier 설정 파일이 있는 project에서만
Prettier를 사용하게 한다. 다른 formatter policy를 가진 저장소까지 우연히 다시 쓰는
일을 막는다.

`lazyvim_eslint_auto_format = false`는 ESLint의 자동 formatting을 끈다. 이 가이드에서는
ESLint가 diagnostics와 code action을, Prettier가 source formatting을 소유한다.
두 도구가 같은 저장 event에서 서로 다른 style을 적용하는 문제를 피하기 위한 선택이다.

## 3.5 Mason package와 Python formatter

`lua/plugins/languages.lua`는 plugin override table을 반환한다.

파일: `~/.config/nvim/lua/plugins/languages.lua`

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

Extras도 필요한 package 일부를 Mason에 요청한다. 목록을 다시 명시하는 작업은
idempotent하며, 이 설정이 기대하는 외부 도구를 한 파일에서 검토할 수 있게 한다.

Rust의 `rust-analyzer`와 `rustfmt`는 목록에 없다. 이 둘은 project가 선택한 Rust
toolchain과 같은 version을 사용하도록 rustup component로 설치한다.

Python extra의 Ruff language server는 diagnostics와 code action을 제공한다.
`ruff_format`을 conform.nvim에 별도로 지정하면 현재 buffer가 어떤 formatter를
선택했는지 `:ConformInfo`에서 관찰하기 쉽다.

## 3.6 예제 설정 적용

이 저장소를 clone한 directory의 root에서 다음 명령을 실행하면
[완성 예제](./assets/example-config/README.md)를 Starter 위에 복사할 수 있다.

```console
$ cp -a docs/lazyvim-development-environment/assets/example-config/. ~/.config/nvim/
$ nvim
```

직접 작성한 파일이 있다면 바로 덮어쓰지 말고 `diff -ru`로 먼저 비교한다. 예제는
`lazy-lock.json`을 포함하지 않는다. 첫 동기화가 끝난 뒤 현재 설치 revision으로 새로
생성되기 때문이다.

## 3.7 Plugin과 tool 동기화

Neovim에서 다음 순서로 확인한다.

```vim
:Lazy sync
:MasonUpdate
:Mason
```

`Lazy sync`는 선언된 plugin을 설치·정리·갱신하고 lockfile을 반영한다. Neovim을 한 번
재시작한 뒤 `:Mason`을 열어 다음 package가 `installed`인지 확인한다.

```text
codelldb
debugpy
eslint-lsp
js-debug-adapter
prettier
pyright
ruff
vtsls
```

설치가 실패하면 `:MasonLog`와 `:checkhealth mason`을 확인한다. Mason은 기본적으로
Neovim data directory 아래에 package를 설치하고 그 `bin/` directory를 Neovim process의
`PATH` 앞에 둔다. 일반 shell의 영구 `PATH`가 바뀌는 것은 아니다.

Neovim 안에서 실제 경로를 확인할 수 있다.

```vim
:lua print(vim.fn.exepath("vtsls"))
:lua print(vim.fn.exepath("pyright-langserver"))
:lua print(vim.fn.exepath("ruff"))
:lua print(vim.fn.exepath("debugpy-adapter"))
:lua print(vim.fn.exepath("codelldb"))
```

빈 줄이 나오면 해당 실행 파일이 현재 Neovim `PATH`에 없다.

## 3.8 공통 keymap

LazyVim 기본 keymap은 leader인 Space를 중심으로 구성된다.

| key | 기능 | 필요한 상태 |
|---|---|---|
| `gd` | definition 이동 | LSP attach |
| `gr` | reference 검색 | LSP attach |
| `K` | hover 문서 | LSP attach |
| `<leader>ca` | code action | LSP capability |
| `<leader>cr` | symbol rename | LSP capability |
| `<leader>cl` | LSP 정보 | LSP plugin |
| `<leader>cf` | format | formatter 또는 LSP formatting |
| `<leader>uf` | global autoformat toggle | LazyVim formatter |
| `<leader>uF` | buffer autoformat toggle | LazyVim formatter |
| `<leader>db` | breakpoint toggle | DAP core |
| `<leader>dc` | run/continue | adapter와 configuration |
| `<leader>di` | step into | active DAP session |
| `<leader>dO` | step over | active DAP session |
| `<leader>do` | step out | active DAP session |
| `<leader>du` | DAP UI toggle | DAP UI plugin |
| `<leader>dt` | debug session 종료 | active DAP session |

Key가 기억나지 않으면 Space를 누른 뒤 which-key의 `code` 또는 `debug` group을 따라간다.

## 3.9 도구 mapping

| 언어 | 분석 client/plugin | 실행 파일 | project 기준 파일 |
|---|---|---|---|
| JS·TS | nvim-lspconfig와 vtsls extra | `vtsls` | `package.json`, `tsconfig.json` |
| JS·TS lint | ESLint extra | `vscode-eslint-language-server` | ESLint config와 workspace `eslint` |
| JS·TS format | conform.nvim | `prettier` | `.prettierrc` 등 |
| JS·TS debug | nvim-dap | `js-debug-adapter` | file 또는 `.vscode/launch.json` |
| Python type | nvim-lspconfig | `pyright-langserver` | `pyproject.toml`, `.venv` |
| Python lint/format | Ruff extra와 conform.nvim | `ruff` | `pyproject.toml`, `ruff.toml` |
| Python debug | nvim-dap-python | `debugpy-adapter` | 선택한 project interpreter |
| Rust | rustaceanvim | `rust-analyzer` | `Cargo.toml` |
| Rust format | rust-analyzer formatting | `rustfmt` | Rust toolchain |
| Rust debug | rustaceanvim과 nvim-dap | `codelldb` | Cargo target |

## 3.10 Git으로 관리

첫 실행과 언어별 smoke test가 끝나면 config 자체를 Git 저장소로 만든다.

```console
$ cd ~/.config/nvim
$ git init
$ git add init.lua stylua.toml lua lazy-lock.json
$ git commit -m "Configure LazyVim development environment"
```

`lazy-lock.json`은 plugin의 Git revision을 고정한다. 다른 machine에서는 config를 clone한
뒤 `:Lazy restore`로 lockfile revision을 복원할 수 있다.

Mason package version, Node/Python/Rust runtime, project dependency는 이 lockfile의
범위가 아니다. 각각의 상태를 모두 `lazy-lock.json` 하나가 재현한다고 가정하지 않는다.

## 확인 문제

1. `dap.core`와 `lang.python` 중 하나만 활성화하면 Python debugging에 무엇이 빠지는가?
2. `lazy-lock.json`이 고정하는 대상과 고정하지 않는 대상을 하나씩 말해 보자.
3. `vim.fn.exepath("ruff")`가 빈 문자열이면 어느 계층부터 확인해야 하는가?

## 요약

- `lua/config`는 시작 설정, `lua/plugins`는 plugin spec과 override를 담당한다.
- DAP core, language extra, 사용자 override 순서로 spec을 합친다.
- ESLint는 진단, Prettier는 format을 맡겨 중복 formatter를 피한다.
- Mason package의 executable은 Neovim PATH에 추가되며 일반 shell PATH는 바뀌지 않는다.
- `lazy-lock.json`은 plugin revision만 고정한다.

## 추가 읽을거리

- [LazyVim 구성 파일](https://www.lazyvim.org/configuration/general)
- [LazyVim Extras](https://www.lazyvim.org/extras)
- [LazyVim plugin 설정](https://www.lazyvim.org/configuration/plugins)
- [lazy.nvim lockfile](https://lazy.folke.io/usage/lockfile)
- [Mason package 목록](https://mason-registry.dev/registry/list)

[← 2장](./02-installation.md) · [목차](./index.md) · [4장: JavaScript와 TypeScript →](./04-javascript-typescript.md)
