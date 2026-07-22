# 4. JavaScript와 TypeScript

## 학습 목표

1. vtsls가 JavaScript와 TypeScript buffer에 연결되었는지 확인한다.
2. ESLint diagnostics와 Prettier formatting의 책임을 구분한다.
3. JavaScript와 TypeScript file을 js-debug-adapter로 debug한다.
4. Project-local executable과 Neovim `PATH` 문제를 진단한다.

## 4.1 구성 요소

| 기능 | 도구 | 제공하는 extra |
|---|---|---|
| code navigation, type diagnostics | vtsls | `lang.typescript` |
| lint diagnostics, code action | ESLint language server | `linting.eslint` |
| source formatting | Prettier와 conform.nvim | `formatting.prettier` |
| debugging | js-debug-adapter와 nvim-dap | `dap.core`, `lang.typescript` |

TypeScript extra라는 이름이지만 vtsls와 DAP 설정은 JavaScript, JavaScript React,
TypeScript, TypeScript React filetype을 함께 처리한다.

## 4.2 Runtime과 project 준비

Node.js와 npm이 현재 Linux shell에서 보이는지 확인한다.

```console
$ command -v node npm
/home/dev/.local/bin/node
/home/dev/.local/bin/npm
$ node --version
$ npm --version
```

WSL에서는 출력이 `node.exe`나 `/mnt/c/...`를 가리키지 않는지 확인한다. 이 장의 Mason
package와 project dependency는 WSL Linux 환경에 설치한다.

Smoke-test project를 만든다.

```console
$ mkdir lazyvim-ts-smoke
$ cd lazyvim-ts-smoke
$ npm init -y
$ npm install --save-dev typescript tsx prettier eslint
$ npx tsc --init
$ npm init @eslint/config@latest
```

마지막 명령은 project에 맞는 ESLint flat config를 대화형으로 만든다. JavaScript와
TypeScript 사용 여부, module format은 자신의 project와 맞게 선택한다. 생성된
`package.json`과 package manager lockfile, ESLint config를 Git에 commit한다.

Prettier 설정 `.prettierrc.json`도 만든다.

```json
{
  "semi": true,
  "singleQuote": true
}
```

이 설정 파일이 중요한 이유는 3장에서 `lazyvim_prettier_needs_config = true`를 선택했기
때문이다. 설정이 없는 repository에서 Prettier가 임의로 format하지 않는다.

## 4.3 TypeScript smoke-test file

`src/index.ts`를 만든다.

```typescript
function add(left: number, right: number): number {
  return left + right;
}

const answer = add(20, 22);
console.log({ answer });
```

TypeScript extra의 기본 current-file debug configuration은 `tsx`가 Neovim `PATH`에
있으면 이를 사용하고, 없으면 `ts-node`를 찾는다. `tsx`를 project dependency로 설치한
상태이므로 smoke test를 시작할 때만 `node_modules/.bin`을 앞에 둔다.

```console
$ PATH="$PWD/node_modules/.bin:$PATH" nvim .
```

이 변경은 해당 Neovim process에만 적용된다. 일상 project에서는 direnv 같은 환경
loader를 쓰거나 이 장 뒤의 `.vscode/launch.json`에 실행 경로를 기록한다.

## 4.4 LSP 연결 확인

`src/index.ts`를 열고 다음 순서로 확인한다.

```vim
:set filetype?
:LspInfo
```

Filetype은 `typescript`여야 하고 active client에 vtsls가 있어야 한다. 이어서 다음 동작을
시험한다.

1. `add` 호출 위에서 `gd`를 눌러 함수 정의로 이동한다.
2. `K`를 눌러 type 정보를 본다.
3. `<leader>cr`로 `answer`를 `result`로 rename한다.
4. `<C-o>`로 이전 위치로 돌아간다.

의도적으로 type error를 만든다.

```typescript
const answer: number = "forty-two";
```

Diagnostic이 표시되면 vtsls가 buffer와 project를 분석하고 있다. 확인 후 원래 code로
되돌린다.

## 4.5 ESLint 확인

`:LspInfo`에는 vtsls와 함께 ESLint client가 보일 수 있다. ESLint language server는
열린 workspace의 `eslint` library를 우선 사용한다. `npm install --save-dev eslint`와
project config가 필요한 이유다.

`<leader>ca`를 열어 ESLint fix가 제안되는지 확인한다. 이 가이드에서는
`lazyvim_eslint_auto_format = false`이므로 ESLint가 전체 문서 formatter로 등록되지는
않는다. 자동 fix가 필요하면 code action을 명시적으로 실행한다.

ESLint client가 붙지 않으면 다음 순서로 본다.

1. `:Mason`에서 `eslint-lsp`가 설치되었는가?
2. Project root에 ESLint config가 있는가?
3. `node_modules`에 workspace `eslint`가 있는가?
4. `:LspInfo`가 선택한 root directory가 project root인가?

## 4.6 Prettier formatting 확인

Source를 일부러 흐트러뜨린다.

```typescript
const values=[1,2,3]
console.log(values)
```

현재 buffer에서 다음을 실행한다.

```vim
:ConformInfo
```

