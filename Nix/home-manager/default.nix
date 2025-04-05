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
      btop
      fastfetch
      ncdu
      nixfmt-rfc-style
      nix-output-monitor
      nix-tree
      yazi
      inputs.self.legacyPackages."${system}".haskellEnv
      inputs.self.legacyPackages."${system}".python312Env
    ];
    stateVersion = "25.05";
  };
}
