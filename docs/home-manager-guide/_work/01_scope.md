---
title: Home Manager 가이드 퇴고 범위
---

# 범위 정의

## 독자 상태 진단

- 대상 독자는 이 저장소의 NixOS-WSL 개발 환경 매뉴얼을 끝내고, Flake와 Git의 기본 흐름을 아는 NixOS 사용자다.
- 독자는 `nixos-rebuild`, `home-manager build`, Git의 staging area를 처음부터 설명받을 필요는 없지만, NixOS와 Home Manager의 소유권 및 generation의 차이는 새로 익혀야 한다.
- 특히 로그인 shell, Home Manager의 파일 소유권, `flake.lock`과 `home.stateVersion`을 혼동하기 쉽다.

## 중심 질문과 학습 목표

중심 질문은 "Flake 기반 standalone Home Manager로 사용자 환경을 어떻게 선언하고, 검증·적용·복구할 것인가?"다.

독자는 이 자료를 읽은 뒤 다음을 할 수 있어야 한다.

1. 시스템·사용자·프로젝트 설정의 소유권을 구분한다.
2. Home Manager 모듈과 dotfile을 겹치지 않게 배치한다.
3. 변경을 `build`로 검증한 뒤 `switch`로 적용하고, 문제가 생기면 적절한 generation을 롤백한다.

## 자료 유형

| 장 | 유형 | 판단 근거 |
|---|---|---|
| 1. 역할과 경계 | 개념형 | 마친 증거가 계층 배정과 버전 축 구분이라는 판단이다 |
| 2. Flake와 모듈 구조 | 개념형 | output 이름에서 명령을 만들고 오류 원인을 설명하는 것이 증거다 |
| 3. 패키지와 프로그램 | 실습형 | 새 shell에서 확인되는 도구·변수·Git 설정이 증거다 |
| 4. 옵션과 dotfiles | 개념형 | 배치 방식 선택과 겹친 선언의 결과 예측이 증거다. 실제 충돌 재현은 독자 홈을 바꾸므로 판단 문제로 둔다 |
| 5. 빌드·적용·롤백 | 실습형 | generation 목록과 명령 결과가 증거다 |
| 6. 문제 해결 | 참조형 | 오류를 만난 작업 중에 펴는 장이다. 학습 목표 1과 대응하도록 짧은 진단 연습을 둔다 |

## 범위

- 포함: NixOS 26.05, Home Manager 26.05, Flake 기반 standalone 구성, zsh·Git·direnv, 사용자 파일, 업데이트와 문제 해결.
- 제외: 비밀 관리, Neovim·NVM의 전체 구성, 프로젝트별 언어 런타임, Home Manager의 NixOS 모듈 방식 상세 설정.
- 기준 원고: MkDocs 챕터형 Markdown.
- 최종 산출물: `docs/home-manager-guide/index.md` 및 `01-mental-model.md`부터 `06-troubleshooting.md`까지의 챕터 파일.

## 성공 기준

- 모든 명령의 output 이름과 적용 계층이 명확하다.
- 버전 의존 설명에는 26.05 기준과 공식 출처가 있다.
- 예제만으로 안전한 변경·검증·복구 흐름을 수행할 수 있다.
- 1~5장의 문제와 6장의 진단 연습마다 접힌 정답·해설 또는 기대 출력이 있다.
