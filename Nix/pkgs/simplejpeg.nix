{
  python312Packages,
  fetchPypi,
}:
python312Packages.buildPythonPackage rec {
  pname = "simplejpeg";
  version = "1.8.2";
  format = "wheel";
  src = fetchPypi rec {
    pname = "simplejpeg";
    inherit version format;
    dist = python;
    python = "cp312";
    abi = "cp312";
    platform = "manylinux_2_17_aarch64.manylinux2014_aarch64";
    hash = "sha256-cOo7qZMOqZH6KkZO/c3Zydt+f3F5SfTSkah737/JZqU=";
  };
}
