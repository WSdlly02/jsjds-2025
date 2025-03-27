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
    rev = "3178cdc26ae235e50ebfddbe3836ffbf0bbf7c80";
    hash = "sha256-Egk0D6Un5tpGvikLg8/58sLV2K8ey4i9XlirJn8mYk4=";
  };

  strictDeps = true;

  installPhase = ''
    mkdir -p $out
    cp -r $src/Haskell $out
    cp -r $src/Python $out
    cp $src/thermal-sensor-data.db $out
  '';
}
