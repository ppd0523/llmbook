# Hermes로 Claude Code 대화형 세션 지시·관리하기

Hermes는 터미널에서 Claude Code를 실행하고, 작업 지시를 입력하고, 화면을 읽고, 후속
지시를 보내는 운영자 역할을 할 수 있다. 짧고 단순하며 범위가 닫힌 작업은 비대화형
`claude -p`로 실행할 수 있지만, 구현 → 검토 → 수정 → 테스트처럼 깊은 추론과 여러
도구 왕복이 필요한 작업은 `tmux` 안에서 Claude Code 대화형 세션을 유지하는 편이
안전하다.

이 장은 2026-08-30의 Hermes 번들 `claude-code` 스킬과 Claude Code 공식 문서를 기준으로
한다. 두 도구는 빠르게 바뀌므로 실제 환경의 `/help`, `claude --help`, `claude --version`을
최종 기준으로 삼는다.

## 이 장을 마치면 할 수 있는 일

- 일회성 `claude -p`와 `tmux` 기반 대화형 세션 중 알맞은 방식을 고른다.
- Hermes 세션, `tmux` 세션, Claude Code 세션의 상태를 구분한다.
- Claude Code 화면을 먼저 확인한 뒤 작업 지시, 후속 지시, 중단 신호를 안전하게 보낸다.
- 권한 확인을 임의로 통과시키지 않고 사용자 승인 지점을 유지한다.
- 프로세스가 끝나거나 연결이 끊겨도 이름 있는 Claude Code 세션을 찾아 재개한다.

## 일회성 실행과 대화형 실행을 먼저 구분한다

Hermes의 번들 `claude-code` 스킬은 두 가지 실행 방식을 구분한다.

| 실행 방식 | 상태 | 적합한 작업 | 운영상 주의점 |
|---|---|---|---|
| `claude -p "요청"` | 응답 뒤 프로세스 종료 | 짧은 조회·분류·형식 변환 같은 단순 작업 | `--max-turns`에 걸리면 미완료 상태로 오류 종료할 수 있다 |
| `tmux` 안의 `claude` | 여러 차례 입력 가능한 세션 유지 | 탐색적 구현, 중간 결정, 반복 검토 | 화면 상태와 권한 대화상자를 읽은 뒤 키를 보내야 한다 |

`tmux`는 터미널 프로그램을 이름 있는 세션 안에서 계속 실행하게 해 주는 터미널
멀티플렉서(terminal multiplexer)다. Hermes가 한 번의 터미널 호출을 마쳐도 `tmux`
안의 Claude Code는 계속 실행되며, Hermes는 나중에 다시 화면을 읽거나 키를 보낼 수
있다. pane은 `tmux` 세션 안의 개별 터미널 화면이며, 이 장의 기본 구성은 pane 하나에
Claude Code 하나를 실행한다.

`--max-turns`는 print mode의 도구 사용 왕복 횟수를 제한한다. 도구 사용 왕복(tool-use
turn)은 Claude Code가 도구를 호출하고 결과를 받은 뒤 다음 판단으로 넘어가는 한
차례다. 한도에 도달하면 정상 완료 결과 대신 오류로 끝난다. thinking 자체를 별도
turn으로 세는 것은 아니지만, 깊은 thinking이 필요한 디버깅·리팩터링은 보통 파일 탐색,
수정, 테스트, 재수정의 여러 tool-use turn으로 이어진다. 따라서 낮은 `--max-turns`에서는
최종 답변이나 검증 전에 멈출 수 있고, 한도를 크게 올리면 일회성 실행의 비용과 통제
범위가 커진다.

이 가이드에서는 `claude -p`를 다음 조건을 모두 만족하는 짧고 간단한 작업에만 사용한다.

- 한두 단계로 끝나며 후속 질문 없이 완료 조건을 한 번에 설명할 수 있다.
- 읽을 파일과 실행할 명령 수가 작고 예상 가능하다.
- CI처럼 사람이 대화상자에 답할 수 없는 환경이다.
- 구조화된 JSON 결과나 명확한 종료 코드가 필요하다.
- `error_max_turns`와 비정상 종료를 성공으로 처리하지 않는 호출 측 검사가 있다.

다음 조건이면 대화형 세션이 유리하다.

- Claude Code의 조사 결과를 본 뒤 다음 구현 방향을 정해야 한다.
- 원인 탐색, 다중 파일 수정, 테스트 실패 재진단처럼 tool-use turn 수를 미리 알기 어렵다.
- `/compact`, `/review`, `/model` 같은 대화형 명령을 써야 한다.
- 권한 요청이나 선택지를 사람이 검토해야 한다.
- 같은 저장소에서 여러 차례 수정·테스트·재검토를 이어 가야 한다.

