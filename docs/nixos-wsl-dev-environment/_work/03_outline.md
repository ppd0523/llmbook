---
title: 구성 설계
version: 1.1
status: final
owner: agent
updated: 2026-07-15
target_reader: 터미널 기반 개발 환경에 익숙하지만 Nix 생태계는 처음인 시니어 개발자
topic: NixOS-WSL과 네이티브 NixOS에서 재현 가능한 개발 환경 구축
---

# 구성 설계

## 1. 자료의 한 문장 요약

- NixOS는 호스트를, 독립 실행형 Home Manager는 사용자를, dotfiles는 개별 프로그램 설정을 담당하게 하고 Flake로 입력과 출력을 묶어 한 Git 저장소에서 WSL과 네이티브 NixOS 환경을 복원한다.

## 2. 중심 질문

이 자료는 다음 질문에 답한다.

- 하나의 Git 저장소에서 시스템 설정과 사용자 설정을 분리하면서 NixOS-WSL과 네이티브 NixOS의 개발 환경을 어떻게 재현하는가?

## 3. 학습 흐름

```text
역할 구분
-> NixOS-WSL과 최초 구성 저장소 준비
-> 저장소와 Flake 설계
-> 시스템 모듈 분리
-> 사용자 환경과 dotfiles 구성
-> 언어 툴체인 경계 설정
-> nix develop·direnv와 LazyVim 실전 연결
-> 새 호스트 복원
-> 업데이트·롤백·복구
```

## 4. 섹션 구조

| 번호 | 챕터 제목 | 중심 질문 | 필요한 선행개념 | 산출되는 이해 |
|---|---|---|---|---|
| 1 | Nix 생태계의 역할과 경계 | NixOS, Flake, Home Manager, dotfiles는 무엇을 소유하는가? | 일반 패키지·dotfiles 경험 | 설정을 올바른 계층에 배치한다. |
| 2 | 처음부터 NixOS-WSL과 구성 저장소 만들기 | WSL과 개인 GitHub 저장소가 모두 없을 때 원본 구성을 어떻게 만드는가? | Windows 터미널, Git 기본 사용 | WSL 설치, 빈 원격 저장소, SSH 인증, 첫 lock·push를 완료한다. |
| 3 | Flake 저장소 구조 설계 | 여러 호스트와 한 사용자 환경을 어떻게 조립하는가? | 1장 역할 구분 | 입력, 출력, 공통 모듈, 호스트 모듈을 읽는다. |
| 4 | 시스템 설정 분리 | WSL과 네이티브 NixOS의 차이를 어디에 격리하는가? | NixOS 모듈, `imports` | 공통 시스템과 호스트 전용 설정을 구현한다. |
| 5 | 독립 실행형 Home Manager와 dotfiles | 시스템 rebuild 없이 사용자 환경을 어떻게 재현하는가? | Home Manager 역할 | CLI 도구, zsh, Neovim 설정을 사용자 단위로 적용한다. |
| 6 | uv·nvm·rustup 툴체인 | Nix가 관리자만 고정할 때 프로젝트 버전은 어떻게 재현하는가? | Flake 잠금, PATH | 세 언어의 프로젝트 파일과 자동 설치 흐름을 구성한다. |
| 7 | nix develop·direnv와 LazyVim | 프로젝트 환경과 plugin 구성을 어떻게 자동 활성화하고 격리하는가? | 5장 사용자 도구, 6장 언어 관리자 | `.lazy.lua`·plugin lock과 세 언어 LSP를 프로젝트가 소유한다. |
| 8 | 새 환경 복원 절차 | 복제한 저장소를 어떤 순서로 적용하고 확인하는가? | 앞 장의 완성형 구성 | WSL과 native에서 시스템·사용자 구성을 복원한다. |
| 9 | 업데이트·롤백·문제 해결 | 변경을 어떻게 안전하게 검증하고 되돌리는가? | generation, lock file | 빌드·적용·갱신·복구 루프를 운영한다. |

## 5. 개념 의존성

| 개념 | 먼저 알아야 할 개념 | 이 개념 뒤에 설명할 내용 |
|---|---|---|
| Nix Store와 generation | 패키지 관리자 | rebuild, switch, rollback |
| NixOS module | Nix 속성 집합과 함수의 최소 문법 | 공통·호스트 모듈 |
| Flake input/output | NixOS와 Home Manager의 책임 | `nixosConfigurations`, `homeConfigurations` |
| 독립 실행형 Home Manager | 사용자·시스템 경계 | 사용자 패키지, 홈 파일, 별도 세대 |
| dotfiles 배치 | Home Manager 파일 옵션 | Neovim Lua 설정 |
| 언어 관리자 2계층 모델 | Flake 잠금과 홈의 가변 상태 | uv·nvm·rustup 프로젝트 복원 |
| 프로젝트 개발 셸 | Flake와 언어 관리자 경계 | direnv 자동 로드, LazyVim PATH 상속 |
| LazyVim local spec | Home Manager 공통 기반 | 프로젝트 plugin spec·lock·cache와 trust |
| nix-ld | NixOS의 비표준 파일시스템 | 외부 배포 런타임 실행 |

## 6. 예제 계획

