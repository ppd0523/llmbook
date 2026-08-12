---
title: 출판 전 최종 Markdown 원고
version: 1.1
status: final
owner: agent
updated: 2026-08-12
target_reader: 고등학교 수준의 행렬·삼각함수를 알고 1~3단계를 마친 로보틱스 입문자
topic: 자코비안과 수치 역기구학
---

# 자코비안과 수치 역기구학

3단계에서는 관절벡터 $\mathbf q$를 순기구학에 넣어 말단 자세를 계산했다.

$$
\mathbf x=f(\mathbf q)
$$

2R 팔처럼 구조가 단순하면 이 식을 삼각함수로 직접 풀어 IK 해를 구할 수 있다. 그러나 관절과 목표 조건이 많아지면 모든 해를 한 번에 나타내는 식을 만들기 어렵다. 대신 현재 자세에서 관절을 **조금** 바꾸었을 때 말단이 어느 방향으로 얼마나 움직이는지 계산하고, 목표 오차를 줄이는 방향으로 관절을 반복해서 고칠 수 있다.

이때 관절의 작은 변화와 말단의 작은 변화를 연결하는 행렬이 **자코비안 행렬(Jacobian matrix)** 이다. 이 장의 중심 질문은 다음과 같다.

> 현재 자세의 자코비안으로 목표까지의 작은 관절 업데이트를 구하고, 이를 반복해 수치 역기구학을 푸는 방법을 어떻게 구성하고 검산하는가?

이 장의 반복 계산은 기구학 문제를 푸는 수치 알고리즘이다. 모터를 움직이는 PID·PD 제어나 힘·토크를 계산하는 동역학은 다루지 않는다.

## 학습 목표

이 장을 마치면 다음을 할 수 있다.

- 변화량, 변화율과 편미분을 2R 순기구학의 기울기와 연결한다.
- 2R 위치 자코비안을 유도하고 $\Delta\mathbf p\approx J\Delta\mathbf q$를 계산한다.
- 자코비안의 각 열을 한 관절만 움직였을 때의 말단 운동으로 해석한다.
- 유한차분으로 해석적으로 구한 자코비안을 검산한다.
- 자코비안 열의 독립성과 매니퓰레이터 특이 자세의 관계를 설명한다.
- 역행렬, Moore–Penrose 의사역행렬과 감쇠 최소제곱의 역할을 구별한다.
- 감쇠 최소제곱을 사용한 수치 IK의 반복 절차와 종료 조건을 구성한다.
- 회전관절과 직동관절의 3D 기하 자코비안 열을 읽는다.
- 위치·방위 오차의 좌표계와 단위를 일치시켜야 하는 이유를 설명한다.
- 여유 자유도와 영공간이 휴머노이드 전신 IK에 필요한 이유를 설명한다.

## 학습 전 확인

이 장은 [1단계: 평면 회전과 2관절 IK](./01-planar-kinematics.md), [2단계: 3D 회전과 강체변환](./02-spatial-transformations.md), [3단계: 6자유도 매니퓰레이터의 순기구학](./03-six-dof-forward-kinematics.md)을 마쳤다고 가정한다. 특히 다음 내용을 다시 확인하자.

- 2R 팔의 끝점은 $x=l_1\cos q_1+l_2\cos(q_1+q_2)$, $y=l_1\sin q_1+l_2\sin(q_1+q_2)$다.
- 관절벡터 $\mathbf q$를 FK에 넣으면 현재 말단 위치와 방위가 하나로 정해진다.
- 회전행렬의 세 열은 말단 좌표계의 x·y·z축을 기준 좌표계에서 나타낸 단위벡터다.
- 같은 기하 관계라도 어느 좌표계에서 표현했는지에 따라 벡터의 숫자가 달라진다.

미분, 편미분, 벡터 외적과 의사역행렬은 처음부터 설명한다.

!!! note "이 장의 계산 규약"
    모든 벡터는 열벡터다. 관절각의 작은 변화와 미분은 **라디안**을 사용한다. $\mathbf p$는 위치, $\mathbf x$는 위치 또는 자세를 모은 일반적인 과제벡터, $\mathbf e$는 목표 오차다. 3D 기하 자코비안은 위쪽에 선속도 $\mathbf v$, 아래쪽에 회전축 방향과 초당 회전량을 나타내는 각속도 $\boldsymbol\omega$를 놓는 $[\mathbf v;\boldsymbol\omega]$ 순서를 사용한다. 다른 교재가 $[\boldsymbol\omega;\mathbf v]$ 순서를 사용하면 행 순서도 함께 바꿔야 한다.

## 1. FK를 한 번 뒤집는 대신 여러 번 고치기

현재 반복 번호를 $k$, 현재 관절벡터를 $\mathbf q_k$, 목표 과제벡터를 $\mathbf x_d$라고 하자. FK로 현재 결과를 계산하면 목표 오차는 다음과 같다.

$$
\mathbf e_k=\mathbf x_d-f(\mathbf q_k)
$$

이 단순한 뺄셈은 위치처럼 같은 좌표계의 수를 직접 비교하는 과제에 알맞다. 방위는 회전행렬의 성분을 그대로 빼지 않고, 13절에서 정의할 회전 오차 벡터를 사용해야 한다.

수치 IK는 다음 순환을 반복한다.

```text
현재 관절값 → FK → 목표 오차 → 작은 관절 업데이트 → 새 관절값
```

핵심은 오차 $\mathbf e_k$를 줄일 관절 변화 $\Delta\mathbf q_k$를 구하는 일이다. FK는 삼각함수를 포함하므로 전체 구간에서는 곡선이지만, 현재 자세 주변의 아주 작은 구간에서는 직선처럼 근사할 수 있다. 이를 **국소 선형 근사(local linear approximation)** 라고 한다.

$$
f(\mathbf q_k+\Delta\mathbf q_k)
\approx f(\mathbf q_k)+J(\mathbf q_k)\Delta\mathbf q_k
$$

따라서 다음 관계를 거꾸로 풀면 목표 방향의 작은 관절 업데이트를 얻을 수 있다.

$$
\mathbf e_k\approx J(\mathbf q_k)\Delta\mathbf q_k
$$

한 번의 근사는 보통 정확한 IK 해가 아니다. 업데이트한 자세에서 FK와 자코비안을 다시 계산해야 한다. 수치 IK가 **반복적(iterative)** 인 이유다.

## 2. 작은 변화를 읽는 데 필요한 수학

### 2.1 변화량과 벡터의 크기

어떤 값이 이전의 $a$에서 새로운 $a'$로 바뀌었다면 변화량은 $\Delta a=a'-a$다. 관절이 여러 개면 변화량을 한 열에 모은다.

$$
\Delta\mathbf q=
\begin{bmatrix}
\Delta q_1&\Delta q_2&\cdots&\Delta q_n
\end{bmatrix}^T
$$

벡터 $\mathbf u=[u_1,\ldots,u_n]^T$의 크기는 **2-노름(2-norm)** 으로 나타낸다.

$$
\|\mathbf u\|_2=\sqrt{u_1^2+\cdots+u_n^2}
$$

