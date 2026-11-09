# 여러 챕터가 공유하는 예제 프로젝트는 `assets/<project-slug>/`에 둔다

책 자산은 한 챕터 전용이면 `assets/<chapter-slug>/`, 여러 챕터가 쓰는 낱개 파일이면 `assets/common/`에 둔다. 여러 챕터가 함께 쓰는 예제 프로젝트 한 벌(예: `nix-flakes/assets/flake-greeter`, `nix-cpp-cyclonedds/assets/cyclonedds-cross-demo`)은 어느 쪽에도 맞지 않으므로 `assets/<project-slug>/`를 허용한다.

## 고려한 대안

하나는 예제를 가장 많이 참조하는 챕터의 slug에 귀속시키는 것이다. 여러 챕터가 참조하는 예제에 한 챕터의 이름을 붙이면 "이 예제는 그 챕터의 것"이라는 틀린 신호를 준다. 다른 하나는 `assets/common/`으로 옮기는 것이다. `common`은 낱개 공용 파일을 담는 자리이고, 프로젝트 한 벌을 통째로 넣으면 `flake-greeter`나 `cyclonedds-cross-demo`라는 이름이 주는 "이것이 무슨 예제인지"가 사라진다.

챕터에 귀속되지 않는다는 사실 자체가 이 자산의 성질이므로, 챕터가 아니라 예제를 가리키는 이름을 규칙으로 인정한다.

## 결과

`assets/` 아래에는 세 종류가 온다. 한 챕터 전용 자산은 `<chapter-slug>/`, 여러 챕터가 쓰는 낱개 파일은 `common/`, 여러 챕터가 쓰는 예제 프로젝트는 `<project-slug>/`다. 한 챕터에만 대응하는 자산에는 `<chapter-slug>` 규칙이 그대로 적용된다.
