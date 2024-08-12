{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    poetry2nix-python = {
      url = "github:nix-community/poetry2nix";
      inputs = {
        flake-utils.follows = "utils";
        nixpkgs.follows = "nixpkgs";
        systems.follows = "utils/systems";
        nix-github-actions.follows = "nix-github-actions";
      };
    };
    utils.url = "github:numtide/flake-utils";
    playwrightOverwrite.url = "github:tembleking/nixpkgs/playwright";
    nix-github-actions = {
      url = "github:nix-community/nix-github-actions";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      poetry2nix-python,
      utils,
      ...
    }@inputs:
    let
      supportedPythonVersions = [
        "python3"
        "python310"
        "python311"
        "python312"
        "python313"
      ];
      forAllSupportedPythonVersions = nixpkgs.lib.genAttrs supportedPythonVersions;

      flake = utils.lib.eachDefaultSystem (
        system:
        let
          latestPlaywrightVersion = final: prev: {
            playwright-driver = inputs.playwrightOverwrite.legacyPackages.${prev.system}.playwright-driver;
          };

          pkgs = import nixpkgs {
            inherit system;
            config.allowUnfree = true;
            overlays = [
              poetry2nix-python.overlays.default
              latestPlaywrightVersion
            ];
          };

          bizneo = pkgs.callPackage ./bizneo.nix { };
          checkPackageForAllSupportedVersions =
            pkg:
            nixpkgs.lib.mapAttrs' (name: value: nixpkgs.lib.nameValuePair ("${pkg}-" + name) value) (
              forAllSupportedPythonVersions (
                pythonVersion: self.packages.${system}.${pkg}.override { python3 = pkgs.${pythonVersion}; }
              )
            );
        in
        {
          packages = {
            inherit bizneo;
            default = bizneo;
          };

          checks = checkPackageForAllSupportedVersions "bizneo";
          devShells.default =
            with pkgs;
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
                ruff
              ];
            };

          formatter = pkgs.nixfmt-rfc-style;
        }
      );

      overlays = {
        default = final: prev: { bizneo = self.packages.${prev.system}.bizneo; };
      };

      nixosModules.bizneo = import ./bizneo-module.nix flake;

      githubActions = inputs.nix-github-actions.lib.mkGithubMatrix {
        checks = nixpkgs.lib.getAttrs [
          "x86_64-linux"
          "x86_64-darwin"
          "aarch64-darwin"
        ] self.checks;
      };
    in
    flake // { inherit overlays nixosModules githubActions; };
}
