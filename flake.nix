{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    poetry2nix-python.url = "github:nix-community/poetry2nix";
    poetry2nix-python.inputs.flake-utils.follows = "utils";
    poetry2nix-python.inputs.nixpkgs.follows = "nixpkgs";
    poetry2nix-python.inputs.systems.follows = "utils/systems";
    utils.url = "github:numtide/flake-utils";
    playwrightOverwrite.url = "github:tembleking/nixpkgs/playwright";
  };

  outputs = {
    self,
    nixpkgs,
    poetry2nix-python,
    utils,
    ...
  } @ inputs: let
    flake = utils.lib.eachDefaultSystem (
      system: let
        latestPlaywrightVersion = final: prev: {
          playwright-driver = inputs.playwrightOverwrite.legacyPackages.${prev.system}.playwright-driver;
        };

        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
          overlays = [poetry2nix-python.overlays.default latestPlaywrightVersion];
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
              black
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

    nixosModules.bizneo = import ./bizneo-module.nix flake;
  in
    flake // {inherit overlays nixosModules;};
}
