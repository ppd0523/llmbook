---
title: Home Manager 가이드 기술 검토
updated: 2026-08-11
---

# 검토 결과

## 확인한 항목

- `homeConfigurations.<name>`과 `home-manager --flake .#<name>`의 대응: 확인.
- `extraSpecialArgs`, `follows`, `flake.lock`, `stateVersion` 설명: 공식 26.05 문서와 대조.
- `home.file`, `xdg.configFile`, `recursive`, `force`, out-of-store symlink 설명: 공식 파일 관리 문서와 대조.
- `home-manager switch --rollback`: 25.11부터 제공됨을 확인.
- 5장의 bootstrap command: 이 저장소의 example-config `apps.<system>.home-manager`와 대조.

## 반영할 수정

1. recursive link의 overlap 결과를 구체화하고 겹치지 않도록 권고한다.
2. rollback 명령의 최소 Home Manager version을 적는다.
3. 전체 update만 제시하지 않고 input 이름을 지정한 update도 제시한다.
4. Flake의 experimental 상태와 사용 중인 lock 기준 확인을 명시한다.
