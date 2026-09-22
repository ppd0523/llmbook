# 4. Conan recipe와 교차 프로필

## 학습 목표

- `conanfile.py`와 profile의 책임을 구분한다.
- build profile과 host profile을 사용한다.
- Nix CMake를 Conan의 platform tool로 선언한다.
- lockfile이 무엇을 고정하는지 설명한다.

## 4.1 `conanfile.py`는 의존성 선언이다

예제의 [`conanfile.py`](./assets/cyclonedds-cross-demo/conanfile.py)는 두 직접 의존성을
선언한다.

```python
def requirements(self):
    self.requires("cyclonedds/0.10.2")
    self.requires("spdlog/1.17.0")
```

Conan이 이 파일을 읽는다. `python conanfile.py`로 실행하지 않으며 `uv`도 필요하지 않다.

같은 파일은 네 개의 생성기를 선언한다. `CMakeDeps`는 `find_package()`가 읽을 package
config를 만들고, `CMakeToolchain`은 컴파일러와 빌드 옵션을 담은 `conan_toolchain.cmake`를
만든다. `VirtualBuildEnv`는 빌드 도구용 환경 변수 스크립트를, `VirtualRunEnv`는 실행용
환경 변수 스크립트를 만든다.

```python
generators = "CMakeDeps", "CMakeToolchain", "VirtualBuildEnv", "VirtualRunEnv"
```

`VirtualBuildEnv`가 왜 필요한지는 7장에서 드러난다. Cyclone DDS recipe는 자기 패키지의
`bin` 디렉터리를 build 환경의 `PATH`에 추가하도록 선언하고, `VirtualBuildEnv`가 그 선언을
`conanbuild.sh`라는 셸 스크립트로 옮겨 적는다. 이 스크립트를 `source`한 셸에서만 `idlc`를
이름만으로 실행할 수 있다.

## 4.2 정적 옵션

최종 aarch64 실행 파일에 공유 라이브러리를 남기지 않도록 기본 옵션을 고정한다. 예제의
`default_options`는 아홉 항목이며, 아래는 전체다.

```python
default_options = {
    "cyclonedds/*:shared": False,
    "cyclonedds/*:with_ssl": False,
    "cyclonedds/*:with_shm": False,
    "cyclonedds/*:enable_security": False,
    "cyclonedds/*:enable_discovery": True,
    "spdlog/*:shared": False,
    "spdlog/*:header_only": False,
    "spdlog/*:use_std_fmt": False,
    "fmt/*:shared": False,
}
```

세 묶음으로 읽으면 된다.

- **정적 링크를 위한 값**: `cyclonedds/*:shared`, `spdlog/*:shared`, `fmt/*:shared`가 모두
  `False`다. `fmt`는 `conanfile.py`가 직접 요구하지 않지만 spdlog recipe가 끌어오므로
  여기서 함께 고정한다.
- **의존성을 줄이기 위한 값**: `with_ssl`, `with_shm`, `enable_security`가 `False`다.
  security와 shared memory를 끄면 OpenSSL과 Iceoryx를 추가하지 않아도 된다.
  `enable_discovery`는 켠 채로 두므로 UDP discovery와 기본 DDS 통신은 유지한다.
- **CMake target 이름을 결정하는 값**: `spdlog/*:header_only`가 `False`다. spdlog recipe는
  이 옵션이 참이면 `spdlog::spdlog_header_only`를, 거짓이면 `spdlog::spdlog`를 target
  이름으로 쓴다. 5장이 `spdlog::spdlog`에 링크할 수 있는 것은 이 값이 `False`이기
  때문이다. `use_std_fmt`는 `False`라야 C++17로 충분하다. 참이면 C++20과 더 높은 최소
  컴파일러를 요구한다.

Conan은 이런 설정값을 조합해 패키지마다 binary package ID를 계산하고, 같은 ID의 binary가
cache에 있으면 다시 빌드하지 않는다. 따라서 옵션 하나만 바꿔도 다른 binary가 된다.

## 4.3 세 프로필

