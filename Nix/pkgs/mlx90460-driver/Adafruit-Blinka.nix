{
  python312Packages,
  fetchPypi,
}:
python312Packages.buildPythonPackage rec {
  pname = "Adafruit-Blinka";
  version = "8.55.0";
  format = "wheel";
  src = fetchPypi rec {
    pname = "adafruit_blinka";
    inherit version format;
    dist = python;
    python = "py3";
    hash = "sha256-GTJfTmpzQxe0cZ/e6+cZia0wKgkFFYWEH9Af912gZJg=";
  };
}
