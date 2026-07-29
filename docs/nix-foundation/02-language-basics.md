# 2. Nix 언어를 읽는 최소 문법

## 학습 목표

1. 값, 목록, 속성 집합, 함수, `let`, 문자열 보간을 읽는다.
2. `.nix` 파일 하나가 표현식 하나라는 사실을 이해한다.
3. REPL, 한 줄 표현식, `.nix` 파일을 직접 평가한다.
4. 평가, 빌드, 실행, module 적용에 사용하는 명령을 구분한다.
5. NixOS와 Home Manager module의 함수 머리 부분을 해석한다.

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

## 2.2 Nix 언어를 실행하는 방법

Nix 언어에는 일반 프로그램의 `main` 함수처럼 무조건 실행되는 시작점이 없다.
표현식을 **평가**해 값을 얻고, 결과가 derivation이면 그 계획을 **실현**한다.
따라서 무엇을 얻고 싶은지에 따라 명령이 달라진다.

### 한 줄 표현식 평가

가장 짧은 실험은 `nix eval --expr`로 실행한다.

```console
$ nix eval --expr '1 + 2'
3

$ nix eval --expr 'let x = 3; in x * x'
9
```

기본 출력은 다시 읽을 수 있는 Nix 표현식 형태다. 문자열의 따옴표 없이 내용만
필요하면 `--raw`를 사용한다.

```console
$ nix eval --raw --expr '"hello, Nix"'
hello, Nix
```

속성 집합이나 목록을 다른 도구로 넘기려면 JSON이 편리하다.

```console
$ nix eval --json --expr '{ name = "Alice"; tools = [ "git" "jq" ]; }'
{"name":"Alice","tools":["git","jq"]}
```

함수처럼 JSON으로 표현할 수 없는 값에는 `--json`을 사용할 수 없다.

### REPL에서 대화형 평가

여러 표현식을 조금씩 바꿔 볼 때는 REPL을 연다.

```console
$ nix repl
```

```nix
nix-repl> person = { name = "Alice"; age = 20; }

nix-repl> person.name
"Alice"

nix-repl> (x: x + 1) 41
42

nix-repl> :q
```

REPL은 read-eval-print loop의 약자다. 입력을 읽고 평가한 뒤 결과를 출력하는 과정을
반복한다. `:q`로 종료한다.

### `.nix` 파일 평가

다음 파일 전체는 문자열 하나가 되는 표현식이다.

파일: `<practice>/hello.nix` (전체)

```nix
let
  name = "Nix";
in
"Hello, ${name}!"
```

파일을 직접 평가한다.

```console
$ nix eval --file ./hello.nix
"Hello, Nix!"

$ nix eval --raw --file ./hello.nix
Hello, Nix!
```

`--file` 뒤에 속성 경로를 붙이면 파일 결과의 일부만 선택할 수 있다.

파일: `<practice>/person.nix` (전체)

```nix
{
  name = "Alice";
  role = "developer";
}
```

```console
$ nix eval --raw --file ./person.nix name
Alice
```

### 함수가 들어 있는 파일 호출

파일 전체가 함수라면 평가만 해서는 최종 문자열이 나오지 않는다.

파일: `<practice>/greet.nix` (전체)

```nix
{ name, greeting ? "Hello" }:
"${greeting}, ${name}!"
```

`import`로 함수 값을 얻고 속성 집합 인자를 전달한다.

```console
$ nix eval --raw --expr '(import ./greet.nix) { name = "Alice"; }'
Hello, Alice!
```

이 명령은 다음 순서로 읽는다.

1. `import ./greet.nix`가 파일을 평가해 함수를 반환한다.
2. `{ name = "Alice"; }`를 함수 인자로 전달한다.
3. 함수의 결과 문자열을 `--raw`로 출력한다.

### 결과 종류에 맞는 명령 선택

| 원하는 결과 | 대표 명령 | 의미 |
|---|---|---|
| 숫자·문자열·속성 집합 | `nix eval` | 표현식을 값으로 계산 |
| 대화형 문법 실험 | `nix repl` | 입력과 평가를 반복 |
| package·derivation output | `nix build` | Store 결과를 확보 |
| Flake app 실행 | `nix run` | app이 가리키는 프로그램 실행 |
| 프로젝트 개발 환경 | `nix develop` | dev shell process 시작 |
| NixOS 구성 | `nixos-rebuild build` | NixOS module 전체 평가·빌드 |
| Home Manager 구성 | `home-manager build` | Home Manager module 전체 평가·빌드 |

