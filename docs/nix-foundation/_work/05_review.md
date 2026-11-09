---
title: 기술 검증
status: final
owner: agent
target_reader: Nix 입문자
topic: Nix 기초 학습자료 기술 검증
---

# 기술 검증

## 1. 검증 결과

| 위치 | 항목 | 결과 | 상태 |
|---|---|---|---|
| 1장 | 선언성·입력 고정·재현성 | 입력 고정의 필요성과 source 범위를 정확히 설명한다 | 확인 |
| 3장 | `nix path-info` | build 수행과 cache 메타데이터 조회를 구분한다 | 확인 |
| 4장 | `nix shell`, `nix develop`, `nix search` | Nix 2.34 reference의 명령 설명 및 output 탐색 순서와 일치 | 확인 |
| 4·7·8장 | 로컬 Git Flake source | 새 파일은 Git에 추가해야 하며 tracked 파일의 dirty 수정은 stage 전에도 평가됨을 설명한다 | 확인 |
| 5장 | module·definition 구분 | 한 줄 definition과 파일 단위 module의 관계를 모순 없이 설명한다 | 확인 |
| 6장 | Home Manager build·switch | `build`는 활성화 전 검증, `switch`는 활성화와 generation 전환으로 설명한다 | 확인 |
| 2·6장 | Home Manager Git option | 예제가 26.05 option 문서의 `programs.git.settings.user.name` 구조를 따른다 | 확인 |
| 6장 | Home Manager Bash 별칭 | 26.05 Bash module은 `enable`이 참일 때만 `.bashrc`와 별칭을 생성하며, 예제가 이를 따른다 | 확인 |
| 6장 | Home Manager rollback | 26.05 CLI의 `switch --rollback`은 직전 profile generation을 선택하고 activation script를 실행함 | 확인 |
| 6장 | `stateVersion` 예제 | 새 26.05 구성 전용 값이며 기존 구성에서는 유지해야 함을 명시한다 | 확인 |
| 6장 | `nixos-rebuild` 모드 | `build`, `test`, `switch`, `boot` 범위가 NixOS Manual과 일치 | 확인 |
| 7장 | lockfile과 Git index | 입력 갱신, 새 source 포함, tracked 파일 수정을 분리한다 | 확인 |
| 8장 | 문제 해결 명령 | 읽기 전용 진단과 source 수정 원칙이 앞 장과 일치 | 확인 |

## 2. 가정 확인

| 가정 | 타당성 | 본문 반영 |
|---|---|---|
| 독자는 Git 기본 명령을 안다. | 책 소개의 선행지식에 명시됨 | 예 |
| 예제는 Nix 2.34.9와 26.05 계열에서 읽는다. | index front matter와 준비 조건에 기록 | 예 |
| 독자의 shell과 registry는 다를 수 있다. | 명령 출력의 환경 의존성을 본문에 표시 | 예 |

## 3. 검증 결론

- Nix 2.34.9와 26.05 공식 문서·구현을 기준으로 명령 의미, Home Manager Git option·Bash
  enable 조건·rollback, 로컬 Git Flake의 stage 설명, module·definition 구분, `stateVersion`
  예제의 적용 조건, output 탐색 순서를 확인했다.