| 프로필 | 사용 위치 | 결과 |
|---|---|---|
| `build-x86_64` | 모든 빌드의 build context | x86_64에서 실행할 빌드 도구 |
| `host-x86_64` | 네이티브 host context | x86_64 라이브러리 |
| `host-aarch64-musl` | 교차 host context | aarch64 정적 라이브러리 |

네이티브 설치:

```console
$ conan install . \
    --profile:build=profiles/build-x86_64 \
    --profile:host=profiles/host-x86_64 \
    --build=missing
```

교차 설치에서는 host 프로필만 바뀐다. build 프로필은 그대로 `build-x86_64`다. 빌드를
수행하는 PC가 바뀌지 않기 때문이다.

## 4.4 컴파일러 경로

프로필은 Jinja 문법으로 3장에서 개발 셸이 내보낸 환경 변수를 읽는다. aarch64 host
프로필([`profiles/host-aarch64-musl`](./assets/cyclonedds-cross-demo/profiles/host-aarch64-musl))의
해당 부분은 다음과 같다.

```ini
{% set target_cc = os.getenv("AARCH64_CC") %}
{% set target_cxx = os.getenv("AARCH64_CXX") %}

[conf]
tools.build:compiler_executables={"c": "{{ target_cc }}", "cpp": "{{ target_cxx }}"}
```

`compiler_executables`의 키는 `c`와 `cpp` 두 개이며 둘 다 채워야 한다. Cyclone DDS는 C로
작성되었고 애플리케이션은 C++이므로, 하나라도 비우면 그 언어의 컴파일러가 지정되지 않은
채 Conan의 기본 탐색에 맡겨진다. 교차 빌드에서는 그 결과가 x86_64 컴파일러다.

위 블록은 프로필의 일부만 옮긴 것이다. 생략한 부분에는 `[settings]`의 `arch=armv8`,
`compiler.version`, `[options]`의 정적 옵션, `[platform_tool_requires]`가 들어 있다.
전체는 예제 파일에서 읽는다.

`compiler.version`, `compiler.libcxx`, `compiler.cppstd`는 Conan의 binary package ID에
포함되므로 실제 컴파일러와 값을 맞추지 않으면 잘못된 cache가 재사용될 수 있다. 다만 이
규칙에는 패키지별 예외가 있다. `cyclonedds` recipe는 `configure()`에서 `compiler.cppstd`와
`compiler.libcxx`를 제거하므로, 프로필에 두 값을 적어도 이 패키지의 package ID에는
반영되지 않는다. 프로필에 값을 적는 이유는 이 패키지 하나가 아니라 graph 전체와 우리
프로젝트의 컴파일 설정을 맞추기 위해서다.

## 4.5 Nix CMake를 platform tool로 사용

Cyclone DDS recipe는 CMake를 `tool_requires`로 요청한다. 3장에서 CMake 3.31을 별도 Flake
입력으로 가져온 것은 이 요청이 `cmake/[>=3.16 <4]` 범위이기 때문이다. 이 범위는 recipe에
적힌 값이고, recipe는 판(revision)마다 달라질 수 있다. 우리 프로젝트에서 그 판을 고정하는
것은 4.7의 lockfile이다.

다음 선언은 Conan에게 정확한 CMake가 이미 플랫폼에 있다고 알려준다. `cmake_version`은
개발 셸이 내보낸 `CMAKE_PLATFORM_VERSION`에서 온다.

```ini
[platform_tool_requires]
cmake/{{ cmake_version }}
```

선언한 버전이 recipe의 요구 범위 안에 있으면 Conan은 ConanCenter에서 CMake binary를
내려받지 않고 시스템에 있는 것을 쓴다. ConanCenter에서 CMake를 내려받는다면 버전이 recipe
범위와 일치하지 않거나 `[platform_tool_requires]`가 잘못된 profile context에 들어간 것이다.

## 4.6 정적 링크 플래그

aarch64 host 프로필에는 다음 conf가 있다.

```ini
tools.build:cflags=["-static"]
tools.build:cxxflags=["-static"]
tools.build:exelinkflags=["-static"]
```

