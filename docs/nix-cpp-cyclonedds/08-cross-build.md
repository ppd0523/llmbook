# 8. aarch64-musl 정적 교차 빌드

## 학습 목표

- build profile과 host profile의 차이를 실제 빌드에 적용한다.
- aarch64용 정적 실행 파일을 만든다.
- 실행하지 않고 ELF 형식과 동적 의존성을 검사하는 절차를 수행한다.
- 정적 링크가 보장하는 것과 보장하지 않는 것을 구분한다.

7장에서 네이티브 빌드가 통과했다면 소스와 의존성 구성은 이미 검증된 상태다. 이 장에서
바뀌는 것은 host profile 하나뿐이고, 이후 실패는 도구 체인과 링크 방식의 문제로 범위가
좁아진다.

## 8.1 교차 dependency graph 고정

```console
$ conan lock create . \
    --lockfile-out=conan-aarch64.lock \
    --profile:build=profiles/build-x86_64 \
    --profile:host=profiles/host-aarch64-musl
```

7.2의 명령과 비교하면 `--profile:host`와 출력 파일 이름만 다르다. build profile은
`idlc`나 CMake처럼 x86_64 개발 PC에서 실행할 도구를, host profile은 최종 aarch64
프로그램과 링크될 라이브러리를 설명한다. 여기서 host는 빌드를 실행하는 PC라는 일상적
의미가 아니라 **결과물이 실행될 플랫폼**이라는 Conan 용어다.

두 구성의 dependency graph는 컴파일러와 옵션이 다르므로 lockfile도 따로 둔다. 예제
저장소에는 `conan-aarch64.lock`이 이미 기록되어 있다.

## 8.2 aarch64 라이브러리 준비

```console
$ conan install . \
    --output-folder=build/aarch64/conan \
    --build=missing \
    --lockfile=conan-aarch64.lock \
    --profile:build=profiles/build-x86_64 \
    --profile:host=profiles/host-aarch64-musl
```

host profile은 Nix store에 있는 `aarch64-unknown-linux-musl-gcc`와 `g++`를 사용한다.
Cyclone DDS, spdlog와 전이 라이브러리도 같은 컴파일러와 정적 옵션으로 빌드한다.
출력 폴더가 `build/native/`가 아니라 `build/aarch64/`인 점을 확인한다. 두 구성이 같은
폴더를 공유하면 이전 구성의 CMake cache가 남아 진단이 어려워진다.

## 8.3 애플리케이션 빌드

```console
$ cmake -S . -B build/aarch64/app \
    -G "Unix Makefiles" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_TOOLCHAIN_FILE="$PWD/build/aarch64/conan/build/Release/generators/conan_toolchain.cmake"

$ make -C build/aarch64/app -j"$(nproc)"
```

CMake configure 로그의 C/C++ 컴파일러가 `aarch64-unknown-linux-musl-`로 시작하는지
확인한다. 여기에 x86_64 컴파일러가 보이면 toolchain 파일 경로나 `--profile:host` 지정이
잘못된 것이므로, 빌드를 계속하지 말고 8.1부터 다시 확인한다.

이 빌드는 이미 기록된 `generated/Telemetry.c`를 컴파일하며 aarch64용 `idlc`를 실행하지
않는다.

## 8.4 실행 전에 ELF 검사

x86_64 개발 PC에서는 aarch64 프로그램을 직접 실행할 수 없다. 대신 산출물의 형식을 읽어
"대상 장치에서 실행될 수 있는 모양인가"를 확인한다. Nix 셸이 내보낸 `AARCH64_READELF`가
교차 도구 체인의 `readelf` 경로를 가리킨다.

```console
$ "$AARCH64_READELF" -h build/aarch64/app/dds_publisher
$ "$AARCH64_READELF" -l build/aarch64/app/dds_publisher
$ "$AARCH64_READELF" -d build/aarch64/app/dds_publisher
```

세 명령은 각각 ELF header, program header 목록, dynamic section을 출력한다. 출력에서
다음을 찾아 기대값과 대조한다.

| 확인할 명령 | 출력에서 찾을 것 | 기대값 | 어긋나면 의심할 것 |
|---|---|---|---|
| `readelf -h` | `Machine:` 줄 | `AArch64` | host profile의 `arch` 설정, 사용된 컴파일러 |
| `readelf -l` | `INTERP` 항목 | 항목이 없음 | 링커 플래그 `-static`이 전달되지 않음 |
| `readelf -d` | `NEEDED` 항목 | 항목이 없거나 dynamic section 자체가 없음 | 일부 라이브러리가 shared로 빌드됨 |

