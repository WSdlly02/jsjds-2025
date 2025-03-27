{
  description = "JSJDS 2025 work code repo";

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
      flake.homeConfigurations."wsdlly02" = home-manager.lib.homeManagerConfiguration {
        extraSpecialArgs = { inherit inputs; };
        modules = [
          ./Nix/home-manager
        ];
        pkgs = import nixpkgs {
          system = "aarch64-linux";
        };
      };
      flake.overlays = {
        pytorch-overlay = final: prev: {
          # python312 = prev.python312.override {
          #   packageOverrides = pyfinal: pyprev: { torch = pyprev.torch.override { vulkanSupport = true; }; };
          # };
        };
      };
      perSystem =
        {
          system,
          ...
        }:
        let
          pkgs = import nixpkgs {
            inherit system;
            config = {
              allowUnfree = true;
            };
            overlays = [ self.overlays.pytorch-overlay ];
          };
          inherit (pkgs)
            callPackage
            mkShell
            ;
          inherit (pkgs.python312Packages)
            toPythonModule
            ;
        in
        {
          devShells = {
            default = callPackage ./Nix/devShells-default.nix { inherit inputs; };
          };

          formatter = pkgs.nixfmt-rfc-style;

          legacyPackages = {
            # system pkgs
            selfSrc = callPackage ./Nix/pkgs/selfSrc.nix { };
            thermal-data-processor = callPackage ./Nix/pkgs/thermal-data-processor.nix { inherit inputs; };
            haskellEnv = callPackage ./Nix/pkgs/haskellEnv.nix { }; # IMPORTANT !!!
            python312Env = callPackage ./Nix/pkgs/python312Env.nix { inherit inputs; }; # IMPORTANT !!!
            python312FHSEnv = callPackage ./Nix/pkgs/python312FHSEnv.nix { inherit inputs; }; # depends on python312Env
            # python312Packages
            kmsxx-src = callPackage ./Nix/pkgs/kmsxx-src.nix { };
            libcamera = toPythonModule (callPackage ./Nix/pkgs/libcamera-raspi.nix { inherit inputs; });
            libpisp = callPackage ./Nix/pkgs/libpisp.nix { };
            picamera2 = callPackage ./Nix/pkgs/picamera2.nix { };
            pidng = callPackage ./Nix/pkgs/pidng.nix { };
            rpi-kms = toPythonModule (callPackage ./Nix/pkgs/rpi-kms.nix { inherit inputs; });
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
