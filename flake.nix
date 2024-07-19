{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    poetry2nix-python.url = "github:nix-community/poetry2nix";
    utils.url = "github:numtide/flake-utils";
    playwrightOverwrite.url = "github:tembleking/nixpkgs/playwright";
    playwrightOverwrite.inputs.nixpkgs.follows = "nixpkgs";
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
