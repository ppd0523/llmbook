---
title: Home Manager 가이드 퇴고 범위
updated: 2026-08-11
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

## 범위

- 포함: NixOS 26.05, Home Manager 26.05, Flake 기반 standalone 구성, zsh·Git·direnv, 사용자 파일, 업데이트와 문제 해결.
- 제외: 비밀 관리, Neovim·NVM의 전체 구성, 프로젝트별 언어 런타임, Home Manager의 NixOS 모듈 방식 상세 설정.
- 기준 원고: MkDocs 챕터형 Markdown.
- 최종 산출물: `docs/home-manager-guide/index.md` 및 `01-mental-model.md`부터 `06-troubleshooting.md`까지의 챕터 파일.

## 성공 기준

- 모든 명령의 output 이름과 적용 계층이 명확하다.
- 버전 의존 설명에는 26.05 기준과 공식 출처가 있다.
- 예제만으로 안전한 변경·검증·복구 흐름을 수행할 수 있다.
