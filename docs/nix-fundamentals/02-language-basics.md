# 2. Nix 언어를 읽는 최소 문법

## 학습 목표

1. 값, 목록, 속성 집합, 함수, `let`, 문자열 보간을 읽는다.
2. `.nix` 파일 하나가 표현식 하나라는 사실을 이해한다.
3. NixOS와 Home Manager module의 함수 머리 부분을 해석한다.

## 2.1 Nix 파일은 “문장 목록”이 아니라 표현식 하나다

Nix 언어에서 표현식을 평가하면 값이 나온다. `.nix` 파일 전체도 표현식 하나다.

```nix
1 + 2
```

```console
$ nix eval --expr '1 + 2'
3
```

다음 파일은 속성 집합 하나를 반환한다.

```nix
{
  name = "demo";
  enabled = true;
}
```

각 대입 끝의 세미콜론과 속성 집합 전체의 중괄호를 눈여겨본다. Nix에는 일반적인
절차형 언어의 “이 줄 다음 저 줄을 실행한다”는 모형이 없다. 값 사이의 의존 관계를
평가한다.

## 2.2 가장 자주 보는 값

| 종류 | 예 | 읽는 법 |
|---|---|---|
| 문자열 | `"hello"` | 큰따옴표 문자열 |
| 여러 줄 문자열 | `''hello''` | 들여쓰기 정리 기능이 있는 문자열 |
| 정수 | `42` | 숫자 |
| 불리언 | `true`, `false` | 참·거짓 |
| null | `null` | 값 없음 |
| path | `./module.nix` | 현재 파일 기준 경로 값 |
| 목록 | `[ "a" "b" ]` | 쉼표 없는 값 목록 |
| 속성 집합 | `{ a = 1; }` | 이름과 값의 모음 |
| 함수 | `x: x + 1` | `x`를 받아 식을 반환 |

### 목록에는 쉼표가 없다

```nix
[
  pkgs.git
  pkgs.ripgrep
  (pkgs.python3.withPackages (ps: [ ps.requests ]))
]
```

공백으로 항목을 나눈다. 복잡한 함수 호출을 목록의 한 항목으로 만들 때는 괄호가
중요하다. 세미콜론도 목록 항목 뒤에는 붙이지 않는다.

### 속성 집합에는 세미콜론이 있다

```nix
{
  name = "alice";
  shell = pkgs.zsh;
}
```

각 속성 정의는 `;`로 끝난다. JavaScript 객체와 달리 쉼표를 쓰지 않는다.

## 2.3 속성 경로와 중첩

다음 두 값은 같은 구조다.

```nix
{
  programs.git.enable = true;
}
```

```nix
{
  programs = {
    git = {
      enable = true;
    };
  };
}
```

NixOS와 Home Manager 설정에서는 첫 번째 축약형을 자주 쓴다. 공통 접두사가 많으면
두 번째 형태를 적절히 섞는다.

```nix
{
  programs.git = {
    enable = true;
    userName = "Alice";
  };
}
```

속성 선택도 점을 쓴다.

```nix
let
  person = {
    name = "Alice";
    role = "developer";
  };
in
person.name
```

결과는 `"Alice"`다.

## 2.4 `let ... in`: 이름 붙여 반복을 줄인다

```nix
let
  greeting = "hello";
  target = "Nix";
in
"${greeting}, ${target}"
```

`let`과 `in` 사이에서 이름을 정의하고, `in` 다음 표현식이 전체 결과가 된다.
문자열 안의 `${...}`는 Nix 표현식의 값을 끼워 넣는다.

실제 설정에서는 다음처럼 중복을 줄인다.

```nix
let
  commonPackages = [
    pkgs.git
    pkgs.ripgrep
  ];
in
{
  environment.systemPackages = commonPackages;
}
```

## 2.5 함수 호출에는 괄호도 쉼표도 없다

Nix 함수는 `인자: 결과` 형태다.

