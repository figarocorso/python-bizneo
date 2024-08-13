{
  poetry2nix,
  python3,
  playwright-driver,
  installShellFiles,
  makeWrapper,
}:
poetry2nix.mkPoetryApplication {
  projectDir = ./.;
  python = python3;
  meta.mainProgram = "bizneo";

  nativeBuildInputs = [
    installShellFiles
    makeWrapper
  ];

  buildInputs = [ playwright-driver.browsers ];

  postInstall = ''
    installShellCompletion --cmd bizneo \
      --bash <(_BIZNEO_COMPLETE=bash_source $out/bin/bizneo) \
      --zsh <(_BIZNEO_COMPLETE=zsh_source $out/bin/bizneo) \
      --fish <(_BIZNEO_COMPLETE=fish_source $out/bin/bizneo)
  '';

  postFixup = ''
    wrapProgram $out/bin/bizneo \
      --set-default PLAYWRIGHT_BROWSERS_PATH ${playwright-driver.browsers} \
      --set-default PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS true
  '';

  doInstallCheck = true;
  installCheckPhase = ''
    $out/bin/bizneo --help
    $out/bin/bizneo admin --help
    $out/bin/bizneo browser --help
    $out/bin/bizneo browser expected --help
  '';
}
