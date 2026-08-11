---
title: 기술 검증
version: 0.2
status: final
owner: agent
updated: 2026-08-11
target_reader: Nix 입문자
topic: Nix 기초 학습자료 기술 검증
---

# 기술 검증

## 1. 검증 결과

| 위치 | 항목 | 결과 | 상태 |
|---|---|---|---|
| 1장 | 선언성·입력 고정·재현성 | 입력 고정의 필요성을 정확히 설명하며 source 범위를 보강 | 반영 |
| 3장 | `nix path-info` | build 수행과 cache 메타데이터 조회를 구분 | 반영 |
| 4장 | `nix shell`, `nix develop`, `nix search` | Nix 2.34 reference의 명령 설명 및 output 탐색 순서와 일치 | 확인 |
| 6장 | Home Manager build·switch | `build`는 활성화 전 검증, `switch`는 활성화와 generation 전환으로 수정 | 반영 |
| 6장 | `nixos-rebuild` 모드 | `build`, `test`, `switch`, `boot` 범위가 NixOS Manual과 일치 | 확인 |
| 7장 | lockfile과 Git index | 변경 입력과 source 포함의 관계가 일관됨 | 확인 |
| 8장 | 문제 해결 명령 | 읽기 전용 진단과 source 수정 원칙이 앞 장과 일치 | 확인 |

## 2. 가정 확인

| 가정 | 타당성 | 본문 반영 |
|---|---|---|
| 독자는 Git 기본 명령을 안다. | 책 소개의 선행지식에 명시됨 | 예 |
| 예제는 Nix 2.34와 26.05 계열에서 읽는다. | index front matter와 준비 조건에 기록 | 예 |
| 독자의 shell과 registry는 다를 수 있다. | 명령 출력의 환경 의존성을 본문에 표시 | 예 |

## 3. 검증 결론

- 공식 문서와 충돌하는 핵심 설명은 발견하지 못했다.
- Home Manager build의 generation 표현은 수정이 필요했고 반영했다.
- 현재 입력과 release note 확인이라는 버전 의존성 경고를 강화했다.
