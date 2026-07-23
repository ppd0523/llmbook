# 1. Home Manager의 역할과 경계

## 학습 목표

1. NixOS, Home Manager, 프로젝트 설정의 소유권을 구분한다.
2. standalone 방식의 build와 activation 흐름을 설명한다.
3. 고정된 선언과 실행 중 생성되는 상태를 구분한다.

## 1.1 Home Manager가 해결하는 문제

사용자 환경을 수동으로 구성하면 여러 위치가 서로 다른 시점에 바뀐다.

- 패키지는 `nix profile`, 배포판 패키지 관리자, 설치 스크립트에 흩어진다.
- `.zshrc`, `.gitconfig`, `~/.config/*`는 직접 수정된다.
- 새 머신에서는 과거에 실행했던 명령의 순서를 기억해야 한다.
- 설정 파일은 복사했지만 필요한 실행 파일이나 shell hook이 빠질 수 있다.

Home Manager는 사용자 환경의 **원하는 상태**를 Nix 모듈로 선언한다. 선언을
평가하여 새 generation을 만들고, activation 과정에서 패키지 프로필과 홈 디렉터리의
링크를 그 generation으로 전환한다.

```text
Git의 flake.nix와 Home Manager 모듈
                │
                ▼
       평가 및 패키지 빌드
                │
                ▼
    Nix Store의 Home Manager generation
                │
                ▼
  사용자 프로필·설정 링크·shell hook 활성화
```

이 흐름 덕분에 구성 원본은 Git으로 검토하고, 생성 결과는 Nix Store에서 재사용하며,
현재 사용자 환경은 generation 단위로 전환할 수 있다.

## 1.2 세 가지 소유권 계층

현재 프로젝트는 다음 경계를 사용한다.

| 계층 | 소유하는 것 | 적용 명령 |
|---|---|---|
| NixOS | 사용자 계정, 로그인 shell, system service, 커널·하드웨어, 시스템 전체 정책 | `nixos-rebuild` |
| Home Manager | 사용자 패키지, shell 설정, Git 설정, 환경 변수, `$HOME` 아래 설정 파일 | `home-manager` |
| 프로젝트 | 언어 버전, 의존성 lockfile, 개발 shell, 프로젝트별 editor 설정 | `nix develop`, 언어별 도구 |

예를 들어 zsh는 양쪽에 설정이 필요할 수 있다.

- NixOS의 `programs.zsh.enable`과 `users.users.<name>.shell`은 로그인 shell을 준비한다.
- Home Manager의 `programs.zsh`는 history, alias, completion과 사용자 `.zshrc`를
  관리한다.

Home Manager에서 zsh를 활성화했다고 해서 NixOS 계정의 로그인 shell이 자동으로
바뀌는 것은 아니다. 반대로 NixOS에서 zsh를 로그인 shell로 지정해도 사용자 alias와
Starship 설정까지 생기지는 않는다.

## 1.3 standalone이라는 말의 의미

standalone은 Home Manager가 혼자 실행된다는 뜻이 아니라 **NixOS generation과
독립된 사용자 generation을 가진다**는 뜻이다.

```console
$ sudo nixos-rebuild switch --flake .#wsl
$ home-manager switch --flake .#nixos
```

두 명령은 같은 Flake와 `flake.lock`을 사용할 수 있지만 서로 다른 output을
선택한다. 따라서 사용자 설정만 수정했다면 `sudo`나 NixOS 전체 rebuild가 필요 없다.
대신 롤백도 각각 수행해야 한다.

Home Manager 공식 매뉴얼은 사용자 홈을 시스템 전체와 독립적으로 관리하려는
NixOS 사용자에게 standalone 방식을 사용할 수 있다고 설명한다. NixOS 모듈 방식은
사용자 환경을 `nixos-rebuild`와 함께 빌드하고 전환한다.

## 1.4 선언과 상태

모든 사용자 파일을 Nix로 고정하는 것은 바람직하지 않다.

| 선언하여 Git에 넣을 것 | 실행 중 생성되며 Git에 넣지 않을 것 |
|---|---|
| 패키지 목록과 모듈 옵션 | shell history |
| alias와 정적 프로그램 설정 | cache와 log |
| dotfile 원본 | 인증 토큰과 개인 키 |
| `flake.nix`, `flake.lock` | 프로그램이 갱신하는 데이터베이스 |
| 복원 가능한 plugin lock | 머신별 세션·임시 파일 |

Nix Store의 파일은 읽기 전용이다. 프로그램이 직접 수정해야 하는 파일이나 디렉터리를
일반 store 링크로 만들면 저장에 실패한다. 이런 값은 상태 디렉터리에 남겨 두거나,
정말 필요한 파일만 out-of-store 링크로 연결한다.

## 1.5 패키지 버전과 stateVersion

다음 세 값은 역할이 다르다.

| 값 | 역할 | 언제 변경하는가 |
|---|---|---|
| `nixpkgs.url` | 사용할 Nixpkgs release 계열 | 릴리스 업그레이드 |
| `flake.lock` | 실제 입력 commit과 content hash | 검토한 업데이트 |
| `home.stateVersion` | 기존 사용자 데이터와 호환되는 기본 동작 | 릴리스 노트를 읽고 필요한 마이그레이션을 수행할 때만 |

`home.stateVersion = "26.05";`는 패키지를 26.05에 고정하는 설정이 아니다.
패키지와 Home Manager 소스는 Flake input과 lock이 정한다. 이미 활성화한 home의
`stateVersion`을 새 릴리스마다 올리면 호환성을 지켜 주던 이전 기본값이 바뀔 수 있다.

## 1.6 무엇을 어디에 둘지 판단하는 규칙

새 설정을 추가할 때 다음 순서로 판단한다.

1. 시스템 전체 또는 계정 생성에 필요한가? NixOS 모듈에 둔다.
2. 한 사용자의 실행 파일이나 `$HOME` 설정인가? Home Manager에 둔다.
3. 특정 저장소에서만 필요한가? 프로젝트 Flake나 프로젝트 설정에 둔다.
4. Home Manager에 전용 프로그램 옵션이 있는가? 전용 옵션을 먼저 사용한다.
5. 전용 옵션이 부족한가? 필요한 파일만 dotfiles에서 배치한다.
6. 비밀 또는 실행 중 변경되는 상태인가? 평문 구성 저장소에서 제외한다.

이 규칙은 같은 경로를 NixOS, Home Manager, 수동 dotfiles가 동시에 소유하는 충돌을
줄인다.

## 요약

- standalone Home Manager는 NixOS와 별도 generation을 관리한다.
- NixOS는 시스템, Home Manager는 사용자, 각 프로젝트는 프로젝트 상태를 소유한다.
- Nix Store의 선언 결과와 프로그램이 쓰는 상태를 분리한다.
- 패키지 release, `flake.lock`, `home.stateVersion`은 서로 다른 버전 축이다.

[목차](./index.md) · [2장: Flake와 모듈 구조 읽기 →](./02-configuration-structure.md)
