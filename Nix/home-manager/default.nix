{
  username,
  pkgs,
  ...
}:
{
  imports = [
    ./sh.nix
    ./services/central-compositor.nix
    ./services/ensure-runtimes-existence.nix
  ];
  programs = {
    command-not-found = {
      enable = true;
      dbPath = "/nix/programs.sqlite";
    };
    home-manager.enable = true;
    lazygit.enable = true;
    nh = {
      enable = true;
      flake = "/home/wsdlly02/Documents/NixOS-Configurations";
    };
  };
  home = {
    inherit username;
    homeDirectory = "/home/${username}";
    packages = with pkgs; [
      fastfetch
      haskellEnv
      nix-tree
      python312Env
    ];
    stateVersion = "25.05";
  };
  targets.genericLinux.enable = true;
}
