# 6. Rust

## 학습 목표

1. Rust toolchain과 Mason package의 소유권을 구분한다.
2. rustaceanvim이 rust-analyzer를 연결하는 구조를 설명한다.
3. rustfmt formatting과 CodeLLDB debugging을 검증한다.
4. Linux binary compatibility와 Cargo target 문제를 분리한다.

## 6.1 구성 요소

| 기능 | 도구 | 설치 위치 |
|---|---|---|
| code navigation과 diagnostics | rust-analyzer와 rustaceanvim | rustup component와 LazyVim extra |
| source formatting | rustfmt | rustup component |
| debugging | CodeLLDB와 nvim-dap | Mason package와 DAP core |
| build와 target discovery | Cargo | Rust toolchain과 project |

Rust extra는 일반 nvim-lspconfig의 `rust_analyzer` server를 비활성화하고
rustaceanvim이 rust-analyzer lifecycle을 소유하게 한다. 별도의 generic LSP 설정으로
rust-analyzer를 다시 추가하면 client가 중복될 수 있다.

## 6.2 Rust toolchain 준비

현재 Linux shell의 rustup과 Cargo를 확인한다.

```console
$ command -v rustup cargo
/home/dev/.cargo/bin/rustup
/home/dev/.cargo/bin/cargo
$ rustup --version
$ cargo --version
```

Language server와 formatter를 현재 toolchain에 추가한다.

```console
$ rustup component add rust-analyzer rustfmt
```

Clippy diagnostics를 project workflow에서 사용할 경우 함께 추가한다.

```console
$ rustup component add clippy
```

rustup component는 toolchain별로 설치된다. `rust-toolchain.toml`이 있는 project에서는 그
파일이 선택한 toolchain에 component가 존재하는지 확인한다.

```console
$ rustup component list --installed
rust-analyzer-...
rustfmt-...
```

## 6.3 Project 준비

Cargo binary project를 만든다.

```console
$ cargo new lazyvim-rust-smoke
$ cd lazyvim-rust-smoke
$ nvim .
```

`src/main.rs`를 다음처럼 수정한다.

파일: `<project-root>/src/main.rs`

```rust
fn add(left: i32, right: i32) -> i32 {
    left + right
}

fn main() {
    let answer = add(20, 22);
    println!("answer={answer}");
}
```

Editor integration을 검사하기 전에 shell에서 project가 build되는지 확인한다.

```console
$ cargo build
```

Cargo build가 실패하면 DAP보다 project/compiler 문제를 먼저 해결한다.

## 6.4 rust-analyzer와 rustaceanvim 확인

Neovim에서 Rust 전용 health check를 실행한다.

```vim
:checkhealth rustaceanvim
```

Cargo, rust-analyzer, Rust Treesitter parser, conflicting plugin 항목을 확인한다. 이어서
`:LspInfo`에서 현재 Rust buffer에 rust-analyzer가 attach되었는지 확인한다.

다음 동작을 시험한다.

1. `add` 호출 위에서 `gd`로 function definition에 이동한다.
2. `K`로 function signature를 확인한다.
3. `<leader>cr`로 local symbol을 rename한다.
4. `add(20, "22")`처럼 type error를 만들어 diagnostic을 확인한다.
5. `<leader>ca` 또는 `<leader>cR`에서 Rust code action을 확인한다.

오류 확인 후 source를 되돌린다.

## 6.5 rustfmt 확인

Source의 indentation을 일부러 흐트러뜨리고 `<leader>cf`를 실행한다. Rust extra는
rust-analyzer의 formatting capability를 사용하며, 실제 formatting은 toolchain의
rustfmt가 담당한다.

```console
$ rustfmt --version
```

LazyVim의 conform.nvim은 external formatter가 없을 때 LSP formatting으로 fallback한다.
따라서 `:ConformInfo`에 Rust 전용 formatter가 표시되지 않아도 `<leader>cf`가 동작할 수
있다. 이 경우 다음 세 항목을 함께 확인한다.

- `rustfmt --version`이 성공한다.
- rust-analyzer가 buffer에 attach되어 있다.
- `<leader>cf` 실행 후 source가 실제로 바뀐다.

## 6.6 CodeLLDB 확인

`:Mason`을 열어 `codelldb`가 installed 상태인지 확인한다. Neovim에서 executable 경로도
확인한다.

