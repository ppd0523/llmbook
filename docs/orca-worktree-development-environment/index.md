---
title: Orca 워크트리 개발환경: uv와 nvm으로 의존성 관리
updated: 2026-09-27
---

# Orca 워크트리 개발환경: uv와 nvm으로 의존성 관리

Orca에서 여러 에이전트를 병렬로 실행하면 각 작업은 독립된 Git worktree를 사용한다. 새 작업 폴더에는 이전 폴더의 `.venv`나 `node_modules`가 없으므로 의존성을 다시 준비해야 한다. 이때 실제 네트워크 다운로드와 로컬 캐시에서 설치 결과를 구성하는 작업을 구별해야 준비 시간을 줄일 수 있다.

이 책은 macOS에서 **Orca 데스크톱 IDE**, **uv 프로젝트**, **nvm과 npm**을 사용한다. Git·Python·Node.js 프로젝트 경험이 있지만 worktree와 Orca는 처음인 개발자를 대상으로 한다. Git·uv·nvm의 기본 목적은 알고 있다고 가정한다. 기존 [NixOS-WSL 책의 언어 도구 챕터](../nixos-wsl-dev-environment/06-language-toolchains.md)와 [Hermes Agent 책의 병렬 작업 챕터](../hermes-agent-guide/05-multi-agent-operations.md)는 선택 읽기 자료다.

## 이 책을 마치면

- Python과 Node.js 예제를 각각 Git 저장소로 준비하고 잠금 파일을 추적한다.
- Orca setup hook으로 새 워크트리의 환경을 준비한다.
- 같은 잠금 파일을 쓰는 여러 작업과 의존성이 달라진 브랜치를 동시에 검증한다.
- 캐시 재사용, 설치 결과 구성, 새 다운로드의 시간을 구별한다.
- 공유 `.venv`·`node_modules`가 병렬 작업에 미치는 영향을 판단하고 워크트리를 정리한다.
- Git 무시 도구 스크립트와 `.env`의 복사·공유·로드 방식을 선택한다.

## 환경과 범위

실습은 **Python 3.14 계열**, **Node.js v24 계열(LTS)**, `uv`, `nvm`, npm, Git, Orca가 이미 설치된 macOS에서 시작한다. Node v24의 LTS 상태는 2026-09-27의 [Node.js 릴리스 표](https://nodejs.org/en/about/previous-releases)를 기준으로 한다. `.python-version`의 `3.14`와 `.nvmrc`의 `24`는 패치 버전까지 고정하지 않는다. 예제의 패키지 버전은 `uv.lock`과 `package-lock.json`으로 고정한다. 실제 실행 결과에는 독자의 패치 버전과 도구 버전이 영향을 줄 수 있다. Orca UI 경로는 2026-09-27의 공식 문서, CLI 옵션은 로컬 Orca 1.4.214를 기준으로 확인했다. 메뉴 이름이 달라졌다면 [Orca 공식 문서](https://www.onorca.dev/docs/)를 우선 확인한다.

도구 자체의 설치 절차, Rust 빌드, pnpm·Yarn 실습, 포트·데이터베이스·비밀 설정은 다루지 않는다. `fnm`은 `nvm`과 다른 동작을 비교하는 범위에서만 설명한다. Linux·Windows 차이도 필요한 지점에서 짧게 표시한다.

## 읽는 순서

1. [워크트리와 의존성 경계](./01-worktree-and-cache-boundaries.md)
2. [두 예제 프로젝트 준비](./02-prepare-projects.md)
3. [uv 환경과 캐시 재사용](./03-uv-across-worktrees.md)
4. [nvm·npm과 작업별 node_modules](./04-nvm-npm-across-worktrees.md)
5. [Orca 병렬 작업과 setup hook](./05-orca-parallel-worktrees.md)
6. [준비 시간 측정과 문제 해결](./06-measure-and-troubleshoot.md)

처음 실습할 때는 1장부터 순서대로 읽는다. 이미 두 예제 저장소를 만들었다면 3장부터 시작해도 된다.

[1장: 워크트리와 의존성 경계 →](./01-worktree-and-cache-boundaries.md)
