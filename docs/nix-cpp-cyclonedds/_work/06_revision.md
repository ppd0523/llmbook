---
title: 퇴고 계획 및 반영 내역
version: 1.0
status: final
owner: agent
updated: 2026-09-22
target_reader: C++와 Linux 명령을 조금 써 봤지만 빌드 시스템과 교차 컴파일을 직접 구성해 본 적 없는 개발자
topic: Nix·Conan·CMake로 만드는 Cyclone DDS C++ 교차 개발 환경
---

# 퇴고 계획 및 반영 내역

`05_review.md`의 판정과 `03_outline.md` 12절의 구성 지적을 항목별로 처리한 기록이다.

## 1. 기술 오류 반영

| 번호 | 위치 | 처리 |
|---|---|---|
| X1 | 5장 configure 출력 | 실제 생성 파일 기준으로 교체. 전역 target과 component target의 메시지 차이를 설명 |
| X2 | 9장 네트워크 설정 | `General/Interfaces/NetworkInterface`로 교체, 구형 옵션 대응 추가 |
| X3 | 8장 정적 링크 서술 | musl과 glibc를 상호 대체 관계로 다시 서술 |
| X4 | 4장 `default_options` | 9항목 전부 제시, `header_only=False`의 역할 명시 |
| X5 | 4장 `compiler_executables` | 잘려 있던 C 컴파일러 항목 복원 |
| X6 | `index.md` 참고 링크 | 0.10.5 문서 링크를 baseline과 같은 0.10.2로 교체 |

버전 조건 5건(V1–V5)은 각각 recipe revision 의존, `COMPILE_LANG_AND_ID`의 CMake 3.15 하한, `cyclonedds`가 `compiler.cppstd`·`libcxx`를 제거하는 예외, `conanbuild.sh`가 `idlc`를 PATH에 올리는 전제, `-static`이 `CMakeToolchain` 경로에 의존한다는 조건으로 본문에 드러냈다.

## 2. 확인 불가 항목 처리

실행 검증이 필요한 5건(U1–U5)은 주장 대신 확인 방법으로 바꿨다.

- `nix develop` 출력과 `cmake --version`: 예시임을 밝히고 세 가지 점검 방법으로 재구성.
- `conan graph info`의 platform 출력: 출력 예시 블록을 빼고 확인할 항목만 남김.
- aarch64 ELF의 `Machine`·`INTERP`·`NEEDED`: 점검 절차와 기대값 표로 전환.
- 장치 간 LAN discovery와 WSL2 대역: `ip address`로 대역을 비교해 판단하는 조건으로 전환.
- 예제 소스의 domain ID 상한: 본문 서술이 아니므로 챕터를 고치지 않았다.

## 3. 구성 지적 처리

| 번호 | 지적 | 처리 |
|---|---|---|
| 1 | 2장과 5장의 코드 중복 | 2장을 최소 예제로 교체, 프로젝트 코드는 5장 단독 |
| 2 | lockfile 절차 3중 중복 | 4.7은 개념, 생성 명령은 7·8장 |
| 3 | CMake 3.x 고정 이유 중복 | 3.1이 유일한 설명, 10.3은 참조 |
| 4 | musl 근거 분산 | 1.4는 선택 이유, 8.5는 보장 범위 |
| 5 | 6장의 위치 | 유지. 근거는 `04_draft.md` 2절 |
| 6 | 확인 절 이름 불일치 | "직접 확인"으로 통일, 10장에도 신설 |
| 7 | 목차와 H1 불일치 | `index.md`의 6·7·9·10장 항목을 H1과 일치시킴 |
| 8 | `target`의 두 의미 | 장치는 "대상 장치", `target`은 CMake 용어로 한정 |
| 9 | 명령행 인터페이스 설명 시점 | 6장에 정리 절 신설 |

## 4. 처리하지 않은 것

예제 자산 `assets/cyclonedds-cross-demo/flake.nix`의 `pkgs.nixfmt-rfc-style`이 Nixpkgs 26.05에서 별칭으로 강등됐다는 지적이 있었다. 본문이 아니라 예제 파일의 문제이고 이번 범위는 본문 재집필이므로 손대지 않았다. 예제 수정은 별도 요청으로 다룬다.
