{
  inputs,
  pkgs,
  ...
}:
{
  imports = [
    ./fish-config.nix
    ##./python-web-server.nix
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
      ##inputs.self.devShells."aarch64-linux".default
    ];
    stateVersion = "25.05";
  };
}
