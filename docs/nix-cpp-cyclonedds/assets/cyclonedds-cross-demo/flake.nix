{
  description = "C++17, Conan 2, Cyclone DDS, and aarch64-musl development shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

    # Cyclone DDS 0.10.2의 Conan recipe는 CMake [>=3.16 <4]를 요구한다.
    # Nixpkgs 26.05의 기본 CMake는 4.x이므로 CMake 3만 별도 입력에서 가져온다.
    nixpkgsCmake.url = "github:NixOS/nixpkgs/nixos-25.05";
  };

  outputs =
    { nixpkgs, nixpkgsCmake, ... }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
      cmakePkgs = nixpkgsCmake.legacyPackages.${system};
      nativeCC = pkgs.stdenv.cc;
      crossCC = pkgs.pkgsCross.aarch64-multiplatform-musl.stdenv.cc;
      targetPrefix = crossCC.targetPrefix;
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        packages = [
          cmakePkgs.cmake
          pkgs.gnumake
          pkgs.conan
          nativeCC
          crossCC
        ];

        CMAKE_PLATFORM_VERSION = cmakePkgs.cmake.version;
        NATIVE_GCC_VERSION = pkgs.lib.versions.major nativeCC.version;
        CROSS_GCC_VERSION = pkgs.lib.versions.major crossCC.version;

        NATIVE_CC = "${nativeCC}/bin/cc";
        NATIVE_CXX = "${nativeCC}/bin/c++";
        AARCH64_CC = "${crossCC}/bin/${targetPrefix}cc";
        AARCH64_CXX = "${crossCC}/bin/${targetPrefix}c++";
        AARCH64_READELF = "${crossCC.bintools.bintools}/bin/${targetPrefix}readelf";

        shellHook = ''
          export CONAN_HOME="$PWD/.conan2"

          echo "C++/Cyclone DDS development shell"
          echo "  CMake       : $(cmake --version | head -n 1)"
          echo "  Make        : $(make --version | head -n 1)"
          echo "  Conan       : $(conan --version)"
          echo "  Native C++  : $NATIVE_CXX"
          echo "  Target C++  : $AARCH64_CXX"
          echo "  Conan home  : $CONAN_HOME"
        '';
      };

      formatter.${system} = pkgs.nixfmt-rfc-style;
    };
}
