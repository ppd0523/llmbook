---
title: 조사 노트
version: 0.2
status: final
owner: agent
updated: 2026-08-30
target_reader: Nix 입문자
topic: Nix 기초 학습자료 기술 검증
---

# 조사 노트

## 1. 핵심 출처

| 구분 | 제목/문서 | 링크 | 사용할 내용 | 신뢰도 |
|---|---|---|---|---|
| 공식문서 | Nix 2.34 `nix shell` | <https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-env-shell.html> | `PATH`, 기본 shell, `--command` | 높음 |
| 공식문서 | Nix 2.34 `nix develop` | <https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-develop.html> | 개발·빌드 환경, output 탐색 순서 | 높음 |
| 공식문서 | Nix 2.34 `nix search` | <https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-search.html> | 정규식 검색과 output 경로 | 높음 |
| 공식문서 | Nix 2.34 `nix flake update` | <https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-flake-update.html> | 선택 입력 갱신과 lockfile | 높음 |
| 공식문서 | Nix 2.34 Flake reference | <https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-flake.html> | 로컬 Git Flake의 tracked·dirty source 처리 | 높음 |
| 공식문서 | NixOS 26.05 Manual | <https://nixos.org/manual/nixos/stable/> | `nixos-rebuild` 적용·전환·부팅 | 높음 |
| 공식문서 | Home Manager Manual | <https://nix-community.github.io/home-manager/> | standalone 설정, Home Manager 파일 관리 | 높음 |
| 구현체 | Home Manager 26.05 Git module | <https://github.com/nix-community/home-manager/blob/release-26.05/modules/programs/git.nix> | `userName`에서 `settings.user.name`으로의 option rename | 높음 |
| 구현체 | Home Manager 26.05 Bash module | <https://github.com/nix-community/home-manager/blob/release-26.05/modules/programs/bash.nix> | `shellAliases`가 `enable` 조건 아래에서 `.bashrc`에 반영되는 구조 | 높음 |
| 구현체 | Home Manager 26.05 CLI | <https://github.com/nix-community/home-manager/blob/release-26.05/home-manager/home-manager> | `build`, `switch`, `switch --rollback`의 activation·generation 효과 | 높음 |

## 2. 핵심 확인 결과

| 항목 | 검증 결과 | 본문 반영 |
|---|---|---|
| `nix shell` | 지정한 installable을 `PATH`에서 사용할 수 있는 환경에서 명령을 실행하며, 명령이 없으면 `$SHELL`을 시작한다. | 4장과 7장 예제 유지 |
| `nix develop` | 기본 output은 `devShells.<system>.default`, 그다음 `packages.<system>.default` 순서로 찾는다. | 4장 설명 유지 |
| `nix search` | 모든 정규식과 일치하는 package 이름·설명을 검색한다. | 4장 설명 유지 |
| 로컬 Git Flake | Git에 추가된 파일을 source로 사용하며, tracked 파일의 미커밋 수정은 dirty source로 평가한다. | 새 파일과 tracked 파일의 stage 필요 여부를 4·7·8장에서 분리 |
| `home-manager build` | 활성화 결과를 build하지만 그 결과만으로 현재 home generation을 전환하지 않는다. | 6장 표현 수정 |
| `home-manager switch` | build와 활성화를 수행하며 generation을 전환한다. | 6장 표현 수정 |
| `programs.git` | 현재 option 문서는 사용자 이름을 `programs.git.settings.user.name` 아래에 둔다. | 2장과 6장 예제 갱신 |
| `programs.bash` | `shellAliases`는 `programs.bash.enable`이 참일 때 생성되는 `.bashrc`에 반영된다. | 6장 예제에 `enable = true` 추가 |
| `home-manager switch --rollback` | 직전 profile generation으로 되돌리고 해당 activation script를 실행한다. | 6장의 복구 흐름 보강 |
| `nixos-rebuild test` | 실행 중인 시스템을 전환하되 다음 부팅 기본값으로 만들지 않는다. | 6장과 8장 설명 유지 |
| `nix flake update nixpkgs` | 지정한 입력만 갱신하고 lockfile을 변경한다. | 4장과 7장 설명 유지 |

## 3. 주의점

- 새 `nix` CLI와 Flake는 Nix 2.34 문서에서 experimental로 표시된다. 기준 버전과 실제 잠근 입력을 함께 기록한다.
- `nixpkgs` registry는 사용자별로 달라질 수 있으므로, 재현 보고에는 Nix 버전과 lockfile 유무를 포함한다.
- Git 저장소의 Flake는 새 source 파일이 Git index에 포함되지 않아 평가에서 빠질 수 있다. 이미 tracked인 파일의 수정은 stage하지 않아도 dirty source로 평가된다.
- `stateVersion = "26.05"` 예제는 26.05에서 처음 만든 새 구성에만 그대로 적용한다. 기존 구성은 release upgrade와 별개로 현재 값을 유지한다.

## 4. 조사 결론

- 기존 자료의 기본 구조와 대부분의 기술 설명은 공식 문서와 맞는다.
- Home Manager의 `build`와 generation 표현을 정정한다.
- Store 결과·source·generation을 구분하는 운영 설명을 보강한다.
- Git source의 새 파일과 tracked 수정 파일을 구분하고, Home Manager Git option 예제를 현재 구조로 갱신한다.
- Home Manager Bash 별칭 예제의 활성화 누락을 수정하고, 공개 CLI가 지원하는 직전
  generation rollback 절차를 설명한다.
