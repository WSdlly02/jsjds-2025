{
  inputs,
  pkgs,
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
      #ExecStartPre = "${pkgs.coreutils}/bin/mkfifo %%t/thermal-data-processor.stdout";
      ExecStart = "/home/wsdlly02/Documents/jsjds-2025/Haskell/thermal-data-processor"; # !!! JUST SUBSITUTE
      ExecStopPost = "rm -f %%t/thermal-data-processor.stdout";
      StandardInput = "file:%%t/thermal-data-reader.stdout";
      StandardOutput = "file:%%t/thermal-data-processor.stdout";
    };
    Install = {
      WantedBy = [ "default.target" ];
    };
  };
}
