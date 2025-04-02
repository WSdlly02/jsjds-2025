{
  inputs,
  pkgs,
  ...
}:
{
  systemd.user.services.ensure-runtimes-existence = {
    Unit.Description = "Checking beingness of the runtimes";
    Service = with inputs.self.legacyPackages."aarch64-linux"; {
      Type = "oneshot";
      ExecStart = "${pkgs.writeScript "ensure-runtimes-existence.py" ''
        #!${python312Env}/bin/python3.12
        import os
        import shutil


        def check_and_sync():
            # 定义需要创建的目录
            directories = [
                os.path.expanduser("~/Documents/databases"),
                os.path.expanduser("~/Pictures/analyzed"),
                os.path.expanduser("~/Pictures/captured"),
            ]

            # 定义需要同步的文件对 (源文件, 目标文件)
            file_pairs = [
                ("${selfRuntime}/photos-timestamp-data.db", os.path.expanduser("~/Documents/databases/photos-timestamp-data.db")),
                ("${selfRuntime}/thermal-sensor-data.db", os.path.expanduser("~/Documents/databases/thermal-sensor-data.db")),
            ]

            try:
                # 创建目录（如果不存在）
                for dir_path in directories:
                    os.makedirs(dir_path, exist_ok=True)
                    os.chmod(dir_path, 0o755)
                    print(f"Directory ensured: {dir_path}")

                # 同步文件（如果目标不存在）
                for src, dest in file_pairs:
                    if not os.path.exists(src):
                        raise FileNotFoundError(f"模板文件不存在: {src}")

                    if not os.path.exists(dest):
                        shutil.copy(src, dest)
                        os.chmod(dest, 0o644)
                        print(f"File copied: {src} -> {dest}")

            except Exception as e:
                print(f"操作失败: {str(e)}")
                exit(1)  # 异常时返回错误状态码


        if __name__ == "__main__":
            check_and_sync()
            print("操作完成")

      ''}";
    };
    Install = {
      WantedBy = [ "default.target" ];
    };
  };
}
