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
    rev = "a988cb50b0a9d915b205fd786ed97394d3f66ef8";
    hash = "sha256-cZ2mJkX2yfKkNPvy0QyFqiMMUDWSLfzqoEW2f5l6ybQ=";
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
