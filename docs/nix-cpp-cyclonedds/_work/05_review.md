---
title: 기술 검증
status: final
owner: agent
target_reader: C++와 Linux 명령을 조금 사용해 본 개발자
topic: Nix·Conan 2·CMake·Cyclone DDS 교차 빌드 서술 검증
---

# 기술 검증

## 0. 실행 검증을 하지 않았다

이 검증은 **실행 검증을 포함하지 않는다.** 검증 환경은 Windows 11이고 `nix`, `conan`,
`cmake`, `make`, `readelf`가 없다. `nix develop`, `conan install`, `conan lock create`,
`conan graph info`, CMake configure, `make`, ELF 검사, DDS 통신을 **한 건도 실행하지
않았다.** 아래의 모든 판정은 다음 두 가지 근거 중 하나다.

- **문서 대조**: 공식 문서·매뉴얼·recipe·상류 소스 코드와 본문 서술을 비교했다.
- **코드 읽기**: 예제 파일(`flake.nix`, `conanfile.py`, 프로필, `CMakeLists.txt`, `src/`,
  `generated/`, lockfile)과 작업 사본에 있던 `build/native/` 산출물을 읽고 본문 서술과
  비교했다. `build/`는 `.gitignore` 대상이라 저장소에는 기록되지 않고 현재 작업 사본에도
  없다. 따라서 생성 파일과 대조한 판정(X1, V4, 5.2의 toolchain 경로, 5.5의 subscriber 로그)은
  현재 저장소만으로는 다시 확인할 수 없다.

실행해야만 알 수 있는 항목은 "확인 불가"로 남겼고, 통과했다고 적지 않았다.

- 검증일: 2026-09-22
- 검증 대상 baseline: Nixpkgs 26.05, Conan 2.28, Cyclone DDS 0.10.2, spdlog 1.17.0
- 근거 목록: [`02_research.md`](02_research.md)

## 1. 판정 요약

| 판정 | 건수 |
|---|---|
| 확인됨 | 52 |
| 버전·적용 조건과 함께 확인됨 | 5 |
| 확인 불가 | 5 |
| 합계 | 62 |

건수는 아래 표의 행 수다. 확인됨 52건은 5절 표의 46행(5.1 9, 5.2 12, 5.3 11, 5.4 5,
5.5 9)과, 생성 파일·상류 소스와 따로 대조한 2절의 6건(X1–X6)이다.

## 2. 생성 파일·상류 소스와 대조한 주장

| # | 위치 | 확인한 사실 | 본문 서술 | 근거 형태 |
|---|---|---|---|---|
| X1 | `05-cmake-project.md` configure 출력 | `CMakeDeps`가 출력하는 "Conan: Target declared" 메시지는 전역 target 이름을 쓴다. 생성 파일 `CycloneDDSTargets.cmake`는 `'CycloneDDS::CycloneDDS'`를 선언한다. `CycloneDDS::ddsc`는 `CycloneDDS-Target-release.cmake`에서 component target으로 선언되지만 같은 메시지를 내지 않는다 | 출력 예시에 `Target declared 'CycloneDDS::CycloneDDS'`를 보이고, component target은 이 줄에 나타나지 않는다고 설명한다 | 코드 읽기(생성 파일) + recipe 대조 |
| X2 | `09-deploy-and-network.md` 네트워크 설정 | 0.10.2의 `docs/manual/options.md`에서 `General`의 자식 목록에 `NetworkInterfaceAddress`가 없고, `General/Interfaces/NetworkInterface`와 `[@address]`, `[@name]` 속성이 있다. 0.10.2의 `ddsi_config.c`는 `NetworkInterfaceAddress`를 받아들이되 "deprecated configuration option. Migrate to using General/Interfaces."를 출력한다 | `General/Interfaces/NetworkInterface`의 `address`·`name` 예시를 쓰고, 구형 `NetworkInterfaceAddress`를 만나면 새 형태로 옮기라고 안내한다 | 문서 대조 + 상류 소스 대조 |
| X3 | `08-cross-build.md` 정적 링크 서술 | 이 빌드는 musl 도구 체인을 쓴다. 링크되는 libc는 musl이고 대상 장치에는 glibc가 아예 없을 수 있다 | musl을 glibc와 같은 자리를 차지하는 C 표준 라이브러리 구현으로 설명하고, 결과물이 대상 장치의 glibc 유무와 무관하다고 서술한다 | 코드 읽기(`flake.nix`, 프로필) |
| X4 | `04-conan-profiles.md` `default_options` | 예제 `conanfile.py`의 `default_options`는 아홉 항목이다. spdlog recipe는 `header_only`가 참이면 `spdlog::spdlog_header_only`를 쓰므로 `header_only=False`는 `spdlog::spdlog` target 이름이 성립하는 조건이다 | 아홉 항목을 모두 보이고 `header_only=False`의 역할을 밝힌다 | 코드 읽기 + recipe 대조 |
| X5 | `04-conan-profiles.md` `compiler_executables` | `profiles/host-aarch64-musl`은 `{"c": "{{ target_cc }}", "cpp": "{{ target_cxx }}"}`이고, `target_cc`는 `AARCH64_CC`를 읽는다 | C와 C++ 컴파일러 항목을 모두 보인다 | 코드 읽기 |
| X6 | `index.md` 공식 참고 자료 | baseline은 0.10.2이고 0.10.2 문서 사이트가 따로 있다. 다른 patch 버전 문서는 설정 요소와 API 서술이 0.10.2 소스와 같다고 보장되지 않는다 | 0.10.2 문서를 링크한다 | 문서 대조 |

