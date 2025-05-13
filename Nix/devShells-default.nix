{
  haskellEnv,
  haskellPackages,
  inputs,
  mkShell,
  python312Env,
  python312Packages,
  stdenv,
}:

mkShell {
  packages = [
    (haskellEnv.override {
      extraPackages = with haskellPackages; [ ];
    })
    (python312Env.override {
      extraPackages =
        with python312Packages;
        with inputs.self.legacyPackages."${stdenv.hostPlatform.system}";
        [ ];
    })
  ];
  shellHook = ''
    fish
  '';
}
