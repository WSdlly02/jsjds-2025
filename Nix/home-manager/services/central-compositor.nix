{
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
    Service = with pkgs; {
      Environment = "PATH=${systemd}/bin";
      ExecStartPre = "${coreutils}/bin/sleep 3";
      ExecStart = "${runtimeShell} -c \"${python312Env}/bin/python3.12 ${selfRuntime}/thermal-data-reader.py | ${selfRuntime}/thermal-data-processor | ${python312Env}/bin/python3.12 ${selfRuntime}/central-compositor.py\"";
    };
    Install = {
      WantedBy = [ "default.target" ];
    };
  };
}
