# 2. CMake와 GNU Make 기초

## 학습 목표

- `CMakeLists.txt`와 Makefile의 관계를 설명한다.
- configure와 build 단계를 구분한다.
- CMake target 기반으로 라이브러리를 연결한다.

이 장의 코드는 CMake 개념만 보이기 위한 최소 예제다. 예제 프로젝트의 실제
`CMakeLists.txt`는 [5장](05-cmake-project.md)에서 읽는다. 여기서는 Conan도 Cyclone DDS도
필요하지 않으므로, 빈 디렉터리 하나를 만들어 그대로 따라 할 수 있다.

## 2.1 CMake는 빌드 생성기다

CMake가 C++를 직접 컴파일하는 것은 아니다. `CMakeLists.txt`를 읽고 선택한 생성기에 맞는
빌드 규칙을 만든다. 이 자료는 생성기를 `Unix Makefiles`로 고정한다.

```console
$ cmake -S . -B build -G "Unix Makefiles"
$ make -C build
```

첫 명령은 configure 단계다. `CMakeLists.txt`를 해석하고 컴파일러를 찾아 build 디렉터리에
Makefile을 만든다. 두 번째 명령은 그 Makefile을 실행하는 build 단계다. 컴파일러가 실제로
호출되는 것은 두 번째 명령에서다.

## 2.2 source와 build 디렉터리를 분리한다

- `-S .`: `CMakeLists.txt`가 있는 source 디렉터리
- `-B build`: 생성 파일과 목적 파일을 둘 build 디렉터리

소스 옆에 목적 파일을 만들지 않는 방식을 out-of-source build라고 한다. 이 방식이면 build
디렉터리를 통째로 지우는 것만으로 빌드 상태를 초기화할 수 있다.

이 책에서 이 분리가 특히 중요한 이유가 하나 더 있다. 뒤에서 같은 소스로 x86_64용과
aarch64용을 각각 빌드하는데, 두 결과는 컴파일러도 라이브러리도 다르다. build 디렉터리를
`build/native`와 `build/aarch64`로 나누어 두면 두 설정이 섞이지 않는다.

## 2.3 프로젝트가 C와 C++를 함께 쓰는 이유

이 책의 애플리케이션 코드는 C++17이지만, IDL 컴파일러가 만들어 주는 타입 지원 코드는
C다. 두 언어를 함께 쓰려면 `project()`에서 둘 다 선언한다.

```cmake
cmake_minimum_required(VERSION 3.23)

project(hello_cmake LANGUAGES C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
```

이렇게 선언하면 CMake가 `.c` 파일에는 C 컴파일러를, `.cpp` 파일에는 C++ 컴파일러를
자동으로 고른다. 선언하지 않은 언어의 소스를 추가하면 configure 단계에서 실패한다.

`cmake_minimum_required`는 형식적인 한 줄이 아니라 쓸 수 있는 기능의 하한을 정하는
선언이다. 예를 들어 5장에서 쓰는 `$<COMPILE_LANG_AND_ID:CXX,GNU>` 같은 generator
expression은 CMake 3.15에서 추가되었으므로, 최소 버전을 그보다 낮게 선언한 프로젝트에서는
쓸 수 없다. 예제 프로젝트는 최소 버전을 3.23으로 두고 있어 이 조건을 만족한다.

## 2.4 target으로 관계를 표현한다

CMake에서 빌드의 단위는 파일 목록이 아니라 target이다. target은 라이브러리나 실행 파일
하나를 가리키며, 자신이 필요로 하는 include 경로·컴파일 옵션·링크 대상을 스스로 들고
다닌다.

아래는 개념을 보이기 위한 최소 구성이다. 정적 라이브러리 하나와 그것을 쓰는 실행 파일
하나를 만든다.

```cmake
add_library(greeting STATIC src/greeting.c)
target_include_directories(greeting PUBLIC include)

add_executable(hello src/main.cpp)
target_link_libraries(hello PRIVATE greeting)
```

여기서 `PUBLIC`과 `PRIVATE`은 요구사항이 어디까지 전달되는지를 정한다.

- `PUBLIC`: `greeting` 자신이 쓰고, `greeting`을 링크하는 target에도 전달한다.
- `PRIVATE`: 해당 target 안에서만 쓰고 전달하지 않는다.

`greeting`의 include 경로가 `PUBLIC`이므로 `hello`는 `include` 디렉터리를 직접 지정하지
않아도 `greeting`의 헤더를 찾는다. `hello`는 `greeting`이 어느 경로의 어떤 `.a` 파일로
빌드되는지도 알 필요가 없다. 경로 대신 이름으로 관계를 적는 것이 target 기반 빌드의
핵심이다.

`greeting`처럼 이 프로젝트가 직접 만드는 target 말고, 밖에서 가져다 쓰는 target도 있다.
`CycloneDDS::ddsc`처럼 이름에 `::`가 들어간 것이 그런 경우이며, 이를 imported target이라고
한다. 이 프로젝트가 빌드하는 것이 아니라 이미 빌드되어 있는 라이브러리를 CMake의 target
문법으로 가리키는 이름이다. imported target을 어디서 얻는지는
[4장](04-conan-profiles.md)과 [5장](05-cmake-project.md)에서 다룬다.

## 2.5 `make`와 `cmake --build`

다음 두 명령은 `Unix Makefiles` 생성기를 쓰는 이 구성에서 같은 빌드를 수행한다.

```console
$ make -C build -j4
$ cmake --build build --parallel 4
```

첫 번째는 생성된 Makefile을 그대로 실행하므로 무슨 일이 일어나는지 관찰하기 좋다. 두
번째는 생성기가 Ninja나 IDE 프로젝트로 바뀌어도 같은 명령을 쓸 수 있다. 이 자료에서는
흐름을 드러내기 위해 `make`를 직접 사용한다.

## 직접 확인

빈 디렉터리에서 2.3과 2.4의 코드로 최소 프로젝트를 만들고 configure한 뒤, 생성된 결과를
확인한다.

```console
$ cmake -S . -B build -G "Unix Makefiles"
$ test -f build/Makefile && echo "Makefile generated"
$ make -C build help
```

`make ... help`는 그 Makefile이 알고 있는 target 목록을 출력한다. 여기에 `greeting`과
`hello`가 보이면 `CMakeLists.txt`에 적은 target 선언이 Make의 규칙으로 옮겨졌다는 뜻이다.
이어서 `make -C build`로 빌드해 `build/hello`가 만들어지는지 확인한다.

## 요약

- CMake는 Makefile을 만들고 Make는 그 규칙을 실행한다.
- configure는 규칙을 만드는 단계이고, build는 컴파일러가 실제로 호출되는 단계다.
- source와 build 디렉터리를 분리하면 네이티브와 교차 빌드 설정이 섞이지 않는다.
- 라이브러리 경로 대신 CMake target으로 관계를 표현하고, `PUBLIC`과 `PRIVATE`으로 전달
  범위를 정한다.
- C와 C++ 소스가 함께 있으므로 `project()`에서 두 언어를 모두 활성화한다.
