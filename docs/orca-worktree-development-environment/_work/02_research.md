# 조사 노트: Orca 병렬 워크트리의 uv·nvm·npm 의존성

확인일: 2026-09-26. **확인**은 공식 문서의 명시적 동작, **판단**은 이 책의 운영 권고다.

## 핵심 출처

| 영역 | 공식 문서 | 본문에 쓸 내용 |
|---|---|---|
| Git | [git-worktree](https://git-scm.com/docs/git-worktree) | 공유 Git 저장소와 별도 작업 파일·인덱스·HEAD |
| Orca | [Worktrees](https://www.onorca.dev/docs/model/worktrees), [Hooks](https://www.onorca.dev/docs/agents/hooks-memory), [CLI](https://www.onorca.dev/docs/cli/reference), [Parallel agents](https://www.onorca.dev/docs/recipes/parallel-agents) | 생성·에이전트·Shared Paths·setup |
| uv·Python | [Cache](https://docs.astral.sh/uv/concepts/cache/), [Sync](https://docs.astral.sh/uv/concepts/projects/sync/), [Layout](https://docs.astral.sh/uv/concepts/projects/layout/), [CLI](https://docs.astral.sh/uv/reference/cli/), [Python versions](https://docs.astral.sh/uv/concepts/python-versions/), [venv](https://docs.python.org/3.14/library/venv.html) | 캐시, 작업별 환경, 잠금, 경로 |
| Node | [nvm](https://github.com/nvm-sh/nvm/blob/master/README.md), [fnm](https://github.com/Schniz/fnm), [fnm configuration](https://github.com/Schniz/fnm/blob/master/docs/configuration.md) | 런타임과 쉘별 선택 |
| npm | [npm ci](https://docs.npmjs.com/cli/v11/commands/npm-ci/), [Cache](https://docs.npmjs.com/cli/v11/commands/npm-cache/), [Config](https://docs.npmjs.com/cli/v11/using-npm/config/), [Scripts](https://docs.npmjs.com/cli/v11/using-npm/scripts/) | 캐시와 node_modules 구분 |

## 병렬 워크트리의 경계

- **확인:** Git 연결 워크트리는 객체·대부분의 ref를 공유하면서 작업 파일, 인덱스, HEAD는 따로 둔다. 같은 로컬 브랜치의 중복 체크아웃은 기본적으로 거부한다. 커밋되지 않은 잠금 파일 수정은 다른 워크트리에 자동 전파되지 않는다. [Git](https://git-scm.com/docs/git-worktree)
- **확인:** Orca는 start-from ref에서 워크트리를 백그라운드로 만들며 각 작업에 브랜치·파일·에이전트 터미널을 둔다. 공식 병렬 예시는 같은 ref에서 세 에이전트를 시작한다. [Orca Worktrees](https://www.onorca.dev/docs/model/worktrees), [Parallel agents](https://www.onorca.dev/docs/recipes/parallel-agents)
- **확인:** 새 Orca 워크트리는 깨끗한 체크아웃이므로 Git 무시 경로의 .venv와 node_modules는 기본으로 없다. [Orca Worktrees](https://www.onorca.dev/docs/model/worktrees)
- **판단:** 3~5개 에이전트에서는 사용자별 다운로드 캐시·설치된 런타임을 재사용하고, 브랜치 잠금 파일·설치 결과를 분리한다. 시작 ref, HEAD, 잠금 파일을 같이 기록해야 브랜치 차이와 캐시 차이를 구별할 수 있다. [Git](https://git-scm.com/docs/git-worktree), [uv Cache](https://docs.astral.sh/uv/concepts/cache/), [npm Config](https://docs.npmjs.com/cli/v11/using-npm/config/)

## Orca 복사와 setup

- **확인:** Settings → Repository의 Worktree Shared Paths는 기본 체크아웃의 경로를 새 워크트리에 준비한다. macOS의 APFS clone-copy가 가능하면 복제하고, 아니면 심볼릭 링크로 연결한다. 같은 컴퓨터·디스크라고 clone을 보장할 수 없다. [Orca Worktrees](https://www.onorca.dev/docs/model/worktrees)
- **확인:** 추적된 orca.yaml의 worktree.sharedDirectories는 Git 무시 상태이며 기본 체크아웃에 존재하는 디렉터리를 공유 목록에 추가한다. 공식 문서에는 node_modules도 예시로 나온다. .worktreeinclude는 Git 무시 경로를 작업별로 복사한다. 글롭·부정 패턴은 지원하지 않고 이미 공유된 경로는 재복사하지 않는다. [Orca Worktrees](https://www.onorca.dev/docs/model/worktrees)
- **확인:** Settings → Repository → Hooks에 워크트리 생성 후 setup 명령을 둔다. CLI worktree create의 --setup run|skip|inherit는 실행·건너뛰기·저장소 정책 상속을 정한다. --agent와 --prompt로 에이전트를 시작할 수도 있다. [Orca Hooks](https://www.onorca.dev/docs/agents/hooks-memory), [Orca CLI](https://www.onorca.dev/docs/cli/reference)
- **미확인:** GUI setup hook의 정확한 셸, 시작 디렉터리, 실패 후 재시도 방식은 위 문서에서 명시적으로 확인되지 않는다. 실습에서 pwd, command -v, 종료 코드로 확인한다. [Orca Hooks](https://www.onorca.dev/docs/agents/hooks-memory)
- **판단:** .venv와 node_modules는 Shared Paths 또는 .worktreeinclude 대상에서 빼고 각 워크트리에서 잠금 파일 기반 setup을 수행한다. 심볼릭 링크면 두 브랜치가 설치 상태를 같이 바꿀 수 있고, APFS 복사도 Python 가상환경의 절대 경로를 고치지 않는다. [Orca Worktrees](https://www.onorca.dev/docs/model/worktrees), [Python venv](https://docs.python.org/3.14/library/venv.html)

## uv·Python 3.14

- **확인:** .python-version의 3.14는 uv의 버전 요청이며 uv는 현재 디렉터리에서 상위로 찾는다. uv python install 3.14는 같은 minor의 최신 패치를 설치한다. 자동 다운로드도 설정에 따라 가능하다. 패치 버전까지 재현되지는 않는다. [uv Python versions](https://docs.astral.sh/uv/concepts/python-versions/)
- **확인:** uv.lock은 pyproject.toml 옆에 생성되고 기본 프로젝트 환경은 .venv다. uv sync는 잠금 파일에 맞추며 기본적으로 불필요한 설치 패키지를 제거한다. --locked는 잠금 파일이 없거나 최신이 아니면 실패한다. uv run도 기본적으로 잠금·동기화를 확인한다. [uv Layout](https://docs.astral.sh/uv/concepts/projects/layout/), [uv Sync](https://docs.astral.sh/uv/concepts/projects/sync/), [uv CLI](https://docs.astral.sh/uv/reference/cli/)
- **확인:** uv cache dir로 사용자 캐시 위치를 확인한다. 기본 설치 링크 모드는 macOS·Linux의 Copy-on-Write clone, Windows의 hardlink다. 캐시와 .venv가 같은 파일시스템이 아니면 느린 복사 방식으로 물러날 수 있다. 물리 디스크가 같아도 볼륨이 다르면 확인이 필요하다. [uv Cache](https://docs.astral.sh/uv/concepts/cache/), [uv CLI](https://docs.astral.sh/uv/reference/cli/)
- **확인:** uv 캐시는 동시 읽기·쓰기에 안전하고 같은 환경 설치에는 파일 잠금을 건다. --offline은 네트워크를 차단하며 로컬 캐시·파일만 쓴다. 그래서 uv sync --locked --offline의 성공은 해당 실행에 필요한 데이터가 로컬에 있다는 근거이고, 새 브랜치의 uncached 의존성은 실패할 수 있다. [uv Cache](https://docs.astral.sh/uv/concepts/cache/), [uv CLI](https://docs.astral.sh/uv/reference/cli/)
- **확인:** Python venv의 설치 스크립트는 해당 환경의 절대 경로를 갖는다. 이동·복사 시 재생성이 원칙이다. uv의 editable 설치는 소스 디렉터리를 참조하고, 프로젝트·workspace 멤버도 editable일 수 있다. 따라서 다른 워크트리로 복사한 .venv가 이전 소스를 바라볼 위험이 있다. [Python venv](https://docs.python.org/3.14/library/venv.html), [uv Dependencies](https://docs.astral.sh/uv/concepts/projects/dependencies/), [uv Project config](https://docs.astral.sh/uv/concepts/projects/config/)
- **판단:** uv의 centralized-project-envs는 현재 preview이므로 기본 실습에서 사용하지 않는다. [uv Layout](https://docs.astral.sh/uv/concepts/projects/layout/)

## nvm·npm·fnm

- **확인:** nvm은 사용자별 설치·쉘별 실행의 Node 버전 관리자이고 sourced shell function이다. 비대화식 Orca 훅에서 nvm을 못 찾으면 그 쉘에서 nvm.sh 로드를 점검한다. nvm use는 현재 디렉터리에서 부모 방향으로 .nvmrc를 찾는다. .nvmrc의 24는 계열 선택으로 패치를 고정하지 않는다. [nvm README](https://github.com/nvm-sh/nvm/blob/master/README.md)
- **확인:** NVM_BIN은 현재 선택된 Node·npm과 그 버전의 전역 패키지 위치다. 같은 사용자·Node v24를 쓰는 여러 워크트리는 런타임을 재사용할 수 있지만 프로젝트의 node_modules는 별도다. 후자는 nvm의 런타임 범위와 npm의 설치 위치를 합친 판단이다. [nvm README](https://github.com/nvm-sh/nvm/blob/master/README.md), [npm Config](https://docs.npmjs.com/cli/v11/using-npm/config/)
- **확인:** npm ci는 기존 일치하는 package-lock.json을 요구하고 package.json과 불일치하면 실패한다. 기존 node_modules가 있으면 지우고 다시 설치하며 잠금 파일은 쓰지 않는다. 훅을 재실행할 때 네트워크 전송이 없어도 재설치 시간이 드는 이유다. [npm ci](https://docs.npmjs.com/cli/v11/commands/npm-ci/)
- **확인:** npm의 기본 cache는 POSIX에서 ~/.npm, Windows에서 %LocalAppData%\\npm-cache이며 npm config get cache로 현재 설정을 본다. npm ci --offline은 npm의 네트워크 요청을 막지만 --prefer-offline은 캐시 미스 시 네트워크를 쓴다. 설치 스크립트는 별도 명령을 실행하므로 그 내부의 네트워크 여부는 따로 검증해야 한다. [npm Config](https://docs.npmjs.com/cli/v11/using-npm/config/), [npm Scripts](https://docs.npmjs.com/cli/v11/using-npm/scripts/)
- **확인:** npm 캐시는 내용 주소 방식이고 읽기·쓰기 무결성을 검사한다. npm cache verify로 점검한다. 캐시 지우기는 통상적인 속도 개선책이 아니다. [npm Cache](https://docs.npmjs.com/cli/v11/commands/npm-cache/)
- **확인:** fnm은 .nvmrc와 .node-version을 이해한다. fnm env --use-on-cd는 디렉터리 이동 시 버전 전환을 돕는다. 그러나 부모 버전 파일 탐색은 기본 local이며 recursive는 명시해야 한다. nvm의 부모 탐색과 같다고 설명하지 않는다. 자동 cd hook이 비대화식 setup에서도 동작한다고 가정하지 않는다. [fnm README](https://github.com/Schniz/fnm), [fnm Configuration](https://github.com/Schniz/fnm/blob/master/docs/configuration.md), [nvm README](https://github.com/nvm-sh/nvm/blob/master/README.md)

## 실습용 진단과 주의

- 각 워크트리에서 pwd, git rev-parse --show-toplevel, git rev-parse HEAD, git status --short와 잠금 파일 diff를 먼저 확인한다. 시작 ref·브랜치·작업 디렉터리의 차이를 의존성 문제로 오인하지 않기 위해서다. [Git](https://git-scm.com/docs/git-worktree), [Orca Worktrees](https://www.onorca.dev/docs/model/worktrees)
- uv cache dir, npm config get cache, command -v nvm, node -v, test -L .venv, test -L node_modules로 공유 위치·쉘 초기화·링크 여부를 확인한다. [uv Cache](https://docs.astral.sh/uv/concepts/cache/), [npm Config](https://docs.npmjs.com/cli/v11/using-npm/config/), [nvm README](https://github.com/nvm-sh/nvm/blob/master/README.md), [Orca Worktrees](https://www.onorca.dev/docs/model/worktrees)
- 각 예제의 폴더에서 uv sync --locked --offline 또는 npm ci --offline을 실행한다. 첫 실행·재실행의 시간을 /usr/bin/time -p로 측정한다. 오프라인 성공은 해당 패키지 관리자 호출의 캐시 가용성 증거이며 머신 전체의 네트워크 차단 증거는 아니다. npm 설치 스크립트는 별도 프로세스다. [uv CLI](https://docs.astral.sh/uv/reference/cli/), [npm Config](https://docs.npmjs.com/cli/v11/using-npm/config/), [npm Scripts](https://docs.npmjs.com/cli/v11/using-npm/scripts/)
- 같은 잠금 파일의 3~5개 워크트리와 한 브랜치에서 의존성을 바꾼 워크트리를 모두 비교한다. 동일한 Python·Node 런타임인데도 설치 결과가 갈릴 수 있음을 보여 준다. 이는 공식 병렬 작업 흐름을 이용한 **실험 설계**다. [Orca Parallel agents](https://www.onorca.dev/docs/recipes/parallel-agents), [uv Sync](https://docs.astral.sh/uv/concepts/projects/sync/), [npm ci](https://docs.npmjs.com/cli/v11/commands/npm-ci/)
- 작업 종료 시 Orca의 diff와 미병합 브랜치를 확인한 다음 워크트리를 archive 또는 delete한다. Orca는 삭제할 때 디렉터리·브랜치를 제거하며, Git이 미병합 커밋 때문에 브랜치를 보존하면 별도 검토 목록을 보여 줄 수 있다. 단순히 폴더만 수동 삭제하면 Git 관리 정보가 남을 수 있다. [Orca Worktrees](https://www.onorca.dev/docs/model/worktrees), [Git](https://git-scm.com/docs/git-worktree)
- Linux에서는 uv 캐시와 환경의 파일시스템, nvm 쉘 초기화를 확인한다. Windows에서는 uv/npm 캐시 경로와 Python venv의 Scripts, nvm의 WSL 지원 또는 fnm의 네이티브 지원을 짧게 비교한다. [uv Cache](https://docs.astral.sh/uv/concepts/cache/), [npm Config](https://docs.npmjs.com/cli/v11/using-npm/config/), [Python venv](https://docs.python.org/3.14/library/venv.html), [nvm README](https://github.com/nvm-sh/nvm/blob/master/README.md), [fnm README](https://github.com/Schniz/fnm)

**집필 금지 단정:** “캐시 공유로 설치가 생략된다”, “Shared Paths는 항상 독립 사본이다”, “nvm과 fnm의 버전 파일 탐색은 같다”. 각각 동기화·재구성 비용, 링크 fallback, fnm의 local 기본값을 빠뜨린다. [uv Sync](https://docs.astral.sh/uv/concepts/projects/sync/), [npm ci](https://docs.npmjs.com/cli/v11/commands/npm-ci/), [Orca Worktrees](https://www.onorca.dev/docs/model/worktrees), [fnm Configuration](https://github.com/Schniz/fnm/blob/master/docs/configuration.md)

## 2026-09-27 보강: 패키지 밖의 로컬 파일

- **확인:** Orca `.worktreeinclude`는 기본 체크아웃에 있고 Git에서 무시된 리터럴 경로를 새 작업 폴더로 복사한다. 누락·추적된 경로는 복사하지 않으며 이미 Shared Paths로 준비한 경로는 재복사하지 않는다. [Orca Worktrees](https://www.onorca.dev/docs/model/worktrees)
- **확인:** Worktree Shared Paths는 macOS APFS 복제가 가능하면 복제하고 그렇지 않으면 심볼릭 링크로 연결할 수 있다. 따라서 작업별로 수정할 `.env`와 개인 스크립트의 독립성을 무조건 보장하는 수단으로 설명하지 않는다. [Orca Worktrees](https://www.onorca.dev/docs/model/worktrees)
- **확인:** `uv run --env-file`과 Node의 `node --env-file`은 환경 파일 값을 실행 프로세스에 전달한다. 파일을 복사하는 것과 로드하는 것은 별개다. [uv configuration files](https://docs.astral.sh/uv/configuration/files/#environment-variable-files), [Node CLI](https://nodejs.org/api/cli.html#--env-filefile)
- **판단:** 팀 공통 빌드·테스트 명령과 hook 진입 스크립트는 추적하고, 개인별 값만 Git 무시 파일로 둔다. `.env`의 실제 비밀값을 여러 워크트리에 복제할 때는 에이전트의 접근 범위와 사본 수를 고려한다. [Git ignore](https://git-scm.com/docs/gitignore), [Orca Worktrees](https://www.onorca.dev/docs/model/worktrees)
