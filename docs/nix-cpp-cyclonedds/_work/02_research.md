---
title: 조사 노트
version: 1.0
status: final
owner: agent
updated: 2026-09-22
target_reader: C++와 Linux 명령을 조금 사용해 본 개발자
topic: Nix·Conan 2·CMake·Cyclone DDS 교차 빌드의 공식 근거
---

# 조사 노트

이 책이 고정한 baseline은 Nixpkgs 26.05, Conan 2.28, Cyclone DDS 0.10.2, spdlog 1.17.0이다.
모든 대조는 2026-09-22에 수행했다.

## 1. 핵심 출처

| 구분 | 제목 | 기관·저자 | 연도 | 링크 | 사용할 내용 |
|---|---|---|---|---|---|
| 공식 문서 | Nixpkgs Manual: Cross-compilation | NixOS Foundation | 2026 | <https://nixos.org/manual/nixpkgs/stable/#chap-cross> | `pkgsCross`, target prefix, build/host/target 구분 |
| 공식 저장소 | `lib/systems/examples.nix` (`nixos-26.05`) | NixOS/nixpkgs | 2026 | <https://github.com/NixOS/nixpkgs/blob/nixos-26.05/lib/systems/examples.nix> | `aarch64-multiplatform-musl`의 `config` 값 |
| 공식 저장소 | `pkgs/by-name/cm/cmake/package.nix` (`nixos-26.05`, `nixos-25.05`) | NixOS/nixpkgs | 2026 | <https://github.com/NixOS/nixpkgs/blob/nixos-26.05/pkgs/by-name/cm/cmake/package.nix> | 각 채널의 CMake 버전 |
| 공식 저장소 | `pkgs/by-name/co/conan/package.nix` (`nixos-26.05`) | NixOS/nixpkgs | 2026 | <https://github.com/NixOS/nixpkgs/blob/nixos-26.05/pkgs/by-name/co/conan/package.nix> | Conan 버전과 Python 런타임 포함 여부 |
| 공식 저장소 | `pkgs/top-level/aliases.nix` (`nixos-26.05`) | NixOS/nixpkgs | 2026 | <https://github.com/NixOS/nixpkgs/blob/nixos-26.05/pkgs/top-level/aliases.nix> | `nixfmt-rfc-style`의 별칭·경고 상태 |
| 공식 문서 | Conan 2: profiles | JFrog | 2026 | <https://docs.conan.io/2/reference/config_files/profiles.html> | 프로필 섹션 목록과 Jinja2 `os.getenv` |
| 공식 문서 | Conan 2: `conan install` | JFrog | 2026 | <https://docs.conan.io/2/reference/commands/install.html> | `--output-folder`, `--build`, `--lockfile`, `--profile:build/host` |
| 공식 문서 | Conan 2: `conan lock create` | JFrog | 2026 | <https://docs.conan.io/2/reference/commands/lock/create.html> | 경로 인자와 `--lockfile-out` |
| 공식 문서 | Conan 2: `cmake_layout` | JFrog | 2026 | <https://docs.conan.io/2/reference/tools/cmake/cmake_layout.html> | 빌드·generators 폴더 구조 |
| 공식 소스 | `conan/tools/cmake/layout.py` (develop2) | conan-io/conan | 2026 | <https://github.com/conan-io/conan/blob/develop2/conan/tools/cmake/layout.py> | `folders.generators = folders.build/generators` |
| 공식 소스 | `conan/internal/model/conf.py` (develop2) | conan-io/conan | 2026 | <https://github.com/conan-io/conan/blob/develop2/conan/internal/model/conf.py> | `tools.build:*`와 `tools.cmake.cmaketoolchain:generator`의 정식 이름 |
| 공식 문서 | Conan 2: `CMakeToolchain` | JFrog | 2026 | <https://docs.conan.io/2/reference/tools/cmake/cmaketoolchain.html> | 플래그 conf가 `*_FLAGS_INIT`로 전달되는 경로 |
| 공식 문서 | Conan 2: cross building (host/build context) | JFrog | 2026 | <https://docs.conan.io/2/tutorial/consuming_packages/cross_building_with_conan.html> | host·build context 정의 |
| 공식 recipe | `recipes/cyclonedds/all/conanfile.py` | conan-io/conan-center-index | 2026 | <https://github.com/conan-io/conan-center-index/blob/master/recipes/cyclonedds/all/conanfile.py> | 옵션 이름, `tool_requires`, CMake target |
| 공식 recipe | `recipes/spdlog/all/conanfile.py`, `conandata.yml` | conan-io/conan-center-index | 2026 | <https://github.com/conan-io/conan-center-index/blob/master/recipes/spdlog/all/conanfile.py> | 1.17.0 존재, 옵션, `fmt` 매핑, target |
| 공식 문서 | CMake: `cmake(1)` | Kitware | 2026 | <https://cmake.org/cmake/help/latest/manual/cmake.1.html> | `-S`, `-B`, `-G`, `--build`, `--parallel`, `--toolchain` |
| 공식 문서 | CMake: generator expressions | Kitware | 2026 | <https://cmake.org/cmake/help/latest/manual/cmake-generator-expressions.7.html> | `COMPILE_LANG_AND_ID` (3.15+) |
| 공식 소스 | `src/core/ddsc/include/dds/dds.h` (tag 0.10.2) | eclipse-cyclonedds | 2022 | <https://github.com/eclipse-cyclonedds/cyclonedds/blob/0.10.2/src/core/ddsc/include/dds/dds.h> | `dds_return_loan`, `DDS_DOMAIN_DEFAULT` |
| 공식 소스 | `src/tools/idlc/src/idlc.c` (tag 0.10.2) | eclipse-cyclonedds | 2022 | <https://github.com/eclipse-cyclonedds/cyclonedds/blob/0.10.2/src/tools/idlc/src/idlc.c> | `idlc -l`, `-o` 옵션 |
| 공식 소스 | `docs/manual/options.md` (tag 0.10.2) | eclipse-cyclonedds | 2022 | <https://github.com/eclipse-cyclonedds/cyclonedds/blob/0.10.2/docs/manual/options.md> | `General`의 자식 요소 목록 |
| 공식 소스 | `src/core/ddsi/src/ddsi_config.c` (tag 0.10.2) | eclipse-cyclonedds | 2022 | <https://github.com/eclipse-cyclonedds/cyclonedds/blob/0.10.2/src/core/ddsi/src/ddsi_config.c> | `NetworkInterfaceAddress`의 deprecated 처리 |
| 공식 문서 | Eclipse Cyclone DDS 0.10.2 문서 | Eclipse Foundation | 2022 | <https://cyclonedds.io/docs/cyclonedds/0.10.2/> | 0.10.2 계열의 문서 진입점 |

