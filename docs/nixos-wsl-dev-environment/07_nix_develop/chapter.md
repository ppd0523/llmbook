# 7. `nix develop`과 direnv로 프로젝트 환경 만들기

## 학습 목표

1. `nix develop`, direnv, nix-direnv의 역할 차이를 설명한다.
2. 프로젝트에 `devShell`을 만들고 수동으로 들어갔다가 나올 수 있다.
3. 신뢰한 프로젝트에서만 개발 환경을 자동으로 불러온다.
4. `.lazy.lua`와 `.lazy-lock.json`으로 프로젝트별 LazyVim plugin을 격리하고 LSP를 연결한다.

## 7.1 먼저 알아둘 핵심

`nix develop`은 프로젝트에 필요한 도구를 컴퓨터 전체에 영구 설치하는 명령이 아니다. 프로젝트의 Flake가 선언한 `devShell`을 읽고, 그 도구와 환경 변수가 보이는 임시 셸을 연다. `exit`하면 원래 셸로 돌아온다.

```text
NixOS / Home Manager
  └─ 평소 어느 프로젝트에서나 쓰는 사용자 환경

프로젝트의 flake.nix + flake.lock
  └─ nix develop이 만드는 프로젝트 전용 환경
       └─ direnv + nix-direnv가 디렉터리별로 자동 진입·해제
```

세 도구의 역할은 겹치지 않는다.

| 도구 | 하는 일 |
|---|---|
| `nix develop` | `devShell`을 평가하고 개발 도구가 들어 있는 셸을 연다. |
| direnv | 디렉터리에 들어오고 나갈 때 `.envrc`에 따라 환경을 불러오거나 해제한다. |
| nix-direnv | direnv가 Nix 개발 환경을 빠르게 재사용하도록 캐시하고 Flake 변경을 감시한다. |

direnv만으로도 Nix를 호출할 수 있지만, nix-direnv를 함께 쓰면 매번 환경을 다시 만드는 대기 시간이 줄어든다. nix-direnv는 direnv를 대체하지 않는 보조 도구다.

## 7.2 Home Manager로 direnv와 nix-direnv 설치

이 책의 [Home Manager 예제](../assets/example-config/modules/home/programs.nix)에는 다음 설정이 포함되어 있다.

```nix
programs.direnv = {
  enable = true;
  enableZshIntegration = true;
  nix-direnv.enable = true;
};
```

- `enable`: direnv를 설치하고 기본 설정을 만든다.
- `enableZshIntegration`: `cd`할 때 direnv가 동작하도록 zsh 훅을 연결한다.
- `nix-direnv.enable`: `.envrc`의 `use flake`를 nix-direnv 구현으로 처리한다.

설정을 적용하고 새 zsh를 열어 설치를 확인한다.

```console
$ home-manager build --flake ~/.config/nixos#nixos
$ home-manager switch --flake ~/.config/nixos#nixos
$ exec zsh
$ direnv version
$ type _direnv_hook
```

`home-manager build`는 먼저 평가만 해 보는 안전 확인이고, `switch`가 실제 사용자 프로필을 바꾼다.

## 7.3 가장 작은 `devShell` 만들기

프로젝트 루트에 다음 `flake.nix`를 만든다. 그대로 실행할 수 있는 파일은 [예제 개발 셸](../assets/example-dev-shell/flake.nix)에도 있다.

```nix
{
  description = "Small project development shell example";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs = { nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        packages = with pkgs; [
          jq
          openssl
          pkg-config
        ];

        PROJECT_ENV = "nix-develop";

        shellHook = ''
          echo "development shell loaded"
        '';
      };
    };
}
```

처음 보는 문법은 네 부분만 구분하면 된다.

- `inputs.nixpkgs`: 패키지를 가져올 Nixpkgs 계열을 정한다.
- `system`: 이 예제의 실행 플랫폼인 64비트 Linux를 선택한다. NixOS-WSL도 여기에 해당한다.
- `devShells.${system}.default`: 인자 없이 `nix develop`을 실행할 때 선택할 기본 셸이다.
- `pkgs.mkShell`: `packages`, 환경 변수, 시작 스크립트를 하나의 개발 환경으로 묶는다.

