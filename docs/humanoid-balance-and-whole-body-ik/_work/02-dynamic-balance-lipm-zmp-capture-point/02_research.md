---
stage: 02_research
chapter: 06-dynamic-balance-lipm-zmp-capture-point
status: complete
updated: 2026-08-12
---

# 6단계 조사 노트

## 1. 핵심 출처

| 구분 | 자료 | 사용할 내용 | 적합성 |
|---|---|---|---|
| MIT 공개 강의 | Underactuated Robotics, Ch. 5: Highly-articulated Legged Robots | 전신 CoM, 전신 운동량 변화와 외력 합, 센트로이달 관점 | 직접 관련 |
| MIT 공개 강의 | Underactuated Robotics, Ch. 4: Simple Models of Walking and Running | 단순 보행 모형, 접촉 상태에 따른 구간별 동역학 | 직접 관련 |
| MIT 공개 강의 | Underactuated Robotics, Ch. 23: Multi-Body Dynamics | 접촉력, 접촉 자코비안, 접촉 생성·해제의 복잡성 | 직접 관련 |
| Caltech 연구 공개본 | Xiong & Ames, 3-D Underactuated Bipedal Walking via H-LIP Based Gait Synthesis and Stepping Stabilization | LIP 기반 축소 모형과 걸음 간 CoM 상태 연결 | 직접 관련 |
| Caltech 연구 공개본 | Xiong & Ames, Dynamic and Versatile Humanoid Walking via Embedding 3D Actuated SLIP Model with Hybrid LIP Based Stepping | 축소 모형 목표를 전신 휴머노이드 동작에 연결하는 계층 | 직접 관련 |
| 원 논문 | Kajita et al., Biped Walking Pattern Generation by Using Preview Control of Zero-Moment Point | CoM 운동과 ZMP 관계, 보행 패턴 생성의 역문제 | 직접 관련 |
| 원 논문 | Pratt et al., Capture Point: A Step toward Humanoid Push Recovery | LIPM의 캡처 포인트, 지지 영역과 한 걸음 판단 | 직접 관련 |
| 원 논문 | Vukobratović & Borovac, Zero-Moment Point—Thirty Five Years of Its Life | ZMP 정의, 지지 경계와 가상 ZMP 주의, CoP 구분 | 직접 관련 |

## 2. 핵심 정의와 본문 표기

| 용어 | 독자 수준의 한 문장 정의 | 원어/약어 | 혼동 방지 |
|---|---|---|---|
| 상태 | 한 시점의 운동을 예측하는 데 필요한 위치와 속도 정보 | state | 자세는 위치 정보만 가리킬 수 있다. |
| 궤적 | 시간마다 목표 상태가 어떻게 바뀌는지 정한 함수 또는 표 | trajectory | 경로는 시간 정보가 없을 수 있다. |
| 지면반력 | 발이 바닥을 누를 때 바닥이 발에 되돌려 주는 힘 | ground reaction force, GRF | 중력과 별개인 외력이다. |
| 모멘트 | 힘이 한 점 주위를 회전시키려는 효과 | moment | 2D에서는 힘×수직거리의 부호 있는 수다. |
| 압력중심 | 분포된 바닥 압력을 하나의 합력으로 바꿨을 때 그 합력이 작용하는 위치 | center of pressure, CoP | 실제 접촉 영역 안에 있어야 한다. |
| 영모멘트점 | 지면반력의 수평축 모멘트가 0이 되는 바닥 위 기준점 | zero-moment point, ZMP | 동적 평형이 가능한 경우 CoP와 일치해 사용할 수 있다. |
| 축소 모형 | 전체 로봇의 많은 자유도 중 핵심 변수만 남긴 근사 모형 | reduced-order model, ROM | 전체 로봇의 정확한 관절 운동이 아니다. |
| 선형 역진자 모형 | CoM을 일정 높이의 점질량으로, 다리를 질량 없는 연결로 보는 보행 근사 | linear inverted pendulum model, LIPM | 일정 높이와 작은 접촉 모멘트 가정이 중요하다. |
| 캡처 포인트 | LIPM에서 그 위치를 지지 영역에 포함하고 CoP를 두면 한 발로 정지 상태에 접근할 수 있는 바닥점 | capture point, CP | 일반 휴머노이드의 정확한 유일 해가 아니다. |
| 하이브리드 동역학 | 접촉 중 연속 운동과 착지 같은 이산 사건이 함께 있는 동역학 | hybrid dynamics | 단순히 두 모델을 섞는다는 일상 뜻과 다르다. |

## 3. 핵심 수식과 조건

