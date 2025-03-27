{
  inputs,
  ...
}:
{
  systemd.user.services.web-central-compositor = {
    Unit = {
      Description = "Compositing thermal sensor data & camera data, analyzing photos, operating db";
      After = [ "thermal-data-processor.service" ];
      Requires = [ "thermal-data-processor.service" ];
    };
    Service = with inputs.self.legacyPackages."aarch64-linux"; {
      # ExecStartPre = "mkfifo /tmp/thermal-data-processor.stdout";
      ExecStart = "${python312Env}/bin/python3.12 ${selfSrc}/Python/web-central-compositor.py";
      # ExecStartPost = "rm -f /tmp/thermal-data-processor.stdout";
      StandardInput = "file:/tmp/thermal-data-processor.stdout";
    };
    Install = {
      WantedBy = [ "default.target" ];
    };
  };
}
