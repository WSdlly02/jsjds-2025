{
  fetchFromGitHub,
  lib,
  stdenvNoCC,
}:

stdenvNoCC.mkDerivation rec {
  pname = "selfSrc";
  version = "0.0.1";

  src = fetchFromGitHub {
    owner = "WSdlly02";
    repo = "jsjds-2025";
    rev = "ec050d785fb060f4a0808de44b04fe64968f3b0e";
    hash = "sha256-ilULfEtDPgqIiDx8x2lx/01Z1KDPrEhuN4PZZDMnAZU=";
  };

  strictDeps = true;

  installPhase = ''
    mkdir -p $out
    cp -r $src/Haskell $out
    cp -r $src/Python $out
    cp $src/thermal-sensor-data.db $out
  '';
}
