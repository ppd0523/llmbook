# 6. 문제 해결

## 학습 목표

1. 평가, build, activation, runtime 실패를 구분한다.
2. 오류가 발생한 소유권 계층부터 진단한다.
3. 기존 파일과 generation을 보존하며 복구한다.

## 6.1 먼저 실패 단계를 구분한다

```text
Nix 문법 분석
  → 모듈 평가와 옵션 병합
    → package·generation build
      → activation과 파일 링크
        → 새 shell·프로그램 runtime
```

| 단계 | 대표 증상 | 먼저 볼 것 |
|---|---|---|
| 문법 | `unexpected`, `syntax error` | 오류가 가리킨 `.nix` 줄과 세미콜론 |
| 평가 | `option does not exist`, `attribute missing` | 옵션 이름, release, module import |
| build | package build 실패, fetch 실패 | 실패한 derivation과 input |
| activation | `Existing file ... is in the way` | 최종 target의 기존 파일과 소유자 |
| runtime | 명령 없음, 환경 변수 미반영 | 활성 generation, 새 shell, PATH |

실패 단계가 다른데도 무조건 `nixos-rebuild`부터 반복하면 원인을 좁히기 어렵다.

## 6.2 최소 진단 명령

```console
$ cd ~/.config/nixos
$ git status --short
$ git diff
$ nix flake show
$ home-manager build --flake .#nixos
$ home-manager generations
```

각 명령의 목적:

- `git status`: 새 파일이 추적되는지와 예상하지 않은 상태 파일 확인
- `git diff`: 실제로 무엇을 바꿨는지 확인
- `nix flake show`: `homeConfigurations.nixos` output 존재 여부 확인
- `home-manager build`: activation 없이 평가와 build 재현
- `home-manager generations`: 현재와 이전 사용자 generation 확인

## 6.3 output을 찾지 못함

증상:

```text
flake ... does not provide attribute
'homeConfigurations."현재사용자"'
```

원인:

- `#nixos`를 생략하여 CLI가 현재 사용자 이름을 자동 선택했다.
- 실제 output 이름과 명령의 attribute가 다르다.
- 잘못된 디렉터리에서 `.`을 사용했다.

확인:

```console
$ nix flake show ~/.config/nixos
$ grep -n "homeConfigurations" ~/.config/nixos/flake.nix
```

해결:

```console
$ home-manager build --flake ~/.config/nixos#nixos
```

`nixosConfigurations.wsl`의 `wsl`과 `homeConfigurations.nixos`의 `nixos`는 서로
다른 namespace의 이름이다.

## 6.4 새 모듈을 찾지 못함

증상:

```text
path '.../modules/home/example.nix' does not exist
```

파일은 실제로 있지만 새로 만든 뒤 Git에 추가하지 않은 경우가 흔하다.

```console
$ git status --short
?? modules/home/example.nix
$ git add modules/home/example.nix
$ home-manager build --flake .#nixos
```

Git 기반 local Flake는 추적되지 않은 파일을 source snapshot에 포함하지 않는다.

## 6.5 옵션이 존재하지 않음

증상:

```text
The option `programs.example.someSetting' does not exist
```

다음을 확인한다.

1. 옵션 이름과 대소문자가 정확한가?
2. NixOS 옵션을 Home Manager 모듈에 쓴 것은 아닌가?
3. 검색한 문서와 현재 `flake.lock`의 Home Manager release가 같은가?
4. 해당 프로그램 모듈을 import하거나 enable해야 하는가?

공식 [Home Manager 옵션 검색](https://nix-community.github.io/home-manager/options.html)에서
namespace, 타입과 선언 파일을 확인한다. 인터넷 문서의 master 전용 옵션을 stable
26.05 구성에 그대로 복사하지 않는다.

Nixpkgs와 Home Manager release가 맞지 않으면 기본 release check 경고가 나타날 수
있다. stable 구성은 다음처럼 같은 release 계열을 사용한다.

```nix
nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
home-manager.url =
  "github:nix-community/home-manager/release-26.05";
```

## 6.6 기존 파일 충돌

증상:

```text
Existing file '/home/nixos/.config/git/config' is in the way
```

Home Manager가 데이터 손실을 막기 위해 activation을 중단한 것이다.

```console
$ ls -la ~/.config/git/config
$ cp -a ~/.config/git/config ~/git-config.before-home-manager
```

기존 설정을 `programs.git.settings` 또는 저장소의 dotfile로 옮긴 뒤 기존 target을
백업 위치로 이동하고 다시 switch한다.

한 번만 자동 백업하려면:

```console
$ home-manager switch -b hm-backup --flake .#nixos
```

`.hm-backup` target이 이미 있으면 다시 중단된다. `force = true`를 일반 해결책으로
사용하지 않는다.

## 6.7 부모 링크 안에 파일을 만들 수 없음

증상은 다음과 비슷하다.

```text
Error installing file '.config/example/config.toml' outside $HOME
```

또는 같은 target이 여러 번 정의되었다는 평가 오류가 발생할 수 있다.

원인은 부모 디렉터리 전체를 링크하면서 다른 모듈이 그 안의 파일을 별도로 생성하기
때문이다.

```nix
# 충돌 가능
xdg.configFile."example".source = ../../dotfiles/example;
xdg.configFile."example/config.toml".text = "...";
```

부모 링크를 제거하고 파일 또는 하위 디렉터리 단위로 소유권을 나눈다.

```nix
xdg.configFile."example/scripts".source =
  ../../dotfiles/example/scripts;
xdg.configFile."example/config.toml".source =
  ../../dotfiles/example/config.toml;
