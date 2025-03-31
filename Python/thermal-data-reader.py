import os
import time
import struct
import sys
import board
import adafruit_mlx90640
import sqlite3
import numpy

# 初始化 MLX90640
i2c = board.I2C()
mlx = adafruit_mlx90640.MLX90640(i2c)
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_32_HZ  # 32Hz 刷新率
temps = [0.0] * 768

conn = sqlite3.connect(
    os.path.expanduser("~/Documents/databases/thermal-sensor-data.db")
)
cursor = conn.cursor()


def insert_data(timestamp, avg_temp, min_temp, max_temp):
    cursor.execute(
        """
    INSERT INTO "thermal-sensor-data" (timestamp, avg_temp, min_temp, max_temp)
    VALUES (?, ?, ?, ?)
    """,
        (timestamp, avg_temp, min_temp, max_temp),
    )
    conn.commit()


last_processed_second = None
try:
    while True:
        # 读取温度数据（类型为 float）
        mlx.getFrame(temps)
        timestamp = time.time()
        # 打包二进制数据：时间戳 (double) + 768 个温度值 (float)
        # 格式说明：
        #   < : 小端字节序
        #   d : 8字节 double (时间戳)
        #   768f : 768 个 4字节 float
        data_bytes = struct.pack("<d768f", timestamp, *temps)
        # 写入标准输出缓冲区
        sys.stdout.buffer.write(data_bytes)
        sys.stdout.buffer.flush()  # 强制刷新缓冲区

        current_int_second = int(timestamp)
        if last_processed_second != current_int_second:  # 每秒钟向数据库记录一次温度
            last_processed_second = current_int_second
            temp_max = numpy.max(temps)
            temp_min = numpy.min(temps)
            temp_avg = numpy.mean(temps)
            insert_data(timestamp, temp_avg, temp_min, temp_max)
        # time.sleep(1 / 32)
except KeyboardInterrupt:
    print("程序终止")
