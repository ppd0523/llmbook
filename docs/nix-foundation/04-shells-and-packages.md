# 4. 패키지 사용과 세 종류의 셸

## 학습 목표

1. `nix search`로 package 후보를 찾고 검색 결과를 읽는다.
2. `nix shell`과 `nix develop`이 만드는 환경의 차이를 설명한다.
3. `nixpkgs#hello` 형태의 installable을 읽는다.
4. `nix shell`, `nix develop`, `nix-shell`의 용도를 구분한다.
5. 임시 도구와 영구 package를 올바른 계층에 둔다.

## 4.1 가장 먼저 배울 명령은 설치가 아니라 임시 사용이다

도구를 시험할 때 사용자 환경에 곧바로 영구 설치할 필요가 없다.

```console
$ nix shell nixpkgs#hello
$ hello
Hello, world!
$ exit
```

Nix는 필요한 Store 결과를 확보하고, 새 shell의 `PATH` 앞부분에 그 package의 실행
경로를 넣는다. shell을 나가면 `PATH` 변경이 사라진다. Store의 다운로드 결과가
즉시 삭제되는 것은 아니며 나중에 재사용되거나 참조가 없을 때 GC 대상이 된다.

한 명령만 실행할 수도 있다.

```console
$ nix shell nixpkgs#jq --command jq --version
```

여러 도구도 가능하다.

```console
$ nix shell nixpkgs#git nixpkgs#ripgrep nixpkgs#jq
```

이 기능은 “도구가 필요하지만 시스템이나 사용자 구성을 바꾸고 싶지 않을 때” 가장
유용하다.

## 4.2 `nixpkgs#hello`를 두 부분으로 읽는다

```text
nixpkgs # hello
────────   ─────
Flake      그 Flake에서 찾을 출력 이름
reference
```

- `nixpkgs`는 보통 Flake registry에 등록된 Nixpkgs reference다.
- `#hello`는 현재 시스템에서 `hello` package output을 찾게 한다.

로컬 프로젝트도 같은 형태다.

```console
$ nix develop .#backend
```

- `.`: 현재 디렉터리의 Flake
- `#backend`: `devShells.<현재-system>.backend` 같은 출력 이름

`nixpkgs#hello`만으로 실행하면 registry가 현재 가리키는 Nixpkgs를 사용하므로
장기간 재현할 명세로는 부족할 수 있다. 잠깐 시험하는 데는 편리하고, 프로젝트에서는
`flake.lock`으로 정확한 입력 revision을 고정한다.

## 4.3 `nix search`: 사용할 package 찾기

`nix shell`에 넣을 이름을 모를 때 추측부터 하지 말고 먼저 검색한다.

```console
$ nix search nixpkgs ripgrep
```

기본 형태는 다음과 같다.

```text
nix search <검색할 Flake> <정규식>...
```

`nixpkgs`는 검색 대상이고 `ripgrep`은 정규식이다. 검색 결과에는 보통 다음 정보가
나온다.

```text
* legacyPackages.x86_64-linux.ripgrep (버전)
  A fast line-oriented search tool ...
```

- `legacyPackages.x86_64-linux.ripgrep`: package의 전체 속성 경로
- 괄호 안 값: package 버전
- 다음 줄: `meta.description`에 기록된 설명

여기서 검색된 package 속성 `ripgrep`을 installable로 옮기면
`nixpkgs#ripgrep`이 된다.

```console
$ nix shell nixpkgs#ripgrep --command rg --version
```

package 속성 이름과 실행 명령 이름은 같을 수도, 다를 수도 있다. 이 예제의 package는
`ripgrep`, 실행 파일은 `rg`다. `nix search`는 실행 파일 목록을 직접 검색하는 명령이
아니라 package 이름과 설명을 대상으로 검색한다.

### 정규식 여러 개는 모두 만족해야 한다

```console
$ nix search nixpkgs git 'frontend|gui'
```

위 명령은 `git`과 `frontend|gui`를 **모두** 만족하는 결과를 찾는다. 두 번째 정규식
안의 `|`는 `frontend` 또는 `gui`라는 뜻이다. 즉 다음처럼 구분한다.

| 목적 | 작성법 |
|---|---|
| `git`과 `gui`를 모두 포함 | `nix search nixpkgs git gui` |
| `firefox` 또는 `chromium` 포함 | `nix search nixpkgs 'firefox|chromium'` |
| `python` 또는 `gui`가 들어간 결과 제외 | `nix search nixpkgs tool --exclude 'python|gui'` |

