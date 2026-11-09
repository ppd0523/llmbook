# 4. Home Manager 옵션과 dotfiles 함께 사용하기

## 학습 목표

1. Home Manager 옵션, `home.file`, `xdg.configFile`의 사용 시점을 구분한다.
2. store link와 out-of-store link의 차이를 이해한다.
3. 기존 파일 충돌을 데이터 손실 없이 해결한다.

## 4.1 dotfiles는 필수가 아니다

Home Manager 프로그램 모듈만으로 설정할 수 있다면 별도 dotfile이 필요 없다.

```nix
programs.git = {
  enable = true;
  settings.init.defaultBranch = "main";
};
```

이 방식은 패키지와 설정의 관계가 한 모듈에 드러나고, 옵션 타입 검사를 받을 수 있다.
반면 다음 경우에는 파일 배치가 더 단순하다.

- Home Manager 모듈이 지원하지 않는 설정 파일
- 기존 애플리케이션 설정을 거의 그대로 재사용할 때
- 설정 언어의 도구와 formatter를 계속 사용해야 할 때
- Nix 외의 환경과 같은 원본을 공유할 때

권장 원칙은 **Home Manager 옵션을 먼저 사용하고, 표현할 수 없는 부분만 dotfiles로
배치하는 것**이다.

## 4.2 선택 기준

```text
전용 programs.* 옵션이 필요한 설정을 표현하는가?
  ├─ 예 → 전용 옵션 사용
  └─ 아니오
       ├─ ~/.config 아래 파일인가? → xdg.configFile
       └─ 그 밖의 $HOME 아래 파일인가? → home.file
```

같은 최종 경로를 프로그램 모듈과 파일 선언이 동시에 만들지 않도록 한다.

## 4.3 설정 내용을 Nix에서 생성

짧고 단순한 파일은 `text`로 만들 수 있다.

```nix
{
  xdg.enable = true;

  xdg.configFile."example-app/config.toml".text = ''
    theme = "dark"
    check_updates = false
  '';
}
```

결과는 기본적으로 다음 위치에 배치된다.

```text
~/.config/example-app/config.toml
```

`xdg.configFile`의 attribute 이름은 `xdg.configHome`(기본값 `~/.config`)에 상대적인
target이다. `home.file`의 이름은 홈 디렉터리에 상대적인 target이다.

`xdg.enable = true`는 `XDG_CONFIG_HOME` 같은 XDG 디렉터리 환경 변수를 session에 설정한다.
`xdg.configFile` 자체는 이 옵션 없이도 `~/.config` 아래에 파일을 만든다. 예제 구성은
`lazyvim.nix`에서 이 옵션을 켜며, 1.5절에서 본 것처럼 zsh 설정 위치에도 영향을 준다.

```nix
home.file.".hushlogin".text = "";
```

## 4.4 저장소의 파일을 source로 사용

설정 원본을 별도 파일로 유지하려면 저장소에 dotfile을 둔다.

```text
~/.config/nixos/
├── modules/home/example-app.nix
└── dotfiles/example-app/config.toml
```

`modules/home/example-app.nix`에서 상대 경로로 연결한다.

```nix
{ ... }:
{
  xdg.enable = true;
  xdg.configFile."example-app/config.toml".source =
    ../../dotfiles/example-app/config.toml;
}
```

일반 `source`는 평가 과정에서 원본을 Nix Store로 가져오고 Home Manager가 그 결과를
링크한다. 장점은 generation이 정확한 원본을 참조하여 롤백 가능하다는 점이다.
dotfile을 수정한 뒤에는 다시 `build`와 `switch`해야 반영된다.

## 4.5 디렉터리 전체와 재귀 링크

source가 디렉터리일 때 기본 동작은 대상 디렉터리 하나를 source 디렉터리에 연결하는
것이다.

```nix
xdg.configFile."example-app".source = ../../dotfiles/example-app;
```

`recursive = true`를 사용하면 대상 디렉터리를 만들고 각 leaf 파일을 개별적으로
연결한다.

```nix
xdg.configFile."example-app" = {
  source = ../../dotfiles/example-app;
  recursive = true;
};
```

재귀 링크는 일부 하위 파일을 다른 선언과 조합할 때 유용하지만, 겹치는 target은
피하는 편이 안전하다. 정확히 같은 target을 두 번 선언하면 평가 단계에서
`Conflicting managed target files` 오류가 난다. 반면 재귀
링크가 제공하는 `example-app/config.toml`과 일반 파일 선언이 겹치면, Home Manager는
기본적으로 재귀 링크 쪽을 유지하고 일반 파일 선언을 무시한다. 의도한 설정이 조용히
적용되지 않을 수 있으므로, 작은 구성에서는 파일 단위 선언이 가장 명확하다.