```nix
x: x + 1
```

호출은 함수와 인자를 공백으로 잇는다.

```nix
(x: x + 1) 41
```

여러 값을 받을 때는 속성 집합 하나를 인자로 받는 패턴이 흔하다.

```nix
{ name, greeting ? "hello" }:
"${greeting}, ${name}"
```

- `name`은 필수 속성이다.
- `greeting ? "hello"`는 기본값이 있는 선택 속성이다.
- 함수는 인자 속성 집합을 받아 문자열을 반환한다.

호출은 다음과 같다.

```nix
({ name, greeting ? "hello" }: "${greeting}, ${name}") {
  name = "Nix";
}
```

Nix에서 함수 적용의 결합 우선순위가 높기 때문에 긴 호출을 읽을 때는 “왼쪽 함수가
오른쪽 값 하나를 받는다”라고 괄호를 마음속으로 그린다.

## 2.6 `{ config, pkgs, ... }:`의 정체

NixOS와 Home Manager 파일 첫 줄에서 자주 만나는 코드는 함수다.

```nix
{ config, pkgs, lib, ... }:
{
  # option definitions
}
```

모듈 시스템이 큰 속성 집합을 인자로 전달하고, 이 함수는 필요한 값만 꺼낸다.

- `pkgs`: 선택된 Nixpkgs의 package 집합
- `config`: 모든 module 정의를 합친 최종 구성에 접근하는 값
- `lib`: module과 속성 집합을 다루는 Nixpkgs 함수 모음
- `...`: 나열하지 않은 추가 속성도 허용

이 파일을 일반 함수처럼 읽으면 된다.

```text
입력: config, pkgs, lib 등이 든 속성 집합
출력: option 정의가 든 속성 집합
```

중요한 점은 `pkgs`가 Nix 언어의 예약어가 아니라 호출자가 넘겨준 함수 인자라는
사실이다.

## 2.7 `inherit`, `with`, `import`

### `inherit`

```nix
let
  name = "demo";
  version = "1.0";
in
{
  inherit name version;
}
```

다음의 축약이다.

```nix
{
  name = name;
  version = version;
}
```

다른 속성 집합에서 꺼낼 수도 있다.

```nix
{ inherit (pkgs) git ripgrep; }
```

### `with`

다음 두 목록은 같은 package를 가리킨다.

```nix
with pkgs; [
  git
  ripgrep
]
```

```nix
[
  pkgs.git
  pkgs.ripgrep
]
```

`with pkgs;`는 범위 안에서 `pkgs`의 속성을 짧게 쓸 수 있게 한다. 짧은 설정을
읽는 데는 편하지만 값의 출처가 흐려질 수 있다. 입문 실습에서는 `pkgs.git`처럼
출처를 명시한다.

### `import`

`import ./packages.nix`는 파일을 텍스트처럼 붙이는 기능이 아니다. 그 파일의 Nix
표현식을 평가해 나온 값을 반환한다.

파일: `packages.nix`

```nix
{ pkgs }:
[
  pkgs.git
  pkgs.ripgrep
]
```

파일: `home.nix` (일부)

```nix
{ pkgs, ... }:
{
  home.packages = import ./packages.nix { inherit pkgs; };
}
```

순서는 다음과 같다.

1. `import ./packages.nix`의 결과는 함수다.
2. 그 함수에 `{ pkgs = pkgs; }`를 전달한다.
3. 결과인 package 목록을 `home.packages`에 정의한다.

반면 module을 합칠 때는 보통 module 시스템의 `imports`를 쓴다.

```nix
{
  imports = [
    ./shell.nix
    ./git.nix
  ];
}
```

`import`와 `imports`는 같은 기능이 아니다. 자세한 차이는 5장에서 다룬다.

## 2.8 path와 문자열을 구분한다

```nix
{
  source = ./config;
  destination = ".config/example";
}
```