## 시작 전에 읽기 전용으로 확인한다

Claude Code와 `tmux`가 같은 terminal backend에 설치되어 있고, Claude Code 인증이 그
환경에서 보여야 한다. Hermes에게 다음처럼 사전 점검만 요청한다.

```text
/claude-code
아직 작업을 시작하지 말고 다음 항목만 읽기 전용으로 확인해 줘.
- 작업 디렉터리: /absolute/path/to/project
- claude --version
- claude auth status --text
- tmux -V
- git status --short
누락된 도구, 인증 문제, 기존 변경사항을 요약하고 기다려.
```

`/claude-code`는 설치된 스킬을 현재 요청에 불러오는 Hermes 명령이다. 기본 설치에 스킬이
없다면 먼저 Hermes의 스킬 목록과 설치 버전을 확인한다. 번들 스킬을 지웠던 경우에는
서버 터미널에서 `hermes skills reset claude-code --restore`로 복구할 수 있다.

Claude Code를 처음 실행하면 로그인이나 작업 공간 신뢰 확인이 나타날 수 있다. Hermes가
화면을 읽을 수 있다는 사실이 자동 승인 권한을 뜻하지는 않는다. 선택지가 나오면 내용을
요약하고 사용자에게 판단을 요청하게 한다.

## 세 겹의 상태를 구분한다

Hermes가 Claude Code를 운영할 때는 세 종류의 세션이 겹친다.

```text
사용자
  │
  ▼
Hermes 세션
  │  terminal로 tmux 명령 실행
  ▼
tmux 세션과 pane
  │  Claude Code 화면·키 입력 유지
  ▼
Claude Code 세션
  │  대화 history·checkpoint·작업 상태
  ▼
repository 또는 task 전용 Git worktree
```

| 상태 단위 | 식별 방법 | 사라지면 생기는 일 |
|---|---|---|
| Hermes 세션 | Discord thread나 Hermes session ID | 현재 운영 대화와 지시 맥락을 잃을 수 있다 |
| `tmux` 세션 | `claude-auth-refactor` 같은 이름 | 실행 중인 Claude Code 화면과 프로세스 연결이 끊긴다 |
| Claude Code 세션 | session ID 또는 `--name`으로 지정한 이름 | Claude Code 대화 history를 바로 재개할 수 없다 |
| 작업 공간 | 절대 경로, branch, worktree | 다른 저장소를 수정하거나 기존 변경과 충돌할 수 있다 |

세 이름을 하나의 단어로 뭉뚱그려 “그 세션”이라고 하지 않는다. 작업을 시작할 때 Hermes가
다음 네 값을 보고하게 하면 복구가 쉬워진다.

```text
Hermes 대화 위치:
tmux 세션 이름:
Claude Code 세션 이름:
작업 디렉터리와 Git branch:
```

## 시작 지시를 완결된 운영 계약으로 쓴다

다음 템플릿은 Discord, Hermes CLI, 대시보드에서 그대로 응용할 수 있다.

```text
/claude-code
작업 디렉터리: /srv/acme-api
실행 방식: tmux 안의 Claude Code 대화형 세션
tmux 세션 이름: claude-auth-refactor
Claude Code 세션 이름: auth-refactor

목표: login API의 간헐적인 500 오류를 재현하고 최소 수정한다.
범위: src/auth와 관련 테스트만 수정한다.
금지: migration, dependency major update, push, deploy, secret 접근.
완료 조건: 재현 원인, 변경 diff, regression test 결과, 남은 위험을 보고한다.

운영 규칙:
1. 같은 이름의 tmux 세션이 있는지 먼저 확인하고 중복 실행하지 않는다.
2. Claude Code를 시작한 뒤 화면을 캡처해 입력 가능한 상태인지 확인한다.
3. 신뢰·권한·로그인·선택 대화상자가 나오면 키를 보내지 말고 내용을 요약해 묻는다.
4. 일반 입력창일 때만 초기 지시를 보낸다.
5. 작업 중에는 상태 전환이나 입력 대기 때 화면을 확인하고, 같은 지시를 반복하지 않는다.
6. 완료 주장을 그대로 믿지 말고 Hermes가 git diff와 테스트 결과를 별도로 확인한다.
7. Claude Code 종료, tmux 종료, commit, push는 내 승인 없이 하지 않는다.
```

작업 디렉터리, 세션 이름, 범위, 금지사항, 완료 증거가 빠지면 Hermes가 올바른 프로세스를
찾더라도 잘못된 저장소에서 잘못된 일을 할 수 있다. 여러 대화형 작업을 병렬 실행한다면
작업마다 다른 `tmux` 이름과 Git worktree를 사용한다.

