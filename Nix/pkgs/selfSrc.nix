{
  fetchFromGitHub,
  lib,
  stdenvNoCC,
}:

stdenvNoCC.mkDerivation rec {
  pname = "selfSrc";
  version = "1.0.0";

  src = fetchFromGitHub {
    owner = "WSdlly02";
    repo = "jsjds-2025";
    rev = "34d532fad111ec1f3edacf6714d615946132afca";
    hash = "sha256-8yVlb7fpm9iNXs6ZiKVa+u9mbtJMvNXEstPKOxrRNFs=";
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