`INTERP`는 실행 시 동적 로더의 경로를 담는 program header다. 이 항목이 있으면 대상
장치에 같은 경로의 로더가 있어야 실행된다. `NEEDED`는 실행 시 찾아야 할 shared
library 이름 목록이다. 완전 정적 실행 파일에는 둘 다 없어야 한다.

subscriber도 같은 방식으로 검사한다.

```console
$ "$AARCH64_READELF" -h build/aarch64/app/dds_subscriber
$ "$AARCH64_READELF" -l build/aarch64/app/dds_subscriber
$ "$AARCH64_READELF" -d build/aarch64/app/dds_subscriber
```

`readelf -d`의 출력에 `/nix/store/`로 시작하는 경로가 보이는지도 함께 본다. Nix store
경로는 대상 장치에 존재하지 않으므로, 남아 있다면 그 실행 파일은 복사만으로 동작하지
않는다.

두 실행 파일의 세 검사가 모두 기대값과 같을 때에만 9장의 배포로 넘어간다. 한 항목이라도
어긋나면 대상 장치에서의 실패를 네트워크 문제로 오해하기 쉽다.

## 8.5 정적 링크가 보장하는 것과 보장하지 않는 것

1장에서 정적 musl을 선택한 이유는 "실행 파일 하나만 복사해서 실행하기 위해서"였다.
여기서는 그 선택이 실제로 무엇까지 책임지는지를 정리한다.

musl은 glibc와 같은 자리를 차지하는 C 표준 라이브러리 구현이다. 둘 중 하나가 다른
하나 위에 얹히는 관계가 아니라 서로 대체 관계이고, 이 빌드가 링크하는 libc는 musl
하나다. musl을 고른 이유는 정적 링크를 전제로 설계되어 완전 정적 실행 파일을 만들기
쉽기 때문이다. 결과적으로 이 산출물은 대상 장치에 glibc가 있든 없든, 있더라도 버전이
무엇이든 영향을 받지 않는다.

정적 링크가 보장하는 것은 다음과 같다.

- Cyclone DDS, spdlog, 전이 라이브러리를 대상 장치에 따로 설치하지 않아도 된다.
- C 표준 라이브러리를 대상 장치에서 찾지 않는다. 필요한 부분이 실행 파일 안에 있다.
- 동적 로더를 거치지 않으므로 Nix store 경로가 실행 시점에 필요하지 않다.
- Nix, Conan, 컴파일러, CMake, Make를 대상 장치에 설치하지 않아도 된다.

정적 링크가 보장하지 않는 것은 다음과 같다.

- CPU 아키텍처는 여전히 맞아야 한다. aarch64 실행 파일은 aarch64에서만 동작한다.
- Linux 커널과 그 시스템 호출 인터페이스가 필요하다. 커널까지 포함되는 것은 아니다.
- 네트워크 장치, IP 주소 설정, 방화벽 규칙은 그대로 대상 장치의 몫이다.
- 실행 권한과 파일 시스템 접근 권한은 복사 방법에 따라 달라진다.
- DDS discovery가 성공한다는 보장은 전혀 없다. 이는 9장이 다루는 별개의 계층이다.

8.4의 ELF 검사는 위 목록의 앞쪽만 확인해 준다. 뒤쪽 항목은 대상 장치에서만 확인할 수
있고, 그것이 9장을 따로 두는 이유다.

## 직접 확인

1. 네이티브와 교차 configure 로그의 컴파일러 경로를 비교한다.
2. 두 실행 파일의 ELF `Machine` 값을 확인하고, 네이티브 실행 파일에 같은 명령을 적용해
   값이 어떻게 다른지 본다.
3. `INTERP`와 `NEEDED`가 각각 무엇을 의미하는지 자신의 말로 설명한다.
4. "대상 장치에 glibc가 설치되어 있지 않아도 되는가"라는 질문에 답하고, 그 근거를 8.5의
   어느 문장에서 찾았는지 밝힌다.

## 요약

- build profile은 x86_64에서 실행할 도구를, host profile은 aarch64 결과물을 정의한다.
- 라이브러리와 애플리케이션 모두 같은 musl 교차 도구 체인으로 빌드한다.
- 복사하기 전에 ELF header의 `Machine`, `INTERP` 부재, `NEEDED` 부재를 절차로 확인한다.
- 정적 링크는 라이브러리 설치 문제를 없애지만 아키텍처, 커널, 네트워크는 그대로 남는다.
