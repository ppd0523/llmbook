# 작성 범위 정의

작성일: 2026-09-26

## 중심 질문

Orca에서 여러 에이전트가 서로 다른 Git worktree를 병렬로 사용할 때, Python과 Node.js 개발환경을 빠르게 준비하면서 브랜치별 의존성 변경을 안전하게 검증하려면 어떻게 해야 하는가?

## 대상 독자와 선행지식

- 대상 독자: Git, Python, Node.js 프로젝트를 사용해 봤지만 Git worktree와 Orca 병렬 작업은 처음인 개발자.
- 선행지식: Git의 commit·branch, `uv`와 `nvm`의 기본 목적, `pyproject.toml`과 `package.json`의 역할, 터미널 명령 실행.
- 이 책에서 설명할 개념: Git worktree의 파일 경계, 사용자별 다운로드 캐시와 작업별 설치 결과의 차이, Git 무시 로컬 파일, 잠금 파일, Orca setup hook, 병렬 설치 충돌, 캐시 적중과 소요 시간 측정.
- 기존 NixOS-WSL 책과 Hermes Agent 책은 선택 읽기 자료이며 필수 선행 학습이 아니다.

## 학습 목표

독자는 이 책을 읽고 다음을 수행할 수 있다.

1. 두 예제 프로젝트에서 Python 3.14와 Node.js v24를 선택하고 잠금 파일을 만든다.
2. Orca가 만든 워크트리마다 `uv` 가상환경과 npm `node_modules`를 준비하는 setup hook을 구성한다.
3. 동일한 잠금 파일을 쓰는 병렬 워크트리와 의존성이 달라진 브랜치를 실행·검증한다.
4. 다운로드, 캐시 재사용, 환경 구성 시간을 분리해 측정하고 느려진 원인을 좁힌다.
5. 공유 디렉터리의 위험을 판단하고 작업 종료 후 워크트리를 정리한다.

## 포함·제외 범위

- 포함: macOS 실습, Linux·Windows에서 달라지는 경로와 동작의 짧은 설명, Orca 저장소 등록·워크트리 생성·에이전트 실행·setup hook·검증·정리, `uv` 프로젝트 방식(`pyproject.toml`·`uv.lock`), `nvm`·npm(`.nvmrc`·`package-lock.json`), fnm과 nvm의 핵심 차이, Orca Shared Paths의 `.venv`·`node_modules` 동작과 위험, Git 무시 스크립트·`.env`의 복사와 명시적 로드.
- 실습: 외부 서비스를 호출하지 않는 독립된 Python·Node 예제 두 개. 동일한 잠금 파일과 브랜치별 의존성 변경을 모두 다룬다. 캐시가 준비되면 오프라인으로 실행·검증할 수 있도록 한다.
- 제외: Orca·Git·uv·nvm·Node·Python 설치 절차, Rust 빌드, pnpm·Yarn 실습, 포트·데이터베이스·실제 비밀값 구성, 전체 운영체제 구축, PDF 등 추가 변환. `.env`의 파일 수명주기는 다루되 실제 인증값을 예제에 넣지 않는다.
- 버전: `.python-version`에는 `3.14`, `.nvmrc`에는 `24`를 기록해 같은 계열의 최신 패치를 허용한다. Node v24는 집필 시점의 LTS 계열이다. 패치 버전에 따른 재현성 한계를 설명한다.
- 중점: 새 워크트리의 준비 시간. 네트워크 다운로드, 로컬 캐시에서의 설치, 디스크 사용을 구분하되 특정 시간 단축을 보장하지 않는다.

## 최종 산출물

- 제목: Orca 워크트리 개발환경: uv와 nvm으로 의존성 관리
- 형식: MkDocs 챕터형 Markdown 책. 본문은 `docs/orca-worktree-development-environment/index.md`와 같은 폴더의 `NN-<chapter-slug>.md` 여섯 편.
- 예제: `docs/orca-worktree-development-environment/assets/python-demo/`와 `assets/node-demo/`.
- 내부 작업 산출물: `docs/orca-worktree-development-environment/_work/`.
- 사이트 목록: `docs/index.md`, `docs/.pages`, 책의 `.pages`를 함께 갱신한다.
- 검증: 예제 README의 실행 절차와 `python -m mkdocs build --strict`, `git diff --check`를 확인하고 미실행 조건을 구분해 보고한다.

## 구성 방향

1. 워크트리·런타임·패키지 캐시의 관계
2. Python 3.14와 Node.js v24 예제 프로젝트 준비
3. 워크트리별 uv 환경과 공용 캐시
4. nvm·npm 환경과 `node_modules` 재구성
5. Orca setup hook, 병렬 작업, 브랜치별 의존성 변경
6. 준비 시간·오프라인 검증·문제 해결·워크트리 정리

사용자와 grill-me 문답으로 이 범위를 확정했다. 마지막 요청에 따라 병렬 에이전트가 워크트리를 만들고 개발할 때 생기는 의존성 관련 문제를 깊이 다룬다.

2026-09-27 후속 질문에 따라 패키지 관리자 밖의 Git 무시 스크립트와 `.env` 처리 범위를 1·5·6장에 추가했다. 비밀값 자체의 설정은 여전히 예제 밖이다.