이 장에서는 아래첨자 2를 생략해 $\|\mathbf u\|$로도 쓴다. 수치 IK에서는 $\|\mathbf e\|$로 목표와의 거리, $\|\Delta\mathbf q\|$로 한 번에 바꾸는 관절량을 확인한다.

### 2.2 기울기와 미분

입력 $a$가 조금 변할 때 출력 $g(a)$가 얼마나 변하는지 나타내는 비율은 다음과 같다.

$$
\frac{\Delta g}{\Delta a}
=\frac{g(a+\Delta a)-g(a)}{\Delta a}
$$

$\Delta a$를 매우 작게 줄였을 때 이 비율이 가까워지는 값을 $g'(a)$ 또는 $dg/da$라고 쓰며 **미분값(derivative)** 이라고 부른다. 그래프에서는 현재 점에서 곡선에 접하는 직선의 기울기다.

삼각함수를 미분할 때 각도는 라디안이어야 다음 식이 성립한다.

$$
\frac{d}{dq}\sin q=\cos q,
\qquad
\frac{d}{dq}\cos q=-\sin q
$$

도(degree)를 그대로 사용하면 1°가 $\pi/180$ rad이므로 기울기에 추가 배율이 생긴다. 화면에는 도를 표시하더라도 자코비안 계산 내부에서는 라디안을 사용해야 한다.

### 2.3 다른 입력을 고정한 편미분

출력이 $g(q_1,q_2)$처럼 입력 여러 개에 의존할 때, $q_2$를 고정하고 $q_1$만 바꾼 기울기를 다음처럼 쓴다.

$$
\frac{\partial g}{\partial q_1}
$$

이를 **편미분(partial derivative)** 이라고 한다. $\partial g/\partial q_i$는 “다른 관절은 현재 값에 고정하고 관절 $i$만 아주 조금 움직였을 때 출력 $g$가 변하는 비율”이다.

함수 안에 또 함수가 들어 있으면 바깥 변화율과 안쪽 변화율을 곱한다. 이를 **연쇄법칙(chain rule)** 이라고 한다. 예를 들어 $u=q_1+q_2$로 두면 $\partial u/\partial q_1=\partial u/\partial q_2=1$이므로

$$
\frac{\partial}{\partial q_1}\sin(q_1+q_2)
=\cos(q_1+q_2)\cdot1
$$

이다. 반면 $\sin(2q)$에서는 안쪽 $2q$의 변화율이 2이므로 $d\sin(2q)/dq=2\cos(2q)$가 된다. 이 차이를 기억하면 4절의 2R 미분을 따라갈 수 있다.

길이 $l$인 1R 링크의 끝점이

$$
\mathbf p(q)=
\begin{bmatrix}
l\cos q\\l\sin q
\end{bmatrix}
$$

라면 각도에 대한 변화율은 다음과 같다.

$$
\frac{d\mathbf p}{dq}=
\begin{bmatrix}
-l\sin q\\l\cos q
\end{bmatrix}
$$

$q=0$에서는 $[0,l]^T$다. 링크가 +x축을 향할 때 양의 각도로 조금 돌리면 끝점은 거의 +y 방향으로 움직인다는 그림과 일치한다.

### 2.4 점 표기는 시간당 변화량이다

$\dot q=dq/dt$는 1초당 관절값이 얼마나 바뀌는지 나타낸다. 회전관절이면 rad/s, 직동관절이면 m/s 같은 단위를 가진다. 위치의 시간당 변화 $\dot{\mathbf p}$는 선속도다.

이 장은 속도 명령을 제어하는 방법을 다루지 않는다. 점 표기는 자코비안의 기구학적 의미를 설명하는 데만 사용한다.

## 3. 자코비안은 여러 기울기를 모은 행렬이다

$n$개의 관절값에서 $m$개의 과제값을 계산한다고 하자.

$$
\mathbf x=f(\mathbf q),
\qquad
\mathbf q\in\mathbb R^n,
\quad
\mathbf x\in\mathbb R^m
$$

$\mathbb R^n$은 실수 $n$개를 한 열에 모은 벡터들의 집합을 뜻한다.

**자코비안 행렬(Jacobian matrix)** 은 출력 각각을 입력 각각으로 편미분한 값을 한 표에 모은 $m\times n$ 행렬이다.

$$
J(\mathbf q)=
\begin{bmatrix}
\dfrac{\partial x_1}{\partial q_1}&\cdots&\dfrac{\partial x_1}{\partial q_n}\\
\vdots&\ddots&\vdots\\
\dfrac{\partial x_m}{\partial q_1}&\cdots&\dfrac{\partial x_m}{\partial q_n}
\end{bmatrix}
$$

자코비안은 로봇 이름만으로 하나가 정해지는 행렬이 아니다. 어떤 출력 $\mathbf x$를 과제로 골랐는지, 어느 도구점을 관찰하는지, 벡터를 어느 좌표계로 표현하는지까지 정해야 한다. 같은 2R 팔도 TCP 위치 $[x,y]^T$를 과제로 삼으면 $2\times2$지만, 평면 방위 $\phi=q_1+q_2$까지 넣은 $[x,y,\phi]^T$를 과제로 삼으면 셋째 행 $[1,1]$이 추가된 $3\times2$ 자코비안이 된다.

현재 자세 주변의 작은 변화 관계는 다음과 같다.

$$
\Delta\mathbf x\approx J(\mathbf q)\Delta\mathbf q
$$

시간으로 나누면 속도 관계가 된다.

$$
\dot{\mathbf x}=J(\mathbf q)\dot{\mathbf q}
$$

자코비안의 $i$번째 열 $\mathbf J_i$만 따로 보면 의미가 더 분명하다.

$$
J\Delta\mathbf q
=\mathbf J_1\Delta q_1+\cdots+\mathbf J_n\Delta q_n
$$

$\mathbf J_i$는 다른 모든 관절을 멈추고 관절 $i$만 양의 방향으로 단위 속도로 움직였을 때의 말단 속도다. 실제 말단 움직임은 이 열벡터들을 관절 변화량만큼 확대하거나 축소해 더한 결과다.

!!! warning "자코비안은 현재 자세 주변의 지도다"
    $J(\mathbf q)$는 $\mathbf q$가 달라지면 함께 달라진다. 현재 자세에서 구한 자코비안을 큰 관절 변화에 그대로 적용하면 오차가 커진다. 수치 IK에서는 작은 업데이트 뒤에 FK와 자코비안을 다시 계산한다.

## 4. 2R 위치 자코비안을 직접 유도하기

1단계의 평면 2R FK를 다시 쓰자.

$$
x=l_1\cos q_1+l_2\cos(q_1+q_2)
$$

$$
y=l_1\sin q_1+l_2\sin(q_1+q_2)
$$

과제벡터를 끝점 위치 $\mathbf p=[x,y]^T$로 정하면 입력 2개, 출력 2개이므로 자코비안은 $2\times2$다.

먼저 $x$를 두 관절각으로 편미분한다.

$$
\frac{\partial x}{\partial q_1}
=-l_1\sin q_1-l_2\sin(q_1+q_2)
$$

$$
\frac{\partial x}{\partial q_2}
=-l_2\sin(q_1+q_2)
$$

$y$도 같은 방법으로 편미분한다.

$$
\frac{\partial y}{\partial q_1}
=l_1\cos q_1+l_2\cos(q_1+q_2)
$$

