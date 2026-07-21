{
  description = "Rust development shell for rustup and LazyVim";

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

        RUST_BACKTRACE = "1";

        shellHook = ''
          echo "Rust shell: rustup installs the pinned toolchain; then nvim ."
        '';
      };
    };
}
