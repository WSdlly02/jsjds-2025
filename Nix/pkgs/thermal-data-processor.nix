{
  inputs,
  stdenv,
  system,
}:
stdenv.mkDerivation {
  pname = "thermal-data-processor";
  version = "1.0.0";
  src = inputs.self.legacyPackages."${system}".selfSrc;
  nativeBuildInputs = [ inputs.self.legacyPackages."${system}".haskellEnv ];
  buildPhase = ''
    ghc -O2 -Wall -threaded -rtsopts -with-rtsopts=-N -optlo-O3 -funfolding-use-threshold=32 ./Haskell/thermal-data-processor.hs -o thermal-data-processor
  '';
  installPhase = ''
    mkdir -p $out/bin
    cp thermal-data-processor $out/bin
  '';
}
