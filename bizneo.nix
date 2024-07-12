{
  poetry2nix,
  python3,
}:
poetry2nix.mkPoetryApplication {
  projectDir = ./.;
  python = python3;
  meta.mainProgram = "bizneo";
}
