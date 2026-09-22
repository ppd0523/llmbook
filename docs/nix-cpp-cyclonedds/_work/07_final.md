---
title: 기준 원고 확정
version: 1.0
status: final
owner: agent
updated: 2026-09-22
target_reader: C++와 Linux 명령을 조금 써 봤지만 빌드 시스템과 교차 컴파일을 직접 구성해 본 적 없는 개발자
topic: Nix·Conan·CMake로 만드는 Cyclone DDS C++ 교차 개발 환경
---

# 기준 원고 확정

## 1. 기준 원고의 위치

이 책은 MkDocs 챕터형이므로 챕터 본문이 곧 기준 원고이자 최종 산출물이다. 근거는 [adr/0001](../../../adr/0001-chapter-body-is-the-canonical-manuscript.md)이다. 이 파일은 확정 기록이며 그 자체가 원고는 아니다.

## 2. 확정 목록

- `docs/nix-cpp-cyclonedds/index.md`
- `docs/nix-cpp-cyclonedds/01-toolchain-mental-model.md` … `10-troubleshooting.md` (10개 챕터)
- 예제: `docs/nix-cpp-cyclonedds/assets/cyclonedds-cross-demo/`

## 3. 확정 조건 점검

- 문서마다 `#` 제목 하나, 제목 계층 건너뜀 없음.
- 챕터 파일명 slug와 첫 번째 `#` 제목이 같은 주제를 가리킨다. `index.md`의 읽는 순서 항목도 각 챕터 H1과 일치한다.
- 내부 링크는 대상 `.md` 상대 경로다.
- 코드블록에 언어 식별자가 있다.
- 본문에 `TODO`, `검증 필요`, `출처 필요` 표시가 없다.
- 버전 기준은 `index.md` 프런트매터의 baseline과 같다. Nixpkgs 26.05, Conan 2.28, Cyclone DDS 0.10.2, spdlog 1.17.0.
