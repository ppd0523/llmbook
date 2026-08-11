---
title: 초고 검토 기록
version: 0.2
status: final
owner: agent
updated: 2026-08-11
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
| 7장 | stage의 두 역할이 명시되지 않는다. | 평가 포함과 변경 검토를 연결 |
| 8장 | Home Manager 관리 파일과 Store 결과의 수정 위치가 모호하다. | 수정할 source와 재적용 절차를 명확화 |
