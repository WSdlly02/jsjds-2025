{
  inputs,
  ...
}:
{
  systemd.user.services.photo-recognizer = {
    Unit.Description = "Checking beingness of the databases";
    Service = with inputs.self.legacyPackages."aarch64-linux"; {
      # ExecStartPre = "mkfifo /tmp/thermal-data-processor.stdout";
      ExecStart = "";
      # ExecStartPost = "rm -f /tmp/thermal-data-processor.stdout";
      # StandardInput = "file:/tmp/thermal-data-processor.stdout";
    };
    Install = {
      WantedBy = [ "default.target" ];
    };
  };
}
