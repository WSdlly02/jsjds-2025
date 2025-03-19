{
  description = "WSdlly02's Codes Library";

  inputs = {
    flake-parts = {
      url = "github:hercules-ci/flake-parts";
      inputs.nixpkgs-lib.follows = "nixpkgs";
    };
    home-manager = {
      url = "github:nix-community/home-manager/master";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    {
      flake-parts,
      home-manager,
      self,
      nixpkgs,
    }@inputs:
    flake-parts.lib.mkFlake { inherit inputs; } {
      perSystem =
        {
          inputs',
          ...
        }:
        let
          pkgs = inputs'.nixpkgs.legacyPackages; # can be defined in arguments
          inherit (pkgs)
            callPackage
            mkShell
            ;
        in
        {
          devShells = {
            default = callPackage ./Nix/devShells-default.nix { inherit inputs; };
          };

          formatter = pkgs.nixfmt-rfc-style;

          legacyPackages = {
            ####################
            haskellEnv = callPackage ./Nix/pkgs/haskellEnv.nix { };
            kmsxx-src = callPackage ./Nix/pkgs/kmsxx-src.nix { };
            libcamera = callPackage ./Nix/pkgs/libcamera-raspi.nix { inherit inputs; };
            libpisp = callPackage ./Nix/pkgs/libpisp.nix { };
            picamera2 = callPackage ./Nix/pkgs/picamera2.nix { };
            pidng = callPackage ./Nix/pkgs/pidng.nix { };
            python312Env = callPackage ./Nix/pkgs/python312Env.nix { inherit inputs; };
            python312FHSEnv = callPackage ./Nix/pkgs/python312FHSEnv.nix { inherit inputs; }; # depends on python312Env
            rpi-kms = callPackage ./Nix/pkgs/rpi-kms.nix { inherit inputs; };
            simplejpeg = callPackage ./Nix/pkgs/simplejpeg.nix { };
            v4l2-python3 = callPackage ./Nix/pkgs/v4l2-python3.nix { };
            mlx90460-driver =
              let
                driverPath = "./Nix/pkgs/mlx90460-driver";
              in
              {
                Adafruit-Blinka = callPackage ./${driverPath}/Adafruit-Blinka.nix { };
                adafruit-circuitpython-busdevice =
                  callPackage ./${driverPath}/adafruit-circuitpython-busdevice.nix
                    { };
                adafruit-circuitpython-connectionmanager =
                  callPackage ./${driverPath}/adafruit-circuitpython-connectionmanager.nix
                    { };
                adafruit-circuitpython-mlx90640 =
                  callPackage ./${driverPath}/adafruit-circuitpython-mlx90640.nix
                    { };
                adafruit-circuitpython-requests =
                  callPackage ./${driverPath}/adafruit-circuitpython-requests.nix
                    { };
                adafruit-circuitpython-typing = callPackage ./${driverPath}/adafruit-circuitpython-typing.nix { };
                rpi-ws281x = callPackage ./${driverPath}/rpi-ws281x.nix { };
              };
          };
        };
      systems = [
        "x86_64-linux"
        "aarch64-linux"
      ];
    };
}
