{ ... }:
{
  imports = [ ./hardware-configuration.nix ];

  networking.hostName = "nixos-native";

  # For an existing installation, preserve its original value from
  # /etc/nixos/configuration.nix.
  system.stateVersion = "26.05";
}
