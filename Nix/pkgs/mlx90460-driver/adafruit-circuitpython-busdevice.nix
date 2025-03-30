{
  python312Packages,
  fetchPypi,
}:
python312Packages.buildPythonPackage rec {
  pname = "adafruit-circuitpython-busdevice";
  version = "5.2.11";
  format = "wheel";
  src = fetchPypi rec {
    pname = "adafruit_circuitpython_busdevice";
    inherit version format;
    dist = python;
    python = "py3";
    hash = "sha256-1DecmuhqFfcETeqBWpRSXKntpqfAsvoOdc+ecAyThLg=";
  };
}
