# PPO-Clip 목적함수

**PPO(Proximal Policy Optimization)** 는 “가까운 범위에서 정책을 최적화한다”는 이름의 policy-gradient 알고리즘군이다. 여기서 **proximal**은 새 정책을 데이터 수집 정책에서 지나치게 멀리 보내지 않겠다는 뜻이다. 이 장의 중심 질문은 **“같은 rollout을 여러 번 학습하면서 정책 변화가 너무 커지는 것을 어떻게 억제하는가?”** 다. REINFORCE와 actor–critic 위에 가장 널리 쓰이는 PPO-Clip을 한 층씩 쌓는다.

## 학습 목표

이 장을 마치면 다음을 할 수 있다.

1. old 정책과 현재 정책의 같은 행동 확률로 importance ratio를 계산한다.
2. advantage 부호에 따라 clipping이 제한하는 ratio 방향을 판단한다.
3. 최대화 목적과 최소화 policy loss의 부호를 변환한다.
4. rollout, mini-batch, update epoch의 차이를 설명한다.
5. PPO clipping이 엄밀한 trust region 보장은 아니라는 한계를 말한다.

## 한 batch를 여러 번 쓰면 생기는 문제

Policy gradient는 현재 정책으로 모은 데이터를 전제로 한다. rollout을 한 번 모은 직후에는 데이터 정책과 학습 정책이 같다. 첫 optimizer step 뒤에는 정책이 바뀐다. 같은 데이터를 계속 학습하면 데이터는 점점 **old 정책**의 것이 된다.

REINFORCE loss만 여러 번 반복하면 일부 행동 확률이 너무 크게 바뀌어 다음 문제가 생길 수 있다.

- 이전에 잘 작동하던 행동이 한 update에서 사라진다.
- 같은 batch의 우연한 advantage에 과적합한다.
- 새 정책이 old 데이터 분포와 멀어져 gradient 추정이 부정확해진다.

PPO는 probability ratio로 변화량을 측정하고 clipped objective로 과도한 변화의 추가 이득을 제한한다. 여기서 **과적합(overfitting)** 은 한 rollout의 우연한 패턴에는 지나치게 잘 맞지만 새로 수집한 데이터에서는 성능이 나빠지는 현상이다.

## Old log probability를 저장한다

Rollout 시점에 다음 값을 함께 저장한다.

```text
observation, action, reward, terminated, truncated,
old_log_prob, old_value
```

Update 중에는 저장한 같은 행동 $a_t$에 대해 현재 정책의 `new_log_prob`을 다시 계산한다.

$$
r_t(\theta)=\frac{\pi_\theta(a_t\mid s_t)}{\pi_{old}(a_t\mid s_t)}
=\exp(\log\pi_\theta-\log\pi_{old})
$$

!!! warning "$r_t$와 $r_t(\theta)$를 구별한다"
    2장 기호표의 괄호 없는 $r_t$는 **보상**이었다. 이 장부터 나오는 확률비는 보상과 아무 관계가 없으며 **항상 $r_t(\theta)$** 처럼 $\theta$를 붙여 쓴다. 아래 표와 수식에서 괄호가 보이면 확률비, 보이지 않으면 보상이다.

이 비율은 **importance sampling(중요도 표본추출)** 의 핵심 가중치다. 다른 분포에서 얻은 표본을 현재 분포의 기댓값에 맞게 재가중하는 방법이다. PPO에서는 완전한 importance-sampling 보정 전체를 사용하는 것이 아니라 old 정책이 고른 행동에 대한 확률비를 surrogate 목적에 넣는다.

한 상태에서 old 정책이 `[왼쪽 0.8, 오른쪽 0.2]`, 새 정책이 `[왼쪽 0.6, 오른쪽 0.4]`라 하자.

| 실제 저장 행동 | old 확률 | 새 확률 | ratio | 의미 |
|---|---:|---:|---:|---|
| 왼쪽 | 0.8 | 0.6 | 0.75 | 새 정책에서 덜 흔해짐 |
| 오른쪽 | 0.2 | 0.4 | 2.00 | 새 정책에서 두 배 흔해짐 |

같은 상태라도 **실제로 rollout에 저장된 행동**에 따라 ratio가 다르다. 모든 행동 확률을 한꺼번에 나누는 값이 아니다.

| ratio | 의미 |
|---:|---|
| $r_t(\theta)=1$ | 선택 행동의 확률이 old와 같다. |
| $r_t(\theta)=1.2$ | 선택 행동 확률이 20% 커졌다. |
| $r_t(\theta)=0.7$ | 선택 행동 확률이 30% 작아졌다. |

