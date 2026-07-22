# 6. uv, NVM, rustup으로 프로젝트 툴체인 관리

## 학습 목표

1. 도구 버전, 언어 런타임 버전, 프로젝트 의존성 잠금을 구분한다.
2. Python, Node.js, Rust 프로젝트를 각 생태계의 표준 파일로 복원한다.
3. Nix 입력 업데이트가 언어 도구에 미치는 영향을 예측한다.

## 6.1 세 층의 버전

| 계층 | Python | Node.js | Rust |
|---|---|---|---|
| Nix/Flake가 고정 | uv 패키지 | NVM 0.40.4 소스 | rustup 패키지 |
| 프로젝트가 고정 | `.python-version` | `.nvmrc` | `rust-toolchain.toml` |
| 의존성을 고정 | `uv.lock` | `package-lock.json` 등 | `Cargo.lock` |

Nixpkgs 입력의 리비전이 uv와 rustup 패키지 버전을 결정한다. NVM은 별도 Flake 입력의 태그와 잠금 리비전이 결정한다. 하지만 이 도구가 내려받는 Python, Node.js, Rust 툴체인은 각 프로젝트 파일의 책임이다.

이 설계는 Nix가 모든 언어 패키지를 대신 관리하는 방식보다 재현성 범위가 좁다. 대신 기존 프로젝트의 표준 파일과 CI 흐름을 유지한다.

## 6.2 Python과 uv

uv는 시스템에 적합한 Python이 없으면 관리형 Python을 자동으로 내려받을 수 있다. `.python-version`은 기본 Python 요청을, `pyproject.toml`은 프로젝트 요구사항을, `uv.lock`은 해결된 의존성을 기록한다.

새 프로젝트에서 정확한 Python 패치 버전을 선택하는 예시는 다음과 같다.

```console
$ uv python install 3.13.7
$ uv python pin 3.13.7
$ uv init
$ uv add httpx
$ git add .python-version pyproject.toml uv.lock
```

복원할 때는 잠금 파일을 수정하지 않도록 `--frozen`을 사용한다.

```console
$ uv sync --frozen
$ uv run python --version
Python 3.13.7
```

마이너 버전만 기록할 수도 있지만 정확한 패치 버전은 의도를 더 분명히 한다. uv 릴리스가 제공하는 다운로드 가능 Python 목록도 uv 버전에 묶이므로, 새 Python 패치가 필요하면 Nix 입력의 uv 업데이트 여부도 함께 확인한다.

## 6.3 Node.js와 NVM

NVM은 `.nvmrc`의 값을 읽어 Node.js를 설치하고 현재 셸의 PATH를 바꾼다. 새 프로젝트에서는 현재 지원되는 LTS를 선택한 뒤 실제 버전 문자열을 저장한다.

```console
$ nvm install --lts
$ node --version > .nvmrc
$ cat .nvmrc
v24.x.y
$ git add .nvmrc package.json package-lock.json
```

`lts/*`나 `24` 같은 별칭을 `.nvmrc`에 넣으면 나중에 설치할 때 더 최신 패치로 해석될 수 있다. 정확한 복원이 목표라면 `node --version`이 출력한 `vMAJOR.MINOR.PATCH`를 커밋한다.

다른 머신에서는 디렉터리에 들어올 때 zsh 훅이 버전을 설치·선택한다. 의존성은 별도로 잠금 파일에서 복원한다.

```console
$ cd project
$ node --version
$ npm ci
```

pnpm이나 Yarn을 사용한다면 해당 패키지 관리자의 lockfile과 Corepack 정책을 프로젝트에 기록한다. NVM은 Node 런타임만 관리한다.

## 6.4 Rust와 rustup

rustup은 `rustc`와 Cargo 앞의 프록시로 동작하며 디렉터리의 `rust-toolchain.toml`을 보고 툴체인을 선택한다.

파일: 프로젝트 루트의 `rust-toolchain.toml` (전체 예시)

```toml
[toolchain]
channel = "1.88.0"
profile = "minimal"
components = ["clippy", "rustfmt"]
```

