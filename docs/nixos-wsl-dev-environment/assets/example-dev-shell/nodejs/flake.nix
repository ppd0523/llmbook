{
  description = "NVM과 LazyVim용 Node.js 개발 셸";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs = { nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        packages = with pkgs; [
          openssl
          pkg-config
        ];

        shellHook = ''
          export PATH="$PWD/node_modules/.bin:$PATH"
          echo "Node.js 셸: nvm install, npm install 후 nvim ."
        '';
      };
    };
}
