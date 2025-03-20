{
  haskellPackages,
  inputs,
  mkShell,
  python312Packages,
  system,
}:

mkShell {
  packages = [
    inputs.self.legacyPackages."${system}".haskellEnv.override
    {
      extraPackages = [ ];
    }
    (inputs.self.legacyPackages."${system}".python312Env.override {
      extraPackages = with python312Packages; with inputs.self.legacyPackages."${system}"; [ ];
      extraPostBuild = "";
    })
  ];
  shellHook = ''
    fish
  '';
}
