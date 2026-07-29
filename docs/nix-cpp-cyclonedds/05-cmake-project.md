# 5. CMake 프로젝트와 spdlog 연결

## 학습 목표

- Conan이 만든 CMake target을 찾는다.
- IDL 생성 코드와 C++ 실행 파일의 링크 관계를 구성한다.
- configure 결과를 검사한다.

## 5.1 package 찾기

[`CMakeLists.txt`](./assets/cyclonedds-cross-demo/CMakeLists.txt)는 package config 모드로
두 라이브러리를 찾는다.

```cmake
find_package(CycloneDDS REQUIRED CONFIG)
find_package(spdlog REQUIRED CONFIG)
```

Conan의 `CMakeDeps`가 만든 파일을 찾으려면 configure 때
`conan_toolchain.cmake`를 전달해야 한다. 시스템에 우연히 설치된 다른 버전을 찾는
방식이 아니다.

## 5.2 생성 C 코드 묶기

```cmake
add_library(telemetry_type STATIC generated/Telemetry.c)
target_include_directories(
  telemetry_type
  PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/generated"
)
target_link_libraries(telemetry_type PUBLIC CycloneDDS::ddsc)
```

IDL 생성 코드는 Cyclone DDS의 C runtime을 사용한다. `PUBLIC` 링크이므로
`telemetry_type`을 사용하는 publisher와 subscriber에도 `ddsc` 요구사항이 전달된다.

## 5.3 실행 파일 만들기

두 실행 파일의 공통 규칙을 함수로 묶는다.

```cmake
function(add_demo_executable target source)
  add_executable(${target} ${source})
  target_link_libraries(${target} PRIVATE telemetry_type spdlog::spdlog)
endfunction()

add_demo_executable(dds_publisher src/publisher.cpp)
add_demo_executable(dds_subscriber src/subscriber.cpp)
```

파일 경로 대신 imported target을 연결하면 include path, compile definition, 전이
라이브러리를 Conan이 전달한다.

## 5.4 경고 옵션

예제는 GNU C++ 컴파일러에만 경고를 적용한다.

```cmake
target_compile_options(
  ${target}
  PRIVATE
    $<$<COMPILE_LANG_AND_ID:CXX,GNU>:-Wall;-Wextra;-Wpedantic>
)
```

generator expression `$<...>`은 조건이 참인 언어와 컴파일러에만 값을 적용한다.

## 5.5 configure 검사

Conan install 뒤 CMake configure를 실행하면 다음 항목을 확인한다.

```text
-- The C compiler identification is GNU ...
-- The CXX compiler identification is GNU ...
-- Conan: Target declared 'CycloneDDS::ddsc'
-- Conan: Target declared 'spdlog::spdlog'
-- Build files have been written to: .../build/.../app
```

네이티브 configure에서 aarch64 컴파일러가 보이거나 교차 configure에서 x86_64
컴파일러가 보이면 host profile 또는 toolchain 경로를 잘못 사용한 것이다.

## 연습문제

1. `make -C build/native/app help`에서 세 target을 찾는다.
2. `cmake --build build/native/app --target telemetry_type --verbose`로 실제 컴파일 명령을
   확인한다.
3. `spdlog::spdlog`를 링크 목록에서 잠시 제거하고 나타나는 차이를 확인한 뒤 복구한다.

## 요약

- `CMakeDeps`가 만든 config를 `find_package(... CONFIG)`로 읽는다.
- 생성 C 코드는 별도 target으로 묶어 관계를 단순화한다.
- Conan target은 include, compile option, 전이 링크 정보를 함께 전달한다.
