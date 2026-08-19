---
title: 구성 설계
version: 0.2
status: final
owner: agent
updated: 2026-08-19
target_reader: Nix 입문자
topic: Nix 기초 학습자료 퇴고 구조
---

# 구성 설계

## 1. 장의 한 문장 요약

Nix의 개념·언어·Store·명령·module을 차례로 쌓아 NixOS, Home Manager, 프로젝트 Flake의 안전한 적용으로 연결한다.

## 2. 학습 흐름

```text
이름과 책임 → Nix 코드 읽기 → Store와 generation → 셸과 Flake → module → 시스템·home 적용 → 통합 실습 → 문제 해결
```

## 3. 섹션 구조

| 장 | 목적 | 다음 장에 주는 이해 |
|---|---|---|
| 1 | 생태계 용어와 공통 작업 흐름 분리 | 입력·평가·실현·활성화 |
| 2 | Nix 표현식 읽기 | 설정 파일과 module 함수 읽기 |
| 3 | Store·profile·generation 설명 | build와 rollback의 범위 |
| 4 | 임시 셸과 개발 셸 선택 | Flake와 lockfile 사용 |
| 5 | module·option·merge 설명 | NixOS/HM 설정 해석 |
| 6 | 책임 계층과 적용 명령 연결 | system·home 운영 판단 |
| 7 | 작은 Flake 실습 | source·lockfile·활성 셸 구분 |
| 8 | 오류 분류와 다음 학습 경로 | 안전한 독립 학습 |

## 4. 퇴고 원칙

- 새 용어는 처음 등장한 문맥에서 목적과 한 문장 정의를 제공한다.
- 추상 개념은 명령, 표, 저장소 구조 또는 직접 해보기로 바로 연결한다.
- `build`·`switch`, Store 결과·source, 새 파일의 stage·tracked 파일의 수정·commit을 혼동하지 않게 분리한다.
- 길게 반복되는 설명은 핵심 규칙을 먼저 제시하고 상세 근거는 해당 장의 공식 자료로 연결한다.
