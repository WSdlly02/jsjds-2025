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
    rev = "a0da060e879c54f2a9b55ae020b46101f26a4f76";
    hash = "sha256-ilULfEtDPgqIiDx8x2lx/01Z1KDPrEhuN4PZZDMnAZU=";
  };

  strictDeps = true;

  installPhase = ''
    mkdir -p $out
    cp -r $src/Haskell $out
    cp -r $src/Python $out
    cp $src/photos-timestamp-data.db $out
    cp $src/thermal-sensor-data.db $out
  '';
}
