# 5. Orca 병렬 작업과 setup hook

## 학습 목표

이 장을 마치면 Orca에 두 예제 저장소를 등록하고, 새 워크트리가 생성될 때 잠금 파일과 로컬 설정에 맞춰 환경을 준비하며, 3~5개 에이전트가 동시에 작업할 때 발생하는 충돌을 작업 파일·설치 결과·캐시·Git 이력의 경계에서 설명할 수 있다.

## 5.1 하나의 작업에는 하나의 워크트리와 브랜치

Orca는 워크트리를 만들 때 시작 ref를 고르고, 작업마다 별도의 브랜치·파일·에이전트 터미널을 둔다. 2장에서 만든 `python-demo`와 `node-demo`는 **별도 Git 저장소**이므로 Orca에도 각각 프로젝트로 등록한다. Orca의 프로젝트 추가에서 두 폴더를 선택한다. 이미 Git 명령으로 만든 `python-a`·`python-b`·`node-a`·`node-b`는 외부 워크트리로 나타날 수 있고, 숨겨져 있다면 해당 프로젝트의 **Non-Orca worktrees**에서 표시할 수 있다. [Orca Worktrees](https://www.onorca.dev/docs/model/worktrees)

이 장의 Orca 실습은 각 프로젝트에서 **새 작업 이름**을 사용한다. 생성 화면에서 시작 ref를 `main`으로 명시한다. 원격 저장소가 없는 2장의 실습에는 `origin/main`이 없다. 같은 브랜치를 여러 워크트리에 체크아웃하려 하면 Git이 기본적으로 거부하므로, 이름과 브랜치가 겹치지 않게 한다. 생성 화면의 고급 옵션에서 브랜치 이름을 직접 지정할 수도 있다. [Orca Worktrees](https://www.onorca.dev/docs/model/worktrees), [Git worktree 문서](https://git-scm.com/docs/git-worktree)

| 작업 | 예제 저장소 | 시작 ref | 요청할 작업 |
|---|---|---|---|
| `py-check-a`, `py-check-b`, `py-change` | `python-demo` | `main` | 같은 환경 2개 확인, Rich 버전 변경 1개 |
| `node-check-a`, `node-change` | `node-demo` | `main` | 같은 환경 확인 1개, Chalk 추가 1개 |

표는 **최대 5개 작업을 동시에** 관찰하는 예다. 먼저 Python 작업 2개와 Node 작업 1개로 시작하고, 준비 시간과 자원 사용량을 확인한 뒤 나머지 둘을 추가해도 된다. 에이전트마다 아래처럼 경로와 시작 상태를 먼저 출력하게 하면 결과를 합칠 때 출처를 구별할 수 있다.

```bash
pwd
git rev-parse --show-toplevel
git branch --show-current
git rev-parse HEAD
git status --short
```

**작업 지시 예:** “이 워크트리에서만 작업하세요. 먼저 위 다섯 명령의 결과를 보고하세요. 잠금 파일을 수정했다면 변경 이유와 `git diff -- uv.lock` 또는 `git diff -- package-lock.json` 결과를 요약하고, 이 워크트리의 실행 명령으로 검증하세요.” 에이전트가 같은 저장소의 다른 워크트리까지 수정하지 않도록 작업 범위를 명시한다.

## 5.2 생성 직후 setup hook

Orca의 **Settings → Repository → Hooks**에서 저장소별 워크트리 setup 명령을 설정한다. 공식 문서는 생성 뒤 명령을 자동 실행한다고 설명한다. 다만 hook이 어떤 셸·시작 디렉터리에서 실행되는지는 여기서 단정하지 않는다. 먼저 각 저장소에 다음 진단 명령 **한 줄**을 넣고 워크트리 하나를 만들어 로그에서 경로와 도구를 확인한다. [Orca Agent hooks](https://www.onorca.dev/docs/agents/hooks-memory)

```sh
sh -c 'pwd; git rev-parse --show-toplevel; command -v uv; command -v node'
```

진단 결과의 Git 루트가 **새 워크트리**인지 확인한다. 다른 폴더에서 시작한다면 해당 Orca 버전의 hook 실행 설정에 맞춰 이동 경로를 명시한다. 각 예제의 `setup-worktree.sh`는 Git에 들어 있으므로 새 워크트리에서도 사용할 수 있다. Python 저장소의 hook에는 다음 한 명령을 넣는다. `--locked`는 선언 파일과 잠금 파일이 어긋난 경우 조용히 해결을 바꾸지 않고 실패한다. `uv`가 hook의 `PATH`에 없다면 스크립트에 실제 실행 파일 경로를 지정한다. [uv 동기화](https://docs.astral.sh/uv/concepts/projects/sync/)

```sh
sh ./setup-worktree.sh
```

Node 저장소에도 같은 명령을 hook으로 넣는다. Node 예제의 스크립트가 hook 셸에서 `nvm.sh`를 불러오고 `nvm use 24`, `npm ci`를 실행한다. `NVM_DIR`을 다르게 설치했다면 스크립트에서 실제 위치로 바꾼다. 두 스크립트 모두 **새 워크트리 루트에서 실행**해야 잠금 파일을 읽는다. [nvm README](https://github.com/nvm-sh/nvm), [npm ci](https://docs.npmjs.com/cli/v11/commands/npm-ci/)

```sh
sh ./setup-worktree.sh
```

hook 스크립트는 별도 셸에서 실행되므로 그 안의 `nvm use 24`가 이후 에이전트 터미널의 Node 선택을 바꾸지는 않는다. Node 작업의 에이전트 터미널에서도 4.2절처럼 `nvm.sh`를 불러와 `nvm use 24`와 `node --version`을 확인한다. [nvm README](https://github.com/nvm-sh/nvm)

Orca CLI를 쓰는 경우 `orca worktree create --setup run|skip|inherit`로 저장소 정책의 실행 여부를 선택할 수 있다. 이 책의 실습은 GUI에서 작업 이름·시작 ref·에이전트를 눈으로 확인하며 만든다. 새 워크트리 생성은 백그라운드로 진행될 수 있으므로 **setup 결과를 확인한 뒤** 에이전트의 코드 변경을 시작한다. hook이 실패한 작업은 설치 상태를 진단하고 해당 워크트리에서 같은 설치 명령을 다시 실행한다. [Orca CLI](https://www.onorca.dev/docs/cli/reference), [Orca Worktrees](https://www.onorca.dev/docs/model/worktrees)

이 setup은 **워크트리 생성 시점의 준비**다. 이후 에이전트가 의존성을 추가하거나 다른 브랜치의 잠금 파일 변경을 가져오면 hook 실행 여부와 관계없이 해당 워크트리에서 `uv sync --locked` 또는 `npm ci`를 다시 실행한다. 잠금 파일과 설치 결과는 자동으로 서로 따라가지 않는다. [uv 동기화](https://docs.astral.sh/uv/concepts/projects/sync/), [npm ci](https://docs.npmjs.com/cli/v11/commands/npm-ci/)

## 5.3 같은 시작점에서 3~5개 에이전트 실행

Orca의 생성 화면에서 5.1절의 작업 이름을 차례로 만들고 각 작업의 시작 ref를 `main`으로 고른다. 작업마다 Agent를 선택하면 Orca가 해당 워크트리의 에이전트 탭을 열고, Blank Terminal을 선택하면 일반 셸로 시작한다. Orca의 병렬 작업 예제도 같은 시작점에서 세 워크트리를 만든 뒤 각 에이전트의 diff를 비교한다. [Orca Worktrees](https://www.onorca.dev/docs/model/worktrees), [Orca 병렬 에이전트 예제](https://www.onorca.dev/docs/recipes/parallel-agents)

1. `py-check-a`와 `py-check-b`에는 `uv run --locked python main.py`를 실행하게 한다. 두 작업에서 출력 버전은 같고 `.venv` 경로는 달라야 한다.
2. `py-change`에는 Rich를 15.0.0으로 바꾸고 `pyproject.toml`·`uv.lock`의 diff와 실행 결과를 보고하게 한다. 변경이 필요한 이 작업의 다운로드는 다른 두 작업의 캐시 재사용 실패가 아니다.
3. `node-check-a`와 `node-change`에는 먼저 해당 터미널에서 `nvm use 24`와 `node --version`을 확인하게 한다. 전자에는 `npm start`를, 후자에는 4.3절의 Chalk 추가와 `npm ci`를 수행하게 한다. 두 작업의 `package-lock.json` 차이를 비교한다.
4. 각 작업의 setup 시간, `uv cache dir` 또는 `npm config get cache`, 실행 결과, Git diff를 별도 줄로 기록한다. 동일한 잠금 파일 작업 둘과 변경 작업을 섞어서 평균 내지 않는다.

Python과 Node 저장소 사이에는 공유 Git 이력이 없다. **같은 저장소 안의** 워크트리끼리는 Git 객체와 ref를 공유하지만 작업 파일·인덱스·HEAD는 따로 있다. 한 브랜치에서 `uv.lock`이나 `package-lock.json`을 수정해도 다른 브랜치에 자동 반영되지 않는다. 반대로 다른 브랜치의 변경을 merge·cherry-pick으로 가져오면 잠금 파일과 설치 결과의 관계를 다시 확인해야 한다. [Git worktree 문서](https://git-scm.com/docs/git-worktree)

## 5.4 병렬 작업에서 충돌하는 네 경계

| 경계 | 동시에 일어나는 일 | 확인과 조치 |
|---|---|---|
| 같은 작업 폴더 | 두 에이전트가 같은 파일과 `node_modules`를 바꿈 | 에이전트마다 별도 워크트리를 배정하고 `pwd`·Git 루트를 보고하게 한다. |
| 다른 브랜치의 잠금 파일 | 두 에이전트가 각각 의존성을 갱신함 | 각 diff와 실행 결과를 검토한다. 병합 뒤 잠금 파일을 다시 동기화하고 실행한다. |
| 사용자 캐시 | 여러 설치가 동시에 새 패키지를 요청함 | 캐시 경로를 통일한다. uv 캐시는 동시 접근을 지원하고 npm 캐시는 무결성을 검사한다. 대량 병렬 설치에서는 CPU·디스크·네트워크 경쟁도 시간을 늘릴 수 있다. |
| 작업 밖의 상태 | 설치 스크립트나 에이전트가 사용자 전역 파일을 수정함 | 명령이 쓰는 경로를 확인한다. 워크트리는 프로젝트 파일을 분리하지만 사용자 홈의 임의 파일까지 격리하지 않는다. |

첫째·둘째·넷째 줄은 Git의 작업 파일 분리 범위에서 나온 **운영 판단**이다. 캐시의 동시 접근에 관해서는 [uv 캐시](https://docs.astral.sh/uv/concepts/cache/)와 [npm 캐시](https://docs.npmjs.com/cli/v11/commands/npm-cache/)를 참고한다. 설치 중 병렬 작업이 더 느리다면 캐시를 지우기 전에 동시 작업 수를 줄여 같은 명령의 시간을 다시 측정한다.

## 5.5 Shared Paths를 의존성 디렉터리에 쓰기 전에

Orca의 **Worktree Shared Paths**는 기본 체크아웃의 Git 무시 경로를 새 워크트리에 준비한다. macOS에서 조건이 맞으면 APFS clone-copy로 만들고, 그렇지 않으면 심볼릭 링크로 연결한다. `orca.yaml`의 `worktree.sharedDirectories`도 공유 목록에 더할 수 있고, `.worktreeinclude`는 무시된 경로를 작업별로 복사한다. 어떤 방식이 실제로 적용됐는지는 파일시스템과 원본 상태에 따라 달라진다. [Orca Worktrees](https://www.onorca.dev/docs/model/worktrees)

| 대상 | APFS clone-copy가 된 경우 | 심볼릭 링크가 된 경우 |
|---|---|---|
| `.venv/` | 복제 파일 안의 절대 경로·editable 소스 참조가 옛 워크트리를 가리킬 수 있다. | 한 브랜치의 `uv sync`가 다른 브랜치의 환경을 바꿀 수 있다. |
| `node_modules/` | 복제 비용이 들고, setup의 `npm ci`가 복제본을 지운 뒤 다시 만든다. | `npm ci`가 링크를 따라가거나 링크 자체를 교체하는 동작에 의존하게 되어 브랜치별 설치를 보장하기 어렵다. |

Python 가상환경은 이동 가능한 묶음으로 설계되지 않았고, uv 동기화는 기본적으로 잠금 파일에 맞춰 불필요한 패키지를 제거한다. `npm ci`도 기존 `node_modules`를 제거하고 새로 설치한다. 따라서 이 책의 기본 설정에서는 **`.venv/`와 `node_modules/`를 Shared Paths, `orca.yaml`, `.worktreeinclude`에 넣지 않는다.** 사용자 캐시와 런타임은 재사용하고 설치 결과는 작업별로 만든다. [Python venv](https://docs.python.org/3.14/library/venv.html), [uv 동기화](https://docs.astral.sh/uv/concepts/projects/sync/), [npm ci](https://docs.npmjs.com/cli/v11/commands/npm-ci/)

이미 공유 설정이 있는 저장소라면 먼저 `test -L .venv`, `test -L node_modules`, `readlink .venv`, `readlink node_modules`로 심볼릭 링크 여부를 살핀다. 링크가 아니어도 APFS 복제나 일반 복사가 있었는지는 별도 확인이 필요하다. **링크가 아니라는 사실만으로 안전한 새 환경이라고 판단하지 않는다.**

## 5.6 패키지 밖의 도구 스크립트와 .env

빌드·테스트 명령이 개인 도구 스크립트에만 있고 Git에서 무시된다면 새 워크트리는 그 명령을 알 수 없다. `.env`도 마찬가지다. `uv sync`와 `npm ci`는 패키지를 준비할 뿐, Git 무시 파일을 복원하지 않는다. 파일의 **역할**에 따라 준비 방법을 선택한다. [Orca Worktrees](https://www.onorca.dev/docs/model/worktrees)

| 파일의 역할 | 권장 위치와 방법 | 이유 |
|---|---|---|
| 팀 공통 빌드·테스트 명령, setup 진입점 | Git에 추적한 `scripts/`, `Makefile` 또는 프로젝트 명령 | 모든 브랜치에서 동일한 절차로 시작한다. 이 책의 `setup-worktree.sh`도 추적 파일이다. |
| 작업마다 바꿀 `.env`, 개인 설정, 무시된 보조 스크립트 | 기본 작업 폴더에서 Orca `.worktreeinclude`로 **작업별 복사** | 한 에이전트의 수정이 다른 워크트리의 파일을 곧바로 바꾸지 않는다. |
| 여러 작업이 읽기만 하는 큰 로컬 자원 | 사용자가 관리하는 공통 경로를 명시하거나 Shared Paths의 실제 방식을 확인 | 심볼릭 링크로 연결될 수 있으므로 쓰기 작업과 섞지 않는다. |

공통 명령 전체를 Git 밖에 두기보다, **재현 가능한 명령은 추적**하고 컴퓨터마다 다른 경로·값만 Git 무시 파일로 남긴다. 비밀 값이 필요한 경우에도 추적하는 `.env.example`에는 키 이름과 무해한 예시만 둔다. `.env`는 Git에서 무시한다. 프로젝트가 실제로 어떤 값이 필요한지 알려 주면서 값 자체는 커밋하지 않는 구성이다. [Git ignore 문서](https://git-scm.com/docs/gitignore)

2장의 두 예제는 `.gitignore`에서 `.env`를 무시하고, 추적된 `.worktreeinclude`에는 아래 한 줄이 있다. 기본 작업 폴더에는 `.env.example`에서 만든 **비밀이 아닌** `.env`가 이미 있다. 새 Orca 워크트리에서 이 파일의 작업별 사본을 확인한다. `.worktreeinclude`는 리터럴 경로만 지원하며, 원본이 없거나 추적된 경로는 복사하지 않는다. 같은 경로를 Shared Paths에도 등록했다면 공유 설정이 우선할 수 있으므로 중복 등록하지 않는다. [Orca Worktrees](https://www.onorca.dev/docs/model/worktrees)

```text
# .worktreeinclude — 이 파일 자체는 Git에 추적
.env
```

```bash
# 기본 작업 폴더에서, 내용을 출력하지 않고 준비 상태만 확인
git check-ignore -v .env
test -f .env
git ls-files .worktreeinclude
```

새 Orca 워크트리를 만든 뒤에는 파일의 존재와 링크 여부를 확인한다. `.worktreeinclude`의 복사는 **생성 당시의 사본**이므로 나중에 원본을 바꿔도 기존 작업 폴더가 자동 갱신된다고 가정하지 않는다. 일반 `git worktree add`는 Orca의 `.worktreeinclude`를 처리하지 않는다. [Orca Worktrees](https://www.onorca.dev/docs/model/worktrees), [Git worktree 문서](https://git-scm.com/docs/git-worktree)

```bash
# 새 워크트리에서, 파일 내용은 표시하지 않는다
test -f .env && test ! -L .env
```

개인 도구 스크립트 `tools/local-test.sh`도 복사하려면 그 **리터럴 경로**를 `.gitignore`와 `.worktreeinclude`에 추가해 커밋하고, 기본 작업 폴더에 파일을 준비한다. `git check-ignore -v tools/local-test.sh`와 `test -f tools/local-test.sh`로 원본을 먼저 확인한다. Orca setup hook이 이 무시된 스크립트에 의존한다면 파일 준비 순서를 해당 버전에서 확인한다. 가장 단순한 시작점은 이 책의 예제처럼 hook 진입 스크립트를 Git에 넣는 것이다. [Orca Worktrees](https://www.onorca.dev/docs/model/worktrees)

`.env`의 **복사만으로** 실행 셸에 변수가 적용되지는 않는다. Python 예제라면 `uv run --locked --env-file .env python main.py`, Node v24 예제라면 `node --env-file=.env index.mjs`처럼 실행 명령에서 명시한다. 어떤 빌드·테스트 명령이 `.env`를 읽는지도 같은 방식으로 확인한다. [uv 환경 파일](https://docs.astral.sh/uv/configuration/files/#environment-variable-files), [Node.js 명령줄 옵션](https://nodejs.org/api/cli.html#--env-filefile)

앞서 넣은 `WORKTREE_LABEL=local`이 실제 프로세스에 전달되는지 **값을 출력하지 않고** 확인할 수도 있다. 첫 줄은 Python 저장소, 둘째 줄은 Node 저장소에서 실행한다. Node 명령은 해당 터미널에서 `nvm use 24`를 실행한 뒤 사용한다.

```bash
uv run --locked --env-file .env python -c 'import os; assert os.getenv("WORKTREE_LABEL")'
node --env-file=.env -e 'if (!process.env.WORKTREE_LABEL) process.exit(1)'
```

실제 인증 정보가 든 `.env`를 복사하면 워크트리 수만큼 사본이 생기고 각 작업의 에이전트가 읽을 수 있다. 이 방법을 쓰기 전에 그 접근 범위가 적절한지 판단한다. 진단 로그에는 파일의 존재 여부만 남기고 내용과 변수 값을 출력하지 않는다. 다른 경로에서 값을 공급하는 팀은 그 경로를 setup 절차에 명시한다.

## 직접 해보기

1. `py-change`가 Rich 15를 설치한 직후 `py-check-a`에서 Rich 14가 사라졌다. 두 워크트리의 `pwd`, `git rev-parse --show-toplevel`, `test -L .venv`, `uv cache dir`를 비교해 보자. 어느 결과라면 공유 캐시는 정상이고, 어느 결과라면 두 작업이 설치 결과를 공유한 것인가?
2. 3·4장에서 Git 명령으로 만든 워크트리에는 `.env`가 없는데 5장의 새 Orca 워크트리에는 있다. 두 생성 경로의 차이를 설명하고, Orca 작업에서 `.env`가 심볼릭 링크인지 확인해 보자.

**확인:** 1번에서 같은 `uv cache dir`는 정상이다. 두 워크트리의 `.venv`가 같은 실제 경로를 가리키거나 에이전트가 같은 작업 폴더에서 실행됐다면 작업 격리가 깨진다. 2번에서 Git 자체는 `.worktreeinclude`를 처리하지 않고 Orca가 무시 파일을 복사한다. `test -f .env && test ! -L .env`로 Orca 작업의 독립 사본을 확인한다.

[6장: 준비 시간 측정과 문제 해결 →](./06-measure-and-troubleshoot.md)
