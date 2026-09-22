---
title: 작성 범위 정의
version: 1.0
status: reconstructed
owner: agent
updated: 2026-09-22
target_reader: C++와 Linux 명령을 조금 써 본, 교차 빌드는 처음인 개발자
topic: Nix·Conan·CMake·Make로 Cyclone DDS C++ 교차 개발 환경 만들기
---

# 작성 범위 정의

> 이 기록은 완성된 본문을 근거로 재구성했으며 집필 당시의 기록이 아니다. 아래 항목은
> `docs/nix-cpp-cyclonedds/`의 `index.md`와 10개 챕터를 읽고 역으로 정리한 것이므로,
> 집필 시점에 실제로 이런 판단을 내렸다는 증거로 읽어서는 안 된다.

## 1. 주제

- 다룰 주제: Nix Flake 개발 셸, Conan 2 recipe와 build/host 프로필, CMake와 GNU Make, Cyclone DDS와 IDL, aarch64-musl 정적 교차 빌드, Nix 없는 장치로의 배포와 LAN 통신 검증
- 중심 질문: x86_64 개발 PC에서 어떻게 Nix가 없는 aarch64 Linux 장치에서 그대로 실행되는 Cyclone DDS C++ 프로그램을 만들고, 그 결과가 재현되는지 확인하는가?
- 이 자료가 해결하는 문제: Nix·Conan·CMake·Make를 한 프로젝트에서 함께 쓸 때 어느 도구가 무엇을 소유하는지 구분하지 못해, 교차 빌드에서 컴파일러가 뒤섞이거나 대상 장치에서 실행되지 않는 바이너리를 만드는 문제
- 이 자료가 다루는 기술 영역: Nixpkgs 26.05와 25.05, Conan 2.28, CMake 3.31, GNU Make, GCC(x86_64, aarch64-unknown-linux-musl), Cyclone DDS 0.10.2, spdlog 1.17.0

## 2. 독자 상태 진단

### 2.1 숙련도

- 초심자: Nix Flake, Conan 프로필, DDS, 교차 빌드에 대해서는 초심자다.
- 일부 지식이 있는 중급자: C++ 소스를 읽고 컴파일러를 호출해 본 적이 있다.
- 실무 경험이 있는 중급자: 터미널과 Git을 일상적으로 사용한다.
- 전문가: 해당 없음
- 이 자료에서 기준으로 삼을 독자 수준: C++와 Linux 명령을 조금 사용해 본, 빌드 시스템과 교차 컴파일은 직접 구성해 본 적 없는 개발자

### 2.2 선행지식

- 반드시 알고 있어야 하는 개념: 터미널 명령과 환경 변수, 파일 경로, Git 저장소, C++ 함수와 구조체 읽기
- 알고 있으면 좋은 개념: 정적·공유 라이브러리의 차이, `Makefile`을 본 경험, IP 주소와 LAN
- 모른다고 가정할 개념: Nix Flake의 입력과 잠금, Conan의 recipe·프로필·lockfile·package ID, CMake의 target과 generator expression, DDS의 domain·topic·QoS, IDL과 생성 코드, build/host 플랫폼 구분, musl과 완전 정적 링크, ELF의 `INTERP`와 `NEEDED`
- 이 자료에서 새로 설명할 개념: 위의 "모른다고 가정할 개념" 전부
- 선행지식으로 가정할 용어: 컴파일러, 라이브러리, 실행 파일, 저장소, 환경 변수
- 처음 등장할 때 설명할 새 용어: build 플랫폼과 host 플랫폼, 교차 컴파일러, out-of-source build, imported target, platform tool, lockfile, DomainParticipant·Topic·DataWriter·DataReader, type descriptor, 완전 정적 링크

### 2.3 경험 수준

- 이론 학습 경험: C++ 문법을 학습한 수준이며 빌드 시스템 이론은 가정하지 않는다.
- 구현 경험: 단일 파일 C++ 프로그램을 컴파일해 본 정도를 가정한다.
- 실험/측정 경험: 명령 출력과 로그를 읽고 기대값과 비교할 수 있다.
- 디버깅 경험: 컴파일 오류 메시지를 읽을 수 있으나 링크 오류와 구분하지는 못한다고 가정한다.
- 논문/표준 문서 독해 경험: 가정하지 않는다. DDS 명세를 직접 읽게 하지 않는다.

### 2.4 학습 목적

