# 4. Conan recipe와 교차 프로필

## 학습 목표

- `conanfile.py`와 profile의 책임을 구분한다.
- build profile과 host profile을 사용한다.
- Nix CMake를 Conan의 platform tool로 선언한다.

## 4.1 `conanfile.py`는 의존성 선언이다

예제의 [`conanfile.py`](./assets/cyclonedds-cross-demo/conanfile.py)는 두 직접 의존성을
선언한다.

```python
def requirements(self):
    self.requires("cyclonedds/0.10.2")
    self.requires("spdlog/1.17.0")
```

Conan이 이 파일을 읽는다. `python conanfile.py`로 실행하지 않으며 `uv`도 필요하지 않다.

`CMakeDeps`는 `find_package()`가 읽을 package config를 만든다. `CMakeToolchain`은
컴파일러와 빌드 옵션을 담은 `conan_toolchain.cmake`를 만든다.

## 4.2 정적 옵션

최종 aarch64 실행 파일에 공유 라이브러리를 남기지 않도록 기본 옵션을 고정한다.

```python
default_options = {
    "cyclonedds/*:shared": False,
    "cyclonedds/*:with_ssl": False,
    "cyclonedds/*:with_shm": False,
    "cyclonedds/*:enable_security": False,
    "spdlog/*:shared": False,
    "fmt/*:shared": False,
}
```

Security와 shared memory를 끄면 OpenSSL과 Iceoryx를 추가하지 않아도 된다. UDP discovery와
기본 DDS 통신은 유지한다.

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

교차 설치에서는 host 프로필만 바뀐다.

## 4.4 컴파일러 경로

프로필은 Jinja 문법으로 Flake 환경 변수를 읽는다.

```ini
{% set target_cxx = os.getenv("AARCH64_CXX") %}

[conf]
tools.build:compiler_executables={"c": "...", "cpp": "{{ target_cxx }}"}
```

`compiler.version`, `compiler.libcxx`, `compiler.cppstd`는 Conan의 binary package ID에
포함된다. 실제 컴파일러와 값을 맞추지 않으면 잘못된 cache가 재사용될 수 있다.

## 4.5 Nix CMake를 platform tool로 사용

Cyclone DDS recipe는 CMake를 `tool_requires`로 요청한다. 다음 선언은 Conan에게 정확한
CMake가 이미 플랫폼에 있다고 알려준다.

```ini
[platform_tool_requires]
cmake/{{ cmake_version }}
```

정상 graph에는 다음과 같은 항목이 나타난다.

```text
Build requirements
    cmake/3.31.x#platform - Platform
```

ConanCenter에서 CMake binary를 내려받는다면 버전이 recipe 범위와 일치하지 않거나
`[platform_tool_requires]`가 잘못된 profile context에 들어간 것이다.

## 4.6 정적 링크 플래그

aarch64 host 프로필에는 다음 conf가 있다.

```ini
tools.build:cflags=["-static"]
tools.build:cxxflags=["-static"]
tools.build:exelinkflags=["-static"]
```

`*:shared=False`는 라이브러리 종류를 정하고, `-static`은 최종 링크에서 정적 라이브러리를
선택하도록 한다. 두 설정은 역할이 다르므로 모두 필요하다.

## 4.7 lockfile

두 dependency graph를 각각 확인한 후 lockfile을 만든다.

```console
$ conan lock create conanfile.py \
    --lockfile-out=conan-native.lock \
    --profile:build=profiles/build-x86_64 \
    --profile:host=profiles/host-x86_64

$ conan lock create conanfile.py \
    --lockfile-out=conan-aarch64.lock \
    --profile:build=profiles/build-x86_64 \
    --profile:host=profiles/host-aarch64-musl
```

이후 `conan install`에 `--lockfile=...`을 추가한다. 의존성을 의도적으로 갱신할 때만
lockfile을 다시 만든다.

## 직접 확인

```console
$ conan graph info . \
    --profile:build=profiles/build-x86_64 \
    --profile:host=profiles/host-aarch64-musl
```

graph에서 `cyclonedds/0.10.2`, `spdlog/1.17.0`, aarch64 host setting, platform CMake를
확인한다.

## 요약

- recipe는 무엇을, profile은 어떤 환경으로 빌드할지 정한다.
- 교차 빌드에는 build와 host 프로필이 모두 필요하다.
- platform tool 선언으로 CMake의 소유권을 Nix에 유지한다.
- library option과 linker flag를 모두 정적으로 설정한다.
