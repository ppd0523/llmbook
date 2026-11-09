---
title: Home Manager 가이드 구성
---

# 구성 설계

## 장 구성

1. `index.md`: 대상 독자, 전제 조건, 표준 작업 흐름, 장별 성격과 버전 정책을 제시한다.
2. 1장(개념형): 시스템·사용자·프로젝트의 소유권, generation, 상태와 선언을 구분한다.
3. 2장(개념형): Flake input, output 이름, 모듈 경계와 Git source 규칙을 설명한다.
4. 3장(실습형): 패키지·프로그램 옵션·shell integration·환경 변수의 역할을 연결하고, 새 설정이 보이는 시점(3.10절)을 따로 둔다.
5. 4장(개념형): Home Manager 옵션과 파일 source를 선택하고, 겹친 선언·기존 파일 충돌·가변 상태를 안전하게 처리한다.
6. 5장(실습형): `build` → build 결과 확인 → `switch` → 검증 → commit, 업데이트, rollback 순서를 설명한다.
7. 6장(참조형): 실패 단계를 분류하고 output·source·activation·runtime 문제를 좁힌다.

위험 구간은 `stateVersion`과 lock의 차이, Git staging, 겹친 파일 선언의 조용한 무시, `exec zsh`로는 session 변수가 갱신되지 않는 점, rollback의 버전 조건, input update 범위다.

## 연습과 피드백

| 장 | 문제 | 유형 | 검증할 학습 목표 | 피드백 |
|---|---|---|---|---|
| 1 | 1 계층 배정 6항목 | 분류 | 1 | 정답·해설 |
| 1 | 2 stateVersion 변경 | 비교 | 3 | 정답·해설 |
| 1 | 3 sudo 불필요 이유 | 설명 | 2 | 정답·해설 |
| 1 | 4 즉시 복구와 재발 방지 | 비교 | 2·3 | 정답·해설 |
| 2 | 1 output 이름에서 명령 | 변형 | 1 | 정답·해설 |
| 2 | 2 attribute 생략 실패 | 디버깅 | 1 | 정답·해설 |
| 2 | 3 새 모듈 미추적 | 디버깅 | 2 | 검증 명령 |
| 2 | 4 `extraSpecialArgs` 제거 | 추적 | 3 | 정답·해설 |
| 3 | 1 `jq` 추가 | 실습 | 1 | 기대 출력(`result/home-path/bin/jq`, `command -v`) |
| 3 | 2 `PAGER` 추가 | 실습 | 3 | 기대 출력(같은 터미널 빈 줄, 새 탭 `less -R`) |
| 3 | 3 Git 조건부 include | 실습 | 2 | 검증 명령(`git config --get-regexp`) |
| 3 | 4 fzf hook 중복 | 설명 | 2 | 기대 출력과 해설 |
| 4 | 1 배치 방식 3항목 | 설계 | 1·2 | 정답·해설 |
| 4 | 2 재귀 링크 겹침 결과 | 추적 | 1 | 정답·해설 |
| 4 | 3 부모 링크 겹침 결과 | 추적 | 1 | 정답·해설 |
| 4 | 4 기존 파일 충돌 처리 | 절차 | 3 | 정답·해설 |
| 5 | 1 build 결과 확인 후 switch | 실습 | 1 | 기대 출력(generations의 `(current)`) |
| 5 | 2 rollback 뒤 Git 상태 | 실습 | 3 | 기대 출력과 해설 |
| 5 | 3 input 하나만 갱신 후 복원 | 실습 | 2 | 검증 명령(`git status --short flake.lock`) |
| 6 | 진단 1~4 | 디버깅 | 1·2·3 | 정답·해설 |

3·5장 실습은 예제 구성에서 바로 할 수 있고 `git restore`와 재`switch`로 원래 상태로 돌아갈 수 있는 변경만 쓴다. 4장의 충돌은 독자의 실제 파일을 옮기게 되므로 실습 대신 결과 예측 문제로 둔다.
