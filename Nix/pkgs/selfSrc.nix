{
  fetchFromGitHub,
  selectedModel,
  stdenvNoCC,
}:

stdenvNoCC.mkDerivation rec {
  pname = "selfSrc";
  version = "1.0.0";

  src = fetchFromGitHub {
    owner = "WSdlly02";
    repo = "jsjds-2025";
    rev = "6ce7a73c40ddca24de0bac32f71de4d66933d5e9";
    #hash = "sha256-KK85UCzL/r3TMfMEDuOBX1teuy+fL5WXnNp8Llakty0=";
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
    --replace "os.path.abspath(\"./Python/models/best-train1.pt\")" "\"$out/Python/models/${selectedModel}\"" 
  '';
}