`--exclude`는 여러 번 쓸 수 있다. `|`, `*`, `^` 같은 문자를 shell이 먼저 해석하지
않도록 정규식은 작은따옴표로 감싸는 습관이 안전하다.

### 전체 목록, 범위 제한, 기계 판독

```console
# ^는 모든 문자열의 시작과 일치하므로 전체 package를 표시한다.
$ nix search nixpkgs '^'

# Nixpkgs의 python3Packages 속성 아래로 검색 범위를 제한한다.
$ nix search nixpkgs#python3Packages requests

# 현재 Flake가 제공하는 package를 검색한다.
$ nix search . '^'

# 스크립트에서 처리할 JSON을 출력한다.
$ nix search nixpkgs ripgrep --json
```

출력에 `legacyPackages`가 보인다고 해서 legacy 명령을 써야 한다는 뜻은 아니다. 이것은
Nixpkgs가 호환성과 구성상의 이유로 package 집합을 노출하는 Flake output 이름이다.
현재 system까지의 앞부분을 뺀 package 속성 경로를 installable에 사용한다. 예를 들어
`legacyPackages.x86_64-linux.ripgrep`은 `nixpkgs#ripgrep`으로,
`legacyPackages.x86_64-linux.python3Packages.foo`는
`nixpkgs#python3Packages.foo`로 옮겨 쓸 수 있다.

