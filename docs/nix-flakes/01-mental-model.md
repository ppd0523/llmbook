# 1. Flake의 역할과 출력 트리

## 학습 목표

1. Flake를 입력과 출력의 관계로 설명한다.
2. Flake reference와 출력 속성 경로를 구분한다.
3. `nix flake show`에서 현재 시스템의 기본 package를 찾는다.

## 1.1 Flake가 추가하는 경계

Nix 표현식은 원래도 package와 개발 환경을 만들 수 있다. 문제는 다른 저장소의 Nix
코드를 사용할 때다.

- 의존 소스의 위치와 revision을 어떤 방식으로 기록할 것인가?
- 저장소가 package, 개발 셸, 앱 중 무엇을 제공하는지 어떻게 찾을 것인가?
- 명령이 기본값으로 선택할 출력의 이름을 어떻게 맞출 것인가?

Flake는 이 세 문제에 공통 경계를 제공한다.

```text
input URL                     output schema
github:NixOS/nixpkgs/...      packages.<system>.default
           │                  devShells.<system>.default
           ▼                  apps.<system>.default
      flake.lock                     ▲
           │                         │
           └────── outputs 함수 ─────┘
```

`flake.nix`는 입력의 위치와 출력 계산 방법을 선언한다. `flake.lock`은 입력 URL을
실제 revision과 content hash로 해석한 결과를 고정한다. `outputs` 함수가 반환한 속성
트리는 `nix build`, `nix develop`, `nix run` 같은 명령이 탐색한다.

공식 문서는 Flake를 루트에 `flake.nix`를 가진 파일 시스템 트리이자, 입력과 출력을
표준 구조로 선언하는 단위로 설명한다. Flake가 Nix 언어 자체를 대체하는 것은 아니다.

## 1.2 세 가지를 분리해서 읽기

다음 `flake.nix`는 Nixpkgs의 GNU Hello package를 기본 package로 내보낸다.

```nix
{
  description = "A first flake";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs =
    { nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      packages.${system}.default = pkgs.hello;
    };
}
```

코드를 세 부분으로 나누면 읽기 쉽다.

1. `description`은 사람을 위한 설명이다.
2. `inputs.nixpkgs.url`은 Nixpkgs를 어디에서 가져올지 선언한다.
3. `outputs`는 잠긴 입력을 받아 package 출력 트리를 반환하는 함수다.

현재 머신이 Apple Silicon macOS라면 예제의 시스템은 `aarch64-darwin`, Intel macOS면
`x86_64-darwin`으로 바꾼다. 5장에서 이 하드코딩을 제거한다.

## 1.3 `self`와 나머지 입력

`outputs` 함수에 전달되는 속성 집합에는 `self`와 선언된 input이 들어온다.

```nix
outputs = { self, nixpkgs }: {
  # ...
};
```

- `self`는 현재 Flake와 그 output을 참조한다.
- `nixpkgs`는 `inputs.nixpkgs`가 잠긴 뒤 평가된 Flake다.
- `{ nixpkgs, ... }`의 `...`는 사용하지 않는 추가 인자를 허용한다.

지금 예제는 `self`를 사용하지 않으므로 `{ nixpkgs, ... }`로 받았다. 4장에서 app이
현재 Flake의 package를 가리킬 때 `self.packages.${system}.default`를 사용한다.

## 1.4 Flake reference와 속성 경로

다음 명령에서 `.`과 `hello`는 역할이 다르다.

```console
$ nix build .#hello
```

- `.`은 현재 디렉터리의 Flake를 가리키는 reference다.
- `#hello`는 그 Flake에서 선택할 출력 이름이다.
- 현재 시스템이 `x86_64-linux`라면 `nix build`는 우선
  `packages.x86_64-linux.hello` 같은 경로를 찾는다.

원격 Flake도 같은 모양으로 참조한다.

```console
$ nix build github:NixOS/nixpkgs/nixos-26.05#hello
```

reference는 소스의 위치를 말하고, `#` 뒤는 그 소스가 제공하는 출력의 이름을 말한다.
이 둘을 분리해 읽으면 긴 명령도 추적할 수 있다.

## 1.5 첫 출력 확인

빈 디렉터리에서 예제를 실습한다.

```console
$ mkdir first-flake
$ cd first-flake
$ git init
```

앞의 코드를 `flake.nix`로 저장하고 Git에 추가한다.

```console
$ git add flake.nix
$ nix flake show
```

처음 실행할 때 Nix는 `flake.lock`을 만들 수 있다. 자세한 의미는 2장에서 다룬다.
출력에는 다음 경로가 보여야 한다.

```text
packages
└───x86_64-linux
    └───default: package 'hello-...'
```

기본 package를 빌드하고 실행한다.

```console
$ nix build
$ ./result/bin/hello
Hello, world!
```

`result`는 Nix Store의 빌드 결과를 가리키는 심볼릭 링크다. package 자체가 현재
디렉터리에 복사된 것은 아니다.

## 1.6 명령은 출력 트리를 탐색한다

자주 사용하는 기본 경로를 먼저 기억한다.

| 명령 | 첫 번째 기본 출력 |
|---|---|
| `nix build` | `packages.<system>.default` |
| `nix develop` | `devShells.<system>.default` |
| `nix run` | `apps.<system>.default` |
| `nix fmt` | `formatter.<system>` |

모든 명령이 임의의 속성을 같은 방식으로 처리하는 것은 아니다. 예를 들어 app은
`type = "app"`과 Nix Store 안의 실행 파일을 가리키는 `program`이 필요하다. 명령이
무엇을 기대하는지는 해당 명령의 reference에서 확인한다.

## 직접 해보기

1. `packages.${system}.default`를 `packages.${system}.hello`로 바꾸고
   `nix build .#hello`를 실행한다.
2. 이름만 바꾼 상태에서 인자 없는 `nix build`가 왜 실패하는지 출력 경로로 설명한다.
3. 자신의 시스템 문자열을 `nix eval --impure --raw --expr builtins.currentSystem`으로
   확인하고 예제 값과 비교한다.

## 흔한 오류

| 증상 | 원인 | 해결 |
|---|---|---|
| `does not provide attribute packages...default` | 기본 package 이름이 없음 | `default`를 추가하거나 `.#name` 지정 |
| 현재 시스템 출력이 없다는 오류 | 다른 system만 선언 | 현재 system 문자열로 출력 생성 |
| 새 파일을 찾지 못함 | Git 저장소에서 파일이 추적되지 않음 | `git add` 후 다시 평가 |
| `result/bin/...`이 없음 | package의 실제 실행 파일명이 다름 | `ls result/bin` 또는 package metadata 확인 |

## 요약

- Flake는 input의 위치·잠금과 output의 표준 이름을 한 경계에 모은다.
- Flake reference와 `#` 뒤의 출력 이름은 서로 다른 축이다.
- `nix flake show`는 명령을 실행하기 전에 출력 트리를 확인하는 첫 도구다.
- 출력에는 보통 `<system>` 축이 있으며 현재 머신과 맞아야 한다.

## 공식 자료

- [Flakes 개념](https://nix.dev/concepts/flakes.html)
- [`nix flake show`](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-flake-show.html)
- [Nix installable과 출력 탐색](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix.html#installables)

[목차](./index.md) · [2장: 입력과 `flake.lock` →](./02-inputs-and-locks.md)
