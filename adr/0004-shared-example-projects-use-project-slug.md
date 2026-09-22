# 여러 챕터가 공유하는 예제 프로젝트는 `assets/<project-slug>/`에 둔다

`.guide/OUTPUTS.md`는 책 자산을 `assets/<chapter-slug>/`와 `assets/common/`으로만 나눴다. 그런데 `nixos-wsl-dev-environment/assets/example-config`, `nix-cpp-cyclonedds/assets/cyclonedds-cross-demo`, `nix-flakes/assets/flake-greeter`, `lazyvim-development-environment/assets/example-config`는 여러 챕터가 함께 쓰는 예제 프로젝트 한 벌이라 어느 쪽에도 맞지 않는다. 예제 프로젝트에는 `<project-slug>` 폴더를 허용하기로 했다.

## 고려한 대안

두 가지를 검토했다. 하나는 예제를 가장 많이 참조하는 챕터의 slug에 귀속시키는 것이다. `example-config`는 `nixos-wsl-dev-environment` 본문 19곳이 참조하고 그중 한 챕터에 속하지 않으므로, 챕터 이름을 붙이면 "이 예제는 그 장의 것"이라는 틀린 신호를 준다. 다른 하나는 `assets/common/`으로 옮기는 것이다. `common`은 낱개 공용 파일을 담는 자리이고, 프로젝트 한 벌을 통째로 넣으면 `flake-greeter`나 `cyclonedds-cross-demo`라는 이름이 주던 "이것이 무슨 예제인지"가 사라진다.

챕터에 귀속되지 않는다는 사실 자체가 이 자산의 성질이므로, 챕터가 아니라 예제를 가리키는 이름을 규칙으로 인정했다.

## 결과

`assets/` 아래에는 세 종류가 온다. 한 챕터 전용 자산은 `<chapter-slug>/`, 여러 챕터가 쓰는 낱개 파일은 `common/`, 여러 챕터가 쓰는 예제 프로젝트는 `<project-slug>/`다. 기존 네 책의 예제 폴더 이름은 그대로 둔다.

한 챕터에만 대응하는 자산에는 `<chapter-slug>` 규칙이 그대로 적용된다. 이 결정에 맞춰 `pytorch-ppo-learning`의 실험실 폴더 네 개를 참조 챕터의 slug로 바꿨다(`advantage-estimation`→`policy-gradient-and-gae`, `discounted-return`→`mdp-value-and-math`, `ppo-objective`→`ppo-clipped-objective`, `pytorch-foundations`→`pytorch-for-policies`). 참조하는 파일이 없던 빈 `assets/debugging/`은 삭제했다.