## 2. 주장과 대조 결과

확인 날짜는 모두 2026-09-22이다. "근거 형태"는 공식 문서·소스 대조인지, 저장소에 기록된
산출물을 읽은 것인지를 구분한다.

### 2.1 Nix와 도구 체인

| # | 본문의 주장 | 출처 | 적용 조건 | 근거 형태 |
|---|---|---|---|---|
| N1 | Nixpkgs 26.05의 기본 CMake는 4.x | `nixos-26.05` 브랜치의 `cmake/package.nix`에 `version = "4.1.6"` | `nixos-26.05` 브랜치 기준 | 소스 대조 |
| N2 | Nixpkgs 25.05가 3.31 계열 CMake를 제공 | `nixos-25.05` 브랜치의 `cmake/package.nix`에 `version = "3.31.6"` | `nixos-25.05` 브랜치 기준 | 소스 대조 |
| N3 | 26.05의 Conan은 2.x | `nixos-26.05`의 `conan/package.nix`에 `version = "2.28.1"` | baseline "Conan 2.28"과 일치 | 소스 대조 |
| N4 | Conan 실행에 별도 `python3`·`uv`가 필요 없다 | 같은 파일이 `python3Packages.buildPythonApplication`을 사용 | Nixpkgs 패키지로 설치한 Conan에 한정 | 소스 대조 |
| N5 | `pkgsCross.aarch64-multiplatform-musl`의 타깃 삼중자는 `aarch64-unknown-linux-musl` | `lib/systems/examples.nix`의 `config = "aarch64-unknown-linux-musl"` | Nixpkgs 26.05 | 소스 대조 |
| N6 | 교차 컴파일러 실행 파일에는 target prefix가 붙는다 | Nixpkgs 매뉴얼 cross-compilation 장, `stdenv.cc.targetPrefix` | 교차 `stdenv`에 한정 | 문서 대조 |
| N7 | `flake.lock`이 두 입력의 revision과 content hash를 고정한다 | 예제의 `flake.lock`에 `rev`, `narHash` 기록 | 예제 프로젝트 | 파일 읽기 |
| N8 | 예제가 쓰는 `pkgs.nixfmt-rfc-style` | `nixos-26.05`의 `aliases.nix`에서 `warnAlias`로 `nixfmt`를 가리킴 (2025-07-14 추가) | 26.05에서는 경고를 내는 별칭 | 소스 대조 |

