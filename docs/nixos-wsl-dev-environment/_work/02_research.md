---
title: 조사 노트
version: 1.3
status: final
owner: agent
updated: 2026-07-21
target_reader: 터미널 기반 개발 환경에 익숙하지만 Nix 생태계는 처음인 시니어 개발자
topic: NixOS-WSL과 네이티브 NixOS에서 재현 가능한 개발 환경 구축
---

# 조사 노트

## 1. 핵심 출처

| 구분 | 제목/문서 | 링크/서지 | 사용할 내용 | 신뢰도 | 비고 |
|---|---|---|---|---|---|
| 공식 발표 | NixOS 26.05 released | https://nixos.org/blog/announcements/2026/nixos-2605/ | 2026-07-14 현재 안정 버전과 지원 기간 | 높음 | 예제 기준 버전은 26.05 |
| 공식 문서 | NixOS Manual 26.05 | https://nixos.org/manual/nixos/stable/ | 모듈, 시스템 적용, 사용자, 롤백 | 높음 | 시스템 계층의 기준 |
| 공식 문서 | Flakes | https://nix.dev/concepts/flakes.html | `flake.nix` 입력·출력과 `flake.lock` | 높음 | Flake 개념의 기준 |
| 공식 문서 | Nix flake reference | https://nix.dev/manual/nix/latest/command-ref/new-cli/nix3-flake.html | 로컬 Git Flake와 추적 파일의 동작 | 높음 | 미추적 파일 누락 설명 |
| 공식 문서 | NixOS-WSL Installation | https://nix-community.github.io/NixOS-WSL/install.html | `.wsl` 설치, 초기 사용자, WSL 버전별 명령 | 높음 | WSL 2.4.4 전후 구분 |
| 공식 문서 | NixOS-WSL Flake setup | https://nix-community.github.io/NixOS-WSL/how-to/nix-flakes.html | `nixos-wsl.nixosModules.default` 사용법 | 높음 | WSL 호스트 모듈의 기준 |
| 공식 문서 | NixOS-WSL options | https://nix-community.github.io/NixOS-WSL/options.html | `wsl.enable`, `wsl.defaultUser`, 상호운용 옵션 | 높음 | Docker 통합은 제외 |
| 공식 문서 | NixOS-WSL username change | https://nix-community.github.io/NixOS-WSL/how-to/change-username.html | 설치 후 기본 사용자 변경 절차 | 높음 | `boot` 적용과 WSL 재시작 필요 |
| 공식 문서 | NixOS-WSL recovery shell | https://nix-community.github.io/NixOS-WSL/troubleshooting/recovery-shell.html | 잘못된 세대에서 복구하는 방법 | 높음 | WSL 전용 복구 절차 |
| 공식 문서 | Install WSL | https://learn.microsoft.com/windows/wsl/install | WSL이 없는 Windows에서 기능 설치와 재시작 | 높음 | `--no-distribution` 옵션은 basic commands도 확인 |
| 공식 문서 | Basic commands for WSL | https://learn.microsoft.com/windows/wsl/basic-commands | `wsl --install --no-distribution`, 업데이트, 버전 확인 | 높음 | NixOS 등록 전에 WSL만 설치 |
| 공식 문서 | Adding locally hosted code to GitHub | https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github | 빈 원격 저장소, `git init`, remote 연결, 첫 push | 높음 | README·license·gitignore로 초기화하지 않음 |
| 공식 문서 | Generating a new SSH key | https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent?platform=linux | Ed25519 키 생성과 passphrase | 높음 | WSL/Linux 절차 |
| 공식 문서 | Adding a new SSH key to GitHub | https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account?platform=linux | 공개 키를 GitHub 계정에 등록 | 높음 | 개인 키는 등록·커밋하지 않음 |
| 공식 문서 | Testing your SSH connection | https://docs.github.com/en/authentication/connecting-to-github-with-ssh/testing-your-ssh-connection?platform=linux | `ssh -T git@github.com` 검증과 성공 시 종료 코드 1 가능성 | 높음 | 사용자 이름이 성공 메시지에 보여야 함 |
| 공식 문서 | GitHub REST API rate limits | https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api | 비인증 요청은 사용자 대신 공인 IP 기준이며 시간당 60회 | 높음 | SSH 인증과 무관 |
| 공식 문서 | Ad hoc shell environments | https://nix.dev/tutorials/first-steps/ad-hoc-shell-environments.html | `nix-shell -p git`로 채널 기반 임시 도구 셸 생성 | 높음 | Git 없는 최초 bootstrap에 사용 |
| 공식 문서 | Nix `access-tokens` | https://releases.nixos.org/nix/nix-2.31.3/manual/command-ref/conf-file.html#conf-access-tokens | `github.com=token` 형식의 GitHub fetcher 인증 | 높음 | 토큰은 Git에 커밋하지 않음 |
| 공식 문서 | Home Manager introduction | https://nix-community.github.io/home-manager/introduction.html | 사용자 패키지와 홈 파일의 재현 관리 | 높음 | 사용자 계층의 기준 |
| 공식 저장소 | Home Manager README | https://github.com/nix-community/home-manager | 독립 실행형과 NixOS 모듈 방식의 차이 | 높음 | 사용자 요구에 따라 독립 실행형 채택 |
| 공식 소스 | Home Manager 26.05 flake | https://raw.githubusercontent.com/nix-community/home-manager/release-26.05/flake.nix | 26.05 입력과 패키지 출력 확인 | 높음 | nixpkgs 26.05와 맞춤 |
| 공식 소스 | Home Manager CLI 26.05 | https://raw.githubusercontent.com/nix-community/home-manager/release-26.05/home-manager/home-manager | `switch`, `--rollback`, `generations` 동작 | 높음 | 운영 명령 검증 |
| 공식 문서 | Home Manager state version | https://nix-community.github.io/home-manager/installation/nixos.html | `home.stateVersion` 유지 원칙 | 높음 | 업데이트 버전과 혼동 금지 |
| 공식 문서 | Nix-ld | https://wiki.nixos.org/wiki/Nix-ld | Nix 밖에서 받은 ELF 바이너리 실행 | 높음 | uv·nvm·rustup 방식의 필수 보완 |
| 공식 저장소 | nvm README | https://github.com/nvm-sh/nvm | `.nvmrc`, `nvm install`, zsh 자동 전환 | 높음 | v0.40.4를 Flake 입력으로 고정 |
| 공식 문서 | uv Python versions | https://docs.astral.sh/uv/concepts/python-versions/ | `.python-version`과 관리형 Python | 높음 | Python 런타임 관리의 기준 |
| 공식 문서 | uv project layout | https://docs.astral.sh/uv/concepts/projects/layout/ | `pyproject.toml`, `uv.lock`, `.venv` | 높음 | Git에 커밋할 파일 구분 |
| 공식 문서 | uv locking and syncing | https://docs.astral.sh/uv/concepts/projects/sync/ | `uv sync --locked`와 잠금 갱신 | 높음 | 복원 검증 명령 |
| 공식 문서 | rustup concepts | https://rust-lang.github.io/rustup/concepts/ | rustup 프록시와 툴체인 관리 | 높음 | Rust 계층의 기준 |
| 공식 문서 | rustup overrides | https://rust-lang.github.io/rustup/overrides.html | `rust-toolchain.toml` 자동 선택 | 높음 | 정확한 버전·컴포넌트 고정 |
| 공식 문서 | rustup environment variables | https://rust-lang.github.io/rustup/environment-variables.html | 누락 툴체인 자동 설치 | 높음 | `RUSTUP_AUTO_INSTALL=1` 확인 |
| 공식 문서 | Nix develop | https://nix.dev/manual/nix/latest/command-ref/new-cli/nix3-develop.html | Flake `devShell` 활성화와 명령 실행 | 높음 | 수동 검증 경로 |
| 공식 문서 | direnv | https://direnv.net/ | `.envrc` 승인과 디렉터리별 환경 전환 | 높음 | clone 후 신뢰 경계 |
| 공식 저장소 | nix-direnv | https://github.com/nix-community/nix-direnv | `use flake` 캐시와 Flake 변경 감시 | 높음 | direnv 보조 계층 |
| 공식 문서 | LazyVim Installation | https://www.lazyvim.org/installation | starter 구조, 요구 도구, `:LazyHealth` | 높음 | Neovim 0.11.2 이상 기준 |
| 공식 문서 | LazyVim Python extra | https://www.lazyvim.org/extras/lang/python | basedpyright와 Ruff 선택 | 높음 | uv 개발 의존성 사용 |
| 공식 문서 | LazyVim TypeScript extra | https://www.lazyvim.org/extras/lang/typescript | vtsls 선택 | 높음 | npm 프로젝트 의존성 사용 |
| 공식 문서 | LazyVim Rust extra | https://www.lazyvim.org/extras/lang/rust | rustaceanvim과 PATH의 rust-analyzer 사용 | 높음 | rustup component 사용 |
| 공식 문서 | uv Working on projects | https://docs.astral.sh/uv/guides/projects/ | `.venv`, `uv.lock`, `uv sync --locked` | 높음 | LazyVim PATH 연결 |
| 공식 문서 | lazy.nvim configuration | https://lazy.folke.io/configuration | `local_spec`, `root`, `lockfile` 설정 | 높음 | 프로젝트별 plugin 격리 |
| 공식 소스 | lazy.nvim local spec loader | https://github.com/folke/lazy.nvim/blob/main/lua/lazy/core/plugin.lua | 상위 `.lazy.lua` 탐색과 `vim.secure.read()` 사용 | 높음 | 실제 신뢰 동작 확인 |
| 공식 문서 | Neovim trusted files | https://neovim.io/doc/user/editing.html#trust | `:trust`와 내용 hash 기반 신뢰 DB | 높음 | `.lazy.lua` 보안 경계 |