Rollout 직후 optimizer step 전에는 같은 actor를 사용하므로 ratio가 수치 오차 범위에서 1이어야 한다. 이것은 중요한 단위 검사다.

## Unclipped surrogate objective

**Surrogate objective(대리 목적함수)** 는 진짜 기대 return을 매 update마다 새로 끝까지 측정하는 대신, 수집된 데이터로 정책 개선 방향을 근사하는 계산 가능한 목적함수다. Importance ratio로 old 데이터를 현재 정책 목적에 보정한 기본 항은 다음이다.

$$
L_t^{unclip}(\theta)=r_t(\theta)\hat A_t
$$

- $\hat A_t>0$: ratio가 커질수록 목적이 커진다. 좋은 행동 확률을 올린다.
- $\hat A_t<0$: ratio가 작아질수록 목적이 커진다. 나쁜 행동 확률을 내린다.

이 항만 사용하면 ratio가 멀리 움직여도 계속 이득이 생긴다.

## Clipped surrogate objective

$\epsilon$을 clip 폭이라 하자. 보통 첫 실험에서 0.2를 자주 사용한다.

`clip(x, lower, upper)`는 $x$가 아래 경계보다 작으면 아래 경계, 위 경계보다 크면 위 경계, 사이면 $x$ 그대로를 반환한다.

$$
\operatorname{clip}(x,l,u)=
\begin{cases}
l & x<l\\
x & l\le x\le u\\
u & x>u
\end{cases}
$$

$$
L_t^{clip}(\theta)=\min\left(
r_t(\theta)\hat A_t,
\operatorname{clip}(r_t(\theta),1-\epsilon,1+\epsilon)\hat A_t
\right)
$$

두 후보 중 더 작은 값, 즉 더 비관적인 목적을 선택한다.

[PPO clipping 실험실에서 ratio·advantage·epsilon 바꾸기](./assets/ppo-objective/ppo-clipping-lab.html)

### Advantage가 양수일 때

$\hat A=2$, $\epsilon=0.2$라 하자.

| ratio | $rA$ | $clip(r)A$ | `min` | 해석 |
|---:|---:|---:|---:|---|
| 0.7 | 1.4 | 1.6 | 1.4 | 좋은 행동 확률이 줄어 손해 |
| 1.0 | 2.0 | 2.0 | 2.0 | old와 같음 |
| 1.1 | 2.2 | 2.2 | 2.2 | 허용 구간의 개선 |
| 1.5 | 3.0 | 2.4 | 2.4 | 1.2 이후 추가 이득 제한 |

양의 advantage에서는 주로 위쪽 $1+\epsilon$이 제한한다.

### Advantage가 음수일 때

$\hat A=-2$, $\epsilon=0.2$다.

| ratio | $rA$ | $clip(r)A$ | `min` | 해석 |
|---:|---:|---:|---:|---|
| 0.4 | -0.8 | -1.6 | -1.6 | 0.8 아래 추가 이득 제한 |
| 0.9 | -1.8 | -1.8 | -1.8 | 허용 구간 |
| 1.0 | -2.0 | -2.0 | -2.0 | old와 같음 |
| 1.4 | -2.8 | -2.4 | -2.8 | 나쁜 행동 확률 증가를 강하게 벌점 |

음수에 `min`을 적용할 때 부호 때문에 직관이 뒤집히기 쉽다. 곡선을 외우기보다 두 후보를 직접 계산한다.

## 최대화 목적을 최소화 loss로 바꾸기

논문은 $L^{clip}$을 최대화한다. PyTorch optimizer는 loss를 최소화하므로 음수를 붙인다.

```python
log_ratio = new_log_prob - old_log_prob
ratio = torch.exp(log_ratio)

unclipped = ratio * advantages
clipped = torch.clamp(
    ratio,
    1.0 - clip_epsilon,
    1.0 + clip_epsilon,
) * advantages

policy_loss = -torch.minimum(unclipped, clipped).mean()
```

같은 계산을 `torch.maximum(-unclipped, -clipped).mean()`으로 쓸 수도 있다.

## Actor, critic과 entropy를 합친 loss

교육용 구현의 total loss는 다음처럼 구성한다.

$$
L_{total}=-L^{clip}+c_vL_V-c_eH
$$

$$
L_V=\frac12\left(V_\phi(s_t)-\hat V_t^{target}\right)^2
$$

| 항 | 목적 | 흔한 시작 계수 |
|---|---|---:|
| policy loss | clipped objective 최대화 | 1 |
| value loss | critic을 value target에 회귀 | $c_v=0.5$ |
| entropy bonus | 탐색 유지 | $c_e=0.01$ |