### 2.2 Conan 2

| # | 본문의 주장 | 출처 | 적용 조건 | 근거 형태 |
|---|---|---|---|---|
| C1 | 프로필에 `[settings]`, `[options]`, `[conf]`, `[platform_tool_requires]` 섹션이 있다 | Conan 2 profiles reference의 섹션 목록 | Conan 2 | 문서 대조 |
| C2 | 프로필은 Jinja2로 렌더링되고 `os.getenv`를 쓸 수 있다 | 같은 문서: "the Python `os` module is added to the render context" | Conan 2 | 문서 대조 |
| C3 | `[platform_tool_requires]`는 host·build 프로필 양쪽에 둘 수 있다 | 같은 문서의 platform tool requires 설명 | 선언한 버전이 recipe의 범위와 정확히 일치해야 함 | 문서 대조 |
| C4 | `conan install`이 `--output-folder`, `--build=missing`, `--lockfile`, `--profile:build`, `--profile:host`를 받는다 | `conan install` reference | Conan 2 | 문서 대조 |
| C5 | `conan lock create <path> --lockfile-out=...`로 lockfile을 만든다 | `conan lock create` reference | Conan 2 | 문서 대조 |
| C6 | `cmake_layout`의 generators 폴더는 `build/Release/generators` | `layout.py`의 `folders.generators = os.path.join(folders.build, "generators")`와 단일 구성 시 `build/<build_type>` | 단일 구성 생성기(`Unix Makefiles`) + `build_type=Release` | 소스 대조 |
| C7 | `tools.build:compiler_executables`, `tools.build:cflags`, `tools.build:cxxflags`, `tools.build:exelinkflags`가 정식 conf 이름이다 | `conf.py`의 정의 목록 | Conan 2 | 소스 대조 |
| C8 | `tools.cmake.cmaketoolchain:generator`가 정식 conf 이름이다 | `conf.py`: "User defined CMake generator to use instead of default" | Conan 2 | 소스 대조 |
| C9 | conf의 링커 플래그가 실제 링크에 반영된다 | `CMakeToolchain` 문서: `exelinkflags` → `CMAKE_EXE_LINKER_FLAGS_INIT`, `cflags` → `CMAKE_C_FLAGS_INIT` | `CMakeToolchain` 생성기 사용 시 | 문서 대조 |
| C10 | host는 결과물이 실행될 플랫폼, build는 도구가 실행될 플랫폼 | Conan 2 cross building 튜토리얼의 context 정의 | Conan 2 | 문서 대조 |
| C11 | 예제 lockfile이 `cmake/3.31.6#platform`을 build requirement로 기록한다 | `conan-native.lock`, `conan-aarch64.lock` | 예제 프로젝트 | 파일 읽기 |

### 2.3 Cyclone DDS와 spdlog recipe

