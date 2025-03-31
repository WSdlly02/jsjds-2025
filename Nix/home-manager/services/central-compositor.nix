{
  inputs,
  pkgs,
  ...
}:
{
  systemd.user.services.central-compositor = {
    Unit = {
      Description = "Compositing thermal sensor data & camera data, analyzing photos, operating db";
      After = [ "ensure-runtimes-existence.service" ];
      Requires = [ "ensure-runtimes-existence.service" ];
    };
    Service = with inputs.self.legacyPackages."aarch64-linux"; {
      Environment = "PATH=${pkgs.systemd}/bin";
      ExecStartPre = "${pkgs.coreutils}/bin/sleep 5";
      ExecStart = "${pkgs.runtimeShell} -c \"${python312Env}/bin/python3.12 ${selfSrc}/Python/thermal-data-reader.py | ${thermal-data-processor}/bin/thermal-data-processor | ${python312Env}/bin/python3.12 ${selfSrc}/Python/central-compositor.py\"";
    };
    Install = {
      WantedBy = [ "default.target" ];
    };
  };
}