계수는 환경과 reward scale에 따라 달라진다. 원 논문의 수식과 특정 구현의 기본값을 같은 필수 규칙으로 혼동하지 않는다.

## Rollout, mini-batch와 epoch

![현재 정책으로 수집한 batch를 제한된 epoch 동안 사용한 뒤 폐기하는 PPO 흐름](./assets/common/ppo-dataflow.svg)

- `rollout_steps`: 정책을 고정한 채 모으는 transition 수
- `minibatch_size`: optimizer step 한 번에 사용하는 샘플 수
- `update_epochs`: 같은 rollout 전체를 다시 섞어 학습하는 횟수

예를 들어 rollout 1,024개, mini-batch 64개, epoch 10이면 최대 optimizer step 수는 다음과 같다.

$$
\frac{1024}{64}\times10=160
$$

PPO가 on-policy라는 사실은 같은 batch를 한 번만 쓴다는 뜻이 아니다. **현재 정책 batch를 제한된 여러 epoch 동안 사용한 뒤 버리고 새 정책으로 다시 수집한다**는 뜻이다.

## PPO-Clip 전체 알고리즘

```text
정책 πθ와 가치 Vφ 초기화

반복:
  1. πold = 현재 정책인 상태에서 rollout 수집
  2. action의 old_log_prob와 value 저장
  3. reward, 종료 신호, value로 GAE와 value target 계산
  4. 여러 epoch 반복:
       rollout index를 섞고 mini-batch로 나눔
       같은 action의 new_log_prob 계산
       ratio = exp(new_log_prob - old_log_prob)
       clipped policy loss + value loss - entropy bonus 계산
       backward → gradient clip → optimizer step
       KL이 너무 크면 epoch 조기 중단 가능
  5. 이 rollout 폐기
```

## 변화량을 보는 진단 지표

### Approximate KL

**KL divergence(Kullback–Leibler divergence)** 는 기준 분포 $p$에서 볼 때 다른 분포 $q$가 얼마나 다른지를 재는 양이다. 이산 행동에서는

$$
D_{KL}(p\Vert q)=\sum_a p(a)\log\frac{p(a)}{q(a)}
$$

이다. 0 이상이고 두 분포가 같으면 0이지만, 일반적으로 $D_{KL}(p\Vert q)\ne D_{KL}(q\Vert p)$이므로 거리처럼 대칭은 아니다. 또한 삼각부등식을 만족하는 일반적인 거리도 아니다.

정책 변화가 허용 범위 안에 있도록 KL 같은 척도로 제한한 영역을 **trust region(신뢰 영역)** 이라 한다. PPO의 전신인 **TRPO(Trust Region Policy Optimization)** 는 평균 KL 제약을 근사해 푸는 더 복잡한 방법이다. PPO-Clip은 제약 최적화 대신 clipping으로 구현을 단순화한다.

직접 구현에서 자주 쓰는 비음수 근사치는 다음 샘플 평균이다.

$$
\widehat{KL}\approx\mathbb E[(r_t(\theta)-1)-\log r_t(\theta)]
$$

갑자기 커지면 학습률, epoch 수, advantage scale, 데이터 정합성을 점검한다. `target_kl`을 넘으면 나머지 epoch를 조기 중단하는 구현도 있다.

PPO 논문에는 clipped surrogate를 쓰는 **PPO-Clip**과 KL 벌점 계수를 조절하는 **PPO-Penalty**가 함께 제안됐다. 이 책과 예제에서 “PPO”라고 부르는 것은 별도 표기가 없으면 PPO-Clip이다.

### Clip fraction

$$
\text{clipfrac}=\frac1N\sum_t
\mathbf1[|r_t(\theta)-1|>\epsilon]
$$

샘플 중 ratio가 clip 구간 밖으로 나간 비율이다.

- 거의 0이 계속됨: update가 매우 작거나 gradient가 제대로 흐르지 않을 수 있다.
- 매우 높음: 정책이 너무 크게 움직이거나 epoch가 많을 수 있다.

절대적인 정상 범위는 환경과 설정에 따라 달라 단독으로 성공·실패를 판정하지 않는다.

### Entropy

Entropy가 너무 빠르게 0으로 떨어지면 정책이 탐색 전에 한 행동으로 굳을 수 있다. 반대로 높은 entropy가 끝까지 유지되고 return이 오르지 않으면 유용한 행동 선호를 학습하지 못했을 수 있다.

## Clipping이 보장하지 않는 것

PPO clipping은 다음을 **보장하지 않는다**.

- 모든 상태에서 정책 확률 변화가 $\epsilon$ 이내라는 hard constraint
- KL divergence가 항상 일정 값 아래라는 보장
- 학습 안정성의 자동 보장
- 잘못된 GAE나 환경 종료 처리의 복구

