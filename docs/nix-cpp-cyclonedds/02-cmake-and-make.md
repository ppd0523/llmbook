# 2. CMake와 GNU Make 기초

## 학습 목표

- `CMakeLists.txt`와 Makefile의 관계를 설명한다.
- configure와 build 단계를 구분한다.
- CMake target 기반으로 라이브러리를 연결한다.

## 2.1 CMake는 빌드 생성기다

CMake가 C++를 직접 컴파일하는 것은 아니다. `CMakeLists.txt`를 읽고 선택한 생성기에 맞는
빌드 규칙을 만든다. 이 자료는 생성기를 `Unix Makefiles`로 고정한다.

```console
$ cmake -S . -B build/native/app -G "Unix Makefiles"
$ make -C build/native/app
```

첫 명령은 configure 단계다. 두 번째 명령은 생성된 Makefile을 실행하는 build 단계다.

## 2.2 source와 build 디렉터리를 분리한다

- `-S .`: `CMakeLists.txt`가 있는 source 디렉터리
- `-B build/native/app`: 생성 파일과 목적 파일을 둘 build 디렉터리

소스 옆에 목적 파일을 만들지 않는 방식을 out-of-source build라고 한다. 네이티브와
aarch64 결과물도 서로 다른 디렉터리에 두므로 설정이 섞이지 않는다.

## 2.3 프로젝트가 C와 C++를 함께 쓰는 이유

애플리케이션은 C++17이지만 `idlc`가 만든 타입 지원 코드는 C다.

```cmake
project(cyclonedds_cross_demo LANGUAGES C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
```

CMake가 `.c`에는 C 컴파일러를, `.cpp`에는 C++ 컴파일러를 선택한다.

## 2.4 target으로 관계를 표현한다

예제는 생성 코드를 라이브러리로 먼저 묶는다.

```cmake
add_library(telemetry_type STATIC generated/Telemetry.c)
target_include_directories(telemetry_type PUBLIC generated)
target_link_libraries(telemetry_type PUBLIC CycloneDDS::ddsc)
```

`PUBLIC`은 `telemetry_type` 자체와 이를 사용하는 타깃 모두에 요구사항을 전달한다.
publisher는 구체적인 include 경로나 `.a` 파일 경로를 알 필요가 없다.

```cmake
add_executable(dds_publisher src/publisher.cpp)
target_link_libraries(
  dds_publisher
  PRIVATE
    telemetry_type
    spdlog::spdlog
)
```

`CycloneDDS::ddsc`, `spdlog::spdlog`는 Conan의 `CMakeDeps`가 만든 imported target이다.

## 2.5 `make`와 `cmake --build`

다음 두 명령은 이 프로젝트에서 같은 Makefile을 실행한다.

```console
$ make -C build/native/app -j4
$ cmake --build build/native/app --parallel 4
```

첫 번째는 Make를 직접 학습하기 좋다. 두 번째는 생성기가 Ninja나 IDE로 바뀌어도 같은
명령을 쓸 수 있다. 이 자료에서는 흐름을 보이기 위해 `make`를 직접 사용한다.

## 직접 확인

configure 후 다음 파일을 찾아본다.

```console
$ test -f build/native/app/Makefile
$ make -C build/native/app help
```

`help` 출력에 `dds_publisher`, `dds_subscriber`, `telemetry_type`이 있어야 한다.

## 요약

- CMake는 Makefile을 만들고 Make는 그 규칙을 실행한다.
- source와 build 디렉터리를 분리한다.
- 라이브러리 경로 대신 CMake target으로 관계를 표현한다.
- C와 C++ 소스가 함께 있으므로 두 언어를 모두 활성화한다.
