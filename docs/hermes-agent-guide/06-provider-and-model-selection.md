# 작업에 맞는 provider와 model 고르기

provider는 model에 접근하고 인증·billing·routing하는 경로이고, model은 실제 reasoning과
tool call을 수행하는 engine이다. 같은 model family를 native provider, Nous Portal,
OpenRouter 같은 서로 다른 경로로 쓸 수 있다. 따라서 “어떤 model이 좋은가”와
“어느 provider로 호출할 것인가”를 나눠 결정한다.

모델 이름과 availability는 자주 바뀐다. 이 장의 이름은 2026-07-30의 공식 Hermes
catalog 예시이며, 설치된 환경의 `/model` picker와
[live model catalog](https://hermes-agent.nousresearch.com/docs/reference/model-catalog)를
최종 기준으로 삼는다.

## provider를 먼저 고른다

| 필요 | 우선 검토할 provider 유형 | 판단 기준 |
|---|---|---|
| 한 번의 인증으로 여러 model과 web·browser·media tool 사용 | Nous Portal | 운영 단순성, bundled tool |
| 여러 vendor model 비교와 세밀한 routing | OpenRouter | model 폭, routing, provider 선택 |
| 기존 ChatGPT·Claude·Copilot 구독 활용 | OpenAI Codex, Anthropic, GitHub Copilot OAuth | 기존 entitlement와 rate limit |
| vendor와 직접 계약·data path 단순화 | native API | privacy 조건, support, latency |
| enterprise cloud 정책 준수 | Bedrock, Azure AI Foundry 등 | region, audit, IAM, data policy |
| local·offline·민감 정보 | Ollama, vLLM, custom endpoint | hardware, tool-call 품질, 64K 이상 context |

aggregator는 model 전환과 fallback이 쉽고, native provider는 auth와 data path가
단순할 수 있다. 이름만 보고 고르지 말고 다음을 실제 task로 시험한다.

- tool call schema를 정확히 따르는가
- 긴 작업에서 같은 목표를 유지하는가
- file 수정 뒤 test와 verification을 수행하는가
- 긴 context에서 중요한 constraint를 놓치지 않는가
- latency와 rate limit이 운영 workload를 감당하는가
- input·output·reasoning token의 실제 비용이 얼마인가

Hermes quickstart는 최소 64,000-token context를 요구한다. local model을 쓸 때 parameter
수보다 context와 tool-use 호환성을 먼저 확인한다.

## model slot을 나눠 쓴다

Hermes의 모든 호출을 가장 비싼 main model 하나로 처리할 필요는 없다.

| slot | 하는 일 | 선택 원칙 |
|---|---|---|
| main | user turn, planning, tool loop, final response | 실패 비용과 tool-use 정확도 우선 |
| auxiliary | title, vision, compression, web extract, approval, routing | 빠르고 저렴한 model |
| delegation | child agent의 reasoning과 tool loop | subtask 난이도에 맞는 중간 tier |
| fallback | 장애 시 session을 이어갈 대체 경로 | 다른 provider와 충분한 capability |
| session override | 이번 session만 다른 model | 비교·일회성 고난도 작업 |

장기 역할별 품질 차이는 profile의 main model로 고정한다. 같은 profile 안의 작은 side
job은 auxiliary slot으로 빼고, 짧은 child 작업은 delegation model을 별도로 둔다.

## 작업 성격별 출발점

다음 표는 절대 순위가 아니라 첫 benchmark 후보를 고르는 방법이다.

| 작업 | 필요한 성질 | 2026-07-30 후보 예 |
|---|---|---|
| 일반 agent·coding·tool use | 균형, instruction 유지, 안정적 tool call | Claude Sonnet 4.6 |
| architecture·고위험 review | 깊은 reasoning, 긴 검토 | Claude Opus 4.7, GPT-5.5 Pro |
| repository 구현·debugging | code 탐색, edit, test loop | GPT-5.3 Codex, Claude Sonnet 4.6 |
| 긴 문서·multimodal synthesis | 긴 context, image·document 이해 | Gemini 3.1 Pro Preview |
| 단순 formatting·분류·요약 | 낮은 latency와 비용 | Gemini 3 Flash Preview, GPT-5.4 Mini, Claude Haiku 4.5 |
| local·privacy 우선 | self-host 가능, 충분한 context와 tool call | 환경에서 검증한 Ollama·vLLM model |

공식 Nous Portal 문서는 Sonnet 계열을 general-purpose agentic model의 출발점으로
제시하고 GPT, Gemini, DeepSeek, Qwen, Kimi, GLM, MiniMax 등 다양한 model을 제공한다.
하지만 실제로는 자신의 repository, source language, toolset으로 작은 acceptance
suite를 만들어 비교해야 한다.

## 실용적인 기본 구성

아래 예시는 main agent의 품질을 유지하면서 반복 side job 비용을 낮추고 provider
장애에 대비하는 형태다. model ID는 provider의 현재 catalog에 맞게 바꾼다.

```yaml
model:
  provider: openrouter
  default: anthropic/claude-sonnet-4.6

auxiliary:
  compression:
    provider: openrouter
    model: google/gemini-3-flash-preview
    reasoning_effort: low
  vision:
    provider: openrouter
    model: google/gemini-2.5-flash
    reasoning_effort: none

delegation:
  provider: openrouter
  model: openai/gpt-5.4-mini

fallback_providers:
  - provider: openai-codex
    model: gpt-5.3-codex
```

구성 key와 model ID는 version에 따라 달라질 수 있으므로 dashboard의 Models 화면이나
`hermes model`, `hermes fallback`을 우선 사용한다. 직접 YAML을 수정했다면
`hermes config`와 새 session에서 결과를 확인한다.

## profile별 model 예

| profile | main model tier | auxiliary | 이유 |
|---|---|---|---|
| orchestrator | 강한 general reasoning | cheap routing·title | task graph와 acceptance 판단이 중요 |
| researcher | 긴 context·web synthesis | cheap web extract | source 읽기와 claim 비교가 많음 |
| coder | 강한 coding agent | cheap title·compression | edit·test loop의 실패 비용이 큼 |
| reviewer | main과 다른 강한 family | cheap title | 독립 시각과 상관된 오류 감소 |
| high-volume formatter | fast low-cost | 같은 low-cost | 반복 단순 작업 |

reviewer는 coder와 다른 model family를 사용하면 같은 blind spot을 반복할 가능성을
낮출 수 있다. 반면 형식 변환처럼 deterministic한 일은 model을 키우기보다 script나
`execute_code`로 바꾸는 편이 낫다.

## `/model`을 언제 쓰는가

Discord에서 `/model`을 보내면 이미 인증된 provider와 model을 picker로 고를 수 있다.
현재 session의 일회성 변경에는 편리하지만 model이 바뀌면 prompt cache가 reset되어
다음 message가 전체 conversation input을 다시 처리할 수 있다.

- 긴 session에서 model을 여러 번 왕복하지 않는다.
- 새 역할이나 장기 정책이면 profile config를 바꾸고 새 session을 시작한다.
- 한 번의 고난도 판단이면 `/model`로 올렸다가, 후속 단순 작업은 새 session에서
  저비용 model로 시작한다.
- `/usage`로 switch 이후 input cost와 context 크기를 확인한다.

## auxiliary model을 먼저 최적화한다

title generation, compression, approval scoring, web extraction은 호출 횟수가 많지만
대부분 flagship reasoning을 요구하지 않는다. main model을 낮추기 전에 이 side job을
fast model로 옮기면 품질 손실이 작고 절감 효과를 측정하기 쉽다.

다만 compression은 이후 session이 무엇을 기억하는지 결정한다. 지나치게 약한 model이
constraint나 unresolved risk를 버리지 않는지 긴 대화로 검증한다. vision model은
image 이해가 필요한 task에서만 별도 지정하고, OCR 정확도도 시험한다.

## fallback은 capability가 있는 다른 경로로

fallback은 동일 provider의 같은 장애를 반복하지 않도록 다른 provider를 섞는다.
main model이 tool use, vision, 긴 context를 필요로 한다면 fallback도 필요한 capability를
가져야 한다. 단순히 가장 싼 model을 넣으면 API error는 피했지만 task가 잘못 완료될 수
있다.

Hermes는 같은 provider의 여러 credential을 먼저 돌리는 credential pool, 다른
provider:model로 전환하는 primary fallback, side job별 auxiliary fallback을 지원한다.
자세한 설정은
[Fallback Providers](https://hermes-agent.nousresearch.com/docs/user-guide/features/fallback-providers/)를
참조한다.

[← 5장](./05-multi-agent-operations.md) · [목차](./index.md) ·
[7장: 보안·비용·신뢰성 운영 →](./07-security-cost-reliability.md)
