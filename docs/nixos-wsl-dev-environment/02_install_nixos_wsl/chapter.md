# 2. 처음부터 NixOS-WSL과 구성 저장소 만들기

이 장은 GitHub 계정만 있고 구성 저장소, SSH 키, NixOS-WSL이 모두 없는 첫 컴퓨터에서 시작한다. 여기서 만든 저장소가 이후 컴퓨터를 복원하는 원본이 된다. 이미 이 절차를 한 번 끝낸 저장소가 있다면 [7장의 복원 절차](../07_restore_workflow/chapter.md)로 이동한다.

## 학습 목표

1. Windows에 WSL과 NixOS-WSL을 처음 설치한다.
2. GitHub에 빈 구성 저장소를 만들고 NixOS-WSL의 SSH 접근을 설정한다.
3. 제공 예제를 로컬 Git 저장소로 초기화하고 `flake.lock`을 처음 생성한다.
4. 시스템과 Home Manager를 적용한 뒤 첫 커밋을 GitHub에 push한다.

## 2.1 전체 순서

첫 컴퓨터에서는 아직 clone할 개인 구성 저장소가 없다. 다음 순서로 원본 저장소를 먼저 만든다.

```text
Windows에 WSL 설치
  → NixOS-WSL 등록
  → GitHub에 비어 있는 원격 저장소 생성
  → NixOS-WSL에서 GitHub SSH 인증 설정
  → 제공 예제를 ~/.config/nixos로 복사
  → git init과 flake.lock 생성
  → 시스템과 사용자 구성 빌드·적용
  → 첫 commit과 push
```

여기서 만든 `flake.lock`을 커밋해야 두 번째 컴퓨터부터 같은 입력 리비전을 복원할 수 있다.

## 2.2 Windows에 WSL 자체 설치

WSL이 전혀 없다면 **관리자 권한 PowerShell**에서 배포판 없이 WSL 기능부터 설치한다.

```powershell
wsl --install --no-distribution
```

Windows를 재시작한 뒤 일반 PowerShell에서 WSL을 업데이트하고 버전을 확인한다.

```powershell
wsl --update
wsl --version
```

