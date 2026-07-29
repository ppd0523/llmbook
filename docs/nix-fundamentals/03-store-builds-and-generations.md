# 3. Store, derivation, profile, generation

## 학습 목표

1. Store path, derivation, output, closure를 구분한다.
2. profile과 generation이 롤백을 가능하게 하는 방식을 설명한다.
3. garbage collection이 무엇을 지울 수 있는지 판단한다.

## 3.1 `/nix/store`는 결과의 저장소다

Nix가 관리하는 package와 구성 결과는 보통 다음과 같은 경로에 있다.

```text
/nix/store/8ab...-hello-2.12.1
/nix/store/f4c...-git-2.51.0
```

앞의 digest는 이름만 같아도 입력이나 빌드 계획이 다른 결과를 별도 경로로 구분하게
한다. 정확한 Store path 계산 방식은 객체 종류에 따라 세부 사항이 다르므로
“파일 내용의 단순 hash”로 이해하지 않는다.

Store 객체에는 두 중요한 성질이 있다.

1. **불변성**: 만들어진 객체를 제자리에서 수정하지 않는다.
2. **참조 관계**: 한 Store 객체가 의존하는 다른 Store path를 기록할 수 있다.

업데이트는 기존 경로를 덮어쓰는 작업이 아니라 새 Store 경로를 만든 뒤 현재 링크를
바꾸는 작업에 가깝다.

!!! warning
    `/nix/store` 안의 파일을 `sudo`로 직접 수정하지 않는다. 수정에 성공하더라도
    Nix 데이터베이스와 내용이 어긋나고 다음 빌드에서 보존되지 않는다. 원본 Nix
    설정이나 source를 고친 뒤 새 결과를 만든다.

## 3.2 derivation은 package 자체가 아니라 빌드 계획이다

derivation은 필요한 입력, builder, 환경 변수, 예상 output 등을 표현한 빌드 계획이다.
평가 결과로 `.drv` Store 객체가 생길 수 있고, 그 계획을 실현하면 output Store
객체가 생긴다.

```text
Nix 표현식
   │ 평가
   ▼
derivation(.drv): 빌드 계획
   │ 실현
   ├── binary cache에 있으면 다운로드
   └── 없으면 builder 실행
   ▼
output path: 실행 파일·라이브러리·문서 등
```

일상 대화에서는 `pkgs.git` 같은 derivation 값을 “package”라고 편하게 부른다.
엄밀한 오류 분석에서는 다음을 구분한다.

- **source**: 빌드 입력 파일
- **derivation**: 결과를 만드는 계획
- **output**: 계획을 실현해 얻은 Store 객체
- **package**: 사용자 관점에서 배포되는 소프트웨어 단위

package 하나가 `out`, `dev`, `doc`처럼 여러 output을 만들 수도 있다.

## 3.3 closure는 실행에 필요한 전체 묶음이다

Git 실행 파일 Store 객체가 라이브러리와 인증서 등을 참조한다면 Git의 closure는 그
참조를 따라 도달할 수 있는 모든 Store 객체다.

```text
git output
├── openssl
│   └── libc
├── curl
│   ├── openssl
│   └── zlib
└── locale data
```

그림의 실제 구성은 예시일 뿐이다. 핵심은 Store 객체 하나를 다른 머신에 복사하거나
보존하려면 closure 전체가 필요하다는 점이다.

다음 명령으로 현재 Nixpkgs의 `hello`가 필요로 하는 Store path를 볼 수 있다.

```console
$ nix build nixpkgs#hello
$ nix path-info --recursive nixpkgs#hello
```

closure의 크기도 확인할 수 있다.

```console
$ nix path-info --recursive --closure-size nixpkgs#hello
```

`nix path-info` 자체는 없는 output을 build하거나 내려받지 않으므로 먼저 `nix build`로
결과를 확보했다.

`nix why-depends`는 예상하지 못한 의존성이 왜 들어왔는지 추적할 때 쓴다.

```console
$ nix why-depends nixpkgs#git nixpkgs#openssl
```

Nixpkgs revision이나 package 구성에 따라 실제 관계가 없으면 명령이 그 사실을
알려준다.

## 3.4 binary cache는 빌드를 생략하게 한다

실현할 output이 로컬 Store에 없을 때 Nix는 신뢰하도록 설정된 binary cache에서
동일한 결과를 찾는다. 있으면 source에서 직접 컴파일하는 대신 서명된 사전 빌드
결과와 필요한 closure를 내려받는다.

```text
필요한 output이 로컬 Store에 있는가?
├── 예 → 그대로 재사용
└── 아니오
    ├── cache에 있음 → 다운로드
    └── cache에 없음 → 로컬 또는 원격 builder가 빌드
```

그래서 콘솔의 `building`과 `copying path from ...`은 다른 동작이다. 둘 다 최종적으로
필요한 Store 결과를 확보한다.

## 3.5 profile은 Store 결과를 사용 가능하게 하는 링크다

Store에 package가 존재하는 것만으로 현재 shell의 `PATH`에 자동으로 들어오지는
않는다. profile은 선택된 package들을 모은 Store 결과를 가리키는 심볼릭 링크다.

```text
~/.nix-profile
       │
       ▼
사용자 profile의 현재 generation
       │
       ├── bin/git     → /nix/store/...-git.../bin/git
       └── bin/rg      → /nix/store/...-ripgrep.../bin/rg
```

`~/.nix-profile/bin` 같은 경로가 `PATH`에 있어 명령을 찾는다. Nix 설치 방식과
`use-xdg-base-directories` 설정에 따라 실제 profile 링크 위치는 달라질 수 있다.