`packages`는 이 셸 안에서만 PATH에 나타난다. `PROJECT_ENV`는 일반 환경 변수가 되고, `shellHook`은 셸에 들어갈 때마다 실행된다. 비밀번호나 토큰을 `flake.nix` 또는 `shellHook`에 넣어서는 안 된다. Flake 소스와 빌드 결과가 Nix Store에 복사될 수 있기 때문이다.

## 7.4 잠금 파일을 만들고 수동으로 사용하기

프로젝트에서 잠금 파일을 한 번 만들고 두 파일을 Git에 넣는다.

```console
$ git add flake.nix
$ nix flake lock
$ git add flake.lock
$ nix develop
development shell loaded
```

첫 실행은 Nixpkgs와 필요한 패키지를 내려받으므로 오래 걸릴 수 있다. 셸 안에서 확인한다.

```console
$ echo "$PROJECT_ENV"
nix-develop
$ jq --version
$ openssl version
$ exit
```

`exit` 또는 `Ctrl-D` 뒤에는 개발 셸에서 추가된 도구와 환경 변수가 사라진다. 대화형 셸 없이 명령 하나만 실행하려면 `-c`를 사용한다.

```console
$ nix develop -c jq --version
```

기본 셸이 아닌 이름 있는 셸 `devShells.x86_64-linux.docs`를 만들었다면 `nix develop .#docs`처럼 선택한다.

## 7.5 디렉터리 진입 시 자동으로 불러오기

프로젝트 루트의 `.envrc`에는 한 줄만 둔다.

```bash
use flake
```

파일을 Git에 추가한 뒤 최초 한 번 승인한다.

```console
$ git add .envrc
$ direnv allow
direnv: loading .../.envrc
development shell loaded
```

이후 프로젝트 디렉터리를 벗어나면 환경이 자동으로 해제되고, 다시 들어오면 로드된다. `flake.nix`, `flake.lock`, `.envrc`가 바뀌면 nix-direnv가 환경을 다시 평가한다.

`.envrc`는 단순 설정 파일이 아니라 셸 코드다. clone한 저장소에서 내용을 먼저 읽고 신뢰할 때만 `direnv allow`를 실행한다. 파일이 바뀌면 direnv가 기존 승인을 취소하고 다시 승인을 요구하는 것도 이 때문이다.

```console
$ direnv status
$ direnv reload
$ direnv deny
```

- `status`: 현재 허용 상태와 로드된 `.envrc`를 확인한다.
- `reload`: 환경을 즉시 다시 읽는다.
- `deny`: 현재 `.envrc` 승인을 취소한다.

이름 있는 `docs` 셸을 자동으로 선택하려면 `.envrc`를 `use flake .#docs`로 바꾼다.

## 7.6 무엇을 `devShell`에 넣어야 할까

판단 기준은 “이 프로젝트를 clone한 동료와 CI도 같은 도구가 필요한가?”다.

| 대상 | 권장 위치 |
|---|---|
| `git`, `nvim`, `direnv`처럼 매일 쓰는 개인 도구 | Home Manager |
| 컴파일러, 코드 생성기, `pkg-config`, 네이티브 라이브러리 | 프로젝트 `devShell` |
| Python·Node.js·Rust의 정확한 버전 | 프로젝트가 택한 한 가지 방식 |
| LSP, formatter, linter | 가능하면 프로젝트의 언어 의존성 또는 툴체인 파일 |
| LazyVim 언어 extra와 프로젝트 plugin | 프로젝트 `.lazy.lua`, `.lazy-lock.json` |
| API 토큰, 개인 SSH 키 | Flake 밖의 비밀 저장소 또는 로컬 환경 |

6장의 uv·NVM·rustup 방식을 쓰는 기존 프로젝트라면 `devShell`에는 그 프로젝트가 추가로 요구하는 시스템 라이브러리만 넣어도 된다. 반대로 새 프로젝트가 Python이나 Node.js 자체를 `devShell`에서 고정하도록 정했다면 같은 런타임을 NVM이나 rustup으로 다시 선택하지 않는다. 한 런타임을 두 도구가 동시에 소유하면 PATH 순서에 따라 버전이 달라져 디버깅이 어려워진다.

`flake.lock`은 Nix 패키지 쪽 재현성을 맡는다. `uv.lock`, `package-lock.json`, `Cargo.lock` 같은 언어 의존성 잠금 파일을 대신하지 않는다.

## 7.7 LazyVim과 프로젝트 환경 연결하기

