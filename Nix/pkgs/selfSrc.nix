{
  fetchFromGitHub,
  stdenvNoCC,
}:

stdenvNoCC.mkDerivation rec {
  pname = "selfSrc";
  version = "1.0.0";

  src = fetchFromGitHub {
    owner = "WSdlly02";
    repo = "jsjds-2025";
    rev = "d95cb536b4269018ee3991649f6f6b3ce6df4f75";
    hash = "sha256-hKCS+JvxS5YTw4VgMOJ3iEflaeDR8xJLUgDQsyQBtSo=";
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
