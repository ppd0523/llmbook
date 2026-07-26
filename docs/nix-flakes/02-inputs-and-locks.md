# 2. 입력과 `flake.lock`

## 학습 목표

1. input URL과 잠긴 revision의 역할을 구분한다.
2. `nix flake lock`과 `nix flake update`를 올바른 상황에 사용한다.
3. 잠금 파일 변경을 검토하고 Git으로 복구한다.

## 2.1 URL만으로는 실제 revision이 정해지지 않는다

1장의 input은 release branch를 가리킨다.

```nix
inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
```

`nixos-26.05` branch는 시간이 지나면서 새 commit을 가리킬 수 있다. `flake.nix`만
보면 어느 시점의 Nixpkgs를 사용했는지 알 수 없다. Nix는 URL을 해석한 결과를
`flake.lock`에 기록한다.

| 파일 | 답하는 질문 |
|---|---|
| `flake.nix` | 어떤 입력 계열을 사용하고 어떤 출력을 만들 것인가? |
| `flake.lock` | 그 입력을 실제 어느 revision과 content hash로 고정했는가? |

따라서 둘은 경쟁 관계가 아니다. 선언과 해석 결과를 나누어 가진다.

## 2.2 잠금 그래프 읽기

`flake.lock`은 JSON 문서다. 실제 값은 생성 시점마다 달라지지만 구조는 다음과 같다.

```json
{
  "nodes": {
    "nixpkgs": {
      "locked": {
        "lastModified": 0,
        "narHash": "sha256-...",
        "owner": "NixOS",
        "repo": "nixpkgs",
        "rev": "...",
        "type": "github"
      },
      "original": {
        "owner": "NixOS",
        "ref": "nixos-26.05",
        "repo": "nixpkgs",
        "type": "github"
      }
    },
    "root": {
      "inputs": {
        "nixpkgs": "nixpkgs"
      }
    }
  },
  "root": "root",
  "version": 7
}
```

- `original`은 `flake.nix`에 선언한 의도를 정규화한 값이다.
- `locked.rev`는 실제 Git revision이다.
- `locked.narHash`는 가져온 소스 트리 내용의 hash다.
- `root.inputs`는 현재 Flake의 input 이름을 잠금 그래프 node에 연결한다.

`lastModified`나 lock schema version을 직접 편집하지 않는다. Nix 명령으로 갱신하고
Git diff를 검토한다.

## 2.3 생성과 갱신은 다른 작업이다

잠금 파일이 없거나 새 input만 추가했다면 다음 명령을 사용한다.

```console
$ nix flake lock
```

현재 Nix reference에서 `nix flake lock`은 누락된 lock entry를 만들되 이미 잠긴
input을 임의로 최신 revision으로 올리지 않는 명령이다.

기존 input을 의도적으로 갱신하려면 다음 명령을 사용한다.

```console
$ nix flake update nixpkgs
```

모든 input을 한꺼번에 갱신하려면 이름을 생략한다.

```console
$ nix flake update
```

변경 범위를 줄이려면 특정 input 이름을 지정하는 편이 안전하다. 예전 자료에서 볼 수
있는 `nix flake lock --update-input nixpkgs`는 최신 reference에서
`nix flake update nixpkgs`로 대체되었다.

## 2.4 업데이트 검토 루프

잠금 파일 갱신을 package manager의 lockfile 변경처럼 다룬다.

```console
$ git status --short
$ nix flake update nixpkgs
$ git diff -- flake.lock
$ nix flake check
$ nix build
$ nix run .
$ git add flake.lock
$ git commit -m "chore: update nixpkgs input"
```

아직 app이나 check가 없는 초기 Flake라면 존재하는 검증 명령만 실행한다. 핵심은
갱신, diff 확인, 검증, 커밋의 순서를 분리하는 것이다.

`flake.lock`에서 확인할 항목은 다음과 같다.

- 의도한 input node만 바뀌었는가?
- `original.ref`가 기대한 release branch인가?
- `locked.rev`, `lastModified`, `narHash`가 함께 바뀌었는가?
- 예상하지 못한 간접 input이 대량으로 바뀌지 않았는가?

## 2.5 복구는 Git으로 한다

