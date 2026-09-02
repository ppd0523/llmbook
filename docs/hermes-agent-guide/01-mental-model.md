# Hermes를 이해하는 운영 모델

Hermes를 잘 쓰려면 먼저 “에이전트 하나”를 하나의 대화창으로 생각하지 않아야 한다.
사용자가 Discord·명령줄(CLI)·대시보드에서 메시지를 보내면 게이트웨이(gateway)가
적절한 세션을 찾고, 에이전트가 모델과 도구(tool)를 사용해 일한다. 게이트웨이는
Discord 같은 메시징 서비스와 Hermes 실행부 사이에서 메시지 수신, 권한 검사, 세션
선택, 응답 전달을 맡는 장기 실행 프로세스다. 프로필은 이 실행에 사용할 장기 설정과
상태를 고른다.

```text
Discord / CLI / Dashboard
          │
          ▼
       게이트웨이 ── 세션 선택
          │
          ▼
   프로필의 에이전트 실행부
     ├─ 주 모델
     ├─ 도구와 스킬
     ├─ SOUL·프로젝트 맥락·기억
     └─ 터미널 작업 공간
```

## Hermes가 할 수 있는 일

도구(tool)는 파일 읽기나 웹 검색처럼 에이전트가 호출할 수 있는 개별 기능이다. 도구
모음(toolset)은 관련 도구를 한 이름으로 묶어 세션이나 플랫폼별 사용 가능 범위를
정하는 설정 단위다. 설치하고 활성화한 도구 모음에 따라 Hermes는 다음 작업을 할 수
있다.

| 영역 | 가능한 동작 |
|---|---|
| 파일과 코드 | 파일 읽기·수정, 검색, patch, test·build 실행, Git diff와 checkpoint 복구 |
| 터미널 | local, Docker, SSH, cloud sandbox에서 명령과 background process 실행 |
| 웹과 브라우저 | 검색, 페이지 추출, 브라우저 탐색과 상호작용 |
| 미디어 | 이미지 분석·생성, 음성 합성, Discord 음성 채널 |
| 기억 | 사용자 취향과 환경 사실을 세션을 넘어 저장하고 과거 세션 검색 |
| 자동화 | cron 일정, background session, 지속 목표 |
| 병렬화 | 새 맥락의 하위 에이전트 위임 |
| 다중 에이전트 | 프로필별 독립 에이전트와 공유 Kanban 보드 |
| 확장 | 스킬, MCP 서버, Home Assistant와 외부 연동 |

스킬(skill)은 기존 도구를 어떤 순서와 규칙으로 사용할지 적은 재사용 절차다. MCP
(Model Context Protocol)는 GitHub·데이터베이스·사내 API처럼 Hermes 밖에 있는 도구
서버를 연결하는 표준 프로토콜이다. 스킬은 “도구를 쓰는 방법”, MCP는 “외부 도구를
연결하는 방법”에 가깝다.