예제 자산에 관한 항목 하나를 덧붙인다. 본문 챕터의 주장은 아니다.

- `assets/cyclonedds-cross-demo/flake.nix`는 formatter로 `pkgs.nixfmt`를 쓴다.
  `pkgs.nixfmt-rfc-style`은 Nixpkgs 26.05의 `pkgs/top-level/aliases.nix`에서 `warnAlias`로
  정의된 별칭이라 평가할 때 "now the same as pkgs.nixfmt which should be used instead"
  경고가 붙는다.

## 3. 버전·적용 조건과 함께 확인한 주장

| # | 위치 | 조건 |
|---|---|---|
| V1 | `03-nix-development-shell.md`, `10-troubleshooting.md` | "`cmake/[>=3.16 <4]`를 요구한다"는 ConanCenter `cyclonedds` recipe revision에 매인 값이다. recipe revision은 lockfile(`cyclonedds/0.10.2#fcf3624443f1b31bda38578f77f8f777`)이 고정한다. 본문은 3장에 이 범위가 recipe revision에 매여 있고 lockfile이 함께 고정한다고 적는다 |
| V2 | `02-cmake-and-make.md`, `05-cmake-project.md` | `$<COMPILE_LANG_AND_ID:...>`는 CMake 3.15 이상에서만 쓸 수 있다. `CMakeLists.txt`의 `cmake_minimum_required(VERSION 3.23)`이 이를 만족한다. 본문은 두 장에 3.15 하한을 적는다 |
| V3 | `04-conan-profiles.md` | "`compiler.version`, `compiler.libcxx`, `compiler.cppstd`는 Conan의 binary package ID에 포함된다"는 일반적으로 맞지만, `cyclonedds` recipe는 `configure()`에서 `compiler.cppstd`와 `compiler.libcxx`를 `rm_safe`로 제거한다. 본문은 이 패키지에 한한 예외를 적는다 |
| V4 | `04-conan-profiles.md`, `07-native-build.md` | `source .../conanbuild.sh` 후 `idlc`를 PATH에서 찾을 수 있는 것은 `cyclonedds` recipe가 `buildenv_info`에 패키지의 `bin`을 추가하고, `conanfile.py`가 `VirtualBuildEnv`를 생성기로 선언했기 때문이다. 생성된 `conanbuildenv-release-x86_64.sh`에서 해당 PATH 추가를 확인했다. 본문은 두 전제 조건을 적는다 |
| V5 | `04-conan-profiles.md` | "`-static`은 최종 링크에서 정적 라이브러리를 선택하도록 한다"는 `CMakeToolchain` 생성기가 `tools.build:exelinkflags`를 `CMAKE_EXE_LINKER_FLAGS_INIT`로 전달하는 경로에 의존한다. 본문은 이 경로를 함께 적는다 |

## 4. 확인 불가

실행이 필요해 이 환경에서 판정할 수 없는 항목이다. 틀렸다는 뜻이 아니라, 검증하지
못했다는 뜻이다. 본문은 이 항목들을 단정 대신 확인 방법으로 서술한다.

