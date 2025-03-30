{
  python312Packages,
  fetchPypi,
}:
python312Packages.buildPythonPackage rec {
  pname = "picamera2";
  version = "0.3.25";
  # format = "wheel";
  src = fetchPypi rec {
    pname = "picamera2";
    inherit version;
    # dist = python;
    # python = "py3";
    hash = "sha256-ys88QLgkDwuAICac6Wa6kRxw/ph8Sivy+5ac4010Zpo=";
  };
}
