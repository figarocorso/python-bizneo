{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    poetry2nix-python = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      poetry2nix-python,
    }:
    let
      supportedSystems = [
        "x86_64-linux"
        "x86_64-darwin"
        "aarch64-linux"
        "aarch64-darwin"
      ];

      forEachSystem =
        f:
        nixpkgs.lib.genAttrs supportedSystems (
          system:
          let
            pkgs = import nixpkgs {
              inherit system;
              overlays = [
                poetry2nix-python.overlays.default
                self.overlays.default
              ];
            };
          in
          f pkgs
        );
    in
    {
      overlays.default = final: prev: { bizneo = final.pkgs.callPackage ./bizneo.nix { }; };
      nixosModules.bizneo = import ./bizneo-module.nix self;

      packages = forEachSystem (
        pkgs: with pkgs; {
          inherit bizneo;
          default = bizneo;
        }
      );

      checks = forEachSystem (
        pkgs: with pkgs; {
          inherit bizneo;
        }
      );

      devShells = forEachSystem (
        pkgs: with pkgs; {
          default = mkShellNoCC {
            shellHook = ''
              pre-commit install
            '';

            packages = [
              (poetry2nix.mkPoetryEnv { projectDir = ./.; })
              poetry
              pre-commit
              ruff
            ];
          };
        }
      );

      formatter = forEachSystem (pkgs: pkgs.nixfmt-rfc-style);
    };
}