이 절부터는 앞에서 설치한 Home Manager 구성과 언어 버전 관리자를 실제 프로젝트에
연결한다. 경계는 다음과 같다.

```text
Home Manager
  ├─ nvim + lazy.nvim + 최소 LazyVim 기반
  ├─ 공통 UI·키맵 + fd + tree-sitter
  ├─ 프로젝트 spec 로더 + Mason 비활성화 정책
  └─ uv + NVM + rustup + direnv + nix-direnv

프로젝트 저장소
  ├─ .lazy.lua + .lazy-lock.json   플러그인 선택과 리비전
  ├─ flake.nix + flake.lock         네이티브 도구와 라이브러리
  ├─ .envrc                         디렉터리 진입 자동화
  ├─ 언어 버전 파일                Python·Node.js·Rust 버전
  └─ 언어 잠금 파일                패키지와 LSP 실행 파일
```

`.envrc`와 `.lazy.lua`는 모두 프로젝트 파일이지만 역할은 다르다. direnv는
`.envrc`를 읽어 Nix 개발 환경과 PATH를 활성화한다. 그 뒤 실행한 Neovim은
`.lazy.lua`를 읽어 이 프로젝트에 필요한 LazyVim extra와 플러그인을 합성한다.
따라서 direnv가 LazyVim을 설정하는 것은 아니다.

### LazyVim 공통 요구사항 설치

[예제 `lazyvim.nix`](../assets/example-config/modules/home/lazyvim.nix)는 Neovim,
Nixpkgs가 고정한 lazy.nvim, 공통 요구사항만 설치한다. 언어 extra는 여기에 없다.

```nix
programs.neovim = {
  enable = true;
  defaultEditor = true;
  viAlias = true;
  vimAlias = true;
  extraPackages = with pkgs; [
    fd
    tree-sitter
  ];
  plugins = [ pkgs.vimPlugins.lazy-nvim ];
};
```

Git, ripgrep, C 컴파일러는 앞의 Home Manager 패키지 목록에 이미 있다. LazyVim 설치
문서는 현재 Neovim 0.11.2 이상을 요구하므로 적용 뒤 버전을 확인한다.

```console
$ home-manager build --flake ~/.config/nixos#nixos
$ home-manager switch --flake ~/.config/nixos#nixos
$ exec zsh
$ nvim --version | head -n 1
$ fd --version
$ tree-sitter --version
```

### LazyVim 설정을 Git으로 관리

[예제 Neovim dotfiles](../assets/example-config/dotfiles/nvim/init.lua)는 공식 starter 구조를
따르되 프로젝트별 spec, lock 파일, 플러그인 캐시를 선택한다.

```lua
local project_spec = vim.fs.find(".lazy.lua", {
  path = vim.uv.cwd(),
  upward = true,
})[1]
local project_root = project_spec and vim.fs.dirname(project_spec) or nil
local project_id = project_root and vim.fn.sha256(project_root):sub(1, 12) or nil

require("lazy").setup({
  root = project_id
      and (vim.fn.stdpath("data") .. "/lazy-projects/" .. project_id)
    or (vim.fn.stdpath("data") .. "/lazy"),
  lockfile = project_root
      and (project_root .. "/.lazy-lock.json")
    or (vim.fn.stdpath("config") .. "/lazy-lock.json"),
  local_spec = true,
  spec = {
    { "LazyVim/LazyVim", import = "lazyvim.plugins" },
    { import = "plugins" },
  },
})
```

프로젝트마다 플러그인 설치 디렉터리까지 분리하는 이유는 lock 파일만 나누고 checkout을
공유하면 서로 다른 프로젝트가 요구하는 리비전이 충돌할 수 있기 때문이다. 절대 경로의
해시는 캐시 식별자일 뿐 Git에 넣지 않는다. 같은 프로젝트를 다른 위치에 clone하면 새
캐시를 만들지만 커밋된 `.lazy-lock.json`으로 같은 리비전을 복원한다.

Mason을 끄는 것도 공통 정책이다. Mason이 편집기 전용 LSP를 설치하면 프로젝트의 언어
잠금 파일과 무관한 버전이 선택될 수 있다. LSP가 없으면 Mason으로 해결하지 않고
`uv sync`, `npm ci`, rustup component 중 해당 프로젝트의 복원 명령을 실행한다.
DAP 디버거도 자동 설치되지 않으므로 필요한 프로젝트만 `.lazy.lua`와 개발 환경에
함께 선언한다.