## 4.6 out-of-store link

프로그램이 파일을 직접 수정해야 하거나 Git 작업 트리 변경을 rebuild 없이 바로
읽어야 한다면 out-of-store link를 고려한다.

```nix
{ config, ... }:
let
  configRoot =
    "${config.home.homeDirectory}/.config/nixos/dotfiles/example-app";
in
{
  xdg.configFile."example-app/config.toml".source =
    config.lib.file.mkOutOfStoreSymlink "${configRoot}/config.toml";
}
```

이 링크는 Nix Store의 복사본이 아니라 실제 작업 트리를 가리킨다. 경로를
`../../dotfiles/...` 같은 Nix 경로 값이 아니라 `"${config.home.homeDirectory}/..."`
문자열로 쓰는 이유가 여기에 있다. Nix 경로 값은 평가할 때 store로 복사되므로, 그것을
넘기면 링크가 다시 store 복사본을 가리키게 된다.

장점:

- 원본 수정이 즉시 보인다.
- 애플리케이션이 원본 파일에 써야 하는 경우 사용할 수 있다.

비용:

- generation만으로 파일 내용을 완전히 복원할 수 없다.
- 저장소 clone 위치를 바꾸면 링크 경로도 바꿔야 한다.
- 프로그램이 수정한 내용이 Git 작업 트리에 바로 나타난다.

앱이 이 링크를 통해 파일에 쓸 수 있는 것은 링크 끝의 작업 트리 파일이 원래 사용자가 쓸
수 있는 일반 파일이기 때문이다. Home Manager가 따로 쓰기 권한을 주는 것은 아니다. 일반 `source`와 out-of-store link를 같은 target에
섞어 선언하지 않는다.

정적이고 generation과 함께 롤백해야 하는 설정은 일반 `source`를 사용한다.
out-of-store link는 쓰기 가능성이 실제로 필요한 파일에만 제한한다.

## 4.7 부모 디렉터리 소유권 충돌

다음 두 선언은 같은 디렉터리를 두 곳이 소유하려 한다.

```nix
programs.neovim = {
  enable = true;
  initLua = builtins.readFile ../../dotfiles/nvim/init.lua;
};
xdg.configFile."nvim".source = ../../dotfiles/nvim;
```

`programs.neovim`은 `~/.config/nvim/init.lua`를 생성하고, 파일 선언은 `~/.config/nvim`
전체를 store 디렉터리 하나로 연결한다. Home Manager는 관리 파일 트리를 build할 때 부모
링크 안에 하위 파일을 만들 수 없다. 결과는 부모 링크의 종류와 source 내용에 따라 갈린다.

| 부모 링크 | 결과 |
|---|---|
| out-of-store link(4.6절) | build가 `Error installing file '.config/nvim/init.lua' outside $HOME`로 실패한다. 링크가 build 밖의 작업 트리를 가리키기 때문이다 |
| 일반 `source`, 그 안에 하위 파일이 없음 | 같은 오류로 build가 실패한다 |
| 일반 `source`, 그 안에 같은 이름의 하위 파일이 있음 | build는 성공하지만 하위 파일 선언은 무시되고 부모 source의 파일이 쓰인다 |

위 선언은 일반 `source`이고 예제 구성의 `dotfiles/nvim`에는 `init.lua`가 있으므로 세 번째
경우에 해당한다. 같은 디렉터리를 out-of-store link로 연결하면 첫 번째 경우가 된다.
세 번째 경우가 가장 위험하다. 오류 없이 의도한 설정만 빠지기 때문이다. 4.5절의 재귀
링크가 겹칠 때와 같은 결과다.

해결 방법은 부모 디렉터리를 통째로 연결하지 않고 하위 경로의 소유권을 나누는 것이다.

```nix
programs.neovim.enable = true;
xdg.configFile."nvim/lua".source = ../../dotfiles/nvim/lua;
xdg.configFile."nvim/stylua.toml".source =
  ../../dotfiles/nvim/stylua.toml;
```

