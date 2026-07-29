# 8. 문제 해결, 용어집, 다음 학습

## 학습 목표

1. 오류가 평가·실현·활성화 중 어느 단계인지 분류한다.
2. 안전한 진단 명령과 공식 검색 경로를 선택한다.
3. 이 저장소의 후속 책을 알맞은 순서로 이어서 읽는다.

## 8.1 먼저 실패 단계를 찾는다

Nix 오류는 길지만 첫 분류는 단순하다.

```text
명령 실패
├── 평가
│   ├── 문법 오류
│   ├── option 없음·type 불일치
│   ├── attribute 없음
│   └── infinite recursion
├── 실현
│   ├── 다운로드·network·서명
│   ├── hash 불일치
│   ├── build failure
│   └── disk 부족
└── 활성화
    ├── 기존 파일 충돌
    ├── 권한 부족
    ├── service 전환 실패
    └── 새 generation의 runtime 문제
```

평가 오류에 network를 고치거나, 활성화 충돌에 `--show-trace`만 반복해도 진전이
없다. 마지막에 실행한 명령과 “어느 단계까지 성공했는가”를 먼저 기록한다.

## 8.2 증상별 첫 확인

| 증상 | 가능성이 큰 원인 | 첫 확인 |
|---|---|---|
| `experimental Nix feature ... disabled` | 기능 비활성 | `nix.conf` 또는 NixOS `nix.settings` |
| `attribute ... missing` | package/output 이름 또는 system 불일치 | `nix flake show`, package 검색 |
| `option ... does not exist` | 오타·다른 module 세계·미수입 module | NixOS/HM option 검색 |
| `expected ... but found ...` | option type 오류 | option type과 현재 값 |
| `infinite recursion` | `config`·`rec` 자기 의존 | trace와 option 의존 관계 |
| 새 파일을 못 찾음 | Flake의 Git source에 미포함 | `git status`, `git add` |
| `home-manager switch` 파일 충돌 | 기존 실제 파일을 덮으려 함 | 오류의 정확한 대상 path |
| build log가 화면에 없음 | log가 축약됨 | `-L` 또는 `nix log` |
| disk 사용량 급증 | 여러 closure와 generation 보존 | `nix path-info`, generation 목록, GC dry-run |
| 명령 버전이 예상과 다름 | 여러 profile·system package의 `PATH` 경쟁 | `type -a`, `command -v` |

## 8.3 읽기 전용 진단부터 한다

```console
$ nix --version
$ nix config show
$ nix flake show
$ nix flake metadata
$ nix profile list
$ nix profile history
$ command -v git
$ type -a git
$ git status --short
```

필요한 명령만 선택한다. 구성에 secret이 environment variable이나 URL parameter로
포함될 수 있다면 출력 전체를 공개 issue에 그대로 붙이지 않는다.

### build log

실행하며 log를 본다.

```console
$ nix build -L
```

이미 실패한 build의 log가 남아 있다면 installable을 지정해 확인한다.

```console
$ nix log .#packageName
```

### 상세 평가 trace

```console
$ nix build --show-trace
```

Trace가 매우 길 수 있다. 가장 아래 오류 메시지, 사용자가 편집한 파일 경로, 처음
등장한 option 이름을 우선 찾는다.

## 8.4 흔한 함정

### `nix shell` 안인데 package가 없다

package attribute 이름과 실제 executable 이름이 다를 수 있다.

```console
$ nix build nixpkgs#packageName
$ find result/bin -maxdepth 1 -type f -o -type l
```

`find` 조건이 shell마다 다르게 보일 수 있으므로 단순히 `ls -l result/bin`으로
확인해도 된다.

### `nix develop`이 다른 output을 찾는다

```console
$ nix flake show
```

현재 system 아래 `devShells.<system>.default`가 있는지 본다. 이름 있는 shell이면
`nix develop .#name`을 쓴다.

### Flake가 수정한 파일을 무시한다

Git 저장소 안의 Flake는 Git index에 없는 새 파일을 source로 보지 않을 수 있다.

```console
$ git status --short
$ git add path/to/new-file
```

