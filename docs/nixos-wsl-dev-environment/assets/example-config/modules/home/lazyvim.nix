{
  config,
  pkgs,
  ...
}:
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
  };

  xdg.enable = true;

  # The base lock file is writable and tracked with the configuration repo.
  # Projects use their own .lazy.lua, .lazy-lock.json, and plugin cache.
  xdg.configFile."nvim".source = config.lib.file.mkOutOfStoreSymlink
    "${config.home.homeDirectory}/.config/nixos/dotfiles/nvim";
}
