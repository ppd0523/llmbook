---
title: 초고
version: 1.0
status: reviewed
owner: agent
updated: 2026-07-24
target_reader: Nix 기초는 알지만 Flake는 처음인 개발자
topic: Nix Flake의 입출력과 재현 가능한 개발 워크플로
---

# 초고

## 1. 문제 제기

Flake 예제를 복사할 수는 있지만 input, lock, system별 output과 명령의 탐색 규칙을
모르면 작은 변경도 원인을 찾기 어렵다. 이 자료는 Flake를 잠긴 input에서 표준 output
tree를 만드는 함수로 읽고, 실행 가능한 작은 예제를 점진적으로 완성한다.

## 2. 직관적 예시

- 상황: 호스트에는 `cowsay`가 설치되어 있지 않다.
- 관찰: Nixpkgs에서 package를 선택해 개발 셸에 선언하면 `nix develop` 안에서만
  command를 사용할 수 있다.
- 확장: 같은 package를 runtime dependency로 선언한 `flake-greeter`를 package와
  app으로 제공한다.
- 검증: `checks`가 실제 실행 결과를 검사하고 `formatter`가 프로젝트 서식을 고정한다.

## 3. 핵심 개념

### 3.1 Flake

- 루트의 `flake.nix`가 input과 output을 표준 구조로 선언한다.
- `outputs`는 `self`와 잠긴 input을 받아 속성 트리를 반환하는 함수다.
- 출력은 `packages.<system>.default`처럼 명령이 해석할 수 있는 경로를 사용한다.

### 3.2 잠금 파일

- `flake.nix`의 URL은 의존성 계열을 나타낸다.
- `flake.lock`은 실제 revision과 content hash를 기록한다.
- 생성은 `nix flake lock`, 기존 input 갱신은 `nix flake update <input>`으로 분리한다.

### 3.3 개발 셸

- `nix shell`은 임시 실험, `nix develop`은 저장소에 선언한 개발 환경에 사용한다.
- `pkgs.mkShellNoCC { packages = [ pkgs.cowsay ]; }`로 package를 셸 PATH에 제공한다.
- 이것은 시스템 또는 사용자 프로필 전체 설치가 아니다.

### 3.4 package와 app

- package는 build할 derivation이다.
- app은 Store 안의 실행 파일 경로를 선언한다.
- 개발 셸의 의존성과 package의 runtime dependency를 분리한다.

### 3.5 검사와 다중 시스템

- `nixpkgs.lib.genAttrs`로 지원 system마다 같은 output 계약을 생성한다.
- `formatter.<system>`은 `nix fmt`가 사용한다.
- `checks.<system>.*`는 `nix flake check`가 평가하고 build한다.

## 4. 형식화

명령과 기본 출력의 대응은 다음과 같다.

| 명령 | 기본 출력 |
|---|---|
| `nix develop` | `devShells.<system>.default` |
| `nix build` | `packages.<system>.default` |
| `nix run` | `apps.<system>.default` |
| `nix fmt` | `formatter.<system>` |
| `nix flake check` | 표준 output schema와 `checks.<system>.*` |

## 5. Worked Example

- 문제: Nixpkgs의 `cowsay`를 개발 중과 build 결과 실행 중에 모두 사용할 수 있게 한다.
- 입력: Nixpkgs 26.05 input, `writeShellApplication`, 네 system 목록
- 풀이 과정:
  1. `devShells`에 `pkgs.cowsay`를 넣는다.
  2. `writeShellApplication.runtimeInputs`에도 `pkgs.cowsay`를 넣는다.
  3. package를 app의 `program`에 연결한다.
  4. `runCommand`로 출력에 메시지가 있는지 검사한다.
- 최종 결과: `nix develop`, `nix build`, `nix run`, `nix flake check`가 같은 잠긴
  Nixpkgs input을 공유한다.

## 6. 직접 해보기

1. 개발 셸에 `lolcat`을 추가한다.
2. 이름 있는 app을 추가한다.
3. greeting check를 의도적으로 실패시키고 build log에서 원인을 찾는다.
4. `nixpkgs` input만 갱신하고 lock diff를 복구한다.

## 7. 흔한 오류

| 오류 | 원인 | 확인 방법 | 해결 방법 |
|---|---|---|---|
| 기본 출력 없음 | `default` 이름 누락 | `nix flake show` | 이름 지정 또는 default 추가 |
| 셸에서만 command 실행 | runtime dependency 누락 | build 결과 직접 실행 | `runtimeInputs` 추가 |
| app 실행 파일 없음 | `program` 경로 오타 | `ls result/bin` | 실제 파일명 연결 |
| 새 파일 누락 | Git 미추적 | `git status` | `git add` |
| update 뒤 실패 | lock revision 변화 | `git diff flake.lock` | 검증 또는 Git 복구 |

## 8. 실제 응용

- 프로젝트 개발 환경의 표준 진입점
- package와 CLI application 배포
- CI의 `nix flake check`
- NixOS와 Home Manager input 잠금

## 9. 요약

- Flake는 input pinning과 output schema를 한 저장소 경계에 모은다.
- 명령이 찾는 output 경로를 알면 오류를 평가·build·실행 단계로 나눌 수 있다.
- 작은 `cowsay` 예제로 개발 의존성과 runtime dependency의 차이를 확인한다.

## 10. 초고 점검

- [x] 처음부터 끝까지 읽을 수 있는 형태다.
- [x] 주요 개념이 빠지지 않았다.
- [x] 불확실했던 formatter 이름과 update 명령을 조사 단계에서 확정했다.
- [x] 문장 교정보다 구조 완성을 우선했다.
