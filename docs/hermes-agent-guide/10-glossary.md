# Hermes Agent 운영 용어집

이 장은 Hermes를 설치·운영할 때 반복해서 만나는 말을 빠르게 찾기 위한 참고 자료다.
명령어와 설정 키는 실제 화면의 원문을 유지하고, 설명은 한국어를 우선한다. 용어집은
본문의 첫 설명을 대신하지 않는다. 어떤 기능을 선택해야 하는지 판단하려면 해당 장의
예시와 주의사항도 함께 읽는다.

## 가장 먼저 구분할 여섯 쌍

| 혼동하기 쉬운 말 | 차이 |
|---|---|
| 프로필 / 세션 | 프로필은 장기 역할·설정·기억의 묶음이고, 세션은 한 대화의 이력과 실행 상태다. |
| 작업 공간 / 샌드박스 | 작업 공간은 도구가 시작하는 디렉터리이고, 샌드박스는 실제 접근을 제한하는 실행 경계다. |
| 도구 / 도구 모음 / 스킬 | 도구는 개별 기능, 도구 모음은 기능 묶음, 스킬은 그 기능을 쓰는 재사용 절차다. |
| `/queue` / `/background` / Kanban | 각각 같은 세션의 다음 차례, 별도 세션의 독립 실행, 재시작 뒤에도 남는 공유 작업 큐다. |
| 자격 증명 풀 / 대체 경로 | 자격 증명 풀은 같은 제공자 안에서 키를 바꾸고, 대체 경로는 다른 `provider:model` 조합으로 전환한다. |
| Hermes / `tmux` / Claude Code 세션 | 운영 대화, 터미널 프로세스와 화면, Claude Code 대화 이력을 각각 보존하는 서로 다른 상태다. |

## 에이전트와 상태

| 용어 | 뜻 | 혼동하지 말 것 |
|---|---|---|
| 에이전트(agent) | 모델이 지시와 현재 맥락을 바탕으로 도구를 선택해 작업하는 실행 주체다. | Discord 봇 계정 자체 |
| 프로필(profile) | 설정, 키, SOUL, 기억, 세션, 스킬, cron, 게이트웨이 상태를 분리한 Hermes home이다. | 파일 시스템 샌드박스 |
| 세션(session) | 한 대화의 전체 이력과 현재 실행 상태를 저장·재개하는 단위다. | Discord 채널 전체 |
| 세션 ID | 저장된 세션 한 건을 식별하는 고유 값이다. | 메시징 경로를 계산한 세션 키 |
| 세션 키(session key) | 플랫폼, 채팅, 스레드, 사용자 같은 메시지 출처로부터 계산한 안정적인 경로 선택 키다. | 사람이 붙인 세션 제목 |
| 게이트웨이(gateway) | 메시징 서비스 연결, 권한 검사, 세션 선택, cron 실행, 응답 전달을 맡는 장기 실행 프로세스다. | 모델 제공자 |
| 작업 공간(workspace) | 터미널과 파일 도구가 작업을 시작하는 디렉터리다. | 접근 가능한 전체 경계 |
| 샌드박스(sandbox) | 파일·명령·네트워크 접근을 실제 환경 수준에서 제한하는 격리 경계다. | 프로필 또는 `terminal.cwd` |
| 맥락(context) | 모델이 현재 판단에 사용할 수 있도록 이번 호출에 전달된 지시, 대화, 도구 결과의 묶음이다. | 저장된 전체 세션 이력 |
| 맥락 창(context window) | 모델이 한 번의 호출에서 처리할 수 있는 token 양의 한도다. | 세션 저장 용량 |

세션 이력은 저장돼 있어도 전부가 매 호출의 맥락에 다시 들어가는 것은 아니다. 길어진
대화는 압축될 수 있고, 도구 출력 일부는 별도 저장소에서 다시 찾아야 할 수 있다.

## 도구와 확장

