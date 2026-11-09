---
title: Home Manager 가이드 기술 검토
---

# 검토 결과

## 검증 환경

- NixOS-WSL 26.05, Nix 2.34.7, Home Manager 26.05(release branch rev `3cd22efe`, Nixpkgs rev `8eeec934`).
- 사용자 설정과 홈 디렉터리를 바꾸지 않으려고 같은 rev를 고정한 임시 Flake를 `/tmp`에 만들어 `home-manager build`만 실행했다. activation 동작은 같은 rev의 소스로 확인했다.

## build로 확인한 항목

- 3장 `programs.git`(`settings`, `includes`), `programs.bat.config`, zsh·Starship·direnv·fzf 설정이 26.05에서 평가·build된다. 생성된 Git 설정의 조건부 include는 `includeif.gitdir:~/work/.path ~/.config/git/work`로 읽힌다.
- `home.sessionVariables`에서 `config.home.sessionVariables.TOOL_HOME`을 참조하면 완성된 문자열이 생성된다. `home.sessionPath`는 `PATH` 앞에 붙는다.
- `hm-session-vars.sh`의 `__HM_SESS_VARS_SOURCED` 가드와 `.zshenv`의 source 줄을 확인했다. 3·5·6장의 확인 방법(alias는 `exec zsh`, session 변수는 새 터미널)은 이 동작에 근거한다.
- 겹친 파일 선언 세 가지(같은 target, 재귀 링크와 하위 파일, 부모 링크와 하위 파일)와 `programs.neovim` + `nvim` 부모 링크의 결과를 build로 재현했다. 4.5·4.7·6.7절과 4장 문제 2·3의 정답은 이 결과와 일치한다.
- 6장의 `nix flake show`, `nix eval ... builtins.attrNames`, 없는 output, 없는 옵션, 추적되지 않은 파일 출력은 실제 실행 결과다.
- `result` 링크의 `home-path/bin`, `home-files` 구조와 `home-manager generations` 출력 형식을 확인했다.
- `xdg.enable = true`와 `stateVersion = "26.05"`에서 zsh 설정은 `~/.config/zsh/.zshrc`·`.zshenv`에 생기고 홈의 `~/.zshenv`는 그것을 source한다. 검증 기기의 실제 홈에도 `~/.zshrc`가 없다. 1.5·3.10·6.10절과 3장 실습 4의 경로는 이 결과를 따른다.
- `programs.neovim`과 `nvim` 부모 링크를 함께 선언한 세 경우를 build했다. 부모가 out-of-store link이면 `init.lua`가 있어도 `outside $HOME`으로 실패한다(예제 구성 README의 설명과 같다). 일반 `source`이면 `init.lua`가 없을 때 같은 오류로 실패하고, 있을 때는 build가 성공하며 부모 source의 `init.lua`가 쓰인다. 4.7절 표와 일치한다.

## 소스로 확인한 항목

- activation 충돌 검사(`check-link-targets.sh`): 오류 문구, 내용이 같은 파일 건너뛰기, `-b` 백업 충돌, HM이 소유하지 않은 symlink 처리.
- `home-manager switch --rollback`은 Home Manager 프로필의 직전 generation을 활성화한다. 25.11에서 추가되었다.
- 5장의 bootstrap 명령은 예제 구성의 `apps.<system>.home-manager`와 대조했다.

## 실행하지 않은 항목

- `switch`, `--rollback`, `-b` 백업과 `wsl --terminate`는 실제 사용자 환경을 바꾸므로 실행하지 않았다. 3·5장 실습 과제의 `switch` 이후 기대 출력은 build 결과와 소스에서 추론했다.
- 5.10절 NixOS 모듈 방식 예시는 비교용 발췌이며 build하지 않았다.
