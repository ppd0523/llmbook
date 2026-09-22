# 1. 도구의 역할과 C++ 빌드 흐름

## 학습 목표

- 컴파일과 링크를 구분한다.
- Nix, Conan, CMake, Make가 개입하는 시점을 설명한다.
- 네이티브 빌드와 교차 빌드의 build/host 플랫폼을 구분한다.
- 이 자료가 왜 aarch64-musl 정적 링크를 선택하는지 설명한다.

## 1.1 소스 파일은 바로 실행할 수 없다

C++ 소스가 실행 파일이 되기까지 크게 두 단계를 거친다.

```text
publisher.cpp ──컴파일──> publisher.o
Telemetry.c   ──컴파일──> Telemetry.o

publisher.o + Telemetry.o + libddsc.a + libspdlog.a
                         └────링크────> dds_publisher
```

컴파일은 각 소스 파일을 목적 파일로 바꾼다. 링크는 목적 파일과 라이브러리를 모아 최종
실행 파일을 만든다. 헤더를 찾지 못하면 대개 컴파일 단계 문제이고, `undefined reference`
오류는 대개 링크 단계 문제다.

이 구분은 이 책 전체에서 반복해서 쓰인다. 오류 메시지를 읽을 때 먼저 던질 질문은 "어느
단계에서 멈췄는가"다.

## 1.2 네 도구는 서로 대체 관계가 아니다

Nix는 개발 셸에 프로그램을 준비한다. Conan은 Cyclone DDS와 spdlog의 소스와 빌드 옵션을
관리한다. CMake는 애플리케이션 타깃과 링크 관계를 정의한다. Make는 CMake가 생성한 실제
명령을 실행한다.

```console
$ nix develop
$ conan install ...
$ cmake -S . -B build/... -G "Unix Makefiles" ...
$ make -C build/... -j4
```

네 명령은 같은 작업을 네 번 하는 것이 아니라 서로 다른 층을 차례로 처리한다. 층이
나뉘어 있으므로 실패했을 때 어느 도구의 문제인지 물어볼 수 있다.

## 1.3 build와 host

이 자료에서 플랫폼은 다음처럼 정의한다.

| 이름 | CPU | 역할 |
|---|---|---|
| build 플랫폼 | x86_64 | CMake, Make, Conan, `idlc`를 실행 |
| native host | x86_64 | 개발 PC에서 테스트할 프로그램 실행 |
| cross host | aarch64 | 대상 Linux에서 최종 프로그램 실행 |

host는 "빌드를 실행하는 PC"가 아니라 **결과물이 실행될 플랫폼**이다. 일상어의 "호스트
PC"와 뜻이 반대에 가까우므로 주의한다. 네이티브 빌드에서는 build와 host가 모두 x86_64다.
교차 빌드에서는 build가 x86_64이고 host가 aarch64다.

## 1.4 왜 aarch64-musl 정적 링크인가

대상 장치에는 Nix가 없다. 일반적인 Nix GCC로 만든 동적 실행 파일은 동적 로더와 공유
라이브러리를 Nix store 경로에서 찾는다. 그 경로가 없는 장치에 실행 파일만 복사하면
실행되지 않는다.

선택지는 둘이다. 장치 쪽에 라이브러리 환경을 맞춰 주거나, 실행 파일 안에 필요한 것을
모두 넣거나다. 이 자료는 뒤쪽을 택한다. 배포 절차가 파일 복사로 끝나고, 장치의 배포판
구성에 덜 의존하기 때문이다.

그래서 도구 체인을 aarch64-musl로 잡는다. musl은 정적 링크를 전제로 설계된 작은 C 표준
라이브러리 구현이며, Nixpkgs가 `pkgsCross.aarch64-multiplatform-musl`로 이 조합의 교차
도구 체인을 제공한다. 이 도구 체인과 정적 라이브러리를 함께 쓰면 동적 인터프리터도
공유 라이브러리 의존성도 없는 실행 파일 하나가 나온다.

정적 링크가 실제로 무엇을 보장하고 무엇은 보장하지 않는지, 그리고 그것을 어떻게 검사해
판정하는지는 [8장](08-cross-build.md)에서 다룬다. 여기서는 선택의 이유까지만 기억하면
된다.

## 1.5 재현 가능성의 두 자물쇠

도구와 라이브러리는 서로 다른 파일로 고정한다.

- `flake.lock`: Nixpkgs revision과 거기서 나오는 도구 버전
- Conan lockfile: C++ recipe revision과 dependency graph

둘은 고정하는 대상이 다르므로 서로를 대신하지 못한다. 하나만 고정하면 나머지 절반이
언제든 달라질 수 있다. 앞의 것은 [3장](03-nix-development-shell.md), 뒤의 것은
[4장](04-conan-profiles.md)에서 세운다.

## 직접 확인

다음 질문에 답해 본다.

1. `spdlog` 헤더를 찾지 못한 오류는 어느 단계의 문제인가?
2. aarch64용 `idlc`를 x86_64 PC에서 실행할 수 없는 이유는 무엇인가?
3. Nix와 Conan 중 컴파일러를 소유하는 도구는 무엇인가?
4. 교차 빌드에서 build 플랫폼과 host 플랫폼은 각각 무엇인가?

## 요약

- 컴파일은 소스를 목적 파일로, 링크는 목적 파일과 라이브러리를 실행 파일로 바꾼다.
- Nix는 도구, Conan은 C++ 라이브러리, CMake는 구조, Make는 실행을 맡는다.
- host는 결과물이 실행될 플랫폼이고, 교차 빌드에서는 build와 host가 다르다.
- aarch64-musl 정적 링크는 Nix가 없는 대상에 단일 실행 파일을 배포하기 위한 선택이다.
- `flake.lock`과 Conan lockfile은 서로 다른 것을 고정하며 둘 다 필요하다.
