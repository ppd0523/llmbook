{
  pkgs,
  username,
  ...
}:
{
  imports = [
    ./programs.nix
    ./lazyvim.nix
    ./nvm.nix
  ];

  home = {
    inherit username;
    homeDirectory = "/home/${username}";

    # system.stateVersion처럼 첫 활성화 이후에는 이 값을 유지한다.
    stateVersion = "26.05";

    packages = with pkgs; [
      tree
      ripgrep
      uv
      rustup

      # 프로젝트가 관리하는 런타임의 빌드·다운로드에 공통으로 쓰는 도구.
      curl
      unzip
      gcc
      pkg-config
    ];

    sessionPath = [
      "$HOME/.local/bin"
      "$HOME/.cargo/bin"
    ];

    sessionVariables = {
      EDITOR = "nvim";
      VISUAL = "nvim";
      CARGO_HOME = "$HOME/.cargo";
      RUSTUP_HOME = "$HOME/.rustup";
      RUSTUP_AUTO_INSTALL = "1";
    };
  };

  # 한 번 실행하는 부트스트랩 명령 이후에도 standalone Home Manager CLI를
  # 관리 대상 프로필에 유지한다.
  programs.home-manager.enable = true;
}
