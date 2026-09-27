# 1. 워크트리와 의존성 경계

## 학습 목표

이 장을 마치면 Git이 공유하는 상태와 워크트리마다 새로 준비할 상태를 경로로 구분하고, 새 워크트리의 설치 메시지를 곧바로 재다운로드로 해석하지 않을 수 있다.

## 1.1 새 작업 폴더에는 왜 패키지가 없을까

Orca에서 같은 저장소의 작업을 에이전트 세 명에게 나누어 맡긴다고 하자. Orca는 각 작업에 **Git worktree**를 만든다. Git worktree는 하나의 Git 저장소에 연결된 별도 작업 디렉터리다. 커밋 객체와 대부분의 참조(ref)는 공유하지만, 작업 파일·인덱스·`HEAD`는 각각 갖는다. Orca도 작업마다 브랜치와 파일, 에이전트 터미널을 둔다. [Git worktree 문서](https://git-scm.com/docs/git-worktree), [Orca worktree 문서](https://www.onorca.dev/docs/model/worktrees)

```text
저장소의 공통 Git 데이터
├── 원래 작업 폴더: main, .venv/, node_modules/
├── 작업 A 폴더:  feature/a, 새 .venv/ 또는 node_modules/
└── 작업 B 폴더:  feature/b, 새 .venv/ 또는 node_modules/
```

그림의 `.venv/`와 `node_modules/`는 Git이 추적하지 않는 **설치 결과**다. 새 워크트리는 선택한 커밋의 추적 파일을 체크아웃하므로 원래 폴더의 설치 결과가 자동으로 따라오지 않는다. 이는 Orca의 [깨끗한 워크트리 생성 방식](https://www.onorca.dev/docs/model/worktrees)과 맞는다. 반대로 `pyproject.toml`, `uv.lock`, `package.json`, `package-lock.json`을 커밋했다면 새 작업 폴더에도 해당 브랜치의 파일이 생긴다.

같은 로컬 브랜치를 여러 워크트리에서 동시에 체크아웃하는 것은 Git이 기본적으로 막는다. 병렬 에이전트에는 작업별 브랜치를 주고, 시작 커밋과 변경 파일을 확인한다. 브랜치 이름이 다르다고 설치 결과까지 분리되는 것은 아니며, 설치 경로도 따로 두어야 한다. [Git worktree 문서](https://git-scm.com/docs/git-worktree)

## 1.2 여섯 층을 따로 본다

| 층 | Python 실습 | Node.js 실습 | 기본 범위 |
|---|---|---|---|
| 작업 파일 | `main.py`, `pyproject.toml`, `uv.lock` | `index.mjs`, `package.json`, `package-lock.json` | 워크트리·브랜치별 |
| 런타임 요청 | `.python-version`의 `3.14` | `.nvmrc`의 `24` | 워크트리·브랜치별 파일 |
| 설치된 런타임 | uv가 찾거나 설치한 Python | nvm에 설치된 Node | 사용자 계정에서 재사용 가능 |
| 다운로드 캐시 | `uv cache dir` | `npm config get cache` | 보통 사용자 계정에서 재사용 |
| 패키지 설치 결과 | `.venv/` | `node_modules/` | 워크트리별로 준비 |
| 셸의 선택 상태 | 실행 명령의 Python 경로 | `nvm use`가 바꾼 `PATH` | 실행 중인 셸별 |

`nvm`은 Node 런타임을 고르는 도구이며 프로젝트의 npm 패키지를 설치하지 않는다. `uv`는 프로젝트의 Python 선택과 의존성 동기화를 수행한다. npm은 잠금 파일을 읽어 `node_modules`를 구성한다. 도구의 역할을 나누면 "Node는 이미 설치했는데 패키지가 없다"는 상황이 자연스럽다. [nvm README](https://github.com/nvm-sh/nvm), [uv 프로젝트 구조](https://docs.astral.sh/uv/concepts/projects/layout/), [npm ci](https://docs.npmjs.com/cli/v11/commands/npm-ci/)

## 1.3 다운로드와 설치는 다른 시간이다

첫 워크트리에서 패키지를 받으면 `uv`와 npm은 각자의 캐시에 데이터를 남길 수 있다. 다음 워크트리는 같은 데이터를 캐시에서 읽더라도 `.venv`나 `node_modules`를 만들어야 한다. 따라서 설치 로그의 `Installed`와 네트워크에서 받는 `Downloading`을 구별한다. `uv`는 캐시로 재다운로드와 재빌드를 줄이고, npm도 캐시를 사용하지만 `npm ci`는 실행할 때마다 기존 `node_modules`를 지우고 다시 설치한다. [uv 캐시](https://docs.astral.sh/uv/concepts/cache/), [npm 캐시](https://docs.npmjs.com/cli/v11/commands/npm-cache/), [npm ci](https://docs.npmjs.com/cli/v11/commands/npm-ci/)

macOS에서 uv의 기본 패키지 설치 방식은 Copy-on-Write 복제다. 이는 복제 직후 데이터를 공유하고 어느 한쪽을 수정할 때 분리하는 파일시스템 동작이다. 캐시와 가상환경이 **같은 파일시스템**에 있어야 이 방식의 이점을 얻는다. 같은 물리 디스크에 있어도 서로 다른 볼륨이면 복사 방식으로 물러날 수 있다. 이 조건은 6장에서 실제 경로와 시간으로 확인한다. [uv 캐시](https://docs.astral.sh/uv/concepts/cache/), [uv 링크 모드](https://docs.astral.sh/uv/reference/settings/#link-mode)

## 1.4 병렬 작업의 안전한 기본 경계

에이전트마다 **다른 워크트리와 브랜치**, 워크트리마다 **다른 설치 결과**, 같은 사용자와 컴퓨터에서는 **공용 다운로드 캐시**를 기본으로 둔다. 이 권고는 패키지 관리자의 캐시 재사용과 브랜치별 잠금 파일 차이를 함께 수용한다. `uv` 캐시는 병렬 읽기·쓰기를 고려해 설계되어 있고 환경 변경 시 해당 환경에 잠금을 건다. [uv 캐시 안전성](https://docs.astral.sh/uv/concepts/cache/)

```text
작업 A: uv.lock A ──> 작업 A/.venv ──┐
                                      ├──> 사용자별 uv 캐시
작업 B: uv.lock B ──> 작업 B/.venv ──┘

작업 C: package-lock.json C ──> 작업 C/node_modules ──┐
                                                       ├──> 사용자별 npm 캐시
작업 D: package-lock.json D ──> 작업 D/node_modules ──┘
```

공용 캐시와 공용 설치 결과는 다르다. 두 브랜치가 같은 `.venv`나 `node_modules`를 심볼릭 링크로 공유하면 한쪽의 동기화가 다른 쪽의 실행 중인 환경을 바꿀 수 있다. 5장에서 Orca Shared Paths의 APFS 복제와 심볼릭 링크 대체 동작까지 나누어 판단한다. [Orca 공유 경로](https://www.onorca.dev/docs/model/worktrees), [uv 동기화](https://docs.astral.sh/uv/concepts/projects/sync/), [npm ci](https://docs.npmjs.com/cli/v11/commands/npm-ci/)

## 확인 문제

1. `uv.lock`은 새 워크트리에 있는데 `.venv/`가 없다. 무엇이 잘못되었는가?
2. 같은 사용자로 만든 두 워크트리에서 `npm config get cache`는 같고 `node_modules` 경로는 다르다. 재사용되는 것은 무엇인가?

**확인:** 1번은 정상적인 새 체크아웃이다. 잠금 파일은 Git 추적 파일이고 `.venv/`는 작업별 설치 결과다. 2번은 다운로드 캐시를 재사용하면서 각 작업 폴더에 별도 설치 결과를 만든다.

[2장: 두 예제 프로젝트 준비 →](./02-prepare-projects.md)
