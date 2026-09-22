# 7. x86_64 네이티브 빌드와 실행

## 학습 목표

- 고정된 개발 셸에서 dependency graph를 고정하고 의존성을 설치한다.
- 같은 플랫폼에서 먼저 빌드해 코드와 의존성이 맞는지 확인한다.
- publisher와 subscriber의 로컬 통신을 확인한다.
- IDL 생성물을 안전하게 갱신한다.

교차 빌드로 넘어가기 전에 build와 host가 모두 x86_64인 경우를 먼저 통과시킨다. 이
단계가 잡아내는 것은 소스, CMake target 연결, 의존성 구성의 문제다. 도구 체인이나
배포 문제는 8장과 9장이 맡는다.

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
Nixpkgs의 Conan 패키지는 Python 애플리케이션으로 빌드되어 있어 실행에 필요한 Python
런타임을 자신의 의존성으로 가져온다.

이후 이 장과 8장의 모든 명령은 이 셸 안에서 실행한다. 셸 밖에서 실행하면 프로필이
읽는 환경 변수가 없어 컴파일러 경로가 비고, 시스템에 설치된 다른 CMake가 사용된다.

## 7.2 네이티브 dependency graph 고정하기

4장에서 설명한 lockfile을 여기서 처음 실제로 만든다. lockfile은 recipe 버전뿐 아니라
recipe revision과 전이 의존성까지 한 파일에 적어 두는 장치다.

```console
$ conan lock create . \
    --lockfile-out=conan-native.lock \
    --profile:build=profiles/build-x86_64 \
    --profile:host=profiles/host-x86_64
```

`.`은 현재 디렉터리의 `conanfile.py`를 가리킨다. 생성된 `conan-native.lock`은 저장소에
함께 기록한다. 이 파일이 있으면 다른 사람이나 다른 시점의 빌드가 같은 recipe revision을
쓴다.

예제 저장소에는 이미 `conan-native.lock`이 기록되어 있다. 그대로 재현해 볼 때는 이
명령을 건너뛰고 7.3으로 가도 된다. 의존성을 의도적으로 올릴 때의 재생성 절차는
[10장](10-troubleshooting.md)에 있다.

## 7.3 의존성 설치

```console
$ conan install . \
    --output-folder=build/native/conan \
    --build=missing \
    --lockfile=conan-native.lock \
    --profile:build=profiles/build-x86_64 \
    --profile:host=profiles/host-x86_64
```

Conan은 `cyclonedds/0.10.2`, `spdlog/1.17.0`과 전이 의존성을 로컬 cache에서 가져오거나,
없으면 소스에서 빌드한다. `--build=missing`은 "binary가 없으면 빌드해도 좋다"는
허가이지 의존성을 최신으로 올리라는 뜻이 아니다. 무엇을 쓸지는 lockfile이 정한다.

출력 마지막에서 generator 폴더와 `conan_toolchain.cmake`의 위치를 확인한다. 예제의
layout에서는 다음 경로다.

```text
build/native/conan/build/Release/generators/conan_toolchain.cmake
```

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

`cmake --build build/native/app`도 같은 빌드를 수행한다. 이 책에서는 각 도구의 경계를
보여 주기 위해 Make를 직접 호출한다.

configure 로그에서 C/C++ 컴파일러 경로가 Nix store 아래의 네이티브 GCC인지 확인해
둔다. 8장에서 같은 줄을 교차 컴파일러와 비교하게 된다.

## 7.5 로컬 통신

터미널 A에서 subscriber를 먼저 실행한다. DDS는 브로커가 없으므로 받는 쪽이 먼저 떠
있어야 초기 샘플을 놓치지 않는다.

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

두 명령의 domain ID가 다르면 subscriber는 아무것도 받지 못한 채 timeout으로 끝난다.
이는 빌드 문제가 아니라 설정 불일치이고, 9장의 LAN 검증에서도 같은 원인이 가장 먼저
의심할 항목이다.

## 7.6 IDL 생성물 갱신

`generated/`의 C 소스와 헤더는 저장소에 기록되어 있다. IDL을 수정한 경우에만, 그리고
네이티브 빌드에서만 다시 생성한다.

```console
$ source build/native/conan/build/Release/generators/conanbuild.sh
$ cmake --build build/native/app --target regenerate_idl
$ git diff -- idl generated
```

`conanbuild.sh`를 먼저 읽어 들이는 이유는 `idlc`가 여기서 PATH에 들어오기 때문이다.
`cyclonedds` recipe가 패키지의 `bin` 경로를 build environment 정보로 내보내고, 예제의
`conanfile.py`가 `VirtualBuildEnv` 생성기를 선언해 이 스크립트를 만든다. 두 조건 중
하나라도 없으면 `idlc`를 찾지 못한다.

`Telemetry.idl`과 `generated/`의 변경이 같은 의미를 나타내는지 검토한다. 교차
빌드에서는 이 target을 실행하지 않는다. 교차 구성에서 만들어지는 `idlc`는 aarch64
바이너리여서 x86_64 개발 PC에서 실행하면 `Exec format error`가 난다.

## 직접 확인

1. 샘플 수와 전송 간격을 바꿔 로그를 비교한다.
2. domain ID를 서로 다르게 실행해 timeout을 확인한 후 복구한다.
3. `make -C build/native/app VERBOSE=1`에서 사용한 컴파일러와 include path를 찾는다.
4. `conan-native.lock`을 열어 `cyclonedds`의 recipe revision을 찾고, 그것이 `conanfile.py`의
   버전 표기와 무엇이 다른지 설명한다.

## 요약

- 항상 `nix develop` 안에서 Conan, CMake, Make를 실행한다.
- dependency graph는 lockfile로 고정하고, lockfile은 이 장의 절차에서 만든다.
- subscriber를 먼저 실행하고 같은 domain의 publisher를 시작한다.
- IDL 재생성은 네이티브 빌드에서만 수행한다.
