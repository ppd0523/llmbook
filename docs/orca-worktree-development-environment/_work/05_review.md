# 기술 검증

검증일: 2026-09-27. 대상은 `index.md`, 1~6장, Python·Node 예제다.

## 주장과 출처

- Git의 공유 객체 저장소와 별도 작업 파일·HEAD·인덱스, 동일 로컬 브랜치 중복 체크아웃 제한은 [git-worktree](https://git-scm.com/docs/git-worktree)와 대조했다.
- Orca의 시작 ref, 외부 워크트리 표시, Shared Paths, `.worktreeinclude`, setup hook은 [Worktrees](https://www.onorca.dev/docs/model/worktrees)와 [Agent hooks](https://www.onorca.dev/docs/agents/hooks-memory)에서 확인했다. CLI의 `--setup`은 [CLI reference](https://www.onorca.dev/docs/cli/reference)와 로컬 CLI 1.4.214 상태를 확인했다.
- uv의 캐시·동기화·오프라인·가상환경 경로는 [uv cache](https://docs.astral.sh/uv/concepts/cache/), [sync](https://docs.astral.sh/uv/concepts/projects/sync/), [Python venv](https://docs.python.org/3.14/library/venv.html)에 근거했다.
- npm `ci`의 삭제 후 재설치, 잠금 파일 검사와 캐시 경로는 [npm ci](https://docs.npmjs.com/cli/v11/commands/npm-ci/)와 [npm config](https://docs.npmjs.com/cli/v11/using-npm/config/)를 확인했다. `nvm`의 셸 함수 동작은 [nvm README](https://github.com/nvm-sh/nvm)를 확인했다.
- Git 무시 파일 복사 조건은 [Orca Worktrees](https://www.onorca.dev/docs/model/worktrees), `.env` 로드 명령은 [uv 환경 파일](https://docs.astral.sh/uv/configuration/files/#environment-variable-files)과 [Node CLI](https://nodejs.org/api/cli.html#--env-filefile)에 대조했다.

## 실행 검증

예제 폴더를 `/private/tmp/llmbook-orca-verify.gBLMq7/`로 복사해 각각 Git 저장소로 초기화하고, `git worktree add`로 두 워크트리씩 만들었다.

| 실습 | 실제 결과 |
|---|---|
| Python 두 워크트리의 `uv sync --locked --offline` | 둘 다 성공. Python 3.14.3과 Rich 14.3.3을 사용하고 `.venv` 경로가 달랐다. |
| Python 한 브랜치의 `uv add 'rich==15.0.0'` | `pyproject.toml`·`uv.lock`만 변경. 변경 브랜치는 Rich 15.0.0, 다른 브랜치는 14.3.3으로 실행됐다. |
| Node 두 워크트리의 `npm ci --offline` | 둘 다 성공. Node v24.21.0·npm 11.19.0을 선택하고 `Node worktree ready`를 출력했다. |
| Node 한 브랜치의 Chalk 5.6.2 추가 | 변경 브랜치에서 Chalk 로드 성공. 다른 브랜치의 `import('chalk')`는 예상대로 `ERR_MODULE_NOT_FOUND`였다. |
| 두 `setup-worktree.sh`의 새 복사본 실행 | Python은 `.venv`를 만들고 Rich 14.3.3을 실행했다. Node는 nvm으로 v24를 선택하고 `npm ci`를 완료했다. |
| MkDocs | 현재 저장소에서 uv와 Python 3.14로 준비한 환경(MkDocs 1.6.1, Material 9.7.6)에서 `python -m mkdocs build --strict`가 성공한다. |
| `.env` 로드 명령 | 비밀이 아닌 `WORKTREE_LABEL=local`로 `uv run --env-file`과 Node v24 `--env-file`을 실행해 모두 정상 로드됨을 확인했다. |
| 두 예제의 로컬 파일 구성 | 새 복사본에서 `.env.example`을 `.env`로 복사하고 Git 초기 커밋을 만들었다. `.env`는 무시되고 `.env.example`·`.worktreeinclude`는 추적됐다. 일반 `git worktree add`로 만든 작업에는 `.env`가 없었다. |

## 검증에서 확인한 문제와 대응

- Node hook 스크립트는 `set -e`보다 `nvm.sh` 소싱을 먼저 한다. `set -e`를 먼저 켜면 nvm 기본 별칭이 없는 셸에서 조기 종료된다. 이 순서로 새 복사본에서 검증했다.
- hook은 자식 셸에서 Node를 선택하므로 이후 에이전트 터미널의 Node 버전을 바꾸지 않는다. 그래서 5장은 해당 터미널에서 `nvm use 24`를 확인하는 절차를 둔다.
- Orca의 hook 입력 필드가 여러 줄 셸 문장을 어떻게 처리하는지 공식 문서에서 확인되지 않는다. 그래서 hook은 추적된 짧은 setup 스크립트를 호출하는 한 줄 명령으로 둔다.

## 남은 검증 한계

- Orca GUI에서 임시 저장소를 등록하고 실제 setup hook을 실행하지는 않았다. 공식 문서가 보장하지 않는 hook의 정확한 셸·시작 디렉터리·실패 후 재시도 동작은 본문에서 단정하지 않고 독자가 생성 로그로 확인하도록 했다.
- 성능 수치는 이 컴퓨터의 작은 예제에만 해당하므로 보편적 절감률로 제시하지 않았다. 3~5개 실제 Orca 에이전트의 동시 설치 시간은 책의 측정 절차로 독자가 직접 확인해야 한다.
- Linux·Windows 명령은 공식 문서의 차이만 설명했고 해당 OS에서 예제를 실행하지 않았다.
- Orca `.worktreeinclude`의 실제 GUI 복사는 실행하지 않았다. 파일 존재·Git 무시 여부와 새 작업의 링크 상태를 확인하는 절차를 본문에 제시했다.
- 위 실행 표의 예제 명령은 현재 예제 파일로 다시 실행하지 않았다. 현재 `assets/python-demo/`의 `pyproject.toml`과 `uv.lock`이 일치함은 Windows에서 `uv lock --check --offline`으로만 확인했다.

## 결론

잠금 파일을 공유하는 새 워크트리의 오프라인 재구성과 브랜치별 설치 결과 격리는 실행으로 확인했다. Orca 전용 UI 동작은 공식 문서 근거와 현장 진단 절차로 제한해 설명한다.
