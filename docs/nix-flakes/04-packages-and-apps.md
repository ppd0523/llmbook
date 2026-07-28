# 4. 패키지와 앱 만들기

## 학습 목표

1. package와 app output의 역할을 구분한다.
2. `writeShellApplication`으로 런타임 의존성이 명시된 CLI를 만든다.
3. 같은 결과를 `nix build`와 `nix run`으로 각각 검증한다.

## 4.1 package와 app은 같은 것이 아니다

`packages.<system>.<name>`은 Nix가 빌드해 Nix Store에 둘 derivation을 제공한다.
`apps.<system>.<name>`은 어떤 Store 내부 실행 파일을 실행할지 설명하는 작은 속성
집합이다.

| 출력 | 질문 | 대표 명령 |
|---|---|---|
| package | 무엇을 빌드할 것인가? | `nix build` |
| app | 어떤 실행 파일을 시작할 것인가? | `nix run` |

`nix run`은 app이 없을 때 package의 main program을 추론해 실행할 수도 있다. 그러나
app을 명시하면 공개 실행 진입점과 설명을 분명히 할 수 있다.

## 4.2 `flake-greeter` package

3장의 Flake에 `self`를 받고 package를 추가한다.

파일: `<project-root>/flake.nix` (전체)

```nix
{
  description = "A package and app backed by cowsay";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs =
    {
      self,
      nixpkgs,
    }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      packages.${system} = rec {
        flake-greeter = pkgs.writeShellApplication {
          name = "flake-greeter";
          runtimeInputs = [ pkgs.cowsay ];
          text = ''
            message="''${1:-Hello from a Nix flake!}"
            cowsay "$message"
          '';
        };

        default = flake-greeter;
      };

      devShells.${system}.default = pkgs.mkShellNoCC {
        packages = [
          pkgs.cowsay
          self.packages.${system}.default
        ];
      };
    };
}
```

`writeShellApplication`은 실행 가능한 shell application을 만들고 runtime dependency를
PATH에 연결한다.

- `name`은 생성할 실행 파일명이다.
- `runtimeInputs`의 `pkgs.cowsay`는 실행 시 필요한 command를 명시한다.
- `text`는 shell script 본문이다.
- `default = flake-greeter`는 인자 없는 `nix build`의 기본 package를 정한다.

`pkgs.cowsay`를 개발 셸에만 넣고 package의 `runtimeInputs`에서 빼면 빌드 결과를 개발
셸 밖에서 실행할 때 실패할 수 있다. 개발 의존성과 런타임 의존성은 별도로 선언한다.

## 4.3 Nix 문자열 안의 shell 확장

다음 줄에는 Nix와 shell이 모두 `${...}` 문법을 사용한다.

파일: `<project-root>/flake.nix` (`packages.${system}.flake-greeter.text` 부분)

```nix
message="''${1:-Hello from a Nix flake!}"
```

Nix의 indented string `'' ... ''`에서 `''${`는 문자 `${`를 결과 script에 남긴다.
따라서 실제 실행되는 shell은 다음 코드를 받는다.

생성 파일: `/nix/store/<hash>-flake-greeter/bin/flake-greeter`
(Nix가 생성한 shell script의 본문 일부)

```bash
message="${1:-Hello from a Nix flake!}"
```

인자가 있으면 첫 번째 인자를, 없으면 기본 메시지를 사용한다. 앞의 작은따옴표 두 개를
빼면 Nix가 `1`을 Nix interpolation으로 해석하려 하여 평가 오류가 난다.

## 4.4 package 빌드와 실행

파일을 Git 추적 대상으로 만든 뒤 출력과 build를 확인한다.

```console
$ git add flake.nix
$ nix flake show
$ nix build
$ ./result/bin/flake-greeter
 __________________________
< Hello from a Nix flake! >
 --------------------------
```

인자도 전달할 수 있다.

```console
$ ./result/bin/flake-greeter "built as a package"
```

여기서 중요한 검증은 개발 셸에 들어가지 않고도 `cowsay`가 실행된다는 점이다.
`writeShellApplication`이 runtime dependency를 wrapper의 PATH에 연결한다.

이름 있는 package는 명시적으로 선택한다.

```console
$ nix build .#flake-greeter
```

`nix flake show`의 `packages.<system>.flake-greeter`와 명령의 `#flake-greeter`를
연결해서 읽는다.

## 4.5 app output 추가

package의 실행 파일을 기본 app으로 노출한다.

파일: `<project-root>/flake.nix` (`apps.${system}.default` 부분)

```nix
apps.${system}.default = {
  type = "app";
  program = "${self.packages.${system}.default}/bin/flake-greeter";
  meta.description = "Print a message with cowsay";
};
```

app의 핵심 field는 두 개다.