## 2. 핵심 정의

| 용어 | 정의 | 출처 | 본문 표기 | 비고 |
|---|---|---|---|---|
| Nix | 패키지와 구성을 불변 Store 경로에 실현하고 프로필 세대로 활성화하는 도구 및 언어 | NixOS Manual, nix.dev | Nix | NixOS와 구분 |
| Nixpkgs | 패키지 정의와 NixOS 모듈을 제공하는 저장소 | NixOS Manual | Nixpkgs | Flake 입력으로 고정 |
| NixOS | NixOS 모듈을 합성해 운영체제 전체 상태를 선언적으로 구성하는 Linux 배포판 | NixOS Manual | NixOS | 호스트와 시스템 책임 |
| Flake | 표준 형태의 입력과 출력을 선언하고 입력을 잠그는 Nix 코드 진입점 | nix.dev Flakes | Flake | 구성 엔진 자체가 아님 |
| Home Manager | Nix를 이용해 사용자 패키지와 홈 디렉터리 내용을 재현하는 도구 | Home Manager Introduction | Home Manager | 독립 실행형 채택 |
| dotfiles | 프로그램이 직접 읽는 사용자 설정 파일 | Home Manager Introduction | dotfiles | Home Manager가 배치 |
| stateVersion | 기존 상태와 호환되는 기본 동작을 선택하기 위한 설치 기준 버전 | NixOS/Home Manager 문서 | `system.stateVersion`, `home.stateVersion` | 업데이트 번호가 아님 |
| generation | 시스템 또는 사용자 프로필의 활성화 가능한 구성 세대 | NixOS Manual, Home Manager CLI | 세대 | 롤백 단위 |

