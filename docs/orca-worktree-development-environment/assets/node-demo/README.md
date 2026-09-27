# Node.js 예제

이 예제는 책의 2장에서 독립 Git 저장소로 복사해 사용한다. 기준 환경은 Node.js v24 계열, nvm, npm이다. `.nvmrc`는 패치 버전을 고정하지 않는다.

`.env.example`에는 비밀이 아닌 실습 변수만 있다. 2장에서 이를 `.env`로 복사하면 Git은 `.env`를 무시하고, 추적된 `.worktreeinclude`를 읽는 Orca는 새 워크트리에 작업별 사본을 준비한다. 일반 `git worktree add`는 이 복사를 수행하지 않는다.

## 실행

프로젝트 루트의 대화형 셸에서 실행한다.

```bash
nvm use 24
npm ci
npm start
```

새 워크트리의 Orca setup hook에서는 프로젝트 루트를 확인한 뒤 `sh ./setup-worktree.sh`를 실행한다. 스크립트가 비대화식 셸에 `nvm`을 불러와 Node v24를 선택하고 `npm ci`를 실행한다.

기대 출력은 `Node worktree ready`다. `package.json`, `package-lock.json`, `.nvmrc`는 Git에 포함하고 `node_modules/`는 포함하지 않는다.

패키지가 npm 캐시에 들어온 뒤에는 다음 명령으로 패키지 관리자 호출이 네트워크 없이 완료되는지 확인한다.

```bash
npm ci --offline
npm start
```

`npm ci`는 실행할 때마다 기존 `node_modules`를 지우고 다시 구성한다. 따라서 `--offline` 성공은 재다운로드가 없었다는 근거이지 설치 작업이 생략되었다는 뜻은 아니다. 설치 스크립트가 자체적으로 네트워크에 접속하는 일반 프로젝트라면 그 동작도 따로 확인한다.
