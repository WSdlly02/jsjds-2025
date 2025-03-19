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
      aria2
      btop
      fastfetch
      ncdu
      nixfmt-rfc-style
      nix-output-monitor
      nix-tree
      nnn
      inputs.self.devShells."pkgs.system".default
    ];
    stateVersion = "25.05";
  };
}
