# flake-greeter 예제

이 디렉터리는 학습자료의 완성형 Flake다. Nixpkgs 26.05의 `cowsay`와 `nixfmt`를
사용한다.

## 실행

```console
$ nix flake show
$ nix develop --command cowsay "development shell"
$ nix build
$ ./result/bin/flake-greeter "built package"
$ nix run . -- "flake app"
$ nix fmt flake.nix
$ nix flake check
```

예제에는 Nixpkgs 26.05 revision을 고정한 `flake.lock`이 포함되어 있다. input을
갱신한 뒤에는 다음 순서로 검토한다.

```console
$ git diff -- flake.lock
$ nix flake check
$ git add flake.nix flake.lock
```

예제의 해설은 [Nix Flake 입문](../../index.md)에서 읽을 수 있다.
