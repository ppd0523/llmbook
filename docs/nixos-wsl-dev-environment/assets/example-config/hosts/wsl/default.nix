{ username, ... }:
{
  networking.hostName = "nixos-wsl";

  wsl = {
    enable = true;
    defaultUser = username;

    # Keep the Linux PATH deterministic. Windows programs remain reachable by
    # an explicit /mnt/c/... path when needed.
    interop.includePath = false;
  };

  # Set once at installation time. Do not raise this merely because you update
  # NixOS; it controls compatibility migrations, not the package release.
  system.stateVersion = "26.05";
}
