{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    poetry2nix-python.url = "github:nix-community/poetry2nix";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    poetry2nix-python,
    utils,
  }: let
    flake = utils.lib.eachDefaultSystem (
      system: let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
          overlays = [poetry2nix-python.overlays.default];
        };

        bizneo = pkgs.callPackage ./bizneo.nix {};
      in {
        packages = {
          inherit bizneo;
          default = bizneo;
        };

        devShells.default = with pkgs;
          mkShellNoCC {
            shellHook = ''
              pre-commit install
            '';

            packages = [
              (poetry2nix.mkPoetryEnv {
                projectDir = ./.;
                python = python3;
              })
              poetry
              pre-commit
              bizneo
            ];
          };

        formatter = pkgs.alejandra;
      }
    );

    overlays = {
      default = final: prev: {
        bizneo = self.packages.${prev.system}.bizneo;
      };
    };
  in
    flake // {inherit overlays;};
}
