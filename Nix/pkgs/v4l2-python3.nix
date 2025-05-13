{
  python312Packages,
  fetchPypi,
}:
python312Packages.buildPythonPackage rec {
  pname = "v4l2-python3";
  version = "0.3.5";
  # format = "wheel";
  src = fetchPypi {
    pname = "v4l2-python3";
    inherit version;
    # dist = python;
    # python = "py3";
    hash = "sha256-5+JHOcGBbWSoKSm4F4GtpOVkCXQVejlYWtLgLf2xAv0=";
  };
}