$$
\frac{\partial y}{\partial q_2}
=l_2\cos(q_1+q_2)
$$

네 값을 행렬에 놓으면 2R 위치 자코비안을 얻는다.

$$
J(\mathbf q)=
\begin{bmatrix}
-l_1\sin q_1-l_2\sin(q_1+q_2)&-l_2\sin(q_1+q_2)\\
l_1\cos q_1+l_2\cos(q_1+q_2)&l_2\cos(q_1+q_2)
\end{bmatrix}
$$

행과 열을 다음처럼 읽는다.

- 첫째 행: 관절 변화가 x 위치를 바꾸는 비율
- 둘째 행: 관절 변화가 y 위치를 바꾸는 비율
- 첫째 열: $q_1$만 움직였을 때의 끝점 이동 방향
- 둘째 열: $q_2$만 움직였을 때의 끝점 이동 방향

링크 길이가 m, 관절 변화가 rad이면 각 성분의 단위는 m/rad이다. 라디안은 비율을 나타내는 무차원량으로 취급하기도 하지만, 어떤 입력에 대한 변화율인지 확인하려면 m/rad처럼 적는 편이 안전하다.

## 5. 자코비안 한 열을 유한차분으로 검산하기

편미분 식을 잘못 유도했거나 프로그램에서 관절축을 잘못 사용해도 최종 행렬만 보면 찾기 어렵다. 이때 **유한차분(finite difference)** 으로 한 열씩 검사할 수 있다.

$\mathbf b_i$를 $i$번째 성분만 1이고 나머지는 0인 선택 벡터라고 하자. 작은 라디안 값 $\varepsilon$을 사용한 중앙차분은 다음과 같다.

$$
\mathbf J_i
\approx
\frac{
\mathbf p(\mathbf q+\varepsilon\mathbf b_i)
-\mathbf p(\mathbf q-\varepsilon\mathbf b_i)
}{2\varepsilon}
$$

검산 순서는 다음과 같다.

1. 현재 $\mathbf q$에서 해석 자코비안 $J$를 계산한다.
2. 관절 $i$만 $+\varepsilon$와 $-\varepsilon$만큼 바꾸어 FK 위치 두 개를 계산한다.
3. 중앙차분 결과를 $J$의 $i$번째 열과 비교한다.
4. 모든 관절에 대해 반복한다.

$\varepsilon$이 너무 크면 곡선을 직선으로 보는 근사 오차가 커진다. 너무 작으면 컴퓨터가 매우 가까운 두 수를 뺄 때 반올림 오차가 커질 수 있다. 이 장의 2R 예제에서는 $\varepsilon=10^{-4}$ rad부터 시작하면 충분하다.

유한차분은 해석식을 몰라도 자코비안을 근사할 수 있지만, 관절마다 FK를 여러 번 계산해야 하고 $\varepsilon$ 선택에 영향을 받는다. 해석 자코비안과 유한차분을 서로 검산하는 용도로 사용하면 좋다.

## 6. 특이 자세에서는 가능한 순간 방향이 줄어든다

자코비안의 열들이 서로 다른 방향을 가리키면 이들을 조합해 여러 말단 운동을 만들 수 있다. 반대로 열들이 나란해지거나 어떤 열이 0이 되면 만들 수 있는 독립 방향의 수가 줄어든다.

행렬의 행이나 열에서 서로 독립인 방향의 최대 개수를 **랭크(rank)** 라고 한다. 2차원 위치 과제를 자유롭게 움직이려면 2R 위치 자코비안의 랭크가 2여야 한다. 랭크가 1이면 현재 순간에는 한 방향의 운동만 만들 수 있다.

$2\times2$ 행렬에서는 행렬식으로 이 변화를 확인할 수 있다. 2R 위치 자코비안의 행렬식을 정리하면 다음과 같다.

$$
\det J=l_1l_2\sin q_2
$$

$q_2=0°$이면 두 링크가 같은 방향으로 완전히 펴지고, $q_2=180°$이면 반대 방향으로 접힌다. 두 경우 모두 $\sin q_2=0$이므로 $\det J=0$이다.

예를 들어 $l_1=l_2=1$, $q_1=q_2=0°$이면

$$
J=
\begin{bmatrix}
0&0\\
2&1
\end{bmatrix}
$$

두 열 모두 y축 방향이다. 관절을 순간적으로 움직여 y 방향 속도는 만들 수 있지만 x 방향 속도는 1차 근사에서 만들 수 없다. 이런 자세를 **기구학적 특이 자세(kinematic singular configuration)** 라고 한다.

특이 자세 근처에서는 두 열이 거의 나란하다. 만들기 어려운 방향의 작은 말단 운동을 요구하면 매우 큰 관절 변화가 계산될 수 있다. 이것이 역자코비안만 사용한 IK가 특이점 근처에서 불안정해지는 이유다.

!!! note "유한한 움직임과 순간 움직임은 다르다"
    완전히 편 팔을 조금 굽히면 끝점의 x 위치도 변한다. 그러나 정확히 편 순간의 첫 번째 변화는 주로 접선 방향이고, x 변화는 각도 변화의 제곱처럼 더 빠르게 작아지는 고차 효과로 나타난다. 자코비안은 현재 점의 1차 근사만 표현한다.

2단계의 RPY 짐벌락은 방위 **표현**의 특이점이다. 여기의 매니퓰레이터 특이점은 실제 관절 운동이 만들 수 있는 말단 순간 방향이 줄어드는 기구의 특성이다.

## 7. 국소 관계를 거꾸로 푸는 세 가지 방법

목표 오차 $\mathbf e$에 대해 다음 식을 만족하는 작은 관절 변화를 찾고 싶다.

$$
J\Delta\mathbf q\approx\mathbf e
$$

### 7.1 정사각 역행렬

$J$가 정사각행렬이고 $\det J\ne0$이면 다음처럼 풀 수 있다.

$$
\Delta\mathbf q=J^{-1}\mathbf e
$$

$2\times2$ 행렬의 역행렬은 다음과 같다.

$$
\begin{bmatrix}a&b\\c&d\end{bmatrix}^{-1}
=\frac{1}{ad-bc}
\begin{bmatrix}d&-b\\-c&a\end{bmatrix}
$$

하지만 관절 수와 과제 수가 다르면 $J$는 정사각형이 아니다. 정사각형이어도 특이 자세에서는 역행렬이 존재하지 않고, 특이점 근처에서는 값이 지나치게 커질 수 있다.

### 7.2 자코비안 전치 방법

가장 단순한 반복 방향은 **자코비안 전치 방법(Jacobian transpose method)** 을 사용하는 것이다.

$$
\Delta\mathbf q=\eta J^T\mathbf e
$$

$\eta>0$는 한 번의 이동 크기를 조절하는 **스텝 크기(step size)** 다. $J^T\mathbf e$는 오차 제곱을 줄이는 쪽의 관절 방향을 제공하지만, $J$의 역행렬은 아니다. $\eta$가 너무 크면 목표를 지나치며 진동하고, 너무 작으면 반복이 느리다. 위치 단위나 링크 길이가 달라지면 적절한 $\eta$도 달라진다.

