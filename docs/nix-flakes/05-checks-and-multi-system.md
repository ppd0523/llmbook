# 5. 검사, formatter, 여러 시스템

## 학습 목표

1. 반복되는 시스템별 출력을 `genAttrs`로 생성한다.
2. `formatter`와 `checks` 출력을 추가한다.
3. 현재 시스템의 build 검사와 전체 시스템의 평가 검사를 구분한다.

## 5.1 system 하드코딩의 한계

앞 장까지는 설명을 단순하게 유지하려고 다음 값을 고정했다.

파일: `<project-root>/flake.nix` (`outputs`의 `let` 바인딩 일부)

```nix
system = "x86_64-linux";
```

이 Flake는 Apple Silicon macOS나 ARM Linux에서 기본 출력을 제공하지 않는다.
package와 app은 플랫폼마다 다른 binary와 dependency를 가질 수 있으므로 출력 경로에
system 축이 필요하다.

일반적인 네 플랫폼을 목록으로 선언한다.

파일: `<project-root>/flake.nix` (`outputs`의 `let` 바인딩 일부)

```nix
systems = [
  "x86_64-linux"
  "aarch64-linux"
  "x86_64-darwin"
  "aarch64-darwin"
];
```

모든 package가 이 네 플랫폼을 지원한다는 뜻은 아니다. 이 예제의 `cowsay`,
`nixfmt`, shell application은 해당 플랫폼에서 사용할 수 있다는 가정으로 출력을
만든다. 실제 프로젝트는 지원하고 검증할 플랫폼만 명시한다.

Nixpkgs 26.05 평가에서는 `x86_64-darwin`이 지원되는 마지막 release라는 경고가
표시된다. 이 자료는 현재 stable 기준의 네 플랫폼을 모두 보여 주지만, 다음 release로
올릴 때는 Nixpkgs release notes를 확인하고 지원 목록을 다시 결정해야 한다.

## 5.2 `genAttrs`로 시스템별 출력 만들기

Nixpkgs library의 `genAttrs`는 이름 목록과 값 생성 함수를 받아 속성 집합을 만든다.

파일: `<project-root>/flake.nix` (`outputs`의 `let` 바인딩 일부)

```nix
forAllSystems = nixpkgs.lib.genAttrs systems;
```

다음 식을 평가하면 각 system 이름을 key로 가진 속성 집합이 된다.

```nix
forAllSystems (system: "value for ${system}")
```

개념적인 결과는 다음과 같다.

```nix
{
  x86_64-linux = "value for x86_64-linux";
  aarch64-linux = "value for aarch64-linux";
  x86_64-darwin = "value for x86_64-darwin";
  aarch64-darwin = "value for aarch64-darwin";
}
```

`packages = forAllSystems (...)`로 만들면 결과 경로는 자연스럽게
`packages.<system>.*`가 된다.

## 5.3 package와 app을 여러 시스템으로 확장

파일: `<project-root>/flake.nix` (`outputs`의 `packages`와 `apps` 부분)

```nix
packages = forAllSystems (
  system:
  let
    pkgs = nixpkgs.legacyPackages.${system};
  in
  rec {
    flake-greeter = pkgs.writeShellApplication {
      name = "flake-greeter";
      runtimeInputs = [ pkgs.cowsay ];
      text = ''
        message="''${1:-Hello from a Nix flake!}"
        cowsay "$message"
      '';
    };
    default = flake-greeter;
  }
);

apps = forAllSystems (system: {
  default = {
    type = "app";
    program = "${self.packages.${system}.default}/bin/flake-greeter";
    meta.description = "Print a message with cowsay";
  };
});
```

각 반복 안에서 같은 `system`으로 Nixpkgs, package, app을 연결한다. 예를 들어
`apps.aarch64-darwin.default`가 실수로 `packages.x86_64-linux.default`를 가리키지
않도록 system 값을 끝까지 전달한다.

## 5.4 formatter 출력