파일과 의존성 잠금을 함께 커밋한다.

```console
$ git add rust-toolchain.toml Cargo.toml Cargo.lock
$ cargo build --locked
$ rustc --version
```

예제 사용자 프로필은 `RUSTUP_AUTO_INSTALL=1`을 설정하므로 지정 툴체인이 없으면 rustup 프록시가 설치할 수 있다. 자동 네트워크 사용을 원하지 않으면 `RUSTUP_AUTO_INSTALL=0`으로 바꾸고 다음을 명시적으로 실행한다.

```console
$ rustup toolchain install 1.88.0 \
    --profile minimal \
    --component clippy \
    --component rustfmt
```

## 6.5 프로젝트 복원 명령의 의미

```text
uv sync --frozen
  → Python 요청 확인
  → 필요한 관리형 Python 준비
  → uv.lock 그대로 환경 동기화

cd Node 프로젝트
  → .nvmrc 확인
  → 필요한 Node 설치/선택
  → npm ci로 package-lock.json 그대로 설치

cargo build --locked
  → rust-toolchain.toml의 툴체인 선택
  → Cargo.lock 변경 없이 빌드
```

Nix는 이 과정의 도구를 제공하지만 프로젝트 의존성 다운로드까지 Nix Store에 넣지는 않는다. 따라서 언어별 캐시와 설치 상태는 삭제 후 다시 만들 수 있는 파생 상태로 취급한다.

## 6.6 네이티브 라이브러리가 필요한 프로젝트

`gcc`와 `pkg-config`만으로 모든 C 라이브러리가 생기지는 않는다. OpenSSL, SQLite, PostgreSQL 헤더처럼 프로젝트별 네이티브 의존성이 필요하면 두 선택지가 있다.

1. 공통 개발 머신 전체에 필요하면 Home Manager 패키지에 추가한다.
2. 특정 프로젝트에만 필요하면 프로젝트의 `devShell`을 별도 Flake 출력으로 만든다.

이 자료의 전역 Flake는 범용 사용자 도구까지만 다룬다. 프로젝트별 `devShell`은 해당 프로젝트 저장소가 소유하는 편이 경계를 지키기 쉽다.

## 흔한 오류

| 증상 | 원인 | 해결 |
|---|---|---|
| `.nvmrc`가 있는데 매번 다른 패치 설치 | 별칭 또는 메이저만 기록 | 정확한 `node --version` 값을 커밋 |
| `uv sync`가 lock을 변경 | 복원과 갱신을 구분하지 않음 | CI·복원에서는 `uv sync --frozen` 사용 |
| `cargo build`가 다른 툴체인 사용 | 툴체인 파일 누락 또는 상위 override | `rustup show`, `rust-toolchain.toml` 위치 확인 |
| 네이티브 패키지 빌드 실패 | 시스템 라이브러리/헤더 누락 | 프로젝트 `devShell` 또는 필요한 Nix 패키지 추가 |

## 요약

- Nix는 버전 관리자 자체를, 프로젝트 파일은 런타임을 고정한다.
- 언어 버전 파일과 의존성 lockfile은 서로 다른 책임을 가진다.
- 정확한 패치 버전을 기록해야 시간에 따른 별칭 이동을 피할 수 있다.
- 프로젝트별 네이티브 의존성은 프로젝트 `devShell`로 분리하는 편이 좋다.

## 추가 읽을거리

- [uv Python 버전](https://docs.astral.sh/uv/concepts/python-versions/)
- [uv 프로젝트 동기화](https://docs.astral.sh/uv/concepts/projects/sync/)
- [NVM `.nvmrc` 사용법](https://github.com/nvm-sh/nvm#nvmrc)
- [rustup 툴체인 override](https://rust-lang.github.io/rustup/overrides.html)
- [rustup 환경 변수](https://rust-lang.github.io/rustup/environment-variables.html)

[← 5장](../05_home_manager/chapter.md) · [목차](../index.md) · [7장: nix develop과 direnv →](../07_nix_develop/chapter.md)
