# 5. NixOS·Home Manager의 모듈 시스템

## 학습 목표

1. module, option declaration, option definition을 구분한다.
2. 여러 module의 정의가 type에 따라 합쳐지는 방식을 이해한다.
3. `imports`, `config`, `pkgs`, `lib`를 읽고 흔한 충돌을 진단한다.

## 5.1 Nix 언어와 module system은 같은 층이 아니다

Nix 언어에는 문자열, 함수, 속성 집합 같은 일반 규칙이 있다. Module system은 그
언어로 구현된 별도의 구성 규약이다. NixOS와 Home Manager가 이 규약을 사용한다.

```text
Nix 언어
└── 함수와 속성 집합
    └── Nixpkgs module system
        ├── NixOS modules
        └── Home Manager modules
```

따라서 다음 코드는 Nix 문법상 속성 집합을 반환하는 함수이면서, module system
문맥에서는 option을 정의하는 module이다.

```nix
{ pkgs, ... }:
{
  programs.git.enable = true;
  home.packages = [ pkgs.ripgrep ];
}
```

이 파일만 `nix eval`한다고 Home Manager 설정이 되는 것은 아니다. Home Manager의
module evaluator가 알려진 option 선언들과 함께 평가해야 한다.

## 5.2 option은 설정 API다

Module system은 option에 이름, type, default, 설명 등을 선언할 수 있다.

```nix
options.services.example.enable = lib.mkEnableOption "example service";
```

사용자는 그 option의 값을 정의한다.

```nix
services.example.enable = true;
```

두 역할을 구분한다.

- **declaration**: `services.example.enable`이라는 option이 존재하며 boolean이라는
  계약을 만든다.
- **definition**: 이 구성에서는 값을 `true`로 하겠다고 정한다.

대부분의 사용자는 NixOS와 Home Manager가 이미 선언한 option에 값을 정의한다.
직접 module을 만들 때만 option declaration을 작성하는 경우가 많다.

존재하지 않는 option 이름을 쓰거나 type이 맞지 않으면 평가 단계에서 오류가 난다.
오타를 조용히 무시하지 않는 것이 module system의 큰 장점이다.

## 5.3 여러 파일의 정의는 type 규칙으로 합쳐진다

파일: `base.nix`

```nix
{ pkgs, ... }:
{
  environment.systemPackages = [ pkgs.git ];
}
```

파일: `tools.nix`

```nix
{ pkgs, ... }:
{
  environment.systemPackages = [ pkgs.ripgrep ];
}
```

두 module을 함께 평가하면 list type인 이 option은 보통 두 목록을 연결한다.

```nix
environment.systemPackages = [
  pkgs.git
  pkgs.ripgrep
];
```

이것은 단순 속성 집합 연산자 `//`의 오른쪽 덮어쓰기와 다르다. Module system은
option declaration에 기록된 type과 merge 규칙을 사용한다.

반면 boolean이나 문자열 같은 단일 값을 서로 다르게 두 번 정의하면 충돌 오류가
날 수 있다.

```nix
# a.nix
{ services.openssh.enable = true; }

# b.nix
{ services.openssh.enable = false; }
```

이 문제를 만났을 때 곧바로 `lib.mkForce`로 덮지 않는다. 먼저 왜 두 파일이 같은
option을 서로 다르게 소유하는지 정리한다.

## 5.4 `imports`는 module graph를 만든다

```nix
{ ... }:
{
  imports = [
    ./hardware.nix
    ./networking.nix
    ./users.nix
  ];
}
```

`imports`에 들어간 각 파일은 같은 module evaluation에 참여한다. 모든 definition을
모은 뒤 type 검사와 merge가 일어난다.

일반 `import`와 비교한다.

| 구문 | 하는 일 |
|---|---|
| `import ./value.nix` | 파일의 표현식을 즉시 평가해 값 반환 |
| `imports = [ ./module.nix ];` | 파일을 module graph에 등록해 함께 평가 |

보통 구성 파일을 나눌 때는 `imports`를 쓴다. `import`로 module 함수에 인자를 직접
전달하는 고급 패턴도 있지만, module system이 제공하는 인자와 merge를 우회하지
않는지 이해한 뒤 사용한다.

## 5.5 module 인자의 출처

```nix
{
  config,
  lib,
  pkgs,
  ...
}:
{
  # ...
}
```

| 인자 | 의미 |
|---|---|
| `config` | 모든 module definition을 합친 최종 option 값 |
| `options` | 평가 중 알려진 option declaration |
| `pkgs` | 이 구성이 선택한 Nixpkgs package 집합 |
| `lib` | `mkIf`, `mkDefault`, type 등 Nixpkgs library |
| `modulesPath` | NixOS module 디렉터리 등 evaluator가 제공하는 추가 값 |
| `...` | 사용하지 않는 다른 module 인자 허용 |

NixOS와 Home Manager는 비슷한 이름의 인자를 제공하지만 서로 다른 module
evaluation이다. Home Manager를 NixOS module로 통합하면 `osConfig`처럼 시스템
구성에 접근하는 별도 인자가 제공되기도 한다.

Flake의 `inputs`는 기본 module 인자가 아니다. 바깥에서 `specialArgs` 또는 Home
Manager의 `extraSpecialArgs`로 전달한 경우에만 `{ inputs, ... }:`로 받을 수 있다.

## 5.6 `config`를 읽는 법

다음 module은 다른 곳에서 정의된 option을 조건으로 package를 추가한다.

```nix
{ config, lib, pkgs, ... }:
{
  environment.systemPackages = lib.mkIf config.programs.zsh.enable [
    pkgs.starship
  ];
}
```

