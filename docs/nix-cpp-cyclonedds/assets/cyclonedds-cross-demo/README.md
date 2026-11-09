# Cyclone DDS 교차 빌드 예제

이 프로젝트는 상위 디렉터리의 학습 안내서가 사용하는 완성 예제다. 다음 두 C++17
애플리케이션을 빌드한다.

- `dds_publisher`
- `dds_subscriber`

빌드 도구는 Nix가 제공한다. `cyclonedds/0.10.2`, `spdlog/1.17.0`과 그 전이 의존성은
Conan이 제공한다.

## 개발 셸 진입

```console
$ nix develop
```

## 네이티브 x86_64 빌드

```console
$ conan install . \
    --output-folder=build/native/conan \
    --build=missing \
    --lockfile=conan-native.lock \
    --profile:build=profiles/build-x86_64 \
    --profile:host=profiles/host-x86_64

$ cmake -S . -B build/native/app \
    -G "Unix Makefiles" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_TOOLCHAIN_FILE="$PWD/build/native/conan/build/Release/generators/conan_toolchain.cmake"

$ make -C build/native/app -j"$(nproc)"
```

subscriber를 먼저 실행하고, 다른 `nix develop` 셸에서 publisher를 실행한다.

```console
$ ./build/native/app/dds_subscriber 10 20 0
$ ./build/native/app/dds_publisher 10 500 0 native-pc
```

## 저장소에 기록된 IDL 생성물 재생성

네이티브 Conan install을 마친 뒤 그 빌드 환경을 활성화하고 명시적인 CMake target을
실행한다.

```console
$ source build/native/conan/build/Release/generators/conanbuild.sh
$ cmake --build build/native/app --target regenerate_idl
```

`idl/Telemetry.idl`과 그 결과로 `generated/`에 만들어진 파일을 함께 commit한다.

## aarch64-musl 정적 빌드

```console
$ conan install . \
    --output-folder=build/aarch64/conan \
    --build=missing \
    --lockfile=conan-aarch64.lock \
    --profile:build=profiles/build-x86_64 \
    --profile:host=profiles/host-aarch64-musl

$ cmake -S . -B build/aarch64/app \
    -G "Unix Makefiles" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_TOOLCHAIN_FILE="$PWD/build/aarch64/conan/build/Release/generators/conan_toolchain.cmake"

$ make -C build/aarch64/app -j"$(nproc)"
```

출력 파일에 동적 인터프리터나 공유 라이브러리 의존성이 없는지 확인한다.

```console
$ "$AARCH64_READELF" -h build/aarch64/app/dds_publisher
$ "$AARCH64_READELF" -l build/aarch64/app/dds_publisher
$ "$AARCH64_READELF" -d build/aarch64/app/dds_publisher
```

ELF header는 AArch64를 보고해야 한다. program header 출력에는 `INTERP`가 없어야 하고,
dynamic section 출력에는 `NEEDED`가 없어야 한다.
