{
  fetchFromGitHub,
  inputs,
  system,
  stdenvNoCC,
}:

stdenvNoCC.mkDerivation rec {
  pname = "selfSrc";
  version = "1.0.0";
  src = ../../Src;
  nativeBuildInputs = [ inputs.self.legacyPackages."${system}".haskellEnv ];
  buildPhase = ''
    ghc -O2 -Wall -threaded -rtsopts -with-rtsopts=-N -optlo-O3 -funfolding-use-threshold=32 thermal-data-processor.hs -o thermal-data-processor
  '';
  strictDeps = true;
  allowSubstitutes = false;
  preferLocalBuild = true;
  installPhase = ''
    mkdir -p $out
    cp -r $src/* $out
    cp thermal-data-processor $out
  '';
}