### 두 개의 신뢰 절차

`.envrc`와 `.lazy.lua`는 모두 실행 가능한 코드다. clone한 프로젝트에서는 두 파일을
각각 검토한다.

```console
$ less .envrc
$ less .lazy.lua
$ direnv allow
$ nvim .
```

`direnv allow`는 `.envrc`만 승인한다. lazy.nvim은 `.lazy.lua`를 읽을 때 Neovim의
`vim.secure.read()`를 사용하므로 최초 실행에서 별도의 신뢰 확인을 요청한다. 선택은
`$XDG_STATE_HOME/nvim/trust`에 파일 내용의 hash와 함께 저장되며 파일이 바뀌면 다시
검토해야 한다. 직접 승인할 때는 파일을 버퍼에서 읽은 뒤 `:trust`를 실행한다.

### 기본 lock과 프로젝트 lock

LazyVim은 플러그인 리비전을 `~/.config/nvim/lazy-lock.json`에 쓴다. Nix Store의
디렉터리는 읽기 전용이므로 예제 Home Manager는 `~/.config/nvim`을 Git 작업 트리인
`~/.config/nixos/dotfiles/nvim`으로 연결하는 out-of-store 링크를 사용한다. 이 예외로
프로젝트 밖에서 사용하는 기본 lock을 구성 저장소에 커밋할 수 있다. clone 위치를
바꾸면 링크 대상도 바꿔야 한다.

`.lazy.lua`가 있는 프로젝트에서는 기본 lock 대신 프로젝트 루트의
`.lazy-lock.json`을 사용한다. 예제의 초기 파일은 빈 JSON 객체이며 최초 동기화가 실제
리비전을 기록한다.

```console
$ cd <project>
$ less .lazy.lua
$ nvim .
# Neovim 안에서 실행
:Lazy sync
:LazyHealth
```

종료한 뒤 프로젝트 lock의 변경을 확인해 같은 프로젝트 저장소에 커밋한다.

```console
$ git diff -- .lazy-lock.json
$ git add .lazy.lua .lazy-lock.json
$ git commit -m "Configure project LazyVim plugins"
```

## 7.8 Python: uv 가상환경을 LazyVim에 연결

전체 파일은 [Python 예제](../assets/example-dev-shell/python/flake.nix)에 있다.
소유권은 다음처럼 나뉜다.

| 파일 | 역할 |
|---|---|
| `.python-version` | uv가 설치하고 선택할 Python 3.13.7 |
| `pyproject.toml`, `uv.lock` | 애플리케이션 의존성과 basedpyright, Ruff, pytest |
| `.lazy.lua`, `.lazy-lock.json` | Python·test extra와 프로젝트 플러그인 리비전 |
| `flake.nix`, `flake.lock` | OpenSSL과 `pkg-config` 같은 네이티브 의존성 |
| `.envrc` | `use flake`로 Nix 환경 자동 로드 |

Python 자체와 basedpyright를 `flake.nix`에 다시 넣지 않는다. `devShell`은 `uv sync`가
만드는 `.venv/bin`을 PATH 앞에 추가한다.

Python 프로젝트가 필요한 LazyVim 기능도 프로젝트가 선언한다.

```lua
vim.g.lazyvim_python_lsp = "basedpyright"
vim.g.lazyvim_python_ruff = "ruff"

return {
  { import = "lazyvim.plugins.extras.lang.python" },
  { import = "lazyvim.plugins.extras.test.core" },
}
```

```nix
devShells.${system}.default = pkgs.mkShell {
  packages = with pkgs; [
    openssl
    pkg-config
  ];

  shellHook = ''
    export PATH="$PWD/.venv/bin:$PATH"
  '';
};
```

먼저 자동화를 배제한 `nix develop`로 각 층을 검증한다.

```console
$ cd python
$ nix flake lock
$ nix develop
$ uv python install 3.13.7
$ uv sync
$ command -v python basedpyright ruff
$ python --version
$ uv run pytest
$ nvim .
```

최초 신뢰 확인 뒤 `:Lazy sync`를 실행해 `.lazy-lock.json`을 채운다. `main.py`를 열고
`:LspInfo`를 실행하면 `basedpyright`와 `ruff`가 보여야 한다. 둘의 경로는 프로젝트의
`.venv/bin` 아래여야 한다. 정상 동작을 확인했으면 `exit`하고 자동 로드를 승인한다.