| 항목 | 식 | 가정·적용 조건 | 검증 |
|---|---|---|---|
| CoM 병진 동역학 | \(M\ddot{\mathbf p}_G=M\mathbf g+\sum_i\mathbf f_i\) | 외력만 합산, 관절 내부력 상쇄 | MIT 센트로이달 식과 일치 |
| 2D 모멘트 | \(\tau_y=r_zF_x-r_xF_z\) 또는 선택한 부호 규약 | 기준점과 축 부호 고정 | 직접 전개 |
| LIPM | \(\ddot x=\frac gh(x-p)=\omega^2(x-p)\) | CoM 높이 \(h\) 일정, 점질량, 각운동량 변화 무시, 평평한 바닥 | Pratt/Kajita 계열과 일치 |
| 요구 CoP | \(p_{\mathrm{req}}=x-\frac hg\ddot x_d\) | 위 LIPM 가정 | LIPM 대수 변형 |
| 자연 각주파수 | \(\omega=\sqrt{g/h}\) | \(g,h>0\) | 단위 \(1/s\) 확인 |
| LIPM 시정수 | \(T_c=1/\omega=\sqrt{h/g}\) | LIPM | 단위 s 확인 |
| 캡처 포인트 | \(\xi=x+\dot x/\omega\) | 1D LIPM, 발 재배치 가능, 각운동량 효과 무시 | Pratt 식의 세계좌표 표현 |
| CP 동역학 | \(\dot\xi=\omega(\xi-p)\) | CoP \(p\)와 LIPM | 미분·대입 검증 |
| 5차 시간 스케일 | \(s(r)=10r^3-15r^4+6r^5\) | \(0\le r\le1\) | 양 끝 위치 0/1, 속도·가속도 0 검산 |

## 4. 기술적 주의점

- 전신 CoM 병진식은 정확한 운동량 관계지만, 가능한 접촉력과 관절 토크 조건을 아직 포함하지 않는다.
- CoP는 실제 압력 분포에서 얻는 접촉 결과다. ZMP는 동역학적 모멘트 조건으로 계산하는 점이며, 정상적인 평평한 접촉에서 지지 영역 안에 있을 때 같은 위치로 해석하는 경우가 많다.
- 계산된 ZMP가 지지 영역 밖이면 그 위치에 실제 CoP를 만들 수 있다는 뜻이 아니다. 요구가 물리적으로 실현 불가능함을 알리는 값일 수 있다.
- LIPM은 CoM 높이 변화, 큰 몸통 각운동량, 발 회전, 비평면 접촉과 비행 구간을 표현하지 못한다.
- CP 공식은 LIPM의 단일 점이다. 일반 휴머노이드에서는 가능한 멈춤 발 위치가 영역이 되며 동역학·관절·접촉 제약에 의존한다.
- 지지 다각형 안 CoM 투영은 정적 기하 판단이고, CP는 속도를 포함한 LIPM 동적 판단이다.

## 5. 예제 후보와 검산값

| 예제 | 입력 | 기대 결과 |
|---|---|---|
| 이산 궤적 | \(\Delta t=0.1\) s, \(x_{k-1}=0.02,x_k=0.05,x_{k+1}=0.10\) m | \(\dot x_k\approx0.4\) m/s, \(\ddot x_k\approx2.0\) m/s² |
| 요구 CoP | \(x=0.04\) m, \(h=0.8\) m, \(\ddot x_d=0.50\) m/s² | \(p_{\mathrm{req}}\approx-0.0008\) m |
| 캡처 포인트 | \(x=0.02\) m, \(\dot x=0.35\) m/s, \(h=0.8\) m | \(T_c=0.2856\) s, \(\xi\approx0.120\) m |
| 높이 비교 | 같은 \(x,\dot x\), \(h=0.5\) vs 1.0 m | 높은 CoM일수록 \(T_c\)와 속도 보정 거리 증가 |

## 6. 출처·범위 결론

- MIT 자료는 정확한 전신 운동량 관계와 단순 보행 모형의 교육 흐름을 제공한다.
- Caltech 공개 연구는 LIP/H-LIP 축소 상태를 스텝 계획과 전신 휴머노이드에 연결하는 현대적 사례다.
- Kajita, Pratt, Vukobratović 원 논문은 ZMP·LIPM·CP의 정의와 한계를 고정한다.
- preview control, MPC, 피드백 제어 설계는 출처에 포함되지만 본문에서는 다음 학습으로만 안내한다.

## 7. 품질 점검

- [x] 핵심 정의와 수식에 1차 또는 공식 출처가 있다.
- [x] 수식마다 적용 조건이 있다.
- [x] CoP·ZMP와 CP의 과도한 일반화를 경계한다.
- [x] Worked Example 수치를 독립 계산할 수 있다.
- [x] 제외 범위의 제어 내용을 본문 주장과 분리했다.