- `type`은 `"app"`이어야 한다.
- `program`은 Nix Store 안의 실행 파일 전체 경로여야 한다.

`${self.packages.${system}.default}`가 package의 Store path로 바뀌고, 뒤에 실제 실행
파일 경로를 붙인다. `meta.description`은 최신 Nix에서 사용할 수 있는 선택 설명이다.

실행할 Flake를 `.`로 명시하고, application 인자는 `--` 뒤에 둔다.

```console
$ nix run . -- "run as an app"
```

이름 있는 app을 만들었다면 `nix run .#name -- ...`으로 선택한다.

## 4.6 이름 있는 app

기본 app과 같은 package를 다른 이름으로 노출할 수도 있다.

파일: `<project-root>/flake.nix` (`apps.${system}` 부분)

```nix
apps.${system} = {
  default = {
    type = "app";
    program = "${self.packages.${system}.default}/bin/flake-greeter";
  };

  greet = {
    type = "app";
    program = "${self.packages.${system}.flake-greeter}/bin/flake-greeter";
  };
};
```

```console
$ nix run .#greet -- "named app"
```

동일한 실행 파일에 의미 없는 별칭을 많이 만들 필요는 없다. 여러 독립 실행 파일을
제공하거나 사용자에게 안정적인 공개 이름이 필요할 때 이름 있는 app을 사용한다.

## 4.7 개발 셸에도 자체 package 넣기

개발 중 `flake-greeter`를 바로 실행하려면 현재 Flake의 package를 개발 셸에 넣는다.

파일: `<project-root>/flake.nix` (`devShells.${system}.default` 부분)

```nix
devShells.${system}.default = pkgs.mkShellNoCC {
  packages = [
    pkgs.cowsay
    self.packages.${system}.default
  ];
};
```

```console
$ nix develop -c flake-greeter "available during development"
```

이 패턴은 “프로젝트가 만드는 프로그램”과 “프로젝트를 만드는 데 필요한 도구”를 한
개발 셸에서 함께 시험할 때 유용하다.

## Worked Example: 실행 실패 추적

다음 app은 평가되지만 실행 경로가 틀렸다.

파일: `<project-root>/flake.nix` (`apps.${system}.default`의 잘못된 예)

```nix
apps.${system}.default = {
  type = "app";
  program = "${self.packages.${system}.default}/bin/greeter";
};
```

진단 순서는 다음과 같다.

1. `nix flake show`가 성공하는지 확인한다. 성공하면 output schema 평가 단계는 지났다.
2. `nix build`로 package를 만든다.
3. `ls result/bin`으로 실제 실행 파일명을 확인한다.
4. `writeShellApplication.name`이 `flake-greeter`임을 확인한다.
5. app의 `program`을 `/bin/flake-greeter`로 수정한다.
6. `nix run . -- "fixed"`로 다시 검증한다.

평가 성공이 실행 파일의 존재까지 보장하지는 않는다. 실패 단계를 나누면 원인을 빨리
찾을 수 있다.

## 직접 해보기

1. 기본 메시지를 자신의 프로젝트 이름으로 바꾼다.
2. `apps.${system}.greet`를 추가하고 `nix run .#greet -- "hello"`로 실행한다.
3. `runtimeInputs`에서 `pkgs.cowsay`를 잠시 제거한 뒤 개발 셸 밖에서 package를
   실행하고, 실패 이유를 설명한 다음 복구한다.

## 흔한 오류

| 증상 | 원인 | 해결 |
|---|---|---|
| Nix가 shell `${1...}`을 평가하려 함 | `''${` 이스케이프 누락 | indented string의 escape 사용 |
| 개발 셸에서는 되고 build 결과는 실패 | runtime dependency 누락 | `runtimeInputs`에 package 추가 |
| `nix run`에서 파일이 없다고 나옴 | app의 `program` 경로 오류 | `result/bin`과 application `name` 확인 |
| app schema 오류 | `type = "app"` 또는 `program` 누락 | 공식 app schema에 맞춤 |

## 요약

- package는 빌드 결과, app은 실행할 Store 경로를 설명한다.
- `writeShellApplication`은 shell script와 runtime dependency를 하나의 package로 묶는다.
- 개발 셸의 package 목록은 runtime dependency 선언을 대신하지 않는다.
- 평가, build, 실행을 분리해 검증하면 app 경로 오류를 빠르게 찾을 수 있다.

## 공식 자료

- [`nix run`과 app schema](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-run.html)
- [`nix build`](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-build.html)
- [Nixpkgs `writeShellApplication`](https://nixos.org/manual/nixpkgs/stable/#trivial-builder-writeShellApplication)

[← 3장: 개발 셸에 `cowsay` 추가하기](./03-development-shells.md) ·
[목차](./index.md) · [5장: 검사, formatter, 여러 시스템 →](./05-checks-and-multi-system.md)
