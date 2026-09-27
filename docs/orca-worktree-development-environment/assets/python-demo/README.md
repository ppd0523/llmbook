# Python 예제

이 예제는 책의 2장에서 독립 Git 저장소로 복사해 사용한다. 기준 환경은 Python 3.14 계열과 uv 프로젝트 모드다. `.python-version`은 패치 버전을 고정하지 않는다.

## 실행

프로젝트 루트에서 실행한다.

```bash
uv sync --locked
uv run --locked python main.py
```

새 워크트리의 Orca setup hook에서는 프로젝트 루트를 확인한 뒤 `sh ./setup-worktree.sh`를 실행한다. 스크립트는 같은 `uv sync --locked`를 수행한다.

기대 출력은 `Python worktree ready (rich 14.3.3)`이다. `uv.lock`과 `pyproject.toml`은 Git에 포함하고 `.venv/`는 포함하지 않는다.

패키지가 캐시에 들어온 뒤에는 다음 명령으로 네트워크 없이 준비되는지 확인할 수 있다.

```bash
uv sync --locked --offline
uv run --locked --offline python main.py
```

이 명령이 실패하면 사용 중인 Python 또는 잠금 파일의 배포 파일이 로컬에 있는지 확인한다. 새 의존성을 추가한 브랜치는 그 패키지를 한 번 받아야 오프라인 검증이 가능하다.