```console
$ exit
$ less .envrc
$ direnv allow
$ uv sync --locked
$ nvim .
$ git add .envrc .lazy.lua .lazy-lock.json .python-version \
    flake.nix flake.lock pyproject.toml uv.lock
```

`.venv`와 `.direnv`는 생성 상태이므로 Git에서 제외한다. clone한 컴퓨터는 lock 파일을
바탕으로 `uv sync --locked`를 실행해 같은 환경을 복원한다.

## 7.9 Node.js: NVM과 프로젝트 로컬 vtsls 연결

전체 파일은 [Node.js 예제](../assets/example-dev-shell/nodejs/flake.nix)에 있다.
`.nvmrc`는 정확한 Node.js 버전을, `package-lock.json`은 TypeScript와
`@vtsls/language-server`, Prettier 버전을 고정한다. `flake.nix`에는 Node.js를 넣지
않는다. 프로젝트의 `.lazy.lua`도 TypeScript와 Prettier extra만 선택한다.

```lua
vim.g.lazyvim_ts_lsp = "vtsls"

return {
  { import = "lazyvim.plugins.extras.lang.typescript" },
  { import = "lazyvim.plugins.extras.formatting.prettier" },
}
```

```nix
shellHook = ''
  export PATH="$PWD/node_modules/.bin:$PATH"
'';
```

Home Manager의 NVM 훅은 디렉터리의 `.nvmrc`를 인식한다. 최초에는 다음 순서로
명시적으로 설치하고 수동 개발 셸을 검사한다.

```console
$ cd nodejs
$ nvm install
$ nvm use
$ nix flake lock
$ nix develop
$ npm install
$ command -v node npm vtsls prettier
$ node --version
$ npm run check
$ nvim .
```

최초 신뢰 확인 뒤 `:Lazy sync`를 실행한다. `src/index.ts`를 열고 `:LspInfo`를
실행했을 때 `vtsls` 경로가 `node_modules/.bin`을 가리키면 프로젝트 로컬 LSP를
사용 중이다. `:ConformInfo`에서는 프로젝트의 Prettier를 확인한다. 첫
`npm install`이 만든 `package-lock.json`을 커밋한 뒤부터는 `npm ci`를 사용한다.

```console
$ exit
$ less .envrc
$ direnv allow
$ npm ci
$ nvim .
$ git add .envrc .lazy.lua .lazy-lock.json .nvmrc flake.nix flake.lock \
    package.json package-lock.json tsconfig.json src
```

디렉터리에 다시 들어왔는데 `node --version`이 `.nvmrc`와 다르면 `nvm use`를 실행한다.
이것은 Nix 평가 문제가 아니라 NVM zsh 훅의 실행 순서 문제다.

## 7.10 Rust: rustup component를 LazyVim에 연결

전체 파일은 [Rust 예제](../assets/example-dev-shell/rust/flake.nix)에 있다.
`rust-toolchain.toml`이 컴파일러뿐 아니라 LazyVim이 사용할 구성 요소도 고정한다.

Rust와 test extra는 프로젝트의 `.lazy.lua`에서만 활성화한다.

```lua
vim.g.lazyvim_rust_diagnostics = "rust-analyzer"

return {
  { import = "lazyvim.plugins.extras.lang.rust" },
  { import = "lazyvim.plugins.extras.test.core" },
}
```

```toml
[toolchain]
channel = "1.88.0"
profile = "minimal"
components = ["rust-analyzer", "rustfmt", "clippy"]
```

Home Manager에서 설정한 `RUSTUP_AUTO_INSTALL=1` 때문에 해당 디렉터리에서 처음
`rustc`나 `cargo`를 실행할 때 없는 툴체인이 설치된다. 프로젝트 Flake는 OpenSSL과
`pkg-config` 같은 네이티브 의존성만 제공한다.

```console
$ cd rust
$ nix flake lock
$ nix develop
$ rustup show active-toolchain
$ rustc --version
$ rust-analyzer --version
$ cargo fmt --check
$ cargo clippy --locked -- -D warnings
$ cargo test --locked
$ nvim .
```

최초 신뢰 확인 뒤 `:Lazy sync`를 실행한다. `src/main.rs`를 열고 `:LspInfo`를
실행하면 Rust extra의 rustaceanvim이 PATH의 `rust-analyzer`를 사용한다. 자동화도
같은 환경을 불러오는지 확인한다.

