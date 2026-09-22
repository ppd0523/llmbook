---
title: 휴머노이드 전신 역기구학과 동적 균형
version: 1.0
updated: 2026-08-12
---

# 휴머노이드 전신 역기구학과 동적 균형

이 책은 매니퓰레이터의 수치 역기구학을 익힌 학습자가 휴머노이드 locomotion의 기초로 나아가기 위한 자료다. 지지발 접촉을 보존하면서 여러 자세 과제를 전신 관절에 분배하고, CoM과 지면 접촉을 잇는 가장 단순한 동적 균형 모형을 배운다. 접촉력과 운동방정식을 다루는 동적 locomotion 계획, PID·PD 제어와 저수준 제어는 다루지 않는다.

## 선행지식

[로보틱스 기구학 기초](../robotics-kinematics-foundations/index.md)와 [매니퓰레이터 순기구학과 수치 역기구학](../robotics-manipulator-kinematics/index.md)의 1–4단계를 마쳤다고 가정한다. 특히 자코비안, 의사역행렬, 반복 수치 IK가 여기에 해당한다.

## 이 책을 마치면

- 지지발 접촉을 보존하면서 스윙발·골반·자세 목표를 전신 관절에 분배할 수 있다.
- 과제 우선순위와 영공간을 구별해 해를 구성할 수 있다.
- LIPM에서 필요한 CoP와 캡처 포인트를 계산할 수 있다.
- CoM의 위치와 속도로 현재 발로 멈출 수 있는지 판단할 수 있다.

## 목차

| 단계 | 학습 대상 | 완료 기준 | 권장 시간 |
|---|---|---|---|
| 5 | [휴머노이드 보행을 위한 전신 역기구학](./01-humanoid-whole-body-inverse-kinematics.md) | 지지발 접촉을 보존하며 스윙발·골반 과제를 우선순위에 따라 푼다. | 12–18시간 |
| 6 | [휴머노이드 동적 균형의 기초: LIPM, ZMP와 캡처 포인트](./02-dynamic-balance-lipm-zmp-capture-point.md) | CoM 위치·속도와 지지 구간에서 요구 CoP와 CP를 계산하고 한 발 정지 가능성을 판단한다. | 10–14시간 |

!!! tip "학습 순서"
    5단계에서 자코비안·영공간을 기구학 트리와 접촉 과제로 확장한다. 6단계에서는 같은 CoM 위치라도 속도에 따라 정지 가능성이 달라짐을 확인하고, 기구학 목표를 동적 locomotion 계획과 연결한다.

## 실습 자료

- [휴머노이드 전신 IK 비교 실습: 가중 해와 접촉 우선 해 비교하기](./assets/humanoid-whole-body-inverse-kinematics/whole-body-ik-lab.html)
- [동적 균형 실습: CoM 투영, CoP와 캡처 포인트 비교하기](./assets/dynamic-balance-lipm-zmp-capture-point/dynamic-balance-lab.html)

모든 실습은 외부 라이브러리 없이 동작한다. 각 장의 Worked Example을 푼 뒤, 같은 값을 입력해 수식과 그림이 일치하는지 확인해 보자.

## 세 권으로 이어지는 학습 경로

역기구학 학습자료는 세 권으로 나뉘어 있고 1단계부터 6단계까지 하나의 순서로 이어진다. 본문에서 "3단계"처럼 부르는 번호는 이 여섯 단계를 가리키며, 각 책 안의 챕터 번호와는 별개다.

| 권 | 단계 | 내용 |
|---|---|---|
| [로보틱스 기구학 기초](../robotics-kinematics-foundations/index.md) | 1–2 | 평면 회전과 2관절 IK, 3D 회전과 강체변환 |
| [매니퓰레이터 순기구학과 수치 역기구학](../robotics-manipulator-kinematics/index.md) | 3–4 | 6R 변환 체인과 DH 표, 자코비안과 반복 수치 IK |
| [휴머노이드 전신 역기구학과 동적 균형](../humanoid-balance-and-whole-body-ik/index.md) | 5–6 | 접촉을 보존하는 전신 IK, LIPM·ZMP·캡처 포인트 |