## 3. 수식, 알고리즘, 표준

| 항목 | 내용 요약 | 가정 | 출처 | 검증 상태 |
|---|---|---|---|---|
| 안정 버전 정렬 | nixpkgs `nixos-26.05`와 Home Manager `release-26.05`를 사용한다. | 2026-07-14 신규 설치 | NixOS 발표, Home Manager 저장소 | 검증 완료 |
| WSL 모듈 결합 | WSL 호스트만 `nixos-wsl.nixosModules.default`를 가져오고 `wsl.enable = true`로 설정한다. | WSL 2 | NixOS-WSL Flake 문서 | 검증 완료 |
| 사용자 환경 분리 | `homeConfigurations`를 별도로 출력하고 `home-manager switch`로 독립 활성화한다. | Nix daemon에 일반 사용자가 접근 가능 | Home Manager README/CLI | 검증 완료 |
| 언어 관리자 경계 | Flake는 uv·nvm·rustup 자체를 고정하고 프로젝트 파일은 언어 툴체인을 고정한다. | 첫 복원 시 네트워크 사용 가능 | 각 도구 공식 문서 | 검증 완료 |
| 외부 바이너리 호환 | uv·nvm·rustup이 받은 일반 Linux 바이너리를 위해 공통 NixOS 모듈에서 nix-ld를 활성화한다. | x86_64-linux | Nix-ld 공식 위키 | 검증 완료 |
| nvm 자동 전환 | zsh `chpwd` 훅이 `.nvmrc`를 찾고 누락 버전이면 `nvm install`, 설치 버전이면 `nvm use`를 실행한다. | zsh와 nvm 함수가 먼저 로드됨 | nvm README | 검증 완료 |
| 업데이트 | `nix flake update`로 입력 잠금을 바꾼 뒤 빌드·적용하고 Git에 `flake.lock`을 커밋한다. | Git 저장소 사용 | Nix Flake 문서 | 검증 완료 |
| 롤백 | NixOS는 `nixos-rebuild switch --rollback`, Home Manager는 `home-manager switch --rollback`을 사용한다. | 이전 세대가 GC되지 않음 | NixOS Manual, Home Manager CLI | 검증 완료 |
| 최초 저장소 생성 | GitHub 원격은 비워 두고 로컬 예제를 `git init -b main`으로 초기화한 뒤 remote를 연결해 push한다. | GitHub 계정과 네트워크 사용 가능 | GitHub Docs | 검증 완료 |
| Git 없는 bootstrap | 갱신한 NixOS 채널의 `nix-shell -p git openssh`를 사용한다. `github:`는 REST API 한도, `git+https:`는 외부 Git 선행 요구가 있다. | `sudo nix-channel --update` 완료 | nix.dev, Nix 및 GitHub 문서 | 검증 완료 |
| 편집기와 프로젝트 연결 | 활성화된 devShell이 `.venv/bin` 또는 `node_modules/.bin`을 PATH 앞에 두고 Rust는 rustup proxy를 사용한다. | 프로젝트 루트에서 `nvim .` 실행 | LazyVim extras, 각 언어 공식 문서 | 정적 검증 완료 |
| LSP 단일 소유권 | Mason을 끄고 basedpyright·Ruff·vtsls는 언어 lock, rust-analyzer는 `rust-toolchain.toml`로 관리한다. | LSP 누락 시 프로젝트 의존성을 복원 | LazyVim extras | 정적 검증 완료 |
| LazyVim 프로젝트 소유권 | Home Manager는 최소 기반과 `local_spec`만 제공하고 각 저장소가 `.lazy.lua`, `.lazy-lock.json`을 커밋한다. | 프로젝트 파일을 신뢰한 뒤 실행 | lazy.nvim configuration과 source | 정적 검증 완료 |
| LazyVim plugin 격리 | 프로젝트 절대 경로 hash로 plugin `root`를 분리하고 프로젝트 루트의 `.lazy-lock.json`을 사용한다. | cache 중복 허용 | lazy.nvim `root`, `lockfile` 옵션 | 정적 검증 완료 |
| LazyVim 기본 lock 쓰기 | 프로젝트 밖 기본 lock을 위해 `~/.config/nvim`은 Git 작업 트리의 out-of-store 링크로 둔다. | 저장소 위치가 `~/.config/nixos` | Home Manager 파일 링크 동작 | 정적 검증 완료 |

