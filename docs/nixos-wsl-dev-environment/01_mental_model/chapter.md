# 1. NixOS, Flake, Home Manager, dotfiles의 역할

## 학습 목표

이 장을 마치면 다음을 할 수 있다.

1. NixOS와 Nix 패키지 관리자의 역할을 구분한다.
2. Flake와 `flake.lock`이 무엇을 고정하는지 설명한다.
3. 시스템 설정, 사용자 설정, 프로젝트 설정의 소유자를 결정한다.

## 필요한 선행지식

Git 저장소, 셸 초기화 파일, `nvm`이나 `uv` 같은 버전 관리 도구에 대한 경험이면 충분하다. Nix 문법은 필요하지 않다.

## 1.1 먼저 해결할 문제

기존 개발 환경을 새 머신에서 복원한다고 생각해 보자. `apt install` 목록과 `.zshrc`만 Git에 넣으면 도구 버전, OS 정책, 파일 배치가 느슨하다. 반대로 Python과 Node.js까지 모두 Nix 패키지로 고정하면 기존 프로젝트의 `.python-version`과 `.nvmrc` 흐름이 사라진다.

이 자료는 재현성이 필요한 경계를 세 단계로 나눈다.

```text
호스트: NixOS
  └── 사용자: standalone Home Manager
        └── 프로젝트: uv / nvm / rustup
```

아래 계층은 위 계층이 제공한 도구를 사용하지만, 위 계층이 아래 계층의 버전까지 대신 결정하지 않는다.

## 1.2 Nix와 NixOS

Nix는 입력을 바탕으로 패키지와 설정 결과를 `/nix/store`의 불변 경로에 만든다. 같은 프로그램의 여러 버전이 서로 다른 Store 경로에 공존할 수 있고, 프로필은 어떤 결과를 현재 사용할지 가리킨다.

NixOS는 이 모델을 운영체제 전체에 적용한다. 사용자 계정, 서비스, 기본 셸, 커널 매개변수 같은 시스템 상태를 Nix 모듈로 선언하고 하나의 시스템 세대로 만든다. 실패하면 이전 세대로 돌아갈 수 있다.

NixOS-WSL도 NixOS다. 다만 커널, 가상화, Windows 연동은 WSL이 제공하므로 실제 하드웨어 NixOS와 호스트 모듈은 같을 수 없다.

## 1.3 Flake는 저장소의 공개 인터페이스다

Flake는 두 질문에 답한다.

- `inputs`: 이 구성이 참조하는 외부 소스는 무엇인가?
- `outputs`: 이 저장소에서 빌드하거나 적용할 수 있는 결과는 무엇인가?

예제 출력은 다음처럼 읽는다.

```text
nixosConfigurations.wsl    → WSL 호스트 시스템
nixosConfigurations.native → 실제 하드웨어 시스템
homeConfigurations.nixos   → nixos 사용자의 홈 프로필
```

`flake.nix`가 입력 URL과 출력 구조를 선언하면 `flake.lock`은 각 입력의 실제 리비전과 해시를 기록한다. `package.json`과 lockfile의 관계에 가깝지만, 잠금 대상이 애플리케이션 의존성이 아니라 Nixpkgs·Home Manager·NixOS-WSL 같은 구성 입력이라는 점이 다르다.

복원할 때는 커밋된 `flake.lock`을 그대로 사용한다. `nix flake update`는 복원 명령이 아니라 의도적인 업그레이드 명령이다.

## 1.4 standalone Home Manager

Home Manager는 Nix 모듈로 사용자 패키지, 환경 변수, 셸, dotfiles를 관리한다. NixOS 모듈로 통합할 수도 있지만 이 자료는 독립 실행형을 선택한다.

```console
$ sudo nixos-rebuild switch --flake .#wsl
$ home-manager switch --flake .#nixos
```

두 전환을 분리하면 다음 성질을 얻는다.

