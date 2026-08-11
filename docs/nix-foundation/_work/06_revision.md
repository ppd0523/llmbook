---
title: 퇴고 계획 및 반영 내역
version: 0.2
status: final
owner: agent
updated: 2026-08-11
target_reader: Nix 입문자
topic: Nix 기초 학습자료 퇴고
---

# 퇴고 계획 및 반영 내역

## 1. 퇴고 목표

- 구조 개선: 책 소개에서 기준 버전과 Git source 주의를 먼저 제시한다.
- 학습성 개선: source·Store·generation·activation의 경계를 반복되는 실제 작업 흐름으로 연결한다.
- 정확성 개선: Home Manager build와 switch의 효과를 분리한다.
- 중복 제거: 기존 장의 상세 설명은 유지하고, 보강 문단은 각 장의 판단 지점에만 둔다.

## 2. 반영 내역

| 변경 항목 | 반영 위치 | 이유 |
|---|---|---|
| 버전·experimental 주의 | `index.md` | 예제의 기준과 현재 release 확인 기준을 분명히 함 |
| source와 lockfile의 관계 | 1장 | 선언성만으로 입력이 고정되지 않는다는 설명 보강 |
| Store 결과와 Git source 복구 | 3장 | generation 롤백 뒤의 후속 조치 명시 |
| registry·stage 주의 | 4장 | 재현과 Flake source 포함을 구체화 |
| Home Manager build·switch 분리 | 6장 | generation에 관한 부정확한 표현 수정 |
| stage 검토 절차 | 7장 | 평가 포함과 commit을 구분 |
| 관리 파일 수정 위치 | 8장 | Store 결과를 직접 수정하지 않는 원칙 강화 |

## 3. 품질 점검

- [x] 기술 검증에서 나온 수정 사항을 반영했다.
- [x] 새 용어의 첫 설명과 표기법이 기존 장 전체에서 일관된다.
- [x] 연습문제는 앞선 본문만으로 풀 수 있다.
- [x] 최종 산출물에 내부 작업 메모와 미검증 표시가 없다.
