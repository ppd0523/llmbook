---
title: Home Manager 가이드 기술 검토
---

# 검토 결과

## 확인한 항목

- `homeConfigurations.<name>`과 `home-manager --flake .#<name>`의 대응: 확인.
- `extraSpecialArgs`, `follows`, `flake.lock`, `stateVersion` 설명: 공식 26.05 문서와 대조.
- `home.file`, `xdg.configFile`, `recursive`, `force`, out-of-store symlink 설명: 공식 파일 관리 문서와 대조.
- `home-manager switch --rollback`: 25.11부터 제공됨을 확인.
- 5장의 bootstrap command: 이 저장소의 example-config `apps.<system>.home-manager`와 대조.
