{ ... }:
{
  imports = [ ./hardware-configuration.nix ];

  networking.hostName = "nixos-native";

  # 기존 설치에서는 /etc/nixos/configuration.nix에 있던 원래 값을
  # 유지한다.
  system.stateVersion = "26.05";
}