```

## 6.8 home-manager 명령이 없음

최초 bootstrap 전이거나 사용자 프로필이 현재 PATH에 없을 수 있다.

```console
$ command -v home-manager
$ nix run .#home-manager -- build --flake .#nixos
$ nix run .#home-manager -- switch --flake .#nixos
```

기존 예제의 local app은 잠긴 Home Manager CLI를 실행한다. activation 후 새 shell에서
다시 확인한다.

```console
$ exec zsh
$ command -v home-manager
```

`modules/home/default.nix`에 다음 선언도 있어야 한다.

```nix
programs.home-manager.enable = true;
```

## 6.9 프로그램은 설치됐지만 shell 설정이 적용되지 않음

다음을 구분한다.

- 패키지가 프로필에 있는가?
- Home Manager가 shell integration을 생성했는가?
- 현재 로그인 shell이 그 shell인가?
- activation 후 새 shell을 시작했는가?

```console
$ command -v starship
$ echo "$SHELL"
$ ps -p $$ -o comm=
$ getent passwd "$USER" | cut -d: -f7
```

`$SHELL`은 계정의 로그인 shell을 나타내며 현재 프로세스와 다를 수 있다.
`ps -p $$` 결과도 함께 본다.

zsh 로그인 shell 지정은 NixOS 모듈의 책임이다.

```nix
programs.zsh.enable = true;
users.users.${username}.shell = pkgs.zsh;
```

Starship과 direnv의 zsh integration은 Home Manager에서 활성화한다.

## 6.10 환경 변수가 보이지 않음

`home.sessionVariables`는 activation 이후 시작한 지원 shell이나 session에서
불러온다. 현재 shell을 새로 시작한다.

```console
$ exec zsh
$ printenv EDITOR
```

Home Manager가 관리하지 않는 shell을 사용한다면
`hm-session-vars.sh`를 불러오는 방법을 검토해야 한다. 기존 매뉴얼은 zsh를 Home
Manager로 관리하므로 별도 수동 source를 중복하지 않는다.

프로젝트에서만 필요한 환경 변수는 direnv가 해당 디렉터리에 진입했을 때만 보이는
것이 정상이다.

## 6.11 package collision

오류에 `collision between .../bin/<name>`이 포함되면 서로 다른 package가 같은 실행
파일 경로를 제공하는 경우다. 파일 activation 충돌과 원인이 다르다.

다음 위치에서 중복 설치를 찾는다.

- `home.packages`
- `programs.<name>.package`
- 같은 도구의 full/minimal 변형

한 package만 최종 실행 파일을 제공하도록 중복을 제거한다. NixOS 시스템 패키지와
사용자 패키지에 같은 프로그램이 있는 것 자체는 항상 build collision을 만들지는
않지만, PATH에서 어느 버전이 선택되는지 혼동할 수 있으므로 소유 계층을 하나로
정한다.

## 6.12 rollback이 필요한 경우

새 사용자 설정 때문에 shell이나 필수 도구가 동작하지 않으면 직전 generation으로
돌아간다.

```console
$ home-manager switch --rollback
```

명령 실행 자체가 어려우면 현재 terminal을 닫지 말고 열린 다른 shell에서 실행한다.
복구 후 Git의 잘못된 선언도 수정한다.

시스템 service, 계정, 로그인 shell 등 NixOS 변경이 원인이면 Home Manager rollback이
아니라 시스템 rollback을 사용한다.

```console
$ sudo nixos-rebuild switch --rollback
```

## 6.13 flake.lock이 의도치 않게 바뀜

새 머신 복원 중에는 input을 업데이트하지 않는다.

```console
$ git status --short flake.lock
$ git diff -- flake.lock
```

복원 과정에서 실수로 lock을 갱신했다면 저장소의 커밋된 lock으로 되돌려야 한다.
사용자의 다른 변경을 덮어쓸 수 있으므로 현재 diff를 먼저 확인하고, 필요한 경우
문제 변경만 직접 되돌린다.

의도적인 업데이트라면 lock diff를 검토하고 NixOS와 Home Manager 양쪽 build를
통과시킨 뒤 commit한다.

## 6.14 최종 진단 체크리스트

1. 오류는 NixOS, Home Manager, 프로젝트 중 어느 계층인가?
2. 문법, 평가, build, activation, runtime 중 어느 단계인가?
3. `git diff`에 예상한 변경만 있는가?
4. 새 `.nix`와 dotfile이 Git에 추가되었는가?
5. 명령의 `#output` 이름이 Flake와 일치하는가?
6. Home Manager와 Nixpkgs release가 일치하는가?
7. 같은 최종 경로를 여러 모듈이 소유하는가?
8. 현재 shell이 새 generation을 불러왔는가?
9. 즉시 롤백이 필요한가, 아니면 build 실패라 현재 환경은 그대로인가?
10. 복구 뒤 Git 원본도 수정했는가?

## 요약

- 오류 메시지에서 실패 단계와 소유권 계층을 먼저 찾는다.
- activation 충돌은 Home Manager의 데이터 보호 동작이다.
- Flake가 참조하는 새 파일은 Git에 추가해야 한다.
- shell과 환경 변수는 새 session에서 확인한다.
- generation 롤백 뒤에는 Git 선언도 함께 바로잡는다.

## 추가 읽을거리

- [Home Manager 매뉴얼](https://nix-community.github.io/home-manager/)
- [Home Manager 옵션](https://nix-community.github.io/home-manager/options.html)
- [dotfile 충돌과 백업](https://nix-community.github.io/home-manager/usage/dotfiles.html)
- [기존 매뉴얼의 업데이트와 문제 해결](../nixos-wsl-dev-environment/08_operations_and_troubleshooting/chapter.md)

[← 5장](./05-apply-and-rollback.md) · [목차](./index.md)
