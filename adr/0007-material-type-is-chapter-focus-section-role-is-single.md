# 자료 유형은 챕터의 중심을 정하고, 유형을 섞지 않는 단위는 절이다

자료 유형(개념형·실습형·참조형)을 챕터 하나에 하나씩 붙이면, Hermes Agent 가이드처럼 "개념을 익혀 실습으로 완성하는" 책은 분류할 수 없다. 외부 문헌은 이 두 가지를 다른 층으로 다룬다. 정보를 어떻게 주는가는 블록·주제 단위로 나누고(Horn의 정보 유형, DITA의 concept·task·reference), 독자에게 무엇을 시키는가는 그 위에서 설계한다(Horn의 "능동적 참여", DITA 학습용 확장의 학습 내용·평가, 4C/ID의 학습 과제). 그래서 자료 유형은 챕터의 중심만 정하고, 섞지 않는 규칙은 절 단위(개념·절차·참조·과제)에 적용하기로 했다. 챕터 설계는 독자가 수행할 과제를 먼저 정하고 개념과 절차를 거기에 붙인다(4C/ID에서 학습 과제가 뼈대인 것과 같다).

## 고려한 대안

- 챕터마다 유형 하나만 허용: 섞인 챕터를 억지로 나누거나 한쪽 골격을 강요하게 된다. DITA 학습용 확장은 학습 내용이 concept·task·reference를 함께 쓰는 것을 전제한다.
- 네 번째 유형(혼합형) 추가: 섞이는 단위가 절인데 챕터에 이름을 하나 더 붙여도 판정 문제는 풀리지 않는다.
- Diátaxis처럼 튜토리얼과 how-to를 별도 유형으로 분리: 이미 배운 독자가 작업 중에 찾는 how-to는 4C/ID에서 매뉴얼·빠른 참조로 전달하는 절차 정보에 해당한다. 그래서 별도 유형 대신 참조형의 레시피로 흡수했다.

## 결과

유형은 두 질문(공부 중인가 일하는 중인가, 마친 증거가 이해인가 수행 결과인가)으로 정한다(`.guide/01_scope.md`). `03_outline.md`의 섹션 구조에는 절마다 역할 열이 있다. 목적별 레시피는 참조형이므로 연습을 생략할 수 있지만 결과 확인 방법은 있어야 한다.

## 근거

- Diátaxis, [The compass](https://diataxis.fr/compass/), [Tutorials and how-to guides](https://diataxis.fr/tutorials-how-to/)
- OASIS DITA 1.3, [Information typing](https://docs.oasis-open.org/dita/dita/v1.3/cos02/part1-base/archSpec/base/information-typing.html); DITA 1.2, [learningContent](https://docs.oasis-open.org/dita/v1.2/os/spec/langref/learningContent.html)
- R. E. Horn, "Structured Writing as a Paradigm"(1998), "What Kinds of Writing Have a Future?"(2001)
- J. J. G. van Merriënboer, *The Four-Component Instructional Design Model: An Overview of its Main Design Principles*, Maastricht University, 2019