- `./config`는 Nix가 추적하고 Store로 복사할 수 있는 **path 값**이다.
- `".config/example"`은 글자 그대로의 **문자열**이다.

`./foo`는 slash가 있어 path로 해석되지만 `foo`는 변수 이름이다. 절대 path는
이식성을 낮추며, Flake의 순수 평가에서는 home 경로나 현재 시스템 같은 외부 상태가
제한될 수 있다.

## 2.9 lazy evaluation은 “아무것도 안 한다”는 뜻이 아니다

Nix는 값이 필요할 때 평가한다. 이 성질 덕분에 module이 최종 `config`를 인자로
받으면서 그 `config`의 일부를 정의하는 패턴이 가능하다.

```nix
{ config, lib, ... }:
{
  config = lib.mkIf config.services.example.enable {
    # example service implementation
  };
}
```

그러나 자기 자신을 끝없이 요구하면 `infinite recursion` 오류가 난다. 입문 단계에서는
오류 메시지의 마지막 줄만 보지 말고 어떤 option이 어떤 값에 의존하는지 추적한다.

## 직접 해보기

REPL을 연다.

```console
$ nix repl
```

프롬프트에서 차례로 평가한다.

```nix
1 + 2

{ a = 1; b = 2; }.b

let x = 3; in x * x

(x: x + 1) 41

({ name, greeting ? "hello" }: "${greeting}, ${name}") { name = "Nix"; }

map (x: x * 2) [ 1 2 3 ]
```

REPL을 종료할 때는 `:q`를 입력한다.

### 코드 읽기 연습

다음 코드를 자연어로 설명해 본다.

```nix
{ pkgs, ... }:
let
  cliPackages = [
    pkgs.git
    pkgs.jq
  ];
in
{
  home.packages = cliPackages;
  programs.bash.enable = true;
}
```

모범 설명:

> `pkgs` 등이 든 속성 집합을 받아 Home Manager option 정의를 반환하는 함수다.
> `cliPackages`라는 package 목록을 만들고 이를 사용자의 package로 정의하며 Bash
> module을 활성화한다.

## 자주 하는 문법 실수

| 잘못된 코드 | 문제 | 올바른 형태 |
|---|---|---|
| `[ pkgs.git, pkgs.jq ]` | 목록에 쉼표 사용 | `[ pkgs.git pkgs.jq ]` |
| `{ enable = true }` | 속성 정의 뒤 세미콜론 누락 | `{ enable = true; }` |
| `"hello $name"` | Nix 보간 문법 아님 | `"hello ${name}"` |
| `[ f { x = 1; } ]` | 함수와 인자가 별도 항목 | `[ (f { x = 1; }) ]` |
| `source = " ./foo "` | path 대신 다른 문자열 | `source = ./foo;` |
| `{ pkgs }: ...` | 추가 module 인자를 거부할 수 있음 | `{ pkgs, ... }: ...` |

## 요약

- `.nix` 파일 하나는 평가되어 값 하나가 되는 표현식이다.
- 목록은 공백으로, 속성 정의는 세미콜론으로 구분한다.
- 함수는 `인자: 결과`, 호출은 `함수 인자` 형태다.
- NixOS와 Home Manager 파일은 보통 module 인자를 받아 option 정의를 반환하는 함수다.
- `import`는 파일의 값을 평가하고, module의 `imports`는 module graph를 구성한다.

## 공식 자료

- [Nix 언어 입문](https://nix.dev/tutorials/nix-language.html)
- [Nix 2.34 언어 개요](https://nix.dev/manual/nix/2.34/language/)
- [Nix 2.34 문법 reference](https://nix.dev/manual/nix/2.34/language/syntax.html)
- [Nix 모범 사례](https://nix.dev/guides/best-practices.html)

[← 1장](./01-ecosystem-and-mental-model.md) · [목차](./index.md) ·
[3장: Store, derivation, profile, generation →](./03-store-builds-and-generations.md)
