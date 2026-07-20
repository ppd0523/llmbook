---
title: 기술 검증
version: 0.3
status: complete
owner: agent
updated: 2026-07-15
target_reader: 터미널과 언어별 버전 관리에는 익숙하지만 Nix는 처음인 시니어 개발자
topic: Flake와 독립 실행형 Home Manager를 이용한 이식 가능한 NixOS 개발 환경
---

# 기술 검증

## 1. 검증 대상

- 정의: NixOS, Flake, `flake.lock`, 독립 실행형 Home Manager, dotfiles의 소유권 경계
- 코드/알고리즘: Flake 출력, NixOS 모듈, Home Manager 모듈, NVM zsh 자동 전환 훅
- 표: 언어별 버전 관리자와 프로젝트 파일의 책임 구분
- 용어: 복원과 업데이트, 시스템 세대와 Home Manager 세대, 상태 버전
- 출처: NixOS, Nix, NixOS-WSL, Home Manager, NVM, uv, rustup의 공식 문서와 공식 소스
- 가정: x86_64 WSL 2, NixOS 26.05 신규 WSL 설치, 기본 사용자 `nixos`

## 2. 검증 결과

| 위치 | 항목 | 문제 | 수정 제안 | 상태 |
|---|---|---|---|---|
| 예제 README | 최초 `nixos-rebuild` | NixOS-WSL 이미지의 공식 초기 채널 갱신 단계가 빠짐 | `sudo nix-channel --update`를 이미지 bootstrap으로만 추가 | 반영 |
| 예제 README | 복원과 템플릿 초기화 | 복원 과정에서 새 `flake.lock`을 만들도록 읽힐 수 있음 | 기존 저장소 복원과 최초 잠금 파일 생성을 분리 | 반영 |
| 2장과 예제 README | 최초 시작 전제 | clone할 개인 저장소가 이미 있다고 가정해 첫 사용자는 진행할 수 없음 | WSL 자체 설치, GitHub 빈 저장소, SSH 인증, 예제의 `git init`, 첫 lock·push를 순서대로 추가 | 반영 |
| 2장·7장·예제 README | Git 없는 bootstrap | `github:` 입력은 비인증 REST API 403을 낼 수 있고 `git+https:` 우회는 외부 Git을 먼저 요구함 | 갱신한 root 채널의 `nix-shell -p git openssh`로 교체하고 두 오류와 `access-tokens` 대응 설명 | 반영 |
| Home Manager bootstrap | 외부 릴리스 URL을 직접 실행하면 잠금 파일과 다른 브랜치 HEAD를 받을 수 있음 | 잠긴 입력의 Home Manager 바이너리를 로컬 Flake 앱으로 노출 | 반영 |
| `nvm.nix` | non-Flake 입력 경로 | 입력 객체의 암시적 문자열 변환에 의존 | `inputs.nvm-src.outPath`를 명시 | 반영 |
| `common.nix` | 외부 ELF 실행 | nvm·uv·rustup이 내려받은 바이너리가 NixOS 로더 경로와 맞지 않을 수 있음 | `programs.nix-ld.enable = true`와 한계 설명 | 반영 |
| `flake.nix` | 네이티브 하드웨어 | WSL과 실제 하드웨어 모듈을 공유할 수 없음 | 추적된 하드웨어 파일이 있을 때만 `native` 출력 노출 | 반영 |
| `default.nix` | 상태 버전 | 릴리스 업데이트 때 함께 올린다고 오해할 수 있음 | 최초 설치 호환 기준이며 기존 값을 보존한다고 주석·본문에 명시 | 반영 |
| `hosts/wsl` | Windows PATH | `includePath = false`가 Windows 실행 파일 자동 탐색을 제거함 | 재현성을 위한 선택임을 설명하고 필요 시 `true`로 바꿀 수 있게 안내 | 최종 원고 반영 예정 |
| 전체 예제 | 실제 Nix 평가 | Windows 호스트에 Nix가 없고 설치된 WSL 배포판도 없음 | 정적 검증 범위를 기록하고 실제 적용 전 `build` 단계를 필수화 | 보류 |

