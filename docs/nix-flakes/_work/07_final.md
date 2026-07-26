---
title: 출판 전 최종 Markdown 원고
version: 1.0
status: final
owner: agent
updated: 2026-07-24
target_reader: Nix 기초는 알지만 Flake는 처음인 개발자
topic: Nix Flake 입문
---

# Nix Flake 입문: 출판 전 최종 원고

이 자료의 최종 원고는 MkDocs 챕터형 산출물이므로 아래 일곱 파일을 하나의 원고
집합으로 확정한다.

1. `index.md`
2. `01-mental-model.md`
3. `02-inputs-and-locks.md`
4. `03-development-shells.md`
5. `04-packages-and-apps.md`
6. `05-checks-and-multi-system.md`
7. `06-workflow-and-troubleshooting.md`

## 학습 목표

1. input, output, lock file의 역할을 구분한다.
2. 명령이 선택하는 system별 output 경로를 추적한다.
3. Nixpkgs의 `cowsay`가 포함된 개발 셸을 작성한다.
4. `writeShellApplication` package와 app을 만든다.
5. formatter와 실행 check를 Flake output으로 제공한다.
6. input을 제한적으로 갱신하고 실패를 단계별로 진단한다.

## 최종 설명 흐름

```text
Flake의 경계
  -> input URL과 lock revision
  -> devShells와 cowsay
  -> packages와 apps
  -> formatter와 checks
  -> 다중 system
  -> update와 troubleshooting
```

## 최종 예제

`assets/flake-greeter/`는 다음 파일을 포함한다.

```text
assets/flake-greeter/
├── README.md
├── flake.lock
└── flake.nix
```

예제의 공개 출력은 다음과 같다.

```text
apps.<system>.default
checks.<system>.greeting
checks.<system>.package
devShells.<system>.default
formatter.<system>
packages.<system>.default
packages.<system>.flake-greeter
```

개발 셸은 Nixpkgs의 `cowsay`와 `nixfmt`를 제공한다. package는
`writeShellApplication`으로 생성하며 `cowsay`를 runtime dependency로 선언한다.
app은 package의 Store 실행 파일을 가리키고, greeting check는 실제 출력에 지정한
문자열이 있는지 검사한다.

## 최종 검증 명령

```console
nix flake show
nix develop --command cowsay "development shell"
nix build
./result/bin/flake-greeter "built package"
nix run . -- "flake app"
nix fmt flake.nix
nix flake check
nix flake check --all-systems --no-build
```

NixOS WSL의 Nix 2.34.8에서 x86_64-linux의 평가·build·dev shell·app·check가
통과했다. 네 system의 output schema는 `--all-systems --no-build`로 평가됐다.
Nixpkgs revision은 `flake.lock`에 고정했다.

## 흔한 오류의 최종 분류

| 단계 | 대표 원인 | 첫 확인 |
|---|---|---|
| 소스 수집 | Git 미추적 파일 | `git status --short` |
| 잠금 | 의도하지 않은 input update | `git diff -- flake.lock` |
| 평가 | output 이름·system·Nix 문법 | `nix flake show` |
| build | package 또는 check 실패 | `nix flake check -L` |
| 실행 | app 경로·runtime dependency | `ls result/bin`, 직접 실행 |

## 참고문헌

- NixOS Foundation, [Flakes](https://nix.dev/concepts/flakes.html), 확인 2026-07-24.
- NixOS Foundation, [Nix 2.34 Reference Manual](https://nix.dev/manual/nix/2.34/), 확인 2026-07-24.
- NixOS Foundation, [Nixpkgs 26.05 Reference Manual](https://nixos.org/manual/nixpkgs/stable/), 확인 2026-07-24.

## 최종 원고 점검

- [x] 학습 목표가 본문과 연습문제에 반영되어 있다.
- [x] 내부 작업 메모가 최종 챕터에서 제거되어 있다.
- [x] 기술 검증이 완료되어 있다.
- [x] 용어와 표기법이 일관적이다.
- [x] 참고문헌과 추가 읽을거리가 정리되어 있다.
- [x] MkDocs 챕터형 산출물로 분리되어 있다.
