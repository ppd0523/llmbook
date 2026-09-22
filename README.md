# llmBook

개발 환경, 로보틱스, 강화학습 등 한국어 기술 학습자료를 책 단위로 관리하는 MkDocs Material 저장소입니다.

- 읽기: [게시 사이트](https://ppd0523.github.io/llmbook/) · [전체 책 목록](docs/index.md)
- 에이전트 작업 시작: [AGENTS.md](AGENTS.md)
- 저장소 용어: [CONTEXT.md](CONTEXT.md) · 되돌리기 어려운 결정 기록: [adr/](adr/)
- 집필 절차와 템플릿: [.guide/README.md](.guide/README.md)

## 저장소 구조

| 경로 | 역할 |
|---|---|
| `docs/index.md` | 전체 책 목록 |
| `docs/<book-slug>/` | 책 한 권. 목차, 챕터, 책 자산과 예제. `docs/` 바로 아래에는 책 폴더만 둔다 |
| `docs/<book-slug>/_work/` | 내부 집필·검토 기록. 게시에서 제외 |
| `docs/.pages`, `docs/<book-slug>/.pages` | 탐색 메뉴의 책 순서와 표시 이름 |
| `.guide/` | 집필 규칙과 단계별 템플릿 |
| `overrides/` | 어느 책에도 속하지 않는 사이트 자원. 테마 override와 전역 스크립트 |
| `adr/` | 되돌리기 어려운 결정과 그 이유. 게시에서 제외 |
| `mkdocs.yml` | 테마, Markdown 확장, 탐색·제외 설정 |
| `requirements.txt` | 사이트 빌드 의존성. 전이 의존성까지 전체 고정. 갱신 방법은 파일 머리말 참고 |
| `.github/workflows/pages.yml` | GitHub Pages 빌드·배포 |
| `site/` | 생성된 사이트. Git 추적 제외 |

책 목록은 `docs/index.md`에서 관리합니다. 예제 실행 환경은 각 예제의 README와 연결된 챕터를 확인하세요.

## 로컬 미리보기와 검증

CI는 Python 3.14를 사용합니다. 명령은 저장소 루트에서 실행합니다. 기존 `.venv`가 다른 운영체제에서 생성되었다면 현재 환경용 가상환경을 별도로 준비하세요.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m mkdocs serve
```

Linux/macOS:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m mkdocs serve
```

가상환경을 활성화했거나 해당 Python 경로를 지정한 상태에서 빌드를 검증합니다.

```bash
python -m mkdocs build --strict
git diff --check
```

탐색 메뉴는 파일 구조로 생성됩니다. 새 책은 책의 `index.md`와 `docs/index.md`에 반영합니다. `_work/`는 빌드에서 제외되고 `assets/` 아래 Markdown은 탐색 메뉴에서 제외됩니다. 세부 설정은 `mkdocs.yml`에서 확인합니다.

## 배포

`main`에 push하거나 GitHub Actions에서 워크플로를 수동 실행하면 strict 빌드 후 GitHub Pages에 배포됩니다. 생성된 `site/`를 직접 수정하거나 커밋할 필요는 없습니다.