| # | 위치 | 내용 |
|---|---|---|
| U1 | `03-nix-development-shell.md` | `nix develop`의 출력 줄과 `cmake --version`이 실제로 3.31.x를 보고하는지. `nixos-25.05`의 CMake가 3.31.6이라는 문서 대조까지만 했다 |
| U2 | `04-conan-profiles.md` | `conan graph info` 출력에 `Build requirements` / `cmake/3.31.x#platform - Platform` 줄이 그대로 나오는지. 이 출력 형식을 명시한 공식 문서를 찾지 못했다. lockfile에 `cmake/3.31.6#platform`이 기록되어 있다는 사실만 확인했다 |
| U3 | `08-cross-build.md`, `10-troubleshooting.md` | aarch64 실행 파일의 `Machine`이 `AArch64`이고 `INTERP`·`NEEDED`가 없는지. 교차 빌드 산출물이 없고 `readelf`도 실행할 수 없다 |
| U4 | `09-deploy-and-network.md` | 장치 간 LAN discovery, 역할 교체 통신, WSL2 NAT에서 multicast가 전달되지 않는다는 서술. 장치 두 대가 필요하다 |
| U5 | `src/publisher.cpp`, `src/subscriber.cpp` | domain ID 상한을 232로 둔 근거. Cyclone DDS 0.10.2 소스와 문서에서 이 상한을 명시한 곳을 찾지 못했다. 본문 챕터는 상한을 서술하지 않으므로 챕터 수정 대상은 아니다 |

## 5. 확인됨

### 5.1 Nix와 도구 체인 (문서·소스 대조)

| 위치 | 주장 | 확인 근거 |
|---|---|---|
| `index.md`, `03-nix-development-shell.md`, `10-troubleshooting.md` | 26.05의 기본 CMake는 4.x | `nixos-26.05`의 `cmake/package.nix`가 `version = "4.1.6"` |
| `03-nix-development-shell.md`, `10-troubleshooting.md`, `index.md` | 25.05가 CMake 3.31을 제공 | `nixos-25.05`의 `cmake/package.nix`가 `version = "3.31.6"`, lockfile의 `cmake/3.31.6#platform`과 일치 |
| `index.md` | Conan 2 (baseline 2.28) | `nixos-26.05`의 `conan/package.nix`가 `version = "2.28.1"` |
| `03-nix-development-shell.md`, `07-native-build.md`, `index.md` | Conan 실행에 별도 `python3`·`uv`가 필요 없다 | 같은 패키지가 `python3Packages.buildPythonApplication`이라 Python 런타임이 closure에 포함된다 |
| `03-nix-development-shell.md` | 교차 도구 이름이 `aarch64-unknown-linux-musl-` 접두사를 가진다 | `lib/systems/examples.nix`의 `aarch64-multiplatform-musl.config = "aarch64-unknown-linux-musl"`, Nixpkgs 매뉴얼의 `targetPrefix` |
| `03-nix-development-shell.md` | `pkgs.stdenv.cc`와 `pkgs.pkgsCross.aarch64-multiplatform-musl.stdenv.cc`가 두 컴파일러를 준다 | Nixpkgs cross-compilation 장의 `pkgsCross` 설명, `flake.nix` |
| `01-toolchain-mental-model.md`, `03-nix-development-shell.md` | `flake.lock`이 revision과 content hash를 고정한다 | `flake.lock`의 두 노드에 `rev`와 `narHash`가 기록되어 있다 |
| `03-nix-development-shell.md` | 프로필이 Flake 환경 변수를 읽어 버전·경로 중복을 없앤다 | `flake.nix`의 변수와 `profiles/*`의 `os.getenv` 호출이 일대일로 대응한다 |
| `03-nix-development-shell.md` | 셸이 `CONAN_HOME`을 프로젝트 아래로 설정한다 | `flake.nix`의 `export CONAN_HOME="$PWD/.conan2"` |

### 5.2 Conan 2 (문서·소스 대조)

