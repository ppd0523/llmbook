# 7. C++

## 학습 목표

1. C++ compiler·build system과 Mason package의 소유권을 구분한다.
2. `compile_commands.json`을 생성해 clangd에 실제 compile option을 전달한다.
3. clangd의 LSP formatting과 project `.clang-format`을 검증한다.
4. Debug symbol이 포함된 CMake target을 CodeLLDB로 debug한다.

## 7.1 구성 요소

| 기능 | 도구 | 설치·설정 위치 |
|---|---|---|
| code navigation과 diagnostics | clangd와 clangd_extensions.nvim | Mason package와 `lang.clangd` extra |
| source formatting | clangd에 내장된 clang-format | `lang.clangd` extra와 project `.clang-format` |
| debugging | CodeLLDB와 nvim-dap | Mason package, `dap.core`, `lang.clangd` extra |
| build와 compile database | C++ compiler와 CMake | system toolchain과 project `CMakeLists.txt` |

C++ source file은 compiler option, include path, macro에 따라 의미가 달라진다. 따라서 clangd
실행 파일만 설치하는 것으로는 충분하지 않다. Project build system이 각 translation
unit의 실제 compile command를 기록한 `compile_commands.json`을 제공해야 정확한
diagnostics와 navigation을 얻을 수 있다.

## 7.2 Compiler와 build tool 준비

현재 Linux shell에서 C++ compiler와 CMake를 확인한다.

```console
$ command -v c++ cmake
/usr/bin/c++
/usr/bin/cmake
$ c++ --version
$ cmake --version
```

`c++`는 GCC의 `g++`나 Clang의 `clang++`을 가리켜도 된다. Compiler, standard library
header, CMake는 project를 실제로 build하는 system toolchain이 소유한다. Mason의
clangd와 CodeLLDB는 이 toolchain을 대신하지 않는다.

WSL에서는 출력이 `/mnt/c/.../cl.exe` 같은 Windows executable을 가리키지 않는지
확인한다. 이 장의 CMake configure·build, clangd, CodeLLDB는 모두 WSL Linux 환경에서
실행한다.

## 7.3 CMake smoke-test project

Project directory를 만든다.

```console
$ mkdir -p lazyvim-cpp-smoke/include lazyvim-cpp-smoke/src
$ cd lazyvim-cpp-smoke
$ git init
```

`lang.clangd` extra가 `.git`을 root marker로 사용하므로 이 예제에서도 project root를
명확히 만든다. 기존 Git repository 안에서 실습한다면 `git init`을 다시 실행할 필요가
없다. CMake가 생성할 build tree는 source와 분리하고 Git에서 제외한다.

파일: `<project-root>/.gitignore`

```gitignore
build/
```

CMake project를 정의한다.

파일: `<project-root>/CMakeLists.txt`

```cmake
cmake_minimum_required(VERSION 3.20)
project(lazyvim_cpp_smoke LANGUAGES CXX)

add_executable(lazyvim_cpp_smoke
  src/main.cpp
  src/calculator.cpp
)

target_include_directories(lazyvim_cpp_smoke PRIVATE include)
target_compile_features(lazyvim_cpp_smoke PRIVATE cxx_std_20)
```

Header와 구현 file을 만든다.

파일: `<project-root>/include/calculator.hpp`

```cpp
#pragma once

int add(int left, int right);
```

파일: `<project-root>/src/calculator.cpp`

```cpp
#include "calculator.hpp"

int add(int left, int right) {
  return left + right;
}
```

파일: `<project-root>/src/main.cpp`

```cpp
#include "calculator.hpp"

#include <iostream>

int main() {
  const int answer = add(20, 22);
  std::cout << "answer=" << answer << '\n';
  return 0;
}
```

Formatting policy도 project에 기록한다.

파일: `<project-root>/.clang-format`

```yaml
BasedOnStyle: LLVM
IndentWidth: 2
ColumnLimit: 100
```

## 7.4 Compile database와 Debug build

CMake configure 단계에서 compile database와 Debug build를 요청한다.

```console
$ cmake -S . -B build \
    -DCMAKE_BUILD_TYPE=Debug \
    -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
$ cmake --build build
$ test -f build/compile_commands.json
$ ./build/lazyvim_cpp_smoke
answer=42
```

`CMAKE_EXPORT_COMPILE_COMMANDS`는 Makefile과 Ninja generator에서 지원된다. 다른 generator를
쓰는 project라면 해당 build system이 제공하는 방법으로 compilation database를 만든다.