Clipping은 샘플별 surrogate objective에서 과도한 변화가 주는 추가 이득을 제거한다. 여러 상태의 신경망 파라미터가 공유되므로 한 mini-batch update가 다른 관측의 정책에도 영향을 준다.

또한 clipping은 경계 밖의 모든 gradient를 없애는 단순한 벽이 아니다. 선택된 두 항 중 어느 쪽이 더 작은지와 advantage 부호에 따라 평평해지는 방향이 달라진다. 나쁜 방향의 변화에는 여전히 벌점 gradient가 남을 수 있다. 그래서 ratio 평균, KL, clip fraction, return을 함께 관찰해야 한다.

## Worked Example: 한 샘플의 policy loss

다음 값을 가정한다.

```text
old_log_prob = log(0.50)
new_log_prob = log(0.80)
advantage = 2.0
epsilon = 0.2
```

$$
r=\exp[\log(0.8)-\log(0.5)]=1.6
$$

$$
rA=3.2,\qquad clip(r,0.8,1.2)A=2.4
$$

목적값은 `min(3.2, 2.4)=2.4`, 최소화 policy loss 기여는 `-2.4`다. 선택 행동 확률을 이미 크게 올렸으므로 1.2 너머의 추가 이득이 사라진다.

## 흔한 오류

| 오류 | 결과 | 확인 방법 |
|---|---|---|
| old log probability를 update 중 재계산 | ratio가 잘못됨 | optimizer 전 ratio 평균이 1인지 확인 |
| `minimum` 대신 항상 clip 항 사용 | 허용 구간 밖의 나쁜 변화까지 완화 | advantage 부호별 표로 검산 |
| 목적을 그대로 loss로 최소화 | 정책이 반대 방향으로 학습 | policy loss 앞 음수 확인 |
| rollout 중간에 optimizer update | batch 안에 여러 정책 데이터 혼합 | 수집과 update 단계 분리 |
| old batch를 다음 수집 뒤에도 유지 | on-policy 가정 악화 | update 뒤 buffer 비우기 |
| PPO clipping과 gradient clipping 혼동 | 디버깅 지표 해석 오류 | ratio와 gradient norm을 별도 기록 |

## 정리

- 한 batch를 여러 번 쓰려면 old log probability를 저장해야 한다. 그 비율이 $r_t(\theta)$이며 보상 $r_t$와 다른 기호다.
- clipping은 advantage 부호에 따라 서로 다른 방향의 ratio 이동만 막는다. 양쪽을 대칭으로 막지 않는다.
- 최대화 목적 $L^{clip}$은 부호를 뒤집어 최소화 loss로 만든다. entropy 항 앞에는 음수가 붙는다.
- rollout, mini-batch, epoch는 서로 다른 반복 단위다. epoch를 늘리면 데이터 재사용과 함께 KL도 커진다.
- clipping은 KL에 대한 엄밀한 trust region 보장이 아니다. 그래서 7장의 지표로 실제 변화량을 관찰해야 한다.

## 연습문제

1. old 확률 0.4, 새 확률 0.48일 때 ratio를 계산하라.
2. $A=3$, $r=1.5$, $\epsilon=0.2$일 때 unclipped, clipped, min 목적값을 구하라.
3. $A=-3$, $r=0.5$, $\epsilon=0.2$일 때 같은 값을 구하라.
4. rollout 2,048, mini-batch 128, epoch 4일 때 optimizer step 수를 구하라.
5. rollout 직후 첫 forward에서 ratio 평균이 0.6이라면 무엇을 먼저 의심해야 하는가?

??? note "정답 확인"
    1번: 1.2. 2번: 4.5, 3.6, 3.6. 3번: -1.5, -2.4, -2.4. 4번: $2048/128\times4=64$. 5번: old와 new 정책·관측 전처리가 같은지, old log probability를 수집 시점에 저장했는지 확인한다.

## 참고문헌

- Schulman et al. (2017), [*Proximal Policy Optimization Algorithms*](https://arxiv.org/abs/1707.06347)
- [OpenAI Spinning Up: PPO](https://spinningup.openai.com/en/latest/algorithms/ppo.html)
- [UC Berkeley CS 185/285: Advanced Policy Gradients](https://rail.eecs.berkeley.edu/deeprlcourse/)
- [TorchRL `ClipPPOLoss` API](https://docs.pytorch.org/rl/stable/reference/generated/torchrl.objectives.ClipPPOLoss.html)

[← 4장](./04-policy-gradient-and-gae.md) · [목차](./index.md) · [6장: 순수 PyTorch로 PPO 만들기 →](./06-build-ppo-with-pytorch.md)
