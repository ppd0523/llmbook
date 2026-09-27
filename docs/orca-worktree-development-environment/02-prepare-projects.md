# 2. 두 예제 프로젝트 준비

## 학습 목표

이 장을 마치면 Python과 Node.js 예제를 각각 독립 Git 저장소로 만들고, 런타임 요청 파일·패키지 잠금 파일·설치 결과를 구분해 검증할 수 있다.

## 2.1 실습을 시작하는 위치

책 저장소의 예제 파일은 [Python 예제](./assets/python-demo/README.md)와 [Node.js 예제](./assets/node-demo/README.md)에 있다. 아래 명령은 `llmbook` 저장소 루트에서 시작한다. 두 예제를 **서로 다른 Git 저장소**로 복사해야 Orca가 각각의 worktree를 독립적으로 관리할 수 있다. `llmbook`의 `assets/` 폴더 안에서 `git init`을 실행하지 않는다.

```bash
mkdir -p "$HOME/orca-worktree-lab"
cp -R docs/orca-worktree-development-environment/assets/python-demo \
  "$HOME/orca-worktree-lab/python-demo"
cp -R docs/orca-worktree-development-environment/assets/node-demo \
  "$HOME/orca-worktree-lab/node-demo"
```

대상 폴더가 이미 있다면 다른 빈 경로를 선택한다. 새 worktree의 준비 시간을 비교할 때 기존 `.venv`나 `node_modules`가 섞이면 측정이 달라진다. 두 예제 모두 외부 서비스를 호출하지 않는다. 패키지 설치가 끝난 뒤의 프로그램 실행은 로컬에서 가능하다.

## 2.2 Python 3.14 프로젝트

Python 예제의 핵심 파일은 다음과 같다.

| 파일 | 역할 | Git 추적 |
|---|---|---|
| `.python-version` | Python 3.14 계열 요청 | 예 |
| `pyproject.toml` | 프로젝트와 Rich 의존성 선언 | 예 |
| `uv.lock` | 해결된 패키지 버전과 배포 파일 기록 | 예 |
| `main.py` | Rich를 불러와 준비 결과 출력 | 예 |
| `setup-worktree.sh` | 새 워크트리의 uv 동기화 명령 | 예 |
| `.env.example`, `.worktreeinclude` | 실습 변수의 예시와 Orca의 작업별 복사 목록 | 예 |
| `.env` | 이 컴퓨터에서 사용할 로컬 값 | 아니요 |
| `.venv/` | 이 작업 폴더의 Python 실행 환경 | 아니요 |

