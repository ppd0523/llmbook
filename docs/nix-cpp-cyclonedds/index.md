---
title: "Nix·Conan·CMake로 Cyclone DDS C++ 교차 개발 환경 만들기"
version: 1.0
updated: 2026-07-29
baseline: Nixpkgs 26.05, Conan 2.28, Cyclone DDS 0.10.2, spdlog 1.17.0
---

# Nix·Conan·CMake로 Cyclone DDS C++ 교차 개발 환경 만들기

이 자료는 C++와 Linux 명령을 조금 사용해 본 독자를 대상으로 한다. Nix 개발 셸에서
도구를 준비하고, Conan으로 C++ 라이브러리를 빌드하고, CMake와 GNU Make로 애플리케이션을
완성한다. 마지막에는 x86_64 개발 PC에서 만든 완전 정적 aarch64 실행 파일을 Nix가 없는
Linux 장치에서 실행한다.

완성된 예제는 [`assets/cyclonedds-cross-demo/`](./assets/cyclonedds-cross-demo/README.md)에
있다. 설명을 읽으며 직접 파일을 만들거나 예제를 별도 작업 디렉터리에 복사해서 사용할
수 있다.

## 학습 목표

자료를 마치면 다음 작업을 설명하고 수행할 수 있다.

1. Nix, Conan, CMake, GNU Make의 책임을 구분한다.
2. Flake로 네이티브 GCC와 aarch64-musl 교차 GCC를 고정한다.
3. Conan의 build 프로필과 host 프로필이 필요한 이유를 설명한다.
4. `spdlog/1.17.0`과 `cyclonedds/0.10.2`를 소스에서 빌드한다.
5. IDL에서 생성한 C 타입을 C++17 애플리케이션에서 사용한다.
6. publisher와 subscriber를 x86_64에서 실행한다.
7. aarch64용 정적 ELF를 만들고 동적 의존성이 없음을 검사한다.
8. 서로 다른 두 Linux 장치 사이에서 DDS discovery와 데이터 교환을 확인한다.

## 도구의 책임

| 계층 | 소유하는 것 | 소유하지 않는 것 |
|---|---|---|
| Nix Flake | 컴파일러, CMake, Make, Conan의 버전과 실행 경로 | C++ 라이브러리 버전 |
| Conan | Cyclone DDS, spdlog, 전이 라이브러리와 빌드 옵션 | 컴파일러와 CMake 설치 |
| CMake | 소스 파일, 타깃, include 경로, 링크 관계 | 라이브러리 다운로드 |
| GNU Make | CMake가 만든 빌드 규칙 실행 | 프로젝트 구조 결정 |
| 애플리케이션 | DDS domain, topic, 데이터 흐름 | 개발 도구 설치 |

같은 항목을 두 도구가 동시에 관리하지 않는 것이 핵심이다. 예를 들어 CMake는 Nix가
제공하며, Conan recipe가 CMake를 요구할 때도 `[platform_tool_requires]`로 Nix의 CMake를
재사용한다.

## 전체 흐름

```text
flake.nix
  ├─ x86_64 네이티브 GCC
  ├─ aarch64-unknown-linux-musl GCC
  ├─ CMake 3.31
  ├─ GNU Make
  └─ Conan 2
           │
           ├─ build profile: x86_64에서 실행할 도구
           └─ host profile : x86_64 또는 aarch64용 라이브러리
                         │
                         ▼
                 conan_toolchain.cmake
                         │
                         ▼
                   CMake → Make
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
      x86_64 테스트 실행 파일   aarch64-musl 정적 실행 파일
```

Conan에서 `host`는 명령을 실행하는 현재 PC가 아니라 **만들어지는 바이너리가 실행될
플랫폼**을 뜻한다. 교차 빌드에서 가장 자주 혼동하는 이름이다.

## 완성할 프로젝트

```text
cyclonedds-cross-demo/
├── flake.nix
├── flake.lock
├── conanfile.py
├── CMakeLists.txt
├── profiles/
│   ├── build-x86_64
│   ├── host-x86_64
│   └── host-aarch64-musl
├── idl/
│   └── Telemetry.idl
├── generated/
│   ├── Telemetry.c
│   └── Telemetry.h
└── src/
    ├── publisher.cpp
    └── subscriber.cpp
```

`generated/`의 파일은 x86_64용 `idlc`로 미리 만든 후 Git에 함께 기록한다. 따라서
aarch64 교차 빌드 도중에는 aarch64용 실행 파일을 x86_64에서 잘못 실행하지 않는다.

## 읽는 순서

1. [도구의 역할과 C++ 빌드 흐름](./01-toolchain-mental-model.md)
2. [CMake와 GNU Make 기초](./02-cmake-and-make.md)
3. [Flake 개발 셸 구성](./03-nix-development-shell.md)
4. [Conan recipe와 교차 프로필](./04-conan-profiles.md)
5. [CMake 프로젝트와 spdlog 연결](./05-cmake-project.md)
6. [DDS, IDL, publisher/subscriber](./06-dds-and-idl.md)
7. [네이티브 빌드와 IDL 생성](./07-native-build.md)
8. [aarch64-musl 정적 교차 빌드](./08-cross-build.md)
9. [대상 배포와 장치 간 통신](./09-deploy-and-network.md)
10. [문제 해결과 최종 체크리스트](./10-troubleshooting.md)

## 범위 밖의 내용

- Unitree SDK2
- Cyclone DDS C++ binding인 `cyclonedds-cxx`
- DDS Security
- Iceoryx shared memory
- ROS 2
- `uv`와 별도 Python 개발 환경

`conanfile.py`는 Conan이 읽는 recipe다. 사용자가 Python이나 `uv`로 직접 실행하지 않는다.

## 공식 참고 자료

- [Nix 개발 셸](https://nix.dev/tutorials/first-steps/declarative-shell.html)
- [Nixpkgs 교차 컴파일](https://nixos.org/manual/nixpkgs/stable/#chap-cross)
- [Conan 프로필](https://docs.conan.io/2/reference/config_files/profiles.html)
- [Conan CMake 연동](https://docs.conan.io/2/tutorial/consuming_packages/build_simple_cmake_project.html)
- [Cyclone DDS 0.10 문서](https://cyclonedds.io/docs/cyclonedds/0.10.5/)

[문서 목록으로 돌아가기](../index.md)
