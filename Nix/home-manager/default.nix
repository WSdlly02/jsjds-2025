{
  inputs,
  pkgs,
  username,
  ...
}:
{
  imports = [
    ./fish-config.nix
    ./services/central-compositor.nix
    ./services/ensure-runtimes-existence.nix
  ];
  programs = {
    home-manager.enable = true;
    lazygit.enable = true;
  };
  home = {
    inherit username;
    homeDirectory = "/home/${username}";
    packages = with pkgs; [
      fastfetch
      nix-tree
    ];
    stateVersion = "25.05";
  };
}