Stage는 commit이 아니다. 평가에 포함시키기 위해 먼저 stage하고 diff를 검토할 수
있다.

### `sudo nix ...`와 일반 사용자 결과가 다르다

사용자별 registry, channel, profile, config가 다를 수 있다. 시스템 전환에 root가
필요한 `nixos-rebuild`와 일반 package 탐색 명령을 구분한다. 원인을 모른 채 모든
Nix 명령에 `sudo`를 붙이지 않는다.

### Home Manager가 기존 파일을 덮지 않는다

이는 데이터 보호 동작이다. 오류에 나온 파일을 확인하고 다음 중 하나를 명시적으로
선택한다.

1. 기존 내용을 Home Manager source로 옮기고 원본 파일을 안전하게 백업한다.
2. 해당 파일 관리를 Home Manager에서 제외한다.
3. module이 제공하는 backup 옵션을 현재 버전의 공식 문서에서 확인한다.

자동으로 기존 파일을 삭제하지 않는다.

### Store 결과를 고쳤는데 되돌아온다

Store는 생성 결과다. `result`, `~/.config/...`의 Store symlink가 아니라
`configuration.nix`, `home.nix`, module, 원본 dotfile을 수정하고 다시 build한다.

## 8.5 안전한 변경 루프

```text
작게 수정
   │
   ▼
Git diff 확인
   │
   ▼
build/check
   │ 실패 ──> 오류 단계 분류 ──> source 수정
   ▼ 성공
test(가능한 계층)
   │
   ▼
switch
   │ 문제 ──> 이전 generation 복구 + source 수정
   ▼
commit
```

계층별 예:

```console
# 프로젝트
$ nix flake check
$ nix develop --command bash -c 'run-tests'

# NixOS
$ sudo nixos-rebuild build --flake .#myhost
$ sudo nixos-rebuild test --flake .#myhost
$ sudo nixos-rebuild switch --flake .#myhost

# standalone Home Manager
$ home-manager build --flake .#alice
$ home-manager switch --flake .#alice
```

`nix flake check`가 무엇을 검사하는지는 Flake가 선언한 output에 달려 있다. 아무
project test나 자동으로 발견하는 명령은 아니다.

## 8.6 최소 용어집

| 용어 | 이 자료에서의 뜻 |
|---|---|
| attribute | 속성 집합 안의 이름-값 항목 |
| attribute path | `programs.git.enable`처럼 중첩 속성을 가리키는 경로 |
| binary cache | 미리 빌드한 Store 객체를 제공하는 저장소 |
| build | 필요한 Store output을 cache에서 받거나 builder로 생성하는 과정 |
| closure | Store 객체에서 참조를 따라 도달 가능한 전체 requisites |
| declaration | module option의 이름·type·default 등을 정의한 계약 |
| definition | 특정 구성에서 option에 부여한 값 |
| derivation | Store output을 만드는 빌드 계획 |
| evaluation | Nix 표현식을 값과 빌드 계획으로 계산하는 단계 |
| Flake | `flake.nix`의 입력·출력 규약과 lockfile 기반 dependency 경계 |
| generation | profile의 버전이 매겨진 한 상태 |
| GC root | garbage collection에서 Store 객체를 살아 있게 하는 참조 시작점 |
| installable | `nix` 명령이 build·run·shell 대상으로 해석할 수 있는 값 |
| module | option 선언·정의를 module system에 제공하는 Nix 표현식 |
| Nix | 빌드·배포 도구 전체 또는 문맥에 따라 Nix 언어 |
| NixOS | Nix module로 운영체제 전체를 구성하는 Linux 배포판 |
| Nixpkgs | package 함수와 NixOS module이 있는 저장소 |
| option | module system이 제공하는 type이 있는 설정 API |
| output | derivation을 실현해 얻은 Store 객체 |
| profile | 선택된 Store 결과를 노출하는 버전 관리 링크 |
| realisation | derivation이 요구한 Store output을 실제로 확보하는 일 |
| Store path | Store 객체를 가리키는 `/nix/store/<digest>-<name>` 형태의 경로 |
| substituter | Store 객체를 대신 제공하는 binary cache endpoint |

