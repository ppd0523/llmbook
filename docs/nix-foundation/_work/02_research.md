---
title: 조사 노트
version: 0.2
status: final
owner: agent
updated: 2026-08-11
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
| 공식문서 | NixOS 26.05 Manual | <https://nixos.org/manual/nixos/stable/> | `nixos-rebuild` 적용·전환·부팅 | 높음 |
| 공식문서 | Home Manager Manual | <https://nix-community.github.io/home-manager/> | standalone 설정, Home Manager 파일 관리 | 높음 |

## 2. 핵심 확인 결과

| 항목 | 검증 결과 | 본문 반영 |
|---|---|---|
| `nix shell` | 지정한 installable을 `PATH`에서 사용할 수 있는 환경에서 명령을 실행하며, 명령이 없으면 `$SHELL`을 시작한다. | 4장과 7장 예제 유지 |
| `nix develop` | 기본 output은 `devShells.<system>.default`, 그다음 `packages.<system>.default` 순서로 찾는다. | 4장 설명 유지 |
| `nix search` | 모든 정규식과 일치하는 package 이름·설명을 검색한다. | 4장 설명 유지 |
| `home-manager build` | 활성화 결과를 build하지만 그 결과만으로 현재 home generation을 전환하지 않는다. | 6장 표현 수정 |
| `home-manager switch` | build와 활성화를 수행하며 generation을 전환한다. | 6장 표현 수정 |
| `nixos-rebuild test` | 실행 중인 시스템을 전환하되 다음 부팅 기본값으로 만들지 않는다. | 6장과 8장 설명 유지 |
| `nix flake update nixpkgs` | 지정한 입력만 갱신하고 lockfile을 변경한다. | 4장과 7장 설명 유지 |

## 3. 주의점

- 새 `nix` CLI와 Flake는 Nix 2.34 문서에서 experimental로 표시된다. 기준 버전과 실제 잠근 입력을 함께 기록한다.
- `nixpkgs` registry는 사용자별로 달라질 수 있으므로, 재현 보고에는 Nix 버전과 lockfile 유무를 포함한다.
- Git 저장소의 Flake는 새 source 파일이 Git index에 포함되지 않아 평가에서 빠질 수 있다. stage와 commit을 구분해 설명한다.

## 4. 조사 결론

- 기존 자료의 기본 구조와 대부분의 기술 설명은 공식 문서와 맞는다.
- Home Manager의 `build`와 generation 표현을 정정한다.
- Store 결과·source·generation을 구분하는 운영 설명을 보강한다.
