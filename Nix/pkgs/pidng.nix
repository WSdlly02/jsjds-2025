{
  python312Packages,
  fetchPypi,
}:
python312Packages.buildPythonPackage rec {
  pname = "pidng";
  version = "4.0.9";
  # format = "wheel";
  src = fetchPypi rec {
    pname = "pidng";
    inherit version;
    # dist = python;
    # python = "py3";
    hash = "sha256-Vg6wCAhvinFf2eGrmYgXp9TIUAp/Fhuc5q9asnUB+Cw=";
  };
}