업데이트 뒤 빌드가 실패하고 변경을 유지할 이유가 없다면 Git의 이전 잠금 파일로
돌린다.

```console
$ git restore flake.lock
$ nix flake check
```

이미 업데이트 commit을 만들었다면 팀의 Git 정책에 맞춰 해당 commit을 revert한다.
잠금 파일의 `rev`만 손으로 과거 값으로 바꾸면 `narHash`와 그래프가 맞지 않을 수 있다.

일시적으로 다른 input을 시험하되 잠금 파일을 쓰고 싶지 않다면 명령별
`--override-input`을 사용할 수 있다.

```console
$ nix build --override-input nixpkgs github:NixOS/nixpkgs/nixos-unstable
```

이 명령은 실험에 적합하지만 팀의 기준 revision을 기록하지 않는다. 채택하기로 했다면
`flake.nix`와 `flake.lock`을 정상 절차로 갱신한다.

## 2.6 재현성의 정확한 범위

잠금 파일은 Flake input을 고정한다. 그러나 다음 요소까지 자동으로 고정하는 것은
아니다.

- builder가 선언하지 않고 읽는 네트워크 자원
- 현재 시간이나 임의 값에 의존하는 작업
- Nix 밖에서 별도로 내려받는 언어 package
- Git에 포함되지 않은 로컬 파일
- 서로 다른 CPU·운영체제에서 본질적으로 달라지는 결과

따라서 “Flake를 사용했다”와 “모든 입력이 선언되고 빌드가 순수하다”는 같은 문장이
아니다. Flake는 재현 가능한 구성을 만들기 위한 강한 경계지만, 빌드 정의도 그 경계를
지켜야 한다.

## 2.7 Git 추적 상태

Flake가 Git 저장소 안에 있으면 평가 소스는 Git 작업 트리를 기준으로 수집된다. 새
Nix 파일이나 스크립트를 만들고 `git add`하지 않으면 Nix가 소스에서 제외해
“파일이 없다”는 오류가 날 수 있다.

다음 두 명령을 평가 전에 습관화한다.

```console
$ git status --short
$ git add flake.nix path/to/new-source
```

커밋까지 해야 평가되는 것은 아니다. staging하여 Git 추적 대상으로 만드는 것이
핵심이다.

## 직접 해보기

1. `nix flake metadata`에서 `Resolved URL`, `Locked URL`, revision을 찾아 역할을
   설명한다.
2. `nix flake update nixpkgs` 전후의 `flake.lock` diff에서 바뀐 field를 분류한다.
3. 갱신한 lock을 `git restore flake.lock`로 되돌리고 `nix flake metadata` 결과가
   이전 revision으로 돌아왔는지 확인한다.

## 흔한 오류

| 증상 | 원인 | 해결 |
|---|---|---|
| 팀원마다 package 버전이 다름 | `flake.lock`을 커밋하지 않음 | lock 생성·검증 후 Git에 포함 |
| 모든 input이 예상 밖으로 바뀜 | 이름 없이 `nix flake update` 실행 | diff 검토 후 복구, 특정 input만 갱신 |
| lock JSON을 고친 뒤 hash 오류 | field를 수동 편집 | Git으로 복구하고 Nix 명령 사용 |
| 새 소스 파일이 없다고 나옴 | Git 미추적 파일 | `git status`, `git add` 확인 |

## 요약

- `flake.nix`는 input 계열을, `flake.lock`은 실제 revision과 content hash를 기록한다.
- `nix flake lock`은 누락 entry 생성, `nix flake update`는 기존 input 갱신에 사용한다.
- 잠금 파일은 diff와 검증을 거쳐 코드와 함께 커밋한다.
- Flake input을 고정해도 선언 밖 입력까지 자동으로 재현 가능해지는 것은 아니다.

## 공식 자료

- [`nix flake lock`](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-flake-lock.html)
- [`nix flake update`](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-flake-update.html)
- [`nix flake metadata`](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-flake-metadata.html)

[← 1장: Flake의 역할과 출력 트리](./01-mental-model.md) · [목차](./index.md) ·
[3장: 개발 셸에 `cowsay` 추가하기 →](./03-development-shells.md)
