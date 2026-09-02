# 04. 초안 기록

## 작성 결과

- 책 소개와 9개 장을 작성했다.
- 설치에서 최종 moving-target 프로젝트까지 순차적으로 연결했다.
- 모든 장에 이전·다음 장 링크를 넣었다.
- 공식 URL은 Isaac Lab v3.0.0-beta2 문서, patch1 태그 소스, Isaac Sim 6.0.1 문서를 우선했다.
- 외부 예제 프로젝트에 Direct/Manager task, 공통 MDP, physics preset, RSL-RL config, 평가 script, URDF를 작성했다.

## 초안의 핵심 설명 순서

1. Isaac Sim과 Isaac Lab의 역할을 구분한다.
2. 실행 환경을 version lock으로 고정한다.
3. 자산을 URDF로 작성하고 Isaac Sim에서 USD로 변환한다.
4. MDP를 코드 전에 표와 수식으로 확정한다.
5. Direct hook으로 한 step의 호출 흐름을 배운다.
6. RSL-RL로 학습하고 독립 지표로 평가한다.
7. 같은 MDP를 Manager-based term으로 분해한다.
8. Newton과 PhysX를 한 변수 실험으로 비교한다.
9. moving target으로 확장한다.

## 의도적으로 포함하지 않은 결과

문서 작성 PC에는 NVIDIA GPU와 Isaac Sim이 없으므로 생성 USD, 학습 checkpoint, 성능 수치를 만들어 넣지 않았다. 대신 대상 PC에서 해당 산출물을 생성하고 검증하는 명령과 통과 기준을 제공했다.
