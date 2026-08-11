---
title: Home Manager 가이드 퇴고 구성
updated: 2026-08-11
---

# 구성 설계

1. `index.md`: 대상 독자, 전제 조건, 표준 작업 흐름, 버전 정책을 제시한다.
2. 1장: 시스템·사용자·프로젝트의 소유권, generation, 상태와 선언을 구분한다.
3. 2장: Flake input, output 이름, 모듈 경계와 Git source 규칙을 설명한다.
4. 3장: 패키지·프로그램 옵션·shell integration·환경 변수의 역할을 연결한다.
5. 4장: Home Manager 옵션과 파일 source를 선택하고, 충돌과 가변 상태를 안전하게 처리한다.
6. 5장: `build` → `switch` → 검증 → commit, 업데이트, rollback 순서를 설명한다.
7. 6장: 실패 단계를 분류하고 output·source·activation·runtime 문제를 좁힌다.

보강할 위험 구간은 `stateVersion`과 lock의 차이, Git staging, recursive file overlap, rollback의 버전 조건, input update 범위다.
