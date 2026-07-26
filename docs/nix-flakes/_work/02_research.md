---
title: 조사 노트
version: 1.0
status: final
owner: agent
updated: 2026-07-24
target_reader: Nix 기초는 알지만 Flake는 처음인 개발자
topic: Nix Flake의 공식 동작과 출력 스키마
---

# 조사 노트

## 1. 핵심 출처

| 구분 | 제목/문서 | 링크 | 사용할 내용 | 신뢰도 |
|---|---|---|---|---|
| 공식 문서 | Flakes | <https://nix.dev/concepts/flakes.html> | Flake의 정의, input/output, lock file, 실험적 상태 | 높음 |
| 공식 문서 | Nix 2.34 `nix flake` | <https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-flake.html> | Flake reference와 하위 명령 | 높음 |
| 공식 문서 | Nix 2.34 `nix develop` | <https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-develop.html> | `devShells.<system>.default` 탐색 | 높음 |
| 공식 문서 | Nix 2.34 `nix run` | <https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-run.html> | app 스키마와 package fallback | 높음 |
| 공식 문서 | Nix 2.34 `nix flake check` | <https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-flake-check.html> | 검사 대상 출력 | 높음 |
| 공식 문서 | Nix 2.34 `nix flake lock` | <https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-flake-lock.html> | 누락된 lock entry 생성 | 높음 |
| 공식 문서 | Nix 2.34 `nix flake update` | <https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-flake-update.html> | 전체 또는 특정 input 갱신 | 높음 |
| 공식 문서 | Nix 첫 단계: 임시 셸 | <https://nix.dev/tutorials/first-steps/ad-hoc-shell-environments.html> | `cowsay`가 Nixpkgs 예제 패키지임을 확인 | 높음 |
| 공식 문서 | Nixpkgs 26.05 Manual | <https://nixos.org/manual/nixpkgs/stable/> | Nixpkgs와 `writeShellApplication`, 개발 셸 helper | 높음 |
| 공식 문서 | Nixpkgs release notes | <https://nixos.org/manual/nixpkgs/stable/release-notes> | 25.11부터 formatter 속성은 `pkgs.nixfmt` | 높음 |

## 2. 핵심 정의

| 용어 | 정의 | 출처 | 본문 표기 |
|---|---|---|---|
| Flake | 루트의 `flake.nix`가 입력과 출력을 표준 구조로 선언하는 파일 시스템 트리 | Flakes, `nix flake` manual | Flake |
| input | Flake가 평가할 때 참조하는 다른 소스 또는 Flake | Flakes | 입력(input) |
| output | 패키지, 앱, 개발 셸처럼 Flake가 소비자에게 제공하는 Nix 값 | Flakes, 명령 reference | 출력(output) |
| lock file | input의 해석 결과와 revision, content hash를 고정하는 `flake.lock` | Flakes, lock/update reference | 잠금 파일 |
| system | 빌드·실행 대상 플랫폼을 나타내는 문자열 | 명령 reference | 시스템 |
| installable | `nix build`, `nix run` 등이 처리하는 Flake 출력, store path, Nix expression 등의 대상 | Nix command reference | 설치 가능 대상(installable) |

## 3. 명령과 출력 스키마

| 명령 | 기본 출력 | 이름을 지정한 출력 | 검증 상태 |
|---|---|---|---|
| `nix develop` | `devShells.<system>.default`, 이후 `packages.<system>.default` | `devShells.<system>.<name>` 등 | 공식 reference 확인 |
| `nix build` | `packages.<system>.default` | `packages.<system>.<name>` 등 | 공식 reference 확인 |
| `nix run` | `apps.<system>.default`, 이후 `packages.<system>.default` | `apps.<system>.<name>` 등 | 공식 reference 확인 |
| `nix fmt` | `formatter.<system>` | 해당 없음 | 공식 reference 확인 |
| `nix flake check` | 알려진 출력 스키마 평가 후 `checks.<system>.*` 빌드 | `--all-systems`로 전 시스템 검사 | 공식 reference 확인 |

## 4. 예제 후보

| 예제 | 보여줄 개념 | 필요한 도구 | 장점 | 위험 |
|---|---|---|---|---|
| `cowsay` 개발 셸 | Nixpkgs package와 `devShells` | Nix 2.34 | 결과가 즉시 보이고 공식 튜토리얼에서도 사용 | 첫 다운로드 시간 |
| `flake-greeter` | package, app, runtime dependency | `writeShellApplication`, `cowsay` | 별도 언어 툴체인 없이 전체 흐름을 설명 | Nix 문자열 안의 셸 확장 이스케이프 |
| greeting check | `checks`와 자동 실행 검증 | `runCommand`, `grep` | 빌드 성공뿐 아니라 출력도 확인 | 모든 시스템에서 실행 가능한 package 필요 |
| 네 시스템 반복 | `genAttrs`와 system 축 | `nixpkgs.lib.genAttrs` | 의존성 추가 없이 중복 제거 | 독자가 추상화에 먼저 매몰될 수 있음 |

## 5. 논쟁점 또는 주의점

- 쟁점: Flake는 널리 사용되지만 Nix reference manual에서 여전히 experimental로 표시된다.
- 서로 다른 설명 방식: Flake를 완전한 재현성 기능으로 소개하거나, 표준화된 입출력과 input pinning의 조합으로 설명한다.
- 이 자료에서 채택할 설명: Flake는 의존성 위치와 출력 스키마를 표준화하고 lock file로 input을 고정하지만, 외부 네트워크·시간·환경을 사용하는 빌드까지 자동으로 순수하게 만들지는 않는다고 설명한다.
- 채택 이유: “Flake를 쓰면 모든 것이 재현 가능하다”는 과장을 피하고 실제 적용 조건을 드러낸다.
- 버전 기준: Nix/Nixpkgs 26.05에 포함된 Nix 2.34 계열과 2026-07-24 공식 문서를 기준으로 한다.
- formatter: Nixpkgs 25.11 release notes에 따라 임시 이름 `nixfmt-rfc-style` 대신 `pkgs.nixfmt`를 사용한다.
- update 명령: 폐기 예정인 `nix flake lock --update-input` 대신 `nix flake update nixpkgs`를 사용한다.

## 6. 출처 필요 항목

- 없음

## 7. 조사 요약

- 가장 신뢰할 수 있는 기준 출처: Nix 2.34 reference manual과 nix.dev Flakes 개념 문서
- 초고에 반드시 반영할 내용: experimental 표시, system 축, 명령별 출력 탐색, `nix flake lock`과 `nix flake update`의 차이
- 아직 검증이 필요한 내용: 로컬 Nix 환경에서 완성형 예제의 평가·빌드·실행
- 독자에게 혼란을 줄 수 있는 용어: “설치”, “package”, “app”, “lock”, “system”

## 8. 품질 점검

- [x] 정의와 알고리즘의 출처가 기록되어 있다.
- [x] 공식 문서와 구현 reference를 우선 출처로 사용했다.
- [x] 버전 의존적 내용에 날짜와 버전을 기록했다.
- [x] 출처 없는 주장이 남아 있지 않다.
