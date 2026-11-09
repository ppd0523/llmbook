---
title: NixOS-WSL 개발 환경을 Git으로 복원하기 기준 원고 확정
status: final
owner: agent
---

# 기준 원고 확정

## 기준 원고의 위치

이 책은 MkDocs 챕터형이므로 챕터 본문이 곧 기준 원고이자 최종 산출물이다. 이 파일은 확정 기록이며 그 자체가 원고는 아니다. 근거는 [adr/0001](../../../adr/0001-chapter-body-is-the-canonical-manuscript.md)이다.

## 확정 목록

- `docs/nixos-wsl-dev-environment/index.md`
- `docs/nixos-wsl-dev-environment/01-mental-model.md`
- `docs/nixos-wsl-dev-environment/02-install-nixos-wsl.md`
- `docs/nixos-wsl-dev-environment/03-repository-architecture.md`
- `docs/nixos-wsl-dev-environment/04-system-configuration.md`
- `docs/nixos-wsl-dev-environment/05-home-manager.md`
- `docs/nixos-wsl-dev-environment/06-language-toolchains.md`
- `docs/nixos-wsl-dev-environment/07-nix-develop.md`
- `docs/nixos-wsl-dev-environment/08-restore-workflow.md`
- `docs/nixos-wsl-dev-environment/09-operations-and-troubleshooting.md`
- 책 자산: `docs/nixos-wsl-dev-environment/assets/`

## 확정 조건 점검

다음을 확인했다.

- 문서마다 `#` 제목 하나, 제목 계층 건너뜀 없음.
- 챕터 파일명 slug와 첫 번째 `#` 제목이 같은 주제를 가리킨다.
- 내부 링크는 대상 `.md` 상대 경로다.
- 코드블록에 언어 식별자가 있다.
- 본문에 내부 메모와 `TODO`, `검증 필요`, `출처 필요` 표시가 없다.
- `python -m mkdocs build --strict` 통과.
