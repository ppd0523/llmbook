{
  description = "이식 가능한 NixOS-WSL과 standalone Home Manager 설정";

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

    # nvm은 source로 읽어 들이는 셸 함수이므로 소스를 별도로 고정한다.
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
      # native 호스트는 생성된 하드웨어 모듈을 여기에 복사하고 Git에 추가한
      # 뒤에만 노출된다.
      // lib.optionalAttrs (builtins.pathExists nativeHardware) {
        native = mkNixos [ ./hosts/native ];
      };

      homeConfigurations.${username} = home-manager.lib.homeManagerConfiguration {
        pkgs = nixpkgs.legacyPackages.${system};
        extraSpecialArgs = { inherit inputs username; };
        modules = [ ./modules/home ];
      };

      # standalone CLI를 homeConfigurations 평가에 쓰는 것과 같은 잠긴
      # Home Manager 입력에서 부트스트랩한다.
      apps.${system}.home-manager = {
        type = "app";
        program = "${home-manager.packages.${system}.default}/bin/home-manager";
      };

      formatter.${system} = nixpkgs.legacyPackages.${system}.nixfmt-rfc-style;
    };
}
