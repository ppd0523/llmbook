{
  description = "A small multi-system Flake learning project";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs =
    {
      self,
      nixpkgs,
    }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in
    {
      packages = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        rec {
          flake-greeter = pkgs.writeShellApplication {
            name = "flake-greeter";
            runtimeInputs = [ pkgs.cowsay ];
            text = ''
              message="''${1:-Hello from a Nix flake!}"
              cowsay "$message"
            '';
          };
          default = flake-greeter;
        }
      );

      apps = forAllSystems (system: {
        default = {
          type = "app";
          program = "${self.packages.${system}.default}/bin/flake-greeter";
          meta.description = "Print a message with cowsay";
        };
      });

      devShells = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        {
          default = pkgs.mkShellNoCC {
            packages = [
              pkgs.cowsay
              pkgs.nixfmt
              self.packages.${system}.default
            ];
            shellHook = ''
              cowsay "Flake development shell is ready"
            '';
          };
        }
      );

      formatter = forAllSystems (system: nixpkgs.legacyPackages.${system}.nixfmt);

      checks = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          greeter = self.packages.${system}.default;
        in
        {
          package = greeter;
          greeting = pkgs.runCommand "flake-greeter-check" {
            nativeBuildInputs = [
              greeter
              pkgs.gnugrep
            ];
          } ''
            flake-greeter "checked" > "$out"
            grep -q "checked" "$out"
          '';
        }
      );
    };
}
