---
title: 퇴고 기준
status: final
owner: agent
target_reader: Nix 입문자
topic: Nix 기초 학습자료 퇴고
---

# 퇴고 기준

## 1. 퇴고 목표

- 구조: 책 소개(`index.md`)에서 기준 버전·experimental 주의와 Git source 주의를 먼저 제시한다.
- 학습성: source·Store·generation·activation의 경계를 반복되는 실제 작업 흐름으로 연결한다.
  1장은 선언성만으로 입력이 고정되지 않음을, 3장은 generation 롤백 뒤 Git source의 후속
  조치를, 4장은 registry가 재현에 주는 영향을 다룬다.
- 정확성: 6장은 Home Manager build와 switch의 효과를 분리한다.
- 정확성: 6장의 Home Manager Bash 별칭 예제는 module 활성화를 함께 정의해 별칭이 실제
  `.bashrc`에 반영되게 한다.
- 복구성: 6장은 Home Manager의 공개 CLI가 제공하는 직전 generation rollback을 먼저
  안내한다.
- 정확성: 책 소개와 4·7·8장은 새 Git 파일과 tracked 수정 파일의 Flake 평가 조건을 분리한다.
- 버전 적합성: 2·6장의 Home Manager Git option과 6장의 `stateVersion` 예제는 26.05 기준을
  따른다. `stateVersion`은 기존 구성에 현재 release 값을 복사하지 않도록 경고한다.
- 일관성: 5장은 module과 definition의 경계를 모순 없이 설명한다. 8장은 Store 결과를 직접
  수정하지 않고 source를 고쳐 재적용하는 원칙을 둔다.
- 중복 제거: 각 장의 상세 설명은 유지하고, 보강 문단은 각 장의 판단 지점에만 둔다.

## 2. 품질 점검

- [x] 기술 검증 결과가 본문과 일치한다.
- [x] 새 용어의 첫 설명과 표기법이 모든 장에서 일관된다.
- [x] 연습문제는 앞선 본문만으로 풀 수 있다.
- [x] 최종 산출물에 내부 작업 메모와 미검증 표시가 없다.
