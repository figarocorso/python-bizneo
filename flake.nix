{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      ...
    }:
    let
      overlays.default = final: prev: { bizneo = prev.callPackage ./bizneo.nix { }; };
      nixosModules.bizneo = import ./bizneo-module.nix self;
      homeManagerModules.bizneo = import ./bizneo-module-home.nix self;
      flake = flake-utils.lib.eachDefaultSystem (
        system:
        let
          pkgs = import nixpkgs {
            inherit system;
            config.allowUnfree = true;
            overlays = [
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
    flake // { inherit overlays nixosModules homeManagerModules; };
}
