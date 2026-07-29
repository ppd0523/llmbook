# 8. aarch64-musl 정적 교차 빌드

## 학습 목표

- build profile과 host profile의 차이를 실제 빌드에 적용한다.
- aarch64용 정적 실행 파일을 만든다.
- 실행하지 않고 ELF 형식과 동적 의존성을 검사한다.

## 8.1 교차 dependency graph 고정

```console
$ conan lock create . \
    --lockfile-out=conan-aarch64.lock \
    --profile:build=profiles/build-x86_64 \
    --profile:host=profiles/host-aarch64-musl
```

build profile은 `idlc` 같은 x86_64에서 실행할 도구를, host profile은 최종
aarch64 프로그램과 링크될 라이브러리를 설명한다. 여기서 host는 빌드를 실행하는
PC라는 일상적 의미가 아니라 **결과물이 실행될 플랫폼**이라는 Conan 용어다.

## 8.2 aarch64 라이브러리 준비

```console
$ conan install . \
    --output-folder=build/aarch64/conan \
    --build=missing \
    --lockfile=conan-aarch64.lock \
    --profile:build=profiles/build-x86_64 \
    --profile:host=profiles/host-aarch64-musl
```

host profile은 Nix store에 있는
`aarch64-unknown-linux-musl-gcc`와 `g++`를 사용한다. Cyclone DDS, spdlog와 전이
라이브러리도 같은 compiler와 정적 옵션으로 빌드한다.

## 8.3 애플리케이션 빌드

```console
$ cmake -S . -B build/aarch64/app \
    -G "Unix Makefiles" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_TOOLCHAIN_FILE="$PWD/build/aarch64/conan/build/Release/generators/conan_toolchain.cmake"

$ make -C build/aarch64/app -j"$(nproc)"
```

CMake configure 로그의 C/C++ compiler가
`aarch64-unknown-linux-musl-`로 시작하는지 확인한다. 이 빌드는 이미 기록된
`generated/Telemetry.c`를 컴파일하며 aarch64용 `idlc`를 실행하지 않는다.

## 8.4 실행 전에 ELF 검사

x86_64 빌드 호스트에서는 aarch64 프로그램을 직접 실행하지 않는다. Nix 셸이
제공한 target용 `readelf`로 정적 결과를 검사한다.

```console
$ "$AARCH64_READELF" -h build/aarch64/app/dds_publisher
$ "$AARCH64_READELF" -l build/aarch64/app/dds_publisher
$ "$AARCH64_READELF" -d build/aarch64/app/dds_publisher
```

판정 기준은 다음과 같다.

| 검사 | 기대 결과 |
|---|---|
| ELF header의 `Machine` | `AArch64` |
| program header | `INTERP` 항목 없음 |
| dynamic section | `NEEDED` 항목 없음 또는 dynamic section 자체가 없음 |

subscriber도 같은 방식으로 검사한다.

```console
$ "$AARCH64_READELF" -h build/aarch64/app/dds_subscriber
$ "$AARCH64_READELF" -l build/aarch64/app/dds_subscriber
$ "$AARCH64_READELF" -d build/aarch64/app/dds_subscriber
```

## 8.5 “정적”이 보장하는 것

완전 정적 링크는 target에 Cyclone DDS, spdlog, glibc 같은 사용자 공간 shared
library를 따로 설치하지 않아도 된다는 뜻이다. CPU가 aarch64여야 하고 Linux kernel,
네트워크 장치와 권한은 여전히 필요하다.

musl을 사용한 이유는 정적 링크에 적합한 독립적인 libc를 함께 묶기 위해서다. Nix
store 경로가 실행 파일의 동적 loader나 shared library 의존성으로 남지 않았는지도
위 검사로 확인한다.

## 연습문제

1. 네이티브와 교차 configure 로그의 compiler 경로를 비교한다.
2. 두 실행 파일의 ELF `Machine` 값을 확인한다.
3. `INTERP`와 `NEEDED`가 각각 무엇을 의미하는지 자신의 말로 설명한다.

## 요약

- build profile은 x86_64 실행 도구, host profile은 aarch64 결과물을 정의한다.
- 라이브러리와 애플리케이션 모두 같은 musl 교차 도구 체인으로 빌드한다.
- target에 복사하기 전에 ELF header, interpreter, shared-library 의존성을 검사한다.
