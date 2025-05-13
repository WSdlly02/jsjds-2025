{
  autoPatchelfHook,
  python312Packages,
  fetchPypi,
  stdenv,
}:
python312Packages.buildPythonPackage rec {
  pname = "ncnn";
  version = "1.0.20241226";
  format = "wheel";
  src =
    {
      x86_64-linux = fetchPypi rec {
        pname = "ncnn";
        inherit version format;
        dist = python;
        python = "cp312";
        abi = "cp312";
        platform = "manylinux_2_17_x86_64.manylinux2014_x86_64";
        hash = "sha256-5r5CgYZ5Mjt1z147COylKLNR4zyUTKEBFz8RLajE9hA=";
      };
      aarch64-linux = fetchPypi rec {
        pname = "ncnn";
        inherit version format;
        dist = python;
        python = "cp312";
        abi = "cp312";
        platform = "manylinux_2_17_aarch64.manylinux2014_aarch64";
        hash = "sha256-ybFbzbA5PRU5AvjjXB5Rr0d9qpmX060xwl14UtKez4M=";
      };
    }
    .${stdenv.hostPlatform.system};
  nativeBuildInputs = [ autoPatchelfHook ];
}
