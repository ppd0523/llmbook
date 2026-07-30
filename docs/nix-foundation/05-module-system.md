# 5. NixOS·Home Manager의 모듈 시스템

## 학습 목표

1. module과 option을 자기 말로 설명한다.
2. option declaration, option definition, 최종 `config`를 구분한다.
3. option의 type, default, 설명과 merge 규칙을 읽는다.
4. `mkOption`, `mkIf`, `mkDefault` 같은 `mk...` helper의 역할을 구분한다.
5. 하나의 module이 사용자용 option을 실제 package·service 설정으로 바꾸는 과정을
   이해한다.
6. `imports`, `config`, `pkgs`, `lib`를 읽고 흔한 충돌을 진단한다.

## 5.1 먼저 한 문장으로 구분한다

**module은 전체 구성에 참여하는 설정 조각이고, option은 여러 module이 값을
주고받는 이름과 type이 있는 설정 접점이다.**

처음에는 다음 네 단어를 한 묶음으로 이해하면 된다.

| 용어 | 질문 | 짧은 답 |
|---|---|---|
| module | 누가 설정에 참여하는가? | option을 선언하거나 정의하는 구성 조각 |
| option | 무엇을 설정할 수 있는가? | 이름·type·문서·merge 규칙이 있는 설정 API |
| declaration | 어떤 값이 허용되는가? | option의 이름과 계약을 등록 |
| definition | 이 구성에서 어떤 값을 쓸 것인가? | 선언된 option에 실제 값을 제공 |

예를 들어 `services.openssh.enable`은 option의 **이름**이다.

```nix
services.openssh.enable = true;
```

이 한 줄이 module이고 `services.openssh.enable`이 module인 것은 아니다. 이 한 줄을
포함하는 파일 전체가 보통 하나의 module이며, 이 줄은 option에 `true`를 제공하는
definition이다. 해당 option을 선언한 OpenSSH module은 최종 값을 읽고 package,
systemd service, 설정 파일 같은 더 낮은 수준의 option을 정의한다.

다음처럼 생각하면 관계가 선명해진다.

```text
여러 module
  ├─ option declaration: 이름·type·default·설명
  ├─ option definition: 각 파일이 제안한 실제 값
  └─ imports: 함께 평가할 다른 module
             │
             ▼
      우선순위 적용 → type 검사 → type별 merge
             │
             ▼
       최종 config(모든 option의 결정된 값)
             │
             ▼
    package·파일·service·사용자 환경을 만드는 구성
```

module은 package와도 다르다. `pkgs.openssh`는 Store에 만들 프로그램이고,
`services.openssh.enable`을 선언·구현하는 module은 그 프로그램을 어떤 설정으로
실행할지 구성한다. option은 shell 명령이나 Nix 변수도 아니다. Module system이
추적하고 검사하는 구성상의 주소다.

## 5.2 Nix 언어와 module system은 같은 층이 아니다

Nix 언어에는 문자열, 함수, 속성 집합 같은 일반 규칙이 있다. Module system은 그
언어로 구현된 별도의 구성 규약이다. NixOS와 Home Manager가 이 규약을 사용한다.

```text
Nix 언어
└── 함수와 속성 집합
    └── Nixpkgs module system
        ├── NixOS modules
        └── Home Manager modules
```

가장 흔한 module 파일은 module system이 제공하는 인자 집합을 받아 속성 집합을
반환하는 함수다.

```nix
{ pkgs, ... }:
{
  programs.git.enable = true;
  home.packages = [ pkgs.ripgrep ];
}
```

Nix 문법으로만 보면 이 코드는 함수다. Home Manager evaluator가 호출하면 알려진
option에 값을 제공하는 module이 된다. 이 파일만 일반 값처럼 `nix eval`한다고 Home
Manager 설정이 되지는 않는다. Module system이 인자를 제공하고 다른 module과 함께
평가해야 한다.

완전한 module의 골격은 다음과 같다.

```nix
{
  config,
  lib,
  pkgs,
  ...
}:
{
  imports = [
    # 함께 평가할 module
  ];

  options = {
    # 이 module이 공개하는 option declaration
  };

  config = {
    # 이 module이 제공하는 option definition
  };
}
```

