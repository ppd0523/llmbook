# 4. WSL과 네이티브 시스템 설정 분리

## 학습 목표

1. 공통 NixOS 정책과 호스트별 설정을 분리한다.
2. 외부 언어 런타임을 위한 `nix-ld`의 역할과 한계를 이해한다.
3. WSL 호스트를 build한 뒤 안전하게 switch한다.

## 4.1 공통 시스템 모듈

[예제 `modules/nixos/common.nix`](../assets/example-config/modules/nixos/common.nix)는 호스트 종류와 무관한 최소 정책만 둔다.

파일: `modules/nixos/common.nix` (핵심 내용)

```nix
{
  pkgs,
  username,
  ...
}:
{
  nix.settings.experimental-features = [
    "nix-command"
    "flakes"
  ];

  programs.nix-ld.enable = true;
  programs.zsh.enable = true;

  users.users.${username} = {
    isNormalUser = true;
    extraGroups = [ "wheel" ];
    shell = pkgs.zsh;
  };
}
```

각 선언의 이유는 다음과 같다.

- `nix-command`, `flakes`: bootstrap 이후 추가 CLI 플래그 없이 Flake 명령 사용
- `programs.zsh.enable`: zsh를 유효한 로그인 셸로 시스템에 등록
- 사용자 선언: 계정, 관리자 그룹, 기본 셸을 호스트 상태로 관리
- `programs.nix-ld.enable`: 일반 Linux 동적 로더 경로를 기대하는 외부 바이너리 지원

## 4.2 왜 `nix-ld`가 필요한가

NixOS에는 일반 배포판의 `/lib64/ld-linux-x86-64.so.2` 경로가 기본으로 존재하지 않는다. Nixpkgs가 빌드한 패키지는 이 구조에 맞게 패치되지만, NVM·uv·rustup 같은 도구가 업스트림에서 내려받은 바이너리는 전통적인 Linux 경로를 기대할 수 있다.

`nix-ld`는 이 바이너리가 기대하는 동적 로더 경로와 라이브러리 집합을 제공한다. 이 자료처럼 “버전 관리자 자체는 Nix, 런타임은 업스트림 도구”인 혼합 설계에서 실용적인 호환 계층이다.

모든 네이티브 의존성을 자동으로 해결하는 만능 계층은 아니다. 특정 Python wheel이나 Node 네이티브 애드온이 추가 라이브러리를 요구하면 `programs.nix-ld.libraries`를 보강하거나 해당 개발 라이브러리를 Nix 셸로 제공해야 한다.

## 4.3 WSL 호스트 모듈

파일: `hosts/wsl/default.nix` (핵심 내용)

```nix
{ username, ... }:
{
  networking.hostName = "nixos-wsl";

  wsl = {
    enable = true;
    defaultUser = username;
    interop.includePath = false;
  };

  system.stateVersion = "26.05";
}
```

`wsl.interop.includePath = false`는 Windows PATH를 Linux PATH에 자동으로 합치지 않는다. 동일한 명령 이름의 Windows 프로그램이 먼저 선택되는 일을 막아 개발 셸의 재현성을 높인다. 대신 `code.exe`, `powershell.exe` 같은 Windows 명령을 이름만으로 실행하는 편의는 줄어든다.

Windows PATH 연동이 더 중요하면 이 값을 `true`로 바꿀 수 있다. 이 선택은 Nix 재현성의 필수 조건이 아니라 팀의 interop 정책이다.

## 4.4 네이티브 호스트 모듈

파일: `hosts/native/default.nix` (핵심 내용)

```nix
{ ... }:
{
  imports = [ ./hardware-configuration.nix ];
  networking.hostName = "nixos-native";
  system.stateVersion = "26.05";
}
```

`hardware-configuration.nix`에는 파일시스템, 블록 장치, 커널 모듈처럼 실제 머신에서 생성된 정보가 들어간다. WSL 파일로 대체하거나 다른 머신의 파일을 그대로 복사하지 않는다.

기존 네이티브 NixOS를 편입한다면 `system.stateVersion`도 그 호스트의 기존 값을 유지한다. 26.05는 26.05로 새로 설치한 시스템의 예시일 뿐이다.

## 4.5 build 후 switch

WSL 저장소 루트에서 먼저 결과만 빌드한다. 첫 전환 전에는 아직 시스템의 Flake 설정이 활성화되지 않았을 수 있으므로 일회성 Nix 옵션을 함께 전달한다.

```console
$ sudo nixos-rebuild build \
    --option experimental-features "nix-command flakes" \
    --flake .#wsl
```

빌드가 성공해야 현재 시스템을 바꾼다.

```console
$ sudo nixos-rebuild switch \
    --option experimental-features "nix-command flakes" \
    --flake .#wsl
```

이 전환 뒤에는 `nix.settings.experimental-features`가 시스템에 적용되므로 이후 명령에서 `--option`을 생략한다. 기본 셸 변경은 현재 셸 프로세스를 바꾸지 않는다. Windows PowerShell에서 배포판을 종료하고 다시 연다.

```powershell
wsl --terminate NixOS
wsl -d NixOS
```

다시 들어온 뒤 확인한다.

```console
$ echo $SHELL
/run/current-system/sw/bin/zsh
$ nix config show experimental-features
$ test -e /lib64/ld-linux-x86-64.so.2 && echo nix-ld:ok
```

## 흔한 오류

| 증상 | 원인 | 해결 |
|---|---|---|
| `wsl` 옵션을 찾지 못함 | 공식 NixOS-WSL 모듈 누락 | Flake modules에 `nixos-wsl.nixosModules.default` 추가 |
| 새 셸이 bash로 유지됨 | 현재 로그인 세션이 전환 전부터 실행 중 | 배포판 종료 후 다시 시작 |
| 다운로드한 바이너리가 `No such file`로 실패 | 동적 로더 경로가 없음 | `nix-ld` 적용 여부와 interpreter 확인 |
| Windows 명령이 PATH에서 사라짐 | `interop.includePath = false` | 명시 경로 사용 또는 정책을 `true`로 변경 |

## 요약

- 계정, 기본 셸, Flake 기능, 동적 로더는 시스템 설정이다.
- WSL 옵션과 실제 하드웨어 설정은 별도 호스트 모듈에 둔다.
- 외부 런타임은 `nix-ld`가 필요할 수 있지만 추가 네이티브 라이브러리는 별도다.
- 항상 build를 성공시킨 뒤 switch한다.

## 추가 읽을거리

- [NixOS-WSL 옵션](https://nix-community.github.io/NixOS-WSL/options.html)
- [nix-ld 설명](https://github.com/nix-community/nix-ld)
- [NixOS 안정판 매뉴얼](https://nixos.org/manual/nixos/stable/)

[← 3장](../03_repository_architecture/chapter.md) · [목차](../index.md) · [5장: Home Manager →](../05_home_manager/chapter.md)