## Hermes가 내부적으로 하는 동작을 이해한다

Hermes 번들 스킬의 기본 흐름은 `tmux` 세션 생성, Claude Code 시작, 화면 캡처, 키 입력의
반복이다. 다음 명령은 동작을 이해하기 위한 예시이며, 사용자가 직접 실행하기보다 Hermes가
상태를 확인하며 실행하게 하는 편이 안전하다.

```console
tmux new-session -d -s claude-auth-refactor -c /srv/acme-api -x 140 -y 40
tmux send-keys -t claude-auth-refactor -l 'claude --name auth-refactor'
tmux send-keys -t claude-auth-refactor Enter
tmux capture-pane -t claude-auth-refactor -p -S -80
```

`send-keys -l`은 문자열을 단축키가 아닌 글자 그대로 입력하고, 별도의 `Enter`가 제출을
확정한다. 긴 여러 줄 지시나 따옴표·명령 치환 문자가 포함된 입력은 shell command에 바로
이어 붙이지 않는다. Hermes가 임시 파일과 `tmux` buffer를 사용해 원문을 전달하도록
요청하면 의도하지 않은 shell 해석을 줄일 수 있다.

화면 확인은 최근 출력만 충분히 넓게 가져온다.

```console
tmux capture-pane -t claude-auth-refactor -p -S -120
```

전체 화면을 매초 반복 캡처하면 비용과 맥락만 늘어난다. 시작 완료, 도구 실행 종료,
권한 요청, 일반 입력창 복귀처럼 판단이 바뀌는 시점에 확인한다.

## 화면을 읽고 다음 행동을 고른다

| 화면 상태 | 의미 | Hermes가 할 일 |
|---|---|---|
| 일반 입력창 | 새 지시를 받을 수 있음 | 한 번만 입력하고 제출한 내용 보고 |
| 응답 생성·도구 실행 중 | 현재 Claude Code turn 진행 중 | 출력만 확인하고 기다리거나 명시된 후속 지시만 queue |
| permission·trust 대화상자 | 사람의 권한 판단 필요 | command, path, 선택지, 위험을 요약하고 질문 |
| 질문·선택지 대기 | 작업에 필요한 결정이 부족함 | 임의 선택하지 말고 사용자 의사 확인 |
| 입력창 복귀와 완료 요약 | 한 turn 종료 | diff·test·산출물을 독립 검증 |
| shell prompt | Claude Code 프로세스 종료 | 재개할지 종료할지 확인 |
| `tmux` 세션 없음 | 프로세스도 끝났거나 세션 제거됨 | 중복 생성하지 말고 Claude Code 저장 세션부터 조회 |

출력에 “완료”라는 단어가 보인다고 바로 끝내지 않는다. 입력창이 돌아왔는지, 요청한 test가
실제로 실행됐는지, Git diff가 범위 안에 있는지 함께 확인한다.

## 상태 확인과 후속 지시를 분리한다

상태만 보고 싶을 때는 Claude Code에 새 입력을 보내지 않도록 명확히 말한다.

```text
tmux 세션 claude-auth-refactor의 최근 화면만 확인해 줘.
현재 단계, 마지막으로 완료한 행동, 실행 중인 도구, 입력·승인 대기 여부를 요약해.
Claude Code에는 어떤 키나 문장도 보내지 마.
```

후속 지시는 먼저 화면을 확인한 뒤 보낸다.

```text
먼저 claude-auth-refactor 화면을 확인해.
일반 입력창이거나 현재 작업에 후속 지시를 queue할 수 있는 상태라면 다음 문장을 한 번만
보내고, 실제로 보낸 문장을 그대로 보고해.

"public API signature는 유지하고, 새 dependency는 추가하지 마. 현재 수정 뒤 관련
regression test까지 실행해."

권한 대화상자나 사용자 선택지가 열려 있으면 아무 키도 보내지 말고 멈춰.
```

Claude Code는 작업 중 들어온 일반 메시지를 현재 도구 호출 뒤 또는 다음 turn에 전달할
queue로 보관할 수 있다. 그러나 대화상자가 열린 상태에서 문장을 보내면 선택 키로 잘못
해석될 수 있으므로 화면 확인이 먼저다.

Hermes 자체가 아직 응답 중이라면 2장에서 설명한 제어 명령을 사용한다.

- `/steer <지시>`: 현재 Hermes 운영 방향을 바로 보정한다.
- `/queue <지시>`: 현재 Hermes turn이 끝난 뒤 상태 확인이나 다음 행동을 요청한다.
- Claude Code 내부 queue: Hermes가 `tmux`를 통해 Claude Code에 보낸 후속 입력이다.