clangd는 source file의 상위 directory와 그 아래 `build/`에서
`compile_commands.json`을 찾는다. 이 예제의 `build/compile_commands.json`은 별도 설정
없이 발견된다. 다른 이름이나 외부 build directory를 쓴다면 project root에 symlink를
만들거나 `.clangd`의 `CompilationDatabase` 경로를 명시한다. 생성 파일을 수동으로
편집하지 않는다.

Debugging 전에 `cmake --build build`가 성공해야 한다. `Debug` build는 source breakpoint와
변수 inspection에 필요한 debug information을 포함하도록 compiler를 구성한다.

## 7.5 clangd 연결 확인

Project root에서 Neovim을 연다.

```console
$ nvim .
```

`src/main.cpp`에서 다음 상태를 확인한다.

```vim
:set filetype?
:LspInfo
:lua print(vim.fn.exepath("clangd"))
```

Filetype은 `cpp`, active client는 clangd여야 하며 마지막 command는 Mason의 clangd
실행 경로를 출력해야 한다. 이어서 다음 동작을 시험한다.

1. `add` 호출 위에서 `gd`를 눌러 `src/calculator.cpp`의 definition으로 이동한다.
2. `K`를 눌러 function signature를 확인한다.
3. `<leader>cr`로 parameter나 local symbol을 rename한다.
4. `<leader>ch`로 source와 header 사이를 전환한다.
5. `<C-o>`로 이전 위치로 돌아간다.

의도적으로 type error를 만든다.

파일(일부): `<project-root>/src/main.cpp`

```cpp
const int answer = add(20, "22");
```

clangd diagnostic이 표시되면 LSP가 buffer에 연결된 것이다. 앞의 project header 이동이
성공하고 `build/compile_commands.json`에 두 source file의 command가 있으면 clangd가
project 정보를 사용하고 있다고 판단할 수 있다. 확인 후 원래 code로 되돌린다.

## 7.6 Include와 compile option 진단

Header를 찾지 못하거나 project에서 쓰지 않는 C++ standard diagnostic이 나오면 plugin
option보다 compile database를 먼저 확인한다.

```console
$ rg 'calculator.cpp|main.cpp' build/compile_commands.json
$ cmake --build build --verbose
```

두 출력의 compiler, `-I` include path, `-std=` option이 project 의도와 맞는지 비교한다.
CMake option이나 source 목록을 바꾼 뒤에는 configure와 build를 다시 실행한다.

```console
$ cmake -S . -B build \
    -DCMAKE_BUILD_TYPE=Debug \
    -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
$ cmake --build build
```

clangd가 이전 database를 계속 사용하면 Neovim에서 `:LspRestart`를 실행하거나 project
root에서 다시 시작한다. Project가 실제로 build되지 않는데 clangd argument를 임의로
추가해 diagnostic만 숨기지 않는다.

## 7.7 clang-format 확인

Source의 spacing과 indentation을 일부러 흐트러뜨린 뒤 `<leader>cf`를 실행한다. clangd는
clang-format을 내장하고 project의 `.clang-format`을 읽는다.

```vim
:ConformInfo
```

`ConformInfo`에 C++ 전용 external formatter가 표시되지 않아도 정상일 수 있다. 이
가이드에서는 clangd의 LSP formatting으로 fallback한다. 다음 세 항목을 함께 확인한다.

- clangd가 현재 C++ buffer에 attach되어 있다.
- Project root 또는 상위 directory에 `.clang-format`이 있다.
- `<leader>cf` 실행 후 source가 policy에 맞게 실제로 바뀐다.

별도의 `clang-format` executable을 conform.nvim에 추가할 수도 있지만, 같은 save event에
LSP formatter와 external formatter를 모두 실행하지 않는다. Format owner는 하나로 둔다.

## 7.8 CodeLLDB debugging

`:Mason`에서 `codelldb`가 installed 상태인지 확인하고 executable 경로를 본다.

```vim
:lua print(vim.fn.exepath("codelldb"))
```

`src/main.cpp`의 `const int answer = ...` 줄에서 다음 순서로 실행한다.

