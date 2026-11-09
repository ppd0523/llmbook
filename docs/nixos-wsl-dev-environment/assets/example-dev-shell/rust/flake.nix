{
  description = "rustup과 LazyVim용 Rust 개발 셸";

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
          echo "Rust 셸: rustup이 고정된 toolchain을 설치한 뒤 nvim ."
        '';
      };
    };
}
