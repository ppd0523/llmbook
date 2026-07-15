{
  pkgs,
  username,
  ...
}:
{
  nix.settings.experimental-features = [
    "nix-command"
    "flakes"
  ];

  # uv, nvm, and rustup download upstream Linux binaries. nix-ld supplies the
  # conventional dynamic-loader path those binaries expect on NixOS.
  programs.nix-ld.enable = true;
  programs.zsh.enable = true;

  users.users.${username} = {
    isNormalUser = true;
    extraGroups = [ "wheel" ];
    shell = pkgs.zsh;
  };
}