## 8.7 무엇을 외우고 무엇을 검색할까

외울 것:

- 목록에는 쉼표가 없고 속성 정의는 세미콜론으로 끝난다.
- `{ pkgs, ... }:`는 함수 인자다.
- `nix shell`은 임시, `nix develop`은 프로젝트 환경이다.
- Store 결과를 직접 편집하지 않는다.
- `build`와 `switch`는 다르다.
- `stateVersion`은 package release 선택자가 아니다.

매번 검색할 것:

- 정확한 NixOS·Home Manager option 이름과 type
- package attribute와 executable 이름
- release note의 breaking change
- 오래된 예제의 현재 명령 옵션
- 외부 module이 요구하는 `specialArgs`

좋은 Nix 사용자는 option을 모두 외운 사람이 아니라 현재 잠긴 revision의 문서와
source에서 정의의 출처를 찾을 줄 아는 사람이다.

## 8.8 다음 학습 순서

### 개발 셸과 Flake를 더 배우려면

[Nix Flake 입문](../nix-flakes/index.md)으로 이동한다. `inputs`, `outputs`,
`flake.lock`, `devShells`, package, app, formatter, check를 실제 프로젝트로
확장한다.

### Home Manager를 운영하려면

[Standalone Home Manager 운영 가이드](../home-manager-guide/index.md)로 이동한다.
package와 program option, dotfile, build/switch, generation 복구를 다룬다.

### NixOS-WSL 환경 전체를 만들려면

[NixOS-WSL 개발 환경 매뉴얼](../nixos-wsl-dev-environment/index.md)로 이동한다.
NixOS와 Home Manager, 개발 toolchain을 하나의 Git 저장소로 복원하는 구조를
다룬다.

권장 순서는 다음과 같다.

```text
이 기초 자료
├── 프로젝트 개발이 우선 → Nix Flake 입문
├── 사용자 환경이 우선   → Home Manager 운영 가이드
└── 머신 전체 구축       → NixOS-WSL 매뉴얼
```

## 8.9 최종 자기 점검

다음 질문에 자료를 보지 않고 답해 본다.

1. Nixpkgs와 NixOS는 어떻게 다른가?
2. `pkgs.git`은 어디에서 오는가?
3. derivation과 Store output의 관계는 무엇인가?
4. `nix shell`, `nix develop`, `nix-shell`은 각각 언제 쓰는가?
5. `imports`가 일반 `import`와 다른 점은 무엇인가?
6. 두 module이 같은 list option을 정의하면 어떻게 되는가?
7. Home Manager와 NixOS에서 같은 `programs.zsh.enable` 이름을 보아도 왜 같은
   설정이라고 단정할 수 없는가?
8. `flake.lock`과 `home.stateVersion`은 무엇을 각각 고정하는가?
9. `nixos-rebuild build` 뒤 현재 시스템이 자동 전환되는가?
10. GC 전에 어떤 롤백 이력을 잃는지 왜 확인해야 하는가?

모두 설명할 수 있다면 NixOS, 개발 셸, Home Manager 후속 자료를 읽을 사전 지식이
준비되었다.

## 공식 자료 지도

- 시작: [nix.dev First steps](https://nix.dev/tutorials/first-steps/)
- 언어: [Nix language basics](https://nix.dev/tutorials/nix-language.html)
- 명령: [Nix 2.34 command reference](https://nix.dev/manual/nix/2.34/command-ref/)
- Store: [Nix Store](https://nix.dev/manual/nix/2.34/store/)
- Module: [nix.dev Module system](https://nix.dev/tutorials/module-system/)
- NixOS: [NixOS Manual](https://nixos.org/manual/nixos/stable/)
- Package·option: [NixOS Search](https://search.nixos.org/)
- Home: [Home Manager Manual](https://nix-community.github.io/home-manager/)

[← 7장](./07-guided-lab.md) · [목차](./index.md) ·
[문서 목록으로 돌아가기](../index.md)
