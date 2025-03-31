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
    rev = "77584283e698cbde051fb1043c49f4cbc5d3198c";
    hash = "sha256-lBvBQFi3ERbB61ar8XGbeeFYQQob/mwWTABNS6nkamk=";
  };
  strictDeps = true;

  installPhase = ''
    mkdir -p $out
    cp -r $src/Haskell $out
    cp -r $src/Python $out
    cp $src/photos-timestamp-data.db $out
    cp $src/thermal-sensor-data.db $out
    runHook postInstall
  '';
  postInstall = ''
    substituteInPlace $out/Python/inference.py \
    --replace "os.path.abspath(\"./Python/models/best-train1.pt\")" "\"$out/Python/models/best-train1.pt\"" 
  '';
}
