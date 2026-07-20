# 7. `nix develop`과 direnv로 프로젝트 환경 만들기

## 학습 목표

1. `nix develop`, direnv, nix-direnv의 역할 차이를 설명한다.
2. 프로젝트에 `devShell`을 만들고 수동으로 들어갔다가 나올 수 있다.
3. 신뢰한 프로젝트에서만 개발 환경을 자동으로 불러온다.

## 7.1 먼저 알아둘 핵심

`nix develop`은 프로젝트에 필요한 도구를 컴퓨터 전체에 영구 설치하는 명령이 아니다. 프로젝트의 Flake가 선언한 `devShell`을 읽고, 그 도구와 환경 변수가 보이는 임시 셸을 연다. `exit`하면 원래 셸로 돌아온다.

```text
NixOS / Home Manager
  └─ 평소 어느 프로젝트에서나 쓰는 사용자 환경

프로젝트의 flake.nix + flake.lock
  └─ nix develop이 만드는 프로젝트 전용 환경
       └─ direnv + nix-direnv가 디렉터리별로 자동 진입·해제
```

세 도구의 역할은 겹치지 않는다.

| 도구 | 하는 일 |
|---|---|
| `nix develop` | `devShell`을 평가하고 개발 도구가 들어 있는 셸을 연다. |
| direnv | 디렉터리에 들어오고 나갈 때 `.envrc`에 따라 환경을 불러오거나 해제한다. |
| nix-direnv | direnv가 Nix 개발 환경을 빠르게 재사용하도록 캐시하고 Flake 변경을 감시한다. |

direnv만으로도 Nix를 호출할 수 있지만, nix-direnv를 함께 쓰면 매번 환경을 다시 만드는 대기 시간이 줄어든다. nix-direnv는 direnv를 대체하지 않는 보조 도구다.

## 7.2 Home Manager로 direnv와 nix-direnv 설치

이 책의 [Home Manager 예제](../assets/example-config/modules/home/programs.nix)에는 다음 설정이 포함되어 있다.

```nix
programs.direnv = {
  enable = true;
  enableZshIntegration = true;
  nix-direnv.enable = true;
};
```

- `enable`: direnv를 설치하고 기본 설정을 만든다.
- `enableZshIntegration`: `cd`할 때 direnv가 동작하도록 zsh 훅을 연결한다.
- `nix-direnv.enable`: `.envrc`의 `use flake`를 nix-direnv 구현으로 처리한다.

설정을 적용하고 새 zsh를 열어 설치를 확인한다.

```console
$ home-manager build --flake ~/.config/nixos#nixos
$ home-manager switch --flake ~/.config/nixos#nixos
$ exec zsh
$ direnv version
$ type _direnv_hook
```

`home-manager build`는 먼저 평가만 해 보는 안전 확인이고, `switch`가 실제 사용자 프로필을 바꾼다.

## 7.3 가장 작은 `devShell` 만들기

프로젝트 루트에 다음 `flake.nix`를 만든다. 그대로 실행할 수 있는 파일은 [예제 개발 셸](../assets/example-dev-shell/flake.nix)에도 있다.

```nix
{
  description = "Small project development shell example";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs = { nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        packages = with pkgs; [
          jq
          openssl
          pkg-config
        ];

        PROJECT_ENV = "nix-develop";

        shellHook = ''
          echo "development shell loaded"
        '';
      };
    };
}
```

처음 보는 문법은 네 부분만 구분하면 된다.

- `inputs.nixpkgs`: 패키지를 가져올 Nixpkgs 계열을 정한다.
- `system`: 이 예제의 실행 플랫폼인 64비트 Linux를 선택한다. NixOS-WSL도 여기에 해당한다.
- `devShells.${system}.default`: 인자 없이 `nix develop`을 실행할 때 선택할 기본 셸이다.
- `pkgs.mkShell`: `packages`, 환경 변수, 시작 스크립트를 하나의 개발 환경으로 묶는다.

`packages`는 이 셸 안에서만 PATH에 나타난다. `PROJECT_ENV`는 일반 환경 변수가 되고, `shellHook`은 셸에 들어갈 때마다 실행된다. 비밀번호나 토큰을 `flake.nix` 또는 `shellHook`에 넣어서는 안 된다. Flake 소스와 빌드 결과가 Nix Store에 복사될 수 있기 때문이다.

## 7.4 잠금 파일을 만들고 수동으로 사용하기

프로젝트에서 잠금 파일을 한 번 만들고 두 파일을 Git에 넣는다.

```console
$ git add flake.nix
$ nix flake lock
$ git add flake.lock
$ nix develop
development shell loaded
```

첫 실행은 Nixpkgs와 필요한 패키지를 내려받으므로 오래 걸릴 수 있다. 셸 안에서 확인한다.

```console
$ echo "$PROJECT_ENV"
nix-develop
$ jq --version
$ openssl version
$ exit
```

`exit` 또는 `Ctrl-D` 뒤에는 개발 셸에서 추가된 도구와 환경 변수가 사라진다. 대화형 셸 없이 명령 하나만 실행하려면 `-c`를 사용한다.

```console
$ nix develop -c jq --version
```

기본 셸이 아닌 이름 있는 셸 `devShells.x86_64-linux.docs`를 만들었다면 `nix develop .#docs`처럼 선택한다.

## 7.5 디렉터리 진입 시 자동으로 불러오기

프로젝트 루트의 `.envrc`에는 한 줄만 둔다.

```bash
use flake
```

파일을 Git에 추가한 뒤 최초 한 번 승인한다.

```console
$ git add .envrc
$ direnv allow
direnv: loading .../.envrc
development shell loaded
```

