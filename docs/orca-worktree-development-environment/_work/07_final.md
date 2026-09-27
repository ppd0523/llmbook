# 기준 원고 확정 기록

확정일: 2026-09-27.

## 기준 원고와 최종 산출물

형식은 MkDocs 챕터형 Markdown 책이다. 최종 산출물이 곧 기준 원고이며 별도의 본문 복사본은 만들지 않는다.

- `docs/orca-worktree-development-environment/index.md`
- `docs/orca-worktree-development-environment/01-worktree-and-cache-boundaries.md`
- `docs/orca-worktree-development-environment/02-prepare-projects.md`
- `docs/orca-worktree-development-environment/03-uv-across-worktrees.md`
- `docs/orca-worktree-development-environment/04-nvm-npm-across-worktrees.md`
- `docs/orca-worktree-development-environment/05-orca-parallel-worktrees.md`
- `docs/orca-worktree-development-environment/06-measure-and-troubleshoot.md`

실습 자산은 `assets/python-demo/`와 `assets/node-demo/`의 독립 프로젝트다. 두 프로젝트의 버전 요청·잠금 파일·setup 스크립트, `.env.example`·`.worktreeinclude`와 README를 포함한다.

## 확정 점검

- 6개 장이 작업 파일과 캐시의 경계 → 두 예제 → uv → nvm·npm → Orca 병렬 작업 → 측정·정리 순서로 연결된다.
- 후속 보강으로 Git 무시 로컬 파일을 별도 층에 넣고 5.6절에서 `.worktreeinclude` 복사와 환경 파일 로드를 설명한다.
- 각 장의 목표와 확인 문제는 해당 장의 명령 또는 경로 판단으로 풀 수 있다.
- 기술 검증은 `05_review.md`에, 설명 순서와 hook 보강은 `06_revision.md`에 기록했다.
- 최종 본문에 내부 TODO·미확인 표시가 없고, 장마다 하나의 최상위 제목을 둔다. 내부 링크는 상대 `.md` 경로다.
- 코드 블록에 언어 식별자가 있고, 기술 주장의 주요 근거는 Git·Orca·uv·Python·nvm·npm 공식 문서로 연결했다.

## 남은 제한

Orca GUI에서 직접 hook과 `.worktreeinclude` 복사를 실행한 결과는 없다. 공식 문서에서 확인하지 못한 hook 실행 셸·시작 경로는 책의 진단 명령으로 독자가 확인하도록 설명했다. Linux·Windows 실습과 실제 3~5개 Orca 에이전트의 동시 성능 측정도 수행하지 않았다.
