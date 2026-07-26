# 6. 운영 워크플로와 문제 해결

## 학습 목표

1. 완성형 Flake를 복제해 show, develop, build, run, check 순으로 검증한다.
2. input 갱신을 작은 변경 단위로 운영한다.
3. 오류를 소스 수집, 평가, build, 실행 단계로 분류한다.

## 6.1 종합 실습 준비

저장소 루트에서 완성형 예제를 작업 디렉터리로 복사한다.

```console
$ cp -R docs/nix-flakes/assets/flake-greeter ./flake-greeter
$ cd flake-greeter
$ git init
$ git add flake.nix README.md
```

이미 다른 Git 저장소 안으로 복사했다면 `git init`은 생략하고 새 파일만 `git add`한다.
잠금 파일을 생성한다.

```console
$ nix flake lock
$ git add flake.lock
```

이 시점의 파일은 다음과 같다.

```text
flake-greeter/
├── README.md
├── flake.lock
└── flake.nix
```

## 6.2 표준 검증 사다리

다음 순서는 앞 단계가 성공해야 뒤 단계의 실패를 의미 있게 해석할 수 있도록
배치되어 있다.

### 1단계: Git 소스 확인

```console
$ git status --short
```

필요한 새 파일이 추적 대상인지 확인한다. Nix가 “파일을 찾을 수 없다”고 말할 때
가장 먼저 볼 지점이다.

### 2단계: 잠금과 metadata 확인

```console
$ nix flake metadata
```

Nixpkgs의 original reference가 `nixos-26.05`인지, locked revision이 존재하는지
확인한다.

### 3단계: output tree 평가

```console
$ nix flake show
```

현재 system 아래에 `packages`, `apps`, `devShells`, `formatter`, `checks`가 보이는지
확인한다.

### 4단계: 개발 셸 확인

```console
$ nix develop -c sh -c 'command -v cowsay && command -v flake-greeter'
$ nix develop --command cowsay "development dependency"
```

`cowsay`와 프로젝트 package가 개발 셸의 PATH에 들어왔는지 확인한다.

### 5단계: formatter와 check

```console
$ nix fmt flake.nix
$ git diff -- flake.nix
$ nix flake check
```

formatter 변경을 검토한 뒤 package와 greeting check를 build한다.

### 6단계: package와 app 실행

```console
$ nix build
$ ./result/bin/flake-greeter "built package"
$ nix run . -- "default app"
```

Store 결과를 직접 실행하는 경로와 app 진입점을 모두 검증한다.

## 6.3 변경을 추가하는 작은 루프

Flake 변경 하나를 다음 루프로 처리한다.

```text
한 출력 수정
  -> git add로 소스 포함
  -> nix flake show
  -> 관련 명령 단독 검증
  -> nix flake check
  -> git diff 검토
  -> commit
```

예를 들어 `devShells`에 `pkgs.jq`를 추가했다면 먼저 다음처럼 확인한다.

```console
$ nix develop --command jq --version
$ nix flake check
```

package code를 바꿨다면 build와 run까지 확인한다.

```console
$ nix build
$ nix run . -- "changed"
$ nix flake check
```

모든 출력과 input을 한꺼번에 바꾸면 어느 변경이 실패를 만들었는지 알기 어렵다.

## 6.4 input 업데이트 운영

현재 잠금을 먼저 검증하고 작업 트리를 깨끗하게 만든다.

```console
$ nix flake check
$ git status --short
```

Nixpkgs만 갱신한다.

```console
$ nix flake update nixpkgs
$ git diff -- flake.lock
$ nix flake check
$ nix run . -- "updated input"
```

성공하면 lock만 별도 commit으로 남긴다.

```console
$ git add flake.lock
$ git commit -m "chore: update nixpkgs input"
```

실패하면 build log와 lock diff를 보존해 원인을 조사하거나, 변경을 채택하지 않기로
했다면 복구한다.

```console
$ git restore flake.lock
$ nix flake check
```

`flake.nix`의 branch를 `nixos-26.05`에서 새 release로 바꾸는 작업은 단순 revision
갱신보다 큰 migration이다. release notes를 읽고 별도 변경으로 다룬다.

## 6.5 네 단계로 오류 분류하기

### 소스 수집 오류

대표 증상:

- 로컬 파일이 없다고 나온다.
- import path가 source에 존재하지 않는다.
- dirty tree 또는 untracked file과 관련된 결과가 예상과 다르다.

확인:

```console
$ git status --short
$ git ls-files
```

새 소스를 `git add`하고 상대 경로가 Flake root 기준으로 맞는지 확인한다.

### 평가 오류

대표 증상:

- `undefined variable`
- `attribute ... missing`
- `infinite recursion`
- app이나 package output type 오류

확인:

```console
$ nix flake show
$ nix flake check --no-build
```

문법, output 경로, 함수 인자, `self` 참조를 확인한다. `--show-trace`는 깊은 평가
stack을 볼 때 사용한다.

```console
$ nix flake show --show-trace
```

