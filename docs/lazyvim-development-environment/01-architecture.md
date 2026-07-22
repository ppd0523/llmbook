# 1. LazyVim 개발 환경의 구조

## 학습 목표

1. LazyVim과 lazy.nvim의 역할을 구분한다.
2. plugin, external tool, project dependency의 소유자를 구분한다.
3. LSP, formatter, DAP 요청이 실패할 수 있는 계층을 설명한다.
4. Linux와 WSL에서 작업을 시작하기 전 필요한 명령을 확인한다.

## 1.1 “화면이 열린다”와 “개발 기능이 동작한다”는 다르다

LazyVim을 설치하면 file explorer, 검색, completion, diagnostics 같은 사용자 경험을
빠르게 얻을 수 있다. 하지만 화면에 보이는 plugin이 source code를 직접 분석하거나
program을 직접 debug하는 것은 아니다. 대부분의 개발 기능은 Neovim 밖의 실행 파일과
통신한다.

TypeScript definition으로 이동하는 `gd`를 예로 들면 다음 경로를 지난다.

```text
키 입력
-> LazyVim의 LSP keymap
-> Neovim LSP client
-> vtsls language server process
-> tsconfig.json과 source tree
-> definition 위치 응답
```

`gd`가 동작하지 않을 때 keymap만 다시 설정해서는 해결되지 않을 수 있다. vtsls가
설치되지 않았거나, server가 현재 buffer에 연결되지 않았거나, 잘못된 project root를
선택했을 수 있기 때문이다.

## 1.2 다섯 계층으로 나누기

| 계층 | 대표 구성 요소 | 책임 | 대표 확인 방법 |
|---|---|---|---|
| 편집기 | Neovim | buffer, UI, built-in LSP client | `nvim --version`, `:checkhealth` |
| plugin 구성 | lazy.nvim, LazyVim, extras | plugin 설치·로딩과 기본 연결 | `:Lazy`, `:LazyExtras` |
| 도구 관리자 | Mason | server, formatter, adapter 실행 파일 설치 | `:Mason`, `:MasonLog` |
| 외부 process | vtsls, Ruff, CodeLLDB 등 | 분석, format, debug protocol 처리 | `:LspInfo`, `:ConformInfo`, DAP session |
| 프로젝트 | source, runtime, manifest, config | 실제 code와 dependency, tool policy | project command와 root file |

이 표에서 가장 중요한 경계는 plugin과 외부 process 사이에 있다. `nvim-dap` plugin을
설치했다고 debugpy나 CodeLLDB가 저절로 생기는 것은 아니다. 반대로 language server
binary만 설치해도 Neovim client 설정이 없으면 buffer에 연결되지 않는다.

## 1.3 이름이 비슷한 세 구성 요소

### lazy.nvim

lazy.nvim은 Neovim plugin manager다. Git 저장소에서 plugin을 내려받고, 시작 조건에
맞춰 load하며, 설치 revision을 `lazy-lock.json`에 기록한다.

### LazyVim

LazyVim은 lazy.nvim 위에서 동작하는 plugin spec과 기본 설정의 모음이다. 직접 모든
plugin 조합을 설계하는 대신 검증된 기본값을 사용하고 필요한 부분만 override하게 한다.

### LazyVim Starter

Starter는 사용자가 자신의 `~/.config/nvim`으로 소유할 최소 template다. Starter가
LazyVim을 plugin으로 불러오며, 사용자는 `lua/config/`와 `lua/plugins/` 아래의 파일을
수정한다.

## 1.4 LSP, formatter, DAP

### LSP

Language Server Protocol은 editor client와 language server 사이의 통신 규약이다.
definition, reference, hover, rename, completion, diagnostics가 대표 기능이다. 한 buffer에
server가 attach되어야 관련 keymap이 의미를 가진다.

### formatter

Formatter는 source text를 정해진 style로 다시 쓴다. 이 가이드에서는 LazyVim 기본
orchestrator인 conform.nvim이 Prettier나 Ruff를 호출한다. 실행할 formatter가 없으면
지원되는 경우 LSP formatting으로 fallback한다.

### DAP

Debug Adapter Protocol은 editor와 debugger 사이의 통신 규약이다. Debug session에는
세 가지가 모두 필요하다.

1. `nvim-dap` 같은 DAP client plugin
2. debugpy, js-debug-adapter, CodeLLDB 같은 adapter executable
3. 어떤 program을 어떤 argument로 실행하거나 attach할지 정한 configuration