어떤 모듈이 어느 최종 파일을 생성하는지 먼저 확인한다. 예제 구성의
[`lazyvim.nix`](../nixos-wsl-dev-environment/assets/example-config/modules/home/lazyvim.nix)는
`init.lua`를 `programs.neovim`에 맡기고 하위 경로만 연결한 실제 예제다. 다만 그 파일은
LazyVim이 `lazy-lock.json`을 직접 고쳐 써야 하므로 위의 일반 `source` 대신 4.6절의
out-of-store link를 쓴다. 그 상태에서 `nvim` 디렉터리 전체를 링크하면 표의 첫 번째
경우가 되어 build가 실패한다. 예제 구성 README가 경고하는 오류가 이것이다.

## 4.8 기존 파일 충돌

Home Manager는 관리되지 않던 기존 파일을 자동으로 덮어쓰지 않는다. activation은 파일을
바꾸기 전에 모든 target을 검사하고, 충돌이 있으면 해결 방법 안내와 함께 다음 오류를
출력한 뒤 중단한다(Home Manager 26.05 기준).

```text
Existing file '/home/nixos/.config/example-app/config.toml' would be clobbered
```

기존 파일의 내용이 새로 배치할 파일과 정확히 같으면 충돌로 보지 않고 경고만 출력한 뒤
그 파일을 건너뛴다.

가장 안전한 해결 순서는 다음과 같다.

1. 기존 파일의 내용을 확인한다.
2. 유지할 설정을 Home Manager 옵션이나 dotfile 원본으로 옮긴다.
3. 기존 파일을 Home Manager가 관리하지 않는 위치로 옮긴다. 예:
   `mv ~/.config/example-app/config.toml ~/example-app-config.before-hm`
4. `home-manager switch`를 다시 실행한다.
5. 새 설정을 확인한 뒤 백업을 정리한다.

3단계에서 복사(`cp`)가 아니라 이동(`mv`)하는 이유는 원래 자리를 비워야 충돌이 풀리기
때문이다. 백업은 어떤 선언의 target도 아닌 경로에 두면 된다.

standalone Home Manager는 한 번의 전환에서 기존 파일에 확장자를 붙여 이동할 수 있다.

```console
$ home-manager switch -b hm-backup --flake .#nixos
```

이 경우 기존 파일은 `config.toml.hm-backup`으로 옮겨진다. 이미 같은 이름의 백업이
있으면 `Existing file '....hm-backup' would be clobbered by backing up '...'` 오류로
activation이 다시 중단된다. 이 옵션은 관리되지 않은 일반 파일과 디렉터리를 옮기는 용도다. 충돌 target이 기존 symbolic link라면 원본을
확인한 뒤 직접 옮기거나, 정말 버려도 되는 target에만 `force`(4.9절)를 사용한다. `-b`를 평상시
모든 `switch`에 자동으로 붙이기보다 초기 마이그레이션에서 검토 후 사용한다.

## 4.9 force를 기본값으로 쓰지 않는다

파일 옵션에는 `force = true`가 있지만 대상 파일이나 링크를 조건 없이 바꿀 수 있다.

```nix
home.file.".config/example-app/config.toml" = {
  source = ../../dotfiles/example-app/config.toml;
  force = true;
};
```

이 설정은 로컬 변경을 조용히 삭제할 수 있다. 자동 생성되어 버려도 되는 경로라는
근거가 있을 때만 개별 target에 제한하여 사용한다. 일반적인 충돌은 백업하고 소유권을
정리하는 방식으로 해결한다.

## 4.10 비밀과 변경 가능한 상태

다음 자료는 일반 dotfiles source나 `text`에 넣지 않는다.

- SSH 개인 키
- Git hosting, npm, PyPI, cloud access token
- 비밀번호와 복구 코드
- 조직 인증서의 개인 키

Nix Store는 시스템의 다른 사용자가 경로를 알면 읽을 수 있는 경우가 있고, Git
이력에서 삭제한 비밀도 과거 commit에 남는다. 이 가이드는 비밀 관리 체계를 제공하지
않는다.

cache, history, database처럼 프로그램이 계속 변경하는 상태도 정적 store source로
관리하지 않는다. 복원 가능한 선언과 실행 중 생성되는 데이터를 분리한다.

## 연습문제

1. 다음 세 파일마다 두 가지를 고르고 이유를 쓴다. 세 프로그램 모두 Home Manager 전용
   모듈이 없다고 가정한다.
   - 선언 옵션: `xdg.configFile` / `home.file`
   - source 방식: 일반 `source`(store) / out-of-store link

   대상 파일:

   - ① 레지스트리 주소만 적고 토큰은 쓰지 않는 `~/.npmrc`
   - ② 정적인 `~/.config/example-app/config.toml`
   - ③ 앱이 실행 중에 직접 고쳐 쓰고, 그 변경을 Git으로 관리하고 싶은
     `~/.config/editor-x/settings.json`
