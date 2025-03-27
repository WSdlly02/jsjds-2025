{
  inputs,
  pkgs,
  ...
}:
{
  systemd.user.services.ensure-database-existence = {
    Unit.Description = "Checking beingness of the databases";
    Service = with inputs.self.legacyPackages."aarch64-linux"; {
      Type = "oneshot";
      ExecStart = "${pkgs.writeShellScript "ensure-database-existence.sh" ''
        file_path="/home/wsdlly02/Documents/jsjds-2025/thermal-sensor-data.db"
        src_path="${selfSrc}/thermal-sensor-data.db"
        # 检查目标文件是否存在
        if [ -f "$file_path" ];
          then
            exit 0
          else
            # 尝试复制模板文件
            cp "$src_path" "$file_path"
            exit 1  # 复制成功但文件曾被替换
        fi
      ''}";
    };
    Install = {
      WantedBy = [ "default.target" ];
    };
  };
}
