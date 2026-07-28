---
title: "Nix Flake 입문: 개발 셸에서 패키지·앱·검사까지"
version: 1.0
updated: 2026-07-28
baseline: Nix 2.34, Nixpkgs 26.05
---

# Nix Flake 입문: 개발 셸에서 패키지·앱·검사까지

Flake를 처음 보면 `inputs`, `outputs`, `${system}`이 한꺼번에 등장한다. 예제는
복사할 수 있어도 어떤 명령이 어느 출력을 사용하는지 모르면 작은 수정도 시행착오가
된다.

이 자료는 Flake를 **잠긴 입력을 받아 이름 있는 출력을 만드는 함수**로 읽는다.
Nixpkgs의 `cowsay`가 들어 있는 개발 셸에서 시작해 패키지, 앱, formatter, check를
하나씩 추가한다. 마지막에는 네 가지 일반 플랫폼에 같은 출력을 제공하는 작은
`flake-greeter` 프로젝트를 완성한다.

코드 블록이 파일 내용을 나타낼 때는 블록 바로 위에 `파일:`과 경로를 표시한다.
`<project-root>`는 현재 실습 중인 Flake의 루트, 즉 `flake.nix`가 있는 디렉터리다.

## 학습 목표

이 자료를 마치면 다음 작업을 할 수 있다.

1. `flake.nix`의 `inputs`와 `outputs`, `flake.lock`의 역할을 설명한다.
2. `nix flake show` 결과에서 `nix develop`, `nix build`, `nix run`이 사용할 출력을 찾는다.
3. Nixpkgs의 `cowsay`를 제공하는 재현 가능한 개발 셸을 작성한다.
4. 작은 CLI를 package와 app으로 노출한다.
5. formatter와 check를 추가해 변경을 자동 검증한다.
6. input을 선택적으로 갱신하고 실패 지점을 평가·빌드·실행 단계로 분류한다.

## 전제 조건

- Git과 터미널 기본 명령을 사용할 수 있다.
- Nix가 설치되어 있다.
- Nix 속성 집합 `{ ... }`, 목록 `[ ... ]`, 함수 인자 `{ a, b }:`를 대략 읽을 수 있다.

다음 명령으로 기준 환경을 확인한다.

```console
$ nix --version
nix (Nix) 2.34.x

$ nix flake --help
```

이 자료는 NixOS/Nixpkgs 26.05에 포함된 Nix 2.34 계열을 기준으로 검증한다. Flake와
새 `nix` 명령은 공식 reference에서 여전히 experimental로 표시되므로 인터페이스가
바뀔 수 있다.

기능이 비활성화됐다는 오류가 나오면 사용자 설정
`~/.config/nix/nix.conf`에 다음 값을 넣는다.

파일: `~/.config/nix/nix.conf` (`experimental-features` 설정 부분)

```ini
experimental-features = nix-command flakes
```

NixOS의 기본 단일 파일 구성에서는 같은 의미를 다음처럼 표현한다.

파일: `/etc/nixos/configuration.nix` (`nix.settings.experimental-features` 설정 부분)

```nix
nix.settings.experimental-features = [
  "nix-command"
  "flakes"
];
```

이미 Flake 명령이 동작한다면 이 설정을 다시 추가할 필요가 없다.

## 이 자료에서 만드는 것

완성형 예제는 다음 출력을 제공한다.

```text
.
├── apps.<system>.default
├── checks.<system>.greeting
├── devShells.<system>.default
├── formatter.<system>
└── packages.<system>.default
```

개발 셸에는 Nixpkgs의 예제 패키지 `cowsay`와 `nixfmt`가 들어간다. 패키지
`flake-greeter`는 `cowsay`를 런타임 의존성으로 선언하며 `nix run`으로 바로 실행할
수 있다.

완성된 파일은 [`assets/flake-greeter/`](./assets/flake-greeter/README.md)에 있다.

## 읽는 순서

1. [Flake의 역할과 출력 트리](./01-mental-model.md)
2. [입력과 `flake.lock`](./02-inputs-and-locks.md)
3. [개발 셸에 `cowsay` 추가하기](./03-development-shells.md)
4. [패키지와 앱 만들기](./04-packages-and-apps.md)
5. [검사, formatter, 여러 시스템](./05-checks-and-multi-system.md)
6. [운영 워크플로와 문제 해결](./06-workflow-and-troubleshooting.md)

## 명령 지도

| 목적 | 명령 | 주로 찾는 출력 |
|---|---|---|
| 구조 보기 | `nix flake show` | 알려진 전체 output tree |
| 개발 셸 | `nix develop` | `devShells.<system>.default` |
| 빌드 | `nix build` | `packages.<system>.default` |
| 실행 | `nix run .` | `apps.<system>.default` |
| 서식 정리 | `nix fmt flake.nix` | `formatter.<system>` |
| 평가와 검사 | `nix flake check` | 표준 출력과 `checks.<system>.*` |
| input 갱신 | `nix flake update nixpkgs` | `flake.lock`의 `nixpkgs` node |

## 공식 참고 자료

- [nix.dev의 Flakes 개념 문서](https://nix.dev/concepts/flakes.html)
- [Nix 2.34 `nix flake` reference](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-flake.html)
- [Nixpkgs 26.05 reference manual](https://nixos.org/manual/nixpkgs/stable/)

[문서 목록으로 돌아가기](../index.md)
