# 9. 업데이트, 롤백, 문제 해결

## 학습 목표

1. 복원과 업데이트를 서로 다른 절차로 운영한다.
2. 시스템, 사용자, 프로젝트 중 실패한 계층을 식별한다.
3. NixOS와 Home Manager 세대를 독립적으로 롤백한다.

## 9.1 안전한 업데이트 루틴

복원에서는 `flake.lock`을 유지하지만 업데이트에서는 의도적으로 바꾼다.

```console
$ cd ~/.config/nixos
$ nix flake update
$ git diff -- flake.lock
$ nix fmt
$ sudo nixos-rebuild build --flake .#wsl
$ home-manager build --flake .#nixos
```

두 빌드가 성공한 뒤 전환한다.

```console
$ sudo nixos-rebuild switch --flake .#wsl
$ home-manager switch --flake .#nixos
```

동작을 확인한 뒤 잠금 파일을 커밋한다.

```console
$ git add flake.lock
$ git commit -m "Update Nix inputs"
```

이 커밋은 Nixpkgs, Home Manager, NixOS-WSL 입력의 변경을 하나의 검토 단위로 만든다. 특정 입력만 갱신하려면 사용 중인 Nix의 `nix flake update --help`에서 입력별 문법을 먼저 확인한다. Nix CLI 버전에 따라 이 문법이 달라질 수 있다.

프로젝트 LazyVim plugin은 시스템 Flake와 별도 업데이트 단위다. 해당 프로젝트에서
Neovim을 열고 `:Lazy update`를 실행한 뒤 lock diff와 프로젝트 검증을 함께 수행한다.

```console
$ cd <project>
$ nvim .
# Neovim에서 :Lazy update, :LazyHealth
$ git diff -- .lazy-lock.json
$ git add .lazy-lock.json
$ git commit -m "Update project editor plugins"
```

다른 컴퓨터의 복원에서는 update가 아니라 `:Lazy restore`를 사용한다.

## 9.2 롤백 단위

시스템 전환이 문제라면 NixOS 세대를 되돌린다.

```console
$ sudo nixos-rebuild switch --rollback
```

사용자 설정만 문제라면 Home Manager 세대를 확인하고 직전 세대로 전환한다.

```console
$ home-manager generations
$ home-manager switch --rollback
```

Git의 `flake.lock`도 문제가 생기기 전 커밋으로 되돌려야 다음 rebuild가 같은 상태를 유지한다. 세대 롤백은 현재 실행 상태를 바꾸고, Git 되돌리기는 다음 빌드의 입력을 바꾼다. 둘은 목적이 다르다.

프로젝트의 `.nvmrc`, `.python-version`, `rust-toolchain.toml`, `.lazy.lua`,
`.lazy-lock.json` 변경은 NixOS 세대 롤백 대상이 아니다. 프로젝트 Git 이력과 언어별
설치 상태를 확인하고 이전 lock 커밋에서 `:Lazy restore`를 실행한다.

## 9.3 계층별 진단 순서

```text
명령 자체가 없거나 로그인 셸이 다름
  → NixOS / Home Manager 적용 상태

도구는 있지만 런타임 선택이 다름
  → .nvmrc / .python-version / rust-toolchain.toml

런타임은 맞지만 빌드가 실패
  → 프로젝트 lockfile / 네이티브 라이브러리

LSP는 맞지만 editor plugin 구성이 다름
  → .lazy.lua / .lazy-lock.json / Neovim trust
```

처음부터 `nixos-rebuild`를 반복하기보다 실패한 소유권 계층에서 시작한다.

## 9.4 오류 표

| 증상 | 원인 | 확인 | 해결 |
|---|---|---|---|
| 새 `.nix` 파일을 찾지 못함 | Git 미추적 파일은 Flake 입력에서 빠짐 | `git status --short` | `git add` 후 다시 build |
| bootstrap에서 `API rate limit exceeded`와 HTTP 403 | `github:` fetcher의 비인증 GitHub REST API 한도 소진 | 오류 URL이 `api.github.com`인지 확인 | `nix-shell -p git openssh`로 bootstrap; Flake 잠금은 대기 또는 `access-tokens` 사용 |
| bootstrap에서 `executing "git": No such file or directory` | Git 설치 전에 `git+https:` fetcher 사용 | `command -v git` | 채널 기반 `nix-shell -p git openssh` 사용 |
| `home-manager`가 기존 파일과 충돌 | 관리 대상에 수동 파일 존재 | 오류가 지목한 경로 | 백업 후 모듈/dotfiles로 원본 이동 |
| `nvm: command not found` | zsh 초기화 또는 로그인 셸 문제 | `echo $SHELL`, `type nvm` | WSL 재시작, `nvm.nix` 적용 확인 |
| `.nvmrc` 버전이 설치되지 않음 | 훅 미실행 또는 값이 유효하지 않음 | `nvm_find_nvmrc`, `nvm install` | 파일 내용과 NVM 출력 확인 |
| Python/Node/Rust 바이너리가 실행되지 않음 | 동적 로더 또는 공유 라이브러리 누락 | 오류의 interpreter/library | `nix-ld`와 추가 라이브러리 검토 |
| `native` 출력이 없음 | 하드웨어 파일 부재 또는 Git 미추적 | `git ls-files hosts/native` | 파일 복사 후 `git add` |
| 복원 직후 `flake.lock` 변경 | 복원 중 update 실행 | `git diff flake.lock` | 잠긴 커밋으로 되돌리고 다시 build |
| Windows 명령이 이름으로 실행되지 않음 | Windows PATH 제외 정책 | `wsl.interop.includePath` | 명시 경로 또는 옵션 변경 |
| `.lazy.lua`가 적용되지 않음 | 프로젝트 파일을 신뢰하지 않았거나 내용이 변경됨 | Neovim trust 요청, `:messages` | 파일 검토 후 `:trust`, Neovim 재실행 |
| 프로젝트 plugin 버전이 다름 | `.lazy-lock.json` 미복원 또는 실수로 update 실행 | lock diff와 현재 lock 경로 | Git lock 복원 후 `:Lazy restore` |

