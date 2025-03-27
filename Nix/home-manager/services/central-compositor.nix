{
  inputs,
  pkgs,
  ...
}:
{
  systemd.user.services.central-compositor = {
    Unit = {
      Description = "Compositing thermal sensor data & camera data, analyzing photos, operating db";
      After = [ "ensure-database-existence.service" ];
      Requires = [ "ensure-database-existence.service" ];
    };
    Service = with inputs.self.legacyPackages."aarch64-linux"; {
      ExecStart = "${pkgs.runtimeShell} -c \"${python312Env}/bin/python3.12 ${selfSrc}/Python/thermal-data-reader.py | /home/wsdlly02/Documents/jsjds-2025/Haskell/thermal-data-processor | ${python312Env}/bin/python3.12 ${selfSrc}/Python/web-central-compositor.py\"";
      #ExecStopPost = "rm -f %%t/thermal-data-reader.stdout";
      #StandardOutput = "file:%%t/thermal-data-reader.stdout";
    };
    Install = {
      WantedBy = [ "default.target" ];
    };
  };
}
