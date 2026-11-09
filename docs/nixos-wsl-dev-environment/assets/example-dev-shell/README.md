# 프로젝트 개발 셸 예제

`flake.nix`와 `.envrc`를 프로젝트 루트에 복사한 뒤 lock 파일을 만들고 commit한다.

```console
$ git add flake.nix .envrc
$ nix flake lock
$ git add flake.lock
```

`nix develop`으로 셸에 직접 들어가거나, 이 저장소의 `.envrc`를 `direnv allow`로 한 번
승인해 direnv가 자동으로 불러오게 한다.

하위 디렉터리는 LazyVim 실습에서 쓰는 언어별 완성 변형이다.

- `python`: uv, `.python-version`, basedpyright, Ruff, Python LazyVim extras
- `nodejs`: NVM, `.nvmrc`, 로컬 TypeScript/vtsls, Prettier extras
- `rust`: rustup, `rust-toolchain.toml`, rust-analyzer, rustfmt, Rust extras

각 변형은 언어 런타임을 의도적으로 `flake.nix`에 넣지 않는다. Flake는 프로젝트의
네이티브 의존성을 맡고, 런타임과 패키지는 언어 관리자와 언어 lock 파일이 맡는다.

모든 언어 디렉터리에는 프로젝트가 소유하는 `.lazy.lua`와 `.lazy-lock.json`도 있다.
앞의 파일은 그 저장소의 LazyVim extras를 선택한다. 뒤의 파일은 `:Lazy sync`가
채우며, 편집기가 처음 정상적으로 시작된 뒤 commit해야 한다. 공유 Home Manager 설정은
LazyVim 기반만 제공하고 신뢰된 로컬 spec을 켠다.

입문자를 위한 전체 설명은 안내서의 [7장](../../07-nix-develop.md)에 있다.
