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

  # uv, nvm, rustup은 upstream Linux 바이너리를 내려받는다. nix-ld는 이
  # 바이너리들이 NixOS에서 기대하는 관례적인 동적 로더 경로를 제공한다.
  programs.nix-ld.enable = true;
  programs.zsh.enable = true;

  users.users.${username} = {
    isNormalUser = true;
    extraGroups = [ "wheel" ];
    shell = pkgs.zsh;
  };
}
