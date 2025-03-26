{
  inputs,
  ...
}:
{
  systemd.user.services.thermal-data-processor = {
    Unit = {
      Description = "Processing thermal sensor data";
      After = [ "thermal-data-reader.service" ];
      Requires = [ "thermal-data-reader.service" ];
    };
    Service = with inputs.self.legacyPackages."aarch64-linux"; {
      ExecStartPre = "mkfifo /tmp/thermal-data-processor.stdout";
      ExecStart = "${self-code}/Haskell/thermal-data-processor";
      ExecStartPost = "rm -f /tmp/thermal-data-processor.stdout";
      StandardInput = "file:/tmp/thermal-data-reader.stdout";
      StandardOutput = "file:/tmp/thermal-data-processor.stdout";
    };
    Install = {
      WantedBy = [ "default.target" ];
    };
  };
}