이후 프로젝트 디렉터리를 벗어나면 환경이 자동으로 해제되고, 다시 들어오면 로드된다. `flake.nix`, `flake.lock`, `.envrc`가 바뀌면 nix-direnv가 환경을 다시 평가한다.

`.envrc`는 단순 설정 파일이 아니라 셸 코드다. clone한 저장소에서 내용을 먼저 읽고 신뢰할 때만 `direnv allow`를 실행한다. 파일이 바뀌면 direnv가 기존 승인을 취소하고 다시 승인을 요구하는 것도 이 때문이다.

```console
$ direnv status
$ direnv reload
$ direnv deny
```

- `status`: 현재 허용 상태와 로드된 `.envrc`를 확인한다.
- `reload`: 환경을 즉시 다시 읽는다.
- `deny`: 현재 `.envrc` 승인을 취소한다.

이름 있는 `docs` 셸을 자동으로 선택하려면 `.envrc`를 `use flake .#docs`로 바꾼다.

## 7.6 무엇을 `devShell`에 넣어야 할까

판단 기준은 “이 프로젝트를 clone한 동료와 CI도 같은 도구가 필요한가?”다.

| 대상 | 권장 위치 |
|---|---|
| `git`, `nvim`, `direnv`처럼 매일 쓰는 개인 도구 | Home Manager |
| 컴파일러, 코드 생성기, `pkg-config`, 네이티브 라이브러리 | 프로젝트 `devShell` |
| Python·Node.js·Rust의 정확한 버전 | 프로젝트가 택한 한 가지 방식 |
| API 토큰, 개인 SSH 키 | Flake 밖의 비밀 저장소 또는 로컬 환경 |

6장의 uv·NVM·rustup 방식을 쓰는 기존 프로젝트라면 `devShell`에는 그 프로젝트가 추가로 요구하는 시스템 라이브러리만 넣어도 된다. 반대로 새 프로젝트가 Python이나 Node.js 자체를 `devShell`에서 고정하도록 정했다면 같은 런타임을 NVM이나 rustup으로 다시 선택하지 않는다. 한 런타임을 두 도구가 동시에 소유하면 PATH 순서에 따라 버전이 달라져 디버깅이 어려워진다.

`flake.lock`은 Nix 패키지 쪽 재현성을 맡는다. `uv.lock`, `package-lock.json`, `Cargo.lock` 같은 언어 의존성 잠금 파일을 대신하지 않는다.

## 7.7 일상 작업 흐름

자동 로드를 사용하는 프로젝트의 평소 흐름은 짧다.

```console
$ git clone <project-url>
$ cd <project>
direnv: error ... .envrc is blocked
$ less .envrc
$ direnv allow
$ git status --short
```

환경 구성을 바꿀 때는 다음 순서를 사용한다.

```console
$ $EDITOR flake.nix
$ nix develop -c jq --version
$ git diff -- flake.nix flake.lock .envrc
$ git add flake.nix flake.lock .envrc
```

입력을 의도적으로 갱신할 때만 `nix flake update`를 실행한다. 다른 컴퓨터에서 복원할 때는 커밋된 `flake.lock`을 그대로 사용한다.

## 흔한 오류

| 증상 | 원인 | 해결 |
|---|---|---|
| `direnv: command not found` | Home Manager 설정 미적용 | `home-manager build` 후 `switch`, 새 zsh 실행 |
| `cd`해도 아무 반응이 없음 | zsh 훅 미적용 또는 `.envrc` 없음 | `type _direnv_hook`, `.envrc` 위치 확인 |
| `.envrc is blocked` | 아직 승인하지 않았거나 파일이 변경됨 | 내용을 검토한 뒤 `direnv allow` |
| `nix develop`이 기본 셸을 찾지 못함 | `devShells.x86_64-linux.default`가 없거나 이름이 다름 | `nix flake show`, 출력 이름 확인 |
| 새 Nix 파일을 찾지 못함 | Git Flake에서 파일이 아직 추적되지 않음 | `git status --short` 확인 후 필요한 파일 `git add` |
| 수정 뒤에도 이전 환경이 보임 | 자동 재평가가 끝나지 않았거나 캐시된 환경 사용 | `direnv reload`; 필요하면 셸을 나갔다 다시 진입 |
| WSL의 첫 평가가 매우 느림 | 입력과 패키지를 처음 다운로드·빌드함 | 완료를 기다린 뒤 재사용; 프로젝트는 Linux 파일 시스템 아래 배치 |

문제가 자동화인지 Nix 환경 자체인지 구분하려면 먼저 `nix develop`을 수동 실행한다. 이것도 실패하면 `flake.nix`나 Nix 입력 문제이고, 수동 실행만 성공하면 direnv 훅·승인·캐시 문제다.

## 요약

- `nix develop`은 프로젝트의 `devShell`을 임시 셸로 연다.
- direnv는 디렉터리별 환경 진입과 해제를 자동화하고 nix-direnv는 이를 캐시한다.
- `flake.nix`, `flake.lock`, `.envrc`는 프로젝트 저장소에 함께 커밋한다.
- clone한 `.envrc`는 반드시 내용을 검토한 뒤 승인한다.
- 언어 런타임은 Nix와 별도 버전 관리자 중 한 소유자만 정한다.

## 추가 읽을거리

- [Nix `develop` 명령](https://nix.dev/manual/nix/latest/command-ref/new-cli/nix3-develop.html)
- [Nix Flake 개념](https://nix.dev/concepts/flakes.html)
- [direnv 공식 문서](https://direnv.net/)
- [nix-direnv 사용법](https://github.com/nix-community/nix-direnv)

[← 6장](../06_language_toolchains/chapter.md) · [목차](../index.md) · [8장: Git 복원 워크플로 →](../07_restore_workflow/chapter.md)