```console
$ exit
$ less .envrc
$ direnv allow
$ cargo test --locked
$ nvim .
$ git add .envrc .lazy.lua .lazy-lock.json flake.nix flake.lock \
    rust-toolchain.toml Cargo.toml Cargo.lock src
```

`~/.rustup`과 `target`은 생성 상태라 Git에 넣지 않는다. clone 복원에 필요한 것은
툴체인 선언과 Cargo 잠금 파일이다.

## 7.11 세 환경을 같은 방법으로 진단하기

셸에서 먼저 실행 파일을 확인하고, 같은 셸에서 Neovim을 연다.

| 언어 | `.lazy.lua`가 선택 | 셸에서 확인 | Neovim에서 기대할 LSP |
|---|---|---|---|
| Python | Python, test extra | `command -v python basedpyright ruff` | `basedpyright`, `ruff` |
| Node.js | TypeScript, Prettier extra | `command -v node vtsls prettier` | `vtsls` |
| Rust | Rust, test extra | `command -v rustc rust-analyzer` | rustaceanvim의 `rust-analyzer` |

Neovim에서는 `:LazyHealth`, `:checkhealth vim.lsp`, `:LspInfo` 순서로 확인한다.
formatter 문제는 `:ConformInfo`로 본다. `:LspInfo`에 서버가 없으면 다음 순서로
범위를 좁힌다.

1. Neovim을 종료한다.
2. 같은 터미널에서 `command -v <실행 파일>`을 확인한다.
3. 실패하면 `uv sync`, `npm ci`, `rustup component add` 중 해당 명령을 실행한다.
4. `nix develop`에서는 성공하지만 자동 로드에서만 실패하면 `direnv reload`를 실행한다.
5. 셸에서 성공하면 그 터미널에서 다시 `nvim .`을 실행한다.
6. plugin 문제라면 `:lua print(require("lazy.core.config").options.lockfile)`로 현재 lock
   경로를 확인하고 `:Lazy restore`를 실행한다.

`sudo nvim`, Windows 쪽 Neovim, 프로젝트 밖에서 먼저 연 Neovim은 이 PATH를 상속하지
않는다. WSL 프로젝트에서는 NixOS-WSL 터미널에서 프로젝트 디렉터리로 들어간 뒤
Neovim을 시작한다.

## 7.12 일상 작업 흐름

자동 로드를 사용하는 프로젝트의 평소 흐름은 짧다.

```console
$ git clone <project-url>
$ cd <project>
direnv: error ... .envrc is blocked
$ less .envrc
$ less .lazy.lua
$ direnv allow
$ nvim .
# .lazy.lua를 별도로 신뢰한 뒤 :Lazy restore, :LazyHealth
$ git status --short
```

환경 구성을 바꿀 때는 다음 순서를 사용한다.

```console
$ $EDITOR flake.nix
$ nix develop -c jq --version
$ git diff -- flake.nix flake.lock .envrc .lazy.lua .lazy-lock.json
$ git add flake.nix flake.lock .envrc .lazy.lua .lazy-lock.json
```

입력을 의도적으로 갱신할 때만 `nix flake update`를 실행한다. 다른 컴퓨터에서 복원할 때는 커밋된 `flake.lock`을 그대로 사용한다.

## 흔한 오류

