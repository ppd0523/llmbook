# 작업에 맞는 제공자와 모델 고르기

제공자(provider)는 모델에 접근하고 인증·과금·경로 선택을 담당하는 서비스이고,
모델(model)은 실제 추론과 도구 호출을 수행하는 엔진이다. 같은 모델도 native API,
Nous Portal, OpenRouter 같은 서로 다른 제공자를 통해 쓸 수 있다. 따라서 “어떤 모델이
이 작업을 잘하는가”와 “어느 경로로 호출할 것인가”를 따로 결정한다.

모델 이름과 제공 여부는 자주 바뀐다. 이 장의 예시는 2026-08-11에 확인했으며, 실제
선택에서는 설치 환경의 `/model` picker와
[live model catalog](https://hermes-agent.nousresearch.com/docs/reference/model-catalog)를
최종 기준으로 삼는다. picker는 인증된 제공자만 보여 주며, 네트워크에 연결되지 않으면
설치본에 포함된 catalog snapshot을 사용할 수 있다.

## 제공자는 운영 제약으로 고른다

| 운영 조건 | 먼저 검토할 경로 | 확인할 것 |
|---|---|---|
| 한 번의 인증으로 여러 모델과 부가 도구를 쓰고 싶다 | Nous Portal | 구독 범위, 제공 도구, 사용량 정책 |
| 여러 회사의 모델을 같은 API에서 비교하고 싶다 | OpenRouter | 실제 route, 가격, provider pinning |
| 기존 ChatGPT·Claude·Copilot 사용 권한을 활용한다 | OpenAI Codex·Anthropic·GitHub Copilot OAuth | entitlement, rate limit, 조직 정책 |
| 모델 회사와 직접 계약하거나 데이터 경로를 단순화한다 | native API | 보존 정책, 지역, 지원, latency |
| 기업 cloud의 IAM과 감사를 따라야 한다 | Bedrock·Azure AI Foundry 등 | region, audit log, private network |
| 오프라인 또는 민감 정보 처리가 우선이다 | Ollama·vLLM·custom endpoint | hardware, context 길이, tool-call 품질 |

통합 제공자(aggregator)는 여러 회사의 모델을 한 API와 계정으로 중계하는 서비스다.
OpenRouter가 대표적이다. 직접 제공자(native provider)는 모델 회사의 API를 바로 쓰는
경로다. 통합 제공자는 모델 전환과 fallback이 편하고, 직접 제공자는 인증과 데이터
경로가 단순할 수 있다. 이름만 보고 고르지 말고 실제 저장소, 언어, 도구 모음으로
시험한다.
local model은 parameter 수보다 충분한 context 길이와 구조화된 tool call 호환성을 먼저
확인한다. Hermes quickstart의 기준은 최소 64K-token context다.

## 호출 목적에 따라 모델 슬롯을 나눈다

모델 슬롯(model slot)은 호출 목적별로 사용할 모델을 따로 지정하는 설정 자리다. 모든
호출을 가장 비싼 주 모델 하나로 처리할 필요는 없다.

| slot | 하는 일 | 선택 원칙 |
|---|---|---|
| main | 사용자 대화, 계획, 도구 반복, 최종 응답 | 실패 비용과 tool-use 정확도 우선 |
| auxiliary | title, vision, compression, web extract, approval, routing 등 | 목적별로 빠르고 저렴한 모델 |
| delegation | 하위 에이전트의 추론과 도구 반복 | subtask 난이도와 병렬 수에 맞춘 모델 |
| fallback | 주 경로가 실패했을 때 세션을 잇는 대체 경로 | 다른 제공자와 필요한 기능 |
| 세션 override | 현재 세션에서만 쓰는 모델 | 일회성 비교 또는 고난도 판단 |

장기 역할의 품질 차이는 프로필의 main model로 고정한다. 같은 프로필의 반복적인
부가 작업은 auxiliary slot으로, fresh-context 하위 작업은 delegation model로 분리한다.

## 작업 성격으로 모델 등급을 고른다

다음 표는 절대 순위가 아니라 첫 benchmark 후보를 정하는 기준이다.

| 작업 성격 | 우선할 성질 | 시작 tier | 낮추거나 올리는 신호 |
|---|---|---|---|
| 일반 대화·도구 사용 | 지시 유지, 안정적 tool call, 균형 | 강한 general agent | 반복 실패가 없으면 한 단계 낮춰 비교 |
| 저장소 구현·debugging | code 탐색, 정확한 edit, test loop | 강한 coding agent | 수정 누락·잘못된 도구 호출이 생기면 올림 |
| architecture·보안 review | 깊은 reasoning, 긴 검토, 반례 탐색 | flagship reasoning | 실패 비용이 높으면 비용보다 독립 검증 우선 |
| 긴 문서·multimodal 종합 | 긴 context, image·document 이해 | long-context multimodal | citation 누락과 context 손실을 측정 |
| 분류·formatting·title | 낮은 latency와 비용 | flash·mini tier | schema 오류가 없으면 유지 |
| 반복 web extraction | 안정적 요약, 낮은 단가 | fast auxiliary | source 누락·숫자 왜곡이 생기면 올림 |
| local·privacy 작업 | self-host, 충분한 context·tools | 환경에서 검증한 local model | latency와 tool schema 실패를 함께 측정 |

2026-08-11의 catalog에는 예를 들어 GLM 5.2, Kimi K3, GPT-5.4, Claude Opus 4.7 같은
후보가 보인다. Configuring Models 문서는 Gemini Flash 계열을 title·vision·compression
같은 auxiliary 예시로, Codex 계열을 fallback 예시로 사용한다. 이 이름은 추천 순위가
아니며 catalog가 바뀌면 그대로 교체한다.

## 작은 인수 시험 묶음으로 비교한다

인수 시험 묶음(acceptance suite)은 실제 운영을 대표하는 입력과 완료 조건을 모아 모델
후보를 같은 기준으로 비교하는 시험 세트다. 자신의 반복 업무에서 대표 작업 5~10개를
고른다. 각 후보를 같은 입력과 도구로 실행해
다음 항목을 기록한다.

1. 완료 조건을 한 번에 충족한 비율
2. 잘못된 tool call과 사람이 수정한 횟수
3. test·source·diff 같은 검증 증거의 정확성
4. 총 latency와 input·output·reasoning token
5. retry와 사람의 교정 시간을 포함한 실제 비용

예를 들어 coding profile이라면 “한 파일 수정”만 시험하지 않는다. 검색, 다중 파일
수정, 실패 test 진단, 금지 범위 준수, 최종 검증을 함께 넣는다. reviewer는 coder와 다른
model family로 시험하면 같은 blind spot을 반복할 가능성을 줄일 수 있다.

## 실용적인 기본 구성

처음에는 대시보드의 Models 화면이나 `hermes model`, `hermes fallback`을 쓰는 편이
안전하다. 다음 YAML은 각 slot의 위치를 보여 주는 예시다. model ID는 현재 picker에
보이는 ID로 바꾼다.

```yaml
model:
  provider: openrouter
  default: anthropic/claude-sonnet-4

auxiliary:
  title_generation:
    provider: openrouter
    model: google/gemini-3-flash-preview
  web_extract:
    provider: openrouter
    model: google/gemini-3-flash-preview
  compression:
    provider: openrouter
    model: google/gemini-3-flash-preview

delegation:
  provider: openrouter
  model: openai/gpt-5.4

fallback_providers:
  - provider: nous
    model: z-ai/glm-5.2
```

`fallback_providers`는 현재 형식이고, 과거의 단일 `fallback_model`은 이전 버전 호환을
위해 읽히는 형식이다. auxiliary slot을 `provider: auto`로 두면 main 경로, 해당 slot의
`fallback_chain`, top-level fallback, 내장 discovery chain 순서로 사용 가능한 경로를
찾는다. 예상하지 못한 provider로 비용이 나가지 않는지 usage와 log를 확인한다.

## 프로필별 배치 예

| 프로필 | 주 모델 | 보조 모델 | 이유 |
|---|---|---|---|
| orchestrator | 강한 general reasoning | cheap routing·title | task graph와 acceptance 판단이 중요 |
| researcher | long-context·web synthesis | cheap web extract | source 읽기와 claim 비교가 많음 |
| coder | 강한 coding agent | cheap title·compression | edit·test 실패 비용이 큼 |
| reviewer | coder와 다른 강한 family | cheap title | 독립 시각과 상관된 오류 감소 |
| high-volume formatter | fast low-cost | 같은 low-cost | 반복 단순 작업 |

형식 변환처럼 결정적인(deterministic) 작업은 모델을 키우기 전에 script나
`execute_code`로 바꿀 수 있는지 먼저 본다. 반대로 보안 검토처럼 거짓 음성의 비용이 큰
작업은 호출 수를 줄이더라도 강한 main model과 독립 검토를 유지한다.

## `/model`은 현재 세션의 예외에 쓴다

Discord에서 `/model`을 보내면 이미 인증된 provider와 model을 picker로 고를 수 있다.
프롬프트 캐시(prompt cache)는 반복되는 대화 앞부분을 제공자 쪽에 잠시 보관해 다음
호출의 입력 비용과 지연을 줄이는 기능이다. `/model`은 현재 세션에 즉시 적용되지만
모델이 바뀌면 이 캐시가 초기화되어 다음 메시지가 전체 대화 입력을 다시 처리할 수 있다.
새 모델의 맥락 창 한계에 가까우면 다음 메시지 전에 맥락 압축(context compression),
즉 오래된 대화를 요약해 입력 길이를 줄이는 작업이 실행될 수도 있다.

- 긴 세션에서 모델을 여러 번 왕복하지 않는다.
- 새 역할이나 장기 정책이면 프로필 설정을 바꾸고 새 세션을 시작한다.
- 일회성 고난도 판단이면 `/model`을 사용하되 가능하면 대화 초반에 바꾼다.
- `/usage`로 switch 이후 input cost와 context 크기를 확인한다.

대시보드나 config에서 바꾼 main model은 새 gateway session부터 적용된다. 이미 열린
세션은 기존 모델을 유지하므로 즉시 바꾸려면 그 세션에서 `/model`을 사용한다.

## 대체 경로는 필요한 기능을 보존한다

대체 경로(fallback)는 주 제공자나 모델이 실패할 때 이어서 시도하는 예비
`provider:model` 조합이다. 같은 제공자의 같은 장애를 반복하지 않도록 다른 제공자를
섞는다. 주 모델이 도구 사용, vision, 긴 context를 필요로 한다면 fallback도 필요한 기능을
가져야 한다. 가장 싼 모델만 넣으면 API 오류는 피했지만 작업이 잘못 완료될 수 있다.

자격 증명 풀(credential pool)은 같은 제공자의 API key나 OAuth token 여러 개를
차례로 사용하는 묶음이다. 이는 다른 제공자로 넘어가는 fallback과 다르다. Hermes는
같은 provider의 자격 증명 풀을 먼저 돌리고, 필요하면 다른 `provider:model`로 전환하는
주 대체 경로와 부가 작업별 대체 경로를 사용한다.
자세한 현재 형식은
[Fallback Providers](https://hermes-agent.nousresearch.com/docs/user-guide/features/fallback-providers/)에서
확인한다.

## 6장 확인 문제

- 같은 모델을 OpenRouter와 native API로 쓸 때 따로 평가해야 할 운영 조건은 무엇인가?
- main model을 낮추기 전에 auxiliary model을 먼저 최적화하기 좋은 이유는 무엇인가?
- fallback이 main보다 저렴하다는 사실만으로 적합하다고 판단할 수 있는가?

[← 5장](./05-multi-agent-operations.md) · [목차](./index.md) ·
[7장: 보안·비용·신뢰성 운영 →](./07-security-cost-reliability.md)