모든 기능이 자동으로 켜지는 것은 아니다. 선택한 setup mode, provider credential,
toolset, operating system, terminal backend에 따라 실제 도구가 달라진다.
`hermes tools`와 `/status`로 현재 구성을 확인한다. 전체 범위는
[Tools & Toolsets](https://hermes-agent.nousresearch.com/docs/user-guide/features/tools/)에
정리되어 있다.

## 먼저 세 질문으로 범위를 정한다

새 요청을 보내기 전에 다음 세 가지만 결정해도 대부분의 운영 실수를 피할 수 있다.

1. **누가 하는가?** 장기 역할과 권한이 다르면 프로필을 나눈다.
2. **어떤 맥락을 쓰는가?** 이전 대화가 필요하면 기존 세션, 필요 없으면 새 스레드나
   새 세션을 쓴다.
3. **얼마나 오래 남아야 하는가?** 현재 대화 안에서 끝나면 일반 실행이나 위임,
   재시작 뒤에도 남아야 하면 Kanban이나 cron을 쓴다.

프로필은 “누가”, 세션은 “어떤 대화 맥락”, 작업 공간은 “어디서”, 실행 방식은
“얼마나 오래”를 결정한다.

## 상태를 나누는 네 단위

Hermes 운영에서 가장 자주 섞이는 개념은 프로필(profile), 세션(session), 작업 공간
(workspace), 샌드박스(sandbox)다.

| 단위 | 무엇을 결정하는가 | 무엇을 보장하지 않는가 |
|---|---|---|
| 프로필 | 설정, 키, SOUL, 기억, 세션, 스킬, cron, 게이트웨이 상태 | 파일 시스템 격리 |
| 세션 | 한 대화의 이력, 현재 맥락, 실행 상태 | 별도 OS 프로세스나 별도 디렉터리 |
| 작업 공간 | 터미널·파일 도구가 작업을 시작하는 디렉터리 | 그 밖의 경로 접근 차단 |
| 샌드박스 | 명령과 파일 접근을 제한하는 실제 실행 경계 | 기억·성격·세션 분리 |

예를 들어 `coder` profile의 `terminal.cwd`를 `/work/app`으로 설정하면 command가 그
directory에서 시작한다. 그러나 local backend에서 실행한다면 같은 OS user가 읽을 수
있는 다른 directory도 접근할 수 있다. 강한 격리가 필요하면 Docker, SSH, Daytona 같은
terminal backend와 filesystem 정책을 별도로 사용한다.

## 작업을 나누는 여섯 실행 방식

같은 요청이라도 얼마나 오래 남아야 하고 누가 이어받아야 하는지에 따라 실행 방식을
달리 선택한다.

| 실행 방식 | 상태 지속성 | 현재 대화 맥락 | 적합한 일 |
|---|---|---|---|
| 전경 실행(foreground turn) | 현재 세션 | 전부 사용 | 지금 바로 끝낼 일반 작업 |
| `/background` | 별도 background session | 전달한 prompt만 사용 | 주 대화를 막지 않을 독립 작업 |
| 위임 | 현재 세션에 소유된 하위 에이전트 | goal·context만 사용 | 짧은 조사·검토 병렬화 |
| `/goal` | 여러 turn 자동 계속 | 같은 goal session | 완료 조건까지 반복할 한 작업 |
| Kanban | SQLite 보드에 지속 | task body·comment·handoff | 역할 간 전달, 재시도, 재시작 |
| cron | 일정에 지속 | job prompt·skill·workdir | 정기 실행과 알림 |

이 표의 핵심은 “병렬”과 “지속”이 다르다는 점이다. delegation은 비동기로 결과를
돌려줄 수 있지만 소유 세션이 닫히거나 Hermes process가 재시작되면 진행 중 실행을
복구하지 못한다. Kanban은 조금 더 무겁지만 task와 handoff가 남고 다른 profile이 다시
맡을 수 있다.

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

`/status`는 세션, 최근 도구와 파일 정보를 보여 주고, `/whoami`는 슬래시 명령 권한
등급을 보여 준다. `/agents`는 실행 중 에이전트와 작업을 확인한다.

## 운영 원칙

- 대화 history를 database로 보지 않는다. 확정된 요구사항은 project context나 Kanban
  task에 기록한다.
- profile을 많이 만들기 전에 한 profile과 여러 session으로 충분한지 확인한다.
- 일의 결과보다 완료 증거를 요구한다. 파일, test, source URL, diff, 남은 risk를
  closing summary에 포함시킨다.
- 변경 작업에는 범위와 금지사항을 주고, 외부 전송·배포·삭제는 사전 승인을 요구한다.
- 긴 작업은 중간 채팅을 많이 보내기보다 상태 명령과 durable task board로 관찰한다.

## 1장 확인 문제

- 같은 프로필의 새 스레드와 새 프로필은 무엇을 다르게 분리하는가?
- 병렬 실행이 가능하다는 사실만으로 재시작 뒤 복구까지 보장되는가?
- `terminal.cwd`를 지정한 것이 파일 시스템 격리와 같지 않은 이유는 무엇인가?

[← 목차](./index.md) · [2장: Discord에서 안전하게 지시하기 →](./02-discord-operations.md)
