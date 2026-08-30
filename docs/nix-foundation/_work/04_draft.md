---
title: 초고 검토 기록
version: 0.2
status: final
owner: agent
updated: 2026-08-30
target_reader: Nix 입문자
topic: Nix 기초 학습자료 기존 원고
---

# 초고 검토 기록

## 1. 검토한 원고

- `index.md`
- `01-ecosystem-and-mental-model.md`부터 `08-troubleshooting-and-next-steps.md`

## 2. 기존 원고의 강점

- 개념을 이름과 책임에서 출발해 설정 계층까지 연결한다.
- 각 장에 학습 목표, 직접 해보기, 요약, 공식 자료가 있다.
- Store의 불변성, generation 롤백, `stateVersion`, secret의 범위를 과장하지 않는다.
- module 장은 declaration·definition·최종 `config`를 구분해 설명한다.

## 3. 퇴고가 필요한 지점

| 위치 | 관찰 | 조치 |
|---|---|---|
| 책 소개 | 기준 버전의 영향과 Git index 주의가 뒤늦게 나온다. | 준비 조건과 읽기 원칙에 추가 |
| 1장 | 재현성의 입력 범위가 짧게 언급된다. | source와 lockfile, 구성 밖 조건을 명시 |
| 3장 | `nix path-info`의 동작 범위를 단정적으로 읽을 여지가 있다. | build와 cache 메타데이터 조회를 구분 |
| 4장 | registry와 Git stage의 영향이 분산돼 있다. | 재현 보고와 Flake source 문맥을 보강 |
| 6장 | `home-manager build`를 generation 생성으로 표현한다. | build와 activation·generation 전환을 분리 |
| 6장 | 현재 Home Manager 문서와 다른 `programs.git.userName` 예제를 사용한다. | `programs.git.settings.user.name`으로 갱신 |
| 6장 | Bash 별칭을 정의하지만 Bash module을 활성화하지 않는다. | `programs.bash.enable = true`를 함께 정의 |
| 6장 | Home Manager 복구를 activation package 경로로만 설명한다. | 직전 generation은 공개 CLI의 `switch --rollback`으로 복구하도록 보강 |
| 6장 | 기존 구성에 현재 release의 `stateVersion`을 복사할 위험이 있다. | 새 구성 전용 값이라는 경고 추가 |
| 7장 | tracked 파일 수정에도 stage가 필요하다고 읽힌다. | 새 파일과 tracked 파일의 Flake source 처리 분리 |
| 8장 | Home Manager 관리 파일과 Store 결과의 수정 위치가 모호하다. | 수정할 source와 재적용 절차를 명확화 |
| 5장 | 한 줄 definition을 module이라고 부른 뒤 파일 전체가 module이라고 설명한다. | module과 definition의 경계를 모순 없이 정리 |
