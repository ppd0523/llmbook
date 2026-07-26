---
title: 최종 산출물 구성과 출판 변환 검수
version: 1.0
status: final
owner: agent
updated: 2026-07-24
target_reader: Nix 기초는 알지만 Flake는 처음인 개발자
topic: Nix Flake 입문 MkDocs 출판
---

# 최종 산출물 구성과 출판 변환 검수

## 1. 최종 산출물 계획

- 기준 원고 Markdown: `_work/07_final.md`와 확정된 챕터 원고 집합
- 원본 버전: 1.0
- 최종 산출물 형식: MkDocs 챕터형 Markdown
- 최종 산출물 경로: `docs/nix-flakes/`
- MkDocs 책 폴더명: `nix-flakes`
- 챕터 파일명 규칙: `NN-<chapter-slug>.md`
- 챕터 파일 배치: 책 폴더 바로 아래
- 보조 산출물: `assets/flake-greeter/`
- 구성 또는 변환 도구: MkDocs Material 9.7.6
- 구성 또는 변환 명령: `uv run --no-cache --with-requirements requirements.txt mkdocs build --strict`
- 구성 또는 변환 일시: 2026-07-24

## 2. 산출 결과

| 형식 | 파일 | 상태 | 비고 |
|---|---|---|---|
| Chapter Markdown | `index.md`, `01-*.md`~`06-*.md` | 완료 | 6개 챕터 |
| Example Flake | `assets/flake-greeter/` | 완료 | flake, lock, README |
| HTML | `site/` | 검증용 생성 | Git 제외 대상 |
| PDF | 해당 없음 | 미생성 | 요청 범위 아님 |
| ePub | 해당 없음 | 미생성 | 요청 범위 아님 |
| PPT/PPTX | 해당 없음 | 미생성 | 요청 범위 아님 |

## 3. 공통 검수

- [x] `01_scope.md`의 최종 형식과 실제 결과가 일치한다.
- [x] 자료 폴더 루트에서 `index.md`와 6개 챕터가 식별된다.
- [x] 번호가 붙은 내부 단계 파일은 `_work/` 아래에 있다.
- [x] 최종 산출물에 내부 작업 메모가 없다.
- [x] 최종 산출물에 미완료 표지가 없다.
- [x] 제목 계층과 코드 fence가 유지된다.
- [x] MkDocs strict build에서 내부 링크가 통과했다.
- [x] 외부 링크는 공식 Nix/Nixpkgs 문서를 우선했다.
- [x] 코드 블록에 언어 식별자가 있다.
- [x] 표가 과도하게 넓지 않다.
- [x] 참고문헌과 버전 기준이 유지된다.

## 4. MkDocs 챕터형 Markdown 검수

- [x] 책이 `docs/nix-flakes/` 아래에 있다.
- [x] 사이트 진입점과 책 진입점이 있다.
- [x] 챕터 파일이 책 폴더 바로 아래에 있다.
- [x] 챕터 파일명이 두 자리 번호와 kebab-case를 사용한다.
- [x] 반복되는 `chapter.md` 파일명을 사용하지 않는다.
- [x] 파일명 정렬 순서와 읽는 순서가 일치한다.
- [x] `mkdocs.yml`에 수동 `nav`를 추가하지 않았다.
- [x] 챕터 파일명과 H1 제목이 같은 주제를 가리킨다.
- [x] 챕터 간 링크가 상대 `.md` 경로를 사용한다.
- [x] asset 링크가 정상 동작한다.
- [x] `_work/`는 `exclude_docs`로 게시 대상에서 제외된다.
- [x] 각 챕터가 학습 목표, 본문, 실습, 요약을 가진다.

## 5. 실행 예제 검수

- [x] Nix 2.34.8로 `flake.lock`을 생성했다.
- [x] `nix flake show`가 네 system 출력을 평가했다.
- [x] `nix flake check`가 x86_64-linux의 package와 greeting을 build했다.
- [x] `nix develop --command cowsay ...`가 실행됐다.
- [x] `nix run ...`이 application 메시지를 출력했다.
- [x] `--all-systems --no-build`가 네 system의 schema를 평가했다.
- [x] `pkgs.nixfmt`가 네 system에서 derivation으로 평가됐다.

## 6. 발견된 문제

| 위치 | 문제 | 처리 방향 | 상태 |
|---|---|---|---|
| 다중 system | Nixpkgs 26.05가 마지막 `x86_64-darwin` 지원 release라는 경고 | 5장에 버전 의존성 명시 | 반영 |
| 실제 build | Darwin과 aarch64는 현재 host에서 build하지 않음 | 플랫폼별 CI 필요성을 본문과 review에 명시 | 반영 |

## 7. 최종 결론

- 배포 가능 최종 산출물: `docs/nix-flakes/index.md`와 6개 챕터
- 배포 가능 보조 형식: `assets/flake-greeter/` 완성형 Flake
- 배포 보류 형식: 없음
- 추가 작업: 없음