`*:shared=False`는 라이브러리 종류를 정하고, `-static`은 최종 링크에서 정적 라이브러리를
선택하도록 한다. 두 설정은 역할이 다르므로 모두 필요하다.

이 플래그가 실제 링크 명령까지 도달하는 경로는 `CMakeToolchain` 생성기를 거친다.
`CMakeToolchain`이 `tools.build:exelinkflags`를 `conan_toolchain.cmake`의
`CMAKE_EXE_LINKER_FLAGS_INIT`로, `cflags`와 `cxxflags`를 각각 `CMAKE_C_FLAGS_INIT`,
`CMAKE_CXX_FLAGS_INIT`로 옮겨 적는다. 따라서 이 conf는 `CMakeToolchain`이 만든 toolchain
파일을 configure에 전달할 때만 효력이 있다. 직접 작성한 다른 toolchain 파일로 바꾸거나
toolchain 전달을 빠뜨리면 같은 프로필로도 정적 링크가 되지 않는다.

## 4.7 lockfile이 고정하는 것

`conanfile.py`는 `cyclonedds/0.10.2`처럼 버전까지만 적는다. 같은 버전에도 ConanCenter의
recipe는 여러 판이 있고, 판이 바뀌면 옵션 기본값이나 `tool_requires` 범위가 달라질 수
있다. `conanfile.py`가 언급하지 않은 `fmt` 같은 전이 의존성의 버전도 해석 시점에 정해진다.

lockfile은 한 번 해석된 dependency graph를 파일로 굳혀 다음 해석이 같은 결과를 내도록
한다. 예제의 `conan-native.lock`과 `conan-aarch64.lock`이 고정하는 것은 다음과 같다.

- 각 패키지의 버전과 recipe revision. 예: `cyclonedds/0.10.2#fcf3624...`
- `conanfile.py`에 적지 않은 전이 의존성. 예: spdlog가 끌어오는 `fmt/12.1.0`
- build requirement. 예: `cmake/3.31.6#platform`

lockfile을 두 개 두는 이유는 host가 다르면 graph도 달라질 수 있기 때문이다. 네이티브와
교차 빌드는 서로 다른 lockfile을 쓴다.

`flake.lock`과 혼동하지 않는다. `flake.lock`은 도구(컴파일러·CMake·Conan 자체)를
고정하고, Conan lockfile은 C++ 라이브러리를 고정한다. 1장의 "두 자물쇠"가 여기서 두
번째다.

lockfile을 실제로 만드는 명령은 7장과 8장의 빌드 절차에 있다. 의존성을 의도적으로 갱신할
때만 다시 만든다.

## 직접 확인

```console
$ conan graph info . \
    --profile:build=profiles/build-x86_64 \
    --profile:host=profiles/host-aarch64-musl
```

이 명령은 설치하지 않고 해석 결과만 보여준다. 출력에서 다음 세 가지를 확인한다.

1. `cyclonedds/0.10.2`와 `spdlog/1.17.0`이 requirement로 나타난다.
2. host setting의 `arch`가 `armv8`이다.
3. CMake가 build requirement에 나타나되, 내려받을 binary가 아니라 플랫폼에 이미 있는
   것으로 표시된다.

출력 형식은 Conan 버전에 따라 달라지므로 문자열을 그대로 대조하지 말고 위 세 항목이
있는지를 본다. CMake 항목은 `conan-aarch64.lock`의 `build_requires` 목록에서도 같은 값을
확인할 수 있다.

## 요약

- recipe는 무엇을, profile은 어떤 환경으로 빌드할지 정한다.
- 교차 빌드에는 build와 host 프로필이 모두 필요하며 바뀌는 쪽은 host뿐이다.
- 옵션은 링크 방식뿐 아니라 CMake target 이름까지 결정한다.
- platform tool 선언으로 CMake의 소유권을 Nix에 유지한다.
- lockfile은 recipe revision과 전이 의존성까지 포함한 graph 전체를 고정한다.