```vim
:lua print(vim.fn.exepath("codelldb"))
```

경로가 비어 있으면 `:MasonLog`에서 download나 archive extraction error를 확인한다.

## 6.7 Cargo target debugging

`let answer = ...` 줄에 breakpoint를 만든 뒤 Rust 전용 workflow를 사용한다.

1. `<leader>db`로 breakpoint를 만든다.
2. `<leader>dr`을 눌러 `Rust Debuggables`를 연다.
3. `lazyvim-rust-smoke` binary target을 선택한다.
4. Breakpoint에서 정지하면 `<leader>dO`와 `<leader>di`로 step한다.
5. `<leader>de`로 `answer`를 평가한다.
6. `<leader>dt`로 종료한다.

`<leader>dc`는 이미 정의된 generic configuration을 계속 실행할 때 유용하다. 처음에는
rustaceanvim이 Cargo metadata에서 target을 찾는 `<leader>dr`이 더 명확하다.

## 6.8 Linux와 WSL에서만 확인할 문제

CodeLLDB 공식 release binary는 Linux host에서 glibc 2.18 이상을 지원 대상으로 밝힌다.
오래된 배포판에서 `codelldb` process 자체가 시작되지 않거나 shared library error가 나면
LazyVim plugin 설정이 아니라 host binary compatibility를 먼저 확인한다.

WSL에서는 다음 세 program이 모두 WSL Linux 환경에 있어야 한다.

```console
$ command -v nvim cargo rust-analyzer
```

Project가 `/mnt/c`에 있고 rust-analyzer initial indexing이나 Cargo build가 유난히 느리면
WSL Linux file system의 `/home/<user>/projects`에서 같은 project를 비교한다.

실행이 아니라 기존 process에 attach하는 debugging은 Linux의 `ptrace` 보안 정책에 막힐
수 있다. 이 경우 launch debugging이 정상인지 먼저 확인하고, attach 권한 정책은 해당
배포판의 보안 지침을 따른다.

## 6.9 흔한 오류

| 증상 | 가장 가능성 높은 계층 | 확인과 해결 |
|---|---|---|
| rust-analyzer를 찾지 못함 | toolchain/PATH | rustup component와 active toolchain 확인 |
| Rust LSP client가 두 개 | plugin config | 별도 `rust_analyzer = {}` override 제거 |
| Macro나 generated code 진단이 이상함 | project/LSP | Cargo build, feature, proc-macro 설정 확인 |
| `<leader>cf`가 동작하지 않음 | rustfmt/LSP | component, LSP attach, actual format result 확인 |
| Debuggable 목록이 비어 있음 | Cargo project | project root와 `cargo build` 성공 확인 |
| CodeLLDB가 바로 종료 | adapter/platform | Mason log, executable, glibc/shared library 확인 |
| WSL에서 build/index가 매우 느림 | file system | `/mnt/c` 대신 WSL Linux file system에서 비교 |

## 직접 해보기

1. `rustup component remove rust-analyzer` 후 health 결과를 기록하고 다시 설치한다.
2. 별도 generic rust_analyzer 설정을 추가했을 때 client 수가 어떻게 달라지는지 조사한 뒤 제거한다.
3. Cargo project 밖에서 standalone `.rs` file을 열었을 때와 project root에서 열었을 때를 비교한다.
4. CodeLLDB 설치 성공과 Cargo build 성공이 서로 독립적인 조건인 이유를 설명한다.

## 요약

- Rust extra에서는 rustaceanvim이 rust-analyzer lifecycle을 소유한다.
- rust-analyzer와 rustfmt는 project toolchain에 맞춘 rustup component로 설치한다.
- Rust formatting은 conform.nvim 목록보다 LSP fallback과 실제 결과로 검증한다.
- 처음 debug할 때는 `<leader>dr`로 Cargo target을 선택한다.
- Adapter process 실패, Cargo build 실패, attach 권한 실패는 서로 다른 계층이다.

## 추가 읽을거리

- [LazyVim Rust extra](https://www.lazyvim.org/extras/lang/rust)
- [rustup component](https://rust-lang.github.io/rustup/concepts/components.html)
- [CodeLLDB 공식 저장소](https://github.com/vadimcn/codelldb)

[← 5장](./05-python.md) · [목차](./index.md) · [7장: 운영과 문제 해결 →](./07-troubleshooting.md)
