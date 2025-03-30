{
  python312Packages,
  fetchPypi,
}:
python312Packages.buildPythonPackage rec {
  pname = "adafruit-circuitpython-mlx90640";
  version = "1.3.4";
  format = "wheel";
  src = fetchPypi rec {
    pname = "adafruit_circuitpython_mlx90640";
    inherit version format;
    dist = python;
    python = "py3";
    hash = "sha256-Jwlqmy+02cXUaGxINZqe7bRpCoUeu++eRLAaUpF+5xI=";
  };
}