`configuration.nix`와 `home.nix`는 보통 module 함수다. Module system이 `pkgs`,
`config`, `lib` 같은 인자를 제공하고 option을 합쳐야 하므로 일반 파일처럼 단독
평가해서 적용하지 않는다.

```console
$ sudo nixos-rebuild build --flake .#myhost
$ home-manager build --flake .#alice
```

이 명령들도 `build`만으로 현재 환경을 전환하지는 않는다. 실제 활성화와 `switch`의
차이는 6장에서 다룬다.

!!! note
    `nix eval`, `nix repl` 같은 새 CLI에서 experimental feature 오류가 발생하면
    [목차의 준비 설정](./index.md#prerequisites)에서 `nix-command`와 `flakes`
    설정을 확인한다. 단순 `--expr`·`--file` 평가에는 Flake가 필요하지 않지만,
    이 자료의 후속 Flake 명령을 위해 두 기능을 함께 준비한다.

## 2.3 가장 자주 보는 값

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

## 2.4 속성 경로와 중첩

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

## 2.5 `let ... in`: 이름 붙여 반복을 줄인다

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

## 2.6 함수 호출에는 괄호도 쉼표도 없다

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

## 2.7 `{ config, pkgs, ... }:`의 정체

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

## 2.8 `inherit`, `with`, `import`

세 구문은 모두 이름을 짧게 쓰는 데 관여하지만 하는 일은 전혀 다르다.

| 구문 | 핵심 동작 | 결과 |
|---|---|---|
| `inherit` | 이미 scope에 있는 이름을 같은 이름의 binding으로 복사 | 속성 또는 `let` binding |
| `with` | 속성 집합의 이름을 한 표현식 안에서만 짧게 사용 | `with` 뒤 표현식의 값 |
| `import` | 다른 Nix 파일을 평가 | 그 파일이 반환한 값 |

먼저 “현재 scope에 무슨 이름이 있는가”와 “이 표현식이 무슨 값을 반환하는가”를
분리해 생각한다.

### 2.8.1 `inherit`: 같은 이름을 전달한다

#### 바깥 scope의 변수를 속성으로 복사

다음 식에서 `name`과 `version`은 `let`이 만든 현재 scope의 변수다.

```nix
let
  name = "demo";
  version = "1.0";
in
{
  inherit name version;
}
```

`inherit name version;`은 다음 두 정의의 축약이다.

```nix
let
  name = "demo";
  version = "1.0";
in
{
  name = name;
  version = version;
}
```

각 정의의 왼쪽은 새 속성의 이름이고 오른쪽은 바깥 scope에서 찾은 변수다.

```text
inherit name;
        │
        ├── 결과 속성 이름: name
        └── 현재 scope에서 읽을 변수: name
```

`inherit`가 값을 새로 계산하거나 두 값을 연결하는 것은 아니다. 같은 이름을 반복해서
쓰는 수고를 줄일 뿐이다.

#### 함수에 인자를 전달하는 가장 흔한 패턴

NixOS와 Home Manager 코드에서는 다음 형태를 자주 본다.

```nix
import ./packages.nix { inherit pkgs; }
```

여기서 `{ inherit pkgs; }`만 풀어 쓰면 다음과 같다.

```nix
{ pkgs = pkgs; }
```

- 왼쪽 `pkgs`: 호출할 함수에 전달하는 속성 이름
- 오른쪽 `pkgs`: 현재 module 함수가 인자로 받은 package 집합

즉 “현재의 `pkgs`를 `pkgs`라는 이름으로 다음 함수에 전달한다”라는 뜻이다.
값의 출처를 추적할 때는 오른쪽 `pkgs`가 어느 함수 인자나 `let`에서 왔는지 찾는다.

이름을 바꿔 전달하려면 `inherit`가 아니라 일반 정의를 쓴다.

```nix
{
  packages = pkgs;
}
```

#### 특정 속성 집합에서 선택

괄호를 사용하면 현재 scope가 아니라 지정한 속성 집합에서 값을 꺼낸다.

```nix
let
  metadata = {
    name = "demo";
    version = "1.0";
    internal = true;
  };
in
{
  inherit (metadata) name version;
}
```

다음과 같다.

```nix
let
  metadata = {
    name = "demo";
    version = "1.0";
    internal = true;
  };
in
{
  name = metadata.name;
  version = metadata.version;
}
```

`internal`은 이름을 나열하지 않았으므로 결과에 들어가지 않는다. 이 형태는 큰 속성
집합에서 전달할 값만 명시적으로 선택한다.

```nix
{
  inherit (pkgs) git ripgrep;
}
```

이 결과는 package **목록**이 아니라 다음 모양의 **속성 집합**이다.

```nix
{
  git = pkgs.git;
  ripgrep = pkgs.ripgrep;
}
```

따라서 list type인 `home.packages`에는 그대로 넣을 수 없다.

```nix
# 올바른 package 목록
home.packages = [
  pkgs.git
  pkgs.ripgrep
];
```

#### `let` 안에서도 사용

`inherit`는 결과 속성 집합뿐 아니라 `let` binding에도 쓸 수 있다.

```nix
let
  tools = {
    formatter = "nixfmt";
    search = "ripgrep";
  };

  inherit (tools) formatter search;
in
"${formatter} and ${search}"
```

다음과 같은 뜻이다.

```nix
let
  tools = {
    formatter = "nixfmt";
    search = "ripgrep";
  };

  formatter = tools.formatter;
  search = tools.search;
in
"${formatter} and ${search}"
```

`inherit (set) name;`에서 `name`이 실제로 존재하지 않으면 평가 오류가 발생한다.

### 2.8.2 `with`: 한 표현식에 임시 scope를 연다

`with`의 구조는 다음과 같다.

```nix
with 속성집합; 본문표현식
```

Nix는 본문에서 이름을 찾을 때 해당 속성 집합의 속성도 후보로 사용한다.

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

#### scope는 세미콜론 뒤 표현식 하나뿐이다

```nix
let
  tools = {
    git = "git-value";
    jq = "jq-value";
  };
in
{
  inside = with tools; [ git jq ];
  outside = tools.git;
}
```

`inside`의 목록 안에서는 `git`과 `jq`를 짧게 쓸 수 있다. `with`가 끝난
`outside`에서는 다시 `tools.git`이라고 써야 한다.

다음 코드는 `outside = git;`의 `git`을 찾을 수 없어 실패한다.

```nix
let
  tools = {
    git = "git-value";
  };
in
{
  inside = with tools; git;
  outside = git;
}
```

`with`는 주변 scope를 영구히 변경하거나 속성 집합을 수정하지 않는다. 세미콜론 뒤의
본문 표현식을 평가할 때만 이름 검색 범위를 추가한다.

#### 기존 변수와 이름이 겹칠 때

`with`가 추가한 이름은 `let`이나 함수 인자로 들어온 lexical binding을 덮지 않는다.

```nix
let
  git = "from-let";
in
with {
  git = "from-with";
  jq = "jq-from-with";
};
[
  git
  jq
]
```

결과는 다음과 같다.

```nix
[
  "from-let"
  "jq-from-with"
]
```

`git`은 기존 `let` binding이 우선하고, 기존 scope에 없던 `jq`만 `with`의 속성
집합에서 온다. 반면 여러 `with`가 중첩되면 안쪽 `with`가 바깥 `with`의 같은 이름을
가릴 수 있다.

이 규칙 때문에 다음처럼 범위가 큰 `with`는 이름의 출처를 찾기 어렵다.

```nix
with pkgs;
{
  # 수십 줄의 설정
}
```

공식 Nix 모범 사례도 파일 최상위의 `with`를 피하고 명시적인 이름을 권장한다.
입문 단계에서는 다음 순서로 선택한다.

1. 가장 명확한 형태인 `pkgs.git`을 쓴다.
2. 같은 이름을 여러 번 쓸 때 `let`과 `inherit (pkgs)`를 고려한다.
3. `with pkgs; [ ... ]`는 package 목록처럼 짧고 경계가 분명한 곳에 제한한다.

```nix
# 출처가 가장 분명하다.
home.packages = [
  pkgs.git
  pkgs.ripgrep
];
```

```nix
# 이름을 반복해서 사용할 때 선택적으로 scope에 넣는다.
let
  inherit (pkgs) git ripgrep;
in
{
  home.packages = [
    git
    ripgrep
  ];
}
```

```nix
# 짧은 목록에서는 흔히 볼 수 있다.
home.packages = with pkgs; [
  git
  ripgrep
];
```

세 코드는 같은 package 값을 선택한다. 차이는 이름의 출처를 얼마나 명확하게
드러내는가다.

### 2.8.3 `import`: 파일을 평가해 값을 받는다

`import`는 Nix evaluator에 내장된 함수다. 경로를 받아 그 파일의 표현식 하나를
평가하고 결과를 그대로 반환한다. 파일을 텍스트처럼 현재 위치에 붙이는 기능이 아니다.

#### 파일은 어떤 값이든 반환할 수 있다

파일: `<practice>/answer.nix` (전체)

```nix
40 + 2
```

```console
$ nix eval --expr 'import ./answer.nix'
42
```

속성 집합을 반환하는 파일도 있다.

파일: `<practice>/metadata.nix` (전체)

```nix
{
  name = "demo";
  version = "1.0";
}
```

```console
$ nix eval --raw --expr '(import ./metadata.nix).name'
demo
```

`import` 결과가 속성 집합이므로 `.name`으로 속성을 선택했다.

#### 함수 파일은 import한 다음 호출한다

파일: `<practice>/packages.nix` (전체)

```nix
{ pkgs }:
[
  pkgs.git
  pkgs.ripgrep
]
```

파일: `<practice>/home.nix` (일부)

```nix
{ pkgs, ... }:
{
  home.packages = import ./packages.nix { inherit pkgs; };
}
```

함수 적용은 공백으로 이어지므로 괄호를 보충해 읽으면 다음과 같다.

```nix
home.packages = (import ./packages.nix) { pkgs = pkgs; };
```

평가 순서는 다음과 같다.

1. `import ./packages.nix`의 결과는 함수다.
2. `{ inherit pkgs; }`는 `{ pkgs = pkgs; }`가 된다.
3. import가 반환한 함수에 그 속성 집합을 전달한다.
4. 함수가 반환한 package 목록을 `home.packages`에 정의한다.

`import`가 자동으로 `pkgs`를 제공한 것이 아니다. 호출하는 쪽에서 명시적으로
전달했다.

#### imported 파일은 호출자의 지역 변수를 자동으로 보지 못한다

다음 파일은 `pkgs`를 선언하거나 인자로 받지 않았다.

파일: `<practice>/broken-packages.nix` (잘못된 예)

```nix
[
  pkgs.git
]
```

바깥 파일의 `let pkgs = ...;` 안에서 import하더라도 imported 파일이 그 지역
scope를 상속하지는 않는다. `undefined variable 'pkgs'` 오류가 난다. 파일 사이에
값을 전달하려면 앞 예제처럼 imported 파일을 함수로 만들고 인자를 넘긴다.

```nix
# packages.nix
{ pkgs }:
[
  pkgs.git
]
```

```nix
# 호출하는 파일
{ pkgs, ... }:
let
  packages = import ./packages.nix { inherit pkgs; };
in
{
  home.packages = packages;
}
```

이 패턴은 파일이 외부에서 무엇을 필요로 하는지 함수 인자에 드러낸다.

#### 디렉터리를 import하면 `default.nix`를 찾는다

다음 두 표현식은 `./tools/default.nix`가 있을 때 같은 파일을 평가한다.

```nix
import ./tools
```

```nix
import ./tools/default.nix
```

상대 path literal은 그 path literal이 적힌 Nix 파일을 기준으로 해석된다.
`--expr`로 직접 입력한 상대 경로는 명령을 실행한 현재 디렉터리를 기준으로 생각하면
된다.

#### `import`와 module의 `imports`는 다르다

`imports`는 Nix 언어의 키워드가 아니라 module system이 해석하기로 약속한 평범한
속성 이름이다.

```nix
{
  imports = [
    ./shell.nix
    ./git.nix
  ];
}
```

| 구분 | `import ./file.nix` | `imports = [ ./file.nix ];` |
|---|---|---|
| 처리 주체 | Nix 언어 evaluator | NixOS·Home Manager module system |
| 즉시 얻는 것 | imported 파일이 반환한 값 | 함께 평가할 module graph |
| 함수 인자 | 호출자가 직접 전달 | module system이 `pkgs`, `config`, `lib` 등을 전달 |
| 여러 definition merge | 하지 않음 | option type 규칙에 따라 수행 |

NixOS module 파일을 `import ./module.nix`하면 보통 module 함수 값만 얻는다. 그것만으로
현재 NixOS 구성에 option이 합쳐지지 않는다. 일반적인 module 분할은 `imports` 목록에
path를 넣는다. 자세한 merge 과정은 5장에서 다룬다.

### 2.8.4 세 구문을 함께 읽기

다음 Home Manager 조각을 왼쪽에서 오른쪽으로 해석해 보자.

```nix
{ pkgs, ... }:
let
  basePackages = with pkgs; [
    git
    ripgrep
  ];

  extraPackages = import ./extra-packages.nix {
    inherit pkgs;
  };
in
{
  home.packages = basePackages ++ extraPackages;
}
```

파일: `<same-directory>/extra-packages.nix` (전체)

```nix
{ pkgs }:
[
  pkgs.jq
]
```

1. 바깥 module 함수가 `pkgs`를 인자로 받는다.
2. `with pkgs;`는 첫 번째 짧은 목록 안에서 `git`, `ripgrep`을 찾게 한다.
3. `import`는 `extra-packages.nix`를 평가해 함수를 얻는다.
4. `{ inherit pkgs; }`가 현재 `pkgs`를 imported 함수에 전달한다.
5. 두 함수 결과는 각각 package 목록이다.
6. `++`가 두 목록을 연결해 `home.packages`의 최종 정의를 만든다.

이 코드를 읽을 때 세 구문을 “전부 package를 가져오는 문법”으로 묶지 않는다.
`with`는 이름 검색 범위, `inherit`는 값 전달, `import`는 파일 평가를 담당한다.

### 직접 확인

다음 표현식을 `nix repl`이나 `nix eval --expr`로 확인한다.

```nix
let
  source = {
    x = 1;
    y = 2;
  };
in
{
  inherited = {
    inherit (source) x;
  };

  selected = with source; x + y;
}
```

예상 결과:

```nix
{
  inherited = { x = 1; };
  selected = 3;
}
```

그리고 다음 질문에 답해 본다.

1. `{ inherit pkgs; }`를 풀어 쓰면 무엇인가?
2. `with pkgs; [ git ]`의 `git`은 어느 값인가?
3. `import ./file.nix`의 결과 type은 항상 속성 집합인가?
4. imported 함수가 `pkgs`를 요구하면 누가 전달해야 하는가?
5. NixOS module을 다른 module과 합칠 때 `import`와 `imports` 중 무엇을 쓰는가?

정답은 각각 `{ pkgs = pkgs; }`, `pkgs.git`, “아니며 파일 표현식에 따라 달라진다”,
“호출하는 쪽”, “module system의 `imports`”다.

## 2.9 path와 문자열을 구분한다

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

## 2.10 lazy evaluation은 “아무것도 안 한다”는 뜻이 아니다

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
- 값은 `nix eval`이나 `nix repl`로 평가하고 derivation은 `nix build`로 실현한다.
- 함수 파일은 `import`한 함수에 인자를 전달해 최종 값을 얻는다.
- 목록은 공백으로, 속성 정의는 세미콜론으로 구분한다.
- 함수는 `인자: 결과`, 호출은 `함수 인자` 형태다.
- `inherit`는 현재 scope나 지정한 속성 집합에서 같은 이름의 binding을 만든다.
- `with`는 뒤따르는 표현식에만 이름 검색 범위를 추가하며 큰 범위에서는 피한다.
- NixOS와 Home Manager 파일은 보통 module 인자를 받아 option 정의를 반환하는 함수다.
- `import`는 파일의 값을 평가하고, module의 `imports`는 module graph를 구성한다.

## 공식 자료

- [Nix 언어 입문](https://nix.dev/tutorials/nix-language.html)
- [`nix eval`](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-eval.html)
- [`nix repl`](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-repl.html)
- [Nix 2.34 언어 개요](https://nix.dev/manual/nix/2.34/language/)
- [Nix 2.34 문법 reference](https://nix.dev/manual/nix/2.34/language/syntax.html)
- [`import` built-in](https://nix.dev/manual/nix/2.34/language/builtins.html#builtins-import)
- [Nix 모범 사례](https://nix.dev/guides/best-practices.html)

[← 1장](./01-ecosystem-and-mental-model.md) · [목차](./index.md) ·
[3장: Store, derivation, profile, generation →](./03-store-builds-and-generations.md)
