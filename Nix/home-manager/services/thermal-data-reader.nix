{
  inputs,
  pkgs,
  ...
}:
{
  systemd.user.services.thermal-data-reader = {
    Unit = {
      Description = "Reading thermal sensor data";
      After = [ "ensure-database-existence.service" ];
      Requires = [ "ensure-database-existence.service" ];
    };
    Service = with inputs.self.legacyPackages."aarch64-linux"; {
      ExecStartPre = "mkfifo /tmp/thermal-data-reader.stdout";
      ExecStart = "${python312Env}/bin/python3.12 ${selfSrc}/Python/thermal-data-reader.py";
      ExecStartPost = "rm -f /tmp/thermal-data-reader.stdout";
      StandardOutput = "file:/tmp/thermal-data-reader.stdout";
    };
    Install = {
      WantedBy = [ "default.target" ];
    };
  };
}