| 예제 | 위치 | 보여줄 개념 | 입력 | 기대 결과 |
|---|---|---|---|---|
| 책임 분류표 | 1장 | 계층 판단법 | Git, zsh, WSL, Neovim 설정 사례 | 각 항목의 소유자를 구분한다. |
| NixOS-WSL과 최초 저장소 | 2장 | Windows·게스트·GitHub의 bootstrap 경계 | `nixos.wsl`, 예제 구성 | NixOS 셸, GitHub 원격, 첫 `flake.lock`과 push 확인 |
| 전체 `flake.nix` | 3장 | 입력·출력 조립 | nixpkgs, NixOS-WSL, Home Manager, nvm | 두 시스템과 한 사용자 출력 생성 |
| 공통·호스트 모듈 | 4장 | 모듈 재사용 | common, wsl, native | WSL 차이가 사용자 구성으로 새지 않음 |
| Home Manager 모듈 | 5장 | 사용자 도구와 설정 | 프로그램 모듈과 dotfiles | 동일한 홈 환경 생성 |
| 세 프로젝트 파일 | 6장 | 언어 버전 고정 | `.python-version`, `.nvmrc`, `rust-toolchain.toml` | 누락 런타임 자동 설치 |
| LazyVim 언어별 개발 셸 | 7장 | Nix·언어 lock·plugin lock 경계 | 세 프로젝트 Flake, `.envrc`, `.lazy.lua` | plugin과 LSP가 프로젝트 단위로 격리 |
| 복원 체크리스트 | 8장 | 적용 순서와 검증 | Git 저장소 | 시스템과 홈 구성을 독립 적용 |
| 실패 복구 | 9장 | 세대와 WSL recovery | 잘못된 설정 | 이전 구성으로 복귀 |

## 7. 연습문제 계획

| 문제 | 유형 | 검증할 학습목표 | 난이도 |
|---|---|---|---|
| 설정 항목 10개를 네 계층으로 분류한다. | 비교 | 역할 구분 | 낮음 |
| 두 번째 WSL 호스트 모듈을 추가한다. | 변형 | 모듈 설계 | 중간 |
| Neovim dotfile을 변경하고 사용자 구성만 적용한다. | 추적 | 독립 활성화 | 낮음 |
| 세 언어 프로젝트의 고정 파일을 작성하고 버전을 확인한다. | 구현 | 툴체인 경계 | 중간 |
| 각 프로젝트에서 `nix develop`과 direnv의 PATH가 같은 LSP를 가리키는지 확인한다. | 진단 | 개발 셸과 LazyVim 연결 | 중간 |
| 잘못된 Home Manager 변경을 이전 세대로 되돌린다. | 디버깅 | 롤백 | 중간 |
| 네이티브 NixOS에서 하드웨어 파일만 교체해 공통 홈을 적용한다. | 설계 | 호스트 이식 | 높음 |

## 8. 그림, 표, 코드 계획

| 자료 | 위치 | 목적 | 필요한 정확성 검증 |
|---|---|---|---|
| 계층 흐름 그림 | 1장 | Flake에서 시스템과 사용자 출력으로 갈라지는 관계 표시 | 출력 이름과 적용 범위 |
| 책임 판정표 | 1장 | 설정 소유자 선택 | NixOS/Home Manager 경계 |
| 저장소 트리 | 3장 | 최종 파일 구조 제시 | 실제 assets 구조와 일치 |
| 전체 Flake 코드 | 3장 | 입력과 출력 연결 | 속성명과 함수 인자 |
| NixOS 모듈 코드 | 4장 | common·WSL·native 분리 | 옵션명과 `stateVersion` 위치 |
| Home Manager 코드 | 5장 | 프로그램과 홈 파일 선언 | 26.05 옵션명 |
| nvm zsh 훅 | 6장 | `.nvmrc` 자동 설치·전환 | 함수 로드 순서와 쓰기 경로 |
| 세 언어 LazyVim 경로표 | 7장 | 언어별 LSP 소유권 비교 | `command -v`, `:LspInfo` 결과 |
| 운영 명령표 | 9장 | build/test/switch/rollback 구분 | 공식 CLI 동작 |

## 9. 위험 구간

- 설명이 어려운 부분: Flake는 구성 내용이 아니라 입력과 출력을 묶는 진입점이라는 점
- 오해가 잦은 부분: `stateVersion`을 패키지 버전 또는 업데이트 목표로 보는 오해
- 추가 그림이 필요한 부분: NixOS와 Home Manager의 독립 세대, Flake 출력의 분기
- 예제 없이 설명하면 위험한 부분: nvm 소스는 불변이지만 `$NVM_DIR`의 런타임 상태는 쓰기 가능해야 한다는 점
- 예제 없이 설명하면 위험한 부분: LazyVim은 실행된 셸의 PATH를 상속하므로 프로젝트 밖에서 열면 해당 LSP를 보지 못한다는 점
- 보안 위험: `.envrc` 승인과 `.lazy.lua`의 Neovim trust는 별도의 신뢰 절차다.
- 기술 위험: uv·nvm·rustup이 받은 일반 Linux 바이너리는 nix-ld 또는 추가 라이브러리가 필요할 수 있다.
- 이식 위험: 네이티브 호스트의 `hardware-configuration.nix`와 기존 `system.stateVersion`은 다른 호스트에서 복사하지 않는다.
- 검증 위험: 현재 작성 환경에 Nix와 설치된 WSL 배포판이 없어 Nix 평가를 직접 실행할 수 없다.

## 10. 품질 점검

- [x] 섹션 순서가 학습자의 선행지식 흐름과 맞는다.
- [x] 새 용어가 정의 없이 먼저 등장하지 않는다.
- [x] 각 핵심 개념에 예제 또는 확인 질문이 대응된다.
- [x] 최종 연습문제가 학습 목표와 대응된다.
