# 6. 준비 시간 측정과 문제 해결

## 학습 목표

이 장을 마치면 새 워크트리의 느림을 **생성, 런타임 선택, 패키지 확보, 설치 결과 구성, 실행**으로 나누어 측정하고, 결과에 맞는 조치를 선택할 수 있다. 작업이 끝난 뒤 변경 사항을 보존하며 워크트리도 정리할 수 있다.

## 6.1 비교할 대상을 먼저 고정한다

새 워크트리의 전체 준비 시간에는 Git 체크아웃, Orca setup hook, `uv`·`npm` 실행이 모두 들어간다. 2장에서 Python 3.14와 Node v24를 한 번 준비한 뒤 **같은 커밋과 잠금 파일**에서 새 작업을 만들어야 캐시 재사용을 비교할 수 있다. Rich 15나 Chalk를 추가한 브랜치는 별도 집합으로 기록한다. 공식 문서상 uv는 사용자 캐시를 사용하고 npm도 사용자 캐시를 사용하지만, 둘 다 새 작업 폴더에 설치 결과를 만들어야 한다. [uv 캐시](https://docs.astral.sh/uv/concepts/cache/), [npm 캐시](https://docs.npmjs.com/cli/v11/commands/npm-cache/)

| 기록할 값 | Python에서 확인 | Node.js에서 확인 |
|---|---|---|
| 시작 상태 | `git rev-parse HEAD`, `git status --short` | 같은 명령 |
| 요청 런타임 | `cat .python-version` | `cat .nvmrc` |
| 실제 런타임 | `uv run --locked python --version` | `node --version` |
| 캐시 위치 | `uv cache dir` | `npm config get cache` |
| 설치 결과 | `pwd`와 `.venv/` | `pwd`와 `node_modules/` |
| 준비 시간 | `/usr/bin/time -p uv sync --locked` | `/usr/bin/time -p npm ci` |

각 작업의 `real`은 경과 시간이다. `user`와 `sys`는 CPU 사용 시간이라 여러 에이전트가 동시에 실행되면 `real`과 다르게 움직인다. 첫 작업과 따뜻한 캐시 작업을 각각 기록하고, 동시에 3~5개를 시작한 결과도 따로 기록한다. 워크트리 생성 시간과 패키지 명령 시간은 Orca의 진행 표시·hook 로그에서 구별한다. 실행까지 포함하려면 Python은 `uv run --locked python main.py`, Node는 `npm start`를 별도 시간으로 잰다.

캐시를 일부러 지워 차이를 만들 필요는 없다. `uv cache clean`이나 `npm cache clean`은 다른 프로젝트의 캐시도 바꿀 수 있고, 실제 일상 작업의 따뜻한 상태를 없앤다. 먼저 동일한 환경에서 새 워크트리를 하나 더 만들어 비교한다. npm 캐시가 의심되면 `npm cache verify`로 무결성을 점검할 수 있다. [uv 캐시](https://docs.astral.sh/uv/concepts/cache/), [npm 캐시](https://docs.npmjs.com/cli/v11/commands/npm-cache/)

## 6.2 다운로드와 로컬 구성을 구별한다

오프라인 명령은 캐시가 필요한 데이터를 갖고 있는지 확인하는 가장 간단한 실습이다. **새로 만든 워크트리에서** 실행해야 이미 설치된 결과를 재사용한 것과 구별할 수 있다. 아래 명령은 두 예제의 `main` 잠금 파일을 한 번 온라인으로 준비한 후 사용한다. [uv CLI](https://docs.astral.sh/uv/reference/cli/), [npm 설정](https://docs.npmjs.com/cli/v11/using-npm/config/)

```bash
# Python 워크트리 루트
/usr/bin/time -p uv sync --locked --offline
uv run --locked --offline python main.py
```

```bash
# Node.js 워크트리 루트: 같은 셸에서 nvm use 24를 먼저 실행
/usr/bin/time -p npm ci --offline
npm start
```

오프라인 성공은 해당 **패키지 관리자 호출**에 필요한 데이터가 로컬에 있었다는 근거다. 설치 시간이 0이라는 뜻은 아니다. 오프라인 실패가 항상 캐시 고장을 뜻하지도 않는다. 다른 브랜치가 아직 받지 않은 버전을 요구하거나 Python 런타임 자체가 없을 수 있다. npm 설치 스크립트가 자체적으로 네트워크에 접속하는 프로젝트에서는 npm의 `--offline`만으로 그 스크립트의 통신을 차단하지 못한다. [uv 오프라인 옵션](https://docs.astral.sh/uv/reference/cli/), [npm 스크립트](https://docs.npmjs.com/cli/v11/using-npm/scripts/)

**해석 예:** Python 작업 A가 첫 동기화에서 패키지를 받고, 같은 `uv.lock`의 B가 오프라인에서 성공했다면 B의 준비 시간은 주로 `.venv` 구성과 검증에 쓰인 것이다. Node 작업 B가 오프라인에서 성공해도 `npm ci`가 `node_modules`를 다시 만들므로 로컬 작업 시간이 남는다. 실제 비율은 패키지 수·파일시스템·동시 작업 수에 따라 측정한다. [uv 동기화](https://docs.astral.sh/uv/concepts/projects/sync/), [npm ci](https://docs.npmjs.com/cli/v11/commands/npm-ci/)

## 6.3 증상별로 한 단계씩 확인한다

| 증상 | 먼저 확인 | 조치 |
|---|---|---|
| Orca에서 `nvm: command not found` | hook 안의 `command -v nvm`, `echo "$NVM_DIR"` | hook 셸에서 `nvm.sh`를 명시적으로 불러온다. |
| `node --version`이 v24가 아님 | `.nvmrc`, `command -v node`, `nvm use 24` 출력 | 같은 셸에서 버전을 선택한다. v24가 없으면 측정 전에 한 번 설치한다. |
| `uv sync --locked`가 실패 | `git diff -- pyproject.toml uv.lock`, Python 요청 버전 | 선언과 잠금 파일을 맞춘 뒤 변경을 검토한다. 의도한 변경이면 해당 브랜치에서 잠금 파일을 갱신한다. |
| `npm ci`가 잠금 파일 불일치로 실패 | `git diff -- package.json package-lock.json` | 의도한 의존성 변경을 `npm install`로 잠금 파일에 반영하고 다시 `npm ci`를 실행한다. |
| 오프라인 설치만 실패 | 변경된 잠금 파일, 실제 캐시 위치 | 필요한 새 패키지를 온라인에서 한 번 받은 뒤 같은 워크트리에서 다시 확인한다. |
| 캐시가 따뜻한데 느림 | 명령별 `real`, 동시 작업 수, 캐시와 설치 경로의 파일시스템 | 다운로드가 아닌 파일 배치나 경쟁인지 구별한다. 필요하면 병렬 설치 수를 줄여 다시 잰다. |
| 다른 브랜치의 패키지가 보임 | `pwd`, Git 루트, `test -L .venv`, `test -L node_modules` | 작업 폴더나 설치 결과 공유를 해제하고 각 브랜치의 잠금 파일로 다시 설치한다. |

uv는 캐시와 설치 대상이 서로 다른 파일시스템에 있으면 빠른 링크 대신 복사로 물러날 수 있다. macOS에서 `df -P "$(uv cache dir)" .venv`로 두 경로의 볼륨을 확인한다. Node는 `npm config get cache`가 각 워크트리에서 같은지 확인한다. 같은 컴퓨터·물리 디스크라도 설정이나 볼륨이 다르면 가정한 캐시 경로가 아닐 수 있다. [uv 캐시](https://docs.astral.sh/uv/concepts/cache/#cache-directory), [npm 설정](https://docs.npmjs.com/cli/v11/using-npm/config/)

같은 `.venv`를 두 브랜치가 공유하면 `uv sync`의 정확한 동기화가 한 브랜치에만 필요한 패키지를 제거할 수 있다. `node_modules`를 공유하면 한 워크트리의 `npm ci`가 다른 작업의 설치 상태에 영향을 줄 수 있다. 이러한 증상에서 캐시 삭제부터 시도하면 원인을 가린다. 설치 결과가 각각의 작업 폴더에 있는지 먼저 확인한다. [uv 동기화](https://docs.astral.sh/uv/concepts/projects/sync/), [npm ci](https://docs.npmjs.com/cli/v11/commands/npm-ci/)

## 6.4 변경을 합친 뒤 다시 준비한다

에이전트가 만든 결과를 합칠 때는 **코드 diff와 잠금 파일 diff를 함께** 검토한다. Orca의 diff 보기에서 시작 ref와 비교하고, 선택한 변경을 병합하거나 필요한 커밋을 가져온다. 두 브랜치가 같은 선언·잠금 파일을 고쳤다면 Git 충돌 표시만 지우고 끝내지 않는다. 최종 선언에서 잠금 파일을 다시 생성·검증하고 실행 결과를 확인한다. [Orca Worktrees](https://www.onorca.dev/docs/model/worktrees), [uv 동기화](https://docs.astral.sh/uv/concepts/projects/sync/), [npm ci](https://docs.npmjs.com/cli/v11/commands/npm-ci/)

```bash
# Python: 변경을 받은 최종 브랜치 루트
uv lock
uv sync --locked
uv run --locked python main.py
git diff -- pyproject.toml uv.lock
```

```bash
# Node.js: 변경을 받은 최종 브랜치 루트, Node v24 선택 후
npm install --package-lock-only
npm ci
npm start
git diff -- package.json package-lock.json
```

두 명령 묶음은 **충돌을 해결해 최종 의존성 선언을 검토한 다음** 실행한다. `uv lock`과 `npm install --package-lock-only`는 잠금 파일을 바꿀 수 있으므로 diff가 기대한 의존성만 포함하는지 보고 기록한다. 변경을 합치지 않는 비교 실험에서는 각 브랜치의 독립 결과를 유지한다.

## 6.5 작업을 보존하며 정리한다

Orca가 만든 워크트리는 diff·커밋·미병합 브랜치를 확인한 뒤 Orca에서 Archive 또는 Delete를 선택한다. 삭제는 디렉터리와 브랜치에 영향을 주며, Git이 미병합 커밋 때문에 보존한 브랜치는 Orca가 검토 대상으로 보여 줄 수 있다. 검토 전에 일괄 삭제하지 않는다. [Orca Worktrees](https://www.onorca.dev/docs/model/worktrees)

3·4장의 **Git 명령으로 직접 만든** 워크트리는 각 예제의 기본 저장소에서 `git worktree list`와 `git status --short`로 상태를 확인한다. 변경을 보존하거나 버리기로 결정한 뒤 `git worktree remove <경로>`를 사용한다. Git이 수정된 작업 파일 때문에 거부하면 원인을 확인한다. 폴더만 파일 관리자에서 지우면 Git의 워크트리 관리 정보가 남을 수 있다. [Git worktree 문서](https://git-scm.com/docs/git-worktree)

## Linux·Windows에서 달라지는 점

Linux에서도 `uv cache dir`와 환경이 같은 파일시스템에 있는지 확인한다. uv의 링크 방식과 실제 파일시스템 지원에 따라 복사 비용이 달라진다. `nvm`이 비대화식 셸에서 로드되는지는 macOS와 똑같이 확인해야 한다. [uv 캐시](https://docs.astral.sh/uv/concepts/cache/), [nvm README](https://github.com/nvm-sh/nvm)

Windows에서는 Python 가상환경의 실행 파일이 `.venv/Scripts/`에 있고 npm 캐시의 기본 경로도 POSIX와 다르다. `nvm-sh/nvm`은 네이티브 Windows를 지원하지 않으므로 WSL에서 사용하거나, 네이티브 Windows에서 동작하는 버전 관리자를 별도로 선택해야 한다. `fnm`은 Windows를 지원하지만 셸 초기화·버전 파일 탐색 방식이 이 책의 `nvm` 명령과 같지는 않다. [Python venv](https://docs.python.org/3.14/library/venv.html), [npm 설정](https://docs.npmjs.com/cli/v11/using-npm/config/), [nvm README](https://github.com/nvm-sh/nvm), [fnm README](https://github.com/Schniz/fnm)

## 직접 해보기

같은 `main`에서 만든 Orca 작업 세 개의 setup 시간이 각각 다르다. 각 작업의 `HEAD`, 잠금 파일 diff, 캐시 위치, 오프라인 설치 결과, `real` 시간을 표로 기록한다. 세 시간이 다른 이유를 **다운로드, 로컬 설치, 동시 실행 경쟁, hook의 런타임 선택** 중 어디에서 찾을지 설명해 보자.

**확인:** 캐시 경로와 잠금 파일이 같아도 로컬 설치와 동시 작업 경쟁으로 시간이 달라질 수 있다. 잠금 파일이 다르면 새 패키지 확보 비용을 별도로 판단한다. 성공한 빌드나 캐시 경로 하나만으로 원인을 확정하지 않는다.

[책 목차로 돌아가기](./index.md)