| 용어 | 뜻 | 예 |
|---|---|---|
| 도구(tool) | 에이전트가 구조화된 입력으로 호출하는 개별 기능이다. | `read_file`, `web_search`, `terminal` |
| 도구 모음(toolset) | 함께 켜고 끌 수 있도록 관련 도구를 묶은 설정 단위다. | `file`, `terminal`, `coding` |
| 스킬(skill) | 기존 도구와 명령을 어떤 순서·규칙으로 사용할지 적은 재사용 절차와 자료 묶음이다. | `claude-code` |
| MCP | Model Context Protocol의 약자로, 외부 도구 서버를 Hermes에 연결하는 표준 프로토콜이다. | GitHub·DB·사내 API MCP server |
| 플러그인(plugin) | Hermes 프로세스 안에 기능, hook, tool, dashboard surface 등을 추가하는 확장 패키지다. | 설치형 기능 확장 |
| 터미널 백엔드 | Hermes의 셸 명령이 실제로 실행되는 환경이다. | local, Docker, SSH |
| 백그라운드 프로세스(background process) | `terminal(background=true)`로 시작해 터미널 호출이 끝난 뒤에도 계속 실행되는 OS 프로세스다. | `/background` 에이전트 세션 |

스킬은 새 도구를 반드시 만들지 않고도 기존 기능의 사용법을 확장할 수 있다. MCP는
Hermes 밖의 서버가 제공하는 도구를 연결하며, 플러그인은 Hermes 자체의 실행 지점에
코드를 붙인다.

## 지시와 기억

| 용어 | 뜻 | 주로 두는 곳 |
|---|---|---|
| 프롬프트(prompt) | 모델에게 전달하는 자연어 또는 구조화된 지시다. | 현재 메시지, task body |
| 시스템 프롬프트(system prompt) | 역할, 도구, 안전 규칙, 기억처럼 일반 사용자 지시보다 상위에서 실행을 구성하는 지시 묶음이다. | Hermes가 세션 시작 시 구성 |
| 프로젝트 맥락 파일(context file) | 저장소에서 발견해 프로젝트 규칙으로 시스템 프롬프트에 넣는 파일이다. | `.hermes.md`, `AGENTS.md` 등 |
| `SOUL.md` | 프로필의 정체성, 말투, 장기 행동 원칙을 적는 파일이다. | profile home |
| `USER.md` | 이름, 시간대, 소통 선호처럼 사용자에 관한 지속 정보를 적는 파일이다. | profile memory |
| `MEMORY.md` | 환경, 관례, 도구 특성, 확인된 사실처럼 세션을 넘어 기억할 내용을 적는 파일이다. | profile memory |
| 스냅샷(snapshot) | 특정 시점의 상태를 나중에 참조하거나 복원할 수 있도록 저장한 복사본이다. | system prompt snapshot, `/snapshot` |
| 체크포인트(checkpoint) | 파일 변경 전 작업 공간을 복구할 수 있도록 저장한 파일 상태다. | `/rollback` |
| 맥락 압축 | 긴 대화의 핵심 제약과 진행 상태를 요약해 모델 입력 길이를 줄이는 작업이다. | `/compress`, 자동 compression |
| 프롬프트 캐시 | 반복되는 프롬프트 앞부분을 제공자가 잠시 보관해 후속 호출 비용과 지연을 줄이는 기능이다. | 지원 provider의 cache |

`/snapshot`은 Hermes 설정·상태 복원에, checkpoint와 `/rollback`은 작업 파일 복원에
쓰인다. 이름이 비슷해도 복구 대상이 다르므로 실행 전에 무엇이 저장됐는지 확인한다.

## 실행과 큐

| 용어 | 뜻 | 수명 |
|---|---|---|
| 실행 차례(turn) | 사용자 입력 하나를 받아 에이전트 응답이 끝날 때까지의 대화 단위다. | 현재 세션 |
| 실행(run) | 한 turn 안에서 모델 호출과 도구 호출이 이어지는 실제 작업 시도다. | 현재 turn |
| 전경 실행(foreground) | 현재 대화가 완료를 기다리는 일반 실행이다. | 현재 세션 |
| `/queue` | 현재 실행이 끝난 뒤 같은 세션의 다음 turn으로 처리할 메시지를 대기시킨다. | 세션에 종속 |
| `/steer` | 현재 도구가 끝난 다음 실행 중인 turn에 보정 지시를 넣는다. | 현재 run에 종속 |
| `/background` | 전달한 prompt만으로 별도 agent session을 실행하고 결과를 원래 chat에 보낸다. | process·session에 종속 |
| 위임(delegation) | 부모가 새 맥락의 child agent에게 하위 작업을 맡기고 최종 요약을 받는 방식이다. | 소유 세션·process에 종속 |
| 지속 목표(persistent goal) | 완료 판정이 날 때까지 같은 목표를 여러 turn에 걸쳐 자동 계속하는 기능이다. | goal session에 종속 |
| cron | 정해진 시각이나 주기에 독립 agent job을 시작하는 스케줄러다. | 저장된 schedule |
| Kanban | 작업, 상태, 의존 관계, comment, handoff를 DB에 보존하는 공유 작업 큐다. | 재시작 뒤에도 지속 |

