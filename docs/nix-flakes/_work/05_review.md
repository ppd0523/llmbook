---
title: 기술 검증
version: 1.0
status: final
owner: agent
updated: 2026-07-24
target_reader: Nix 기초는 알지만 Flake는 처음인 개발자
topic: Nix Flake 예제와 명령 검증
---

# 기술 검증

## 1. 검증 대상

- 정의: Flake, input, output, lock file, package, app, installable
- 코드: `assets/flake-greeter/flake.nix`
- 출력: packages, apps, devShells, formatter, checks의 네 system 구조
- 명령: lock, show, develop, run, check, all-systems 평가
- 출처: Nix 2.34와 Nixpkgs 26.05 공식 문서
- 문서: Markdown 제목, 링크, 코드 fence, MkDocs strict build

## 2. 검증 환경

- 실행일: 2026-07-24
- Nix 실행 환경: NixOS WSL
- Nix: 2.34.8
- Nixpkgs input: `nixos-26.05`
- 잠긴 revision: `b3fe9581c9061c749abef42b6d4ee7b7c05c33fa`
- formatter: `nixfmt-1.4.0`
- 문서 도구: MkDocs Material 9.7.6

## 3. 검증 결과

| 위치 | 항목 | 결과 | 상태 |
|---|---|---|---|
| `flake.lock` | Nixpkgs input 잠금 | Nix 2.34.8로 생성, revision과 narHash 기록 | 통과 |
| `packages` | 네 system 평가 | 네 system 모두 derivation 평가 | 통과 |
| `apps` | app schema | 네 system 모두 `type`과 `program` 확인 | 통과 |
| `devShells` | `cowsay` 설치 | x86_64-linux에서 shellHook과 직접 명령 실행 | 통과 |
| `formatter` | `pkgs.nixfmt` | 네 system derivation 평가 | 통과 |
| `checks` | package와 greeting | x86_64-linux에서 두 check 실제 build | 통과 |
| 전체 system | `--all-systems --no-build` | 네 system의 모든 표준 출력 평가 | 통과 |
| app | `nix run` | `verified in NixOS WSL` cowsay 출력 | 통과 |
| 문서 | MkDocs strict build | 9.7.6에서 build 성공 | 통과 |
| 작업 트리 | `git diff --check` | whitespace 오류 없음 | 통과 |

## 4. 실행 검증

### Flake 구조

```console
nix flake show path:/mnt/c/Users/dhyeon/llmBook/docs/nix-flakes/assets/flake-greeter
```

결과: apps, checks, devShells, formatter, packages의 네 system 출력이 평가됐다.

### 현재 system 검사

```console
nix flake check path:/mnt/c/Users/dhyeon/llmBook/docs/nix-flakes/assets/flake-greeter -L
```

결과: x86_64-linux package와 greeting check가 build됐고 `all checks passed`가 출력됐다.

### 전체 system 평가

```console
nix flake check path:/mnt/c/Users/dhyeon/llmBook/docs/nix-flakes/assets/flake-greeter \
  --all-systems --no-build
```

결과: x86_64-linux, aarch64-linux, x86_64-darwin, aarch64-darwin의 package, app,
devShell, formatter, check derivation이 모두 평가됐다.

### 개발 셸과 app

```console
nix develop path:/mnt/c/Users/dhyeon/llmBook/docs/nix-flakes/assets/flake-greeter \
  --command cowsay "development shell verified"

nix run path:/mnt/c/Users/dhyeon/llmBook/docs/nix-flakes/assets/flake-greeter \
  -- "verified in NixOS WSL"
```

결과: 두 명령 모두 cowsay ASCII 메시지를 출력하고 종료 상태 0을 반환했다.

## 5. 출처 검증

| 주장 | 출처 | 적합성 |
|---|---|---|
| Flake는 input과 output의 표준 구조를 제공 | nix.dev Flakes | 공식 개념 문서 |
| `nix develop`의 기본 출력은 `devShells.<system>.default` | Nix 2.34 reference | 명령 reference |
| app은 `type`과 Store의 `program` 경로를 가짐 | Nix 2.34 `nix run` | 명령 reference |
| 기존 input 갱신은 `nix flake update` 사용 | Nix 2.34 lock/update reference | 폐기 명령 대체 확인 |
| 현재 stable formatter 속성은 `pkgs.nixfmt` | Nixpkgs stable release notes | 버전 변경 근거 |
| `cowsay`는 Nixpkgs에서 사용 가능한 예제 package | nix.dev 첫 단계 | 공식 튜토리얼 |

## 6. 발견 사항과 반영

| 발견 | 반영 |
|---|---|
| `x86_64-darwin`은 Nixpkgs 26.05가 마지막 지원 release라는 평가 경고 | 5장에 release 이동 시 지원 목록 재검토 안내 추가 |
| 다른 system의 build는 현재 x86_64-linux host에서 실행하지 않음 | 전체 system 평가는 `--no-build`, 실제 build는 플랫폼별 CI로 구분 |
| 병렬 app/dev shell 검증 중 Nix eval cache SQLite busy 메시지가 한 번 발생했으나 ignored 처리 | 예제 기능과 무관하며 각 명령 종료 상태 0 확인 |
| MkDocs build가 `site/`를 생성 | `site/`는 기존 `.gitignore` 대상이며 최종 산출물에 포함하지 않음 |

## 7. 남은 위험

- aarch64-linux와 두 Darwin 출력은 평가됐지만 해당 실제 머신에서 build하지 않았다.
- 외부 Nixpkgs branch는 움직이지만 예제의 `flake.lock`이 검증한 revision을 고정한다.
- 다음 Nix/Nixpkgs release에서는 experimental command와 platform 지원을 다시 확인해야 한다.

## 8. 검증 결론

- 핵심 Flake 코드와 x86_64-linux 실행 경로는 실제 Nix 2.34.8에서 검증됐다.
- 모든 선언 system의 output schema는 평가됐다.
- 플랫폼별 실제 build 범위는 본문에서 과장하지 않고 구분했다.
- 최종 문서와 예제에 미검증 표시나 내부 TODO를 남기지 않는다.

## 9. 품질 점검

- [x] 정의와 용어가 출처와 일치한다.
- [x] 코드와 명령 예제가 실행 검증됐다.
- [x] 현재 system의 package, app, dev shell, check가 검증됐다.
- [x] 다른 system의 검증 한계가 명시되어 있다.