| 위치 | 주장 | 확인 근거 |
|---|---|---|
| `04-conan-profiles.md` | 프로필이 Jinja2로 렌더링되고 `os.getenv`를 쓸 수 있다 | Conan 2 profiles reference: Python `os` 모듈이 렌더 컨텍스트에 추가된다 |
| `04-conan-profiles.md` | `[platform_tool_requires]`가 유효한 프로필 섹션이다 | 같은 문서의 섹션 목록에 포함 |
| `04-conan-profiles.md`, `10-troubleshooting.md` | platform tool 선언으로 ConanCenter CMake 다운로드를 피한다 | 같은 문서: 선언한 버전이 recipe의 `tool_requires` 범위와 일치하면 시스템 도구를 쓴다 |
| `04-conan-profiles.md`, `07-native-build.md`, `08-cross-build.md` | `conan install`의 `--output-folder`, `--build=missing`, `--lockfile`, `--profile:build`, `--profile:host` | `conan install` reference의 옵션 설명 |
| `07-native-build.md`, `08-cross-build.md` | `conan lock create <path> --lockfile-out=...` | `conan lock create` reference의 usage와 옵션 |
| `07-native-build.md`, `08-cross-build.md`, 예제 `README.md` | toolchain 경로가 `build/<config>/conan/build/Release/generators/conan_toolchain.cmake` | `conan/tools/cmake/layout.py`의 `folders.generators = folders.build/"generators"`와 단일 구성의 `build/<build_type>`. 작업 사본의 `build/native/conan/build/Release/generators/conan_toolchain.cmake`와 일치 |
| `04-conan-profiles.md` | `tools.build:cflags`, `cxxflags`, `exelinkflags`가 정식 conf 이름 | `conan/internal/model/conf.py`의 정의 |
| `04-conan-profiles.md` | `tools.build:compiler_executables`가 정식 conf 이름이고 키가 `c`, `cpp` | 같은 파일: 허용 키에 `'c'`, `'cpp'` 포함 |
| `profiles/*`(자산) | `tools.cmake.cmaketoolchain:generator`가 정식 conf 이름 | 같은 파일의 정의 |
| `index.md`, `01-toolchain-mental-model.md`, `08-cross-build.md` | host는 결과물이 실행될 플랫폼, build는 도구가 실행될 플랫폼 | Conan 2 cross building 튜토리얼의 context 정의 |
| `04-conan-profiles.md` | 세 프로필 구성과 교차 설치에서 host 프로필만 바뀐다 | `profiles/build-x86_64`, `host-x86_64`, `host-aarch64-musl`의 차이가 `arch`, 컴파일러 경로, `[options]`, 정적 플래그에 한정된다 |
| `07-native-build.md`, `10-troubleshooting.md` | `--build=missing`은 binary가 없을 때 소스 빌드를 허용할 뿐이다 | `conan install` reference의 `--build` 설명 |

### 5.3 recipe와 라이브러리 (소스 대조)

| 위치 | 주장 | 확인 근거 |
|---|---|---|
| `04-conan-profiles.md`, `index.md` | `cyclonedds/0.10.2`, `spdlog/1.17.0`이 ConanCenter에 있다 | 두 recipe의 `conandata.yml` |
| `04-conan-profiles.md` | `shared`, `with_ssl`, `with_shm`, `enable_security`가 `cyclonedds`의 유효한 옵션 | recipe의 `options` dict |
| `04-conan-profiles.md` | security와 shared memory를 끄면 OpenSSL과 Iceoryx가 빠진다 | recipe의 `requirements()`가 두 옵션에 따라서만 `openssl`, `iceoryx`를 추가한다 |
| `04-conan-profiles.md` | 그래도 UDP discovery와 기본 DDS 통신은 유지된다 | `enable_discovery`는 type/topic discovery 스위치이고, RTPS UDP 통신은 별도 옵션이 아니다 |
| `02-cmake-and-make.md`, `05-cmake-project.md`, `10-troubleshooting.md` | target 이름 `CycloneDDS::ddsc` | recipe가 component `CycloneDDS`에 `cmake_target_name = "CycloneDDS::ddsc"`를 설정한다. 생성 파일 `CycloneDDS-Target-release.cmake`에서 선언을 확인했다 |
| `05-cmake-project.md` | `find_package(CycloneDDS CONFIG)`, `find_package(spdlog CONFIG)` | recipe의 `cmake_file_name`이 각각 `CycloneDDS`, `spdlog` |
| `04-conan-profiles.md`, `05-cmake-project.md` | target 이름 `spdlog::spdlog` | spdlog recipe가 `header_only=False`일 때 `spdlog::spdlog`를 쓴다. `conanfile.py`가 `header_only=False`를 고정한다 |
| `06-dds-and-idl.md`, `10-troubleshooting.md` | 교차 빌드 중 aarch64 `idlc`를 x86_64에서 실행하면 실패한다 | recipe의 `_has_idlc()`가 host os 기준으로 `BUILD_IDLC`를 켜므로, 교차 host 컨텍스트에서 만들어지는 `idlc`는 aarch64 바이너리다 |
| `index.md`, `06-dds-and-idl.md` | 그래서 생성물을 미리 만들어 기록한다 | `generated/Telemetry.h` 머리말이 "Cyclone DDS: V0.10.2"로 기록되어 있다 |
| `04-conan-profiles.md` | lockfile이 두 graph를 각각 고정한다 | `conan-native.lock`, `conan-aarch64.lock` 모두 recipe revision과 `cmake/3.31.6#platform`을 기록한다 |
| `profiles/*`(자산) | `compiler.cppstd=17`이 두 recipe의 최소 요구를 만족한다 | cyclonedds `_min_cppstd="14"`, spdlog `check_min_cppstd(self, 11)` (`use_std_fmt=False`) |