“비동기”는 결과를 기다리는 동안 다른 대화를 할 수 있다는 뜻이지, 재시작 뒤 실행이
자동 복구된다는 뜻은 아니다. 내구성(durability)이 필요하면 Kanban이나 목적에 맞는
cron job을 선택한다.

## Kanban 협업

| 용어 | 뜻 |
|---|---|
| 보드(board) | 여러 작업과 상태 이력을 담는 전체 작업판이다. |
| 작업(task) | 목표, 입력, 담당자, 완료 조건을 담은 실행 단위다. |
| 담당자(assignee) | 작업을 실행할 프로필 또는 worker lane의 이름이다. |
| 의존 관계(dependency) | 부모 작업이 끝나야 자식 작업을 시작할 수 있게 만든 선후 관계다. |
| 디스패처(dispatcher) | 실행 가능한 작업을 찾아 worker process를 시작하는 반복 실행부다. |
| 작업자(worker) | 배정된 task를 읽고 실제 도구 작업과 상태 갱신을 수행하는 agent process다. |
| 인계(handoff) | 다음 작업자가 재조사하지 않도록 남기는 결과 요약, 산출물, 검증, 남은 위험이다. |
| heartbeat | 긴 작업이 살아 있고 진행 중임을 보드에 알리는 생존 신호다. |
| 차단(block) | 필요한 입력·권한·기능이 없어 작업을 진행할 수 없음을 상태와 이유로 기록하는 일이다. |
| 재시도(retry) | 실패 원인을 보완한 뒤 같은 task를 다시 실행하는 시도다. |
| 멱등성 키(idempotency key) | 같은 생성 요청이 반복돼도 중복 task가 생기지 않도록 요청을 식별하는 키다. |
| 감사 이력(audit trail) | 상태 전환, 실행 시도, comment, 결과가 시간순으로 남은 기록이다. |

## 모델과 비용

| 용어 | 뜻 | 혼동하지 말 것 |
|---|---|---|
| 제공자(provider) | 모델 API의 인증, 과금, routing을 제공하는 서비스다. | 모델 자체 |
| 모델(model) | 다음 token과 tool call을 생성하는 추론 엔진이다. | 모델을 호출하는 provider |
| 직접 제공자(native provider) | 모델 개발 회사의 API를 직접 쓰는 경로다. | 여러 회사를 중계하는 aggregator |
| 통합 제공자(aggregator) | 여러 회사의 모델을 한 API로 중계하는 서비스다. | 모델 개발사 |
| 주 모델(main model) | 사용자 turn, 계획, tool loop, 최종 응답을 처리하는 기본 모델이다. | auxiliary model |
| 보조 모델(auxiliary model) | title, vision, compression, approval 같은 작은 부가 작업 전용 모델이다. | child agent의 delegation model |
| delegation model | 위임된 child agent가 추론과 도구 호출에 쓰는 모델이다. | main model |
| 대체 경로(fallback) | 주 `provider:model` 실패 시 이어서 시도하는 예비 조합이다. | 같은 provider 안의 key rotation |
| 자격 증명(credential) | API key나 OAuth token처럼 서비스 접근 권한을 증명하는 값이다. | provider 또는 model |
| 자격 증명 풀 | 같은 provider의 여러 credential을 선택·회전하는 묶음이다. | cross-provider fallback |
| OAuth | 비밀번호를 직접 넘기지 않고 서비스가 발급한 token으로 접근 권한을 위임하는 인증 방식이다. | API key 문자열 |
| token | 모델이 텍스트를 처리하고 생성할 때 세는 작은 단위다. | API access token |
| reasoning token | 모델 내부 추론 과정에 사용되며 제공자 정책에 따라 비용에 포함되는 token이다. | 출력 글자 수 |
| latency | 요청을 보낸 뒤 결과가 오기까지 걸린 시간이다. | token 단가 |

문맥의 token과 인증의 access token은 이름만 같고 역할이 전혀 다르다. 비용을 말할 때는
input·output·reasoning token인지, 인증을 말할 때는 OAuth access token인지 밝혀 쓴다.

## 보안과 변경

