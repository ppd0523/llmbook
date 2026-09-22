# 3. Flake 개발 셸 구성

## 학습 목표

- `flake.nix`와 `flake.lock`의 역할을 설명한다.
- 네이티브 도구 체인과 aarch64-musl 도구 체인을 한 셸에서 사용한다.
- CMake 3을 별도 Nixpkgs 입력에서 가져오는 이유를 설명한다.

## 3.1 Flake 입력 두 개와 CMake 3 고정

예제의 [`flake.nix`](assets/cyclonedds-cross-demo/flake.nix)는 Nixpkgs를 두 개 입력으로
받는다.

```nix
inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
inputs.nixpkgsCmake.url = "github:NixOS/nixpkgs/nixos-25.05";
```

입력이 두 개인 이유는 CMake 하나 때문이다. 이 책에서 CMake 버전을 고정하는 근거는 여기
한 곳에 모아 둔다.

Nixpkgs 26.05의 기본 CMake는 4.x다. 반면 `cyclonedds`의 ConanCenter recipe는 자신을 빌드할
때 쓸 CMake를 `cmake/[>=3.16 <4]` 범위로 요구한다. 4.x는 이 범위 밖이므로, 26.05의 CMake를
그대로 쓰면 Conan이 요구 범위를 만족하는 CMake를 따로 내려받으려 한다. 그래서 CMake만
3.31 계열을 제공하는 25.05에서 가져오고, 나머지 도구는 26.05에 둔다.

이 버전 범위는 recipe에 적힌 값이므로 recipe revision에 매여 있다. 예제의 Conan lockfile이
recipe revision까지 고정하므로, lockfile을 쓰는 한 이 범위도 함께 고정된다. lockfile 없이
최신 recipe를 받아 쓰면 요구 범위가 달라질 수 있다.

두 입력 모두 `flake.lock`에서 정확한 Git revision과 content hash로 고정된다. 이것이
1장에서 말한 첫 번째 자물쇠다.

## 3.2 두 컴파일러

```nix
nativeCC = pkgs.stdenv.cc;
crossCC = pkgs.pkgsCross.aarch64-multiplatform-musl.stdenv.cc;
```

`nativeCC`는 x86_64에서 실행되어 x86_64 프로그램을 만든다. `crossCC`도 x86_64에서
실행되지만 만들어 내는 목적 파일은 aarch64용이다. 이렇게 build 플랫폼과 host 플랫폼이 다른
컴파일러를 교차 컴파일러라고 한다.

두 컴파일러를 한 셸에 두면 이름이 충돌한다. Nixpkgs는 교차 도구 체인의 실행 파일 이름에
target 삼중자를 접두사로 붙여 이를 구분한다. `aarch64-multiplatform-musl`의 삼중자는
`aarch64-unknown-linux-musl`이므로 다음과 같은 이름이 된다.

```text
aarch64-unknown-linux-musl-cc
aarch64-unknown-linux-musl-c++
aarch64-unknown-linux-musl-readelf
```

접두사가 없는 `cc`, `c++`는 네이티브 도구다. 8장에서 교차 빌드 결과를 검사할 때 접두사가
붙은 `readelf`를 쓰는 것도 같은 이유다.

## 3.3 개발 셸이 내보내는 값

Flake는 Conan 프로필이 읽을 값을 환경 변수로 내보낸다.

| 변수 | 용도 |
|---|---|
| `CMAKE_PLATFORM_VERSION` | `[platform_tool_requires]`의 정확한 버전 |
| `NATIVE_GCC_VERSION` | x86_64 Conan compiler setting |
| `CROSS_GCC_VERSION` | aarch64 Conan compiler setting |
| `NATIVE_CC`, `NATIVE_CXX` | 네이티브 컴파일러 절대 경로 |
| `AARCH64_CC`, `AARCH64_CXX` | 교차 컴파일러 절대 경로 |
| `AARCH64_READELF` | 정적 ELF 검사 도구 |

이 값들은 모두 Flake가 실제로 고른 패키지에서 계산된다. Conan 프로필에 버전과 Nix store
경로를 손으로 복사해 두지 않으므로, Flake 입력을 갱신해도 프로필과 실제 도구가 어긋나지
않는다. 프로필이 이 변수를 어떻게 읽는지는 [4장](04-conan-profiles.md)에서 본다.