### 5.4 CMake (문서 대조)

| 위치 | 주장 | 확인 근거 |
|---|---|---|
| `02-cmake-and-make.md` | `-S`, `-B`, `-G`의 의미 | `cmake(1)` 매뉴얼 |
| `07-native-build.md`, `08-cross-build.md` | `-DCMAKE_TOOLCHAIN_FILE=...`로 toolchain을 전달한다 | 같은 매뉴얼의 `--toolchain` 설명 |
| `02-cmake-and-make.md` | `make -C <dir> -j4`와 `cmake --build <dir> --parallel 4`가 같은 빌드를 수행한다 | 같은 매뉴얼의 `--build`, `--parallel` |
| `02-cmake-and-make.md` | `project(... LANGUAGES C CXX)`로 확장자별 컴파일러가 갈린다 | `project()` 문서. `CMakeLists.txt`와 일치 |
| `02-cmake-and-make.md` | `PUBLIC` 요구사항이 소비 타깃에 전파된다 | `target_link_libraries` 문서. `CMakeLists.txt`와 일치 |

### 5.5 DDS와 예제 코드 (소스 대조 + 코드 읽기)

| 위치 | 주장 | 확인 근거 |
|---|---|---|
| `06-dds-and-idl.md` | `idlc`가 `Telemetry.c`, `Telemetry.h`를 만든다 | `generated/`의 두 파일과 0.10.2 `idlc` 헤더 주석 |
| `CMakeLists.txt`(자산) | `idlc -l c -o <dir> <file>` | 0.10.2 `idlc.c`의 옵션 표: `-l <language>`(기본 `c`), `-o <directory>` |
| `06-dds-and-idl.md` | `std::snprintf(sample.source, sizeof(sample.source), ...)` | `generated/Telemetry.h`가 `char source[65]`로 매핑한다. `string<64>` + 종단 문자 |
| `06-dds-and-idl.md` | `dds_take` 뒤 `dds_return_loan`을 호출한다 | 0.10.2 `dds.h`의 `dds_return_loan(dds_entity_t, void**, int32_t)` 선언과 설명 |
| `06-dds-and-idl.md` | `dds_create_topic`, `dds_qset_reliability`, `dds_create_writer` 사용 | 0.10.2 `dds.h`의 선언. `src/publisher.cpp`와 일치 |
| `06-dds-and-idl.md` | domain, topic 이름, 자료형이 같아야 데이터가 흐른다 | OMG DDS 1.4의 매칭 규칙. 예제 두 소스가 같은 topic 이름과 descriptor를 쓴다 |
| `06-dds-and-idl.md` | reliability를 RELIABLE로 지정해도 durability는 기본 VOLATILE이다 | 예제 소스가 durability를 설정하지 않는다. DDS 기본 durability는 VOLATILE |
| `09-deploy-and-network.md` | `CYCLONEDDS_URI`로 설정을 전달한다 | 0.10.2의 설정 파싱 경로. 요소 이름은 X2 참조 |
| `07-native-build.md` | subscriber가 `received all 10 samples`를 출력한다 | `src/subscriber.cpp`의 로그 문자열. 작업 사본의 `build/native/subscriber.log`에도 같은 형식이 있다(이 검증에서 실행한 것이 아니라 이미 있던 로그다) |

## 6. 남은 제한

- U1~U5는 Nix가 있는 Linux 환경과 장치 두 대에서 실행 검증을 수행해야 판정할 수 있다.
  실행 검증을 마치기 전에는 이 책을 "검증 완료"로 표시하지 않는다.
