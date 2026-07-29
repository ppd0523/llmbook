# 1. Nix 생태계와 하나의 작업 흐름

## 학습 목표

1. Nix, Nixpkgs, NixOS, Flake, Home Manager의 책임을 구분한다.
2. 명령 실행을 `입력 → 평가 → 실현 → 활성화`로 나누어 설명한다.
3. 선언적 설정과 재현 가능성이 같은 말이 아님을 이해한다.

## 1.1 먼저 이름부터 분리한다

`Nix`라는 말은 문맥에 따라 도구 전체나 Nix 언어를 가리킨다. 처음에는 다음 표처럼
분리해서 읽는다.

| 이름 | 정체 | 주로 담는 것 | 대표 사용 |
|---|---|---|---|
| Nix | 패키지 빌드·배포 도구와 Store | 빌드 계획, 패키지 결과 | `nix build`, `nix shell` |
| Nix 언어 | 선언형 함수형 언어 | package와 구성의 계산식 | `.nix` 파일 |
| Nixpkgs | Nix로 작성된 거대한 저장소 | package 함수와 NixOS module | `pkgs.git`, `pkgs.python3` |
| NixOS | Nix로 시스템 전체를 만드는 Linux 배포판 | 부팅, 사용자, 서비스, 시스템 package | `nixos-rebuild` |
| Home Manager | 사용자의 home 환경을 만드는 module 모음과 도구 | 사용자 package, dotfile, 환경 변수 | `home-manager switch` |
| Flake | Nix 코드의 입력·출력 규약과 잠금 방식 | `flake.nix`, `flake.lock` | `nix develop`, `--flake` |

비유하면 Nix는 조리 체계, Nix 언어는 조리법을 쓰는 문법, Nixpkgs는 재료와 조리법
모음이다. NixOS는 그 체계로 집 전체를 구성하고, Home Manager는 한 사람의 방을
구성한다. Flake는 사용할 재료판의 정확한 판본과 완성품의 이름을 적은 프로젝트
표지다.

`NixOS`는 Nix를 사용하는 한 가지 큰 결과물이다. Nix는 다른 Linux와 macOS에서도
사용할 수 있고, Home Manager도 NixOS 없이 standalone으로 사용할 수 있다.

## 1.2 package 이름은 문자열이 아니다

다음 NixOS 설정을 보자.

```nix
environment.systemPackages = [
  pkgs.git
  pkgs.ripgrep
];
```

`"git"`과 `"ripgrep"`이라는 이름을 설치 프로그램에 전달한 것이 아니다.
`pkgs`라는 속성 집합에서 `git`과 `ripgrep`이라는 package 값을 꺼내 목록으로 만든
것이다. `pkgs`는 특정 Nixpkgs revision과 특정 시스템 아키텍처를 평가해 얻는다.

```text
Nixpkgs 소스 + system + 설정
              │ 평가
              ▼
       pkgs 속성 집합
       ├── git       → package
       ├── ripgrep   → package
       └── python3   → package
```

그래서 “어느 Nixpkgs를 썼는가”가 package 버전과 빌드 방법을 결정한다.

## 1.3 하나의 공통 작업 흐름

NixOS, 개발 셸, Home Manager는 규모가 다르지만 다음 흐름을 공유한다.

```text
Nix 소스와 잠긴 입력
        │
        ▼
  1. 평가(evaluation)
  Nix 값과 빌드 계획을 계산
        │
        ▼
  2. 실현(realisation)
  binary cache에서 받거나 직접 빌드
        │
        ▼
  /nix/store의 불변 결과
        │
        ▼
  3. 활성화(필요한 경우)
  PATH·profile·시스템·home 링크 전환
```

### 평가

Nix 코드를 계산한다. 타입 오류, 존재하지 않는 option, 무한 재귀 같은 오류는 주로
여기서 발생한다. 아직 서비스가 재시작되거나 사용자의 설정 파일이 바뀐 것은 아니다.

### 실현

평가가 요구한 결과가 Store에 없으면 binary cache에서 내려받거나 빌드한다. Nix
문서에서 “build”는 이 두 경우를 모두 포함해 Store 결과를 확보한다는 뜻으로 자주
쓰인다.

### 활성화

만든 결과를 현재 사용 상태로 전환한다.

- `nix shell`은 새 프로세스의 `PATH`를 잠시 바꾼다.
- `nix profile add`는 사용자 profile의 현재 generation을 전환한다.
- `nixos-rebuild switch`는 시스템 profile을 전환하고 서비스를 조정한다.
- `home-manager switch`는 home generation을 전환하고 파일 링크 등을 적용한다.

`nix build`나 `nixos-rebuild build`가 성공했다고 현재 환경이 자동으로 바뀌지는
않는다. 이 구분이 안전한 운영의 출발점이다.

## 1.4 선언형, 재현 가능, 순수함은 서로 다르다

세 단어를 한 덩어리로 외우면 오해하기 쉽다.

