# 6. NixOS와 Home Manager에 연결하기

## 학습 목표

1. 시스템, 사용자, 프로젝트 설정의 소유권을 정한다.
2. NixOS와 Home Manager의 build·switch·rollback 범위를 구분한다.
3. `stateVersion`, package release, `flake.lock`의 차이를 설명한다.

## 6.1 세 계층은 포함 관계가 아니라 책임 분리다

```text
NixOS: 머신과 운영체제
├── 부팅, kernel, filesystem
├── 사용자 계정과 login shell
├── system service와 firewall
└── 모든 사용자를 위한 package

Home Manager: 한 사용자의 home
├── 사용자 package
├── shell·Git·editor 설정
├── 환경 변수
└── $HOME 아래 파일과 user service

프로젝트 Flake: 한 저장소
├── compiler와 언어 toolchain
├── build dependency
├── 개발 환경 변수
└── formatter·check·package·app
```

Home Manager가 NixOS 위에서 실행된다고 해서 모든 Home Manager 설정이 NixOS의
하위 책임인 것은 아니다. Standalone 방식에서는 별도 generation과 전환 주기를
가진다.

## 6.2 어디에 둘지 결정하는 질문

| 질문 | “예”라면 |
|---|---|
| 부팅, hardware, account, systemd system service에 영향이 있는가? | NixOS |
| 한 사용자의 `$HOME`, user package, shell 설정인가? | Home Manager |
| 이 저장소를 개발할 때만 필요한가? | 프로젝트 Flake |
| 지금 잠깐 시험할 도구인가? | `nix shell` |
| 비밀 값이나 실행 중 생성되는 데이터인가? | 별도 secret/state 관리 |

예를 들어 Python interpreter를 어디에 둘지는 이름만으로 정하지 않는다.

- 서버 관리자가 항상 쓰는 Python: 시스템 또는 사용자 계층
- 프로젝트가 정확한 Python과 library를 요구: 프로젝트 개발 셸
- 한 번 script를 확인: `nix shell`

## 6.3 NixOS 구성의 모양

최소화한 예시는 다음과 같다.

파일: `/etc/nixos/configuration.nix` (개념 예시)

```nix
{ pkgs, ... }:
{
  networking.hostName = "nixbox";

  users.users.alice = {
    isNormalUser = true;
    extraGroups = [ "wheel" ];
    shell = pkgs.zsh;
  };

  programs.zsh.enable = true;
  services.openssh.enable = true;

  environment.systemPackages = [
    pkgs.git
  ];

  system.stateVersion = "26.05";
}
```

이 module은 package 목록만 만드는 것이 아니다. 최종 NixOS system closure에는
`/etc` 파일, systemd unit, 사용자·그룹 설정, boot 정보 등도 포함된다.

일반적인 안전한 적용 순서는 다음과 같다.

```console
$ sudo nixos-rebuild build
$ sudo nixos-rebuild test
$ sudo nixos-rebuild switch
```

| 명령 | 새 system build | 현재 실행 환경 전환 | 다음 boot 기본값 |
|---|---:|---:|---:|
| `build` | 예 | 아니오 | 아니오 |
| `test` | 예 | 예 | 아니오 |
| `switch` | 예 | 예 | 예 |
| `boot` | 예 | 아니오 | 예 |

Flake 구성이라면 `--flake <경로>#<host>`를 붙인다.

```console
$ sudo nixos-rebuild build --flake ~/.config/nixos#myhost
```

## 6.4 Home Manager 구성의 모양

Standalone Flake가 평가하는 `home.nix`는 다음과 비슷하다.

파일: `home.nix` (개념 예시)

```nix
{ pkgs, ... }:
{
  home.username = "alice";
  home.homeDirectory = "/home/alice";

  home.packages = [
    pkgs.ripgrep
    pkgs.fd
  ];

  programs.git = {
    enable = true;
    userName = "Alice";
  };

  programs.bash.shellAliases = {
    ll = "ls -la";
  };

  home.stateVersion = "26.05";
  programs.home-manager.enable = true;
}
```

Home Manager는 package만 profile에 넣는 것보다 더 많은 일을 한다. 예를 들어
`programs.git` module은 Git package와 설정 파일을 함께 관리할 수 있다.

```console
$ home-manager build --flake ~/.config/home-manager#alice
$ home-manager switch --flake ~/.config/home-manager#alice
```

- `build`: 새 home generation을 만들지만 활성화하지 않는다.
- `switch`: build 후 해당 generation을 활성화한다.

Home Manager가 관리하는 파일을 직접 편집하면 그 변경은 원본 선언에 반영되지 않는다.
설정 파일이 Store의 read-only 결과로 연결되어 있다면 편집 자체가 실패할 수 있다.
`home.nix`나 그 source dotfile을 수정하고 다시 switch한다.

## 6.5 standalone과 NixOS module 방식

Home Manager 공식 문서는 NixOS에서 두 방식을 모두 지원한다.

| 방식 | 적용 명령 | system과 home generation | 장점 | 주의점 |
|---|---|---|---|---|
| standalone | `home-manager switch` | 분리 | 사용자 변경을 독립 적용 | system과 별도 검증·롤백 |
| NixOS module | `nixos-rebuild switch` | 함께 build·전환 | 한 번에 일관된 배포 | 작은 home 변경도 system rebuild |

둘 중 하나가 항상 더 “Nix답다”는 결론은 없다. 운영 단위를 기준으로 고른다.
현재 저장소의 후속 Home Manager 책은 standalone 방식을 사용한다.

## 6.6 같은 프로그램을 두 계층이 나눠 맡을 수 있다

zsh 사례를 보자.

