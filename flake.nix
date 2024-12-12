{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    nixpkgs-plarwright-darwin-x86_64.url = "github:NixOS/nixpkgs/pull/349469/head";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      ...
    }@inputs:
    let
      overlays.default = final: prev: { bizneo = prev.callPackage ./bizneo.nix { }; };
      nixosModules.bizneo = import ./bizneo-module.nix self;

      temp-fix-playwright-darwin-x86_64 =
        final: prev:
        let
          nixpkgs-fix = import inputs.nixpkgs-plarwright-darwin-x86_64 { inherit (prev) system; };
        in
        {
          inherit (nixpkgs-fix) playwright-driver;
        };

      flake = flake-utils.lib.eachDefaultSystem (
        system:
        let
          pkgs = import nixpkgs {
            inherit system;
            config.allowUnfree = true;
            overlays = [
              self.overlays.default
              temp-fix-playwright-darwin-x86_64
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
                (python3.withPackages (
                  p: with p; [
                    jedi-language-server
                    python-lsp-server
                  ]
                ))
                uv
                pre-commit
                ruff
              ];

              inputsFrom = [ bizneo ];

            };
          formatter = pkgs.nixfmt-rfc-style;
        }
      );
    in
    flake // { inherit overlays nixosModules; };
}