uv는 `.python-version`을 버전 요청으로 읽고, 프로젝트의 기본 가상환경을 `.venv`에 만든다. `uv.lock`은 `pyproject.toml`과 함께 Git에 넣는 것이 공식 권장 방식이다. 여기의 `3.14`는 패치 버전을 고정하지 않으므로 실제 `python --version` 결과는 실행 시점에 기록한다. [uv Python 버전](https://docs.astral.sh/uv/concepts/python-versions/), [uv 프로젝트 구조](https://docs.astral.sh/uv/concepts/projects/layout/)

```bash
cd "$HOME/orca-worktree-lab/python-demo"
cp .env.example .env
uv python install 3.14
uv sync --locked
uv run --locked python main.py
uv run --locked python --version
uv --version
```

첫 명령은 Python 3.14 계열이 없다면 설치할 수 있다. 이 **런타임 준비 시간은 새 worktree의 패키지 준비 시간과 따로 기록**한다. `uv sync --locked`는 잠금 파일의 변경이 필요하면 오류를 내므로 예제의 버전 집합이 그대로 쓰였는지 확인하기 좋다. 기대 프로그램 출력은 다음과 같다. Python 패치 버전은 독자의 환경에 따라 다르다. [uv CLI](https://docs.astral.sh/uv/reference/cli/)

```text
Python worktree ready (rich 14.3.3)
```

이제 Git 저장소를 초기화한다.

```bash
git init -b main
git add .python-version .gitignore .env.example .worktreeinclude README.md pyproject.toml uv.lock main.py setup-worktree.sh
git status --short
git commit -m "Initialize Python worktree demo"
```

`git status --short`의 추가 대상에 `.venv/`와 `.env`가 없어야 한다. `.gitignore`에 두 경로가 들어 있다. `.env.example`과 `.worktreeinclude`는 추적한다. [uv 프로젝트 구조](https://docs.astral.sh/uv/concepts/projects/layout/), [Orca Worktrees](https://www.onorca.dev/docs/model/worktrees)

## 2.3 Node.js v24 프로젝트

Node 예제도 잠금 파일과 설치 결과를 분리한다.

| 파일 | 역할 | Git 추적 |
|---|---|---|
| `.nvmrc` | Node v24 계열 요청 | 예 |
| `package.json` | npm 프로젝트와 `picocolors` 의존성 | 예 |
| `package-lock.json` | npm이 설치할 정확한 패키지 집합 | 예 |
| `index.mjs` | 패키지를 불러와 준비 결과 출력 | 예 |
| `setup-worktree.sh` | 새 워크트리의 nvm·npm 준비 명령 | 예 |
| `.env.example`, `.worktreeinclude` | 실습 변수의 예시와 Orca의 작업별 복사 목록 | 예 |
| `.env` | 이 컴퓨터에서 사용할 로컬 값 | 아니요 |
| `node_modules/` | 이 작업 폴더의 npm 설치 결과 | 아니요 |

`nvm`은 현재 셸에서 Node 버전을 고른다. `.nvmrc`의 `24`는 v24 계열의 요청이며 패치 버전은 고정하지 않는다. `nvm`이 셸에 아직 로드되지 않았다면 설치할 때 지정한 `NVM_DIR`의 `nvm.sh`를 불러온다. 아래는 일반적인 `~/.nvm` 설치 경로의 예다. [nvm README](https://github.com/nvm-sh/nvm)

```bash
cd "$HOME/orca-worktree-lab/node-demo"
cp .env.example .env
export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
. "$NVM_DIR/nvm.sh"
nvm use 24
npm ci
npm start
node --version
npm --version
```

`nvm use 24`가 설치된 v24를 찾지 못하면 **측정 전에** `nvm install 24`를 한 번 실행한다. `npm ci`는 `package-lock.json`을 요구하고 파일을 수정하지 않으며, `package.json`과 내용이 맞지 않으면 실패한다. 기대 프로그램 출력은 다음과 같다. [npm ci](https://docs.npmjs.com/cli/v11/commands/npm-ci/)

```text
Node worktree ready
```

```bash
git init -b main
git add .nvmrc .gitignore .env.example .worktreeinclude README.md package.json package-lock.json index.mjs setup-worktree.sh
git status --short
git commit -m "Initialize Node worktree demo"
```

`node_modules/`와 `.env`가 추가 대상에 없어야 한다. `package-lock.json`은 추적하지만 설치된 패키지 디렉터리는 새 worktree에서 다시 구성한다. Git 명령으로 만든 3·4장의 워크트리에는 `.env`가 자동 복사되지 않는다. Orca의 `.worktreeinclude` 복사는 5장에서 확인한다. [Orca Worktrees](https://www.onorca.dev/docs/model/worktrees)

## 2.4 기준 상태를 기록한다

두 저장소 각각에서 다음을 기록한다. 이후 에이전트가 "같은 의존성을 쓴다"고 말할 때 브랜치와 잠금 파일이 실제로 같은지 확인하기 위한 기준이다.

```bash
pwd
git branch --show-current
git rev-parse HEAD
git status --short
```

Git worktree는 같은 저장소의 브랜치별 작업 파일을 분리한다. 다른 브랜치에서 `uv.lock`이나 `package-lock.json`을 바꾸면 경로 이름만으로 의존성 상태를 판단할 수 없다. 각 작업의 시작 커밋과 잠금 파일 변경을 함께 봐야 한다. [Git worktree 문서](https://git-scm.com/docs/git-worktree)

## 직접 해보기

1. Python 저장소에서 `git ls-files`로 추적 파일을 열거한다. `.venv/`가 보이는가?
2. Node 저장소에서 `node --version`과 `cat .nvmrc`를 비교한다. 패치 버전이 다른 이유를 설명한다.
3. 각 저장소에서 `git status --short`가 비어 있는지 확인한다. 비어 있지 않다면 어떤 파일이 추적되거나 무시되는지 확인한다.

**확인:** 잠금 파일과 버전 요청 파일은 추적하고 설치 결과는 추적하지 않는다. 버전 요청의 `3.14`·`24`는 계열만 지정한다.

[3장: uv 환경과 캐시 재사용 →](./03-uv-across-worktrees.md)