사용자의 `configuration.nix`나 `home.nix`처럼 option을 **정의만** 하는 module은
`config = { ... };`를 생략한 짧은 형식으로 흔히 쓴다.

```nix
{ pkgs, ... }:
{
  programs.git.enable = true;
  environment.systemPackages = [ pkgs.ripgrep ];
}
```

반면 같은 module에서 `options`를 선언한다면 definition은 `config` 아래에 명시해
두 영역을 구분한다.

## 5.3 option은 type이 있는 설정 API다

Option declaration은 “이 경로에 어떤 값을 넣을 수 있는가”라는 계약이다. 보통
`options` 아래에서 `lib.mkOption` 또는 전용 helper로 선언한다.

```nix
{ lib, ... }:
{
  options.services.example = {
    enable = lib.mkEnableOption "example service";

    port = lib.mkOption {
      type = lib.types.port;
      default = 8080;
      example = 9090;
      description = "TCP port used by the example service.";
    };

    tags = lib.mkOption {
      type = lib.types.listOf lib.types.str;
      default = [ ];
      description = "Labels attached to the example service.";
    };
  };
}
```

각 항목은 다음 역할을 한다.

| 항목 | 의미 | 실행 결과에 직접 포함되는가? |
|---|---|---|
| option 경로 | `services.example.port` 같은 공개 이름 | 이 이름으로 값을 읽고 정의 |
| `type` | 허용 값과 여러 definition의 merge 방법 | 평가 중 검사·merge에 사용 |
| `default` | 다른 값이 없을 때 사용할 기본 definition | 최종 값이 될 수 있음 |
| `example` | 문서에 보여 줄 사용 예 | 아니요 |
| `description` | option 검색과 manual에 나올 설명 | 아니요 |

`lib.mkEnableOption "example service"`는 boolean `enable` option을 만드는 편의
함수다. 개념적으로 `type = lib.types.bool`, `default = false`와 설명을 갖는
`mkOption`에 가깝다. 선언만 했다고 service가 켜지지는 않는다.

사용자나 다른 module은 선언된 option의 값을 정의한다.

```nix
{
  services.example = {
    enable = true;
    port = 9090;
    tags = [
      "internal"
      "metrics"
    ];
  };
}
```

두 역할을 구분한다.

- **declaration**: `services.example.enable`이라는 option이 존재하며 boolean이라는
  계약을 등록한다.
- **definition**: 현재 구성에서는 값을 `true`로 하겠다고 module system에 제공한다.
- **value**: 우선순위, 조건, type 검사와 merge를 거쳐 `config`에 나타난 최종 값이다.

대부분의 사용자는 NixOS와 Home Manager가 이미 선언한 option에 값을 정의한다.
직접 module을 만들 때만 option declaration을 작성하는 경우가 많다.

존재하지 않는 option 이름을 쓰거나 type이 맞지 않으면 평가 단계에서 오류가 난다.
오타를 조용히 무시하지 않는 것이 module system의 큰 장점이다.

!!! warning "`default`와 `mkDefault`는 위치와 목적이 다르다"
    `mkOption { default = 8080; }`의 `default`는 option 계약의 일부다. 반면
    `services.example.port = lib.mkDefault 8080;`은 한 module이 낮은 우선순위로
    제공하는 **definition**이다. 사용자는 보통 전자를 option 검색 문서에서 읽고,
    재사용 module을 작성할 때 후자를 사용한다.

## 5.4 `mk...`는 무엇을 뜻하는가

Nix 코드에서 `mk`는 보통 영어 **make**를 줄인 이름 관례다. “어떤 목적의 값을
만드는 함수”라는 힌트를 주지만 Nix 언어의 키워드, 연산자, wildcard는 아니다.
`mk`로 시작하는 이름에 Nix evaluator가 부여하는 특별한 문법도 없다.

```text
lib.mkOption
────┬──────
    └─ lib 속성 집합에 들어 있는 mkOption이라는 평범한 함수
```

