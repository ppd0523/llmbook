---
title: 퇴고 기록
status: final
owner: agent
target_reader: C++와 Linux 명령을 조금 써 봤지만 빌드 시스템과 교차 컴파일을 직접 구성해 본 적 없는 개발자
topic: Nix·Conan·CMake로 만드는 Cyclone DDS C++ 교차 개발 환경
---

# 퇴고 기록

퇴고 기준은 `05_review.md`의 판정과 `03_outline.md` 12절의 구성 결정이다. 이 기록은 각 판정과 구성 결정이 본문에 어떻게 드러나 있는지 정리한다.

## 1. 기술 판정의 본문 반영

| 번호 | 위치 | 본문의 서술 |
|---|---|---|
| X1 | 5장 configure 출력 | 실제 생성 파일 기준의 출력을 보이고, 전역 target과 component target의 메시지 차이를 설명한다 |
| X2 | 9장 네트워크 설정 | `General/Interfaces/NetworkInterface`를 쓰고, 구형 옵션을 만났을 때의 대응을 함께 둔다 |
| X3 | 8장 정적 링크 서술 | musl과 glibc를 상호 대체 관계인 libc 구현으로 서술한다 |
| X4 | 4장 `default_options` | 9항목 전부를 보이고 `header_only=False`의 역할을 밝힌다 |
| X5 | 4장 `compiler_executables` | C와 C++ 컴파일러 항목을 모두 보인다 |
| X6 | `index.md` 참고 링크 | baseline과 같은 0.10.2 문서를 링크한다 |

버전 조건 5건(V1–V5)은 각각 recipe revision 의존, `COMPILE_LANG_AND_ID`의 CMake 3.15 하한, `cyclonedds`가 `compiler.cppstd`·`libcxx`를 제거하는 예외, `conanbuild.sh`가 `idlc`를 PATH에 올리는 전제, `-static`이 `CMakeToolchain` 경로에 의존한다는 조건으로 본문에 드러나 있다.

## 2. 실행이 필요한 항목의 서술 방식

실행 검증이 필요한 5건(U1–U5)은 주장 대신 확인 방법으로 쓴다.

- `nix develop` 출력과 `cmake --version`: 예시임을 밝히고 세 가지 점검 방법으로 확인하게 한다.
- `conan graph info`의 platform 출력: 출력 예시 블록 없이 확인할 항목만 둔다.
- aarch64 ELF의 `Machine`·`INTERP`·`NEEDED`: 점검 절차와 기대값 표로 쓴다.
- 장치 간 LAN discovery와 WSL2 대역: `ip address`로 대역을 비교해 판단하는 조건으로 쓴다.
- 예제 소스의 domain ID 상한: 본문 서술이 아니므로 챕터에서 다루지 않는다.

## 3. 구성

| 번호 | 주제 | 본문의 구성 |
|---|---|---|
| 1 | 2장과 5장의 CMake 코드 | 2장은 최소 예제, 프로젝트 코드는 5장 단독 |
| 2 | lockfile 절차 | 4.7은 개념, 생성 명령은 7·8장 |
| 3 | CMake 3.x 고정 이유 | 3.1이 유일한 설명, 10.3은 참조 |
| 4 | musl 근거 | 1.4는 선택 이유, 8.5는 보장 범위 |
| 5 | 6장의 위치 | 5장과 7장 사이. 근거는 `03_outline.md` 12절 5번 |
| 6 | 확인 절 이름 | 모든 챕터가 "직접 확인", 10장 포함 |
| 7 | 목차와 H1 | `index.md`의 읽는 순서 항목이 각 챕터 H1과 같다 |
| 8 | `target`의 의미 | 장치는 "대상 장치", `target`은 CMake 용어로 한정 |
| 9 | 명령행 인터페이스 설명 시점 | 6장에 정리 절이 있다 |
