# 5. Python

## 학습 목표

1. Pyright와 Ruff가 서로 다른 분석 책임을 맡는 이유를 설명한다.
2. Project `.venv`를 선택하고 LSP가 올바른 interpreter를 사용하는지 확인한다.
3. Ruff formatter와 debugpy adapter를 검증한다.
4. Adapter Python과 debug 대상 Python을 구분해 문제를 해결한다.

## 5.1 구성 요소

| 기능 | 도구 | 제공하는 extra |
|---|---|---|
| type 분석과 code navigation | Pyright | `lang.python` |
| lint diagnostics와 code action | Ruff server | `lang.python` |
| source formatting | Ruff formatter와 conform.nvim | `lang.python`과 사용자 override |
| virtual environment 선택 | venv-selector.nvim | `lang.python` |
| debugging | debugpy와 nvim-dap-python | `dap.core`, `lang.python` |

Pyright는 type inference, definition, reference, completion을 담당한다. Ruff는 lint,
import 정리, format을 담당한다. Python extra는 두 server가 동시에 hover를 제공하지
않도록 Ruff의 hover capability를 끄고 Pyright를 우선한다.

## 5.2 Python과 virtual environment 확인

현재 Linux shell의 Python을 확인한다.

```console
$ command -v python3
/usr/bin/python3
$ python3 --version
Python 3.x.y
```

Smoke-test project와 virtual environment를 만든다.

```console
$ mkdir lazyvim-python-smoke
$ cd lazyvim-python-smoke
$ python3 -m venv .venv
$ source .venv/bin/activate
$ python --version
$ nvim .
```

`python3 -m venv`가 실패하면 사용 중인 배포판에서 Python venv 지원 package가
설치되었는지 확인한다. 운영체제 package 설치 절차는 이 가이드의 범위 밖이다.

WSL에서는 Windows에서 만든 virtual environment를 재사용하지 않는다. Script의 shebang,
binary wheel, path가 플랫폼에 종속될 수 있으므로 WSL project 안에서 Linux `.venv`를
새로 만든다.

## 5.3 Project 설정

Project root에 `pyproject.toml`을 만든다. 이 예제는 Ruff policy만 담는다.

```toml
[tool.ruff]
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I"]
```

`main.py`를 만든다.

```python
def total(values: list[int]) -> int:
    return sum(values)


numbers = [10, 20, 12]
answer = total(numbers)
print(f"answer={answer}")
```

## 5.4 Interpreter 선택

활성화된 `.venv`에서 `nvim .`을 실행하면 project runtime을 일치시키기 쉽다. Neovim을
먼저 연 경우에는 Python file에서 다음 command를 실행한다.

```vim
:VenvSelect
```

또는 `<leader>cv`를 누르고 project의 `.venv`를 선택한다. 선택 결과가 cache되면 다음에
같은 project를 열 때 다시 사용할 수 있다.

Interpreter를 바꾼 직후 기존 LSP client가 이전 환경을 계속 사용하면 buffer를 다시
열거나 Neovim을 project root에서 재시작한다. 확인할 때는 다음 세 경로를 비교한다.

```vim
:lua print(vim.fn.getcwd())
:lua print(vim.env.VIRTUAL_ENV or "VIRTUAL_ENV is not set")
:LspInfo
```

## 5.5 LSP와 diagnostics 확인

`main.py`에서 `:LspInfo`를 실행한다. Pyright와 Ruff client가 현재 buffer에 attach되어
있어야 한다.

1. `total` 호출 위에서 `gd`로 definition에 이동한다.
2. `K`로 inferred type을 확인한다.
3. `<leader>cr`로 symbol을 rename한다.
4. 사용하지 않는 import를 추가해 Ruff diagnostic을 확인한다.
5. 다음 type error를 만들어 Pyright diagnostic을 확인한다.

```python
answer = total([10, "20", 12])
```

Diagnostic source가 다르면 어느 server가 어떤 문제를 보고했는지 구분할 수 있다. 확인
후 오류를 원래대로 되돌린다.

## 5.6 Ruff formatting 확인

Source의 spacing과 quote를 일부러 흐트러뜨린 뒤 다음 command를 실행한다.

```vim
:ConformInfo
```

Current buffer의 formatter 목록에 `ruff_format`이 있고 `available`인지 확인한다.
`<leader>cf`로 format한다. Autoformat이 켜져 있으면 저장할 때도 같은 formatter가
실행된다.

