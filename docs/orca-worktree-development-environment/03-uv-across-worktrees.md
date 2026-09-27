# 3. uv 환경과 캐시 재사용

## 학습 목표

이 장을 마치면 두 Python 워크트리에서 같은 패키지를 네트워크 없이 준비하고, 브랜치별 `uv.lock`이 달라져도 실행 환경이 섞이지 않는지 확인할 수 있다.

## 3.1 먼저 경로를 예측한다

2장에서 만든 Python 저장소의 `main` 브랜치에는 `pyproject.toml`과 `uv.lock`이 있다. 새 워크트리에는 두 파일이 체크아웃되지만 `.venv/`는 없다. uv 프로젝트는 기본적으로 **프로젝트 루트의 `.venv`**를 사용하며, 이미 받은 패키지와 빌드 결과는 **uv 캐시**에서 찾는다. [uv 프로젝트 구조](https://docs.astral.sh/uv/concepts/projects/layout/), [uv 캐시](https://docs.astral.sh/uv/concepts/cache/)

```text
python-demo/   ── .venv/  ──┐
python-a/      ── .venv/  ──┼── uv cache dir가 가리키는 사용자 캐시
python-b/      ── .venv/  ──┘
```

이 장은 Git 명령으로 실습 워크트리를 만든다. 5장에서 Orca가 같은 종류의 디렉터리를 생성하도록 연결한다. Git은 동일한 로컬 브랜치를 두 곳에 체크아웃하지 않으므로 작업별 브랜치 이름을 지정한다. [Git worktree 문서](https://git-scm.com/docs/git-worktree)

```bash
cd "$HOME/orca-worktree-lab/python-demo"
git worktree add -b lab/python-a ../python-a main
git worktree add -b lab/python-b ../python-b main
git worktree list
```

재실습할 때 이미 같은 경로나 브랜치가 있으면 `git worktree list`로 상태를 보고 새 이름을 고른다. 기존 작업을 덮어쓰지 않는다.

## 3.2 같은 잠금 파일로 두 환경을 만든다

첫 워크트리에서 동기화 시간과 캐시 위치를 확인한다.

```bash
cd "$HOME/orca-worktree-lab/python-a"
uv cache dir
/usr/bin/time -p uv sync --locked
uv run --locked python main.py
.venv/bin/python -c 'import sys; print(sys.prefix)'
```

두 번째 워크트리는 같은 `uv.lock`을 갖는다. 2장에서 원래 저장소를 실행했으므로 패키지 캐시가 준비되었을 가능성이 높다. `--offline`은 uv의 네트워크 접근을 막고 로컬 캐시와 파일만 사용한다. 성공하면 **이 동기화에 필요한 데이터가 로컬에 있었다**는 뜻이다. 새로운 배포 파일이나 Python이 아직 없다면 실패할 수 있다. [uv 오프라인 옵션](https://docs.astral.sh/uv/reference/cli/)

```bash
cd "$HOME/orca-worktree-lab/python-b"
uv cache dir
/usr/bin/time -p uv sync --locked --offline
uv run --locked --offline python main.py
.venv/bin/python -c 'import sys; print(sys.prefix)'
```

기대 출력은 두 곳 모두 `Python worktree ready (rich 14.3.3)`이다. `sys.prefix`는 서로 다른 워크트리의 `.venv`를 가리켜야 한다. 반면 같은 사용자와 설정이라면 `uv cache dir`는 같은 위치를 보여 준다. **캐시 공유는 설치 생략이 아니다.** 새 `.venv`를 만들고 파일을 배치하는 시간은 남는다. uv는 macOS에서 기본적으로 캐시 파일을 Copy-on-Write로 설치하고, 동시 uv 프로세스가 캐시를 읽고 쓸 수 있도록 설계되어 있다. [uv 캐시와 안전성](https://docs.astral.sh/uv/concepts/cache/), [uv 링크 모드](https://docs.astral.sh/uv/reference/settings/#link-mode)

## 3.3 한 브랜치의 의존성을 바꾼다

이제 `python-b`만 Rich 15.0.0을 요구하게 만든다. 이 명령은 `pyproject.toml`과 `uv.lock`을 갱신한다. 패키지가 캐시에 없으면 여기서 **새 다운로드**가 발생하는 것은 정상이다. 잠금 파일을 바꾼 작업의 비용과 같은 잠금 파일을 복원하는 비용을 혼동하지 않는다. [uv 의존성 관리](https://docs.astral.sh/uv/concepts/projects/dependencies/)

```bash
cd "$HOME/orca-worktree-lab/python-b"
uv add "rich==15.0.0"
uv run --locked python main.py
git diff -- pyproject.toml uv.lock
```

기대 출력은 `Python worktree ready (rich 15.0.0)`이다. `python-a`의 잠금 파일과 `.venv`는 그대로여야 한다.

```bash
cd "$HOME/orca-worktree-lab/python-a"
uv run --locked python main.py
git status --short
```

여기서는 여전히 `rich 14.3.3`이 나와야 한다. 이는 **서로 다른 작업 파일과 설치 결과**가 브랜치별 요구를 유지한다는 실행 확인이다. 캐시는 두 버전의 배포 파일을 보관할 수 있지만 어느 버전을 사용할지는 각 브랜치의 잠금 파일과 `.venv`가 정한다. [Git worktree 문서](https://git-scm.com/docs/git-worktree), [uv 동기화](https://docs.astral.sh/uv/concepts/projects/sync/)

## 3.4 `.venv` 공유가 위험한 이유

Orca Shared Paths에 `.venv`를 넣거나 모든 워크트리에 `UV_PROJECT_ENVIRONMENT`로 같은 절대 경로를 지정하면 설치 결과 하나를 여러 브랜치가 사용하게 될 수 있다. `uv sync`는 기본적으로 잠금 파일에 없는 패키지를 제거하는 **정확한 동기화**를 수행한다. `python-b`에서 버전을 바꾼 뒤 동기화하면 `python-a`가 기대하는 환경을 바꿔 버릴 수 있다. uv 문서도 여러 프로젝트가 하나의 절대 환경 경로를 쓰면 서로 덮어쓴다고 경고한다. [uv 동기화](https://docs.astral.sh/uv/concepts/projects/sync/), [프로젝트 환경 경로](https://docs.astral.sh/uv/concepts/projects/config/#project-environment-path)

복사도 일반적인 해법이 아니다. Python 가상환경의 설치 스크립트에는 환경의 **절대 경로**가 들어가며, Python 문서는 옮긴 환경을 재생성하라고 안내한다. 패키지형 uv 프로젝트의 editable 설치는 소스 위치를 참조할 수도 있다. 이 책의 Python 예제는 가상 프로젝트라 그 문제가 직접 나타나지 않지만, 실제 프로젝트에서 복사한 `.venv`가 원래 워크트리의 코드를 읽는지 확인해야 한다. [Python venv](https://docs.python.org/3.14/library/venv.html), [uv editable 의존성](https://docs.astral.sh/uv/concepts/projects/dependencies/#editable-dependencies)

uv의 `centralized-project-envs`는 환경의 저장 위치를 캐시로 옮기는 **미리 보기 기능**이다. 프로젝트별 환경을 한 저장 위치에서 관리하는 기능이며 여러 브랜치가 하나의 변경 가능한 환경을 안전하게 공유하게 만드는 기본 해법으로 사용하지 않는다. [uv 프로젝트 구조](https://docs.astral.sh/uv/concepts/projects/layout/#centralized-project-environments)

## 3.5 느릴 때 먼저 볼 세 가지

1. **캐시가 달라졌는가?** 두 워크트리에서 `uv cache dir`를 비교한다. `UV_CACHE_DIR` 또는 `--no-cache`가 다르면 같은 컴퓨터라도 재사용하지 못할 수 있다. [uv 캐시 경로](https://docs.astral.sh/uv/concepts/cache/#cache-directory)
2. **새 패키지가 필요한가?** `git diff -- pyproject.toml uv.lock`으로 브랜치 변경을 확인한다. `--locked`가 실패하면 잠금 파일이 현재 선언과 맞지 않는 상태일 수 있다. [uv 동기화](https://docs.astral.sh/uv/concepts/projects/sync/)
3. **캐시와 `.venv`가 같은 파일시스템인가?** macOS에서 `df -P "$(uv cache dir)" .venv`로 두 경로의 볼륨을 확인한다. 다르면 빠른 링크 대신 복사할 수 있다. [uv 캐시](https://docs.astral.sh/uv/concepts/cache/#cache-directory)

## 직접 해보기

`python-b`에서 잠금 파일을 바꾸기 전에 `uv sync --locked --offline`이 성공했는데, Rich 15.0.0을 추가한 직후에는 오프라인 동기화가 실패했다고 가정하자. 다른 워크트리의 캐시가 고장 났다고 판단할 수 있는가? 어떤 패키지가 아직 로컬에 없는지 오류를 읽어 보고, 한 번 받은 뒤 같은 명령을 다시 실행해 보자.

**확인:** 새 버전의 배포 파일이 없다면 실패는 정상이다. 기존 `python-a`의 14.3.3 환경이 실행되는지도 별도로 확인해야 브랜치별 격리가 검증된다.

[4장: nvm·npm과 작업별 node_modules →](./04-nvm-npm-across-worktrees.md)
