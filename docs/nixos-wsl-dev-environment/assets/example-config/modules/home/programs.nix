{ ... }:
{
  programs = {
    git = {
      enable = true;
      settings = {
        init.defaultBranch = "main";
        core.editor = "nvim";
        pull.rebase = false;
      };
    };

    bat = {
      enable = true;
      config = {
        style = "plain";
        pager = "less -FR";
      };
    };

    zsh = {
      enable = true;
      enableCompletion = true;
      autosuggestion.enable = true;
      syntaxHighlighting.enable = true;

      history = {
        size = 100000;
        save = 100000;
        share = true;
      };

      shellAliases = {
        cat = "bat";
        grep = "rg";
        ll = "ls -alh";
      };
    };

    starship = {
      enable = true;
      enableZshIntegration = true;
      settings.add_newline = false;
    };

    fzf = {
      enable = true;
      enableZshIntegration = true;
    };

    autojump = {
      enable = true;
      enableZshIntegration = true;
    };

    # Load each project's Nix development shell when entering its directory.
    direnv = {
      enable = true;
      enableZshIntegration = true;
      nix-direnv.enable = true;
    };
  };
}
