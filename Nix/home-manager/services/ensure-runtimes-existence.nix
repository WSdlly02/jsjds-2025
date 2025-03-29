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
      RemainAfterExit = "yes";
      ExecStart = "${pkgs.writeShellScript "ensure-runtimes-existence.sh" ''
        # 定义需要创建的目录
        directories=(
          "~/Pictures/analyzed"
          "~/Pictures/captured"
        )

        # 定义需要同步的文件列表（格式：模板文件:目标文件）
        file_pairs=(
        "${selfSrc}/thermal-sensor-data.db:~/Documents/databses/thermal-sensor-data.db"
        "${selfSrc}/photos-timestamp-data.db:~/Documents/databses/photos-timestamp-data.db"
        )

        # 状态标记
        files_copied=0

        # 函数：处理目录创建
        create_directories() {
          for dir in "$\{directories[@]}"; do
            if [ ! -d "$dir" ]; then
              echo "创建目录: $dir"
              if ! mkdir -p "$dir"; then
                echo "错误：目录创建失败 $dir" >&2
                exit 2
              fi
            fi
          done
        }

        # 函数：处理文件同步
        sync_files() {
            for pair in "$\{file_pairs[@]}"; do
                IFS=':' read -r src dest <<< "$pair"
                
                # 检查模板文件是否存在
                if [ ! -f "$src" ]; then
                    echo "错误：模板文件不存在 $src" >&2
                    exit 2
                fi

                # 执行文件同步
                if [ ! -f "$dest" ]; then
                    echo "正在同步文件: $dest"
                    if cp "$src" "$dest"; then
                        files_copied=1
                    else
                        echo "错误：文件复制失败 $src -> $dest" >&2
                        exit 2
                    fi
                fi
            done
        }

        # 主执行流程
        create_directories
        sync_files

        # 根据同步结果返回状态码
        # exit $files_copied
      ''}";
    };
    Install = {
      WantedBy = [ "default.target" ];
    };
  };
}
