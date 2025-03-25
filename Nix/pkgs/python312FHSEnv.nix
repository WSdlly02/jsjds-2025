{
  buildFHSEnv,
  cmake,
  gcc,
  glib,
  glibc,
  dbus,
  fish,
  libdrm,
  libglvnd,
  inputs,
  udev,
  stdenv,
  system,
  zlib,
  zstd,
  rocmPackages,
}:
let
  usedRocmPackages =
    if (system != "x86_64-linux") then
      [ ]
    else
      with rocmPackages;
      [
        rocm-core
        clr
        rccl
        miopen
        #miopengemm
        rocrand
        rocblas
        rocsparse
        hipsparse
        rocthrust
        rocprim
        hipcub
        roctracer
        rocfft
        rocsolver
        hipfft
        hipsolver
        hipblas
        rocminfo
        rocm-smi
        rocm-thunk
        rocm-comgr
        rocm-device-libs
        rocm-runtime
        clr.icd
        hipify
        llvm.openmp
      ];
in
buildFHSEnv {
  name = "python312FHSEnv";
  targetPkgs =
    pkgs:
    with pkgs;
    [
      # Common pkgs
      cmake
      gcc
      glib.out
      glibc
      dbus
      fish
      libdrm
      libglvnd
      inputs.self.legacyPackages."${system}".python312Env
      udev
      stdenv.cc.cc.lib
      zlib
      zstd
    ]
    ++ usedRocmPackages;
  profile = "export LD_LIBRARY_PATH=/usr/lib";
  runScript = "fish";
}