Prettier가 `available`이고 current filetype에 선택되었는지 확인한다. `<leader>cf`를 눌러
수동 format한 뒤 저장한다. LazyVim의 autoformat이 켜져 있으면 이후 저장에서도 같은
결과가 유지된다.

Format이 되지 않으면 다음을 확인한다.

- `.prettierrc.json`처럼 Prettier가 인식하는 config가 있는가?
- `:ConformInfo`가 `prettier` executable을 찾는가?
- `<leader>uF`로 현재 buffer의 autoformat을 꺼 두지 않았는가?
- 다른 plugin spec이 `conform.nvim`의 `config`를 직접 override하지 않았는가?

LazyVim 공식 문서는 conform.nvim의 `plugin.config`를 직접 바꾸면 LazyVim formatting이
깨질 수 있다고 경고한다. 이 가이드처럼 `opts`를 병합한다.

## 4.7 TypeScript debugging

`const answer = ...` 줄에 cursor를 놓고 다음 key를 누른다.

1. `<leader>db`: breakpoint를 만든다.
2. `<leader>dc`: debug configuration을 선택하고 실행한다.
3. `Launch file`: 현재 TypeScript file을 실행한다.
4. 정지 후 `<leader>dO`, `<leader>di`, `<leader>do`로 step한다.
5. `<leader>de`: cursor 아래 expression을 평가한다.
6. `<leader>dt`: session을 종료한다.

TypeScript extra는 `pwa-node` adapter와 source map 설정을 제공한다. `tsx` 또는
`ts-node`가 PATH에서 발견되지 않으면 adapter가 시작되어도 TypeScript program을 실행할
runtime이 없어 실패한다.

Project가 고정된 debug command를 사용한다면 `.vscode/launch.json`을 commit할 수 있다.
DAP core는 이 파일을 읽는다.

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "pwa-node",
      "request": "launch",
      "name": "Debug current TypeScript file",
      "runtimeExecutable": "${workspaceFolder}/node_modules/.bin/tsx",
      "program": "${file}",
      "cwd": "${workspaceFolder}",
      "sourceMaps": true,
      "skipFiles": ["<node_internals>/**", "**/node_modules/**"]
    }
  ]
}
```

## 4.8 JavaScript debugging

JavaScript file은 Node.js가 직접 실행할 수 있으므로 TypeScript runtime 문제가 없다.
`src/index.js`를 열고 같은 `<leader>db`, `<leader>dc`, `Launch file` 순서를 사용한다.

Browser debugging도 TypeScript extra가 `chrome`과 `msedge` adapter type을 정의하지만,
browser process와 URL, source map 설정이 project마다 다르다. 이 가이드는 Node.js
launch와 attach까지만 다룬다.

## 4.9 흔한 오류

| 증상 | 가장 가능성 높은 계층 | 확인과 해결 |
|---|---|---|
| `gd`가 동작하지 않음 | LSP/root | filetype, `:LspInfo`, vtsls 설치, `tsconfig.json` 확인 |
| ESLint diagnostic이 없음 | project/LSP | ESLint config와 workspace `eslint`, ESLint client 확인 |
| Prettier가 unavailable | formatter/project | `:ConformInfo`, `.prettierrc`, executable 확인 |
| 저장할 때 code가 두 번 바뀜 | formatter ownership | ESLint auto-format이 꺼졌는지 확인 |
| `tsx` executable not found | runtime/PATH | project `node_modules/.bin`을 PATH에 두거나 launch config 사용 |
| Breakpoint가 회색으로 남음 | DAP adapter/config | `js-debug-adapter`, selected configuration, source map 확인 |
| WSL에서 package가 엉뚱한 위치에 설치됨 | platform/PATH | Linux `node`, `npm`, `nvim`인지 `command -v`로 확인 |

## 직접 해보기

1. Type error를 만들고 vtsls diagnostic과 ESLint diagnostic의 source 이름을 비교한다.
2. `<leader>uF`로 buffer autoformat을 끈 뒤 저장과 `<leader>cf`의 차이를 확인한다.
3. 임시 PATH 없이 Neovim을 열어 TypeScript debug 실패를 관찰하고 launch config로 복구한다.
4. `lazy-lock.json`과 package manager lockfile이 각각 무엇을 고정하는지 설명한다.

## 요약

- TypeScript extra는 JavaScript와 TypeScript 모두에 vtsls와 js-debug 설정을 제공한다.
- ESLint는 diagnostics와 code action, Prettier는 formatting을 담당한다.
- Prettier config가 있는 project에서만 formatter를 활성화하도록 제한했다.
- TypeScript current-file debug에는 PATH에서 찾을 수 있는 `tsx` 또는 `ts-node`가 필요하다.
- `:LspInfo`, `:ConformInfo`, DAP session은 서로 다른 계층을 검증한다.

## 추가 읽을거리

- [LazyVim TypeScript extra](https://www.lazyvim.org/extras/lang/typescript)
- [LazyVim Prettier extra](https://www.lazyvim.org/extras/formatting/prettier)
- [LazyVim ESLint extra](https://www.lazyvim.org/extras/linting/eslint)
- [LazyVim DAP core](https://www.lazyvim.org/extras/dap/core)

[← 3장](./03-configuration.md) · [목차](./index.md) · [5장: Python →](./05-python.md)
