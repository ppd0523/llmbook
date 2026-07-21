{
  description = "Python development shell for uv and LazyVim";

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
          export PATH="$PWD/.venv/bin:$PATH"
          echo "Python shell: uv sync, then nvim ."
        '';
      };
    };
}
