{
  inputs,
  ...
}:
{
  systemd.user.services.photo-recognizer = {
    Unit.Description = "Checking beingness of the databases";
    Service = with inputs.self.legacyPackages."aarch64-linux"; {
      # ExecStartPre = "${pkgs.coreutils}/bin/mkfifo %%t/thermal-data-processor.stdout";
      ExecStart = "";
      # ExecStopPost = "rm -f %%t/thermal-data-processor.stdout";
      # StandardInput = "file:%%t/thermal-data-processor.stdout";
    };
    Install = {
      WantedBy = [ "default.target" ];
    };
  };
}