## 9.5 사용자 이름 변경

이미 설치된 NixOS-WSL에서 기본 사용자 이름을 바꿀 때는 일반 `switch`를 사용하지 않는다. 공식 절차의 핵심은 다음과 같다.

1. `flake.nix`의 `username`, NixOS 사용자 선언, `wsl.defaultUser`, Home Manager 홈 경로를 새 이름에 맞춘다.
2. WSL 안에서 부팅 세대를 만든다.

   ```console
   $ sudo nixos-rebuild boot --flake .#wsl
   ```

3. 셸을 나간 뒤 PowerShell에서 배포판을 종료한다.

   ```powershell
   wsl --terminate NixOS
   wsl -d NixOS --user root exit
   wsl --terminate NixOS
   wsl -d NixOS
   ```

4. 새 사용자로 들어온 뒤 Home Manager 출력을 적용한다.

공식 문서는 기존 WSL 사용자를 변경할 때 `nixos-rebuild switch`가 새 계정을 잘못 구성할 수 있다고 경고한다. 사용자 이름은 가능하면 저장소를 처음 만들 때 확정한다.

## 9.6 릴리스 업그레이드

26.05에서 다음 NixOS 릴리스로 이동할 때는 다음을 함께 검토한다.

- `nixpkgs.url`의 브랜치
- Home Manager의 대응 `release-YY.MM` 브랜치
- NixOS-WSL 릴리스 노트
- NixOS와 Home Manager 릴리스 노트
- 폐기되거나 이름이 바뀐 옵션

`system.stateVersion`과 `home.stateVersion`은 자동으로 올리지 않는다. 릴리스 브랜치와 상태 버전은 서로 다른 개념이다.

## 9.7 비밀과 개인 데이터

다음 값은 평문 구성 저장소에 넣지 않는다.

- SSH 개인 키
- Git 호스팅 토큰
- npm·PyPI 인증 토큰
- 클라우드 자격 증명
- 조직 내부 인증서의 개인 키

이 자료는 비밀 관리 체계를 포함하지 않는다. 초기에는 복원 후 별도로 배치하고, 필요해지면 sops-nix나 agenix 같은 도구를 별도 위협 모델과 함께 설계한다.

## 9.8 운영 체크리스트

### 평상시 변경

1. Nix 또는 dotfile 원본 수정
2. `nix fmt`
3. 시스템 변경이면 `nixos-rebuild build`
4. 사용자 변경이면 `home-manager build`
5. 성공한 계층만 `switch`
6. 동작 확인 후 Git 커밋

### 새 머신 복원

1. 채널 기반 `nix-shell`에서 임시 Git·OpenSSH 준비
2. 잠긴 저장소 clone
3. 시스템 build/switch
4. Home Manager bootstrap/switch
5. 새 로그인 셸
6. 프로젝트 clone과 언어별 locked restore

### 문제 발생

1. 시스템·사용자·프로젝트 중 소유 계층 식별
2. 현재 Git diff와 잠금 파일 확인
3. 해당 계층의 세대 또는 프로젝트 커밋 롤백
4. build로 수정 검증 후 switch

## 요약

- update는 잠금 파일을 바꾸고, restore는 잠금 파일을 유지한다.
- 시스템과 Home Manager는 독립적으로 빌드하고 롤백한다.
- 오류는 소유권 계층부터 찾는다.
- 기존 WSL 사용자 이름 변경에는 `boot`와 WSL 재시작 절차가 필요하다.
- 비밀은 평문 Flake나 dotfiles에 넣지 않는다.

## 추가 읽을거리

- [NixOS-WSL 사용자 이름 변경](https://nix-community.github.io/NixOS-WSL/how-to/change-username.html)
- [NixOS-WSL 복구 셸](https://nix-community.github.io/NixOS-WSL/troubleshooting/recovery-shell.html)
- [NixOS 안정판 매뉴얼](https://nixos.org/manual/nixos/stable/)
- [Home Manager 매뉴얼](https://nix-community.github.io/home-manager/)

[← 8장](../07_restore_workflow/chapter.md) · [목차](../index.md)
