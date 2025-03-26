{
  lib,
  fetchgit,
  stdenvNoCC,
}:

stdenvNoCC.mkDerivation rec {
  pname = "kmsxx-src";
  version = "2024-12-09";

  src = fetchgit {
    url = "https://github.com/tomba/kmsxx.git";
    hash = "sha256-KNfWQAxz3ZLoxIe3v1fqaQBJdec0BXwipATfofWIzlQ=";
    deepClone = true;
    leaveDotGit = true;
  };
  installPhase = ''
    mkdir $out
    cp -r $src/* $out
    cp -r $src/.git $out
  '';
  meta = with lib; {
    description = "C++ library for KMS/DRM";
    homepage = "https://github.com/tomba/kmsxx";
    license = licenses.mit;
  };
}
