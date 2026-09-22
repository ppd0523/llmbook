---
stage: 02_research
chapter: 02-spatial-transformations
status: complete
---

# 2단계 조사 기록

## 참고한 공식 자료

| 자료 | 확인한 내용 | 본문 반영 |
|---|---|---|
| [Modern Robotics Chapter 3](https://modernrobotics.northwestern.edu/chapters/chapter3/) | 오른손 규칙, 오른손 좌표계, 회전행렬의 세 역할, 동차변환의 세 역할 | 회전행렬을 단순 공식이 아니라 자세 표현·좌표 변환·벡터 회전의 도구로 구분 |
| [Modern Robotics 3.3.1](https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-3-1-homogeneous-transformation-matrices/) | `T=[R,p;0,1]`, 좌표계 첨자 소거, 변환의 역과 곱 | `^A T_B ^B T_C = ^A T_C`, 점 변환, 역변환 공식 |
| [MIT OCW 2.007 Lecture 6](https://ocw.mit.edu/courses/2-007-design-and-manufacturing-i-spring-2009/3ad37424e0a9ae4ef3350892aa492ebe_MIT2_007s09_lec06.pdf) | 강체의 회전·이동을 동차행렬과 행렬곱으로 표현 | 1단계의 2D 동차변환을 4×4로 자연스럽게 확장 |
| [MIT OCW 2.12 Lecture Notes](https://ocw.mit.edu/courses/2-12-introduction-to-robotics-fall-2005/pages/lecture-notes/) | 로봇 기구 → 평면 기구학 → 미분 기구학의 교육 순서 | 2단계는 미분 기구학 전에 공간 자세 표현을 확실히 하는 연결 장으로 설계 |
| [Caltech ME115 2016](https://robotics.caltech.edu/wiki/index.php/ME115_2016) | 평면 변위 → 구면 회전 → 공간 기구학 → 매니퓰레이터 FK/IK 순서 | 이 장을 회전과 공간 변환에 한정하고 DH/FK는 3단계로 분리 |
| [Caltech Notes on Rotations](https://robotics.caltech.edu/~jwb/courses/ME115/handouts/rotation.pdf) | 강체 회전이 길이를 보존하므로 `R^T R=I`, 회전은 `det R=+1` | 직교성과 행렬식의 의미를 고등학생 수준으로 설명 |

## 교육 설계 판단

1. 학습자는 내적과 직교를 모를 수 있으므로 회전행렬 성질 전에 짧은 벡터 보충을 둔다.
2. 회전행렬의 세 쓰임을 한꺼번에 섞으면 능동·수동 혼동이 생기므로 먼저 능동 회전, 다음에 좌표계 첨자 표기를 소개한다.
3. 6자유도에서 위치 3개와 방향 3개가 필요하다는 동기를 장 앞부분에 명시한다.
4. Euler angle은 표현 방법 중 하나로만 다루며, `Rz Ry Rx` 순서와 짐벌락을 경고한다.
5. axis-angle, Rodrigues, quaternion은 대학 강의에서 이어지는 주제지만 이 단계의 핵심 질문에 필수적이지 않아 후속 학습으로 미룬다.

## 사실 검증 메모

- 회전행렬은 길이와 각도를 보존하며 `R^T R=I`, `det R=+1`을 만족한다.
- 열벡터 규약에서 행렬곱의 가장 오른쪽 변환이 먼저 적용된다.
- `^A R_B`의 열은 B 좌표계의 세 축을 A 좌표로 표현한 벡터다.
- `^A T_B`는 B 좌표의 점을 A 좌표로 바꾼다.
- 역변환은 `R^-1=R^T`, 이동부는 단순히 `-p`가 아니라 `-R^T p`다.
