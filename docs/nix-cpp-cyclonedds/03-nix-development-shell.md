# 3. Flake 개발 셸 구성

## 학습 목표

- `flake.nix`와 `flake.lock`의 역할을 설명한다.
- 네이티브 도구 체인과 aarch64-musl 도구 체인을 한 셸에서 사용한다.
- CMake 3을 별도 Nixpkgs 입력에서 가져오는 이유를 설명한다.

## 3.1 Flake 입력 두 개

예제의 [`flake.nix`](./assets/cyclonedds-cross-demo/flake.nix)는 다음 입력을 사용한다.

```nix
inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
inputs.nixpkgsCmake.url = "github:NixOS/nixpkgs/nixos-25.05";
```

Nixpkgs 26.05의 기본 CMake는 4.x다. 그러나 `cyclonedds/0.10.2`의 Conan recipe는
`cmake/[>=3.16 <4]`를 요구한다. CMake만 25.05의 3.31 계열에서 가져오고 나머지 도구는
26.05에 둔다.

두 입력 모두 `flake.lock`에서 정확한 Git revision과 content hash로 고정된다.

## 3.2 두 컴파일러

```nix
nativeCC = pkgs.stdenv.cc;
crossCC = pkgs.pkgsCross.aarch64-multiplatform-musl.stdenv.cc;
```

`nativeCC`는 x86_64 프로그램을 만든다. `crossCC`는 x86_64에서 실행되지만 aarch64용
목적 파일을 만든다. 교차 컴파일러의 실행 파일에는 target prefix가 붙는다.

```text
aarch64-unknown-linux-musl-cc
aarch64-unknown-linux-musl-c++
aarch64-unknown-linux-musl-readelf
```

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

Conan 프로필에 버전과 Nix store 경로를 복사해서 쓰지 않으므로 Flake input을 갱신해도
프로필과 실제 도구가 어긋나지 않는다.

## 3.4 프로젝트 전용 Conan cache

셸은 다음 값을 설정한다.

```console
$ echo "$CONAN_HOME"
<project-root>/.conan2
```

프로젝트 밖의 사용자 Conan cache와 섞이지 않는다. `.conan2/`는 생성 가능한 상태이므로
Git에는 기록하지 않는다.

## 3.5 셸 시작

예제 프로젝트 루트에서 실행한다.

```console
$ nix develop
C++/Cyclone DDS development shell
  CMake       : cmake version 3.31.x
  Make        : GNU Make 4.x
  Conan       : Conan version 2.x
  Native C++  : /nix/store/.../bin/c++
  Target C++  : /nix/store/.../bin/aarch64-unknown-linux-musl-c++
```

처음에는 Nixpkgs와 교차 도구 체인을 내려받기 때문에 시간이 걸릴 수 있다. 두 번째부터는
Nix store의 결과를 재사용한다.

## 3.6 버전 확인

```console
$ cmake --version
$ make --version
$ conan --version
$ "$NATIVE_CXX" --version
$ "$AARCH64_CXX" --version
```

`python3`이나 `uv`는 이 셸의 공개 도구가 아니다. Conan 자체는 필요한 Python runtime을
Nix closure에 포함하고 있으므로 `conanfile.py` 처리에 별도 Python 환경이 필요하지 않다.

## 연습문제

1. `nix flake metadata`에서 두 Nixpkgs input의 revision을 찾는다.
2. `echo "$AARCH64_CXX"`의 파일이 실제로 존재하는지 `test -x`로 확인한다.
3. `nix develop --command conan --version`처럼 비대화형으로 명령을 실행한다.

## 요약

- 26.05는 주 도구, 25.05는 호환 CMake 3만 제공한다.
- Flake는 네이티브와 교차 컴파일러를 함께 제공한다.
- Conan 프로필은 Flake가 내보낸 실제 버전과 경로를 사용한다.
- `flake.lock`이 도구 공급망을 고정한다.