```nix
# NixOS
{
  programs.zsh.enable = true;
  users.users.alice.shell = pkgs.zsh;
}
```

```nix
# Home Manager
{
  programs.zsh = {
    enable = true;
    shellAliases.ll = "ls -la";
  };
}
```

NixOS는 login shell로 사용할 executable과 시스템 integration을 준비한다.
Home Manager는 Alice의 zsh 설정을 만든다. 같은 이름의 option이지만 서로 다른
module set과 책임이다.

반대로 단순 CLI package 하나를 NixOS와 Home Manager 양쪽 package 목록에 동시에
넣을 필요는 보통 없다. 어느 profile의 package를 실행하는지 `PATH` 순서가 가리고,
업데이트 원본도 둘로 나뉜다.

## 6.7 세 가지 버전 축

다음 값들은 서로 바꿔 쓸 수 없다.

| 값 | 결정하는 것 | 언제 변경하는가 |
|---|---|---|
| `nixpkgs.url`의 release branch | 따라갈 Nixpkgs/NixOS release 계열 | 계획한 release upgrade |
| `flake.lock`의 revision | 실제 사용 중인 입력 commit과 hash | 검증 가능한 dependency update |
| `system.stateVersion` | 기존 시스템의 호환 기본값 | release note와 migration에 따라 매우 신중히 |
| `home.stateVersion` | 기존 home의 호환 기본값 | release note와 migration에 따라 매우 신중히 |

`system.stateVersion = "26.05";`가 package를 26.05로 고정하는 것은 아니다.
package revision은 Nixpkgs 입력과 lockfile이 정한다.

새 NixOS 또는 Home Manager release로 입력을 업데이트해도 기존 설치의
`stateVersion`을 관성적으로 올리지 않는다. 이 값은 과거 기본 동작과 state format의
호환을 유지하는 기준이다.

## 6.8 적용 전에 확인하고 실패 시 되돌린다

### NixOS

```console
$ sudo nixos-rebuild build --flake .#myhost
$ sudo nixos-rebuild test --flake .#myhost
$ sudo nixos-rebuild switch --flake .#myhost
```

문제가 생기면 실행 중인 시스템에서 이전 generation으로 전환할 수 있다.

```console
$ sudo nixos-rebuild switch --rollback
```

부팅이 안 되면 bootloader의 이전 NixOS generation을 선택한다. 단, 오래된 generation을
GC 전에 삭제했다면 사용할 수 없다.

### Home Manager

```console
$ home-manager build --flake .#alice
$ home-manager switch --flake .#alice
$ home-manager generations
```

`home-manager generations`가 보여 주는 이전 generation의 activation package를
실행해 복구할 수 있다. 명령 형식은 현재 출력에 표시된 경로를 사용한다.

### Git

generation 롤백 뒤에도 잘못된 source가 자동으로 고쳐지는 것은 아니다.

1. 이전 generation으로 즉시 환경을 복구한다.
2. Git diff에서 원인을 고친다.
3. `build`로 다시 검증한다.
4. `switch`하고 수정 이력을 commit한다.

## 6.9 비밀과 가변 데이터는 선언 저장소 밖에서 다룬다

다음 값을 평문 `flake.nix`, `configuration.nix`, `home.nix`에 넣지 않는다.

- API token과 password
- SSH private key
- 개인 인증서 private key
- 서비스가 계속 갱신하는 database

Nix source가 Store로 복사되면 같은 머신의 다른 사용자가 Store 내용을 읽을 수 있는
구성도 많다. secret은 전용 secret 관리 방식을 선택하고, Nix에는 secret의 암호화된
source나 안전한 runtime path 연결만 선언한다. 구체적인 secret 도구 선택은 이
입문서 범위 밖이다.

## 직접 해보기

다음 설정의 소유 계층을 결정하고 이유를 한 문장으로 쓴다.

1. Bluetooth 활성화
2. Alice의 Git 사용자 이름
3. Rust 프로젝트의 compiler toolchain
4. 부팅 시 PostgreSQL 시작
5. Alice의 Starship prompt
6. 프로젝트 테스트용 `curl`과 `jq`
7. GitHub access token

모범 답:

1. NixOS — hardware와 system service 범위
2. Home Manager — 사용자 설정
3. 프로젝트 — 저장소가 요구하는 toolchain
4. NixOS — system service
5. Home Manager — 사용자 shell 표시
6. 프로젝트 dev shell — 팀의 개발·검사 의존성
7. Nix 설정 밖의 secret 관리 — 평문 Store 유입 방지

## 요약

- NixOS는 시스템, Home Manager는 사용자, dev shell은 프로젝트를 소유한다.
- 각 계층의 `build`와 `switch`를 분리하면 적용 전 검증이 가능하다.
- Standalone Home Manager는 NixOS와 별도 generation을 가진다.
- release branch, lockfile revision, `stateVersion`은 서로 다른 버전 축이다.
- generation 롤백과 Git source 복구, 가변 데이터 백업은 서로 보완한다.

## 공식 자료

- [NixOS configuration 변경](https://nixos.org/manual/nixos/stable/#sec-changing-config)
- [NixOS configuration option](https://search.nixos.org/options)
- [Home Manager 설치 방식](https://nix-community.github.io/home-manager/installation.html)
- [Home Manager configuration 예시](https://nix-community.github.io/home-manager/usage/configuration.html)
- [`home.stateVersion`](https://nix-community.github.io/home-manager/options/home-manager/home.html#home-stateversion)

[← 5장](./05-module-system.md) · [목차](./index.md) ·
[7장: 안내식 통합 실습 →](./07-guided-lab.md)
