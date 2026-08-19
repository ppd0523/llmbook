---
title: 출판 전 최종 Markdown 원고 인덱스
version: 1.1
status: final
owner: agent
updated: 2026-08-19
target_reader: Nix 지식이 없는 개발자와 NixOS·Home Manager 입문자
topic: Nix 첫걸음
---

# Nix 첫걸음: 출판 전 기준 원고

이 책의 최종 Markdown 기준 원고는 MkDocs 챕터형으로 확정했다. 원고는 다음 파일로 구성하며, 각 파일은 독립적인 `#` 제목과 학습 흐름을 가진다.

1. `../index.md` — 대상, 전제 조건, 학습 경로
2. `../01-ecosystem-and-mental-model.md` — 생태계와 공통 작업 흐름
3. `../02-language-basics.md` — Nix 언어의 최소 문법
4. `../03-store-builds-and-generations.md` — Store, derivation, profile, generation
5. `../04-shells-and-packages.md` — 패키지 사용과 셸 선택
6. `../05-module-system.md` — NixOS·Home Manager module system
7. `../06-nixos-and-home-manager.md` — 설정 계층과 적용·복구
8. `../07-guided-lab.md` — 잠긴 개발 셸 통합 실습
9. `../08-troubleshooting-and-next-steps.md` — 문제 해결과 후속 학습

## 최종 원고 확인

- [x] 학습 목표, 본문, 예제와 연습이 장별로 대응한다.
- [x] Nix 2.34.9, NixOS/Nixpkgs 26.05, Home Manager 26.05의 기준을 표시한다.
- [x] 내부 작업 메모, `TODO`, `검증 필요`, `출처 필요` 표시는 최종 챕터에 없다.
- [x] 새 용어는 사용 전에 설명하고 같은 개념을 같은 표기로 쓴다.
- [x] 장 사이 링크는 상대 `.md` 경로를 사용한다.