## 3. 가정 확인

| 가정 | 타당성 | 근거 | 본문 반영 여부 |
|---|---|---|---|
| NixOS 26.05가 현재 안정 릴리스 | 타당 | NixOS 공식 26.05 발표와 Home Manager `release-26.05` 브랜치 | 반영 |
| NixOS-WSL 기본 사용자는 `nixos` | 타당 | 공식 설치 문서와 `wsl.defaultUser` 옵션 기본값 | 반영 |
| WSL 2.4.4 이상은 `.wsl` 파일을 설치 가능 | 타당 | NixOS-WSL 공식 설치 문서 | 반영 |
| Home Manager를 시스템과 독립적으로 쓸 수 있음 | 타당 | Home Manager 공식 설치 방식 세 가지와 standalone 권고 | 반영 |
| uv는 없는 Python을 자동 설치 가능 | 타당 | uv 공식 Python 버전 문서 | 반영 |
| nvm은 `.nvmrc`를 읽어 설치·선택 가능 | 타당 | NVM 공식 README | 반영 |
| rustup은 디렉터리 툴체인 파일을 우선 적용 | 타당 | rustup 공식 override 문서 | 반영 |
| 외부 패키지 관리자가 받은 ELF에 nix-ld가 유용 | 타당 | nix-ld 공식 설명의 npm·pip 등 제3자 바이너리 사례 | 반영 |

## 4. 실행/계산 검증

- 실행한 검사:
  - 모든 Markdown 파일의 코드 펜스 짝 검사
  - 모든 최종 챕터의 코드 블록 밖 H1 개수와 모든 상대 링크 대상 검사
  - 2장·7장·예제 README의 실제 bootstrap 명령이 모두 `nix-shell -p git openssh`인지 검색
  - 모든 Nix 파일의 중괄호와 대괄호 개수 대조
  - 예제에서 직접 설치하면 안 되는 Node.js, Python, Rust 툴체인, Docker 패키지 검색
  - 상대 경로로 참조한 Neovim dotfiles와 Nix 모듈의 존재 확인
  - 로컬 `nix`, `git`, `wsl` 명령 존재 여부와 설치된 WSL 배포판 확인
- 입력: `nixos-wsl-dev-environment/` 전체와 `assets/example-config/`의 Nix 파일
- 출력:
  - Markdown 18개 모두 코드 펜스 균형 정상, 깨진 상대 링크 0개
  - 챕터 8개 모두 코드 블록 밖 H1이 정확히 1개
  - 사용자 실행 경로의 Git bootstrap 명령 4곳이 모두 채널 기반 `nix-shell`로 일치
  - Nix 파일 7개 모두 중괄호·대괄호 개수 일치
  - 직접 런타임 패키지 검색 결과는 `$HOME/.cargo` 경로 두 곳뿐이며 `cargo` 패키지 선언은 없음
  - 참조한 로컬 경로 모두 존재
  - Windows 호스트에 Git과 `wsl.exe`는 있으나 Nix와 등록된 WSL 배포판은 없음
- 기대 결과: 정적 구조 오류와 범위 위반이 없고, 실제 Nix 평가 불가 사유가 명확할 것
- 실제 결과: 기대한 정적 조건 충족. Nix 평가·빌드·활성화는 수행하지 못함
- 확인 결과: 실제 NixOS에서 `nixos-rebuild build`와 `home-manager build`를 통과한 뒤에만 전환하도록 최종 절차를 구성한다.

## 5. 수식 검증

이 자료에는 수식이나 단위 계산이 없다. 소유권 표와 명령 순서만 검증 대상이다.

## 6. 출처 검증

