{
  description = "Portable NixOS-WSL and standalone Home Manager configuration";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

    nixos-wsl = {
      url = "github:nix-community/NixOS-WSL/main";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    home-manager = {
      url = "github:nix-community/home-manager/release-26.05";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    # nvm is a sourced shell function, so pin its source independently.
    nvm-src = {
      url = "github:nvm-sh/nvm/v0.40.4";
      flake = false;
    };
  };

  outputs = inputs@{
    nixpkgs,
    nixos-wsl,
    home-manager,
    ...
  }:
    let
      system = "x86_64-linux";
      username = "nixos";
      lib = nixpkgs.lib;

      mkNixos = modules:
        lib.nixosSystem {
          inherit system;
          specialArgs = { inherit inputs username; };
          modules = [ ./modules/nixos/common.nix ] ++ modules;
        };

      nativeHardware = ./hosts/native + "/hardware-configuration.nix";
    in
    {
      nixosConfigurations = {
        wsl = mkNixos [
          nixos-wsl.nixosModules.default
          ./hosts/wsl
        ];
      }
      # A native host is exposed only after its generated hardware module is
      # copied here and added to Git.
      // lib.optionalAttrs (builtins.pathExists nativeHardware) {
        native = mkNixos [ ./hosts/native ];
      };

      homeConfigurations.${username} = home-manager.lib.homeManagerConfiguration {
        pkgs = nixpkgs.legacyPackages.${system};
        extraSpecialArgs = { inherit inputs username; };
        modules = [ ./modules/home ];
      };

      # Bootstrap the standalone CLI from the same locked Home Manager input
      # used to evaluate homeConfigurations.
      apps.${system}.home-manager = {
        type = "app";
        program = "${home-manager.packages.${system}.default}/bin/home-manager";
      };

      formatter.${system} = nixpkgs.legacyPackages.${system}.nixfmt-rfc-style;
    };
}
