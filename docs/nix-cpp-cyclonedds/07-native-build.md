# 7. x86_64 네이티브 빌드와 실행

## 학습 목표

- 고정된 개발 셸에서 의존성을 설치하고 빌드한다.
- subscriber와 publisher의 로컬 통신을 확인한다.
- IDL 생성물을 안전하게 갱신한다.

모든 명령은
[`cyclonedds-cross-demo`](./assets/cyclonedds-cross-demo/README.md) 디렉터리에서
실행한다.

## 7.1 개발 셸 들어가기

```console
$ nix develop
```

첫 실행은 Nix store에 도구 체인을 내려받으므로 시간이 걸릴 수 있다. 셸이 열리면
버전을 확인한다.

```console
$ cmake --version
$ make --version
$ c++ --version
$ conan --version
```

Conan이 Python으로 작성되어 있어도 별도의 `python`이나 `uv` 명령은 필요하지 않다.
Nix의 Conan 패키지가 실행에 필요한 Python runtime을 자신의 의존성으로 가져온다.

## 7.2 Conan lockfile 만들기

처음 한 번 dependency graph를 고정한다.

```console
$ conan lock create . \
    --lockfile-out=conan-native.lock \
    --profile:build=profiles/build-x86_64 \
    --profile:host=profiles/host-x86_64
```

이후 install에는 lockfile을 전달한다. recipe 버전만 고정하는 것보다 dependency
revision까지 재현하기 쉽다.

## 7.3 의존성 설치

```console
$ conan install . \
    --output-folder=build/native/conan \
    --build=missing \
    --lockfile=conan-native.lock \
    --profile:build=profiles/build-x86_64 \
    --profile:host=profiles/host-x86_64
```

Conan은 `cyclonedds/0.10.2`, `spdlog/1.17.0`과 전이 의존성을 빌드하거나 cache에서
가져온다. 출력 마지막에서 generator 폴더와 `conan_toolchain.cmake`의 위치를
확인한다.

## 7.4 configure와 build

```console
$ cmake -S . -B build/native/app \
    -G "Unix Makefiles" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_TOOLCHAIN_FILE="$PWD/build/native/conan/build/Release/generators/conan_toolchain.cmake"

$ make -C build/native/app -j"$(nproc)"
```

역할을 구분하면 다음과 같다.

- Conan: 라이브러리와 CMake용 메타데이터 준비
- CMake: 빌드 규칙 생성
- Make: 생성된 규칙을 따라 컴파일과 링크 수행

`cmake --build build/native/app`도 사용할 수 있지만, 이 책에서는 각 도구의 경계를
보여 주기 위해 Make를 직접 호출한다.

## 7.5 로컬 통신

터미널 A에서 subscriber를 먼저 실행한다.

```console
$ ./build/native/app/dds_subscriber 10 20 0
```

인자는 차례로 기대 샘플 수, timeout 초, domain ID다.

터미널 B에서도 같은 프로젝트에서 `nix develop`에 들어간 후 publisher를 실행한다.

```console
$ ./build/native/app/dds_publisher 10 500 0 native-pc
```

인자는 샘플 수, 전송 간격 밀리초, domain ID, source 이름이다. subscriber가
`received all 10 samples`를 출력하면 네이티브 검증이 끝난다.

## 7.6 IDL 생성물 갱신

IDL을 수정한 경우에만 네이티브 Conan build environment를 활성화하고 명시적인
target을 실행한다.

```console
$ source build/native/conan/build/Release/generators/conanbuild.sh
$ cmake --build build/native/app --target regenerate_idl
$ git diff -- idl generated
```

`Telemetry.idl`과 `generated/`의 변경이 같은 의미를 나타내는지 검토한다. 교차
빌드에서는 이 target을 실행하지 않는다.

## 연습문제

1. 샘플 수와 전송 간격을 바꿔 로그를 비교한다.
2. domain ID를 서로 다르게 실행해 timeout을 확인한 후 복구한다.
3. `make -C build/native/app VERBOSE=1`에서 사용한 compiler와 include path를 찾는다.

## 요약

- 항상 `nix develop` 안에서 Conan, CMake, Make를 실행한다.
- dependency graph는 lockfile로 고정한다.
- subscriber를 먼저 실행하고 같은 domain의 publisher를 시작한다.