## 3.4 프로젝트 전용 Conan cache

셸은 `CONAN_HOME`을 프로젝트 아래로 설정한다.

```console
$ echo "$CONAN_HOME"
<project-root>/.conan2
```

Conan이 받아 온 소스와 빌드한 패키지가 이 디렉터리에 쌓이므로 사용자 홈의 공용 Conan
cache와 섞이지 않는다. `.conan2/`는 언제든 다시 만들 수 있는 상태이므로 Git에는 기록하지
않는다.

## 3.5 셸 시작

예제 프로젝트 루트에서 실행한다.

```console
$ nix develop
```

셸에 들어가면 `flake.nix`의 `shellHook`이 준비된 도구를 한 번 출력한다. 출력은 다음과 같은
형태다. 아래는 형식을 보이기 위한 예시이며, `/nix/store/` 아래 경로와 세부 버전 표기는
환경마다 다르다.

```text
C++/Cyclone DDS development shell
  CMake       : cmake version 3.31.6
  Make        : GNU Make 4.4.1
  Conan       : 2.28.1
  Native C++  : /nix/store/<hash>-gcc-wrapper-<ver>/bin/c++
  Target C++  : /nix/store/<hash>-gcc-wrapper-<ver>/bin/aarch64-unknown-linux-musl-c++
  Conan home  : <project-root>/.conan2
```

처음에는 Nixpkgs와 교차 도구 체인을 내려받기 때문에 시간이 걸릴 수 있다. 두 번째부터는
Nix store의 결과를 재사용한다.

## 3.6 버전 확인

셸에 들어온 직후, 뒤 장들이 전제하는 도구가 실제로 그 셸에 있는지 직접 확인한다.

```console
$ cmake --version
$ make --version
$ conan --version
$ "$NATIVE_CXX" --version
$ "$AARCH64_CXX" --version
```

확인할 것은 세 가지다.

1. `cmake --version`이 3.x를 보고하는가. 4.x가 나왔다면 25.05 입력의 CMake가 아니라 다른
   CMake가 PATH 앞쪽에 있는 것이다. 그 상태로는 3.1에서 설명한 recipe의 요구 범위를
   만족하지 못한다.
2. `conan --version`이 2.x를 보고하는가. 이 책의 프로필 문법과 명령은 모두 Conan 2
   기준이다.
3. `"$AARCH64_CXX" --version`이 동작하고 출력에 `aarch64-unknown-linux-musl`이 보이는가.
   변수가 비어 있으면 셸에 들어오지 않은 것이고, 경로는 있는데 실행되지 않으면 교차 도구
   체인이 아직 준비되지 않은 것이다.

`python3`이나 `uv`는 이 셸의 공개 도구가 아니다. Nixpkgs의 Conan 패키지는 Python
애플리케이션으로 빌드되어 필요한 Python runtime을 자신의 closure에 포함하므로,
`conanfile.py`를 처리하는 데 별도 Python 환경이 필요하지 않다.

## 직접 확인

1. `nix flake metadata`에서 두 Nixpkgs 입력의 revision을 찾고 `flake.lock`의 값과 같은지
   비교한다.
2. `test -x "$AARCH64_CXX" && echo ok`로 교차 컴파일러 경로가 실제 실행 파일인지 확인한다.
3. `nix develop --command conan --version`처럼 셸에 머무르지 않고 한 명령만 실행한다.
4. 셸 밖에서 같은 명령을 실행해 결과가 어떻게 달라지는지 본다. 뒤 장의 모든 명령은
   `nix develop` 안에서 실행한다는 전제 위에 있다.

## 요약

- 26.05는 주 도구를, 25.05는 recipe가 요구하는 범위에 드는 CMake 3만 제공한다.
- CMake 3을 고정하는 이유는 이 장에서 한 번만 설명하며, 근거는 recipe의 요구 범위다.
- Flake는 네이티브 컴파일러와 aarch64-musl 교차 컴파일러를 한 셸에 함께 둔다.
- Conan 프로필은 Flake가 내보낸 실제 버전과 경로를 환경 변수로 읽는다.
- `flake.lock`이 도구 공급망을 고정한다.