- `config.programs.zsh.enable`: module 전체를 합친 최종 값 조회
- `lib.mkIf 조건 값`: 조건이 참일 때 definition을 module merge에 참여시킴

일반 `if ... then ... else ...`도 값 계산에 쓸 수 있다.

```nix
environment.systemPackages =
  if config.programs.zsh.enable then
    [ pkgs.starship ]
  else
    [ ];
```

`lib.mkIf`는 여러 option definition 묶음을 조건부로 제공할 때 특히 유용하며 module
system의 재귀 평가를 고려해 구현되어 있다.

## 5.7 우선순위는 최후의 조정 도구다

기존 module의 default를 제안하려면 다음 패턴을 볼 수 있다.

```nix
services.example.port = lib.mkDefault 8080;
```

사용자의 일반 definition은 이 default보다 우선할 수 있다. 반대로 `lib.mkForce`는
낮은 우선순위 definition을 버리고 강제로 선택하는 데 사용한다.

| 도구 | 의미 | 입문자 기준 |
|---|---|---|
| `lib.mkDefault` | 다른 일반 정의가 덮을 수 있는 기본값 | 재사용 module의 default |
| 일반 `=` | 보통의 사용자 definition | 먼저 사용 |
| `lib.mkForce` | 다른 낮은 우선순위 definition 배제 | 원인을 안 뒤 제한적으로 사용 |
| `lib.mkBefore` / `mkAfter` | list 등에서 merge 순서 조정 | 순서가 의미 있을 때만 |

충돌 오류는 설계상 소유권이 겹쳤다는 신호일 수 있다. 강제 override 전에 `imports`
중복, host별 파일, 공통 module을 점검한다.

## 5.8 NixOS option과 Home Manager option은 별도 API다

이름이 같아 보여도 evaluator와 효과가 다를 수 있다.

```nix
# NixOS module
programs.zsh.enable = true;
users.users.alice.shell = pkgs.zsh;
```

```nix
# Home Manager module
programs.zsh.enable = true;
programs.zsh.shellAliases.ll = "ls -la";
```

NixOS option은 zsh package와 시스템 integration, login shell 같은 시스템 책임을
맡는다. Home Manager option은 특정 사용자의 `.zshrc`, alias, plugin 등을 생성한다.
두 option이 자동으로 서로의 설정을 완성해 주지는 않는다.

option이 어느 세계에 속하는지는 각 검색 페이지에서 확인한다.

- [NixOS options](https://search.nixos.org/options)
- [Home Manager options](https://nix-community.github.io/home-manager/options.html)

검색할 때 option의 type, default, 설명, 선언 source를 함께 본다.

## 5.9 오류를 읽는 순서

### option이 존재하지 않음

```text
The option `programs.example.foo` does not exist.
```

1. 철자와 대소문자를 확인한다.
2. NixOS option을 Home Manager에 썼거나 그 반대인지 확인한다.
3. option을 선언하는 외부 module을 `imports`에 추가했는지 확인한다.
4. 현재 잠긴 release에 그 option이 실제로 있는지 확인한다.

### type 불일치

```text
expected a list but found a string
```

option 검색 결과의 type을 본다.

```nix
# 잘못된 예
home.packages = "git";

# 올바른 예
home.packages = [ pkgs.git ];
```

### 서로 충돌하는 definition

오류 trace에서 “defined multiple times” 주변의 파일 경로를 찾는다. 어느 module이
그 option을 소유해야 하는지 정하고 중복 definition을 제거하거나 의도적인
우선순위를 지정한다.

### trace가 너무 짧음

평소에는 짧은 오류부터 읽고 필요할 때만 전체 trace를 본다.

```console
$ nixos-rebuild build --show-trace
$ home-manager build --show-trace
```

Flake를 사용하면 실제 명령에 `--flake <경로>#<이름>`을 덧붙인다.

## 직접 해보기

다음 module을 구성 요소별로 설명한다.

```nix
{ config, lib, pkgs, ... }:
{
  imports = [ ./git.nix ];

  home.packages = [
    pkgs.ripgrep
  ];

  programs.starship.enable =
    lib.mkDefault config.programs.bash.enable;
}
```

확인할 항목:

1. 함수 인자와 반환값은 무엇인가?
2. `imports`와 `import` 중 어느 것인가?
3. `pkgs.ripgrep`의 출처는 무엇인가?
4. `config.programs.bash.enable`은 어느 시점의 값인가?
5. 다른 module이 `programs.starship.enable = false;`를 일반 정의하면 어느 쪽이
   우선하는가?

답: module 인자 집합을 받아 definition 집합을 반환한다. `git.nix`를 module graph에
추가한다. `ripgrep`은 주입된 Nixpkgs package 집합에서 온다. `config`는 합쳐진 최종
구성이다. 일반 definition이 `mkDefault`보다 우선한다.

## 요약

- Module system은 Nix 언어 위에서 option 선언, type 검사, merge를 제공한다.
- 사용자는 대부분 이미 선언된 option의 값을 정의한다.
- `imports`는 module graph를 만들고, 일반 `import`는 파일의 값을 반환한다.
- `config`는 전체 module을 합친 결과이고 `pkgs`는 선택된 package 집합이다.
- NixOS option과 Home Manager option은 별도 검색 공간과 적용 범위를 가진다.

## 공식 자료

- [nix.dev Module system](https://nix.dev/tutorials/module-system/)
- [NixOS module 구조](https://nixos.org/manual/nixos/stable/#sec-writing-modules)
- [NixOS option 검색](https://search.nixos.org/options)
- [Home Manager option 검색](https://nix-community.github.io/home-manager/options.html)

[← 4장](./04-shells-and-packages.md) · [목차](./index.md) ·
[6장: NixOS와 Home Manager에 연결하기 →](./06-nixos-and-home-manager.md)
