{
  config,
  pkgs,
  ...
}:
let
  nvimSource = "${config.home.homeDirectory}/.config/nixos/dotfiles/nvim";
in
{
  programs.neovim = {
    enable = true;
    defaultEditor = true;
    viAlias = true;
    vimAlias = true;

    # 공유 LazyVim 요구 사항만 둔다. 언어 서버와 언어별 플러그인은 각
    # 프로젝트에 속한다.
    extraPackages = with pkgs; [
      fd
      tree-sitter
    ];

    # 잠긴 Nixpkgs 입력에서 lazy.nvim을 부트스트랩한다. LazyVim과 나머지
    # 플러그인은 기본 spec 또는 프로젝트 spec이 선택하고 잠근다.
    plugins = [ pkgs.vimPlugins.lazy-nvim ];

    # 생성되는 ~/.config/nvim/init.lua는 programs.neovim이 소유한다. Lua
    # 소스를 Git에 두더라도 수정한 뒤에는 Home Manager를 다시 빌드해야 한다.
    initLua = builtins.readFile ../../dotfiles/nvim/init.lua;
  };

  xdg.enable = true;

  # nvim 디렉터리 전체를 링크하지 않는다. programs.neovim이 init.lua도
  # 소유하기 때문이다. 사용자가 작성한 하위 트리와 변경 가능한 기본 lock
  # 파일만 링크해 상위 ~/.config/nvim이 일반 디렉터리로 남게 한다. 프로젝트는
  # 각자의 .lazy.lua, .lazy-lock.json, 플러그인 캐시를 쓴다.
  xdg.configFile = {
    "nvim/lua".source =
      config.lib.file.mkOutOfStoreSymlink "${nvimSource}/lua";
    "nvim/stylua.toml".source =
      config.lib.file.mkOutOfStoreSymlink "${nvimSource}/stylua.toml";
    "nvim/lazy-lock.json".source =
      config.lib.file.mkOutOfStoreSymlink "${nvimSource}/lazy-lock.json";
  };
}
