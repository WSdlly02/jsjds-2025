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
    rev = "9130c41838ad747b4e519b4814e5194f52a9064f";
    hash = "sha256-xSw64EcwZEsxJLwwhfWWYMDiKd10A5HNn/dPcKFEJjQ=";
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
