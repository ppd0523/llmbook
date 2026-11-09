---
title: Home Manager 가이드 기준 원고 확정 기록
---

# 기준 원고 확정

기준 원고는 이 파일이 아니라 다음 MkDocs 진입점과 챕터 본문이다. 이 파일은 그 구성을 확정한 기록이다.

- `index.md`
- `01-mental-model.md`
- `02-configuration-structure.md`
- `03-packages-and-programs.md`
- `04-dotfiles.md`
- `05-apply-and-rollback.md`
- `06-troubleshooting.md`

모든 챕터는 하나의 `#` 제목, 상대 Markdown 링크, 언어 식별자가 있는 코드 블록을 사용한다. 내부 작업 메모와 미검증 표시는 최종 챕터에 포함하지 않는다.

## 점검 결과

- 각 장의 학습 목표마다 본문 절과 연습 문항이 대응한다. 대응표는 `03_outline.md`의 연습과 피드백 표에 있다.
- 예제 구성을 가리키는 이름은 "예제 구성", 상위 자료는 "NixOS-WSL 매뉴얼"로 부른다. "프로젝트"는 1.2절의 세 번째 소유권 계층만 뜻한다.
- 예제 구성 파일을 줄여 보인 코드(2.5절 `default.nix`, 3.7절 `programs.nix`)는 발췌임과 생략한 내용을 본문에 밝힌다.
- 버전에 따라 달라지는 오류 문구에는 Home Manager 26.05 또는 Nix 2.34 기준을 표시한다.
