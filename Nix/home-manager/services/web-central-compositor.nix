{
  inputs,
  ...
}:
{
  systemd.user.services.web-central-compositor = {
    Unit = {
      Description = "Compositing thermal sensor data & camera data, analyzing photos, operating db";
      After = [
        "thermal-data-reader.service"
        "thermal-data-processor.service"
      ];
      Requires = [
        "thermal-data-reader.service"
        "thermal-data-processor.service"
      ];
    };
    Service = with inputs.self.legacyPackages."aarch64-linux"; {
      # ExecStartPre = "mkfifo /tmp/thermal-data-processor.stdout";
      ExecStart = "${python312Env}/bin/python3.12 ${self-code}/Python/central-compositor.py";
      # ExecStartPost = "rm -f /tmp/thermal-data-processor.stdout";
      StandardInput = "file:/tmp/thermal-data-processor.stdout";
    };
    Install = {
      WantedBy = [ "default.target" ];
    };
  };
}