- 개념 이해: 네 도구의 책임 경계와 build/host 구분을 설명한다.
- 문제 풀이: 해당 없음. 계산 문제를 다루지 않는다.
- 구현: 예제 프로젝트를 처음부터 구성해 네이티브와 aarch64 바이너리를 만든다.
- 설계: Conan 프로필과 CMake target 구조를 바꿔 볼 수 있을 정도로 이해한다.
- 디버깅: 실패한 계층(Nix·Conan·CMake·Make·ELF·실행·discovery)을 먼저 찾는다.
- 논문/기술문서 독해: Conan과 Cyclone DDS 공식 문서에서 프로필과 설정 항목을 찾는다.
- 실무 적용: Nix가 없는 임베디드 Linux 장치에 단일 실행 파일을 배포한다.
- 이 자료에서 우선할 학습 목적: 구현, 디버깅, 개념 이해 순으로 우선한다.

### 2.5 실패 가능 지점

- 헷갈릴 용어: Conan의 `host`(결과물이 실행될 플랫폼)와 일상어의 "호스트 PC", build profile과 host profile, Nix와 Nixpkgs, `make`와 `cmake --build`, `shared=False`와 `-static`
- 생략하면 안 되는 배경: 컴파일과 링크의 구분, `flake.lock`과 Conan lockfile이 서로 다른 것을 고정한다는 사실, IDL 생성 코드를 저장소에 기록하는 이유
- 수식에서 막힐 지점: 수식을 사용하지 않는다.
- 코드에서 막힐 지점: Conan 프로필의 Jinja 문법, CMake generator expression, `dds_take`가 반환한 loaned sample의 반환 의무
- 추상 개념과 실제 사례가 연결되지 않을 지점: "정적 링크가 보장하는 것"과 "여전히 필요한 것"의 경계, DDS discovery 실패가 빌드 문제가 아니라 네트워크 문제라는 점

## 3. 대상 독자

- 전공/배경: 소프트웨어 또는 임베디드 개발을 시작한 지 얼마 되지 않은 개발자
- 알고 있다고 가정하는 지식: 터미널, Git, C++ 기본 문법
- 모를 가능성이 높은 지식: 교차 컴파일, 패키지 관리자 두 개(Nix와 Conan)를 한 프로젝트에서 쓰는 이유, DDS 미들웨어
- 독자가 원하는 결과: 개발 PC에서 만든 실행 파일 하나를 ARM 장치에 복사해서 바로 돌리는 것
- 독자가 자주 막힐 지점: host 프로필을 잘못 지정해 x86_64 컴파일러로 교차 빌드를 시도하는 것, 교차 빌드 중 aarch64용 `idlc`를 실행해 `Exec format error`를 만나는 것, 빌드는 성공했는데 장치에서 샘플이 오지 않는 것

## 4. 학습 목표

이 자료를 읽은 뒤 독자는 다음을 할 수 있어야 한다.

1. Nix, Conan, CMake, GNU Make 각각이 소유하는 것과 소유하지 않는 것을 구분해 설명한다.
2. Flake로 네이티브 GCC와 aarch64-musl 교차 GCC를 한 개발 셸에 고정하고 버전을 확인한다.
3. Conan의 build 프로필과 host 프로필을 구분해 작성하고, 왜 둘 다 필요한지 설명한다.
4. `spdlog/1.17.0`과 `cyclonedds/0.10.2`를 소스에서 빌드하고 lockfile로 dependency graph를 고정한다.
5. IDL에서 생성한 C 타입을 C++17 애플리케이션의 CMake target으로 연결한다.
6. publisher와 subscriber를 x86_64에서 실행해 샘플 교환을 확인한다.
7. aarch64용 정적 ELF를 만들고 `readelf`로 `INTERP`와 `NEEDED`가 없음을 검사한다.
8. Nix가 없는 aarch64 장치에 배포하고, 서로 다른 두 Linux 장치 사이의 DDS discovery와 데이터 교환을 확인한다.
9. 실패가 발생한 계층을 구분해 우선 확인할 항목을 고른다.

## 5. 포함 범위

- 반드시 포함할 내용: 컴파일과 링크의 구분, 네 도구의 책임 표, CMake configure/build 분리와 target 기반 링크, Flake 입력 두 개와 환경 변수 내보내기, Conan recipe·세 프로필·platform tool·정적 옵션·lockfile, DDS 개체와 IDL 생성 흐름, 네이티브 빌드와 로컬 통신, 교차 빌드와 ELF 검사, 배포와 LAN 통신, 증상별 점검표와 최종 체크리스트
- 선택적으로 포함할 내용: `cmake --build`와 `make`의 관계, WSL2 네트워크 제약, 다음 단계로 확장 가능한 주제 목록
- 예제/실습에 포함할 내용: `assets/cyclonedds-cross-demo/` 예제 프로젝트 하나(Flake, Conan recipe, 프로필 3종, CMake 프로젝트, IDL과 생성 코드, publisher/subscriber 소스, lockfile 2종)
- 수식/코드/그림으로 다룰 내용: 수식은 사용하지 않는다. 코드는 Nix·Python·INI·CMake·IDL·C++·콘솔 블록으로 제시한다. 그림은 이미지 파일 없이 `text` 코드 블록의 흐름도와 Markdown 표로 대체한다.

