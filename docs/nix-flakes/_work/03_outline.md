---
title: 구성 설계
version: 1.0
status: final
owner: agent
updated: 2026-07-24
target_reader: Nix 기초는 알지만 Flake는 처음인 개발자
topic: 여섯 장으로 배우는 Nix Flake
---

# 구성 설계

## 1. 자료의 한 문장 요약

작은 `cowsay` 개발 셸에서 시작해 빌드·실행·검사·업데이트가 가능한 다중 시스템 Flake를 완성한다.

## 2. 중심 질문

이 자료는 다음 질문에 답한다.

- `flake.nix` 하나를 어떻게 읽고 확장하여 재현 가능한 개발 환경과 실행 가능한 패키지를 만드는가?

## 3. 학습 흐름

```text
Flake의 경계
  -> input과 lock
  -> devShell과 Nixpkgs package
  -> package와 app
  -> formatter·checks·여러 system
  -> 업데이트·디버깅·종합 실습
```

## 4. 챕터 구조

| 번호 | 챕터 | 목적 | 필요한 선행개념 | 산출되는 이해 |
|---|---|---|---|---|
| 1 | Flake의 역할과 구조 | `flake.nix`를 입출력 함수로 읽는다. | Nix 속성 집합 | Flake, reference, output tree |
| 2 | 입력과 잠금 파일 | URL과 잠긴 revision을 구분한다. | input/output | lock 생성·갱신·복원 |
| 3 | 개발 셸과 `cowsay` | Nixpkgs package를 프로젝트 환경에 넣는다. | system 축 | `devShells`, `mkShellNoCC` |
| 4 | 패키지와 앱 | 작은 CLI를 빌드하고 실행한다. | derivation 기초 | `packages`, `apps`, `writeShellApplication` |
| 5 | 검사와 여러 시스템 | formatter와 test를 출력으로 제공한다. | package/app | `checks`, `formatter`, `genAttrs` |
| 6 | 운영과 문제 해결 | 전체 예제를 갱신하고 실패를 분류한다. | 앞의 모든 장 | 검증·업데이트·복구 루프 |

## 5. 개념 의존성

| 개념 | 먼저 알아야 할 개념 | 이 개념 뒤에 설명할 내용 |
|---|---|---|
| Flake output | Nix 속성 집합과 함수 | 명령별 출력 탐색 |
| lock file | input URL | update와 Git diff |
| system 축 | output tree | 다중 시스템 반복 |
| dev shell | Nixpkgs package | package와 runtime dependency |
| package | derivation | app와 check |
| check | package와 build | CI 적용 |

## 6. 예제 계획

| 예제 | 위치 | 보여줄 개념 | 입력 | 기대 결과 |
|---|---|---|---|---|
| 최소 Flake | 1장 | output tree | `flake.nix` | `nix flake show` 성공 |
| lock 생성과 제한 갱신 | 2장 | input pinning | Nixpkgs 26.05 input | `flake.lock` diff |
| `cowsay` 개발 셸 | 3장 | Nixpkgs package 설치 | `devShells` | 셸 안에서 `cowsay` 실행 |
| `flake-greeter` | 4장 | package와 app | `writeShellApplication` | `nix build`, `nix run` |
| greeting check | 5장 | 빌드 시 실행 검증 | `runCommand` | `nix flake check` 성공 |
| 완성형 예제 | 6장 | 통합 워크플로 | asset Flake | show→fmt→check→run |

## 7. 연습문제 계획

| 문제 | 유형 | 검증할 학습목표 | 난이도 |
|---|---|---|---|
| 명령이 찾는 출력 경로 연결 | 추적 | 2 | 낮음 |
| 두 번째 input을 추가하고 lock diff 설명 | 변형 | 1, 6 | 중간 |
| `lolcat`을 dev shell에 추가 | 변형 | 3 | 낮음 |
| 이름 있는 app 추가 | 설계 | 4 | 중간 |
| check 실패 원인 찾기 | 디버깅 | 5, 7 | 중간 |
| 한 input만 갱신하고 복구 | 실무 적용 | 6, 7 | 중간 |

## 8. 그림, 표, 코드 계획

| 자료 | 위치 | 목적 | 필요한 정확성 검증 |
|---|---|---|---|
| ASCII 흐름도 | 1장 | input→outputs→commands 흐름 | 용어와 방향 |
| 명령별 출력 표 | 1·4장 | 기본 탐색 경로 비교 | Nix 2.34 reference |
| lock 비교 표 | 2장 | URL과 lock의 역할 분리 | 공식 문서 |
| 완성형 코드 | 3~6장 | 점진적 확장 | Nix 평가·빌드 |

## 9. 위험 구간

- 설명이 어려운 부분: `outputs`가 함수이고 그 결과가 명령의 탐색 트리라는 점
- 오해가 잦은 부분: 개발 셸에 package를 넣는 것을 시스템 전체 설치로 부르는 것
- 추가 그림이 필요한 부분: input URL, lock node, output tree의 관계
- 예제 없이 설명하면 위험한 부분: package와 app의 차이, `${system}`과 셸 변수 이스케이프

## 10. 품질 점검

- [x] 챕터 순서가 학습자의 선행지식 흐름과 맞는다.
- [x] 새 용어가 정의 없이 먼저 등장하지 않는다.
- [x] 각 핵심 개념에 예제 또는 확인 질문이 대응된다.
- [x] 최종 연습문제가 학습 목표와 대응된다.
