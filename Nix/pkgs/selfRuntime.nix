{
  fetchFromGitHub,
  inputs,
  stdenvNoCC,
  system,
}:

stdenvNoCC.mkDerivation {
  pname = "selfRuntime";
  version = "1.0.0";
  src = ../../Src;
  nativeBuildInputs = with inputs.self.legacyPackages."${system}" [ haskellEnv python312Env ];
  buildPhase = ''
    ghc -O2 -Wall -threaded -rtsopts -with-rtsopts=-N -optlo-O3 -funfolding-use-threshold=32 thermal-data-processor.hs -o thermal-data-processor
    pyinstaller --strip --optimize 2 thermal-data-reader.py
    pyinstaller --strip --optimize 2 central-compositor.py
  '';
  strictDeps = true;
  allowSubstitutes = false;
  preferLocalBuild = true;
  installPhase = ''
    mkdir -p $out
    cp -r $src/models $out
    cp -r $src/static $out
    cp -r $src/templates $out
    cp $src/photos-timestamp-data.db $out
    cp $src/thermal-sensor-data.db $out
    cp thermal-data-processor $out
  '';
}