Flake는 프로젝트가 사용할 formatter도 출력으로 제공할 수 있다.

파일: `<project-root>/flake.nix` (`outputs`의 `formatter` 부분)

```nix
formatter = forAllSystems (system: nixpkgs.legacyPackages.${system}.nixfmt);
```

Nixpkgs 25.11부터 공식 `nixfmt` package는 `pkgs.nixfmt`로 제공된다. 예전의 임시
속성명 `nixfmt-rfc-style` 대신 현재 stable 이름을 사용한다.

파일을 지정해 실행한다.

```console
$ nix fmt flake.nix
```

`nix fmt`는 가장 가까운 Flake의 `formatter.<현재-system>`을 찾아 실행한다.
formatter가 코드를 바꿀 수 있으므로 실행 뒤 diff를 확인한다.

```console
$ git diff -- flake.nix
```

개발 셸에서도 직접 formatter를 사용하려면 `pkgs.nixfmt`를 `packages` 목록에 추가할
수 있다. Flake output과 개발 셸 package는 서로 다른 진입점을 제공한다.

## 5.5 check 출력

먼저 package 자체를 check로 재사용한다.

파일: `<project-root>/flake.nix` (`outputs`의 `checks` 부분)

```nix
checks = forAllSystems (system: {
  package = self.packages.${system}.default;
});
```

`nix flake check`는 알려진 Flake 출력이 올바른 종류인지 평가하고 현재 시스템의
`checks.<system>.*` derivation을 빌드한다. package를 check에 넣으면 기본 빌드가
검증 루프에 포함된다.

실제 실행 결과도 검사하려면 `runCommand`를 추가한다.

파일: `<project-root>/flake.nix` (`outputs`의 `checks` 부분)

```nix
checks = forAllSystems (
  system:
  let
    pkgs = nixpkgs.legacyPackages.${system};
    greeter = self.packages.${system}.default;
  in
  {
    package = greeter;

    greeting = pkgs.runCommand "flake-greeter-check" {
      nativeBuildInputs = [
        greeter
        pkgs.gnugrep
      ];
    } ''
      flake-greeter "checked" > "$out"
      grep -q "checked" "$out"
    '';
  }
);
```

이 check는 다음을 검증한다.

1. `flake-greeter`가 빌드된다.
2. wrapper가 `cowsay` runtime dependency를 찾는다.
3. 인자 `"checked"`가 실제 출력에 포함된다.

`$out`은 check derivation의 결과 파일이다. `grep`의 사용도 암묵적인 host 의존성이
되지 않도록 `pkgs.gnugrep`를 `nativeBuildInputs`에 넣었다.

## 5.6 완성형 `flake.nix`

지금까지의 출력을 합치면 다음과 같다.

파일: `docs/nix-flakes/assets/flake-greeter/flake.nix` (전체)

```nix
{
  description = "A small multi-system Flake learning project";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs =
    {
      self,
      nixpkgs,
    }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in
    {
      packages = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        rec {
          flake-greeter = pkgs.writeShellApplication {
            name = "flake-greeter";
            runtimeInputs = [ pkgs.cowsay ];
            text = ''
              message="''${1:-Hello from a Nix flake!}"
              cowsay "$message"
            '';
          };
          default = flake-greeter;
        }
      );

      apps = forAllSystems (system: {
        default = {
          type = "app";
          program = "${self.packages.${system}.default}/bin/flake-greeter";
          meta.description = "Print a message with cowsay";
        };
      });

      devShells = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        {
          default = pkgs.mkShellNoCC {
            packages = [
              pkgs.cowsay
              pkgs.nixfmt
              self.packages.${system}.default
            ];
            shellHook = ''
              cowsay "Flake development shell is ready"
            '';
          };
        }
      );

      formatter = forAllSystems (system: nixpkgs.legacyPackages.${system}.nixfmt);

      checks = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          greeter = self.packages.${system}.default;
        in
        {
          package = greeter;
          greeting = pkgs.runCommand "flake-greeter-check" {
            nativeBuildInputs = [
              greeter
              pkgs.gnugrep
            ];
          } ''
            flake-greeter "checked" > "$out"
            grep -q "checked" "$out"
          '';
        }
      );
    };
}
```

