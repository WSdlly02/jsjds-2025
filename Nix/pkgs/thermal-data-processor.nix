{
  inputs,
  stdenv,
  system,
}:
stdenv.mkDerivation {
  pname = "thermal-data-processor";
  version = "0.0.1";
  src = inputs.self.legacyPackages."${system}".selfSrc.outPath;
  nativeBuildInputs = [ inputs.self.legacyPackages."${system}".haskellEnv ];
  buildPhase = ''
    cp $src/Haskell/thermal-data-processor.hs .
    ghc -O2 -Wall -threaded -rtsopts -with-rtsopts=-N thermal-data-processor.hs -o thermal-data-processor
  '';
  installPhase = ''
    mkdir -p $out/bin
    cp thermal-data-processor $out/bin
  '';
}