| # | 본문의 주장 | 출처 | 적용 조건 | 근거 형태 |
|---|---|---|---|---|
| R1 | `cyclonedds` recipe가 `cmake/[>=3.16 <4]`를 요구한다 | recipe의 `build_requirements`: `self.tool_requires("cmake/[>=3.16 <4]")` | ConanCenter의 현재 recipe revision | 소스 대조 |
| R2 | `shared`, `with_ssl`, `with_shm`, `enable_security`, `enable_discovery`가 유효한 옵션 이름이다 | recipe의 `options` dict | 동일 | 소스 대조 |
| R3 | ConanCenter에 `cyclonedds/0.10.2`가 있다 | recipe의 `conandata.yml`에 0.10.2 항목 | 0.10.2/0.10.3/0.10.4/0.10.5/11.0.1 제공 | 소스 대조 |
| R4 | CMake target `CycloneDDS::ddsc`가 존재한다 | recipe의 component 설정: `components["CycloneDDS"].set_property("cmake_target_name", "CycloneDDS::ddsc")` | 전역 target 이름은 `CycloneDDS::CycloneDDS` | 소스 대조 |
| R5 | `find_package(CycloneDDS CONFIG)`로 찾는다 | recipe의 `set_property("cmake_file_name", "CycloneDDS")` | `CMakeDeps` 생성기 | 소스 대조 |
| R6 | security를 끄면 정적 빌드 제약을 피한다 | recipe `validate()`: 11 미만에서 `enable_security` + 비-shared는 `ConanInvalidConfiguration` | 0.10.2는 "11 미만"에 해당 | 소스 대조 |
| R7 | 교차 빌드에서 recipe가 host용 `idlc`를 만든다 | recipe의 `_has_idlc()`가 `self.settings.os`(host)를 기준으로 `BUILD_IDLC`를 켠다 | Android/iOS 계열 제외 | 소스 대조 |
| R8 | ConanCenter에 `spdlog/1.17.0`이 있고 `fmt/12.1.0`과 짝을 이룬다 | spdlog `conandata.yml`의 버전 목록과 `fmt_version_mapping` | 예제 lockfile의 `fmt/12.1.0`과 일치 | 소스 대조 |
| R9 | target `spdlog::spdlog`를 링크한다 | spdlog recipe: `header_only`가 거짓이면 target 이름이 `spdlog::spdlog` | `header_only=False`일 때만 | 소스 대조 |
| R10 | `shared`, `header_only`, `use_std_fmt`가 유효한 spdlog 옵션이다 | spdlog recipe의 `options` dict | `use_std_fmt=True`는 C++20과 최소 컴파일러를 요구 | 소스 대조 |
| R11 | 예제 프로필의 `compiler.cppstd=17`이 두 recipe의 최소 요구를 만족한다 | cyclonedds `_min_cppstd = "14"`, spdlog `check_min_cppstd(self, 11)` | `use_std_fmt=False` | 소스 대조 |

### 2.4 CMake

| # | 본문의 주장 | 출처 | 적용 조건 | 근거 형태 |
|---|---|---|---|---|
| K1 | `-S`, `-B`, `-G`가 source·build·생성기를 지정한다 | `cmake(1)` 매뉴얼 | CMake 3.13+ | 문서 대조 |
| K2 | `CMAKE_TOOLCHAIN_FILE`로 toolchain을 전달한다 | 같은 매뉴얼의 `--toolchain` 설명 | 상대 경로는 build 디렉터리 기준 | 문서 대조 |
| K3 | `cmake --build <dir> --parallel N`이 `make -C <dir> -jN`과 같은 빌드를 수행한다 | 같은 매뉴얼의 `--build`, `--parallel` | `Unix Makefiles` 생성기 | 문서 대조 |
| K4 | `$<COMPILE_LANG_AND_ID:CXX,GNU>`가 언어·컴파일러 조건을 표현한다 | generator expressions 매뉴얼, "Version added 3.15" | CMake 3.15+ | 문서 대조 |
| K5 | `project(... LANGUAGES C CXX)`로 두 컴파일러를 활성화한다 | `project()` 명령 문서 | - | 문서 대조 |

### 2.5 DDS와 IDL