같은 파일이 [`assets/flake-greeter/flake.nix`](./assets/flake-greeter/flake.nix)에
있다.

## 5.7 검증 순서

가벼운 평가에서 실제 실행으로 범위를 넓힌다.

```console
$ nix flake show
$ nix fmt flake.nix
$ nix flake check
$ nix build
$ nix run . -- "all checks passed"
```

현재 머신에서 다른 운영체제의 derivation을 build할 수 없는 것이 보통이다. 모든
선언한 system의 출력 schema를 평가만 하려면 다음 명령을 사용한다.

```console
$ nix flake check --all-systems --no-build
```

이 명령이 성공해도 다른 system에서 실제 build와 실행이 성공했다는 뜻은 아니다.
지원한다고 선언한 플랫폼은 해당 플랫폼의 CI runner나 실제 머신에서
`nix flake check`로 build해야 한다.

## 5.8 중복 제거의 한계

모든 것을 `forAllSystems` 안에 넣는다고 좋은 설계가 되는 것은 아니다.

- Linux에만 있는 package는 `lib.optional pkgs.stdenv.isLinux` 같은 조건이 필요하다.
- system과 무관한 NixOS module은 `nixosModules`처럼 다른 output 축에 둔다.
- 플랫폼마다 의미가 다른 shell hook을 억지로 하나로 합치지 않는다.
- 지원하지 않는 플랫폼을 목록에 넣어 “지원하는 것처럼 보이게” 하지 않는다.

추상화의 목적은 중복을 숨기는 것이 아니라 같은 계약을 같은 방식으로 생성하는 것이다.

## 직접 해보기

1. `systems`에서 현재 system만 남긴 뒤 `nix flake show`의 차이를 관찰한다.
2. `greeting` check의 검색 문자열을 `"missing"`으로 바꾸어 실패시키고 build log를
   확인한 뒤 복구한다.
3. `formatter`를 제거했을 때 `nix fmt flake.nix`의 오류를 output tree로 설명한다.

## 흔한 오류

| 증상 | 원인 | 해결 |
|---|---|---|
| 다른 system app이 엉뚱한 binary를 참조 | package 경로 system 하드코딩 | 같은 반복 변수 전달 |
| `nix fmt`가 formatter를 못 찾음 | `formatter.<system>` 누락 | 현재 system 출력 추가 |
| check가 host의 `grep`에 우연히 의존 | 검사 도구 미선언 | `nativeBuildInputs`에 추가 |
| `--all-systems` build 실패 | host가 다른 플랫폼 derivation을 build할 수 없음 | `--no-build` 평가와 플랫폼별 CI 분리 |

## 요약

- system별 출력은 실제 지원할 플랫폼만 명시하고 같은 system 값을 끝까지 전달한다.
- `formatter.<system>`은 프로젝트의 표준 서식 도구를 제공한다.
- `checks.<system>.*`는 build와 실행 검사를 `nix flake check`에 연결한다.
- 전체 시스템 평가 성공과 플랫폼별 실제 build 성공은 다른 검증 단계다.

## 공식 자료

- [`nix flake check`](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-flake-check.html)
- [`nix fmt`](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-fmt.html)
- [Nixpkgs 25.11 formatter 변경](https://nixos.org/manual/nixpkgs/stable/release-notes)
- [`lib.genAttrs`](https://nixos.org/manual/nixpkgs/stable/#function-library-lib.attrsets.genAttrs)

[← 4장: 패키지와 앱 만들기](./04-packages-and-apps.md) · [목차](./index.md) ·
[6장: 운영 워크플로와 문제 해결 →](./06-workflow-and-troubleshooting.md)
