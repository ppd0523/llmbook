# 4. nvm·npm과 작업별 node_modules

## 학습 목표

이 장을 마치면 두 Node.js 워크트리에서 설치된 Node v24와 npm 캐시를 재사용하면서, `node_modules`는 각 브랜치의 잠금 파일에 맞춰 따로 구성할 수 있다. 비대화식 셸에서 `nvm`을 찾지 못하는 이유도 확인한다.

## 4.1 Node와 패키지의 위치를 나눈다

2장의 Node 저장소는 `.nvmrc`에 `24`, `package-lock.json`에 `picocolors` 1.1.1을 기록했다. `nvm`이 설치한 Node는 사용자 디렉터리에 있고, npm 다운로드 캐시도 사용자 설정에 따른다. 반면 `node_modules/`는 프로젝트 작업 폴더에 있다. 같은 컴퓨터에서 Node v24를 다시 다운로드할 이유는 없지만 새 워크트리의 패키지 배치는 여전히 필요하다. [nvm README](https://github.com/nvm-sh/nvm), [npm 설정](https://docs.npmjs.com/cli/v11/using-npm/config/)

```text
node-demo/  ── node_modules/ ──┐
node-a/     ── node_modules/ ──┼── npm config get cache가 가리키는 사용자 캐시
node-b/     ── node_modules/ ──┘
                  ↑
          세 셸에서 선택할 Node v24 런타임
```

`nvm`은 실행 파일 하나가 아니라 **현재 셸에 불러오는 함수**다. 따라서 터미널마다 `nvm use`로 버전을 선택하고, 셸 시작 파일을 읽지 않는 hook에서는 `nvm.sh`를 명시적으로 불러와야 한다. `.nvmrc`의 `24`는 v24의 패치 버전을 고정하지 않는다. [nvm README](https://github.com/nvm-sh/nvm)

## 4.2 같은 잠금 파일로 두 워크트리를 준비한다

3장과 마찬가지로 작업마다 브랜치를 만든다. 처음에는 두 워크트리의 `package-lock.json`이 같다. [Git worktree 문서](https://git-scm.com/docs/git-worktree)

```bash
cd "$HOME/orca-worktree-lab/node-demo"
git worktree add -b lab/node-a ../node-a main
git worktree add -b lab/node-b ../node-b main
git worktree list
```

첫 워크트리에서 Node와 npm 캐시 경로를 확인하고 시간을 잰다. `npm ci`는 잠금 파일에 맞는 설치를 수행한다. 기존 `node_modules`가 있으면 먼저 제거하므로 **다시 실행해도 설치 비용이 든다**. [npm ci](https://docs.npmjs.com/cli/v11/commands/npm-ci/)

```bash
cd "$HOME/orca-worktree-lab/node-a"
export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
. "$NVM_DIR/nvm.sh"
nvm use 24
node --version
npm config get cache
/usr/bin/time -p npm ci
npm start
```

두 번째 워크트리에서는 네트워크 접근을 막고 캐시만으로 설치할 수 있는지 본다. `npm ci --offline`이 성공하면 **이 npm 호출에 필요한 패키지 데이터가 로컬에 있었다**는 뜻이다. 첫 실행에 아직 받은 적 없는 패키지가 있으면 오프라인 명령은 실패한다. `--prefer-offline`은 캐시를 우선하지만 누락된 데이터를 받을 수 있으므로 같은 검증에 쓰지 않는다. [npm 설정](https://docs.npmjs.com/cli/v11/using-npm/config/)

```bash
cd "$HOME/orca-worktree-lab/node-b"
export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
. "$NVM_DIR/nvm.sh"
nvm use 24
npm config get cache
/usr/bin/time -p npm ci --offline
npm start
```

두 곳 모두 `Node worktree ready`가 출력되어야 한다. `npm config get cache`는 같은 위치, `node_modules`는 서로 다른 위치여야 한다. `npm ci --offline` 중 실행되는 패키지 설치 스크립트는 npm과 별도 프로세스다. 일반 프로젝트의 스크립트가 자체 네트워크 요청을 하면 npm의 `--offline`만으로 컴퓨터 전체의 오프라인 실행을 보장하지 않는다. 이 작은 예제에는 그런 설치 스크립트가 없다. [npm 스크립트](https://docs.npmjs.com/cli/v11/using-npm/scripts/)

## 4.3 한 브랜치만 의존성을 바꾼다

`node-b`에 `chalk`를 추가한다. 이 명령은 `package.json`과 `package-lock.json`을 함께 갱신한다. 새 패키지가 npm 캐시에 없다면 다운로드가 발생하는 것은 정상이다. 변경 후 `npm ci`로 잠금 파일을 재현한다. [npm ci](https://docs.npmjs.com/cli/v11/commands/npm-ci/)

```bash
cd "$HOME/orca-worktree-lab/node-b"
npm install --save-exact chalk@5.6.2
npm ci
node -e 'import("chalk").then(({default: chalk}) => console.log(chalk.green("chalk ready")))'
git diff -- package.json package-lock.json
```

`node-a`의 잠금 파일은 바뀌지 않아야 한다. 다음 명령의 마지막 줄이 모듈을 찾지 못해 **실패하는 것**이 이 실습의 기대 결과다. `node-a`에서 `chalk`가 로드된다면 두 워크트리의 `node_modules`가 실제로 공유되는지 확인한다. [Git worktree 문서](https://git-scm.com/docs/git-worktree)

```bash
cd "$HOME/orca-worktree-lab/node-a"
git status --short
npm start
node -e 'import("chalk")'
```

브랜치 간 패키지 차이를 확인할 때는 `package-lock.json`의 변경과 실제 `node_modules`를 **함께** 본다. 잠금 파일은 작업이 요구하는 패키지를 기록하지만, 파일을 수정했다고 기존 설치 결과가 자동 갱신되지는 않는다. 새 잠금 파일을 받은 워크트리에서는 `npm ci`를 다시 실행한다. [npm ci](https://docs.npmjs.com/cli/v11/commands/npm-ci/)

## 4.4 hook 셸과 전역 패키지

Orca의 setup hook이나 에이전트가 여는 비대화식 셸은 평소 터미널의 시작 파일을 읽지 않을 수 있다. 아래처럼 **hook에서 실행할 셸 안에서** `nvm.sh`를 불러오고, 버전·캐시 경로를 출력하면 문제를 분리할 수 있다. `command -v nvm`이 실패한 채 시스템 Node로 `npm ci`를 실행하면 같은 워크트리라도 다른 Node를 쓰게 된다. [nvm README](https://github.com/nvm-sh/nvm)

```bash
export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
. "$NVM_DIR/nvm.sh"
nvm use 24
command -v nvm
node --version
npm config get cache
npm ci
```

`npm install -g`로 설치한 명령은 선택된 Node 버전의 전역 설치 위치와 관련된다. 이 책은 같은 v24만 사용하므로 워크트리마다 전역 패키지를 따로 설치하지 않는다. 다른 Node 버전으로 전환하면 그 버전에서 전역 명령이 보이는지 별도로 확인해야 한다. 프로젝트 도구는 가능하면 `package.json`에 기록해 잠금 파일로 재현한다. [nvm README](https://github.com/nvm-sh/nvm)

`fnm`을 쓰는 팀도 `.nvmrc`를 읽을 수 있다. 다만 `fnm env --use-on-cd`의 자동 전환은 셸 초기화에 달리고, 버전 파일의 상위 디렉터리 탐색 기본값도 `nvm`과 다르다. Orca hook에서 자동 전환을 가정하지 말고 해당 셸에서 버전을 명시적으로 선택하고 `node --version`을 확인한다. 이 책의 실습 명령은 `nvm` 기준이다. [fnm README](https://github.com/Schniz/fnm), [fnm 설정](https://github.com/Schniz/fnm/blob/master/docs/configuration.md)

## 직접 해보기

`node-b`에서 `npm ci --offline`이 느리지만 성공했다. `node-a`에서는 `npm start`도 성공한다. 이 결과만으로 두 워크트리가 하나의 `node_modules`를 공유한다고 결론 내릴 수 있는가? `npm config get cache`, `pwd`, `test -L node_modules`와 `package-lock.json`을 확인해 설명해 보자.

**확인:** 오프라인 성공은 npm 캐시 재사용의 근거다. `npm ci`는 각 워크트리의 설치 결과를 다시 구성한다. 실제 디렉터리 공유 여부는 링크와 경로로 따로 확인해야 한다.

[5장: Orca 병렬 작업과 setup hook →](./05-orca-parallel-worktrees.md)
