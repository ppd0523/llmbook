---
title: 로보틱스 역기구학 입문
version: 1.0
updated: 2026-08-12
---

# 로보틱스 역기구학 입문

이 책은 고등학교 수준의 행렬과 삼각함수를 아는 학습자가 **역기구학(Inverse Kinematics, IK)** 을 처음 배우고 휴머노이드 locomotion의 기초로 나아가기 위한 자료다. 1~5단계에서는 관절각과 손·발의 목표 위치·방위를 연결하는 기구학을 익히고, 6단계에서는 CoM과 지면 접촉을 잇는 가장 단순한 동적 균형 모형을 배운다. PID·PD 제어, 모터 명령과 저수준 제어는 다루지 않는다.

## 이 책을 마치면

- 2관절 평면 팔의 손 위치를 관절각에서 계산할 수 있다.
- 목표점이 주어졌을 때 가능한 관절각을 구하고 검산할 수 있다.
- 도달 불가, 복수 해, 특이점을 구별할 수 있다.
- 3D 회전행렬과 강체변환으로 로봇 손·발의 자세를 표현할 수 있다.
- 6R 직렬 팔의 변환 체인과 표준 DH 표에서 순기구학을 구성할 수 있다.
- 자코비안으로 관절의 작은 변화와 말단의 작은 변화를 연결하고 반복 수치 IK를 구성할 수 있다.
- 지지발 접촉을 보존하면서 스윙발·골반·자세 목표를 전신 관절에 분배할 수 있다.
- LIPM에서 필요한 CoP와 캡처 포인트를 계산해 현재 발로 멈출 수 있는지 판단할 수 있다.

## 학습 경로

| 단계 | 학습 대상 | 완료 기준 | 권장 시간 |
|---|---|---|---|
| 1 | [평면 회전과 2관절 IK](./01-planar-kinematics.md) | 도달 조건을 확인하고 IK 공식을 손으로 풀어 FK로 검산한다. | 6–8시간 |
| 2 | [3D 회전과 강체변환](./02-spatial-transformations.md) | 3D 회전행렬과 $4\times4$ 동차변환을 계산한다. | 8–10시간 |
| 3 | [6자유도 매니퓰레이터의 순기구학](./03-six-dof-forward-kinematics.md) | 6R 변환 체인과 표준 DH 표에서 손의 위치·방위를 계산한다. | 10–14시간 |
| 4 | [자코비안과 수치 역기구학](./04-jacobian-numerical-inverse-kinematics.md) | 관절의 작은 변화와 손의 작은 변화를 연결하는 행렬로 오차를 반복해서 줄인다. | 10–14시간 |
| 5 | [휴머노이드 보행을 위한 전신 역기구학](./05-humanoid-whole-body-inverse-kinematics.md) | 지지발 접촉을 보존하며 스윙발·골반 과제를 우선순위에 따라 푼다. | 12–18시간 |
| 6 | [휴머노이드 동적 균형의 기초: LIPM, ZMP와 캡처 포인트](./06-dynamic-balance-lipm-zmp-capture-point.md) | CoM 위치·속도와 지지 구간에서 요구 CoP와 CP를 계산하고 한 발 정지 가능성을 판단한다. | 10–14시간 |

!!! tip "학습 순서"
    1단계의 FK·IK 검산 뒤 2단계의 회전 순서와 좌표계 첨자 규칙을 익히고 3단계로 이동하자. 3단계에서는 이 변환을 관절 수만큼 이어 6R 팔의 FK를 만든다. 4단계에서는 FK의 작은 변화를 자코비안으로 나타내 수치 IK를 반복한다. 5단계에서는 자코비안·영공간을 기구학 트리와 접촉 과제로 확장한다. 6단계에서는 같은 CoM 위치라도 속도에 따라 정지 가능성이 달라짐을 확인하고, 기구학 목표를 동적 locomotion 계획과 연결한다. 각 단계의 Worked Example을 손으로 검산한 뒤 다음 단계로 넘어가는 것을 권장한다.

## 실습 자료

- [FK 놀이터: 관절각을 바꾸어 손 위치 관찰하기](./assets/planar-kinematics/fk-playground.html)
- [IK 연습: 목표점을 찍어 두 해와 특이점 비교하기](./assets/planar-kinematics/ik-practice.html)
- [3D 회전·강체변환 실습: 회전 순서와 좌표계 비교하기](./assets/spatial-transformations/spatial-transform-lab.html)
- [6R 순기구학 실습: 관절별 누적 변환과 TCP 관찰하기](./assets/six-dof-forward-kinematics/forward-kinematics-lab.html)
- [2R 자코비안·수치 IK 실습: 특이점과 반복 경로 비교하기](./assets/jacobian-numerical-inverse-kinematics/numerical-ik-lab.html)
- [휴머노이드 전신 IK 비교 실습: 가중 해와 접촉 우선 해 비교하기](./assets/humanoid-whole-body-inverse-kinematics/whole-body-ik-lab.html)
- [동적 균형 실습: CoM 투영, CoP와 캡처 포인트 비교하기](./assets/dynamic-balance-lipm-zmp-capture-point/dynamic-balance-lab.html)

모든 실습은 외부 라이브러리 없이 동작한다. 각 장의 Worked Example을 푼 뒤, 같은 값을 입력해 수식과 그림이 일치하는지 확인해 보자.