문서에서 `mk* 함수`라고 쓰면 `mkOption`, `mkIf`, `mkDefault`처럼 이름이 `mk`로
시작하는 여러 함수를 통칭하는 표현이다. 실제 Nix 코드에 `lib.mk*`라고 쓰는 것은
아니다.

### 이름을 세 부분으로 읽는다

```text
lib . mk EnableOption
│     │  └────────── 무엇을 만드는가
│     └───────────── make 계열이라는 이름 관례
└────────────────── 어느 속성 집합에서 가져왔는가
```

`lib.mkEnableOption "example service"`는 다음 순서로 읽을 수 있다.

1. `lib`: Nixpkgs library에서 찾는다.
2. `mkEnableOption`: enable option declaration을 만드는 함수다.
3. `"example service"`: 함수에 전달할 첫 번째 인자다.
4. 호출 결과: `options` 아래에 놓을 boolean option declaration이다.

Nix에서는 함수 이름과 인자를 공백으로 나열해 호출한다. 따라서 다음은 `mkIf`에
조건과 definition 집합, 두 인자를 차례로 적용한 것이다.

```nix
lib.mkIf cfg.enable {
  environment.systemPackages = cfg.packages;
}
```

### Module system에서 자주 보는 `mk...`

| 함수 | 무엇을 만드는가 | 주로 놓는 위치 |
|---|---|---|
| `lib.mkOption` | type·default·설명이 든 option declaration | `options` 아래 |
| `lib.mkEnableOption` | 기본값이 `false`인 boolean enable declaration | `options.<경로>.enable` |
| `lib.mkPackageOption` | module이 사용할 package를 선택하는 declaration | `options.<경로>.package` |
| `lib.mkIf` | 조건부로 참여하는 definition 또는 definition 집합 | `config`나 option 값 |
| `lib.mkMerge` | 별도 module처럼 함께 merge할 definition 집합들의 묶음 | 주로 `config` |
| `lib.mkDefault` | 일반 definition이 덮을 수 있는 낮은 우선순위 definition | option definition 값 |
| `lib.mkForce` | 다른 낮은 우선순위 definition을 제외하는 강한 definition | option definition 값 |
| `lib.mkBefore` | list 등에 앞쪽 merge 순서를 부여한 definition | 순서가 있는 option 값 |
| `lib.mkAfter` | list 등에 뒤쪽 merge 순서를 부여한 definition | 순서가 있는 option 값 |

이 함수들이 모두 같은 종류의 결과를 만드는 것은 아니다.

- `mkOption`, `mkEnableOption`, `mkPackageOption`은 **option 선언 자료**를 만든다.
- `mkIf`, `mkMerge`는 **어떤 definition이 merge에 참여할지** 표현한다.
- `mkDefault`, `mkForce`는 definition에 **override 우선순위**를 붙인다.
- `mkBefore`, `mkAfter`는 살아남은 definition들의 **merge 순서**를 정한다.

여기서 “만든다”는 새 파일이나 package를 즉시 생성한다는 뜻이 아니다. 대체로
Module system이 나중에 해석할 표식이 든 Nix 값을 반환한다. 실제 type 검사와
definition merge는 module evaluator가 수행한다.

### 비슷해 보이는 함수의 차이

```nix
{
  options.services.example = {
    enable = lib.mkEnableOption "example service";

    port = lib.mkOption {
      type = lib.types.port;
      description = "TCP port used by the example service.";
    };
  };

  config = lib.mkMerge [
    {
      services.example.port = lib.mkDefault 8080;
    }

    (lib.mkIf config.services.example.enable {
      networking.firewall.allowedTCPPorts =
        lib.mkBefore [ config.services.example.port ];
    })
  ];
}
```

위 코드를 위에서 아래로 읽으면 다음과 같다.

1. `mkEnableOption`이 사용자가 켜고 끌 option을 **선언**한다.
2. `mkMerge`가 두 definition 집합을 하나의 `config`에서 **함께 제공**한다.
3. `mkDefault`가 다른 일반 definition으로 바꿀 수 있는 port 값을 **제안**한다.
4. `mkIf`가 service를 켰을 때만 firewall definition을 **참여**시킨다.
5. `mkBefore`가 firewall port 목록 안에서 이 항목의 **순서**를 앞쪽으로 둔다.

