{
  poetry2nix,
  python3,
  writeShellApplication,
  playwright-driver,
}:
let
  bizneo = poetry2nix.mkPoetryApplication {
    projectDir = ./.;
    python = python3;
    meta.mainProgram = "bizneo";

    doInstallCheck = true;
    installCheckPhase = ''
      $out/bin/bizneo --help
      $out/bin/bizneo admin --help
      $out/bin/bizneo browser --help
      $out/bin/bizneo browser expected --help
    '';
  };
in
writeShellApplication {
  name = "bizneo";
  runtimeInputs = [ playwright-driver.browsers ];
  text = ''
    export PLAYWRIGHT_BROWSERS_PATH=${playwright-driver.browsers}
    export PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=true

    exec ${bizneo}/bin/bizneo "$@"
  '';
}
