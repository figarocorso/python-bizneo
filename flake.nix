{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    poetry2nix-python = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.flake-utils.follows = "flake-utils";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      poetry2nix-python,
    }:
    let
      overlays.default = final: prev: { bizneo = prev.callPackage ./bizneo.nix { }; };
      nixosModules.bizneo = import ./bizneo-module.nix self;

      flake = flake-utils.lib.eachDefaultSystem (
        system:
        let
          pkgs = import nixpkgs {
            inherit system;
            config.allowUnfree = true;
            overlays = [
              poetry2nix-python.overlays.default
              self.overlays.default
            ];
          };
        in
        {
          packages = {
            inherit (pkgs) bizneo;
            default = pkgs.bizneo;
          };

          checks = {
            inherit (pkgs) bizneo;
          };

          devShells.default =
            with pkgs;
            mkShellNoCC {
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
          formatter = pkgs.nixfmt-rfc-style;
        }
      );
    in
    flake // { inherit overlays nixosModules; };
}
