# 에이전트 작업 안내

llmBook은 한국어 기술 학습자료를 Markdown으로 작성하고 MkDocs Material로 게시하는 저장소다. 사용자 요청을 우선하고 작업에 필요한 문서만 읽는다.

## 시작과 탐색

1. `git status --short`로 기존 변경을 확인하고 보존한다.
2. 아래 표에서 작업에 맞는 지침을 읽는다.
3. 대상 책의 `index.md`, 수정할 본문과 관련 예제를 확인한다. 모든 책과 `_work/` 기록을 한꺼번에 읽지 않는다.

| 작업 | 필요한 문서 |
|---|---|
| 새 학습자료·장 추가·대규모 개정 | [.guide/PROCESS.md](.guide/PROCESS.md), [.guide/OUTPUTS.md](.guide/OUTPUTS.md), [.guide/MARKDOWN_STYLE.md](.guide/MARKDOWN_STYLE.md). 템플릿은 해당 단계에서만 읽는다. |
| 본문·오탈자·링크 수정 | 대상 본문과 MARKDOWN_STYLE. 경로 변경 시 OUTPUTS도 확인한다. |
| 예제 코드 수정 | 해당 예제의 README, 버전·실행 조건, 연결된 챕터 |
| 사이트·빌드·CI 수정 | [README.md](README.md), `mkdocs.yml`, `requirements.txt`, `.github/workflows/pages.yml` |
| 지침·템플릿 수정 | [.guide/README.md](.guide/README.md)와 수정 대상 문서 |

## 저장소 규칙

- 독자용 원본은 `docs/`, 내부 집필 기록은 책의 `_work/`, 공통 집필 지침은 `.guide/`에 둔다.
- `site/`는 빌드 결과이므로 직접 편집하지 않는다. `.venv/`, `.obsidian/`, `.git/`는 일반 콘텐츠 탐색에서 제외한다.
- 새 경로는 OUTPUTS를 따른다. 기존 `chapter.md` 하위 폴더 구조와 `examples/`는 관련 요청 없이 일괄 이동하거나 이름을 바꾸지 않는다.
- 전체 책 목록은 `docs/index.md`, 책 목차는 해당 책의 `index.md`에서 관리한다. `mkdocs.yml`에 수동 `nav` 목록을 추가하지 않는다.
- 내부 페이지 링크는 상대 `.md` 경로로 작성한다. 파일 이동 시 참조 링크도 수정한다.
- 본문은 한국어를 기본으로 한다. 기술 주장은 출처·버전·적용 조건으로 검증한다.
- 과거 `_work/`는 당시 기록이다. 현재 본문과 대조하고 오래된 원고로 최신 내용을 덮어쓰지 않는다.
- 작은 수정과 저장소 유지보수에는 집필 8단계 파일을 새로 만들지 않는다.

## 검증과 완료 보고

- 콘텐츠·경로·사이트 설정 변경: `python -m mkdocs build --strict`. 환경 준비는 README를 따른다.
- 예제 변경: 해당 README의 검증 방법을 적용한다. 실행할 수 없는 환경·하드웨어 조건은 명시한다.
- 루트·`.guide/` 문서만 변경: 참조 경로, 중복·충돌 규칙, `git diff --check`를 확인한다. 이 문서들은 MkDocs 게시 대상이 아니다.
- 변경 요점, 실제 검증 결과, 남은 제한을 보고한다. 빌드 성공을 예제 실행이나 화면 검수 성공으로 간주하지 않는다.