- 사용자 설정 변경에 루트 권한이 필요 없다.
- 사용자 프로필을 시스템보다 자주 변경할 수 있다.
- 동일한 `homeConfigurations.nixos`를 WSL과 네이티브 NixOS에서 재사용할 수 있다.
- 시스템 세대와 홈 프로필 세대를 따로 롤백할 수 있다.

대신 전환 명령이 두 개다. 이 비용은 시스템과 사용자의 수명 주기를 분리하기 위한 의도적인 선택이다.

## 1.5 dotfiles는 데이터다

dotfiles는 프로그램이 읽는 설정 원본이다. Home Manager와 경쟁하는 별도 계층이 아니다. 예를 들어 Neovim의 `init.lua` 원본은 `dotfiles/nvim/init.lua`에 두고 Home Manager가 이를 읽어 `~/.config/nvim/init.lua`를 생성한다. Lua 설정 디렉터리와 쓰기 가능한 lock 파일은 충돌하지 않도록 별도 경로 단위로 연결한다.

반면 zsh, Git, Starship처럼 Home Manager에 안정적인 전용 모듈이 있으면 Nix 옵션으로 표현한다. 기준은 다음과 같다.

- 전용 모듈이 설치와 통합을 함께 처리하면 모듈을 사용한다.
- 애플리케이션 고유 언어로 작성된 큰 설정은 `dotfiles/`에 둔다.
- Home Manager가 만든 결과 파일을 직접 수정하지 않는다. 원본 모듈이나 dotfile을 고치고 다시 전환한다.

## 1.6 소유권을 결정하는 질문

| 질문 | 그렇다면 |
|---|---|
| 부팅이나 모든 사용자에게 영향을 주는가? | NixOS 시스템 모듈 |
| `$HOME` 안에서 끝나고 일반 사용자 권한으로 바꿀 수 있는가? | Home Manager |
| 프로그램이 직접 읽는 설정 내용인가? | dotfiles, Home Manager가 배치 |
| Nix 외부 입력의 리비전인가? | `flake.lock` |
| 특정 프로젝트가 요구하는 언어 버전인가? | 프로젝트 버전 파일 |
| 토큰이나 개인 키인가? | 이 저장소 밖의 비밀 관리 체계 |

## 1.7 상태 버전은 업데이트 버전이 아니다

`system.stateVersion`과 `home.stateVersion`은 설치 당시의 데이터 형식과 기본 동작을 보존하는 호환 기준이다. NixOS나 Home Manager를 업데이트한다고 함께 올리지 않는다. 기존 설치를 구성 저장소에 편입할 때는 기존 값을 유지한다.

## 직접 확인

다음 항목의 소유자를 각각 결정해 보자.

1. WSL의 기본 사용자와 로그인 셸
2. Neovim의 `init.lua`
3. Python 3.13을 요구하는 프로젝트
4. Home Manager 릴리스 브랜치의 실제 Git 커밋
5. npm 인증 토큰

정답은 순서대로 NixOS, dotfiles/Home Manager, uv 프로젝트, `flake.lock`, 저장소 밖의 비밀 관리다.

## 요약

- NixOS는 호스트 상태를, Home Manager는 사용자 상태를 관리한다.
- Flake는 입력과 출력의 진입점이고 `flake.lock`이 실제 입력 리비전을 고정한다.
- dotfiles는 프로그램 설정 데이터이며 Home Manager가 배치한다.
- 언어 런타임은 프로젝트 파일이 결정한다.
- 상태 버전은 릴리스 번호처럼 올리지 않는다.

## 추가 읽을거리

- [Nix Flakes 개념](https://nix.dev/concepts/flakes.html)
- [Home Manager 소개](https://nix-community.github.io/home-manager/introduction.html)
- [Home Manager 설치 방식](https://nix-community.github.io/home-manager/installation.html)
- [NixOS `stateVersion` FAQ](https://wiki.nixos.org/wiki/FAQ/When_do_I_update_stateVersion)

[← 목차](../index.md) · [2장: NixOS-WSL 설치 →](../02_install_nixos_wsl/chapter.md)
