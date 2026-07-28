# 3. 개발 셸에 `cowsay` 추가하기

## 학습 목표

1. 임시 package 실행과 프로젝트 개발 셸의 차이를 설명한다.
2. `devShells.<system>.default`에 Nixpkgs package를 추가한다.
3. 셸 진입과 비대화형 명령으로 환경을 검증한다.

## 3.1 “설치”의 범위를 먼저 정한다

Nix에서 package를 사용할 수 있게 만드는 방법은 여러 가지다.

| 목적 | 명령 또는 출력 | package가 보이는 범위 |
|---|---|---|
| 한 번 시험 | `nix shell nixpkgs#cowsay` | 해당 셸 프로세스 |
| 프로젝트 개발 | `devShells.<system>.default`와 `nix develop` | 해당 프로젝트 셸 |
| 사용자 프로필 | `nix profile install` | 해당 사용자 프로필 |
| NixOS 시스템 | `environment.systemPackages` | 시스템 구성 |

이 장의 “설치”는 시스템 전체 설치가 아니다. `flake.nix`에 개발 의존성을 선언하여
`nix develop`으로 연 셸의 `PATH`에 package를 제공한다. 프로젝트를 벗어나면 원래
환경으로 돌아온다.

## 3.2 Nixpkgs에서 package 확인하기

공식 nix.dev 첫 단계 튜토리얼도 눈에 보이는 예제로 `cowsay`를 사용한다. Flake를
작성하기 전에 Nixpkgs에서 package 이름을 확인할 수 있다.

```console
$ nix search nixpkgs cowsay
```

한 번만 실행해 보려면 다음처럼 한다.

```console
$ nix shell nixpkgs#cowsay --command cowsay "temporary shell"
 ___________________
< temporary shell >
 -------------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
```

ASCII 그림의 세부 모양은 package 버전에 따라 다를 수 있다. 중요한 결과는 호스트에
`cowsay`가 미리 없어도 명령이 실행된다는 점이다.

이 방식은 빠른 실험에는 좋지만 프로젝트 파일에 의존성이 남지 않는다. 이제 같은
package를 Flake output으로 선언한다.

## 3.3 `devShells` 출력 추가

1장의 `flake.nix`를 다음처럼 확장한다.

파일: `<project-root>/flake.nix` (전체)

```nix
{
  description = "A development shell with cowsay";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs =
    { nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      packages.${system}.default = pkgs.hello;

      devShells.${system}.default = pkgs.mkShellNoCC {
        packages = [ pkgs.cowsay ];
      };
    };
}
```

Apple Silicon macOS에서는 `system`을 `aarch64-darwin`으로 바꾼다.

각 부분의 책임은 다음과 같다.

- `nixpkgs.legacyPackages.${system}`은 해당 시스템의 Nixpkgs package 집합이다.
- `pkgs.cowsay`는 그 집합에서 `cowsay` package를 선택한다.
- `pkgs.mkShellNoCC`는 C compiler를 기본으로 넣지 않는 가벼운 개발 셸 derivation을
  만든다.
- `packages = [ ... ]`는 셸의 실행 환경에 넣을 package 목록이다.
- `devShells.${system}.default`는 인자 없는 `nix develop`의 첫 기본 경로다.

`legacyPackages`라는 이름에 “legacy”가 있지만 여기서는 Flake가 제공하는 시스템별
Nixpkgs package 집합에 접근하는 일반적인 경로로 사용한다. 이것이 package가 낡았다는
뜻은 아니다.

## 3.4 대화형으로 검증하기

출력 트리를 먼저 확인한다.

```console
$ git add flake.nix
$ nix flake show
```

현재 시스템 아래에 다음 두 출력이 보여야 한다.

```text
devShells
└───x86_64-linux
    └───default: development environment
packages
└───x86_64-linux
    └───default: package 'hello-...'
```

개발 셸에 들어가 package 위치와 실행을 확인한다.

```console
$ nix develop
$ command -v cowsay
/nix/store/...-cowsay-.../bin/cowsay

$ cowsay "declared by this project"
$ exit
```

Nix는 package를 Nix Store에 실현하고 개발 셸의 환경 변수에 연결한다. 프로젝트
디렉터리에 `cowsay` 실행 파일을 복사하지 않는다.

## 3.5 비대화형으로 검증하기

문서 예제와 CI에서는 셸을 직접 열지 않고 한 명령만 실행하는 편이 좋다.

```console
$ nix develop --command cowsay "checked without an interactive shell"
```

짧은 옵션 `-c`도 같은 목적에 사용할 수 있다.

