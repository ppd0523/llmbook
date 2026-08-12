---
stage: 02_research
chapter: 03-six-dof-forward-kinematics
status: complete
updated: 2026-08-11
---

# 3단계 조사 기록

## 참고한 핵심 자료

| 자료 | 확인한 내용 | 본문 반영 |
|---|---|---|
| [MIT OCW 2.12 Chapter 3: Robot Mechanisms](https://ocw.mit.edu/courses/2-12-introduction-to-robotics-fall-2005/resources/chapter3/) | 관절 기본형, 직렬 링크 구조, 직렬 사슬의 각 관절 변위가 독립적인 일반화 좌표라는 설명 | 열린 직렬 사슬, R/P 관절, 관절벡터를 먼저 정의 |
| [MIT OCW 2.12 Chapter 4: Planar Kinematics](https://ocw.mit.edu/courses/2-12-introduction-to-robotics-fall-2005/resources/chapter4/) | 관절 변위에서 말단 위치·방위를 구하는 FK와 반대 문제인 IK의 구분 | 1단계 2R FK를 DH 검산 예제로 다시 사용하고 3D 자세로 확장 |
| [Caltech ME115 2016](https://robotics.caltech.edu/wiki/index.php/ME115_2016) | 직렬 매니퓰레이터 소개 뒤 DH, DH 기반 FK, POE, IK, Jacobian 순서의 강의 구성 | 3단계는 DH와 FK까지, 4단계는 Jacobian과 수치 IK로 경계를 설정 |
| [Caltech ME115 Homework 5 Solution](https://robotics.caltech.edu/~jwb/courses/ME115/homework/sol5a.14.pdf) | DH 표의 각 행을 변환행렬로 바꾸고 직렬 곱으로 FK를 구성하는 예 | DH 표→개별 변환→누적 곱의 검산 절차 반영 |
| [Modern Robotics Chapter 4](https://modernrobotics.northwestern.edu/chapters/chapter4/) | 열린 사슬 FK를 관절변수에서 말단 좌표계 자세로 가는 함수로 정의하고 POE로 계산 | $T(\mathbf q)$라는 입출력 관점을 강조하고 POE는 후속 읽을거리로 분리 |
| [Denavit & Hartenberg (1955)](https://doi.org/10.1115/1.4011045) | 낮은 쌍 기구를 행렬로 일관되게 표기하기 위한 네 매개변수 기법 | 표준 DH의 목적과 이름의 원출처 기록 |
| [Robotics Toolbox: Link](https://www.petercorke.com/RTB/r9/html/Link.html) | 표준 DH와 수정 DH가 별도 규약이며, 회전관절과 직동관절에서 변수가 되는 매개변수가 다름 | 규약 이름과 변환식을 함께 기록하고 서로 섞지 말라는 경고 반영 |

## 교육 설계 판단

1. DH 축 배치를 바로 시작하면 기호가 앞서므로, 먼저 기본 회전·이동을 직접 잇는 변환 체인으로 6R FK의 목적을 보여준다.
2. 1단계의 2R 팔을 표준 DH로 다시 만들면 새 표기와 이미 검증한 삼각함수 식을 연결할 수 있다.
3. 6R 전체 예제는 축 배치가 눈에 보이는 교육용 팔을 사용한다. 특정 상용 로봇의 치수나 DH 표로 일반화하지 않는다.
4. 표준 DH의 네 매개변수와 행렬은 다루되, 축이 겹치거나 교차할 때의 모든 예외적 좌표계 선택은 심화로 넘긴다.
5. POE는 Modern Robotics의 핵심 FK 표현이지만 twist와 행렬지수가 선수 지식이므로 이 장에서는 두 번째 모델링 방법이라는 이름과 다음 읽을거리만 제공한다.
6. 6개 관절과 6차원 자세가 같은 숫자라고 해서 모든 자세가 항상 가능하다고 오해하지 않도록 작업공간, 축 배치, 특이 자세를 미리 경고한다.
7. 한국어로 모두 `작업 공간`이라 쓰기도 하는 task space와 workspace는 각각 `말단 자세 공간`과 `작업공간`으로 구분한다.
8. 2단계의 $3\times3$ 회전행렬 $R_x,R_y,R_z$와 3단계의 $4\times4$ 회전 변환 $\operatorname{Rot}_x,\operatorname{Rot}_y,\operatorname{Rot}_z$를 기호로 구분한다.

## 사실·수식 검증 메모

- 회전관절은 한 축 주위 각도, 직동관절은 한 축을 따르는 거리가 관절변수다.
- 열린 직렬 사슬의 FK는 베이스에서 말단까지 인접 변환을 관절 순서대로 곱한다.
- 이 장의 표준 DH는 ${}^{i-1}A_i=\operatorname{Rot}_z(\theta_i)\operatorname{Trans}_z(d_i)\operatorname{Trans}_x(a_i)\operatorname{Rot}_x(\alpha_i)$로 고정한다.
- 표준 DH 행렬의 이동 열은 $[a_i\cos\theta_i,a_i\sin\theta_i,d_i]^T$다.
- 회전관절에서는 $\theta_i$가 변수이고, 직동관절에서는 $d_i$가 변수다.
- 표준 DH와 수정 DH는 곱 순서와 좌표계 배치가 다르므로 같은 표를 두 공식에 넣을 수 없다.
- 도구 오프셋이 있으면 손목 관절만 움직여도 손목 중심은 고정되지만 TCP 위치는 바뀔 수 있다.
- 여섯 개의 독립 관절변수는 관절공간이 6차원이라는 뜻이다. 도달 가능한 자세와 국소적으로 가능한 움직임은 기구 구조와 현재 자세에 의존한다.

## 출처 적용 범위

- 교과 과정 순서는 MIT·Caltech 공개 강의와 Modern Robotics를 비교해 정했다.
- 본문의 표준 DH 공식은 규약을 명시한 뒤 사용한다.
- 특정 제조사 로봇의 DH 표, 관절 제한, 보정값은 다루지 않는다.
- 6R 교육용 팔의 치수와 축 배치는 수식 학습을 위해 정의한 예이며 실제 로봇 사양이 아니다.
