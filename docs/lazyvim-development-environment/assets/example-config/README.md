# LazyVim 예제 설정

이 디렉터리는 2026-07-22의 공식 LazyVim Starter를 바탕으로 다음 extras를 추가한
완성 예제다.

- `dap.core`
- `lang.typescript`
- `formatting.prettier`
- `linting.eslint`
- `lang.python`
- `lang.rust`

기존 Neovim 설정을 백업하고 공식 starter를 clone한 뒤, 이 디렉터리의 내용을
`~/.config/nvim/`에 복사한다. 첫 실행에서 생성되는 `lazy-lock.json`은 예제에 포함하지
않는다. 정상 구성을 확인한 뒤 자신의 설정 저장소에 commit한다.

```console
$ cp -a docs/lazyvim-development-environment/assets/example-config/. ~/.config/nvim/
$ nvim
```

이 예제에서 Mason이 관리하는 도구는 `lua/plugins/languages.lua`에 기록되어 있다.
Rust의 `rust-analyzer`와 `rustfmt`, 각 프로젝트의 runtime과 dependency는 Mason이 아니라
각 language toolchain과 프로젝트가 관리한다.
