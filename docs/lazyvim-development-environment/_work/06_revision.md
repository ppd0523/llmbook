---
title: LazyVim 개발 환경 가이드 퇴고 기록
status: reviewed
owner: agent
target_reader: 터미널, Git, vi 기초를 알고 LazyVim은 처음인 개발자
topic: LazyVim 다중 언어 개발 환경의 구조와 학습성 개선
---

# LazyVim 개발 환경 가이드 퇴고 기록

## 1. 퇴고 목표

- 구조 개선: 모든 language chapter를 역할, 준비, 설정, 검증, 문제 해결 순서로 통일한다.
- 학습성 개선: command만 나열하지 않고 각 command가 검사하는 계층을 설명한다.
- 누락 보강: rollback, lockfile, WSL 특이 문제, project-local runtime을 보강한다.
- 중복 제거: 공통 keymap과 Mason 설명은 3장에 모으고 language chapter는 차이만 설명한다.
- 예제 개선: 각 language에서 일부러 오류를 만들고 LSP/formatter/debugger를 각각 관찰한다.
- 연습문제 개선: 최종 문제를 layered diagnosis와 restore에 대응시킨다.

## 2. 구조 결정

| 위치 | 구성 | 이유 |
|---|---|---|
| 1장 | 제품 이름보다 요청 흐름과 ownership 표를 먼저 제시한다. plugin/executable/project 3계층보다 상세한 5계층 모델을 쓴다. | 제품 이름이 먼저 나오면 전체 구조가 보이지 않는다. 5계층은 LSP와 DAP 실패 위치를 정확히 구분한다. |
| 2장 | health baseline, backup, rollback을 설치와 같은 장에 둔다. | 화면 표시만으로는 설치 성공을 판단할 수 없고, 설치를 복구 가능한 작업으로 만든다. |
| 3장 | official starter 기반 완성 config(`assets/example-config`)와 언어별 matrix를 한곳에 둔다. | extra와 package 목록이 흩어지지 않고 복사와 비교가 가능하다. |
| 4장 | Node direct launch와 TS runtime PATH를 분리하고, `PATH`에 project-local `tsx`를 노출한다. ESLint format은 끄고(options와 4장) Prettier가 formatting을 맡는다. | JS와 TS의 debug 조건이 다르고, TypeScript default launch에는 `tsx`가 필요하다. Prettier와 formatting owner가 충돌하지 않는다. |
| 5장 | adapter Python과 project Python을 명시적으로 구분하고 `.venv` activation과 VenvSelect를 쓴다. | Python process가 두 개이며, LSP와 debugger의 interpreter가 일치해야 한다. |
| 6장 | LSP fallback과 rustfmt component를 함께 설명하고 `<leader>dr`의 `Rust Debuggables` workflow를 쓴다. | Rust formatting source가 드러나지 않으며, generic DAP config보다 Cargo target에 적합하다. |
| 7장 | Compiler·CMake 준비와 `compile_commands.json`·Debug build 생성을 clangd·CodeLLDB 확인보다 먼저 두고, formatting은 clangd에 내장된 clang-format과 project `.clang-format`에 맡긴다. | clangd 실행 파일만으로는 실제 compile option을 알 수 없어 정확한 diagnostics와 navigation을 얻지 못하고, format owner는 하나로 둔다. |
| 8장 | 증상별 해결책보다 고정된 계층 진단 순서를 먼저 제시한다. | 증상별 해결책만 있으면 암기식이 된다. |
| 1장(1.7)과 8장(8.9) | WSL path·clipboard·binary 주의사항을 둔다. | `01_scope.md`의 운영체제 경계에 따라 WSL에서만 생기는 문제는 별도 주의사항으로 다룬다. |

## 3. 구조 점검

- [x] 문제 제기가 학습 목표와 연결된다.
- [x] 직관 예시가 세부 구성보다 먼저 제공된다.
- [x] 추상 계층 뒤에 다섯 언어 사례가 나온다.
- [x] 섹션 순서가 개념 의존성과 맞는다.
- [x] OS 설치 세부 같은 범위 밖 설명이 없다.

## 4. 학습성 점검

- [x] 학습목표와 본문이 대응한다.
- [x] 각 핵심 개념 뒤에 확인 command가 있다.
- [x] 추상 계층과 구체 증상이 연결된다.
- [x] 연습문제가 본문 내용만으로 풀린다.
- [x] 흔한 오해와 실패 사례가 포함된다.
- [x] worked smoke test와 직접 풀이 문제가 함께 배치된다.

## 5. 교정 전 확인

- [x] 기술 검증에서 나온 수정 사항을 반영했다.
- [x] 최종 산출물에 남기면 안 되는 불확실한 단정을 제거했다.
- [x] 출처 필요 항목을 처리했다.
- [x] 표와 코드의 위치를 확정했다.