`nix profile add`는 사용자의 imperative profile을 관리한다. Home Manager도 사용자
환경을 profile generation으로 만들지만, 선언 원본은 Home Manager 구성에 둔다.
같은 package를 두 방식으로 중복 관리하지 않는 편이 문제를 줄인다.

## 3.6 generation은 시간 순서가 있는 profile 버전이다

profile을 변경하면 새 generation이 생기고 현재 링크가 새 버전을 가리킨다. 이전
generation이 남아 있으면 링크를 되돌릴 수 있다.

```text
profile-1-link → 이전 환경
profile-2-link → 현재 환경
profile        → profile-2-link
```

이 구조는 세 계층에서 반복된다.

| 계층 | generation 내용 | 전환 도구 |
|---|---|---|
| imperative 사용자 profile | `nix profile add`로 고른 package | `nix profile` |
| Home Manager | 사용자 package와 생성된 설정·활성화 정보 | `home-manager` |
| NixOS | 커널, `/etc`, systemd unit, 시스템 package 등 | `nixos-rebuild` |

generation은 Git commit과 다르다.

- Git은 **왜 그런 설정을 선언했는지**와 source 이력을 보존한다.
- generation은 **이미 빌드된 어떤 결과가 활성 상태였는지**를 보존한다.

안전한 복구에는 둘 다 필요하다.

## 3.7 garbage root와 garbage collection

Store는 새 결과를 계속 추가하므로 공간이 늘어난다. Garbage collector는 root에서
도달할 수 없는 Store 객체를 제거한다.

대표적인 root는 현재·보존된 profile generation과 `nix build`가 만든 `result`
심볼릭 링크다.

```text
GC root ──참조──> Store 객체 ──참조──> 의존 객체
                          모두 보존

어떤 root에서도 도달 불가 ──> garbage 후보
```

다음은 삭제 대상만 미리 확인한다.

```console
$ nix store gc --dry-run
```

실제 garbage collection은 복구 가능성을 검토한 뒤 실행한다.

```console
$ nix store gc
```

!!! danger
    `nix-collect-garbage -d`나 generation history 삭제는 오래된 profile과 NixOS
    generation이라는 GC root를 제거할 수 있다. 그러면 해당 세대로 롤백하지 못하고
    그 세대만 참조하던 Store 객체도 이후 GC 대상이 된다. 단순 디스크 정리 명령으로
    습관적으로 실행하지 않는다.

## 3.8 Store가 있어도 데이터베이스 상태는 별개다

NixOS generation 롤백은 선언형 시스템 구성을 되돌리는 강력한 장치지만 모든
외부 상태를 자동 복원하지는 않는다.

- PostgreSQL 데이터베이스 format
- 애플리케이션이 `$HOME`이나 `/var/lib`에 쓴 데이터
- 외부 API와 cloud 자원
- secret 값

package 버전을 되돌려도 새 버전이 마이그레이션한 데이터가 자동으로 과거 format으로
돌아가지는 않는다. 그래서 `system.stateVersion`, `home.stateVersion`, 서비스별
state version을 package 버전과 구분하고, 중요한 데이터는 별도로 백업한다.

## 직접 해보기

### 1. Store path 관찰

```console
$ nix build nixpkgs#hello
$ readlink -f result
$ ls -l result/bin
$ ./result/bin/hello
```

`result`가 package 디렉터리 자체가 아니라 Store output을 가리키는 링크임을 확인한다.

### 2. 같은 결과 재사용

같은 명령을 다시 실행한다.

```console
$ nix build nixpkgs#hello
```

입력이 바뀌지 않았다면 이미 있는 결과를 재사용하므로 첫 실행보다 할 일이 적다.
단, `nixpkgs` registry가 가리키는 revision이 바뀌면 다른 결과가 선택될 수 있다.

### 3. profile은 읽기만 한다

```console
$ nix profile list
$ nix profile history
```

아직 package를 추가하거나 삭제할 필요는 없다. Home Manager를 주된 사용자 환경
관리자로 쓸 계획이라면 이 profile에 같은 package를 따로 설치하지 않는다.

## 확인 문제

1. derivation과 output은 같은 것인가?
2. Store에 `git`이 있으면 현재 shell에서 바로 `git`을 찾을 수 있는가?
3. 오래된 generation을 지운 뒤에도 언제나 롤백할 수 있는가?
4. NixOS 세대 롤백이 데이터베이스 내용까지 복원하는가?

정답은 모두 “아니다”다. derivation은 계획이고 output은 결과다. 사용 가능 여부는
profile이나 shell 환경이 정한다. generation을 지우면 롤백 근거를 잃고, 외부의
가변 데이터는 별도 백업과 마이그레이션 정책이 필요하다.

## 요약

- `/nix/store`는 불변 결과와 그 참조 관계를 보관한다.
- derivation은 빌드 계획이며 실현된 output과 구분한다.
- closure는 한 결과에서 참조를 따라 필요한 Store 객체 전체다.
- profile의 현재 generation 링크를 바꾸므로 원자적인 전환과 롤백이 가능하다.
- GC root를 지우는 정리는 롤백 가능성도 함께 지울 수 있다.

## 공식 자료

- [Nix Store 개요](https://nix.dev/manual/nix/2.34/store/)
- [Store 객체와 참조](https://nix.dev/manual/nix/2.34/store/store-object.html)
- [Derivations](https://nix.dev/manual/nix/2.34/language/derivations.html)
- [Profiles](https://nix.dev/manual/nix/2.34/command-ref/files/profiles.html)
- [`nix store gc`](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-store-gc.html)

[← 2장](./02-language-basics.md) · [목차](./index.md) ·
[4장: 패키지 사용과 세 종류의 셸 →](./04-shells-and-packages.md)