| 용어 | 뜻 |
|---|---|
| 허용 목록(allowlist) | 접근을 허용할 사용자, 역할, 채널만 명시한 목록이다. |
| 기본 거부(fail-closed) | 설정 누락이나 판단 불확실 시 허용하지 않는 정책이다. |
| 명령 승인(command approval) | 위험한 셸 명령을 실행하기 전 정책 또는 사용자가 허용 여부를 결정하는 절차다. |
| 쓰기 보호(write guard) | 파일 도구가 보호 경로나 허용 범위 밖을 수정하지 못하게 막는 검사다. |
| 쓰기 안전 루트(write-safe root) | 파일 도구가 쓸 수 있도록 허용한 최상위 경로다. |
| 부수 효과(side effect) | 파일 수정, 메시지 전송, 배포처럼 답변 밖의 실제 상태를 바꾸는 행동이다. |
| 프롬프트 주입(prompt injection) | 외부 콘텐츠가 원래 지시를 무시하고 다른 행동을 하도록 에이전트를 유도하는 공격·오염이다. |
| 비밀 정보(secret) | API key, token, password처럼 노출되면 권한을 빼앗길 수 있는 값이다. |

## Git과 검증

| 용어 | 뜻 |
|---|---|
| 저장소(repository) | 파일 이력과 branch를 Git으로 관리하는 프로젝트 단위다. |
| branch | 서로 다른 변경 이력을 가리키는 Git 이름이다. |
| 작업 트리(working tree) | 현재 checkout의 파일이 실제로 펼쳐져 수정되는 디렉터리다. |
| Git worktree | 같은 저장소의 다른 branch를 별도 디렉터리에 checkout해 동시에 작업하는 Git 기능이다. |
| diff | 이전 상태와 현재 상태의 줄 단위 차이다. |
| 산출물(artifact) | 작업 결과로 만든 파일, report, build 결과, URL 같은 전달 대상이다. |
| 검증(verification) | test, lint, build, diff, source 확인으로 완료 주장을 확인하는 과정과 증거다. |
| 회귀(regression) | 새 변경 때문에 이전에 되던 기능이 다시 실패하는 문제다. |

## Claude Code와 `tmux`

| 용어 | 뜻 |
|---|---|
| 출력 모드(print mode) | `claude -p` 요청 하나를 처리해 출력하고 프로세스가 끝나는 비대화형 방식이다. |
| 대화형 모드(interactive mode) | 같은 Claude Code 프로세스에 여러 차례 입력하며 상태를 이어 가는 방식이다. |
| 터미널 멀티플렉서 | 터미널 프로그램의 화면과 프로세스를 이름 있는 세션으로 유지·재접속하게 하는 프로그램이다. |
| `tmux` 세션 | `tmux`가 이름 아래 유지하는 창과 터미널 프로세스 묶음이다. |
| 분할 화면(pane) | 한 `tmux` 세션 안의 개별 터미널 화면이다. `tmux` window와는 다른 하위 단위다. |
| Claude Code 세션 | Claude Code가 저장하는 대화 이력, checkpoint, 작업 상태다. |
| 셸 프롬프트(shell prompt) | Bash·PowerShell 같은 셸이 다음 명령을 기다리는 입력 표시다. |
| 권한 대화상자(permission dialog) | Claude Code가 명령이나 파일 접근을 허용할지 묻는 화면이다. |
| 신뢰 대화상자(trust dialog) | Claude Code가 현재 작업 공간을 신뢰할지 묻는 화면이다. |
| `--continue` | 현재 작업 디렉터리의 가장 최근 Claude Code 대화를 재개한다. |
| `--resume` | ID나 이름을 지정해 특정 Claude Code 대화를 재개한다. |

## 더 읽을 자료

- [Hermes Sessions](https://hermes-agent.nousresearch.com/docs/user-guide/sessions)
- [Tools & Toolsets](https://hermes-agent.nousresearch.com/docs/user-guide/features/tools/)
- [MCP](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp)
- [Profiles](https://hermes-agent.nousresearch.com/docs/user-guide/profiles)
- [Kanban](https://hermes-agent.nousresearch.com/docs/user-guide/features/kanban)
- [Credential Pools](https://hermes-agent.nousresearch.com/docs/user-guide/features/credential-pools/)
- [Fallback Providers](https://hermes-agent.nousresearch.com/docs/user-guide/features/fallback-providers)
- [Checkpoints and `/rollback`](https://hermes-agent.nousresearch.com/docs/user-guide/checkpoints-and-rollback/)

[← 9장](./09-control-claude-code-interactive-session.md) · [목차](./index.md)