1. `cmake --build build`로 최신 Debug binary를 만든다.
2. `<leader>db`로 breakpoint를 만든다.
3. `<leader>dc`를 누르고 `Launch file`을 선택한다.
4. Prompt에 `<project-root>/build/lazyvim_cpp_smoke`의 실제 경로를 입력한다.
5. 정지하면 `<leader>dO`와 `<leader>di`로 step한다.
6. `<leader>de`로 `answer`를 평가한다.
7. `<leader>dt`로 session을 종료한다.

`lang.clangd` extra는 C와 C++ filetype에 CodeLLDB launch와 attach configuration을
제공한다. Build target을 자동으로 고르는 것은 아니므로 첫 실행에서는 실행 파일 경로를
직접 선택한다.

Breakpoint가 채워진 표시로 바뀌지 않거나 엉뚱한 줄에서 멈추면 다음을 구분한다.

- CMake가 `Debug`가 아닌 기존 build directory를 재사용하지 않았는가?
- Source를 고친 뒤 binary를 다시 build했는가?
- Prompt에서 library나 object file이 아니라 executable target을 선택했는가?
- Optimized build 때문에 변수나 source line이 제거되지 않았는가?

기존 process에 attach하는 configuration은 Linux `ptrace` 정책에 막힐 수 있다. 먼저
launch debugging이 성공하는지 확인한 뒤 배포판의 보안 지침에 따라 attach 권한을
검토한다.

## 7.9 흔한 오류

| 증상 | 가장 가능성 높은 계층 | 확인과 해결 |
|---|---|---|
| clangd를 찾지 못함 | Mason/PATH | `:Mason`, `vim.fn.exepath("clangd")`, Mason log 확인 |
| Project header에 빨간 밑줄 | compile database | CMake configure, `-I` option, database 위치 확인 |
| 실제 build와 다른 C++ standard diagnostic | compile database | `-std=` option과 stale database 확인 |
| `<leader>ch`가 동작하지 않음 | extra/LSP | `lang.clangd`, clangd attach, 대응 header/source 확인 |
| `<leader>cf`가 동작하지 않음 | LSP/format policy | clangd attach, `.clang-format`, actual result 확인 |
| Debug executable prompt에서 막힘 | build/configuration | `cmake --build build`, target 경로 확인 |
| Breakpoint가 검증되지 않음 | binary/debug info | Debug build, 최신 binary, source path 확인 |
| CodeLLDB가 바로 종료 | adapter/platform | Mason log, executable, shared library compatibility 확인 |
| Attach가 거부됨 | OS security | launch 성공 후 Linux `ptrace` policy 확인 |
| WSL에서 index/build가 매우 느림 | file system | `/mnt/c` 대신 WSL Linux file system에서 비교 |

## 직접 해보기

1. `CMAKE_EXPORT_COMPILE_COMMANDS`를 끈 상태와 켠 상태에서 project header diagnostic을 비교한다.
2. `target_compile_features`의 C++ standard를 바꾸고 database의 `-std=` option을 확인한다.
3. `.clang-format`의 `IndentWidth`를 바꾼 뒤 `<leader>cf` 결과를 비교한다.
4. Release build와 Debug build에서 같은 breakpoint와 local variable inspection을 비교한다.
5. `compile_commands.json`과 `lazy-lock.json`이 각각 무엇을 기록하는지 설명한다.

## 요약

- `lang.clangd` extra는 clangd, C/C++ Treesitter, source/header 전환, CodeLLDB 설정을 연결한다.
- C++ 분석 정확도는 clangd 설치뿐 아니라 project의 `compile_commands.json`에 달려 있다.
- clangd에 내장된 clang-format이 project `.clang-format`을 formatting policy로 사용한다.
- CMake Debug target을 먼저 build한 뒤 CodeLLDB에 실제 executable 경로를 전달한다.
- Compiler/build 실패, clangd 분석 실패, CodeLLDB session 실패는 서로 다른 계층이다.

## 추가 읽을거리

- [LazyVim Clangd extra](https://www.lazyvim.org/extras/lang/clangd)
- [clangd 설치와 project 설정](https://clangd.llvm.org/installation)
- [clangd 기능과 formatting](https://clangd.llvm.org/features)
- [CMake compile database](https://cmake.org/cmake/help/latest/variable/CMAKE_EXPORT_COMPILE_COMMANDS.html)
- [CodeLLDB manual](https://github.com/vadimcn/codelldb/blob/master/MANUAL.md)

[← 6장](./06-rust.md) · [목차](./index.md) · [8장: 운영과 문제 해결 →](./08-troubleshooting.md)
