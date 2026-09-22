---
stage: 02_research
chapter: 05-humanoid-whole-body-inverse-kinematics
status: complete
updated: 2026-08-12
---

# 5단계 조사 기록

## 핵심 출처

| 구분 | 자료 | 사용할 내용 | 신뢰도 |
|---|---|---|---|
| MIT 공개 강의 | [Robotic Manipulation, Ch. 3: Basic Pick and Place](https://manipulation.mit.edu/pick.html) | 기구학 트리, 세계에 고정되지 않은 부유 베이스, 프레임 FK와 자코비안의 연결 | 높음 |
| MIT 공개 강의 | [Underactuated Robotics, Ch. 4: Simple Models of Walking and Running](https://underactuated.mit.edu/simple_legs.html) | 보행은 접촉을 포함하며 정적 지지 다각형 조건만으로 동적 보행을 모두 설명할 수 없다는 범위 구분 | 높음 |
| Caltech 공개 강의 | [ME115 2016](https://robotics.caltech.edu/wiki/index.php/ME115_2016) | 특이점→여유 기구→의사역행렬→여유도 해소→접촉·준정적 locomotion의 교육 순서 | 높음 |
| Caltech 강의 노트 | [The Moore–Penrose Pseudo Inverse](https://www.robotics.caltech.edu/~jwb/courses/ME115/handouts/pseudo.pdf) | 최소 크기 해, 영공간과 여유 자유도의 선형대수 근거 | 높음 |
| 논문 | [Siciliano & Slotine (1991), A General Framework for Managing Multiple Tasks in Highly Redundant Robotic Systems](https://doi.org/10.1109/ICAR.1991.240390) | 낮은 과제를 높은 과제의 영공간에서 수행하는 재귀적 과제 우선순위 | 높음 |
| 논문 | [Sentis & Khatib (2006), A Whole-Body Control Framework for Humanoids Operating in Human Environments](https://khatib.stanford.edu/publications/pdfs/Sentis_2006_ICRA.pdf) | 접촉·관절 제한 같은 제약, 발 같은 동작 과제, 자세 과제의 계층과 기구학적 실행 가능성 | 높음 |
| 논문 | [Escande, Mansard & Wieber (2014), Hierarchical Quadratic Programming](https://gepettoweb.laas.fr/uploads/Publications/2014_escande_ijrr.pdf) | 등식·부등식 과제를 엄격한 계층으로 푸는 HQP의 역할과 관절 제한의 부등식 표현 | 높음 |
| 공식 구현 문서 | [Pinocchio](https://stack-of-tasks.github.io/pinocchio/index.html) | 자유 기저 휴머노이드, 프레임 자코비안과 질량중심·질량중심 자코비안이 실제 다물체 라이브러리의 기본 연산임을 확인 | 높음 |
| 교과서 공개 자료 | [Modern Robotics, Ch. 5](https://modernrobotics.northwestern.edu/nu-gm-book-resource/velocity-kinematics-and-statics/) | 자코비안, 영공간과 프레임 속도 관계의 복습 | 높음 |

## 핵심 정의와 용어 도입

| 용어 | 독자 수준의 한 문장 정의 | 원어/약어 | 혼동 방지 |
|---|---|---|---|
| 기구학 트리 | 골반에서 두 다리·두 팔처럼 여러 갈래로 뻗는 링크 연결 구조 | kinematic tree | 한 줄로 이어지는 직렬 체인과 비교한다. |
| 부유 베이스 | 세계 좌표계에 용접되지 않아 위치 3개와 방위 3개가 바뀔 수 있는 기준 몸체 | floating base | 여섯 값을 직접 구동하는 모터가 있다는 뜻이 아니다. |
| 일반화 좌표 | 베이스 자세와 모든 관절값을 함께 모아 로봇 자세를 나타내는 변수 | generalized coordinates | 구현에 따라 방위 표현 때문에 위치벡터와 속도벡터 차원이 다를 수 있다. |
| 접촉 과제 | 바닥에 닿은 발의 자세 변화를 허용하지 않는 최고 우선순위 기구학 조건 | contact task | 실제 접촉력이나 마찰 조건까지 보장하지 않는다. |
| 단일 지지 | 한 발만 지지 접촉으로 사용하는 구간 | single support | 반대 발은 스윙발이다. |
| 이중 지지 | 두 발을 모두 지지 접촉으로 사용하는 구간 | double support | 제약이 늘어 여유도가 줄어든다. |
| 전신 역기구학 | 여러 몸체 프레임과 자세 목표를 전신 변수 하나로 함께 푸는 IK | whole-body inverse kinematics, WBIK | 제어·역동역학과 분리한다. |
| 과제 계층 | 과제를 중요도 순서의 층으로 나눈 구조 | task hierarchy | 숫자 가중치만 크게 주는 것과 다르다. |
| 엄격한 우선순위 | 낮은 과제가 높은 과제의 최적 결과를 바꾸지 못하게 하는 규칙 | strict priority | 영공간 투영 또는 HQP로 구현한다. |
| 등식 제약 | 목표값을 정확히 하나로 맞추는 조건 | equality constraint | 발 자세 고정이 대표 예다. |
| 부등식 제약 | 값이 허용 구간 안에 있으면 되는 조건 | inequality constraint | 관절 제한·안전 거리가 대표 예다. |
| 질량중심 | 각 링크 위치를 질량으로 가중 평균한 한 점 | center of mass, CoM | 압력중심·ZMP와 다르다. |
| 지지 다각형 | 바닥 접촉 영역들을 감싸는 가장 작은 볼록 영역 | support polygon | CoM 투영 포함은 정적 기하 지표이며 동적 안정성 보장이 아니다. |
| 실행 가능성 | 현재 제약 안에서 과제 오차를 허용 범위까지 줄일 수 있는 성질 | feasibility | 낮은 과제 잔차가 남아도 높은 접촉은 실행 가능할 수 있다. |

## 핵심 수식과 검증 상태

| 항목 | 내용 | 가정과 적용 범위 | 근거 | 상태 |
|---|---|---|---|---|
| 일반화 좌표 | $\mathbf q=[\mathbf p_B;\boldsymbol\theta_B;\mathbf q_j]$ | 개념식이며 실제 3D 구현은 쿼터니언 등 다른 방위 좌표를 쓸 수 있다. | MIT Manipulation | 검증 |
| 프레임 과제 | $\mathbf e_i\approx J_i\Delta\mathbf q$ | 모든 오차와 자코비안을 같은 좌표계·행 순서로 표현한다. | Modern Robotics, 4단계 | 검증 |
| 접촉 유지 | $J_s\Delta\mathbf q=\mathbf0$ | 현재 지지발이 이미 목표 자세에 있다는 속도/증분 수준 표현이다. | Sentis & Khatib | 검증 |
| 가중 누적 | $\min_{\Delta q}\sum_i w_i\|J_i\Delta q-e_i\|^2+\lambda^2\|\Delta q\|^2$ | 유한한 가중치는 타협을 만들며 엄격한 우선순위를 보장하지 않는다. | Escande et al. | 검증 |
| 1순위 해 | $\Delta q_1=J_1^+e_1$ | Moore–Penrose 기준, 국소 선형식 | Caltech 의사역행렬 노트 | 검증 |
| 영공간 투영 | $N_1=I-J_1^+J_1$ | 이상적 Moore–Penrose 의사역행렬에서 $J_1N_1=0$ | Caltech, Siciliano & Slotine | 검증 |
| 2순위 해 | $\Delta q=\Delta q_1+N_1(J_2N_1)^+(e_2-J_2\Delta q_1)$ | 높은 과제를 만족한 뒤 남는 자유도에서 두 번째 과제 잔차를 줄인다. | Siciliano & Slotine | 검증 |
| 관절 제한 | $q_{min}-q\le\Delta q\le q_{max}-q$ | 업데이트 변수에 대한 선형 부등식 | Escande et al. | 검증 |
| 질량중심 | $p_G=M^{-1}\sum_i m_ip_i$, $M=\sum_i m_i$ | 링크별 질량과 링크 질량중심 위치가 필요하다. | Pinocchio 기능·표준 역학 정의 | 검증 |
| CoM 자코비안 | $J_G=M^{-1}\sum_i m_iJ_{G_i}$ | 각 링크 CoM 자코비안을 같은 좌표계로 표현한다. | Pinocchio CoM Jacobian | 검증 |

## 교육 설계 판단

1. 6R 팔과 달리 휴머노이드는 여러 갈래의 트리이고 세계에 고정된 베이스가 없다는 차이부터 설명한다.
2. 부유 베이스를 도입하되 쿼터니언 적분은 범위 밖으로 두고, 작은 자세 변화의 여섯 성분이라는 개념에 집중한다.
3. 접촉은 힘 문제가 되기 전에 기구학적으로 지지발 자세를 고정하는 과제라고 설명한다. 실제 접촉 유지에는 마찰·접촉력이 필요함을 즉시 경고한다.
4. 과제는 접촉→스윙발·골반·CoM→기준 자세의 세 종류로 분류한다.
5. 가중 누적식을 먼저 복습한 뒤 충돌 예를 보여 주고, 그 실패를 해결하려고 엄격한 우선순위를 도입한다.
6. 두 변수 손계산 예제로 $J_1N_1=0$을 직접 확인한 뒤 여러 단계 재귀 알고리즘으로 확장한다.
7. 관절 제한은 목표값이 아니라 허용 구간이므로 부등식이라고 설명하고, 사후 클리핑이 접촉을 깨뜨리는 수치 예를 제공한다.
8. HQP는 왜 필요한지만 소개하고 솔버 유도는 심화 자료로 넘긴다.
9. 질량중심과 지지 다각형은 locomotion 연결에 필요하지만, 정적 기하 조건과 동적 안정성을 명확히 분리한다.
10. 실습은 평면 부유 골반과 두 2R 다리를 사용해 같은 시작 자세에서 가중 DLS와 우선순위 IK를 동시에 비교한다.

## 예제 후보와 채택

| 예제 | 보여줄 개념 | 채택 |
|---|---|---|
| 2변수 지지발·골반 투영 | $N_1$, $J_1N_1=0$, 두 번째 과제 잔차 | Worked Example 1 |
| 관절 제한과 충돌 | 사후 클리핑의 지지발 드리프트, 우선순위 해 | Worked Example 2 |
| 2D 두 다리 시각화 | 단일·이중 지지, 가중 해와 계층 해, CoM 투영 | HTML 실습 |

## 논쟁점과 주의점

- 로봇 문헌은 속도 수준의 과제 우선순위도 흔히 제어라고 부른다. 이 장에서는 모터·힘·시간 응답을 다루지 않고 한 자세를 찾는 반복 기구학 계산으로만 사용한다.
- DLS로 만든 $I-J_\lambda^\#J$는 정확한 영공간 투영자가 아니다. 엄격한 우선순위 식은 Moore–Penrose 의사역행렬을 기준으로 설명하고, 실습의 작은 감쇠는 수치 근사임을 표시한다.
- 접촉 발 자세를 고정하는 IK는 바닥이 실제로 발을 지탱할 힘을 낼 수 있는지 검사하지 않는다.
- 지지 다각형 안의 CoM 투영은 정지·준정적 상황의 직관이다. 빠른 보행, 충돌과 관성 효과에는 동역학 지표가 필요하다.
- 부유 베이스의 3D 방위를 세 개의 Euler 각으로 전역 매개화하지 않는다. 본문 기호 $\boldsymbol\theta_B$는 국소 회전 변화의 개념 표기다.

## 조사 결론

- MIT 자료로 트리·부유 베이스와 locomotion의 접촉·동역학 경계를 보강한다.
- Caltech의 여유 기구·의사역행렬 교육 흐름을 4단계에서 이어 간다.
- Siciliano–Slotine의 영공간 재귀를 입문 수식의 기준으로 삼는다.
- Sentis–Khatib의 제약→동작 과제→자세 과제 분류를 휴머노이드 사례의 기준으로 삼되 동역학 부분은 제외한다.
- Escande 등의 HQP는 등식·부등식과 엄격한 계층이 함께 필요할 때의 다음 구현 단계로 소개한다.
- 핵심 정의, 수식, 알고리즘에 출처가 확보되어 초고 단계로 진행할 수 있다.

## 품질 점검

- [x] 정의, 수식과 알고리즘의 출처가 기록되어 있다.
- [x] 새 용어의 정의, 원어·약어와 혼동 개념이 정리되어 있다.
- [x] 공개 강의, 원 논문과 공식 구현 문서를 우선했다.
- [x] 적용 조건과 범위 제한을 기록했다.
- [x] 출처가 필요한 핵심 주장 없이 초고로 진행할 수 있다.
