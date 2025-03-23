{
  haskellPackages,
  inputs,
  mkShell,
  pkgs,
  python312Packages,
  system,
}:

mkShell {
  packages = with pkgs; [
    (labelImg.overrideAttrs (
      finalAttrs: previousAttrs: {
        propagatedBuildInputs =
          with python312Packages;
          [ distutils ] ++ previousAttrs.propagatedBuildInputs;
      }
    ))
    (inputs.self.legacyPackages."${system}".haskellEnv.override {
      extraPackages = with haskellPackages; [ ];
    })
    (inputs.self.legacyPackages."${system}".python312Env.override {
      extraPackages =
        with python312Packages;
        with inputs.self.legacyPackages."${system}";
        [ ultralytics ];
    })
  ];
  shellHook = ''
    fish
  '';
}