2. `dotfiles/example-app/`에 `config.toml`과 `theme.toml`이 있다. 다음 선언으로
   `switch`하면 `~/.config/example-app/config.toml`의 내용은 무엇이 되는가?

   ```nix
   xdg.configFile."example-app" = {
     source = ../../dotfiles/example-app;
     recursive = true;
   };
   xdg.configFile."example-app/config.toml".text = ''
     theme = "light"
   '';
   ```

3. 2번에서 `recursive = true`를 지우면 결과가 달라지는가? `dotfiles/example-app/`에
   `config.toml`이 없다면 어떻게 되는가?
4. 처음 `switch`할 때 activation이
   `Existing file '/home/nixos/.config/example-app/config.toml' would be clobbered`로
   중단됐다. 그 파일에는 몇 달 동안 직접 고친 설정이 있다. 데이터를 잃지 않는 처리
   순서를 쓰고, 이 상황에서 `force = true`를 쓰지 않는 이유를 설명한다.

??? note "정답 확인"
    1번: ① `home.file.".npmrc"` + 일반 `source`. `~/.config` 밖의 `$HOME` 파일이고
    정적이다. `npm login`처럼 토큰을 써 넣는 도구를 쓴다면 이 파일은 상태가 되므로
    선언하지 않는다. ② `xdg.configFile` + 일반 `source`. 정적 설정이므로 generation과
    함께 롤백되는 store link가 알맞다. ③ `xdg.configFile` + out-of-store link. store
    파일은 읽기 전용이라 앱이 쓸 수 없다. 그 내용은 generation 롤백으로 되돌아가지 않고
    Git으로 관리한다. Git으로 관리할 필요가 없다면 선언하지 않고 상태로 남기는 것도 맞는
    답이다(1.4절).

    2번: `dotfiles/example-app/config.toml`의 내용이다. 재귀 링크가 제공하는 파일과 일반
    파일 선언이 겹치면 재귀 링크 쪽이 유지되고 `text` 선언은 오류 없이 무시된다.

    3번: 달라지지 않는다. 부모 디렉터리 전체가 store 디렉터리 하나로 연결되고, source에
    있는 `config.toml`이 쓰이며 `text` 선언은 무시된다. source에 `config.toml`이 없다면
    build가 `Error installing file '.config/example-app/config.toml' outside $HOME`로
    실패한다. 어느 경우든 해결은 겹치는 선언을 없애는 것이다.

    4번: 파일 내용을 확인하고, 유지할 설정을 Home Manager 옵션이나 `dotfiles/` 원본으로
    옮긴다. 기존 파일을 관리하지 않는 위치로 `mv`하거나 `home-manager switch -b hm-backup
    --flake .#nixos`로 백업하게 한 뒤 다시 `switch`하고, 새 설정을 확인한 다음 백업을
    정리한다. `force = true`는 기존 파일을 백업 없이 바꾸므로 직접 고친 설정을 잃는다.

## 요약

- 프로그램 모듈 옵션을 우선하고 부족한 부분만 dotfiles로 배치한다.
- `xdg.configFile`은 `~/.config`, `home.file`은 `$HOME` 기준 파일을 관리한다.
- 일반 source는 generation과 함께 롤백되고, out-of-store link는 작업 트리를 직접
  가리킨다.
- 부모 디렉터리와 하위 파일의 소유자를 겹치게 만들지 않는다. 겹치면 build가 실패하거나
  한쪽 선언이 조용히 무시된다.
- 충돌은 `force`로 숨기지 말고 기존 데이터를 검토한 뒤 소유권을 이전한다.

## 공식 참고 자료

- [Home Manager의 안전한 dotfile 전환](https://nix-community.github.io/home-manager/usage/dotfiles.html)
- [`home.file` 옵션](https://nix-community.github.io/home-manager/options/home-manager/home.html)
- [`xdg.configFile` 옵션](https://nix-community.github.io/home-manager/options/home-manager/xdg.html)

[← 3장](./03-packages-and-programs.md) · [목차](./index.md) · [5장: 빌드, 적용, 업데이트, 롤백 →](./05-apply-and-rollback.md)
