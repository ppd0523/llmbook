# Cyclone DDS cross-build demo

This project is the complete example used by the Korean learning guide in the
parent directory. It builds two C++17 applications:

- `dds_publisher`
- `dds_subscriber`

Nix supplies the build tools. Conan supplies `cyclonedds/0.10.2`,
`spdlog/1.17.0`, and their transitive dependencies.

## Enter the development shell

```console
$ nix develop
```

## Native x86_64 build

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

Run the subscriber first, then the publisher in another `nix develop` shell.

```console
$ ./build/native/app/dds_subscriber 10 20 0
$ ./build/native/app/dds_publisher 10 500 0 native-pc
```

## Regenerate checked-in IDL output

After the native Conan install, activate its build environment and invoke the
explicit CMake target:

```console
$ source build/native/conan/build/Release/generators/conanbuild.sh
$ cmake --build build/native/app --target regenerate_idl
```

Commit `idl/Telemetry.idl` and the resulting files in `generated/` together.

## aarch64-musl static build

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

Verify that the output has no dynamic interpreter or shared-library
dependencies:

```console
$ "$AARCH64_READELF" -h build/aarch64/app/dds_publisher
$ "$AARCH64_READELF" -l build/aarch64/app/dds_publisher
$ "$AARCH64_READELF" -d build/aarch64/app/dds_publisher
```

The ELF header must report AArch64. The program-header output must not contain
`INTERP`, and the dynamic-section output must not contain `NEEDED`.
