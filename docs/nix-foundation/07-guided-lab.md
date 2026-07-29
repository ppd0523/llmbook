# 7. 안내식 통합 실습

## 실습 목표

1. 임시 package를 사용하고 Store path를 관찰한다.
2. Nix 표현식을 직접 평가한다.
3. 잠긴 프로젝트 개발 셸을 만들고 비대화형으로 검증한다.
4. 변경 파일과 Store 결과, 활성 shell을 구분한다.

이 실습은 기존 NixOS나 Home Manager 설정을 변경하지 않는다. 새 연습 디렉터리 안에
Flake를 만들고 shell process만 실행한다.

## 7.1 기준 환경 확인

```console
$ nix --version
$ nix eval --impure --raw --expr builtins.currentSystem
x86_64-linux
```

두 번째 출력은 머신에 따라 `aarch64-linux`, `x86_64-darwin`,
`aarch64-darwin`일 수 있다. 아래 `flake.nix`의 `system`을 그 출력으로 바꾼다.

기능 오류가 나고 아직 `nix-command`와 `flakes`를 켜지 않았다면 [목차의 준비
설정](./index.md#prerequisites)을 적용한다.

## 7.2 1단계: 설치 없이 도구 사용

shell 밖에서 상태를 본다.

```console
$ command -v cowsay || true
```

임시 shell에 들어간다.

```console
$ nix shell nixpkgs#cowsay nixpkgs#jq
$ command -v cowsay
/nix/store/...-cowsay-.../bin/cowsay
$ cowsay "step one"
$ jq --version
$ exit
```

여기서 확인한 사실:

- package 결과는 Store 경로에 있다.
- `nix shell`은 현재 시스템 package 목록을 고친 것이 아니라 자식 shell의 환경을
  조정했다.
- `nixpkgs` registry가 선택한 revision을 썼으며 아직 프로젝트 lockfile은 없다.

## 7.3 2단계: Nix 값을 직접 평가

```console
$ nix repl
```

REPL에서 입력한다.

```nix
person = { name = "Alice"; tools = [ "git" "jq" ]; }

person.name

builtins.length person.tools

greet = { name, greeting ? "hello" }: "${greeting}, ${name}"

greet { name = person.name; }

:q
```

예상 결과는 차례로 `"Alice"`, `2`, `"hello, Alice"`다. `person`은 속성 집합,
`tools`는 목록, `greet`는 속성 집합 인자를 받는 함수다.

## 7.4 3단계: 연습 저장소 생성

```console
$ mkdir nix-first-shell
$ cd nix-first-shell
$ git init
```

다음 파일을 편집기로 만든다.

파일: `<nix-first-shell>/flake.nix` (전체)

```nix
{
  description = "First locked development shell";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs =
    { nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        packages = [
          pkgs.cowsay
          pkgs.jq
        ];

        shellHook = ''
          echo "entered nix-first-shell"
        '';
      };
    };
}
```

`system`은 7.1에서 확인한 값으로 바꾼다. Git index에 파일을 추가한다.

```console
$ git add flake.nix
$ git status --short
A  flake.nix
```

## 7.5 4단계: 출력과 잠금 확인

```console
$ nix flake show
```

처음 실행하면 `flake.lock`이 생긴다. 출력에는 현재 system 아래 기본 dev shell이
보여야 한다.

```text
devShells
└───x86_64-linux
    └───default: development environment ...
```

잠금 정보를 간단히 확인한다.

```console
$ nix flake metadata
$ git status --short
```

`flake.lock`도 버전 관리에 넣는다.

```console
$ git add flake.lock
$ git diff --cached
```

확인할 부분:

- `flake.nix`에는 따라갈 Nixpkgs 계열과 output 계산식이 있다.
- `flake.lock`에는 실제 선택된 revision과 hash 정보가 있다.
- Store 결과물 자체를 Git에 넣지 않는다.

## 7.6 5단계: 개발 셸 검증

먼저 비대화형으로 실행한다.

```console
$ nix develop --command bash -c 'command -v cowsay && jq --version'
```

두 명령이 성공하면 대화형 shell에 들어간다.

```console
$ nix develop
entered nix-first-shell
$ echo "$IN_NIX_SHELL"
impure
$ cowsay "locked by flake"
$ jq -n '{source: "nix develop", ok: true}'
$ exit
```

`IN_NIX_SHELL` 값의 정확한 표시는 Nix 버전과 shell 모드에 따라 달라질 수 있다.
핵심 검증은 `command -v cowsay`가 Store의 선택된 package를 가리키고 두 도구가
실행된다는 점이다.

## 7.7 6단계: 변경 영향 관찰

`flake.nix`의 package 목록에 `pkgs.ripgrep`을 추가한다.

```nix
packages = [
  pkgs.cowsay
  pkgs.jq
  pkgs.ripgrep
];
```

새 source가 Flake 평가에 보이도록 stage하고 검증한다.

```console
$ git add flake.nix
$ nix develop --command rg --version
```

이 변경에서는 `flake.lock`이 바뀌지 않아야 한다. 입력 revision은 그대로이고, 그
입력에서 선택한 package 목록만 바뀌었기 때문이다.

```console
$ git status --short
$ git diff --cached -- flake.nix flake.lock
```

반대로 다음 명령은 입력 revision을 갱신할 수 있다.

```console
$ nix flake update nixpkgs
```

입문 실습에서 굳이 실행할 필요는 없다. 실행했다면 `flake.lock` diff와 개발 셸
검증을 함께 수행한다.

## 7.8 7단계: 설정 계층 판독

아래 세 조각을 실제로 적용하지 말고 읽기만 한다.

### A

```nix
{ pkgs, ... }:
{
  environment.systemPackages = [ pkgs.git ];
  services.openssh.enable = true;
}
```

### B

```nix
{ pkgs, ... }:
{
  home.packages = [ pkgs.ripgrep ];
  programs.git.enable = true;
}
```

### C

```nix
devShells.${system}.default = pkgs.mkShell {
  packages = [ pkgs.python3 ];
};
```

| 조각 | evaluator·계층 | 활성화 |
|---|---|---|
| A | NixOS module | `nixos-rebuild switch` |
| B | Home Manager module | standalone이면 `home-manager switch` |
| C | Flake dev shell output | `nix develop` process 동안 |

세 조각 모두 `pkgs`에서 package를 선택하지만 결과의 수명과 적용 범위가 다르다.

## 7.9 실습 완료 점검표

다음을 설명하거나 직접 보여 줄 수 있으면 완료다.

- [ ] `nixpkgs#cowsay`에서 `nixpkgs`와 `cowsay`의 역할을 구분한다.
- [ ] `command -v cowsay`가 Store 경로를 보여 주는 이유를 설명한다.
- [ ] 목록과 속성 집합의 구분 기호를 올바르게 쓴다.
- [ ] `flake.nix`의 `inputs`, `outputs`, `devShells`를 찾는다.
- [ ] `flake.lock`을 source와 함께 commit해야 하는 이유를 설명한다.
- [ ] `nix shell`과 `nix develop` 중 프로젝트에 맞는 명령을 고른다.
- [ ] NixOS, Home Manager, 프로젝트 설정 조각을 구분한다.
- [ ] `build`가 성공해도 반드시 활성화된 것은 아님을 설명한다.

## 7.10 실습 뒤 선택 사항

연습 디렉터리를 계속 쓴다면 먼저 현재 상태를 commit한다.

```console
$ git status
$ git add flake.nix flake.lock
$ git commit -m "Add first Nix development shell"
```

Git 작성자 설정이 없어 commit이 실패해도 Nix 실습 결과에는 영향이 없다. 설정을
고친 뒤 다시 commit한다.

디렉터리를 삭제할 필요는 없다. `nix develop`에서 나오는 것만으로 활성 shell은
종료되며, Store의 참조되지 않은 결과는 나중에 GC 정책에 따라 정리할 수 있다.

## 요약

- 임시 탐색은 `nix shell`, 반복 가능한 프로젝트 환경은 잠긴 Flake와 `nix develop`을
  사용한다.
- `flake.nix`는 계산 방법, `flake.lock`은 실제 입력 revision을 기록한다.
- Nix source, Store output, 활성 shell은 서로 다른 상태다.
- 같은 package 표현도 NixOS, Home Manager, 프로젝트 중 어디서 평가하는지에 따라
  수명과 범위가 달라진다.

[← 6장](./06-nixos-and-home-manager.md) · [목차](./index.md) ·
[8장: 문제 해결, 용어집, 다음 학습 →](./08-troubleshooting-and-next-steps.md)