DAP UI가 열린 사실은 session이 시작되었다는 뜻이 아니다. UI는 상태를 표시할 뿐이며,
adapter나 launch configuration이 없으면 breakpoint까지 실행이 도달하지 않는다.

## 1.5 이 가이드의 소유권 정책

| 대상 | 소유자 | 예시 |
|---|---|---|
| Neovim plugin revision | LazyVim config 저장소 | `lazy-lock.json` |
| 편집기용 external tool | Mason | `vtsls`, `debugpy`, `codelldb` |
| Rust toolchain component | rustup과 프로젝트 toolchain | `rust-analyzer`, `rustfmt` |
| JavaScript·TypeScript dependency | Node project | `package.json`, package manager lockfile |
| Python dependency와 interpreter | Python project | `.venv`, `pyproject.toml`, dependency lockfile |
| Rust dependency | Cargo project | `Cargo.toml`, `Cargo.lock` |
| formatter와 linter policy | 프로젝트 | `.prettierrc`, ESLint config, `pyproject.toml` |

Mason 중심 구성은 입문하기 쉽지만 Mason package version은 `lazy-lock.json`에 기록되지
않는다. 조직 차원의 완전한 재현성이 필요하면 이후에 system package manager, Nix,
container 또는 project toolchain으로 external tool까지 고정할 수 있다. 그 전환은 이
가이드의 범위 밖이지만 위 소유권 표를 그대로 적용할 수 있다.

## 1.6 시작 전 확인

2026-07-22 기준 LazyVim 공식 요구사항과 이 가이드의 도구를 다음처럼 확인한다.

```console
$ nvim --version | head -n 1
NVIM v0.11.2
$ git --version
git version 2.19.0
$ command -v cc
/usr/bin/cc
$ command -v curl
/usr/bin/curl
$ command -v unzip
/usr/bin/unzip
$ command -v tar
/usr/bin/tar
$ command -v gzip
/usr/bin/gzip
```

출력의 실제 patch version과 경로는 달라도 된다. 핵심은 Neovim이 0.11.2 이상이고 각
명령이 현재 Linux shell의 `PATH`에서 발견되는 것이다. `ripgrep`과 `fd`도 파일 검색의
성능과 기능을 위해 권장한다.

사용할 언어의 runtime도 확인한다.

```console
$ node --version
$ npm --version
$ python3 --version
$ rustup --version
$ cargo --version
```

이 자료는 배포판 package manager나 WSL 자체의 설치 방법을 설명하지 않는다. 누락된
명령은 각 운영체제 또는 runtime의 공식 설치 문서에서 준비한 뒤 다음 장으로 이동한다.

## 1.7 WSL에서 시작할 때만 확인할 것

WSL shell에서 실행하는 Neovim, Node.js, Python은 Linux binary여야 한다. Windows의
`PATH`가 WSL에 합쳐져 `.exe`가 먼저 선택되는 경우가 있으므로 경로를 확인한다.

```console
$ command -v nvim node python3 git
/usr/bin/nvim
/home/dev/.local/bin/node
/usr/bin/python3
/usr/bin/git
```

예시와 경로가 같을 필요는 없지만 `/mnt/c/.../nvim.exe`처럼 Windows binary가 선택되면
Linux용 Mason package와 섞지 않는다. Windows native Neovim 설정과 WSL Neovim 설정은
각각 다른 환경으로 취급한다.

Microsoft는 Linux command line으로 작업할 project를 WSL의 Linux file system에 두는
것을 권장한다. 대규모 project를 `/mnt/c`에서 열어 file scan과 watcher가 느리다면
`/home/<user>/projects`로 옮긴 뒤 비교한다.

## 요약

- LazyVim은 구성이고 lazy.nvim은 plugin manager이며 Starter는 사용자가 소유할 template다.
- LSP, formatter, debugger는 대부분 외부 process가 실제 작업을 수행한다.
- DAP에는 client plugin, adapter executable, launch configuration이 모두 필요하다.
- Mason은 편집기 도구를 설치하지만 project dependency manager를 대신하지 않는다.
- 문제 해결은 편집기, plugin, 도구 관리자, 외부 process, 프로젝트의 다섯 계층으로 나눈다.

## 추가 읽을거리

- [LazyVim 공식 저장소와 요구사항](https://github.com/LazyVim/LazyVim)
- [mason.nvim 공식 문서](https://github.com/mason-org/mason.nvim)
- [WSL 파일 시스템 작업 지침](https://learn.microsoft.com/windows/wsl/filesystems)

[← 목차](./index.md) · [2장: 설치와 첫 실행 →](./02-installation.md)