| 증상 | 원인 | 해결 |
|---|---|---|
| `direnv: command not found` | Home Manager 설정 미적용 | `home-manager build` 후 `switch`, 새 zsh 실행 |
| `cd`해도 아무 반응이 없음 | zsh 훅 미적용 또는 `.envrc` 없음 | `type _direnv_hook`, `.envrc` 위치 확인 |
| `.envrc is blocked` | 아직 승인하지 않았거나 파일이 변경됨 | 내용을 검토한 뒤 `direnv allow` |
| `nix develop`이 기본 셸을 찾지 못함 | `devShells.x86_64-linux.default`가 없거나 이름이 다름 | `nix flake show`, 출력 이름 확인 |
| 새 Nix 파일을 찾지 못함 | Git Flake에서 파일이 아직 추적되지 않음 | `git status --short` 확인 후 필요한 파일 `git add` |
| 수정 뒤에도 이전 환경이 보임 | 자동 재평가가 끝나지 않았거나 캐시된 환경 사용 | `direnv reload`; 필요하면 셸을 나갔다 다시 진입 |
| WSL의 첫 평가가 매우 느림 | 입력과 패키지를 처음 다운로드·빌드함 | 완료를 기다린 뒤 재사용; 프로젝트는 Linux 파일 시스템 아래 배치 |
| LazyVim이 `lazy-lock.json`을 쓰지 못함 | `~/.config/nvim`이 Nix Store의 읽기 전용 링크 | 예제의 `mkOutOfStoreSymlink` 설정 적용 후 Home Manager 전환 |
| `.lazy.lua` 플러그인이 보이지 않음 | Neovim 신뢰 요청을 거부했거나 파일 변경 뒤 재승인하지 않음 | 파일을 버퍼에서 검토하고 `:trust`; Neovim 다시 실행 |
| `.lazy-lock.json`이 `{}`로 남음 | 아직 프로젝트에서 plugin sync를 하지 않음 | 프로젝트에서 `nvim .`, `:Lazy sync` 후 diff 확인 |
| 프로젝트마다 plugin 다운로드 반복 | 격리를 위해 plugin cache를 프로젝트별로 분리함 | 정상 동작; lock은 Git에, cache는 `$XDG_DATA_HOME`에 유지 |
| `:LspInfo`에 서버가 없음 | 프로젝트 LSP가 설치되지 않았거나 Neovim PATH에 없음 | 셸에서 `command -v` 확인 후 `uv sync`, `npm ci`, rustup component 설치 |
| `:Mason` 명령이 없음 | 예제가 Mason을 의도적으로 비활성화함 | LSP를 해당 프로젝트의 언어 의존성 또는 툴체인에 추가 |

문제가 자동화인지 Nix 환경 자체인지 구분하려면 먼저 `nix develop`을 수동 실행한다. 이것도 실패하면 `flake.nix`나 Nix 입력 문제이고, 수동 실행만 성공하면 direnv 훅·승인·캐시 문제다.

## 요약

- `nix develop`은 프로젝트의 `devShell`을 임시 셸로 연다.
- direnv는 디렉터리별 환경 진입과 해제를 자동화하고 nix-direnv는 이를 캐시한다.
- `flake.nix`, `flake.lock`, `.envrc`는 프로젝트 저장소에 함께 커밋한다.
- clone한 `.envrc`는 반드시 내용을 검토한 뒤 승인한다.
- `.lazy.lua`도 실행 가능한 코드이므로 별도로 검토하고 Neovim trust를 승인한다.
- 언어 런타임은 Nix와 별도 버전 관리자 중 한 소유자만 정한다.
- 각 프로젝트의 `.lazy.lua`가 LazyVim extra를, `.lazy-lock.json`이 plugin 리비전을 고정한다.
- LazyVim은 활성화된 프로젝트 PATH의 basedpyright, vtsls, rust-analyzer를 사용한다.
- `flake.lock`, 언어 lock, `.lazy-lock.json`은 서로 다른 층을 고정한다.

## 추가 읽을거리

- [Nix `develop` 명령](https://nix.dev/manual/nix/latest/command-ref/new-cli/nix3-develop.html)
- [Nix Flake 개념](https://nix.dev/concepts/flakes.html)
- [direnv 공식 문서](https://direnv.net/)
- [nix-direnv 사용법](https://github.com/nix-community/nix-direnv)
- [LazyVim 설치](https://www.lazyvim.org/installation)
- [LazyVim Python extra](https://www.lazyvim.org/extras/lang/python)
- [LazyVim TypeScript extra](https://www.lazyvim.org/extras/lang/typescript)
- [LazyVim Rust extra](https://www.lazyvim.org/extras/lang/rust)
- [lazy.nvim 프로젝트 spec과 lock 설정](https://lazy.folke.io/configuration)
- [Neovim 신뢰 파일](https://neovim.io/doc/user/editing.html#trust)
- [uv 프로젝트 구조와 lock 파일](https://docs.astral.sh/uv/guides/projects/)
- [NVM `.nvmrc` 사용법](https://github.com/nvm-sh/nvm#nvmrc)
- [rustup 디렉터리 override](https://rust-lang.github.io/rustup/overrides.html)

[← 6장](../06_language_toolchains/chapter.md) · [목차](../index.md) · [8장: Git 복원 워크플로 →](../07_restore_workflow/chapter.md)