`--no-distribution`을 인식하지 못하는 구형 Windows/WSL에서는 Microsoft의 [WSL 설치 문서](https://learn.microsoft.com/windows/wsl/install)를 따른다. NixOS-WSL은 Microsoft Store 계열 WSL 2에서 테스트된다.

## 2.3 NixOS-WSL 등록

NixOS-WSL의 [최신 릴리스](https://github.com/nix-community/NixOS-WSL/releases/latest)에서 `nixos.wsl`을 내려받는다. WSL 2.4.4 이상이라면 파일이 있는 디렉터리에서 다음을 실행한다.

```powershell
wsl --install --from-file .\nixos.wsl --name NixOS
wsl -d NixOS
```

`--name`을 생략하면 기본 등록 이름도 `NixOS`다. `--location`으로 가상 디스크 위치를 별도로 정할 수 있다.

WSL 2.4.4보다 오래되어 `--from-file`을 지원하지 않으면 import 방식으로 등록한다.

```powershell
wsl --import NixOS $env:USERPROFILE\NixOS .\nixos.wsl --version 2
wsl -d NixOS
```

가능하면 먼저 `wsl --update`로 최신 설치 경로를 사용하는 편이 단순하다.

## 2.4 초기 `nixos` 사용자 준비

NixOS-WSL의 기본 사용자는 `nixos`이며 `wheel` 그룹에 속한다. WSL 안에서 먼저 암호를 설정한다.

```console
$ passwd
```

현재 NixOS-WSL 설치 문서는 첫 `nixos-rebuild`를 위해 채널 메타데이터를 한 번 갱신하도록 안내한다.

```console
$ sudo nix-channel --update
```

이 명령은 이미지 bootstrap에만 필요하다. 이후 시스템 빌드가 사용할 버전은 채널이 아니라 구성 저장소의 `flake.lock`이 결정한다.

## 2.5 GitHub에 빈 원격 저장소 만들기

[GitHub의 새 저장소 화면](https://github.com/new)에서 다음처럼 만든다.

1. 저장소 이름을 정한다. 이 자료에서는 `nixos-config`를 예로 사용한다.
2. 공개 범위를 선택한다.
3. **Add a README file**, **Add .gitignore**, **Choose a license**를 모두 선택하지 않는다.
4. **Create repository**를 누른 뒤 Quick setup 화면의 SSH URL을 기록한다.

SSH URL은 다음 모양이다.

```text
git@github.com:<github-user>/nixos-config.git
```

기존 로컬 파일을 처음 push할 것이므로 원격 저장소를 비워 두어야 불필요한 병합을 피할 수 있다. 공개 범위는 다음 기준으로 정한다.

| 선택 | 적합한 경우 | 주의점 |
|---|---|---|
| Private | 개인 정보나 호스트 구성을 공개하고 싶지 않을 때 | 새 컴퓨터마다 clone 전에 GitHub 인증이 필요하다. |
| Public | 예제를 공유하고 어디서나 인증 없이 읽고 싶을 때 | 이메일, 호스트 정보, 회사 설정까지 공개 가능한지 검토해야 한다. |

어느 쪽이든 암호, API 토큰, SSH 개인 키, 복호화 키를 커밋하지 않는다. 이 자료는 처음에는 Private 저장소를 권장한다.

## 2.6 임시 Git·OpenSSH 셸 열기

아직 영구 사용자 구성을 적용하지 않았으므로 Git과 SSH 클라이언트를 임시 셸에서 실행한다. 2.4절에서 갱신한 NixOS 채널을 이용하는 기존 `nix-shell` 명령이 이 bootstrap 단계에 적합하다.

```console
$ nix-shell -p git openssh
```

`<nixpkgs>`를 찾지 못하면 갱신한 root 채널 경로를 명시한다.

```console
$ nix-shell \
    -I nixpkgs=/nix/var/nix/profiles/per-user/root/channels/nixos \
    -p git openssh
```

도구가 들어왔는지 확인한다.

```console
$ git --version
$ ssh -V
```

여기서 기존 `nix-shell`을 사용하는 것은 최종 구성 방식을 채널로 바꾸는 것이 아니다. Git조차 없는 초기 이미지에서 필요한 도구만 가져오는 일회성 bootstrap이다. 최종 시스템과 사용자 구성은 계속 `flake.lock`을 사용한다.

다음 Flake 명령을 bootstrap 대안으로 사용하지 않는다.

```console
# 사용하지 않음: github: fetcher는 비인증 GitHub API 한도에 걸릴 수 있다.
$ nix shell github:NixOS/nixpkgs/nixos-26.05#git

# 사용하지 않음: git+https fetcher는 외부 git 실행 파일을 먼저 요구한다.
$ nix shell 'git+https://github.com/NixOS/nixpkgs?ref=nixos-26.05#git'
```

첫 번째 방식은 GitHub REST API 한도가 소진되면 `HTTP error 403`을 낸다. 두 번째 방식은 아직 Git이 없으므로 `executing "git": No such file or directory`를 낸다. SSH 키 등록은 Git clone/push 인증이며 `github:` fetcher의 REST API 인증과는 별개다.

`nix-shell`은 새 셸을 연다. 2장의 첫 push가 끝날 때까지 이 셸에서 계속 작업한다. 마지막에 `exit`하면 임시 도구는 현재 환경에서 사라지고, 이후에는 Home Manager가 설치한 Git을 사용한다.

## 2.7 NixOS-WSL에서 GitHub SSH 인증 만들기

이 안내서에서 사용할 기본 키가 있는지 먼저 확인한다.

```console
$ test -f ~/.ssh/id_ed25519.pub && echo ssh-key:exists
```

아무것도 나오지 않으면 새 키를 만든다. 이메일은 자신의 GitHub 계정 이메일로 바꾼다. 다른 이름의 기존 키를 사용하려면 이후 공개 키 경로도 그 이름으로 바꾼다.

```console
$ ssh-keygen -t ed25519 -C "<github-email>"
```

파일 위치 질문에는 Enter를 눌러 기본값 `~/.ssh/id_ed25519`를 사용한다. 개인 키를 보호하려면 passphrase를 설정한다. 공개 키만 Windows 클립보드에 복사한다.

```console
$ clip.exe < ~/.ssh/id_ed25519.pub
```

GitHub의 **Settings → SSH and GPG keys → New SSH key**에서 붙여 넣고 **Authentication Key**로 등록한다. 개인 키인 `~/.ssh/id_ed25519`는 GitHub나 구성 저장소에 올리지 않는다.

연결을 시험한다.

```console
$ ssh -T git@github.com
```

첫 연결에서는 표시된 host key fingerprint가 [GitHub가 공개한 fingerprint](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/githubs-ssh-key-fingerprints)와 같은지 확인한 뒤 `yes`를 입력한다. 성공 메시지에 자신의 GitHub 사용자 이름이 나오면 된다. GitHub는 SSH 셸을 제공하지 않으므로 성공해도 이 명령의 종료 코드는 1일 수 있다.

## 2.8 제공 예제를 구성 디렉터리로 복사하기

이 안내서의 [`assets/example-config`](../assets/example-config/README.md)가 개인 구성 저장소의 시작점이다. 안내서 저장소를 내려받은 위치를 `<guide-root>`라고 하면 다음처럼 복사한다.

```console
$ mkdir -p ~/.config
$ cp -R <guide-root>/nixos-wsl-dev-environment/assets/example-config \
    ~/.config/nixos
$ cd ~/.config/nixos
```

예를 들어 안내서를 Windows의 `C:\Users\me\llmBook`에 내려받았다면 WSL 경로는 `/mnt/c/Users/me/llmBook`이다.

```console
$ cp -R /mnt/c/Users/me/llmBook/nixos-wsl-dev-environment/assets/example-config \
    ~/.config/nixos
```

위 로컬 경로 방식과 다음 clone 방식 중 하나만 사용한다. GitHub에서 이 안내서를 보고 있다면 먼저 안내서 저장소를 clone한 뒤 같은 디렉터리를 복사해도 된다.

```console
$ git clone <guide-repository-url> /tmp/nixos-wsl-guide
$ mkdir -p ~/.config
$ cp -R /tmp/nixos-wsl-guide/nixos-wsl-dev-environment/assets/example-config \
    ~/.config/nixos
$ cd ~/.config/nixos
```

`~/.config/nixos`가 이미 존재하면 덮어쓰지 말고 내용을 먼저 확인한다. 예제의 기본 사용자 이름은 NixOS-WSL 초기 사용자와 같은 `nixos`이므로 첫 적용에서는 바꾸지 않는다. 사용자 이름 변경은 정상 부팅과 첫 push를 확인한 뒤 8장의 절차로 수행한다.

## 2.9 로컬 저장소 초기화와 첫 `flake.lock` 생성

Git 커밋 작성자 정보를 이 저장소에만 설정하고, 2.5에서 만든 SSH URL을 원격으로 연결한다.

```console
$ git init -b main
$ git config --local user.name "<git-user-name>"
$ git config --local user.email "<git-email>"
$ git remote add origin git@github.com:<github-user>/nixos-config.git
$ git remote -v
```

먼저 예제 파일을 Git에 추가한다. 로컬 Git Flake는 추적되지 않은 파일을 평가 입력에서 제외할 수 있기 때문이다.

```console
$ git add .
$ git status --short
```

이제 이 저장소의 잠금 파일을 **처음 한 번만** 생성하고 바로 Git에 추가한다.

```console
$ nix --extra-experimental-features "nix-command flakes" flake lock
$ git add flake.lock
$ test -f flake.lock && echo flake.lock:ok
```

이것은 원본 저장소를 만드는 첫 컴퓨터이므로 새 입력 리비전을 선택하는 단계다. 이후 컴퓨터의 복원 과정에서는 `nix flake lock`이나 `nix flake update`를 실행하지 않고 커밋된 잠금 파일을 그대로 사용한다.

### GitHub API rate limit가 계속되는 경우

예제 `flake.nix`의 `github:` 입력도 잠금을 만들 때 GitHub REST API를 사용한다. `HTTP error 403`과 `API rate limit exceeded`가 나오면 SSH 키가 아니라 Nix의 GitHub API 인증 문제다. 한도가 초기화될 때까지 기다리거나, 저장소에 커밋하지 않을 GitHub access token을 이번 명령에만 전달한다.

```console
$ read -rsp "GitHub token: " GITHUB_TOKEN; echo
$ nix --extra-experimental-features "nix-command flakes" \
    --option access-tokens "github.com=$GITHUB_TOKEN" \
    flake lock
$ unset GITHUB_TOKEN
$ git add flake.lock
```

토큰 문자열을 명령에 직접 적으면 셸 기록에 남을 수 있다. `flake.nix`, Home Manager 설정, dotfiles에도 토큰을 넣지 않는다.

## 2.10 첫 빌드와 적용

먼저 Flake 출력을 평가하고 WSL 시스템을 build한다.

```console
$ nix --extra-experimental-features "nix-command flakes" flake show
$ sudo nixos-rebuild build \
    --option experimental-features "nix-command flakes" \
    --flake .#wsl
```

build가 성공한 뒤에만 시스템을 전환한다.

```console
$ sudo nixos-rebuild switch \
    --option experimental-features "nix-command flakes" \
    --flake .#wsl
```

그다음 같은 잠금 파일의 standalone Home Manager를 먼저 build하고 최초 적용한다.

```console
$ nix run .#home-manager -- build --flake .#nixos
$ nix run .#home-manager -- switch --flake .#nixos
```

기본 도구를 확인한다.

```console
$ git --version
$ uv --version
$ rustup --version
$ test -f ~/.config/nvim/init.lua && echo nvim-config:ok
```

## 2.11 첫 커밋과 GitHub push

비밀 파일이 섞이지 않았는지 `git status`와 staged diff를 확인한다.

```console
$ git status --short
$ git diff --cached --stat
$ git diff --cached
```

문제가 없으면 첫 커밋을 만들고 GitHub로 push한다.

```console
$ git commit -m "Bootstrap NixOS-WSL environment"
$ git push -u origin main
$ git status --short
```

마지막 `git status --short`가 아무것도 출력하지 않고 GitHub 저장소에 `flake.nix`, `flake.lock`, `hosts/`, `modules/`, `dotfiles/`가 보이면 원본 저장소가 준비된 것이다. 임시 셸을 닫고 WSL 세션에서도 나온다.

```console
$ exit  # 임시 Nix 셸 종료
$ exit  # NixOS-WSL 세션 종료
```

Windows에서 배포판을 한 번 재시작해 로그인 셸과 WSL 설정을 새 세션에 반영한다.

```powershell
wsl --terminate NixOS
wsl -d NixOS
```

이제 3장에서 방금 만든 파일들이 어떤 역할로 분리되어 있는지 읽는다. 다른 컴퓨터에서는 이 초기화 절차를 반복하지 않고 7장의 clone 기반 복원 절차를 사용한다.

## 흔한 오류

| 증상 | 원인 | 해결 |
|---|---|---|
| `--no-distribution` 또는 `--from-file`을 인식하지 못함 | Windows/WSL이 오래됨 | `wsl --update` 또는 공식 구형 설치/import 절차 사용 |
| `sudo`가 암호를 받지 않음 | 초기 암호 미설정 | `passwd` 또는 `sudo passwd nixos` 실행 |
| `Permission denied (publickey)` | 공개 키가 GitHub 계정에 없거나 다른 키를 사용함 | 공개 키 등록과 `ssh -T git@github.com`부터 다시 확인 |
| `API rate limit exceeded`와 HTTP 403 | `github:` fetcher의 비인증 REST API 한도 소진 | 기다리거나 `access-tokens`로 GitHub token을 명령에만 전달 |
| `executing "git": No such file or directory` | Git이 없는 bootstrap에서 `git+https:` fetcher 사용 | 2.6절의 채널 기반 `nix-shell -p git openssh` 사용 |
| push에서 `non-fast-forward` 발생 | GitHub 저장소를 README 등으로 초기화함 | 첫 원격 저장소는 비워서 만들거나 기존 원격 커밋을 의도적으로 병합 |
| Flake가 새 파일을 찾지 못함 | 파일이 Git 미추적 상태임 | `git add` 후 다시 평가 |
| `flake.lock`이 없다고 나옴 | 첫 잠금 생성 또는 `git add` 누락 | 첫 컴퓨터에서 `nix flake lock` 후 `git add flake.lock` |
| Flake 기능이 비활성화됨 | 아직 시스템 설정 적용 전 | bootstrap 명령에 `--extra-experimental-features` 유지 |

## 요약

- 첫 컴퓨터에서는 clone할 구성 저장소가 없으므로 GitHub에 빈 원격부터 만든다.
- 초기 Git과 OpenSSH는 갱신한 NixOS 채널의 `nix-shell`로만 임시 제공하고, 최종 환경은 Flake로 적용한다.
- `flake.lock`은 첫 원본 저장소에서 생성·커밋하고, 이후 복원에서는 갱신하지 않는다.
- build 성공 후 시스템과 Home Manager를 적용하고 첫 커밋을 push한다.
- 두 번째 컴퓨터부터는 7장의 clone 기반 복원 절차를 사용한다.

## 추가 읽을거리

- [Microsoft WSL 설치](https://learn.microsoft.com/windows/wsl/install)
- [NixOS-WSL 공식 설치 문서](https://nix-community.github.io/NixOS-WSL/install.html)
- [NixOS-WSL 릴리스](https://github.com/nix-community/NixOS-WSL/releases)
- [기존 로컬 코드를 GitHub에 추가하기](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github)
- [GitHub SSH 키 생성](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent?platform=linux)
- [GitHub SSH 연결 시험](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/testing-your-ssh-connection?platform=linux)
- [GitHub REST API rate limit](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api)
- [Nix `access-tokens` 설정](https://releases.nixos.org/nix/nix-2.31.3/manual/command-ref/conf-file.html#conf-access-tokens)

[← 1장](../01_mental_model/chapter.md) · [목차](../index.md) · [3장: 저장소 구조와 Flake →](../03_repository_architecture/chapter.md)