```console
$ nix develop -c sh -c 'command -v cowsay && cowsay "ready"'
```

이 방식은 명령이 종료되면 개발 셸도 함께 끝나므로 자동 검증에 적합하다.

## 3.6 `shellHook`은 준비 알림에만 사용한다

셸 진입 시 안내를 표시하려면 `shellHook`을 추가할 수 있다.

파일: `<project-root>/flake.nix` (`devShells.${system}.default` 부분)

```nix
devShells.${system}.default = pkgs.mkShellNoCC {
  packages = [ pkgs.cowsay ];
  shellHook = ''
    cowsay "Flake development shell is ready"
  '';
};
```

`shellHook`은 편리하지만 다음 작업을 넣지 않는 편이 좋다.

- 사용자 홈 파일을 수정하는 작업
- 매번 네트워크에서 의존성을 내려받는 작업
- 데이터베이스를 지우거나 migration하는 작업
- 성공 여부를 예측하기 어려운 긴 bootstrap

개발 셸에 들어가는 것만으로 외부 상태가 바뀌면 재현성과 안전성이 떨어진다. 필요한
도구는 `packages`에 선언하고, 상태 변경은 별도 명령이나 script로 분리한다.

## 3.7 이름 있는 개발 셸

프로젝트에 문서용과 개발용 환경이 따로 필요하면 이름을 나눈다.

파일: `<project-root>/flake.nix` (`devShells.${system}` 부분)

```nix
devShells.${system} = {
  default = pkgs.mkShellNoCC {
    packages = [ pkgs.cowsay ];
  };

  docs = pkgs.mkShellNoCC {
    packages = [ pkgs.mdbook ];
  };
};
```

기본 셸과 이름 있는 셸을 각각 선택한다.

```console
$ nix develop
$ nix develop .#docs
```

이름을 지나치게 많이 만들면 프로젝트의 표준 진입점이 흐려진다. 대부분의 사용자가
써야 할 환경은 `default`로 두고, 목적이 분명한 환경만 추가한다.

## 3.8 package 추가 실습

`cowsay`와 함께 공식 튜토리얼에서 사용하는 `lolcat`을 추가한다.

파일: `<project-root>/flake.nix` (`devShells.${system}.default` 부분)

```nix
devShells.${system}.default = pkgs.mkShellNoCC {
  packages = [
    pkgs.cowsay
    pkgs.lolcat
  ];
};
```

검증 명령은 다음과 같다.

```console
$ nix develop -c sh -c 'cowsay "two packages" | lolcat'
```

두 package의 버전은 `flake.lock`이 가리키는 같은 Nixpkgs revision에서 선택된다.

## 직접 해보기

1. 개발 셸 밖과 안에서 `command -v cowsay` 결과를 비교한다.
2. `pkgs.lolcat`을 추가하고 `nix flake show`에서 output tree가 바뀌지 않는 이유를
   설명한다.
3. `devShells.${system}.tools`를 추가하고 `nix develop .#tools`로 선택한다.

## 흔한 오류

| 증상 | 원인 | 해결 |
|---|---|---|
| `nix develop`이 기본 셸을 못 찾음 | `devShells.<system>.default`가 없음 | 출력 이름과 system 확인 |
| `undefined variable 'cowsay'` | `cowsay`를 `pkgs.cowsay`로 선택하지 않음 | Nixpkgs package 집합에서 참조 |
| 셸 안에서도 command가 없음 | package가 실행 파일을 다른 이름으로 제공 | `nix search`, package metadata 확인 |
| 셸 진입 때마다 느리거나 상태가 바뀜 | `shellHook`에서 bootstrap 수행 | 선언과 상태 변경 명령 분리 |

## 요약

- `nix shell`은 빠른 시험, `nix develop`은 저장소에 선언한 개발 환경에 적합하다.
- `devShells.<system>.default`는 인자 없는 `nix develop`의 표준 진입점이다.
- Nixpkgs package는 `pkgs.cowsay`처럼 선택해 `packages` 목록에 넣는다.
- `nix develop --command`로 개발 셸을 자동 검증할 수 있다.

## 공식 자료

- [임시 Nix 셸과 `cowsay`](https://nix.dev/tutorials/first-steps/ad-hoc-shell-environments.html)
- [`nix develop`](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-develop.html)
- [Nixpkgs 개발 셸 helper](https://nixos.org/manual/nixpkgs/stable/#sec-pkgs-mkShell)

[← 2장: 입력과 `flake.lock`](./02-inputs-and-locks.md) · [목차](./index.md) ·
[4장: 패키지와 앱 만들기 →](./04-packages-and-apps.md)