- **선언형**: 실행 절차보다 원하는 결과를 데이터로 적는다.
- **재현 가능**: 필요한 입력이 같을 때 같은 결과를 다시 얻을 수 있다.
- **순수 평가**: 평가 중 허용되지 않은 외부 상태를 몰래 읽지 않는다.

다음 설정은 선언형이다.

```nix
{ pkgs, ... }:
{
  home.packages = [ pkgs.git ];
}
```

하지만 `pkgs`가 매번 다른 Nixpkgs revision에서 온다면 package 버전은 달라질 수
있다. 선언만으로 입력이 고정되지는 않는다. Flake의 `flake.lock` 같은 잠금 장치가
필요한 이유다.

또한 모든 결과가 bit-for-bit 동일하다는 보장과 “같은 입력을 사용한다”는 운영상의
재현 가능성도 엄밀히는 다르다. 입문 단계에서는 먼저 다음 규칙을 지킨다.

> 재현하고 싶은 Nix 코드와 `flake.lock`을 함께 버전 관리한다.

## 1.5 명령형 사용도 쓸모가 있다

Nix를 쓴다고 모든 작업을 즉시 선언형으로 바꿀 필요는 없다.

```console
$ nix shell nixpkgs#jq
$ jq --version
$ exit
```

이 작업은 임시 셸을 여는 명령형 동작이다. 빠르게 도구를 시험할 때 적합하다. 반면
팀 프로젝트 환경이라면 `flake.nix`의 `devShells`로 기록하고 `flake.lock`을
커밋하는 편이 맞다.

| 필요 | 알맞은 계층 |
|---|---|
| 5분 동안 명령 하나 시험 | `nix shell` |
| 저장소에 들어오면 같은 도구 사용 | `nix develop`과 프로젝트 Flake |
| 한 사용자가 늘 쓰는 CLI·설정 | Home Manager |
| 모든 사용자·부팅·system service | NixOS |

“Nix답게 보이는가”가 아니라 수명과 소유 범위로 선택한다.

## 1.6 기존 패키지 관리자와 다른 점

전통적인 패키지 관리자는 `/usr/bin`, `/usr/lib` 같은 공용 위치를 현재 버전으로
갱신하는 경우가 많다. Nix는 결과를 서로 다른 Store 경로에 함께 둔다.

```text
/nix/store/<hash-a>-hello-2.12.1/
/nix/store/<hash-b>-hello-2.12.2/
```

현재 어떤 결과를 쓰는지는 profile이나 시스템 generation 같은 링크가 정한다.
따라서 서로 다른 버전의 공존과 원자적인 전환이 쉬워진다. 대신 디스크 사용량과
garbage collection, 링크 구조라는 새 개념을 배워야 한다.

## 직접 해보기

다음 상황의 소유 계층을 먼저 답한 뒤 표를 확인한다.

1. 지금 한 번만 JSON을 확인하려고 `jq`가 필요하다.
2. 저장소의 모든 개발자가 동일한 `nodejs`와 `pnpm`을 써야 한다.
3. 내 Git 사용자 이름과 zsh alias를 두 컴퓨터에서 같게 쓰고 싶다.
4. SSH daemon을 부팅 때 시작하고 방화벽 22번 포트를 열어야 한다.
5. Nixpkgs의 정확한 Git revision을 저장해야 한다.

| 번호 | 답 |
|---:|---|
| 1 | `nix shell` |
| 2 | 프로젝트 Flake의 `devShells`, `nix develop` |
| 3 | Home Manager |
| 4 | NixOS |
| 5 | `flake.lock` |

## 확인 문제

1. NixOS를 쓰지 않는 Linux에서도 Nix를 쓸 수 있는가?
2. `pkgs.git`의 `git`은 package 이름 문자열인가?
3. `nixos-rebuild build` 성공 직후 실행 중인 시스템 설정이 바뀌는가?
4. 선언형 코드인데도 package 버전이 달라질 수 있는 경우는 무엇인가?

정답은 각각 “그렇다”, “아니며 `pkgs`의 package 값이다”, “아니다”, “입력
Nixpkgs revision을 고정하지 않은 경우”다.

## 요약

- Nix, Nixpkgs, NixOS, Home Manager, Flake는 같은 것이 아니다.
- 모든 작업은 입력, 평가, Store 결과, 필요시 활성화라는 흐름으로 볼 수 있다.
- 선언형 설정과 고정된 입력이 함께 있어야 재현성이 높아진다.
- 도구의 수명과 적용 범위로 `nix shell`, 프로젝트, Home Manager, NixOS를 고른다.

## 공식 자료

- [Nix 언어의 성격](https://nix.dev/manual/nix/2.34/language/)
- [Nix Store](https://nix.dev/manual/nix/2.34/store/)
- [Flakes 개념](https://nix.dev/concepts/flakes.html)
- [Home Manager 소개](https://nix-community.github.io/home-manager/introduction.html)

[← 목차](./index.md) · [2장: Nix 언어를 읽는 최소 문법 →](./02-language-basics.md)