## 4. 예제 후보

| 예제 | 보여줄 개념 | 필요한 데이터/도구 | 장점 | 위험 |
|---|---|---|---|---|
| 두 호스트와 한 사용자 구성 | NixOS와 Home Manager 출력 분리 | `flake.nix` | 전체 구조를 한 번에 보여준다. | Flake 문법을 먼저 설명해야 한다. |
| 공통·WSL·native 모듈 | 호스트별 차이 격리 | NixOS 모듈 | 네이티브 재사용 목표와 직접 대응한다. | native 하드웨어 파일은 복제할 수 없다. |
| Home Manager 프로그램 모듈 | 사용자 패키지와 설정 | Home Manager | 선언과 dotfiles의 경계를 보여준다. | 기존 파일 충돌을 먼저 처리해야 한다. |
| nvm 소스 입력 | 셸 함수형 도구를 Flake로 고정 | nvm v0.40.4 | nvm 자체와 Node 상태를 분리한다. | `$NVM_DIR` 전체를 Store symlink로 만들면 쓰기가 실패한다. |
| 세 언어 프로젝트 | 관리자와 프로젝트 잠금의 경계 | `.python-version`, `.nvmrc`, `rust-toolchain.toml` | 일관된 멘탈 모델을 만든다. | Flake만으로 완전 재현된다고 오해할 수 있다. |
| LazyVim 실전 개발 셸 | 프로젝트가 plugin spec·lock을 소유하고 편집기가 프로젝트 PATH의 LSP를 사용 | direnv, nix-direnv, 세 언어 예제 | `.vscode`와 유사한 협업 단위를 만든다. | `.lazy.lua` 신뢰와 cache 중복을 설명해야 한다. |