`mkForce`도 type 검사를 무시하는 명령은 아니다. 우선순위가 더 약한 definition을
후보에서 제외할 뿐이며, 살아남은 최종 값은 여전히 option type에 맞아야 한다.
`mkBefore`와 `mkAfter`도 어느 definition이 살아남는지를 정하지 않고 merge 순서만
조정한다.

### 모든 `mk...`가 module 함수는 아니다

다음 이름도 같은 “make” 관례를 사용하지만 module option helper는 아니다.

| 이름 | 속한 문맥 | 만드는 것 |
|---|---|---|
| `pkgs.mkShell` | Nixpkgs package 집합 | `nix develop`에 쓸 개발 shell derivation |
| `stdenv.mkDerivation` | Nixpkgs build 환경 | package derivation |
| `lib.mkOption` | Nixpkgs module library | option declaration |

따라서 `mk`만 보고 기능을 추측하지 않는다. 먼저 `lib`, `pkgs`, `stdenv` 중 어디에서
가져온 함수인지 보고, 전체 이름과 공식 함수 문서를 확인한다.

## 5.5 하나의 module은 인터페이스와 구현을 연결한다

Option이 실제 시스템을 바꾸는 과정을 작은 NixOS module로 살펴보자.

파일: `command-tools.nix`

```nix
{
  config,
  lib,
  ...
}:
let
  cfg = config.my.commandTools;
in
{
  options.my.commandTools = {
    enable = lib.mkEnableOption "a shared command-line tool set";

    packages = lib.mkOption {
      type = lib.types.listOf lib.types.package;
      default = [ ];
      description = "Command-line packages added to the system.";
    };
  };

  config = lib.mkIf cfg.enable {
    environment.systemPackages = cfg.packages;
  };
}
```

사용하는 쪽은 module을 import하고 공개된 option만 정의한다.

파일: `configuration.nix` (일부)

```nix
{ pkgs, ... }:
{
  imports = [
    ./command-tools.nix
  ];

  my.commandTools = {
    enable = true;
    packages = [
      pkgs.git
      pkgs.ripgrep
    ];
  };
}
```

평가 흐름은 다음과 같다.

1. `command-tools.nix`가 `my.commandTools.enable`과 `packages`를 선언한다.
2. `configuration.nix`가 각각 `true`와 package 목록을 정의한다.
3. Module system이 definition을 검사·병합해 `config.my.commandTools`를 만든다.
4. `cfg.enable`이 `true`이므로 `lib.mkIf` 안의 definition이 참여한다.
5. module 구현이 `cfg.packages`를 이미 존재하는
   `environment.systemPackages` option에 전달한다.
6. 최종 NixOS 구성이 해당 package들을 system profile에 포함한다.

이 예제에서 `my.commandTools.*`는 사용자가 다루는 고수준 인터페이스이고
`environment.systemPackages`는 구현에 사용한 기존 NixOS option이다. Option 자체가
package를 설치하는 것이 아니다. **option 값을 읽어 다른 option을 정의하는 module의
구현**이 효과를 만든다.

`let cfg = config.my.commandTools;`는 긴 경로에 붙인 지역 별칭일 뿐 특별한 module
문법이 아니다. `cfg.enable`과 `config.my.commandTools.enable`은 같은 최종 option
값을 가리킨다.

## 5.6 여러 파일의 definition은 type 규칙으로 합쳐진다

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

Type은 값이 맞는지 검사하는 역할과 여러 definition을 합치는 방법을 함께 정한다.

| 선언 type 예 | 허용하는 값 | 여러 definition의 일반적인 결과 |
|---|---|---|
| `lib.types.bool` | `true`, `false` | 서로 다르면 충돌 |
| `lib.types.str` | 문자열 하나 | 서로 다르면 충돌 |
| `lib.types.lines` | 문자열 | 줄바꿈으로 연결 |
| `lib.types.listOf lib.types.package` | package 목록 | 목록을 순서대로 연결 |
| `lib.types.attrsOf lib.types.str` | 문자열 값의 속성 집합 | 서로 다른 key를 합침 |
| `lib.types.nullOr lib.types.port` | `null` 또는 port 번호 | 선택된 실제 type 규칙 적용 |
| `lib.types.submodule { ... }` | 내부 option을 가진 속성 집합 | 하위 option별 검사·merge |

