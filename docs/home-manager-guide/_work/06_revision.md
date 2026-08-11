---
title: Home Manager 가이드 퇴고 기록
updated: 2026-08-11
---

# 퇴고 반영

- 문서 첫머리에 예제 output 이름과 Flake 기능의 상태를 명확히 했다.
- generation이 Git commit과 다른 복구 단위임을 보강했다.
- session 변수·PATH의 shell 확장 규칙을 공식 옵션 설명에 맞춰 정리했다.
- 재귀 링크의 실제 overlap 동작과 `force`·backup의 데이터 보존 경계를 명시했다.
- 변경·update·rollback·진단 절차를 단계별로 보완했다.

학습성 확인:

- 각 보강점은 바로 앞 개념을 전제로 읽을 수 있다.
- 명령 예제는 `index.md`의 output 이름 주의와 연결된다.
- 문제 해결 장에서 빌드·activation·runtime을 각각 구분한다.
