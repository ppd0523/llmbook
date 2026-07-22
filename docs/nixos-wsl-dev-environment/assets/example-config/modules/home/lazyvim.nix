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

    # Shared LazyVim requirements only. Language servers and language-specific
    # plugins belong to each project.
    extraPackages = with pkgs; [
      fd
      tree-sitter
    ];

    # Bootstrap lazy.nvim from the locked Nixpkgs input. LazyVim and the
    # remaining plugins are selected and locked by the base or project spec.
    plugins = [ pkgs.vimPlugins.lazy-nvim ];

    # programs.neovim owns the generated ~/.config/nvim/init.lua. Keeping the
    # Lua source in Git still requires a Home Manager rebuild after edits.
    initLua = builtins.readFile ../../dotfiles/nvim/init.lua;
  };

  xdg.enable = true;

  # Do not link the whole nvim directory: programs.neovim also owns init.lua.
  # Link only the user-authored subtree and mutable base lock file so the
  # parent ~/.config/nvim remains a normal directory. Projects use their own
  # .lazy.lua, .lazy-lock.json, and plugin cache.
  xdg.configFile = {
    "nvim/lua".source =
      config.lib.file.mkOutOfStoreSymlink "${nvimSource}/lua";
    "nvim/stylua.toml".source =
      config.lib.file.mkOutOfStoreSymlink "${nvimSource}/stylua.toml";
    "nvim/lazy-lock.json".source =
      config.lib.file.mkOutOfStoreSymlink "${nvimSource}/lazy-lock.json";
  };
}