### 7.3 Moore–Penrose 의사역행렬

정사각형이 아닌 행렬에도 역행렬과 비슷한 역할을 하도록 정의한 행렬을 **Moore–Penrose 의사역행렬(Moore–Penrose pseudoinverse)** 이라고 하며 $J^+$로 쓴다.

$$
\Delta\mathbf q=J^+\mathbf e
$$

의사역행렬은 $\|J\Delta\mathbf q-\mathbf e\|$를 가장 작게 만드는 최소제곱 해를 고르고, 그런 해가 여러 개면 그중 $\|\Delta\mathbf q\|$가 가장 작은 것을 고른다. 따라서 다음처럼 해석할 수 있다.

- 요구 조건이 관절변수보다 많아 오차를 정확히 0으로 만들 수 없으면 $\|J\Delta\mathbf q-\mathbf e\|$가 가장 작은 **최소제곱(least-squares)** 해를 고른다.
- 관절변수가 더 많아 해가 여러 개면 $\|\Delta\mathbf q\|$가 가장 작은 해를 고른다.
- $J$가 정사각이고 비특이면 $J^+=J^{-1}$이다.

실제 소프트웨어는 보통 **특이값 분해(Singular Value Decomposition, SVD)** 로 의사역행렬을 계산한다. SVD에서 나오는 **특이값(singular value)** 은 행렬이 서로 독립인 각 방향을 얼마나 늘리거나 줄이는지 나타내는 0 이상의 수다. SVD 계산 자체는 이 장의 범위가 아니다. 중요한 점은 특이값이 매우 작으면 그 역수가 커져 특이점 근처에서 큰 관절 업데이트가 생길 수 있다는 사실이다.

## 8. 감쇠 최소제곱은 큰 업데이트를 억제한다

**감쇠 최소제곱(Damped Least Squares, DLS)** 은 목표 오차를 줄이는 일과 관절 업데이트를 작게 유지하는 일을 함께 고려한다. 다음 값을 최소로 만드는 $\Delta\mathbf q$를 찾는다.

$$
\|J\Delta\mathbf q-\mathbf e\|^2
+\lambda^2\|\Delta\mathbf q\|^2
$$

첫 항은 선형화된 말단 오차이고, 둘째 항은 관절 업데이트의 크기다. $\lambda>0$는 **감쇠값(damping factor)** 이다. 해는 다음과 같이 쓸 수 있다.

