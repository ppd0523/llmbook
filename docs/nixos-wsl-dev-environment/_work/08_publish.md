---
title: 최종 산출물 구성과 출판 변환 검수
status: complete
owner: agent
target_reader: 터미널과 언어별 버전 관리에는 익숙하지만 Nix는 처음인 시니어 개발자
topic: Flake와 독립 실행형 Home Manager를 이용한 이식 가능한 NixOS 개발 환경
---

# 최종 산출물 구성과 출판 변환 검수

## 1. 최종 산출물

- 목차: `index.md`
- 본문: 책 폴더 바로 아래의 `NN-<chapter-slug>.md` 챕터 파일 9개
- 기준 원고: 9개 챕터 본문 자체([adr/0001](../../../adr/0001-chapter-body-is-the-canonical-manuscript.md)). `_work/07_final.md`는 이를 확정한 기록이다.
- 복제 가능한 사용자·시스템 구성: `assets/example-config/`
- Python·Node.js·Rust 프로젝트 환경: `assets/example-dev-shell/`
- 사이트 구성: 저장소 루트의 `mkdocs.yml`
- 공개 URL: 챕터 파일명 기준(`/nixos-wsl-dev-environment/01-mental-model/`)이다. 옛 `/nixos-wsl-dev-environment/01_mental_model/chapter/` 형식 URL은 살리지 않는다. 리다이렉트를 넣지 않고 `requirements.txt`의 고정 목록에 `mkdocs-redirects`도 두지 않으므로, 그 경로로 들어오는 링크는 404가 된다.

## 2. 공통 검수

- [x] `index.md`의 읽는 순서 아홉 항목이 01~09 챕터 파일에 각각 연결되고, 읽기 순서 번호 01~09가 중복 없이 한 번씩 쓰인다.
- [x] 챕터 사이 이전·다음 링크와 목차 링크, 챕터의 `assets/` 링크가 현재 파일을 가리킨다.
- [x] `docs/home-manager-guide/06-troubleshooting.md`의 교차 링크가 9장을, 두 예제 asset README의 챕터 링크가 현재 챕터 파일을 가리킨다.
- [x] 각 챕터에 코드 블록 밖 H1이 하나만 있다.
- [x] Markdown 코드 펜스가 모두 짝을 이룬다.
- [x] 깨진 상대 링크가 없다.
- [x] 최종 사용자 문서에 미완료 작업 표지가 없다.
- [x] 시스템, 사용자, 프로젝트 설정의 소유권 표와 예제가 일치한다.
- [x] `.envrc`와 `.lazy.lua`의 별도 신뢰 절차가 복원·운영 장에도 연결된다.
- [x] 3.1절 이후 구조·파일 내용 코드 블록마다 기준 루트, 경로, 전체/일부 여부가 표시된다.
- [x] 5.2장의 `programs.nix` 전체 코드가 companion asset과 일치한다.
- [x] MkDocs strict build가 통과한다.

## 3. 예제 구성 검수

- [x] `modules/home/lazyvim.nix`가 Neovim, lazy.nvim, 공통 요구사항만 제공한다.
- [x] `init.lua` 생성과 `lua/`·`stylua.toml`·기본 lock 링크의 소유권이 겹치지 않는다.
- [ ] standalone Home Manager 구성이 실제 NixOS-WSL에서 정상 평가된다: 평가를 통과한 구성이지만 현재 파일 기준으로 다시 확인하지 않았다(`_work/05_review.md` 4절).
- [x] 공통 Neovim 설정에서 Mason을 비활성화한다.
- [x] 프로젝트 `.lazy.lua`가 Python, TypeScript, Rust extra를 각각 선택한다.
- [x] 세 프로젝트 모두 `.lazy-lock.json`을 추적 대상으로 제공한다.
- [x] 프로젝트별 plugin root와 lockfile 경로가 함께 분리된다.
- [x] Python은 uv, Node.js는 NVM, Rust는 rustup이 언어 버전을 소유한다.
- [x] `flake.nix`는 언어 런타임을 중복 선언하지 않고 네이티브 의존성만 제공한다.
- [x] `.direnv`, `.venv`, `node_modules`, `target` 등 생성 상태는 Git에서 제외한다.
- [x] JSON, TOML, Nix 괄호 정적 검사가 통과한다.

## 4. 출판 검사 결과

현재 본문과 예제 기준 결과다. 검사 항목의 세부 범위는 `_work/05_review.md` 4절에 있다.

| 검사 | 결과 |
|---|---|
| Markdown | 20개 UTF-8 읽기·코드 펜스·상대 링크 통과 |
| Chapter | 9개 H1 구조 통과 |
| JSON | 6개 파싱 통과 |
| TOML | 4개 파싱 통과 |
| Nix | 12개 괄호 수 정적 검사 통과 |
| Git diff | `git diff --check` 통과 |
| MkDocs | strict build 통과 |

## 5. 실행 환경 한계

작성 호스트에는 Nix와 Neovim이 없다. standalone Home Manager 구성은 실제
NixOS-WSL에서 평가를 통과한 구성이지만 현재 파일 기준으로 다시 확인하지 않았다.
NixOS 전체 build, Home Manager switch, Lua runtime 검증 범위와 실제 환경에서 실행할
명령은 `_work/05_review.md`와 본문의 각 실습에 남겼다. 2.8절 예제 복사 명령
`cp -R . ~/.config/nixos`는 예제 README의 `~/.config/nixos` 복사 설명과, 5장
`nix run .#home-manager -- switch --flake .#nixos` bootstrap 명령은 3장의
`apps.${system}.home-manager` 출력과 예제 README 명령과 문자열 대조로만 맞췄다. 실제
실행 검증은 대상 NixOS-WSL에서 수행해야 한다. 상태를 바꾸는 전환보다 `build`를 먼저 수행하며, 프로젝트 플러그인은 최초
`:Lazy sync` 후 생성된 `.lazy-lock.json` diff를 검토한다.

## 6. 최종 결론

- 배포 대상은 `index.md`, 9개 챕터, 두 예제 asset 디렉터리다.
- Home Manager는 최소 LazyVim 기반을, 각 프로젝트는 `.lazy.lua`와
  `.lazy-lock.json`을 소유한다.
- Neovim 설정의 경로별 소유권 분리는 실제 NixOS-WSL의 Home Manager 평가를 통과한
  구성이며, 현재 파일 기준 재평가는 하지 않았다.
- Markdown 사이트는 MkDocs strict build 기준으로 출판 가능하다.
- NixOS와 Neovim 실행 검증은 실제 대상 환경에서 완료해야 한다.
