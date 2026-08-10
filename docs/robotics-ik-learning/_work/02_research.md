---
title: 조사 노트
version: 0.2
status: reviewed
owner: agent
updated: 2026-08-10
target_reader: 고등학교 수준의 행렬·삼각함수를 아는 로보틱스 입문자
topic: 2관절 평면 매니퓰레이터의 역기구학
---

# 조사 노트

## 1. 핵심 출처

| 구분 | 제목/문서 | 링크/서지 | 사용할 내용 | 신뢰도 |
|---|---|---|---|---|
| 교과서·공개 강의 | *Modern Robotics* | Lynch, K. M. & Park, F. C. (2017), [온라인 자료](https://modernrobotics.northwestern.edu/nu-gm-book-resource/foundations-of-robot-motion/) | 회전행렬, 동차변환, FK·IK와 특이점의 표준 용어·맥락 | 높음 |
| 대학 공개강의 | MIT OpenCourseWare, *Introduction to Robotics*, Chapter 4 | [Planar kinematics and inverse kinematics](https://ocw.mit.edu/courses/2-12-introduction-to-robotics-fall-2005/resources/chapter4/) | 직렬 평면 링크 기구와 해석적 IK의 교육적 범위 | 높음 |
| 대학 공개강의 | Caltech ME 115(a,b), *Introduction to Kinematics and Robotics* | [강의 개요와 일정](https://robotics.caltech.edu/wiki/index.php/ME115_2016) | 회전·공간 기구학·직렬 체인·IK·중복성 해결의 학습 순서 | 높음 |
| 전문 학회 교육 자료 | IEEE RAS University, Kinematics | [Kinematics learning material](https://www.ieee-ras.org/ras-university/?ras_page=docs%2Fchap1_basic_motion_ctrl%2Fkinematics) | 2D 좌표 변환과 평면 로봇의 시각적 설명 | 높음 |

## 2. 핵심 정의와 용어 도입

| 용어 | 독자 수준의 한 문장 정의 | 원어/약어 | 본문 표기 | 혼동할 개념 |
|---|---|---|---|---|
| 링크 | 관절과 관절을 잇는 길이가 고정된 막대 부분 | link | 링크 | 관절 자체가 아니다. |
| 관절 | 링크 사이의 상대 회전을 정하는 연결부 | joint | 관절 | 링크 길이와 다르다. |
| 자유도 | 독립적으로 정할 수 있는 관절 변수의 수 | degree of freedom, DOF | 자유도 | 2D 위치 좌표 수와 항상 같지는 않다. |
| 순기구학 | 관절값에서 손의 위치·방향을 계산하는 문제 | forward kinematics, FK | 순기구학(FK) | IK의 역함수가 항상 아니다. |
| 역기구학 | 원하는 손의 위치·방향을 만족하는 관절값을 찾는 문제 | inverse kinematics, IK | 역기구학(IK) | 해가 없거나 여럿일 수 있다. |
| 특이점 | 손의 어떤 순간 이동을 만들기 어려워지는 자세 | singularity | 특이점 | 목표점이 도달 불가한 상태와 다르다. |
| 관절공간 | 관절 변수들을 좌표로 쓰는 공간 | configuration space | 관절공간 | 손이 움직이는 실제 공간이 아니다. |
| 작업공간 | 손이 도달할 수 있는 위치·자세의 집합 | workspace | 작업공간 | 관절공간과 다르다. |
| 자세 | 위치와 방향을 함께 나타낸 값 | pose | 자세 | 이 장의 $(x,y)$ 위치와 다르다. |

## 3. 수식과 알고리즘

| 항목 | 내용 요약 | 가정 | 출처 | 검증 상태 |
|---|---|---|---|---|
| 2D 회전 | $R(\theta)=[[\cos\theta,-\sin\theta],[\sin\theta,\cos\theta]]$ | 원점 중심의 반시계 회전, 열벡터 표기 | Modern Robotics | 검증 완료 |
| 2R FK | $x=l_1\cos\theta_1+l_2\cos(\theta_1+\theta_2)$, $y=l_1\sin\theta_1+l_2\sin(\theta_1+\theta_2)$ | 두 회전관절, 평면, 상대 관절각 $\theta_2$ | MIT OCW, Modern Robotics | 검증 완료 |
| 2R IK | $c_2=(r^2-l_1^2-l_2^2)/(2l_1l_2)$, $\theta_2=\operatorname{atan2}(\pm\sqrt{1-c_2^2},c_2)$ | 링크 길이 양수, 관절 제한 무시 | MIT OCW의 평면 IK 범위와 코사인 법칙 | 검증 완료 |
| 도달 조건 | $|l_1-l_2|\le r\le l_1+l_2$ | 관절이 모든 각을 회전할 수 있음 | 삼각 부등식·코사인 법칙 | 검증 완료 |

## 4. 예제 후보

| 예제 | 보여줄 개념 | 입력 | 기대 결과 | 위험 |
|---|---|---|---|---|
| FK 기본 | 각의 누적 | $l_1=3$, $l_2=2$, $(\theta_1,\theta_2)=(0°,90°)$ | 손 $(3,2)$ | $θ_2$를 절대각으로 오해할 수 있다. |
| IK 두 해 | 팔꿈치 위·아래 | $l_1=3$, $l_2=2$, 목표 $(3,2)$ | $(0°,90°)$와 $(67.38°,-90°)$ | `atan2`가 필요하다. |
| 특이점 | 해의 합침 | 목표 $(5,0)$와 $(1,0)$ | 완전 펴짐·접힘 | 도달 불가로 오해할 수 있다. |

## 5. 주의점과 조사 요약

- 이 자료의 동차변환은 2D 직관을 위한 소개로 한정한다. 3D의 $4\times4$ 행렬과 pose의 6개 자유도는 다음 장에서 다룬다.
- MIT의 로보틱스 입문은 평면·공간 기구학을 함께 다루고, Caltech ME 115은 회전에서 공간 기구학·직렬 체인·IK·중복성 해결로 진행한다. 이에 맞춰 현재 장에는 관절공간·작업공간·자세의 구분과 다음 장의 위치를 추가한다.
- 2R IK 식은 관절 제한과 장애물이 없는 이상화된 기구학 모델의 해다.
- 가장 중요한 검산은 IK 해를 FK 식에 다시 대입하는 것이다.
- 출처 필요 항목 없음. 기구학 이외의 제어·동역학 주장은 최종 원고에서 제외한다.