$$
J_\lambda^{\#}
=J^T\left(JJ^T+\lambda^2I_m\right)^{-1}
$$

$$
\Delta\mathbf q
=\eta J_\lambda^{\#}\mathbf e
$$

$I_m$은 과제 차원 $m$에 맞는 단위행렬이다. $\lambda>0$이면 $JJ^T+\lambda^2I_m$에 양의 값이 대각선으로 더해져 특이 자세에서도 역행렬을 계산할 수 있다.

- $\lambda$가 작으면 의사역행렬에 가까워져 빠르고 정확하지만 특이점 영향이 커진다.
- $\lambda$가 크면 관절 업데이트가 작고 부드러워지지만 목표에 느리게 접근하거나 잔차가 더 남는다.
- 모든 로봇과 단위에 맞는 하나의 $\lambda$는 없다. 과제 성분의 숫자 크기를 비교할 수 있게 맞춘 뒤 실험해야 한다.

회전관절과 직동관절이 섞이면 $\|\Delta\mathbf q\|$ 안에도 rad와 m가 함께 들어간다. 이 경우 관절 변화에도 스케일을 적용해야 한다. 이 장의 2R 실습과 6R 예시는 회전관절만 사용한다.

DLS도 도달 불가능한 목표를 도달 가능하게 만들지는 않는다. 계산이 폭주하는 것을 줄여 줄 뿐이다. 한 번의 업데이트가 너무 크면 다음처럼 최대 크기 $\Delta q_{max}$로 제한한다.

$$
\Delta\mathbf q\leftarrow
\Delta\mathbf q\,
\min\left(1,\frac{\Delta q_{max}}{\|\Delta\mathbf q\|}\right)
$$

## 9. Worked Example 1: 정상 자세에서 한 번 업데이트

$l_1=l_2=1$인 2R 팔을 다음 자세에 두자.

$$
\mathbf q=
\begin{bmatrix}0°\\90°\end{bmatrix}
=
\begin{bmatrix}0\\\pi/2\end{bmatrix}\text{ rad}
$$

현재 위치는 $(1,1)$이고 목표 위치는 $(0.9,1.1)$이다.

$$
\mathbf e=
\begin{bmatrix}0.9\\1.1\end{bmatrix}
-
\begin{bmatrix}1\\1\end{bmatrix}
=
\begin{bmatrix}-0.1\\0.1\end{bmatrix}
$$

현재 자세의 자코비안은 다음과 같다.

$$
J=
\begin{bmatrix}
-1&-1\\
1&0
\end{bmatrix},
\qquad
\det J=1
$$

비특이 정사각행렬이므로 이번 한 단계는 역행렬로 풀어 보자.

$$
J^{-1}=
\begin{bmatrix}
0&1\\
-1&-1
\end{bmatrix}
$$

$$
\Delta\mathbf q
=J^{-1}\mathbf e
=
\begin{bmatrix}
0.1\\0
\end{bmatrix}\text{ rad}
$$

$q_1$을 약 $5.73°$ 늘리고 $q_2$는 그대로 둔다는 뜻이다. 선형 근사에서는 정확히 목표 변화 $[-0.1,0.1]^T$를 만든다.

그러나 실제 FK에 새 관절값을 넣으면 위치는 약 $(0.8952,1.0948)$이다. 목표까지 약 $0.0071$이 남는다. 자코비안이 현재 점의 접선 근사이기 때문이다. 새 자세에서 자코비안을 다시 계산해 한 번 더 업데이트하면 오차를 더 줄일 수 있다.

## 10. Worked Example 2: 특이 자세에서 DLS 한 단계

같은 팔을 완전히 편 $\mathbf q=[0°,0°]^T$에 두면 현재 위치는 $(2,0)$이고 자코비안은 다음과 같다.

$$
J=
\begin{bmatrix}
0&0\\
2&1
\end{bmatrix}
$$

작업공간 안의 목표 $(1.99,0.1)$을 두면 $\mathbf e=[-0.01,0.1]^T$다. $\lambda=0.1$, $\eta=1$인 DLS를 사용하자. 현재 $J$의 첫째 행이 0이므로 첫 업데이트는 x 오차에 반응하지 못한다.

$$
JJ^T+\lambda^2I
=
\begin{bmatrix}
0.01&0\\
0&5.01
\end{bmatrix}
$$

$$
\Delta\mathbf q
=J^T(JJ^T+\lambda^2I)^{-1}\mathbf e
\approx
\begin{bmatrix}
0.03992\\0.01996
\end{bmatrix}\text{ rad}
$$

역행렬 $J^{-1}$은 존재하지 않지만 DLS는 유한한 업데이트를 만든다. 선형 예측은 약 $(0,0.0998)$의 위치 변화를 만들고, 실제 FK의 새 위치는 약 $(1.9974,0.0998)$이다. 목표까지 약 $0.0074$가 남는다. 팔이 조금 굽혀진 새 자세에서는 x 방향도 1차 근사로 움직일 수 있으므로 다음 반복에서 다시 보정한다.

반면 목표가 작업공간 바깥인 $(2.1,0)$이라면 DLS가 숫자를 계산할 수는 있어도 링크 길이의 합보다 먼 점에는 도달하지 못한다. 반복 횟수와 정체 조건을 반드시 함께 확인해야 한다.

## 11. 수치 IK 반복 알고리즘

DLS를 사용하는 위치 IK의 기본 절차는 다음과 같다.

```text
입력: 초기 관절값 q, 목표 x_d, 감쇠값 λ, 스텝 크기 η

반복:
  1. 현재 결과 x = FK(q)를 계산한다.
  2. 오차 e = x_d - x를 계산한다.
  3. 오차가 허용값보다 작으면 성공으로 종료한다.
  4. 현재 자코비안 J(q)를 계산한다.
  5. Δq = η Jᵀ(JJᵀ + λ²I)⁻¹e를 계산한다.
  6. Δq가 너무 크면 최대 스텝으로 제한한다.
  7. q ← q + Δq로 갱신하고 관절 제한을 적용한다.
  8. 최대 반복, 정체 또는 수치 오류가 생기면 실패 이유와 함께 종료한다.
```

종료 상태는 최소한 다음처럼 구분해야 한다.

| 상태 | 판정 예 | 의미 |
|---|---|---|
| 수렴 | $\|\mathbf e\|<\varepsilon_e$ | 목표 허용 오차 안에 들어왔다. |
| 최대 반복 | $k=k_{max}$ | 더 많은 반복이 필요하거나 설정·목표에 문제가 있다. |
| 정체 | $\|\Delta\mathbf q\|<\varepsilon_q$인데 오차가 큼 | 특이점, 관절 제한, 도달 불가 또는 나쁜 초기값일 수 있다. |
| 관절 제한 | 제한 적용이 반복되고 오차가 줄지 않음 | 제한하지 않았을 때의 목표 방향이 허용 범위 밖으로 막혀 있다. |
| 수치 오류 | 숫자가 아님(NaN, Not a Number), 무한대, 행렬 계산 실패 | 단위, 공식, 감쇠값과 구현을 확인해야 한다. |

실제 알고리즘에서는 다음 조건도 중요하다.

- **초기값**: 수치 IK는 가까운 해로 가는 국소 방법이다. 다른 초기값은 다른 팔꿈치 자세나 실패 결과를 만들 수 있다.
- **관절 제한**: 업데이트 뒤 값을 단순히 잘라 내면 목표로 가는 방향이 계속 막힐 수 있다. 제한에 자주 걸리면 별도 제약 처리가 필요하다.
- **여러 허용 오차**: 6D 자세에서는 위치와 방위의 허용 오차를 따로 검사한다.
- **스텝 크기**: 큰 값은 빠를 수 있지만 국소 근사가 깨진다. 작은 값은 안정적이지만 느리다.
- **도달성**: 반복 횟수 초과를 곧바로 프로그램 오류라고 판단하지 않는다. 목표가 작업공간 밖일 수 있다.

자코비안 전치 방법, 의사역행렬과 DLS를 비교하면 다음과 같다.

| 방법 | 장점 | 주의점 |
|---|---|---|
| $\eta J^T\mathbf e$ | 계산과 직관이 단순하다. | 스텝 크기에 민감하고 방향별 크기 차이가 크면 느리다. |
| $J^+\mathbf e$ | 비특이 영역에서 직접적인 최소제곱 업데이트를 준다. | 작은 특이값을 뒤집으면 업데이트가 커질 수 있다. |
| $J_\lambda^{\#}\mathbf e$ | 특이점 근처의 큰 업데이트를 억제한다. | 감쇠가 크면 정확도와 속도를 희생한다. |

## 12. 3D 기하 자코비안으로 확장하기

2R에서는 FK를 직접 편미분했다. 6R 팔도 같은 방법으로 편미분할 수 있지만 식이 길다. 관절축과 TCP의 기하 관계를 사용하면 자코비안의 각 열을 직접 만들 수 있다.

### 12.1 벡터 외적

3D 벡터 $\mathbf a=[a_x,a_y,a_z]^T$, $\mathbf b=[b_x,b_y,b_z]^T$의 **외적(cross product)** 은 다음 벡터다.

$$
\mathbf a\times\mathbf b=
\begin{bmatrix}
a_yb_z-a_zb_y\\
a_zb_x-a_xb_z\\
a_xb_y-a_yb_x
\end{bmatrix}
$$

$\mathbf a\times\mathbf b$는 두 벡터에 모두 수직이고 방향은 오른손 법칙을 따른다. 크기는 두 벡터가 만드는 평행사변형의 넓이와 같다. 두 벡터가 나란하면 외적은 0이다. 외적은 순서가 중요하며 $\mathbf a\times\mathbf b=-\mathbf b\times\mathbf a$다.

회전축 단위벡터 $\hat{\mathbf s}$ 주위로 점이 돌 때, 축 위 한 점에서 회전하는 점까지의 벡터를 $\mathbf r$라고 하면 단위 각속도가 만드는 순간 선속도 방향은 $\hat{\mathbf s}\times\mathbf r$다.

### 12.2 회전관절과 직동관절의 열

다음 벡터를 모두 베이스 좌표계에서 표현했다고 하자.

- $\hat{\mathbf s}_i$: 관절 $i$의 양의 운동축을 나타내는 단위벡터
- $\mathbf p_i$: 관절축 위 한 점의 위치
- $\mathbf p_e$: 자코비안이 설명할 TCP의 현재 위치

회전관절 $i$의 기하 자코비안 열은 다음과 같다.

$$
\mathbf J_i=
\begin{bmatrix}
\hat{\mathbf s}_i\times(\mathbf p_e-\mathbf p_i)\\
\hat{\mathbf s}_i
\end{bmatrix}
\qquad\text{회전관절 R}
$$

위쪽 세 성분은 TCP 선속도, 아래쪽 세 성분은 각속도다. 직동관절은 축을 따라 바로 이동하므로 다음과 같다.

$$
\mathbf J_i=
\begin{bmatrix}
\hat{\mathbf s}_i\\
\mathbf0
\end{bmatrix}
\qquad\text{직동관절 P}
$$

$n$개 열을 나란히 놓으면 $6\times n$ 기하 자코비안을 얻는다.

$$
J_g=
\begin{bmatrix}
\mathbf J_1&\mathbf J_2&\cdots&\mathbf J_n
\end{bmatrix}
$$

$$
\begin{bmatrix}
\mathbf v_e\\
\boldsymbol\omega_e
\end{bmatrix}
=J_g(\mathbf q)\dot{\mathbf q}
$$

표준 DH를 사용했다면 관절 $i$의 축은 $z_{i-1}$축이다.

$$
\hat{\mathbf s}_i
={}^0R_{i-1}
\begin{bmatrix}0\\0\\1\end{bmatrix}
$$

$\mathbf p_i$는 관절축 위라면 어느 점을 골라도 된다. 표준 DH에서는 프레임 $i-1$의 원점이 관절축 위에 있으므로 ${}^0T_{i-1}$의 위치 열을 사용한다. 3단계의 교육용 6R처럼 x·y축 회전도 직접 나열한 모델에서는 각 관절 앞까지의 누적 회전으로 해당 로컬 x·y·z축을 베이스 좌표계로 바꾸면 된다.

TCP를 바꾸면 $\mathbf p_e$가 달라지므로 회전관절 열의 선속도 부분도 달라진다. 플랜지 자코비안을 긴 도구의 TCP 자코비안으로 그대로 사용하면 안 된다.

## 13. 6차원 자세 오차 만들기

6R 자세 IK는 위치 3개뿐 아니라 방위 3개도 맞춰야 한다. 현재 위치와 목표 위치의 오차는 다음과 같다.

$$
\mathbf e_p=\mathbf p_d-\mathbf p
$$

방위 오차를 RPY 각의 단순한 차로 만들면 각도 순서와 짐벌락의 영향을 받는다. 이 장에서는 회전행렬의 축을 직접 비교하는 국소 오차를 사용한다.

현재 회전행렬과 목표 회전행렬의 열을 다음처럼 쓰자.

$$
R=
\begin{bmatrix}
\mathbf r_x&\mathbf r_y&\mathbf r_z
\end{bmatrix},
\qquad
R_d=
\begin{bmatrix}
\mathbf r_{x,d}&\mathbf r_{y,d}&\mathbf r_{z,d}
\end{bmatrix}
$$

베이스 좌표계에서 표현한 작은 방위 오차 벡터를 다음처럼 만들 수 있다.

$$
\mathbf e_R=
\frac12\left(
\mathbf r_x\times\mathbf r_{x,d}
+\mathbf r_y\times\mathbf r_{y,d}
+\mathbf r_z\times\mathbf r_{z,d}
\right)
$$

현재 방위와 목표 방위가 가까우면 $\mathbf e_R$의 방향은 고쳐야 할 회전축, 크기는 대략 회전각 rad를 나타낸다. 이 식은 정확히 180° 차이에서 0이 될 수 있으므로 큰 방위 오차 전체를 안전하게 표현하는 공식은 아니다. 초기 자세를 목표에 가깝게 두거나 목표 방위를 여러 작은 단계로 나누는 것이 좋다. 회전행렬 로그나 단위 쿼터니언을 이용한 큰 회전 오차는 후속 심화 주제다.

위치와 방위 오차를 세로로 쌓으면 6차원 자세 오차가 된다.

$$
\mathbf e=
\begin{bmatrix}
\mathbf e_p\\
\mathbf e_R
\end{bmatrix}
$$

그러나 $\mathbf e_p$는 m, $\mathbf e_R$은 rad이므로 숫자를 그대로 비교하면 단위 선택이 결과를 좌우한다. 서로 다른 성분의 숫자 크기를 비교할 수 있게 맞추는 과정을 **정규화(normalization)** 라고 한다. 이 입문 단계에서는 보통 대각 성분만 있는 가중행렬 $W$로 위치와 방위의 중요도를 정한다.

$$
\widetilde{\mathbf e}=W\mathbf e,
\qquad
\widetilde J=WJ_g
$$

그 뒤 $\widetilde{\mathbf e}$와 $\widetilde J$에 DLS를 적용한다. 예를 들어 방위 1 rad을 위치 $L$ m와 비슷한 중요도로 보고 싶다면 방위 부분에 **특성 길이(characteristic length)** $L$을 곱할 수 있다. $L$은 물리 법칙으로 하나가 정해지는 값이 아니라 과제의 상대적 중요도를 나타내는 설계 선택이다.

!!! warning "좌표계와 속도 순서를 섞지 않는다"
    $J_g$의 열, $\mathbf e_p$, $\mathbf e_R$는 모두 같은 기준 좌표계로 표현해야 한다. 베이스 좌표계 자코비안에 TCP 좌표계 오차를 그대로 넣으면 안 된다. 또한 이 장의 $[\mathbf v;\boldsymbol\omega]$ 순서와 다른 교재의 $[\boldsymbol\omega;\mathbf v]$ 순서를 섞지 않는다. RPY 각의 시간변화와 실제 각속도도 일반적으로 같은 벡터가 아니므로 기하 자코비안에 RPY 차이를 그대로 넣지 않는다.

## 14. 휴머노이드 전신 IK로 이어지는 두 개념

### 14.1 여유 자유도와 영공간

과제 차원보다 관절 수가 더 많은 로봇을 **여유 기구(redundant mechanism)** 라고 한다. 예를 들어 팔의 TCP 위치 3개만 맞추는 데 7개 관절을 사용하면 같은 순간 위치 변화를 만드는 관절 조합이 여러 개일 수 있다.

자코비안에 곱했을 때 0이 되는 관절 변화들의 집합을 **영공간(null space)** 이라고 한다.

$$
J\Delta\mathbf q_N=\mathbf0
$$

$\Delta\mathbf q_N$은 현재 과제를 1차 근사에서 바꾸지 않는 내부 자세 변화다. 이상적인 Moore–Penrose 의사역행렬을 사용하면 일반 해를 다음처럼 나눌 수 있다.

$$
\Delta\mathbf q
=J^+\mathbf e
+\left(I_n-J^+J\right)\mathbf z
$$

$I_n$은 관절 수 $n$에 맞는 $n\times n$ 단위행렬이다. 첫 항은 주과제를 해결하는 최소 크기 업데이트다. 둘째 항은 사용자가 고른 $\mathbf z$에서 주과제를 방해하는 성분을 제거한 영공간 움직임이다. 이를 이용하면 팔꿈치 자세를 고르거나 관절 중앙으로 돌아가려는 보조 목적을 넣을 수 있다.

DLS의 감쇠 의사역행렬을 사용하면 $I-J_\lambda^{\#}J$가 정확히 영공간 성분만 남기지는 않는다. 감쇠와 보조 과제의 상호작용까지 다루는 것은 다음 단계의 주제다.

### 14.2 여러 과제와 우선순위

휴머노이드 보행의 기구학에는 동시에 여러 조건이 나타난다.

- 지지발 자세는 바닥에 고정한다.
- 스윙발은 다음 발 디딜 위치와 방위로 보낸다.
- 골반의 높이와 방위를 원하는 범위에 둔다.
- 관절 제한을 넘지 않는 자세를 고른다.

각 과제의 오차와 자코비안에 가중치 $w_i$를 곱해 세로로 쌓으면 하나의 가중 최소제곱 문제로 만들 수 있다. 예를 들어 지지발(s), 스윙발(w), 골반(p) 과제를 함께 쓰면 다음과 같다.

$$
\overline{\mathbf e}=
\begin{bmatrix}w_s\mathbf e_s\\w_w\mathbf e_w\\w_p\mathbf e_p\end{bmatrix},
\qquad
\overline J=
\begin{bmatrix}w_sJ_s\\w_wJ_w\\w_pJ_p\end{bmatrix}
$$

가중치는 과제 사이의 타협을 바꾸지만 엄격한 우선순위를 만들지는 않는다. 단순히 쌓는 것만으로 지지발이 스윙발보다 반드시 우선한다는 보장은 없다. 5단계에서는 접촉 조건, 과제 가중치와 우선순위를 포함하는 전신 IK로 확장한다.

## 15. 인터랙티브 실습

[2R 자코비안·수치 IK 실습](./assets/jacobian-numerical-inverse-kinematics/numerical-ik-lab.html)을 열면 현재 팔, 목표점, 자코비안 두 열과 반복 경로를 함께 볼 수 있다.

다음 순서로 실험하자.

1. **정상 자세** 프리셋에서 한 단계씩 실행한다. 오차 벡터와 실제 이동이 비슷한 방향인지 본다.
2. 초기화한 뒤 자코비안 전치 방법과 DLS를 각각 30단계 실행해 반복 횟수와 경로를 비교한다.
3. **특이 근처** 프리셋에서 $\det J$가 작아지는지 확인한다. 감쇠값을 0.01과 0.3으로 바꾸어 관절 업데이트 크기를 비교한다.
4. 자코비안 열 $J_1,J_2$가 거의 나란해질 때 만들기 어려운 말단 방향을 찾는다.
5. **도달 불가** 프리셋을 실행한다. 오차가 0이 되지 않고 최대 반복 또는 정체로 끝나는지 확인한다.
6. 목표점을 캔버스에서 선택하고 서로 다른 초기 자세에서 실행한다. 같은 목표에 다른 관절해가 나오는지 관찰한다.

실습의 각도 표시는 도이지만 내부 자코비안과 업데이트는 라디안을 사용한다.

## 16. 흔한 실수

| 실수 | 왜 문제인가 | 고치는 법 |
|---|---|---|
| 도 단위로 편미분한 값과 라디안 업데이트를 섞는다. | 자코비안 크기에 $\pi/180$ 배율 차이가 생긴다. | 내부 미분과 업데이트를 라디안으로 통일한다. |
| $\Delta\mathbf x=J\Delta\mathbf q$를 큰 변화에도 정확한 등식으로 쓴다. | 자코비안은 현재 자세의 1차 근사다. | 작은 스텝 뒤 FK와 $J$를 다시 계산한다. |
| 자코비안의 행과 열을 반대로 해석한다. | 관절별 기여와 과제 성분이 뒤바뀐다. | $m$개 출력은 행, $n$개 관절은 열임을 확인한다. |
| 모든 자코비안에 $J^{-1}$을 사용한다. | 직사각형 또는 특이 행렬에는 역행렬이 없다. | 의사역행렬이나 DLS를 사용하고 차원·랭크를 확인한다. |
| 감쇠값을 0에 가깝게 두면 항상 정확하다고 생각한다. | 특이점 근처에서 큰 업데이트가 다시 나타난다. | 오차와 업데이트 크기를 함께 보고 $\lambda$를 조정한다. |
| 유한차분 $\varepsilon$에 도 값을 넣는다. | 해석 자코비안의 rad 기준과 맞지 않는다. | $\varepsilon$을 rad로 변환한다. |
| 베이스 자코비안과 TCP 좌표계 오차를 곱한다. | 같은 물리 벡터라도 좌표 숫자가 다르다. | $J$와 오차를 같은 좌표계로 표현한다. |
| $[\mathbf v;\boldsymbol\omega]$와 $[\boldsymbol\omega;\mathbf v]$ 순서를 섞는다. | 선운동과 각운동 행이 바뀐다. | 문서와 코드에 채택한 순서를 명시한다. |
| 기하 자코비안에 RPY 각 차이를 그대로 넣는다. | RPY 변화율은 일반적으로 각속도와 같지 않다. | 회전행렬에 맞는 방위 오차를 사용한다. |
| 최대 반복만 두고 종료 이유를 기록하지 않는다. | 도달 불가, 정체와 구현 오류를 구별하기 어렵다. | 수렴·정체·제한·수치 오류를 따로 판정한다. |
| DLS 반복을 PID 제어라고 부른다. | 목표와 역할이 다른 알고리즘이다. | 이 장의 계산은 정적 자세를 찾는 수치 IK로 구분한다. |

## 17. 직접 해보기

1. $g(q_1,q_2)=2\sin(q_1+q_2)$일 때 $\partial g/\partial q_1$과 $\partial g/\partial q_2$를 구하고 $(q_1,q_2)=(0°,0°)$에서 해석하라.
2. 관절이 6개이고 TCP 위치 3개만 과제로 사용한다면 자코비안의 크기는 얼마인가? 위치와 방위 6개를 모두 사용하면 어떻게 바뀌는가?
3. $l_1=l_2=1$, $q_1=0°$, $q_2=90°$에서 2R 위치 자코비안을 계산하라.
4. 문제 3의 자세에서 $\Delta\mathbf q=[0.01,0]^T$ rad일 때 자코비안이 예측하는 $\Delta\mathbf p$를 구하라.
5. 유한차분으로 자코비안의 둘째 열을 검사하려면 어떤 두 FK 입력을 사용해야 하는지 $\varepsilon$과 선택 벡터를 사용해 쓰라.
6. 2R 위치 자코비안의 행렬식이 0이 되는 $q_2$를 $0°$부터 $360°$ 사이에서 모두 쓰고 팔의 모양을 설명하라.
7. Worked Example 1에서 목표를 $(1.05,0.95)$로 바꾸었다. 같은 현재 자세와 $J^{-1}$을 사용해 한 번의 $\Delta\mathbf q$를 구하라.
8. $J=\begin{bmatrix}0&0\\2&1\end{bmatrix}$, $\mathbf e=[0,0.2]^T$, $\lambda=0.1$, $\eta=1$일 때 DLS 업데이트를 계산하라.
9. 베이스 좌표계에서 회전축 $\hat{\mathbf s}=[0,0,1]^T$, 축 위 점 $\mathbf p_i=[1,0,0]^T$, TCP $\mathbf p_e=[1,2,0]^T$인 회전관절의 6차원 기하 자코비안 열을 구하라. 같은 축의 직동관절이면 어떻게 되는가?
10. 현재 방위가 목표 방위와 정확히 180° 다를 때 이 장의 외적 기반 $\mathbf e_R$가 실패할 수 있는 이유를 설명하라.
11. $J$가 $3\times7$인 팔에서 $J^+\mathbf e$가 고르는 해의 특징과 영공간 움직임의 의미를 설명하라.
12. 수치 IK가 `오차는 크지만 업데이트는 거의 0`인 상태로 끝났다. 가능한 원인을 세 가지 쓰고 추가로 확인할 값을 제안하라.

<details>
<summary>정답</summary>

1. 두 편미분 모두 $2\cos(q_1+q_2)$다. $(0°,0°)$에서는 각각 2이므로 다른 각도를 고정하고 한 관절을 양의 방향으로 0.01 rad 늘리면 $g$는 약 0.02 증가한다.
2. 위치만 사용하면 출력 3개, 관절 6개이므로 $3\times6$이다. 위치와 방위를 모두 사용하면 $6\times6$이다.
3. $J=[-1\ -1;\ 1\ 0]$이다.
4. $\Delta\mathbf p\approx J\Delta\mathbf q=[-0.01,0.01]^T$이다.
5. $\mathbf b_2=[0,1]^T$로 두고 $\mathbf p(\mathbf q+\varepsilon\mathbf b_2)$와 $\mathbf p(\mathbf q-\varepsilon\mathbf b_2)$를 계산한다. 두 위치의 차를 $2\varepsilon$로 나눈다. $\varepsilon$은 rad다.
6. $\sin q_2=0$인 $q_2=0°,180°,360°$다. 0°와 360°에서는 두 링크가 같은 방향으로 펴지고, 180°에서는 서로 반대 방향으로 접힌다.
7. 새 오차는 $[0.05,-0.05]^T$다. $J^{-1}=\begin{bmatrix}0&1\\-1&-1\end{bmatrix}$이므로 $\Delta\mathbf q=[-0.05,0]^T$ rad다.
8. 오차가 Worked Example 2의 두 배이므로 업데이트도 두 배다. $\Delta\mathbf q\approx[0.07984,0.03992]^T$ rad다.
9. $\mathbf p_e-\mathbf p_i=[0,2,0]^T$이고 $\hat{\mathbf s}\times(\mathbf p_e-\mathbf p_i)=[-2,0,0]^T$다. 회전관절 열은 $[-2,0,0,0,0,1]^T$다. 직동관절 열은 $[0,0,1,0,0,0]^T$다.
10. 정확히 반대인 각 축의 외적이 0이 될 수 있어 $\mathbf e_R=\mathbf0$이지만 실제 방위 오차는 크다. 이 식은 가까운 두 방위를 비교하는 국소 오차로 사용해야 한다.
11. 출력보다 관절이 많아 해가 여러 개일 수 있다. $J^+\mathbf e$는 그중 2-노름이 가장 작은 관절 업데이트를 고른다. 영공간 움직임은 $J\Delta\mathbf q_N=0$을 만족해 현재 위치 과제를 1차 근사에서 바꾸지 않는 내부 자세 변화다.
12. 특이 자세, 관절 제한에 막힌 상태, 도달 불가 목표, 지나치게 큰 감쇠값 또는 잘못된 좌표계가 원인일 수 있다. $\det J$나 랭크 지표, 제한에 닿은 관절, 목표의 작업공간 포함 여부, $\lambda$, $\|\mathbf e\|$, $\|\Delta\mathbf q\|$를 확인한다.

</details>

## 18. 요약

- 자코비안은 FK의 편미분을 모아 현재 자세에서 관절의 작은 변화와 말단의 작은 변화를 연결한다.
- $m$개 과제와 $n$개 관절 사이의 자코비안은 $m\times n$이며, 각 열은 한 관절의 단위 운동이 만드는 말단 운동이다.
- 2R 위치 자코비안은 기존 FK를 $q_1,q_2$로 편미분해 얻고 유한차분으로 한 열씩 검산할 수 있다.
- 특이 자세에서는 자코비안의 독립 방향 수가 줄고 특정 말단 순간 운동을 만들 수 없다.
- 역행렬은 정사각·비특이 자코비안에만 직접 적용할 수 있다.
- Moore–Penrose 의사역행렬은 최소제곱 또는 최소 크기 해를 고르지만 특이점 근처에서 큰 업데이트가 생길 수 있다.
- DLS는 목표 잔차와 관절 업데이트 크기를 절충해 특이점 근처의 폭주를 줄인다.
- 수치 IK는 FK, 오차, 자코비안, 작은 업데이트와 종료 판정을 반복하는 국소 알고리즘이다.
- 3D 기하 자코비안은 관절축, 축 위 점과 TCP 위치로 회전·직동관절의 열을 구성한다.
- 6D 자세 IK에서는 선운동·각운동의 순서, 좌표계와 위치·방위 단위를 일치시켜야 한다.
- 휴머노이드처럼 여유 자유도가 많은 로봇에서는 영공간과 여러 과제의 우선순위가 중요하다.

## 다음 단계

[5단계: 휴머노이드 보행을 위한 전신 역기구학](./05-humanoid-whole-body-inverse-kinematics.md)에서는 지지발, 스윙발과 골반의 여러 자세 과제를 한 전신 관절벡터에 연결한다. 단순히 오차를 쌓는 방법의 한계를 확인하고, 접촉 조건과 과제 우선순위를 고려하는 휴머노이드 전신 IK로 확장한다.

## 추가 읽을거리

| 자료 | 이어서 볼 부분 |
|---|---|
| [MIT OCW 2.12 Chapter 5](https://ocw.mit.edu/courses/2-12-introduction-to-robotics-fall-2005/resources/chapter5/) | 2R 자코비안 열벡터, 특이 자세와 자코비안 역관계의 연결을 그림으로 복습한다. |
| [Caltech ME115 2016](https://robotics.caltech.edu/wiki/index.php/ME115_2016) | 매니퓰레이터 자코비안·특이점 뒤에 여유 기구와 의사역행렬이 이어지는 강의 순서를 확인한다. |
| [Caltech: The Moore–Penrose Pseudo Inverse](https://www.robotics.caltech.edu/~jwb/courses/ME115/handouts/pseudo.pdf) | 최소제곱, 최소 크기 해와 영공간의 선형대수 근거를 더 깊게 읽는다. |
| [Caltech: The Damped Pseudo Inverse](https://robotics.caltech.edu/~jwb/courses/ME115/handouts/damped.pdf) | 감쇠가 특이값의 역수를 제한하는 이유와 정확도 절충을 살펴본다. |
| [Modern Robotics Chapter 5](https://modernrobotics.northwestern.edu/nu-gm-book-resource/velocity-kinematics-and-statics/) | 공간·몸체 자코비안, 특이점과 조작성으로 확장한다. twist와 screw 이론은 추가 선수 학습이 필요하다. |
| [Modern Robotics Chapter 6](https://modernrobotics.northwestern.edu/chapters/chapter6/) | 변환행렬과 Newton–Raphson 방법을 사용하는 6D 수치 IK를 살펴본다. |

## 참고문헌

1. Asada, H. H. (2005). *Introduction to Robotics, Chapter 5: Differential Motion*. MIT OpenCourseWare. [강의 노트](https://ocw.mit.edu/courses/2-12-introduction-to-robotics-fall-2005/resources/chapter5/).
2. Burdick, J. W. (2016). *ME 115(a,b): Introduction to Kinematics and Robotics*. California Institute of Technology. [강의 일정](https://robotics.caltech.edu/wiki/index.php/ME115_2016).
3. Burdick, J. W. *The Moore–Penrose Pseudo Inverse*. California Institute of Technology. [강의 노트](https://www.robotics.caltech.edu/~jwb/courses/ME115/handouts/pseudo.pdf).
4. Burdick, J. W. *The Damped Pseudo Inverse*. California Institute of Technology. [강의 노트](https://robotics.caltech.edu/~jwb/courses/ME115/handouts/damped.pdf).
5. Lynch, K. M., & Park, F. C. (2017). *Modern Robotics: Mechanics, Planning, and Control*, Chapters 5–6. [공개 강의 보조 자료](https://modernrobotics.northwestern.edu/chapters/).
6. Wampler, C. W. (1986). Manipulator Inverse Kinematic Solutions Based on Vector Formulations and Damped Least-Squares Methods. *IEEE Transactions on Systems, Man, and Cybernetics, 16*(1), 93–101. [DOI](https://doi.org/10.1109/TSMC.1986.289285).