이 표는 대표적인 정신 모형이다. 실제 판단에서는 option 검색 결과의 정확한 type과
해당 type의 merge 규칙을 확인한다. “나중에 import한 파일이 무조건 이긴다”는 일반
규칙은 없다.

## 5.7 `imports`는 module graph를 만든다

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

`imports`는 다른 option의 최종 값보다 먼저 module graph를 확정하는 단계다. 따라서
보통 `config.some.option`에 따라 import할 파일을 고르는 식으로 작성할 수 없다.
조건에 따라 설정을 켜고 끄는 일은 module을 항상 import한 뒤 `lib.mkIf`로 definition을
조건부 제공하는 방식이 기본이다.

일반 `import`와 비교한다.

| 구문 | 하는 일 |
|---|---|
| `import ./value.nix` | 파일의 표현식을 즉시 평가해 값 반환 |
| `imports = [ ./module.nix ];` | 파일을 module graph에 등록해 함께 평가 |

보통 구성 파일을 나눌 때는 `imports`를 쓴다. `import`로 module 함수에 인자를 직접
전달하는 고급 패턴도 있지만, module system이 제공하는 인자와 merge를 우회하지
않는지 이해한 뒤 사용한다.

## 5.8 module 인자의 출처

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

## 5.9 `config`를 읽는 법

Module 코드에는 `config`라는 이름이 서로 다른 두 위치에 나와 처음에 혼동하기 쉽다.

```nix
{ config, lib, ... }:       # ① 함수 인자 config
{
  options.myFeature.enable = lib.mkEnableOption "my feature";

  config =                  # ② 반환 속성 config
    lib.mkIf config.myFeature.enable {
      # option definitions
    };
}
```

| 위치 | 방향 | 의미 |
|---|---|---|
| ① 함수 인자 `config` | Module system → 현재 module | 모든 module의 최종 option 값을 읽는 창 |
| ② 반환 속성 `config` | 현재 module → Module system | 현재 module이 제공하는 definition 묶음 |

Nix의 지연 평가 덕분에 module은 자신을 포함한 전체 definition의 결과를 ①을 통해
참조할 수 있다. 그러나 값의 의존 관계가 자기 자신을 끝없이 요구하면 infinite
recursion이 발생할 수 있다.

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

## 5.10 우선순위는 최후의 조정 도구다

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

## 5.11 NixOS option과 Home Manager option은 별도 API다

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

## 5.12 오류를 읽는 순서

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

### 1. declaration에서 최종 값까지 추적

다음 세 module 조각을 함께 평가한다고 가정한다.

```nix
# declaration.nix
{ lib, ... }:
{
  options.lesson.words = lib.mkOption {
    type = lib.types.listOf lib.types.str;
    default = [ ];
    description = "Words learned in this lesson.";
  };
}
```

```nix
# module-a.nix
{ lesson.words = [ "module" ]; }
```

```nix
# module-b.nix
{ lesson.words = [ "option" ]; }
```

다음 질문에 답한다.

1. `lesson.words`를 선언한 파일과 정의한 파일은 각각 어느 것인가?
2. `"module"`과 `"option"`은 왜 충돌하지 않는가?
3. 최종 `config.lesson.words`의 값은 무엇인가?
4. `module-b.nix`가 `lesson.words = 42;`로 바뀌면 어느 단계에서 실패하는가?
5. declaration의 `example`을 추가하면 최종 목록에도 들어가는가?

답: `declaration.nix`가 선언하고 나머지 두 파일이 정의한다. Type이 문자열 목록이며
목록의 merge 규칙이 definition들을 연결한다. 최종 값은
`[ "module" "option" ]`이다. 정수는 type 검사에서 실패한다. `example`은 문서용이라
최종 값에 들어가지 않는다.

