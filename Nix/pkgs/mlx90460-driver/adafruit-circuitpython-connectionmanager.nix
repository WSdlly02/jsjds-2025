{
  python312Packages,
  fetchPypi,
}:
python312Packages.buildPythonPackage rec {
  pname = "adafruit-circuitpython-connectionmanager";
  version = "3.1.3";
  format = "wheel";
  src = fetchPypi rec {
    pname = "adafruit_circuitpython_connectionmanager";
    inherit version format;
    dist = python;
    python = "py3";
    hash = "sha256-nfOkxhfa4nutGshgfxoIQxLISY2DHr4caiyNXLMJ2uo=";
  };
}