세 queue는 같은 것이 아니다. 어느 층의 실행을 바꾸려는지 문장에 이름을 쓴다.

## 승인 절차를 두 겹으로 유지한다

Hermes가 Claude Code를 실행하면 다음 두 승인 경계가 동시에 존재한다.

1. **Hermes 승인**: Hermes의 terminal command가 host나 sandbox에서 실행되어도 되는가?
2. **Claude Code 승인**: Claude Code가 요청한 Bash, file edit, web access를 허용해도 되는가?

Hermes의 승인을 통과했다고 Claude Code의 선택지를 자동 승인하지 않는다. 특히 다음
경우에는 사용자에게 다시 묻는다.

- 저장소 밖 path 접근
- 삭제, force push, 배포, production 변경
- secret이나 private document 접근
- “이번만 허용”이 아닌 영구 permission rule 저장
- 처음 합의한 범위를 벗어난 파일 수정이나 명령

Claude Code의 `bypassPermissions` 또는 `--dangerously-skip-permissions`는 권한 확인을
건너뛴다. 격리된 disposable container나 VM이고 사용자가 그 실행을 명시적으로 승인한
경우가 아니라면 쓰지 않는다. 처음 조사하는 작업은 `--permission-mode plan`으로 시작하고,
구현 승인을 받은 뒤 쓰기 가능한 mode로 새 세션을 시작하는 방법도 있다.

## Worked Example: 읽기 전용 분석 세션

먼저 파일을 바꾸지 않는 연습으로 세 상태를 확인한다.

```text
/claude-code
작업 디렉터리: /absolute/path/to/repository
실행 방식: tmux 대화형 세션
tmux 세션 이름: claude-readonly-tour
Claude Code 세션 이름: readonly-tour

목표: 이 저장소의 진입점, 테스트 명령, 가장 위험한 변경 영역을 분석해 표로 정리한다.
허용: 파일 읽기, read-only Git 명령.
금지: 파일 수정, package 설치, network access, commit, push.
완료 조건: 근거 파일 path와 확인한 command를 함께 제시한다.

시작 전에 기존 tmux 세션과 git status를 확인해. Claude Code는 plan permission mode로
시작해. 권한 요청이 나오면 승인하지 말고 보고해. 완료 뒤 Hermes가 git status를 다시
확인해 변경이 없음을 검증해.
```

진행 중 다음 세 요청을 순서대로 연습한다.

1. **관찰**: “화면만 확인하고 입력은 보내지 마.”
2. **보정**: “분석 범위를 `src/`와 `tests/`로 제한한다는 후속 지시를 한 번만 보내.”
3. **종료**: “일반 입력창인지 확인한 뒤 `/exit`을 보내고 shell prompt를 확인해.”

성공했다면 Hermes의 최종 보고에는 `tmux`와 Claude Code 세션 이름, 분석 결과, 변경 없는
`git status`, 종료 여부가 포함되어야 한다.

## 중단과 종료를 구분한다

중단은 현재 동작만 멈추고 세션을 남기는 것이고, 종료는 Claude Code 프로세스를 끝내는
것이다.

```text
claude-auth-refactor 화면을 먼저 확인해.
- 실행 중이면 현재 작업을 중단해야 하는 이유를 보고하고 내 확인을 기다려.
- 일반 입력창이면 /exit을 보내 Claude Code만 정상 종료해.
- tmux session을 kill하지 말고 shell prompt가 돌아왔는지 확인해.
```

긴급 중단을 승인했다면 Hermes는 `Ctrl+C`를 한 번 보내고 화면 변화를 확인할 수 있다.
같은 키를 반복하면 입력을 지우거나 Claude Code 자체를 종료할 수 있다. `tmux kill-session`은
Claude Code뿐 아니라 그 세션 안의 프로세스를 모두 끊으므로 정상 종료가 실패했고 사용자가
명시적으로 승인한 마지막 수단으로 둔다.

## 종료된 작업을 복구한다

먼저 실제 상태를 확인한다.

```console
tmux list-sessions
tmux capture-pane -t claude-auth-refactor -p -S -120
```

`tmux`는 남아 있고 shell prompt만 보인다면 같은 pane에서 이름 있는 Claude Code 세션을
재개할 수 있다.

```console
claude --resume auth-refactor
```

`tmux`까지 사라졌다면 새 `tmux` 세션을 하나만 만든 뒤 같은 작업 디렉터리에서
`claude --resume auth-refactor`를 시작한다. `claude --continue`는 현재 작업 디렉터리의
가장 최근 대화를 재개하므로 여러 작업이 섞인 환경에서는 명시적인 이름이나 session ID가
더 안전하다.

