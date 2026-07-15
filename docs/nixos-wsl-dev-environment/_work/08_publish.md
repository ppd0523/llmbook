---
title: 최종 산출물 구성과 출판 변환 검수
version: 1.2
status: complete
owner: agent
updated: 2026-07-15
target_reader: 터미널과 언어별 버전 관리에는 익숙하지만 Nix는 처음인 시니어 개발자
topic: Flake와 독립 실행형 Home Manager를 이용한 이식 가능한 NixOS 개발 환경
---

# 최종 산출물 구성과 출판 변환 검수

## 1. 최종 산출물 계획

- 기준 원고 Markdown: `_work/07_final.md`
- 원본 버전: 1.2
- 최종 산출물 형식: 챕터형 Markdown 학습자료
- 최종 산출물 경로: `nixos-wsl-dev-environment/index.md`와 8개 번호 챕터 폴더
- 챕터 폴더 구조: `01_mental_model/`부터 `08_operations_and_troubleshooting/`
- 보조 산출물: `assets/example-config/`의 복제 가능한 Nix 구성 템플릿
- 구성 또는 변환 도구: Markdown 파일 분할, PowerShell 기반 정적 링크·구조 검사
- 구성 또는 변환 명령: 별도 출판 형식 변환 없음
- 구성 또는 변환 일시: 2026-07-15

## 2. 산출 결과

| 형식 | 파일 | 상태 | 비고 |
|---|---|---|---|
| Chapter Markdown | `index.md`, `01_*/chapter.md`부터 `08_*/chapter.md` | 완료 | 사용자 최종 산출물 |
| Markdown | `_work/07_final.md` | 완료 | 출판 전 기준 원고, 내부 파일 |
| Example config | `assets/example-config/` | 완료 | Flake와 모듈 전체 예제 |
| HTML | 없음 | 대상 아님 | 요청되지 않음 |
| PDF | 없음 | 대상 아님 | 요청되지 않음 |
| ePub | 없음 | 대상 아님 | 요청되지 않음 |
| PPT/PPTX | 없음 | 대상 아님 | 요청되지 않음 |

## 3. 공통 검수

- [x] `01_scope.md`의 챕터형 Markdown 계획과 실제 결과가 일치한다.
- [x] 자료 폴더 루트에서 `index.md`와 번호 챕터를 바로 식별할 수 있다.
- [x] 번호가 붙은 내부 단계 파일은 `_work/` 아래에만 있다.
- [x] 최종 산출물에 내부 작업 메모가 없다.
- [x] 최종 산출물과 기준 원고에 금지된 작업 표지가 없다.
- [x] 각 최종 파일의 제목 계층 밖 `#` 제목은 하나다.
- [x] `index.md`의 목차가 8개 장에 연결된다.
- [x] 최종 Markdown의 상대 링크를 검사했으며 누락된 로컬 대상이 없다.
- [x] 최종 사용자 문서의 고유 외부 링크 33개가 공식 프로젝트 도메인을 가리키며 주요 대상은 조사 단계에서 열어 확인했다.
- [x] 검사 대상 Markdown의 코드 펜스가 모두 짝을 이룬다.
- [x] 코드 블록에 언어 식별자가 있다.
- [x] 표의 열 구분과 제목 행이 유지된다.
- [x] 이미지와 수식은 사용하지 않았으므로 경로·렌더링 대상이 없다.
- [x] 각 장의 추가 읽을거리가 유지된다.

## 4. 챕터형 Markdown 검수

- [x] 챕터 폴더가 `01_`부터 `08_`까지 읽는 순서로 번호가 붙어 있다.
- [x] 8개 챕터 폴더 모두 `chapter.md`가 있다.
- [x] 전체 목차 `index.md`가 있다.
- [x] 앞 장, 목차, 다음 장의 상대 링크가 동작한다.
- [x] `assets/example-config/`에 대한 상대 링크가 동작한다.
- [x] 각 장에 독립적인 제목, 학습 목표, 설명, 확인 또는 오류, 요약이 있다.

