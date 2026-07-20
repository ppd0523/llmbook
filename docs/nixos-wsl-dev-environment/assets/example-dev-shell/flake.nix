{
  description = "Small project development shell example";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs = { nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        packages = with pkgs; [
          jq
          openssl
          pkg-config
        ];

        PROJECT_ENV = "nix-develop";

        shellHook = ''
          echo "development shell loaded"
        '';
      };

      formatter.${system} = pkgs.nixfmt-rfc-style;
    };
}