검색 결과가 너무 많으면 설명에 들어갈 단어를 두 번째 정규식으로 추가한다. 결과가
없으면 정규식 철자와 검색 범위를 확인하고, 먼저 `nix search nixpkgs '^'` 또는
[NixOS package 검색](https://search.nixos.org/packages)에서 후보를 찾는다.

## 4.4 `nix shell`: package를 임시 명령 환경으로 만들기

기본 형태는 다음과 같다.

```text
nix shell <installable>... [--command <명령> <인자>...]
```

예를 들어 다음 명령은 두 package를 확보하고 각 package의 실행 경로를 `PATH`에
추가한 새 shell을 시작한다.

```console
$ nix shell nixpkgs#cowsay nixpkgs#lolcat
$ command -v cowsay
/nix/store/...-cowsay-.../bin/cowsay
$ cowsay hello | lolcat
$ exit
```

명령이 처리되는 순서는 다음과 같다.

1. installable을 평가해 필요한 package output을 찾는다.
2. Store에 없는 output은 binary cache에서 받거나 빌드한다.
3. 각 output의 실행 경로를 앞에 둔 `PATH`를 만든다.
4. `--command`가 없으면 `$SHELL`이 가리키는 shell을 시작한다.
5. `exit`하면 임시 `PATH`가 사라지고 원래 shell로 돌아간다.

Store에 받은 파일 자체가 즉시 삭제되는 것은 아니다. 다음 실행에서 재사용되며, 더는
참조되지 않을 때 garbage collection 대상이 될 수 있다.

### 대화형 shell과 한 명령 실행

도구를 여러 번 써 보려면 대화형 shell이 편하다.

```console
$ nix shell nixpkgs#jq nixpkgs#curl
$ curl --version
$ jq --version
$ exit
```

한 번만 실행하거나 script와 CI에서 사용할 때는 `--command` 또는 짧은 형식 `-c`를
쓴다. `--command` 뒤의 첫 단어가 실행할 명령이고 나머지는 그 명령의 인자다.

```console
$ nix shell nixpkgs#jq --command jq --version
$ nix shell nixpkgs#jq -c jq --version
```

pipe나 `&&` 같은 shell 문법이 필요하면 명시적으로 shell을 실행한다.

```console
$ nix shell nixpkgs#curl nixpkgs#jq \
    --command bash -c 'curl -s https://example.com/data.json | jq .'
```

`nix shell`은 package의 실행 파일을 잠깐 쓰기 위한 도구다. 프로젝트 공통 환경
변수, compiler와 library 조합, 시작 시 검사 같은 개발 환경 설계는 `devShells`와
`nix develop`이 담당한다.

!!! note
    `nix shell`은 container가 아니다. 기존 환경 변수, home 디렉터리, 현재 작업
    디렉터리, network에 접근할 수 있다. 정확히 어떤 명령이 선택되었는지는
    `command -v <명령>`이나 `type -a <명령>`으로 확인한다.

## 4.5 `nix develop`: 프로젝트가 선언한 개발 환경 사용하기

`nix develop`은 단순히 package 실행 경로 몇 개를 추가하는 명령이 아니다. Flake의
개발 shell이나 package derivation을 바탕으로, 빌드에 가까운 환경 변수와 shell
함수를 준비한 Bash를 시작한다.

```console
$ cd project-with-flake
$ nix develop
```

인자 없는 `nix develop`은 현재 디렉터리 `.`에서 현재 system에 맞는 output을 다음
순서로 찾는다.

1. `devShells.<system>.default`
2. 없으면 `packages.<system>.default`

이름을 지정한 `nix develop .#backend`는 다음 후보를 순서대로 찾는다.

1. `devShells.<system>.backend`
2. `packages.<system>.backend`
3. `legacyPackages.<system>.backend`

따라서 `nix develop .#backend`의 `backend`는 임의의 shell 이름이 아니라 Flake가
실제로 제공해야 하는 output 속성이다. 무엇이 있는지 모르면 먼저 확인한다.

```console
$ nix flake show
```

### `devShells`에 넣을 수 있는 것

아래 4.8절의 `pkgs.mkShell` 예제처럼 보통 다음 내용을 프로젝트에 선언한다.

- `packages`: compiler, formatter, test runner 같은 명령
- 환경 변수: 프로젝트 빌드와 실행에 필요한 값
- `shellHook`: shell에 진입할 때 실행할 안내나 초기화

팀원이 같은 `flake.nix`와 `flake.lock`에서 `nix develop`을 실행하면 같은 Nix 입력에서
도구를 선택한다. 다만 사용자의 home 파일, network, Nix 밖의 환경 변수까지 자동으로
동일해지는 것은 아니다.

### 대화형 사용과 비대화형 실행

환경 안에서 오래 작업하려면 그대로 진입한다.

```console
$ nix develop
$ compiler --version
$ run-tests
$ exit
```

명령 하나만 같은 환경에서 실행하려면 `--command` 또는 `-c`를 쓴다.

```console
$ nix develop --command run-tests
$ nix develop .#backend -c bash -c 'formatter --check . && run-tests'
```

이는 local script와 CI가 개발자와 같은 dev shell 정의를 재사용할 때 유용하다.
프로젝트가 외부 shell 설정의 영향을 받는지 점검할 때는
`nix develop --ignore-env`를 별도로 시험할 수 있다. 필요한 변수까지 제거될 수
있으므로 일반 실행을 무조건 대체하는 옵션으로 보지는 않는다.

### package build 환경 조사

`nix develop nixpkgs#hello`처럼 package를 지정하면 그 derivation의 빌드 환경을
가까이 재현한다. `--unpack`, `--configure`, `--build`, `--check`, `--install` 같은
phase 실행 옵션도 있어 package가 왜 빌드되지 않는지 조사할 때 유용하다.

```console
$ nix develop nixpkgs#hello
$ env | sort
$ exit
```

이 사용법은 package 유지·디버깅에 가깝다. 일반 애플리케이션 프로젝트는 직접 만든
`devShells`를 사용하는 것이 출발점이다.

## 4.6 이름이 비슷한 shell 명령 비교

| 명령 | 주 목적 | 입력 | 환경의 성격 |
|---|---|---|---|
| `nix shell` | package 실행 파일을 임시 `PATH`에 추가 | installable 목록 | ad hoc |
| `nix develop` | package 빌드 환경 또는 Flake dev shell 진입 | `devShells`/package | 프로젝트 개발 |
| `nix-shell` | `.nix` 파일 기반의 legacy build/dev shell | `shell.nix`, `default.nix`, `-p` | 오래된 문서·프로젝트 호환 |

하이픈의 유무가 중요하다. `nix shell`은 `nix` 명령의 하위 명령이고, `nix-shell`은
오래된 독립 실행 파일이다.

```console
# 새 CLI: package 실행 경로를 임시 사용
$ nix shell nixpkgs#hello

# 새 CLI와 Flake: 프로젝트 개발 환경
$ nix develop

# legacy CLI: 기존 shell.nix 또는 package 목록 사용
$ nix-shell
$ nix-shell -p hello
```

오래된 튜토리얼에서 `nix-shell`을 많이 볼 수 있다. `shell.nix`나 `default.nix` 기반
프로젝트를 사용하거나 legacy shebang을 유지해야 할 때 필요하다. 새 Flake 프로젝트의
기본 학습 흐름에서는 `nix develop`을 사용한다.

!!! note
    “legacy”는 즉시 제거되었거나 사용할 수 없다는 뜻이 아니다. 기존 생태계를 읽을
    때 반드시 알아야 하지만, 같은 프로젝트에서 channel 기반 `<nixpkgs>` 예제와
    Flake 기반 예제를 이유 없이 섞지 않는다는 뜻이다.

## 4.7 `nix run`, `nix build`, `nix profile`과의 차이

| 하고 싶은 일 | 명령 |
|---|---|
| package 후보 검색 | `nix search nixpkgs ripgrep` |
| 실행 파일을 한 번 실행 | `nix run nixpkgs#hello` |
| 여러 실행 파일이 있는 임시 shell | `nix shell nixpkgs#git nixpkgs#jq` |
| output을 Store에 실현하고 `result` 링크 생성 | `nix build nixpkgs#hello` |
| 프로젝트가 정의한 개발 환경 진입 | `nix develop` |
| imperative 사용자 profile에 계속 추가 | `nix profile add nixpkgs#hello` |
| 선언적으로 사용자 package 유지 | Home Manager의 `home.packages` |
| 선언적으로 시스템 package 유지 | NixOS의 `environment.systemPackages` |

Home Manager를 사용할 계획이라면 평소 계속 쓸 package는 `nix profile add`보다
`home.packages`에 기록하는 편이 원본을 한곳에 유지하기 쉽다. `nix profile`은
Home Manager와 별개의 profile 관리 흐름이다.

## 4.8 Flake는 입력과 출력의 얇은 경계다

최소 Flake는 다음 모양이다.

파일: `flake.nix`

```nix
{
  description = "A minimal development shell";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs =
    { nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        packages = [
          pkgs.git
          pkgs.jq
        ];
      };
    };
}
```

읽는 순서는 다음과 같다.

1. `inputs.nixpkgs.url`: Nixpkgs 입력의 출처와 release 계열
2. `outputs`: 잠긴 입력을 받아 output 속성 집합을 만드는 함수
3. `system`: output이 적용되는 platform
4. `pkgs`: 그 입력과 platform에 대한 package 집합
5. `devShells.${system}.default`: 인자 없는 `nix develop`이 찾을 기본 개발 셸

첫 Flake 명령을 실행하면 `flake.lock`이 생길 수 있다.

```console
$ git add flake.nix
$ nix develop
```

Flake가 Git 저장소 안에 있으면 아직 Git index에 추가하지 않은 새 파일을 평가에서
보지 못할 수 있다. “파일이 분명히 있는데 없다”는 오류가 나면 `git status`와
`git add` 여부를 확인한다.

## 4.9 `flake.lock`은 언제 바뀌는가

`flake.nix`는 입력 URL을 선언하고 `flake.lock`은 실제 revision과 content hash를
기록한다. 팀원이 같은 두 파일을 받으면 같은 입력을 선택할 수 있다.

```text
flake.nix:  nixos-26.05 계열을 사용
flake.lock: 그 계열의 정확한 Git revision과 잠금 정보
```

업데이트는 일반 실행과 분리한다.

```console
$ nix flake update nixpkgs
$ git diff -- flake.lock
$ nix flake check
```

입력을 갱신한 뒤에는 diff와 build/check 결과를 검토하고 lockfile을 source와 함께
커밋한다. `flake.lock`을 무조건 삭제해 새로 만드는 것은 의도한 작은 업데이트보다
변경 범위를 크게 만들 수 있다.

## 4.10 purity와 shell의 격리 수준

Nix가 관리하는 package가 재현 가능해도 `nix shell`에 들어간 프로세스가 완전히
격리된 container가 되는 것은 아니다. 기본 shell은 기존 환경 변수, home 파일,
network, 작업 디렉터리를 볼 수 있다.

```console
$ nix shell nixpkgs#hello
$ echo "$HOME"
```

즉 다음은 서로 다르다.

- package 빌드 입력을 통제하는 Nix build sandbox
- 개발자가 사용하는 shell process의 편의 환경
- filesystem과 network까지 격리하는 container/VM

우연히 host의 도구를 사용하지 않는지 확인할 때는 `type -a <command>`,
`command -v <command>`, `nix develop --ignore-env` 같은 도구를 상황에 맞게 쓴다.
환경을 지울 때 필요한 변수도 함께 사라질 수 있으므로 프로젝트별로 검증한다.

## 4.11 자주 막히는 지점

| 증상 | 먼저 확인할 것 |
|---|---|
| `nix search` 결과가 없다 | 정규식 철자, 따옴표, 검색 Flake와 범위 |
| package는 찾았는데 예상한 명령이 없다 | package 이름과 실행 파일 이름의 차이, package 문서 |
| shell에서 host 명령이 선택된다 | `type -a <명령>`, `command -v <명령>`의 경로와 순서 |
| `nix develop .#name`이 output을 못 찾는다 | `nix flake show`에 현재 system의 `devShells.name`이 있는지 |
| 새 `flake.nix`를 못 찾거나 변경이 반영되지 않는다 | Git 저장소라면 `git status`와 Git index 포함 여부 |
| 다른 사람과 도구 revision이 다르다 | `flake.lock`이 존재하고 함께 커밋되었는지 |

`nix shell nixpkgs#...`는 registry가 그때 가리키는 Nixpkgs를 사용하므로 빠른 실험에는
편리하지만 프로젝트 명세는 아니다. 팀에서 되풀이할 개발 환경은 Flake 입력과
lockfile, `devShells`로 옮긴다.

## 직접 해보기

### 1. 검색 결과를 임시 shell로 연결

먼저 package 후보를 검색한다.

```console
$ nix search nixpkgs ripgrep
```

검색 결과에서 package 속성 이름 `ripgrep`과 설명을 확인하고 실행한다.

```console
$ nix shell nixpkgs#ripgrep --command rg --version
```

`ripgrep`과 `rg`가 왜 다른지 설명해 본다.

### 2. 임시 shell 전후 비교

현재 `cowsay`가 없다면 다음 결과는 실패할 수 있으며 정상이다.

```console
$ command -v cowsay
$ nix shell nixpkgs#cowsay
$ command -v cowsay
$ cowsay "temporary"
$ exit
$ command -v cowsay
```

shell 안의 경로가 `/nix/store/...`를 가리키고, 종료 뒤 원래 `PATH` 선택으로 돌아오는지
확인한다.

### 3. 검색 조건 조합

```console
$ nix search nixpkgs git gui
$ nix search nixpkgs 'firefox|chromium'
$ nix search nixpkgs editor --exclude 'emacs|vim'
```

첫 번째는 두 정규식을 모두 만족해야 하고, 두 번째는 둘 중 하나만 만족하면 된다.
검색량이 많을 수 있으므로 필요한 경우 `Ctrl-C`로 중단하고 조건을 더 구체화한다.

### 4. 개발 shell의 두 실행 방식

```console
$ cd project-with-flake
$ nix flake show
$ nix develop
$ exit
$ nix develop --command bash -c 'echo "inside dev shell"; command -v git'
```

`nix flake show`의 `devShells.<system>.default`와 인자 없는 `nix develop`이 어떻게
연결되는지 확인한다. 마지막 명령은 환경에 진입했다가 수동으로 나오는 대신 명령이
끝나면 바로 종료된다.

## 선택 연습

| 상황 | 선택 |
|---|---|
| 문서 변환을 위해 오늘만 `pandoc` 사용 | `nix shell nixpkgs#pandoc` |
| Python 프로젝트의 interpreter와 native library 고정 | `devShells` + `nix develop` |
| 내 모든 shell에서 `ripgrep` 사용 | Home Manager `home.packages` |
| 서버의 모든 관리자가 `tcpdump` 사용 | NixOS `environment.systemPackages` |
| `shell.nix`만 있는 기존 저장소 사용 | `nix-shell` |
| package의 결과 디렉터리 검사 | `nix build` |

## 요약

- `nix search`는 package 이름과 설명을 정규식으로 검색한다. 여러 정규식은 모두
  만족해야 한다.
- `nix shell`은 package 실행 파일을 잠깐 `PATH`에 제공한다.
- `nix develop`은 Flake의 `devShells` 또는 package가 선언한 개발·빌드 환경에
  들어간다.
- `nix-shell`은 기존 `.nix` 프로젝트와 문서에서 만나는 legacy 도구다.
- `nixpkgs#hello`는 Flake reference와 output 이름으로 나눠 읽는다.
- 임시 shell은 container가 아니며 기존 home, network, 환경 변수를 볼 수 있다.
- 지속할 환경은 `flake.nix`와 `flake.lock`, Home Manager 또는 NixOS에 선언한다.

## 공식 자료

- [nix.dev: Ad hoc shell environments](https://nix.dev/tutorials/first-steps/ad-hoc-shell-environments)
- [`nix search` reference](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-search.html)
- [`nix shell` reference](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-env-shell.html)
- [`nix develop` reference](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix3-develop.html)
- [Flakes 개념](https://nix.dev/concepts/flakes.html)
- [`nix` installable](https://nix.dev/manual/nix/2.34/command-ref/new-cli/nix.html#installables)

[← 3장](./03-store-builds-and-generations.md) · [목차](./index.md) ·
[5장: NixOS·Home Manager의 모듈 시스템 →](./05-module-system.md)