| 주장 | 출처 | 출처 적합성 | 보강 필요 여부 |
|---|---|---|---|
| NixOS-WSL 설치 명령과 WSL 버전 조건 | NixOS-WSL 공식 설치 문서 | 1차 자료, 현재 문서 | 없음 |
| WSL Flake 모듈 출력 | NixOS-WSL 공식 Flake 안내 | 1차 자료 | 없음 |
| `wsl.interop.includePath` 의미 | NixOS-WSL 공식 옵션 문서 | 생성된 옵션 정의 | 없음 |
| 독립 실행형 Home Manager의 성격 | Home Manager 공식 소개·설치 문서 | 1차 자료 | 없음 |
| Home Manager 옵션명 | Home Manager `release-26.05` 공식 모듈 소스 | 사용 버전과 일치 | 없음 |
| 로컬 `home-manager` 앱의 실행 대상 | Home Manager `release-26.05/flake.nix` | `packages.default = hmPkg`를 확인하고 잠긴 입력의 바이너리를 앱으로 노출 | 없음 |
| 상태 버전을 임의로 올리지 않음 | NixOS 및 Home Manager 공식 문서 | 호환성 설명과 일치 | 없음 |
| 언어 버전 파일 동작 | uv, NVM, rustup 공식 문서 | 각 도구의 1차 자료 | 없음 |
| 최초 원격 저장소를 비워 두고 로컬 코드를 push | GitHub의 Adding locally hosted code 공식 문서 | 1차 자료 | 없음 |
| WSL의 Ed25519 공개 키 등록과 `ssh -T` 검증 | GitHub SSH 공식 문서 | 1차 자료 | 없음 |
| 비인증 GitHub API 한도는 공인 IP당 시간당 60회 | GitHub REST API rate limit 공식 문서 | 1차 자료 | 없음 |
| `nix-shell -p git` 임시 환경 | nix.dev 공식 튜토리얼 | 1차 자료 | 없음 |
| Nix GitHub fetcher 토큰 형식 | Nix 2.31.3 `access-tokens` 공식 참조 | 1차 자료 | 없음 |

## 7. 남은 위험

- 검증하지 못한 항목: Nix 2.31/NixOS 26.05에서의 전체 Flake 평가, 패키지 빌드, Home Manager 활성화, 실제 Node/Python/Rust 다운로드 바이너리 실행
- 추가 출처가 필요한 항목: 없음
- 독자에게 혼란을 줄 수 있는 항목: 제공 예제에는 개인화된 `flake.lock`과 실제 하드웨어 모듈이 없다. 첫 컴퓨터에서는 전자를 생성해 커밋하고, 네이티브 시스템까지 관리할 때만 후자를 해당 호스트에서 생성한다.
- 버전 또는 조건에 의존하는 항목: NixOS 26.05, Home Manager 26.05, NVM 0.40.4, WSL 2.4.4 이상 설치 명령
- 운영상 위험: `home-manager switch`가 기존 수동 설정 파일과 충돌할 수 있으므로 최초 적용 전에 오류가 지목한 파일을 백업해야 한다.

## 8. 검증 결론

- 초고에 바로 반영한 수정: 채널 bootstrap, 잠금 파일 절차 분리, non-Flake 입력의 `outPath` 명시
- 구조 퇴고 단계에서 다룰 수정: 8개 장으로 분할하고 각 장의 학습 목표·다음 장 연결 추가
- 최종 산출물 생성 전에 다시 확인할 수정: 모든 내부 링크, 코드 펜스, TODO 문자열, 예제와 본문의 명령 일치

## 9. 품질 점검

- [x] 정의와 용어가 출처와 일치한다.
- [x] 수식이 없는 자료임을 확인했다.
- [x] 코드 예제의 옵션과 구조를 공식 소스로 정적 검증했다.
- [x] 실행 검증을 하지 못한 범위와 이유가 명시되어 있다.
