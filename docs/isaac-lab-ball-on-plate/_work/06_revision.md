# 06. 퇴고 결과

## 내용 기준

- Isaac Lab 3.0 외부 프로젝트는 통합 `train` 명령에서 자동 발견되지 않으므로 `--external_callback ball_on_plate_lab.tasks.register` 경로를 쓴다.
- URDF converter의 output 인자는 directory이며 파일명은 robot 이름으로 결정되는 6.0 importer 동작을 따른다.
- generated USD를 검증한 답안처럼 제공하지 않고, 전체 layered output을 보관하는 절차와 환경 변수 fallback을 둔다.
- 관측을 12차원으로 고정해 center task와 moving-target task가 같은 network shape를 쓰게 한다.
- 공의 실패 경계는 `R`이 아니라 `R-r_ball`이며 이를 강조한다.
- startup material randomization은 Newton과 PhysX backend별 구현을 사용하는 공식 event term을 쓴다.
- 평가는 finite evaluator로 random policy와 learned policy에 같은 seed와 정의를 적용한다.
- 문서 작성 PC와 실제 실행 PC의 역할을 모든 실행 결과 설명에서 분리한다.

## 표현 기준

- Isaac Sim과 Isaac Lab을 경쟁 선택지처럼 표현하지 않고 simulation layer와 learning framework layer로 설명한다.
- “성공할 것이다”라는 예측 대신 확인 명령, 예상 shape, pass/fail gate를 사용한다.
- PPO 수식 반복을 줄이고 환경 contract와 디버깅 순서에 지면을 배분한다.
- 백엔드, 체크포인트, 런타임 등 반복되는 기술어는 한글 표기로 통일하되 코드 식별자와 공식 방식명은 유지한다.