Ruff server는 lint fix와 import 정리를 code action으로도 제공한다. 사용하지 않는 import
위에서 `<leader>ca`를 열어 제안을 확인한다. Formatting과 lint fix는 다른 동작이므로
format만 실행했다고 모든 diagnostic이 사라져야 하는 것은 아니다.

## 5.7 Python debugging

3장의 설정은 Mason의 `debugpy` package와 Python extra의 nvim-dap-python을 연결한다.
`main.py`의 `answer = total(numbers)` 줄에서 다음 순서로 실행한다.

1. `<leader>db`로 breakpoint를 만든다.
2. `<leader>dc`를 누른다.
3. `Launch file` configuration을 선택한다.
4. 정지하면 `<leader>de`로 `numbers` 또는 `answer`를 평가한다.
5. `<leader>dO`로 다음 줄로 이동한다.
6. `<leader>dt`로 session을 종료한다.

Python debugging에는 두 Python 역할이 있다.

| 역할 | 대표 경로 | 실패할 때 증상 |
|---|---|---|
| debug adapter 실행 | Mason의 `debugpy-adapter` | adapter가 시작되지 않음 |
| project program 실행 | project의 `.venv/bin/python` | import error, 다른 dependency, 다른 Python version |

Mason은 debugpy가 독립적으로 실행될 환경을 제공한다. Debug 대상 program은 project
interpreter로 실행되어야 한다. `debugpy-adapter`가 보인다는 사실만으로 `.venv` 선택이
맞다는 뜻은 아니다.

Python extra는 test method와 class debugging keymap도 제공한다.

| key | 동작 |
|---|---|
| `<leader>dPt` | cursor가 있는 test method debug |
| `<leader>dPc` | cursor가 있는 test class debug |

실제 test runner와 dependency는 project가 관리한다. Test integration 자체는 이 가이드의
필수 범위가 아니다.

## 5.8 흔한 오류

| 증상 | 가장 가능성 높은 계층 | 확인과 해결 |
|---|---|---|
| Pyright가 import를 찾지 못함 | interpreter/project | `.venv` 활성화, `:VenvSelect`, root 확인 |
| Pyright가 두 개 attach됨 | plugin/config | 다른 Python LSP spec이 중복 활성화되지 않았는지 확인 |
| Ruff hover와 Pyright hover가 충돌 | option/old config | native Ruff server 사용과 Python extra override 확인 |
| `ruff_format` unavailable | Mason/formatter | `:Mason`, `vim.fn.exepath("ruff")`, `:ConformInfo` 확인 |
| Breakpoint 전에 adapter 종료 | Mason/DAP | `debugpy` 설치와 `debugpy-adapter` 경로 확인 |
| Debug 실행 중 `ModuleNotFoundError` | project interpreter | `.venv`에서 Neovim 재시작, selected interpreter 확인 |
| WSL에서 `.venv` script 실행 실패 | platform | Windows venv를 버리고 WSL에서 다시 생성 |

## 5.9 진단 순서 실습

`.venv`를 deactivate한 새 shell에서 project 밖의 directory를 current working directory로
둔 채 `nvim /path/to/project/main.py`를 실행해 본다. 정상 실행과 비교해 다음을 기록한다.

1. `vim.fn.getcwd()` 결과
2. `VIRTUAL_ENV` 유무
3. Pyright가 선택한 root
4. Debug program의 Python path

그 뒤 project root로 이동하고 `.venv`를 활성화한 다음 `nvim .`으로 다시 열어 차이를
확인한다. 이 실습은 “같은 file을 열었다”와 “같은 project environment에서 열었다”가
다름을 보여 준다.

## 요약

- Pyright는 type/navigation, Ruff는 lint/format을 담당한다.
- `.venv` 활성화 후 project root에서 Neovim을 여는 것이 가장 단순한 baseline이다.
- `:VenvSelect`는 이미 열린 editor에서 interpreter를 바꿀 때 사용한다.
- debugpy adapter Python과 project program Python은 서로 다른 역할이다.
- `:LspInfo`, `:ConformInfo`, DAP launch를 각각 통과해야 전체 환경이 정상이다.

## 추가 읽을거리

- [LazyVim Python extra](https://www.lazyvim.org/extras/lang/python)
- [Ruff editor integration](https://docs.astral.sh/ruff/editors/)
- [debugpy 공식 저장소](https://github.com/microsoft/debugpy)

[← 4장](./04-javascript-typescript.md) · [목차](./index.md) · [6장: Rust →](./06-rust.md)
