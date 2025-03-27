{
  inputs,
  pkgs,
  ...
}:
{
  imports = [
    ./fish-config.nix
    ./services/ensure-database-existence.nix
    ./services/thermal-data-processor.nix
    ./services/thermal-data-reader.nix
    ./services/web-central-compositor.nix
  ];
  programs = {
    home-manager.enable = true;
    lazygit.enable = true;
  };
  home = {
    username = "wsdlly02";
    homeDirectory = "/home/wsdlly02";
    packages = with pkgs; [
      btop
      fastfetch
      ncdu
      nixfmt-rfc-style
      nix-output-monitor
      nix-tree
      nnn
      inputs.self.legacyPackages."${system}".haskellEnv
      inputs.self.legacyPackages."${system}".python312Env
    ];
    stateVersion = "25.05";
  };
}
