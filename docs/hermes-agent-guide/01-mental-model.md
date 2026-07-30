# Hermes를 이해하는 운영 모델

Hermes를 잘 쓰려면 먼저 “agent 하나”를 하나의 대화창으로 생각하지 않아야 한다.
사용자가 Discord·CLI·dashboard에서 메시지를 보내면 gateway가 적절한 session을 찾고,
agent core가 model과 tool을 사용해 일한다. profile은 이 실행에 사용할 장기 설정과
상태를 고른다.

```text
Discord / CLI / Dashboard
          │
          ▼
       Gateway ── session 선택
          │
          ▼
   Profile의 agent core
     ├─ main model
     ├─ tools와 skills
     ├─ SOUL·project context·memory
     └─ terminal workspace
```

## Hermes가 할 수 있는 일

설치하고 활성화한 toolset에 따라 Hermes는 다음 작업을 할 수 있다.

| 영역 | 가능한 동작 |
|---|---|
| 파일과 코드 | 파일 읽기·수정, 검색, patch, test·build 실행, Git diff와 checkpoint 복구 |
| terminal | local, Docker, SSH, cloud sandbox에서 command와 background process 실행 |
| web과 browser | 검색, page 추출, browser navigation과 interaction |
| media | image 분석·생성, text-to-speech, Discord voice |
| 기억 | 사용자 취향과 환경 사실을 session을 넘어 저장하고 과거 session 검색 |
| 자동화 | cron schedule, background session, persistent goal |
| 병렬화 | fresh-context subagent delegation |
| 다중 agent | profile별 독립 agent와 공유 Kanban board |
| 확장 | skill, MCP server, Home Assistant와 외부 integration |

모든 기능이 자동으로 켜지는 것은 아니다. 선택한 setup mode, provider credential,
toolset, operating system, terminal backend에 따라 실제 도구가 달라진다.
`hermes tools`와 `/status`로 현재 구성을 확인한다. 전체 범위는
[Tools & Toolsets](https://hermes-agent.nousresearch.com/docs/user-guide/features/tools/)에
정리되어 있다.

## 상태를 나누는 네 단위

Hermes 운영에서 가장 자주 섞이는 개념은 profile, session, workspace, sandbox다.

| 단위 | 무엇을 결정하는가 | 무엇을 보장하지 않는가 |
|---|---|---|
| profile | config, key, SOUL, memory, session, skill, cron, gateway state | filesystem 격리 |
| session | 대화 history, 현재 맥락, 실행 중 agent | 별도 OS process나 별도 directory |
| workspace | terminal·file tool이 시작하는 directory | 그 밖의 path 접근 차단 |
| sandbox | 실제 command와 file access의 격리 경계 | 기억·성격·session 분리 |

예를 들어 `coder` profile의 `terminal.cwd`를 `/work/app`으로 설정하면 command가 그
directory에서 시작한다. 그러나 local backend에서 실행한다면 같은 OS user가 읽을 수
있는 다른 directory도 접근할 수 있다. 강한 격리가 필요하면 Docker, SSH, Daytona 같은
terminal backend와 filesystem 정책을 별도로 사용한다.

## 작업을 나누는 여섯 실행 방식

같은 요청이라도 얼마나 오래 남아야 하고 누가 이어받아야 하는지에 따라 실행 방식을
달리 선택한다.

| 실행 방식 | 상태 지속성 | 현재 대화 맥락 | 적합한 일 |
|---|---|---|---|
| foreground turn | 현재 session | 전부 사용 | 지금 바로 끝낼 일반 작업 |
| `/background` | 별도 background session | 전달한 prompt만 사용 | 주 대화를 막지 않을 독립 작업 |
| delegation | 현재 process 안의 child | goal·context만 사용 | 짧은 조사·review 병렬화 |
| `/goal` | 여러 turn 자동 계속 | 같은 goal session | 완료 조건까지 반복할 한 작업 |
| Kanban | SQLite board에 지속 | task body·comment·handoff | 역할 간 전달, 재시도, 재시작 |
| cron | schedule에 지속 | job prompt·skill·workdir | 정기 실행과 알림 |

이 표의 핵심은 “병렬”과 “지속”이 다르다는 점이다. delegation은 병렬이지만 실행
process가 사라지면 이어서 실행하는 durable queue가 아니다. Kanban은 약간 더 무겁지만
task와 handoff가 남고 다른 profile이 다시 맡을 수 있다.

## 처음 점검할 명령

```console
hermes doctor
hermes profile
hermes tools
hermes gateway status
hermes config
```

Discord에서는 다음 명령으로 현재 대화와 비용을 확인한다.

```text
/status
/whoami
/usage
/agents
```

`/status`는 session, 최근 tool과 file 정보를 보여 주고, `/whoami`는 slash command
권한 tier를 보여 준다. `/agents`는 실행 중 agent와 task를 확인한다.

## 운영 원칙

- 대화 history를 database로 보지 않는다. 확정된 요구사항은 project context나 Kanban
  task에 기록한다.
- profile을 많이 만들기 전에 한 profile과 여러 session으로 충분한지 확인한다.
- 일의 결과보다 완료 증거를 요구한다. 파일, test, source URL, diff, 남은 risk를
  closing summary에 포함시킨다.
- 변경 작업에는 범위와 금지사항을 주고, 외부 전송·배포·삭제는 사전 승인을 요구한다.
- 긴 작업은 중간 채팅을 많이 보내기보다 상태 명령과 durable task board로 관찰한다.

[← 목차](./index.md) · [2장: Discord에서 안전하게 지시하기 →](./02-discord-operations.md)