재개 전에 다음을 다시 확인한다.

- 현재 작업 디렉터리와 branch가 원래 값과 같은가?
- 다른 프로세스가 같은 working tree를 수정하고 있지 않은가?
- 이전 실행이 남긴 uncommitted change가 무엇인가?
- 사용자 승인 없이 다시 실행하면 안 되는 command가 있는가?
- 완료 조건과 금지사항이 현재 Hermes 대화에도 남아 있는가?

## 완료 보고는 Claude Code 밖에서 검증한다

Claude Code가 완료를 선언한 뒤 Hermes가 독립적으로 다음 증거를 확인하게 한다.

- `git status --short`와 범위 밖 변경 여부
- `git diff --check`와 실제 diff
- 합의한 test·lint·build의 command, exit code, 핵심 output
- 새 dependency, migration, generated file의 예상 밖 변경
- commit·push·deploy 여부
- `tmux`와 Claude Code 세션을 유지했는지 종료했는지

최종 보고 예시는 다음 구조가 좋다.

```text
Claude Code 작업 결과:
Hermes 독립 검증:
변경 파일:
테스트와 종료 코드:
승인 없이 실행하지 않은 행동:
남은 위험:
tmux / Claude Code 세션 상태:
```

## 흔한 오류

| 증상 | 흔한 원인 | 확인과 해결 |
|---|---|---|
| 같은 작업이 두 번 실행됨 | 기존 `tmux`를 확인하지 않고 재생성 | 세션 목록과 pane을 먼저 확인하고 이름을 고정 |
| 지시가 입력되지 않음 | trust·permission dialog가 열려 있음 | 화면을 캡처하고 선택지를 사용자에게 보고 |
| 원치 않은 선택이 실행됨 | dialog 위에 일반 문장을 전송 | 입력 전에 화면 상태를 분류하고, dialog에서는 키를 보내지 않음 |
| 완료라고 했지만 파일이 다름 | nested agent의 요약만 신뢰 | Hermes가 diff와 test를 별도 실행·확인 |
| 잘못된 저장소를 수정함 | `tmux` 시작 directory 누락 | 절대 경로, branch, worktree를 시작 보고에 포함 |
| `/continue`가 다른 대화를 엶 | 같은 directory에 여러 저장 세션 존재 | `--name`과 `--resume <name>` 사용 |
| `claude -p`가 결과 없이 실패함 | thinking·도구 왕복 중 `--max-turns` 도달 | 짧은 단순 작업만 print mode로 실행하고 복잡한 작업은 대화형 세션으로 전환 |
| 화면이 깨지거나 일부만 보임 | terminal 크기·화면 redraw 문제 | pane 크기를 고정하고 필요하면 한 번 redraw한 뒤 다시 캡처 |
| 종료 뒤 background process가 남음 | Claude Code가 별도 task를 실행 | Claude Code task 목록과 OS process를 확인한 뒤 종료 범위 승인 |
| 비용이 예상보다 큼 | 긴 대화·반복 캡처·중복 후속 지시 | 상태 전환 때만 확인하고 `/compact` 또는 새 작업 세션 검토 |

## 9장 확인 문제

- Hermes 세션이 살아 있다는 사실이 `tmux`와 Claude Code 프로세스의 생존을 보장하는가?
- Claude Code가 작업 중일 때 후속 문장을 바로 보낼 수 있어도 화면 확인이 먼저인 이유는
  무엇인가?
- Hermes의 terminal command를 승인한 뒤 Claude Code의 영구 permission rule도 자동으로
  허용하면 안 되는 이유는 무엇인가?
- `claude --continue`보다 이름 있는 `--resume`이 여러 작업을 운영할 때 안전한 이유는
  무엇인가?

## 참고 자료

- [Hermes 번들 Claude Code 스킬](https://hermes-agent.nousresearch.com/docs/user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-claude-code)
- [Hermes 스킬 시스템](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/)
- [Hermes Built-in Tools Reference](https://hermes-agent.nousresearch.com/docs/reference/tools-reference/)
- [Claude Code CLI Reference](https://code.claude.com/docs/en/cli-usage)
- [Claude Code Interactive Mode](https://code.claude.com/docs/en/interactive-mode)
- [Claude Code Permissions](https://code.claude.com/docs/en/permissions)
- [tmux Getting Started](https://github.com/tmux/tmux/wiki/Getting-Started)

[← 8장](./08-recipes-and-troubleshooting.md) · [목차](./index.md)
