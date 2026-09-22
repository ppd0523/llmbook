# 5. CMake 프로젝트와 spdlog 연결

## 학습 목표

- Conan이 만든 CMake target을 찾는다.
- IDL 생성 코드와 C++ 실행 파일의 링크 관계를 구성한다.
- configure 결과를 검사한다.

## 5.1 프로젝트 선언

예제의 [`CMakeLists.txt`](./assets/cyclonedds-cross-demo/CMakeLists.txt)는 다음으로
시작한다.

```cmake
cmake_minimum_required(VERSION 3.23)

project(
  cyclonedds_cross_demo
  VERSION 1.0.0
  LANGUAGES C CXX
)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
```

언어를 `C CXX` 둘로 선언한 이유는 6장에서 다룰 IDL 생성물이 C 코드이고 애플리케이션이
C++이기 때문이다. 표준도 언어별로 따로 정한다. C++17은 4장의 프로필이 지정한
`compiler.cppstd=17`과 같은 값이다.

`cmake_minimum_required(VERSION 3.23)`은 이 프로젝트가 쓰는 기능의 하한이다. 5.4의
generator expression `$<COMPILE_LANG_AND_ID:...>`는 CMake 3.15 이상을 요구하므로 이
선언으로 충족된다.

## 5.2 package 찾기

같은 파일이 package config 모드로 두 라이브러리를 찾는다.

```cmake
find_package(CycloneDDS REQUIRED CONFIG)
find_package(spdlog REQUIRED CONFIG)
```

`CONFIG`는 라이브러리가 제공하는 설정 파일을 찾으라는 뜻이다. Conan의 `CMakeDeps`가 만든
파일을 찾으려면 configure 때 `conan_toolchain.cmake`를 전달해야 한다. 시스템에 우연히
설치된 다른 버전을 찾는 방식이 아니다.

`find_package`에 쓰는 이름 `CycloneDDS`, `spdlog`는 각 recipe가 정한 config 파일 이름이다.
패키지 이름(`cyclonedds`)과 대소문자가 다를 수 있으므로 recipe가 정한 이름을 그대로 쓴다.

## 5.3 생성 C 코드 묶기

IDL 생성 코드는 별도 라이브러리 target으로 묶는다.

```cmake
add_library(telemetry_type STATIC generated/Telemetry.c)
target_include_directories(telemetry_type PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/generated")
target_link_libraries(telemetry_type PUBLIC CycloneDDS::ddsc)
```

`CycloneDDS::ddsc`는 Cyclone DDS의 C runtime을 가리키는 imported target이다. 링크 종류를
`PUBLIC`으로 둔 것이 핵심이다. `telemetry_type`을 사용하는 publisher와 subscriber는
`generated/` include 경로와 `ddsc` 링크를 따로 적지 않아도 전달받는다.

## 5.4 실행 파일 만들기

두 실행 파일의 공통 규칙을 함수로 묶는다.

```cmake
function(add_demo_executable target source)
  add_executable(${target} ${source})
  target_link_libraries(${target} PRIVATE telemetry_type spdlog::spdlog)
  target_compile_options(
    ${target}
    PRIVATE
      $<$<COMPILE_LANG_AND_ID:CXX,GNU>:-Wall;-Wextra;-Wpedantic>
  )
endfunction()

add_demo_executable(dds_publisher src/publisher.cpp)
add_demo_executable(dds_subscriber src/subscriber.cpp)
```

파일 경로 대신 imported target을 연결하면 include path, compile definition, 전이
라이브러리를 Conan이 전달한다.

target 이름 `spdlog::spdlog`가 성립하는 것은 4.2에서 `spdlog/*:header_only=False`를
고정했기 때문이다. header only로 두면 이름이 `spdlog::spdlog_header_only`가 되고 이
`target_link_libraries`는 실패한다.

generator expression `$<$<COMPILE_LANG_AND_ID:CXX,GNU>:...>`은 조건이 참인 언어와
컴파일러에만 값을 적용한다. 여기서는 GNU C++ 컴파일러로 컴파일되는 파일에만 경고 옵션을
붙인다. `generated/Telemetry.c`는 우리가 쓴 코드가 아니라 `idlc`가 만든 코드이므로 경고
대상에서 빠진다.

## 5.5 IDL 재생성 target

같은 파일에는 실행 파일이 아닌 target이 하나 더 있다.

```cmake
add_custom_target(
  regenerate_idl
  COMMAND
    idlc -l c -o "${CMAKE_CURRENT_SOURCE_DIR}/generated"
    "${CMAKE_CURRENT_SOURCE_DIR}/idl/Telemetry.idl"
  COMMENT "Regenerating the checked-in C type support with the native idlc"
  VERBATIM
)
```

이 target은 기본 빌드에 포함되지 않는다. 이름을 지정해 부를 때만 실행된다. 생성물을
빌드마다 다시 만들지 않고 저장소에 기록해 두는 이유는 6장에서 다룬다.

`idlc`를 절대 경로 없이 호출하므로 이 target은 `idlc`가 `PATH`에 있는 셸에서만 동작한다.
그 조건을 만드는 것이 4.1에서 말한 `conanbuild.sh`이며, 실제 실행 절차는 7장에 있다.

## 5.6 configure 검사

Conan install 뒤 CMake configure를 실행하면 다음과 같은 줄이 나온다.

```text
-- The C compiler identification is GNU ...
-- The CXX compiler identification is GNU ...
-- Conan: Component target declared 'CycloneDDS::ddsc'
-- Conan: Component target declared 'CycloneDDS::idl'
-- Conan: Target declared 'CycloneDDS::CycloneDDS'
-- Conan: Target declared 'spdlog::spdlog'
-- Build files have been written to: .../build/.../app
```

`CMakeDeps`가 만든 파일은 두 종류의 target을 선언하고 서로 다른 문장을 쓴다. 패키지 전체를
가리키는 전역 target은 `Target declared`, 패키지 안의 부분을 가리키는 component target은
`Component target declared`다. Cyclone DDS의 전역 target은 `CycloneDDS::CycloneDDS`이고,
우리가 링크하는 `CycloneDDS::ddsc`는 component target이다. 따라서 `CycloneDDS::ddsc`를
`Target declared` 줄에서 찾으려 하면 보이지 않는다. spdlog는 component를 나누지 않으므로
`spdlog::spdlog`가 전역 target으로 한 줄만 나온다.

네이티브 configure에서 aarch64 컴파일러가 보이거나 교차 configure에서 x86_64
컴파일러가 보이면 host profile 또는 toolchain 경로를 잘못 사용한 것이다.

## 직접 확인

1. `make -C build/native/app help`에서 `dds_publisher`, `dds_subscriber`,
   `telemetry_type` 세 target을 찾는다.
2. `cmake --build build/native/app --target telemetry_type --verbose`로 실제 컴파일 명령을
   확인한다. `generated` 경로가 include 옵션에 들어 있는지 본다.
3. `spdlog::spdlog`를 링크 목록에서 잠시 제거하고 나타나는 차이를 확인한 뒤 복구한다.

## 요약

- `CMakeDeps`가 만든 config를 `find_package(... CONFIG)`로 읽는다.
- 생성 C 코드는 별도 target으로 묶고 `PUBLIC`으로 요구사항을 전달한다.
- target 이름은 4장에서 정한 Conan 옵션에 따라 달라진다.
- configure 로그에서 전역 target과 component target은 다른 문장으로 보고된다.
