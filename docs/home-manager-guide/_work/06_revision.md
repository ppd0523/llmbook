---
title: Home Manager 가이드 퇴고 기록
---

# 퇴고 기준

- 문서 첫머리에 예제 output 이름과 Flake 기능의 experimental 상태, 사용 중인 lock 기준 확인을 밝힌다.
- generation이 Git commit과 다른 복구 단위임을 설명한다.
- session 변수·PATH의 shell 확장 규칙은 공식 옵션 설명을 따른다.
- 재귀 링크의 실제 overlap 결과를 구체적으로 보이고, 겹치지 않도록 권고한다. `force`·backup의 데이터 보존 경계를 명시한다.
- 변경·update·rollback·진단 절차를 단계별로 둔다. update는 전체 갱신과 input 이름을 지정한 갱신을 함께 제시하고, rollback 명령에는 최소 Home Manager version(25.11)을 적는다.

학습성 확인:

- 각 보강점은 바로 앞 개념을 전제로 읽을 수 있다.
- 명령 예제는 `index.md`의 output 이름 주의와 연결된다.
- 문제 해결 장에서 빌드·activation·runtime을 각각 구분한다.
