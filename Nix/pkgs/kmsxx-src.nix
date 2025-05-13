{
  lib,
  fetchgit,
  stdenvNoCC,
}:

stdenvNoCC.mkDerivation {
  pname = "kmsxx-src";
  version = "2025-2-12";

  src = fetchgit {
    url = "https://github.com/tomba/kmsxx.git";
    rev = "8b1c053359ed7593e43222daccb8c0db8fcc441f";
    hash = "sha256-qhj3cLh1rOODaj/C1V60W/bsZtOm7r9lJHGGSLBlwJU="; # Notice hash change!!
    deepClone = true;
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