## 6. 제외 범위

- 다루지 않을 내용: Unitree SDK2, `cyclonedds-cxx` C++ 바인딩, DDS Security, Iceoryx shared memory, ROS 2, `uv`와 별도 Python 개발 환경
- 다음 장으로 넘길 내용: 해당 없음. 한 권 안에서 닫는다.
- 심화 자료로 분리할 내용: QoS 구성 파일 분리, unicast peer 설정, CI 자동화와 artifact 생성, Cyclone DDS 상위 버전의 wire 호환성, 인증서 배포
- 독자의 선행지식으로 가정할 내용: 터미널 조작, Git 기본 명령, C++ 문법

## 7. 최종 산출물 형식

- 기준 원고 형식: Markdown
- 기준 원고 위치: 최종 산출물 자체(MkDocs 챕터형)
- 내부 작업 산출물 위치: `docs/nix-cpp-cyclonedds/_work/`
- 최종 산출물 형식: MkDocs 챕터형 Markdown
- 최종 산출물 경로: `docs/nix-cpp-cyclonedds/`
- 챕터 수: 10
- MkDocs 책 폴더명 `<book-slug>`: `nix-cpp-cyclonedds`
- 챕터 파일명 규칙: `NN-<chapter-slug>.md`
- 챕터 파일 배치: 책 폴더 바로 아래. 예제 프로젝트는 `assets/cyclonedds-cross-demo/`에 `<project-slug>` 폴더 하나로 둔다.
- 단일 파일명: 해당 없음
- 보조 배포 형식: 없음. PDF·PPTX 변환은 요청 범위 밖이다.
- 사용할 빌드 도구: MkDocs
- 수식 지원 필요 여부: 불필요
- 코드 실행/검증 필요 여부: 필요. 예제 프로젝트가 실제로 빌드·실행되어야 한다.
- 인터랙티브 요소 필요 여부: 불필요
- 인쇄 가능성 필요 여부: 불필요
- 모바일 가독성 필요 여부: 표와 콘솔 블록이 과도하게 넓지 않은 수준으로 유지한다.

## 8. 성공 기준

- 독자가 풀 수 있어야 하는 문제: 교차 configure 로그에 x86_64 컴파일러가 보일 때 어느 설정을 고쳐야 하는지 지목한다.
- 설명 없이 수행할 수 있어야 하는 작업: `nix develop` 진입, 두 프로필 조합으로 `conan install`, out-of-source configure와 `make`, `readelf`로 정적 ELF 검사, 두 장치 사이 통신 확인
- 독자가 구분할 수 있어야 하는 개념: 컴파일과 링크, build 플랫폼과 host 플랫폼, `flake.lock`과 Conan lockfile, `shared=False`와 `-static`, 라이브러리 준비(Conan)와 빌드 규칙 생성(CMake)과 실행(Make)
- 독자가 피할 수 있어야 하는 흔한 오류: 교차 빌드에서 IDL 재생성 실행, Nix 셸 밖에서 Conan 실행, 네이티브와 교차 build 폴더 공유, domain ID·topic 이름 불일치, 상대 장치 주소를 `CYCLONEDDS_URI`에 지정

## 9. 품질 점검

- [x] 중심 질문이 하나로 정리되어 있다.
- [x] 독자 숙련도가 명시되어 있다.
- [x] 독자의 선행지식과 모른다고 가정할 개념이 분리되어 있다.
- [x] 선행지식으로 가정할 용어와 처음 등장할 때 설명할 새 용어가 분리되어 있다.
- [x] 학습 목적이 명시되어 있다.
- [x] 대상 독자의 선행지식이 명시되어 있다.
- [x] 학습 목표가 행동 중심으로 작성되어 있다.
- [x] 포함 범위와 제외 범위가 분리되어 있다.
- [x] 기준 원고 형식이 Markdown으로 명시되고 위치가 최종 산출물 형식과 맞다.
- [x] 최종 산출물 형식과 경로가 명시되어 있다.
- [x] MkDocs 챕터형 자료이므로 책 폴더명과 챕터 파일명 규칙이 명시되어 있다.
- [x] 내부 작업 산출물 위치가 `docs/nix-cpp-cyclonedds/_work/`로 분리되어 있다.
- [x] 최종 연습문제 또는 실습 과제의 방향이 드러난다. 10장의 최종 체크리스트가 인수 기준 역할을 한다.
