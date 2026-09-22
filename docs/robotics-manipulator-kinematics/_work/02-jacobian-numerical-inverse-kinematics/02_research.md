---
stage: 02_research
chapter: 04-jacobian-numerical-inverse-kinematics
status: complete
updated: 2026-08-12
---

# 4단계 조사 기록

## 참고한 핵심 자료

| 자료 | 확인한 내용 | 본문 반영 |
|---|---|---|
| [MIT OCW 2.12 Chapter 5: Differential Motion](https://ocw.mit.edu/courses/2-12-introduction-to-robotics-fall-2005/resources/chapter5/) | 2R FK의 편미분에서 자코비안을 만들고, 열벡터를 각 관절의 단위 속도가 만드는 말단 속도로 해석하는 흐름 | 작은 변화→2R 유도→열벡터 해석→특이 자세 순서 채택 |
| [MIT OCW 2.12 Chapter 5 PDF](https://ocw.mit.edu/courses/2-12-introduction-to-robotics-fall-2005/d6edf8a76e7674076c6fd5c09dedbed3_chapter5.pdf) | 2R에서 $\det J=0$인 완전 신장·접힘 자세, 특이점 근처 역자코비안의 큰 관절속도 | 행렬식과 열 방향을 함께 해석하고 큰 업데이트 위험을 설명 |
| [Caltech ME115 2016](https://robotics.caltech.edu/wiki/index.php/ME115_2016) | DH·FK·IK 뒤에 매니퓰레이터 자코비안·특이점·여유 기구·의사역행렬을 배치하는 강의 순서 | 3단계 FK 다음에 자코비안과 수치 IK, 마지막에 전신 IK 연결 배치 |
| [Caltech: The Moore–Penrose Pseudo Inverse](https://www.robotics.caltech.edu/~jwb/courses/ME115/handouts/pseudo.pdf) | 직사각 행렬에서 최소제곱 해와 여유 기구의 최소 크기 해, 영공간 해석 | 역행렬·의사역행렬·여유 자유도 설명에 반영 |
| [Caltech: The Damped Pseudo Inverse](https://robotics.caltech.edu/~jwb/courses/ME115/handouts/damped.pdf) | $J^T(JJ^T+\lambda^2I)^{-1}$ 형태와 오차·관절변화 크기의 절충, 특이점 근처 업데이트 제한 | DLS 목적함수·공식·감쇠의 장단점에 반영 |
| [Modern Robotics Chapter 5](https://modernrobotics.northwestern.edu/nu-gm-book-resource/velocity-kinematics-and-statics/) | 자코비안이 관절속도를 말단속도로 매핑하며, $6\times n$ 자코비안과 특이점·조작성으로 확장되는 구성 | 2R 위치 자코비안에서 3D 기하 자코비안으로 확장 |
| [Modern Robotics Chapter 6](https://modernrobotics.northwestern.edu/chapters/chapter6/) | Newton–Raphson 반복으로 변환행렬 목표의 수치 IK를 푸는 관점 | FK→오차→자코비안→관절 업데이트의 반복 구조에 반영 |
| [Wampler (1986)](https://doi.org/10.1109/TSMC.1986.289285) | 특이점 근처에서 해의 크기와 잔차를 절충하는 damped least-squares IK | DLS의 원 논문 근거와 적용 한계 기록 |

## 교육 설계 판단

1. 독자가 미분을 모른다고 가정하므로 순간속도 기호부터 시작하지 않고, 작은 유한 변화와 그래프의 기울기를 먼저 설명한다.
2. 1단계의 2R FK를 다시 사용하면 새 수학이 기존 지식에서 어떻게 나오는지 직접 확인할 수 있다.
3. 자코비안 한 열의 의미를 수식과 그림에서 동시에 보여주면 편미분 표를 기호 암기로 오해하는 일을 줄일 수 있다.
4. 역행렬은 2R Worked Example에서만 사용하고, 실제 6R·휴머노이드로 확장하기 위해 의사역행렬과 DLS를 구분한다.
5. SVD는 의사역행렬을 안정적으로 계산하는 도구로 이름만 안내하고 계산은 후속 심화로 넘긴다.
6. 3D 자세 오차는 위치와 방위를 분리해 설명한다. 회전행렬 열의 외적으로 만든 국소 방위 오차를 사용하되 180° 근처 한계를 명시한다.
7. 본문과 실습의 반복 업데이트는 수치 해법이며 모터 제어나 PID·PD 제어가 아님을 명시한다.
8. 휴머노이드 연결에서는 지지발·스윙발·골반 자세를 예로 들고, 우선순위 전신 IK 자체는 5단계로 넘긴다.

## 사실·수식 검증 메모

- 평면 2R 위치 자코비안은 FK의 각 성분을 $q_1,q_2$로 편미분해 얻는다.
- 각도에 대한 미분과 수치 유한차분은 라디안을 기준으로 해야 본문의 자코비안과 단위가 일치한다.
- 작은 변화에서는 $\Delta\mathbf p\approx J(\mathbf q)\Delta\mathbf q$이고, 속도 관계는 $\dot{\mathbf p}=J(\mathbf q)\dot{\mathbf q}$다.
- 2R 위치 자코비안의 행렬식은 $l_1l_2\sin q_2$이므로 $q_2=0,\pi$에서 특이하다.
- 회전관절의 3D 기하 자코비안 열은 $[\hat{\mathbf s}_i\times(\mathbf p_e-\mathbf p_i);\hat{\mathbf s}_i]$, 직동관절은 $[\hat{\mathbf s}_i;\mathbf0]$다. 모든 벡터는 같은 기준 좌표계로 표현해야 한다.
- 이 자료의 6차원 순서는 선속도 위, 각속도 아래인 $[\mathbf v;\boldsymbol\omega]$로 고정한다. 교재에 따라 반대 순서를 사용하므로 공식을 섞지 않는다.
- Moore–Penrose 의사역행렬은 직사각 행렬에도 정의되며, 일관되지 않은 식에서는 최소제곱 잔차, 해가 여러 개면 최소 2-노름 해를 고른다.
- DLS 업데이트는 $\Delta\mathbf q=\eta J^T(JJ^T+\lambda^2I)^{-1}\mathbf e$로 두며, $\lambda>0$은 특이점 근처 큰 관절 변화를 누르는 대신 정확도를 일부 희생한다.
- 위치와 방위 오차는 단위가 다르므로 6D 오차를 결합할 때 가중치 또는 특성 길이가 필요하다.
- 영공간 성분 $\Delta\mathbf q_N$은 $J\Delta\mathbf q_N=\mathbf0$이므로 현재 과제를 1차 근사에서 바꾸지 않는다.

## 출처 적용 범위

- MIT의 2R 유도와 열벡터 해석을 입문 흐름의 기준으로 삼는다.
- Caltech의 자코비안→특이점→의사역행렬→감쇠 의사역행렬 순서를 6R·여유 기구 연결에 사용한다.
- Modern Robotics의 twist·공간/몸체 자코비안 전체 형식은 선수 지식 범위를 넘으므로, 이 장에서는 같은 기준 좌표계의 기하 자코비안으로 제한한다.
- DLS는 수치 IK의 안정화 방법으로 다루며, 실시간 제어나 추종 성능을 주장하지 않는다.
