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
    (inputs.self.legacyPackages."${system}".haskellEnv.override {
      extraPackages = with haskellPackages; [ ];
    })
    (inputs.self.legacyPackages."${system}".python312Env.override {
      extraPackages = with python312Packages; with inputs.self.legacyPackages."${system}"; [ ];
    })
  ];
  shellHook = ''
    fish
  '';
}