## 5. 논쟁점 또는 주의점

- 쟁점: 언어 런타임까지 Nix Store에서 관리할지 언어별 관리자에게 맡길지 선택해야 한다.
- 서로 다른 설명 방식: 프로젝트 Flake/devShell은 더 강한 Nix 재현성을 제공하고, uv·nvm·rustup 방식은 기존 개발 흐름과 프로젝트 호환성이 높다.
- 이 자료에서 채택할 설명: Nix는 관리자 자체를 고정하고 각 관리자는 프로젝트 파일로 런타임을 고정하는 2계층 방식을 사용한다.
- 채택 이유: 사용자가 명시적으로 uv·nvm·rustup 방식을 선택했고 프로젝트별 버전 전환을 우선했기 때문이다.
- 주의: 이 방식의 언어 런타임과 캐시는 `$HOME` 아래의 가변 상태이며 Nix Store 폐쇄성에 포함되지 않는다. 새 호스트의 첫 실행에는 다운로드가 필요하다.
- 주의: NixOS에서 외부 배포 ELF를 실행하기 위해 nix-ld를 활성화한다. 필요한 공유 라이브러리는 프로젝트 성격에 따라 추가될 수 있다.
- 주의: `system.stateVersion`과 `home.stateVersion`은 패키지 업데이트 방법이 아니며 기존 설치에서는 임의로 올리지 않는다.
- 주의: 네이티브 NixOS의 `hardware-configuration.nix`는 각 컴퓨터에서 생성한 파일을 사용한다.
- 주의: Git 저장소 안의 로컬 Flake는 Git이 추적하지 않는 새 파일을 평가 입력으로 보지 않는다.
- 주의: Private 원격 저장소의 clone은 선언 상태 복원 전에 각 새 호스트의 GitHub 인증 bootstrap이 필요하다. SSH 개인 키 자체는 구성 저장소에 넣지 않는다.
- 주의: GitHub SSH 키는 Git clone/push용이며 Nix `github:` fetcher의 REST API 요청을 인증하지 않는다. API 한도 문제에는 Nix `access-tokens`가 필요하다.
- 주의: LazyVim의 Mason을 비활성화했으므로 LSP와 formatter는 프로젝트가 직접 제공해야 하며 DAP도 자동 설치되지 않는다.
- 주의: out-of-store 링크는 쓰기 가능한 대신 저장소의 절대 clone 위치에 의존한다.
- 주의: `.lazy.lua`는 실행 가능한 Lua이므로 `.envrc`와 별도로 검토해야 한다. lazy.nvim은 Neovim trust DB를 사용한다.
- 주의: 강한 격리를 위해 프로젝트마다 plugin cache를 복제하므로 저장 공간과 최초 다운로드 시간이 늘어난다.

## 6. 출처 필요 항목

- [x] 핵심 정의와 명령은 공식 문서 또는 공식 소스로 확인했다.
- [x] 버전 의존적인 정보는 2026-07-14와 26.05 기준임을 기록했다.

## 7. 조사 요약

- 가장 신뢰할 수 있는 기준 출처: NixOS Manual, nix.dev, NixOS-WSL 문서, Home Manager 공식 문서와 소스
- 초고에 반드시 반영할 내용: 독립 실행형 Home Manager, nix-ld, 상태 버전 유지, nvm의 쓰기 가능한 런타임 디렉터리, native 하드웨어 설정 제외
- 아직 검증이 필요한 내용: 완성형 예제의 Nix 평가와 빌드는 현재 Windows 작업 환경에 Nix가 없어 별도 실행 검증이 필요하다.
- 독자에게 혼란을 줄 수 있는 용어: Flake가 시스템과 사용자를 직접 설정한다는 표현, dotfiles와 Home Manager를 같은 계층으로 보는 표현

## 8. 품질 점검

- [x] 정의, 수식, 알고리즘의 출처가 기록되어 있다.
- [x] 공식 문서와 공식 구현 소스를 우선 출처로 사용했다.
- [x] 버전 의존적 내용에는 날짜 또는 버전이 기록되어 있다.
- [x] 출처 없는 주장을 남기지 않았다.