| # | 본문의 주장 | 출처 | 적용 조건 | 근거 형태 |
|---|---|---|---|---|
| D1 | `idlc -l c -o <dir> <file>`가 유효한 호출이다 | 0.10.2 `idlc.c` 옵션 표: `'l' <language>` (기본 `c`), `'o' <directory>` | Cyclone DDS 0.10.2 | 소스 대조 |
| D2 | `dds_return_loan(entity, buf, bufsz)` 시그니처 | 0.10.2 `dds.h`의 선언 | 0.10.2 | 소스 대조 |
| D3 | `DDS_DOMAIN_DEFAULT`가 설정 파일의 domain을 쓰겠다는 뜻이다 | 0.10.2 `dds.h`의 `dds_create_participant` 설명과 `dds_public_impl.h`의 `#define DDS_DOMAIN_DEFAULT ((uint32_t) 0xffffffffu)` | 0.10.2 | 소스 대조 |
| D4 | `string<64>`가 C에서 `char source[65]`로 매핑된다 | 예제의 `generated/Telemetry.h` (0.10.2 `idlc` 생성물) | 0.10.2 `idlc`, `-l c` | 파일 읽기 |
| D5 | `CYCLONEDDS_URI`로 설정 XML을 전달한다 | 0.10.2 `docs/manual/options.md` 도입부와 `ddsi_config.c`의 설정 파싱 | 0.10.2 | 소스 대조 |
| D6 | `General/NetworkInterfaceAddress`의 상태 | 0.10.2 `options.md`의 `General` 자식 목록에 없고, `ddsi_config.c`가 "deprecated configuration option. Migrate to using General/Interfaces."를 출력한다 | 0.10.2에서 동작하지만 deprecated | 소스 대조 |
| D7 | 0.10.2에서 권장하는 interface 지정 방식 | 0.10.2 `options.md`: `//CycloneDDS/Domain/General/Interfaces/NetworkInterface`와 `[@address]`, `[@name]` 속성 | 0.10.2 | 소스 대조 |
| D8 | reliability를 RELIABLE로 지정해도 durability 기본값은 VOLATILE이다 | OMG DDS 1.4 사양의 기본 QoS, Cyclone DDS 0.10.2 `dds.h`의 QoS 설정 API | 명시적으로 durability를 설정하지 않은 경우 | 문서 대조 |

## 3. 확인하지 못한 항목

| 주장 | 왜 확인하지 못했는가 |
|---|---|
| `nix develop` 출력의 각 줄 문자열과 CMake 3.31.x 표기 | 이 환경(Windows, Nix 없음)에서 셸을 실행할 수 없다 |
| `conan graph info` 출력에 `cmake/3.31.x#platform - Platform` 줄이 그대로 나온다 | 명령을 실행할 수 없고, 출력 형식을 명시한 공식 문서를 찾지 못했다 |
| aarch64 결과물의 ELF에 `INTERP`·`NEEDED`가 없다 | 교차 빌드와 `readelf`를 실행할 수 없다. 저장소에 aarch64 결과물이 기록되어 있지 않다 |
| domain ID 상한 232 | 예제 소스가 쓰는 값이다. Cyclone DDS 0.10.2 소스와 문서에서 이 상한을 명시한 곳을 찾지 못했다 |
| 장치 간 LAN discovery 동작과 WSL2 네트워크 서술 | 물리 장치 두 대와 실행 환경이 필요하다 |

## 4. 주의점

- `cyclonedds` recipe는 `configure()`에서 `compiler.cppstd`와 `compiler.libcxx`를 제거한다.
  프로필에 두 값을 적어도 이 패키지의 binary package ID에는 반영되지 않는다.
- `CMakeDeps`가 출력하는 "Conan: Target declared" 메시지는 전역 target 이름을 사용한다.
  component target 이름과 다를 수 있다.
- `spdlog/1.17.0`의 `fmt` 버전은 recipe의 `fmt_version_mapping`이 정한다. `conanfile.py`에
  `fmt`를 직접 요구하지 않아도 lockfile에는 `fmt`가 나타난다.
- Cyclone DDS 0.10 계열 문서 사이트에는 0.10.2와 0.10.5가 모두 있다. baseline과 다른
  patch 버전의 문서를 링크하면 설정 요소 목록이 달라질 수 있다.