### 2. 실제 Home Manager module 읽기

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

### 3. option 문서에서 계약 읽기

NixOS option 검색에서 `services.openssh.enable`과
`environment.systemPackages`를 찾아 다음 표를 직접 채운다.

| 확인 항목 | `services.openssh.enable` | `environment.systemPackages` |
|---|---|---|
| type |  |  |
| default |  |  |
| 설명 |  |  |
| 선언한 source |  |  |
| 두 module이 정의했을 때 예상 merge |  |  |

그다음 Home Manager option 검색에서 `programs.git.enable`을 찾아 같은 항목을
확인한다. “이름만 보고 의미를 추측하지 않고 현재 release의 declaration을 읽는다”가
이 연습의 목적이다.

### 4. `mk...` 함수 역할 구분

다음 각 표현이 선언, 조건·결합, override 우선순위, merge 순서 중 무엇을 다루는지
분류한다.

```nix
lib.mkOption { type = lib.types.str; }
lib.mkIf cfg.enable { services.example.enable = true; }
lib.mkDefault 8080
lib.mkForce false
lib.mkAfter [ "tail" ]
lib.mkMerge [ commonConfig hostConfig ]
pkgs.mkShell { packages = [ pkgs.git ]; }
```

확인할 항목:

1. `pkgs.mkShell`은 왜 나머지와 같은 module helper 그룹이 아닌가?
2. `lib.mkForce "not-a-port"`가 다른 definition을 이기면 port type 검사도
   통과하는가?
3. `mkDefault`와 `mkAfter` 중 어느 것이 definition의 생존 여부를 결정하는가?

답: `mkOption`은 선언, `mkIf`와 `mkMerge`는 조건·결합, `mkDefault`와 `mkForce`는
override 우선순위, `mkAfter`는 merge 순서를 다룬다. `pkgs.mkShell`은 package 집합에서
개발 shell derivation을 만드는 별도 함수다. `mkForce`로 살아남은 값도 type 검사를
통과해야 한다. 생존 여부는 `mkDefault` 같은 override 우선순위가, 살아남은 값의
순서는 `mkAfter` 같은 order 속성이 조정한다.

## 요약

- Module은 option을 선언하거나 정의해 전체 구성에 참여하는 설정 조각이다.
- Option은 이름, type, default, 설명, merge 규칙이 있는 설정 API다.
- Declaration은 허용할 값을 계약하고 definition은 현재 구성의 실제 값을 제공한다.
- `mk`는 보통 “make”를 줄인 함수 이름 관례이며 Nix의 특별한 문법이 아니다.
- `mkOption`, `mkIf`, `mkDefault`는 각각 선언, 조건, 우선순위라는 서로 다른 자료를
  만든다.
- Module system은 definition의 우선순위를 적용하고 type 검사·merge를 수행해 최종
  `config`를 만든다.
- Option 선언 자체는 시스템을 바꾸지 않는다. Module 구현이 최종 값을 읽고 package,
  service, 파일 등 다른 option을 정의할 때 효과가 생긴다.
- `imports`는 module graph를 만들고, 일반 `import`는 파일의 값을 반환한다.
- 함수 인자 `config`는 전체 결과를 읽는 값이고 반환 속성 `config`는 현재 module의
  definition 묶음이다.
- NixOS option과 Home Manager option은 별도 검색 공간과 적용 범위를 가진다.

## 공식 자료

- [nix.dev: A basic module](https://nix.dev/tutorials/module-system/a-basic-module/)
- [nix.dev: Module system deep dive](https://nix.dev/tutorials/module-system/deep-dive.html)
- [NixOS module 구조](https://nixos.org/manual/nixos/stable/#sec-writing-modules)
- [NixOS option 검색](https://search.nixos.org/options)
- [Home Manager option 검색](https://nix-community.github.io/home-manager/options.html)

[← 4장](./04-shells-and-packages.md) · [목차](./index.md) ·
[6장: NixOS와 Home Manager에 연결하기 →](./06-nixos-and-home-manager.md)
