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

`xdg.configFile`의 attribute 이름은 `xdg.configHome`에 상대적인 target이다.
`home.file`의 이름은 홈 디렉터리에 상대적인 target이다.

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

재귀 링크는 일부 하위 파일을 다른 선언과 조합할 때 유용하지만, 겹치는 target의
우선순위가 직관적이지 않을 수 있다. 작은 구성에서는 파일 단위 선언이 가장 명확하다.

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

이 링크는 Nix Store의 복사본이 아니라 실제 작업 트리를 가리킨다.

장점:

- 원본 수정이 즉시 보인다.
- 애플리케이션이 원본 파일에 써야 하는 경우 사용할 수 있다.

비용:

- generation만으로 파일 내용을 완전히 복원할 수 없다.
- 저장소 clone 위치를 바꾸면 링크 경로도 바꿔야 한다.
- 프로그램이 수정한 내용이 Git 작업 트리에 바로 나타난다.

정적이고 generation과 함께 롤백해야 하는 설정은 일반 `source`를 사용한다.
out-of-store link는 쓰기 가능성이 실제로 필요한 파일에만 제한한다.

## 4.7 부모 디렉터리 소유권 충돌

다음 두 선언은 충돌할 수 있다.

```nix
programs.neovim.enable = true;
xdg.configFile."nvim".source = ../../dotfiles/nvim;
```

프로그램 모듈이 `~/.config/nvim/init.lua`를 생성하는 동시에 dotfile 선언이
`~/.config/nvim` 전체를 하나의 링크로 소유하려 하기 때문이다.

해결 방법은 부모 디렉터리를 통째로 연결하지 않고 하위 경로의 소유권을 나누는 것이다.

```nix
programs.neovim.enable = true;
xdg.configFile."nvim/lua".source = ../../dotfiles/nvim/lua;
xdg.configFile."nvim/stylua.toml".source =
  ../../dotfiles/nvim/stylua.toml;
```

어떤 모듈이 어느 최종 파일을 생성하는지 먼저 확인한다.
기존 매뉴얼의
[`lazyvim.nix`](../nixos-wsl-dev-environment/assets/example-config/modules/home/lazyvim.nix)는
`init.lua`와 하위 dotfiles의 소유권을 나눈 실제 예제다.

## 4.8 기존 파일 충돌

Home Manager는 관리되지 않던 기존 파일을 자동으로 덮어쓰지 않는다. activation 중
다음과 비슷한 오류가 발생한다.

```text
Existing file '/home/nixos/.config/example-app/config.toml' is in the way
```

가장 안전한 해결 순서는 다음과 같다.

1. 기존 파일의 내용을 확인한다.
2. 유지할 설정을 Home Manager 옵션이나 dotfile 원본으로 옮긴다.
3. 기존 파일을 홈 디렉터리 밖의 백업 위치로 이동한다.
4. `home-manager switch`를 다시 실행한다.
5. 새 설정을 확인한 뒤 백업을 정리한다.

standalone Home Manager는 한 번의 전환에서 기존 파일에 확장자를 붙여 이동할 수 있다.

```console
$ home-manager switch -b hm-backup --flake .#nixos
```

이미 같은 `.hm-backup` 파일이 있으면 activation은 다시 중단된다. 이 옵션을 평상시
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

## 요약

- 프로그램 모듈 옵션을 우선하고 부족한 부분만 dotfiles로 배치한다.
- `xdg.configFile`은 `~/.config`, `home.file`은 `$HOME` 기준 파일을 관리한다.
- 일반 source는 generation과 함께 롤백되고, out-of-store link는 작업 트리를 직접
  가리킨다.
- 부모 디렉터리와 하위 파일의 소유자를 겹치게 만들지 않는다.
- 충돌은 `force`로 숨기지 말고 기존 데이터를 검토한 뒤 소유권을 이전한다.

## 공식 참고 자료

- [Home Manager의 안전한 dotfile 전환](https://nix-community.github.io/home-manager/usage/dotfiles.html)
- [`home.file` 옵션](https://nix-community.github.io/home-manager/options/home-manager/home.html)
- [`xdg.configFile` 옵션](https://nix-community.github.io/home-manager/options/home-manager/xdg.html)

[← 3장](./03-packages-and-programs.md) · [목차](./index.md) · [5장: 빌드, 적용, 업데이트, 롤백 →](./05-apply-and-rollback.md)
