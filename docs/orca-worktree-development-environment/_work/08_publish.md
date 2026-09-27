# 게시 산출물 검수

검수일: 2026-09-27.

## 최종 산출물

- 형식: MkDocs 챕터형 Markdown 책. PDF·ePub·슬라이드는 요청 범위 밖이다.
- 기준 원고: `docs/orca-worktree-development-environment/index.md`와 같은 폴더의 `01-`~`06-` 챕터 Markdown.
- 실습 자산: `assets/python-demo/`, `assets/node-demo/`.
- 내부 집필 기록: `_work/`에 분리되어 있으며 게시 산출물에서 제외된다.
- 전체 책 목록과 메뉴 순서는 `docs/index.md`, `docs/.pages`, 책 폴더의 `.pages`에 함께 반영했다.

## 수행한 검수

1. Python 3.14.3 가상환경에 `requirements.txt`를 설치하고 `python -m mkdocs build --strict`를 실행했다. 종료 코드 0, MkDocs 문서 빌드 성공.
2. 생성된 `site/orca-worktree-development-environment/`에서 진입점, 6개 장, 두 예제 README의 HTML을 확인했다. `site/index.html`에 책 링크가 있고 5장→6장 링크가 생성됐다.
3. 빌드 결과에 `_work/`가 없고 코드 블록의 하이라이트 마크업이 있음을 확인했다.
4. `git diff --check`를 실행했고 공백 오류가 없었다. 새 책 본문에도 줄 끝 공백과 내부 TODO·미해결 표시가 없음을 검색했다.
5. 후속 5.6절과 1·6장 연결을 추가한 뒤 Python 3.14.3에서 strict 빌드를 다시 실행했다. 처음 생성한 한글 섹션 앵커가 실제 HTML의 `#56-env`와 달라 이를 고쳤고, 재빌드에서 링크 메시지 없이 성공했다.
6. 두 예제의 `.env.example`·`.worktreeinclude`를 추가한 뒤 Python 3.14.3에서 strict 빌드를 다시 실행해 성공했다. 두 예제를 별도 Git 저장소로 복사해 `.env` 무시와 일반 Git 워크트리의 파일 부재를 확인했다.

## 제한

- 브라우저의 실제 모바일 화면과 표 너비를 눈으로 검수하지 않았다. 엄격 빌드와 HTML 생성은 확인했지만 화면 품질까지 입증하지 않는다.
- Orca GUI hook의 실제 실행은 수행하지 않았으며, 책의 경로 진단 절차와 공식 문서 근거로 설명했다.
- `.worktreeinclude`의 Orca GUI 복사는 직접 실행하지 않았다. 공식 문서의 복사 조건과 새 워크트리에서의 파일·링크 확인 절차를 제시했다.

결론: 요청한 MkDocs Markdown 책과 예제 자산을 생성했고 엄격 빌드가 통과했다. `site/`는 파생 결과이므로 직접 편집하지 않았다.