## 5. 예제 구성 검수

- [x] Nix 파일 7개의 중괄호와 대괄호 수가 일치한다.
- [x] Git, tree, bat, ripgrep, Neovim, uv, NVM, rustup, zsh, Starship, fzf, Autojump 선언을 확인했다.
- [x] Node.js, Python, Rust 툴체인은 직접 Nix 패키지로 선언하지 않았다.
- [x] Docker 구성은 포함하지 않았다.
- [x] 최초 Home Manager 실행 앱이 잠긴 Home Manager 입력을 사용한다.
- [x] NVM 프로그램 파일과 쓰기 가능한 런타임 상태를 분리했다.
- [x] 네이티브 하드웨어 파일이 있을 때만 `native` 출력이 나타난다.
- [x] 템플릿에는 임의의 `flake.lock`을 만들지 않았고 생성·커밋 절차를 문서화했다.

## 6. 실행 환경 검수 범위

현재 작성 호스트에는 Git과 `wsl.exe`는 있지만 `nix` 명령과 등록된 WSL 배포판이 없어 Nix 평가, 빌드, Home Manager 활성화는 실행하지 않았다. 이 제한은 `_work/05_review.md`에 기록했다. 최종 절차는 실제 상태를 바꾸기 전에 `nixos-rebuild build`와 Home Manager `build`를 먼저 수행하도록 구성했다.

## 7. 발견된 문제

| 위치 | 형식 | 문제 | 원인 | 처리 방향 | 상태 |
|---|---|---|---|---|---|
| 최초 시스템 적용 | 명령 | 시스템 Flake 기능 적용 전 rebuild가 실패할 수 있음 | bootstrap 시 기능 미활성 | 최초 두 명령에 일회성 Nix 옵션 추가 | 반영 |
| 최초 Home Manager 적용 | 명령 | 외부 릴리스 브랜치 HEAD를 다시 받을 수 있음 | 원격 URL 직접 실행 | 잠긴 입력을 로컬 Flake 앱으로 노출 | 반영 |
| Rust 자동 설치 설명 | 본문 | 환경 변수를 제거해도 기본 자동 설치가 유지됨 | rustup 기본값 오해 | 비활성 값 `0`을 명시 | 반영 |
| 네이티브 시스템 | 예제 | 하드웨어 파일만으로 기존 호스트 정책을 완전히 복원할 수 없음 | 부트로더·그래픽 등 호스트별 설정 | 전환 전 기존 정책을 이관하도록 경고 | 반영 |
| 최초 시작 | 2장·예제 README | 개인 구성 저장소가 이미 있다고 가정함 | 복원 흐름을 최초 생성에도 사용 | GitHub 빈 저장소와 SSH 인증부터 첫 push까지 별도 절차로 구성 | 반영 |
| Git bootstrap | 2장·7장·예제 README | `github:`는 API 403 가능, `git+https:`는 아직 없는 Git을 요구 | 채널 기반 `nix-shell -p git openssh`로 교체하고 Flake lock의 토큰 대응은 별도로 설명 | 반영 |

## 8. 되돌아가기 판단

- 최종 산출물 구조 수정 필요: 없음
- 형식 변환 문제: 없음
- Markdown 기준 원고 수정 필요: 없음
- 내용 구조 수정 필요: 없음
- 기술 검증 재수행 필요: 실제 NixOS 환경을 확보해 구성을 변경할 때 해당 환경에서 build 검증

## 9. 최종 결론

- 배포 가능 최종 산출물: `index.md`와 8개 챕터형 Markdown
- 배포 가능 보조 형식: `assets/example-config/` 구성 템플릿
- 배포 보류 형식: 없음
- 추가 작업: PDF·HTML 변환은 요청 시 별도 수행
