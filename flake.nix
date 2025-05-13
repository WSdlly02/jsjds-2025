{
  description = "JSJDS 2025 work code repo";

  inputs = {
    home-manager = {
      url = "github:nix-community/home-manager/master";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    {
      home-manager,
      self,
      nixpkgs,
    }@inputs:
    let
      inherit (nixpkgs) lib;
      inherit (self.lib) mkPkgs;
      exposedSystems = [
        "x86_64-linux"
        "aarch64-linux"
      ];
      forExposedSystems = lib.genAttrs exposedSystems;
    in
    {
      homeConfigurations."wsdlly02@WSdlly02-RaspberryPi5" = home-manager.lib.homeManagerConfiguration {
        extraSpecialArgs = {
          inherit inputs;
          username = "wsdlly02";
        };
        modules = [
          ./Nix/home-manager
        ];
        pkgs = mkPkgs { system = "aarch64-linux"; };
      };

      overlays.exposedPackages =
        final: prev: with prev; {
          selfRuntime = callPackage ./Nix/pkgs/selfRuntime.nix { inherit inputs; };
          haskellEnv = callPackage ./Nix/pkgs/haskellEnv.nix { };
          python312Env = callPackage ./Nix/pkgs/python312Env.nix { inherit inputs; };
          python312FHSEnv = callPackage ./Nix/pkgs/python312FHSEnv.nix { inherit inputs; }; # depends on python312Env };
        };

      lib.mkPkgs =
        {
          config ? { },
          overlays ? [ ],
          system,
        }:
        import nixpkgs {
          inherit system;
          config = {
            allowAliases = false;
            allowUnfree = true;
            rocmSupport = true;
          } // config;
          overlays = [
            self.overlays.exposedPackages
          ] ++ overlays;
        };

      devShells = forExposedSystems (
        system: with (mkPkgs { inherit system; }); {
          default = callPackage ./Nix/devShells-default.nix { inherit inputs; };
        }
      );

      formatter = forExposedSystems (system: (mkPkgs { inherit system; }).nixfmt-rfc-style);

      legacyPackages = forExposedSystems (
        system:
        with (mkPkgs { inherit system; });
        {
          # python312Packages
          kmsxx-src = callPackage ./Nix/pkgs/kmsxx-src.nix { };
          libcamera = python312Packages.toPythonModule (
            callPackage ./Nix/pkgs/libcamera-raspi.nix { inherit inputs; }
          );
          libpisp = callPackage ./Nix/pkgs/libpisp.nix { };
          ncnn = callPackage ./Nix/pkgs/ncnn.nix { };
          picamera2 = callPackage ./Nix/pkgs/picamera2.nix { };
          pidng = callPackage ./Nix/pkgs/pidng.nix { };
          rpi-kms = python312Packages.toPythonModule (callPackage ./Nix/pkgs/rpi-kms.nix { inherit inputs; });
          simplejpeg = callPackage ./Nix/pkgs/simplejpeg.nix { };
          v4l2-python3 = callPackage ./Nix/pkgs/v4l2-python3.nix { };
          mlx90460-driver =
            let
              driverPath = "Nix/pkgs/mlx90460-driver";
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
        }
        // self.overlays.exposedPackages null (mkPkgs {
          inherit system;
        })
      );
    };
}