### build 오류

대표 증상:

- derivation build 실패
- check script의 종료 상태가 0이 아님
- 지원하지 않는 system 또는 package

확인:

```console
$ nix build -L
$ nix flake check -L
```

`-L`은 full build log를 표시한다. 실패한 check를 이름으로 직접 build할 수도 있다.

```console
$ nix build .#checks.x86_64-linux.greeting -L
```

명령의 system 문자열은 자신의 현재 system으로 바꾼다.

### 실행 오류

대표 증상:

- app의 `program` 파일이 없음
- runtime command를 찾지 못함
- application 인자가 예상과 다르게 전달됨

확인:

```console
$ nix build
$ ls -la result/bin
$ ./result/bin/flake-greeter "direct"
$ nix run . -- "through app"
```

직접 실행은 되고 app만 실패하면 `apps.<system>.default.program`을 본다. 개발 셸에서는
되고 직접 실행이 실패하면 package의 `runtimeInputs`를 본다.

## 6.6 흔한 진단 패턴

| 증상 | 단계 | 가장 먼저 확인할 것 |
|---|---|---|
| `flake.nix` parse 오류 | 평가 | 괄호, 세미콜론, formatter |
| output을 제공하지 않는다는 오류 | 평가 | `nix flake show`, 현재 system, `default` 이름 |
| package가 현재 platform에서 unavailable | 평가/build | 지원 system 목록과 package metadata |
| check에서 `grep`을 못 찾음 | build | `nativeBuildInputs` |
| `cowsay: command not found` | 실행 | package의 `runtimeInputs` |
| 새 script가 없음 | 소스 수집 | `git status`, `git add` |
| update 뒤만 실패 | 잠금/build | `flake.lock` diff와 Nixpkgs 변경 |

## 6.7 CI에 연결하기

CI의 최소 검증은 다음 두 명령으로 시작할 수 있다.

```console
$ nix flake check
$ nix build
```

실행 결과가 check에 이미 포함되어 있다면 `nix flake check`가 핵심 진입점이 된다.
플랫폼을 지원한다고 선언했다면 Linux runner 하나에서 모든 플랫폼을 build했다고
간주하지 않는다. Linux와 macOS runner가 각자 현재 system의 check를 실행하게 한다.

lock update 자동화는 build 검증과 diff review 없이 자동 merge하지 않는다. input
revision 변경은 source code 변경과 같은 수준으로 검토한다.

## 6.8 NixOS·Home Manager Flake로 확장할 때

일반 프로젝트 Flake에서 익힌 원리는 시스템 구성에도 그대로 이어진다.

- `inputs`와 `flake.lock`이 Nixpkgs와 Home Manager source를 고정한다.
- `outputs`가 `nixosConfigurations.<host>` 또는 `homeConfigurations.<user>`를 만든다.
- 적용 명령은 각각 자신이 기대하는 output 경로를 탐색한다.
- `nix flake check`는 전환 전에 평가 가능한 오류를 찾는 공통 관문이 된다.

다만 NixOS와 Home Manager output은 system별 package를 만드는 것보다 activation과
state migration의 영향이 크다. 전체 구성은 다음 자료에서 이어서 다룬다.

- [NixOS-WSL 개발 환경을 Git으로 복원하기](../nixos-wsl-dev-environment/index.md)
- [NixOS에서 standalone Home Manager 운영하기](../home-manager-guide/index.md)

## 최종 과제

완성형 예제를 다음 요구사항에 맞게 확장한다.

1. 개발 셸에 Nixpkgs의 `jq`를 추가한다.
2. `flake-greeter`에 `--json` 인자가 들어오면 `jq`로 JSON 메시지를 출력하는 별도
   application을 설계한다.
3. 기본 cowsay 동작과 새 동작을 각각 검사하는 check를 만든다.
4. 현재 system에서 `nix fmt`, `nix flake check`, `nix run`을 통과시킨다.
5. `nixpkgs` input만 갱신하고 `flake.lock` diff와 검증 결과를 기록한다.

성공 기준은 “코드가 존재한다”가 아니라 각 공개 output이 해당 명령으로 실제
검증되는 것이다.

## 요약

- 검증은 Git 소스, metadata, 평가, 개발 셸, check, build, run 순으로 범위를 넓힌다.
- input update는 특정 input, lock diff, 전체 check, 별도 commit의 작은 단위로 다룬다.
- 오류를 소스 수집·평가·build·실행으로 나누면 확인할 파일과 명령이 선명해진다.
- 지원 플랫폼마다 실제 runner에서 check해야 다중 시스템 지원을 주장할 수 있다.

## 공식 자료

- [`nix flake` 명령 모음](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-flake.html)
- [`nix flake check`](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-flake-check.html)
- [`nix develop`](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-develop.html)
- [`nix run`](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-run.html)

[← 5장: 검사, formatter, 여러 시스템](./05-checks-and-multi-system.md) ·
[목차](./index.md) · [문서 목록](../index.md)
