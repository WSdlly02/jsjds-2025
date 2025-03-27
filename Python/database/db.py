import sys
import struct
import sqlite3
import numpy

# 连接数据库（不存在则新建）
conn = sqlite3.connect("thermal-sensor-data.db")
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


def query_by_time_range(start, end):
    cursor.execute(
        """
    SELECT * FROM "thermal-sensor-data"
    WHERE timestamp BETWEEN ? AND ?
    ORDER BY timestamp DESC
    """,
        (start.isoformat(), end.isoformat()),
    )

    return cursor.fetchall()


def query_recent():
    cursor.execute(
        """
    SELECT * FROM "thermal-sensor-data"
    ORDER BY timestamp DESC
    """
    )

    return cursor.fetchall()

    # 使用示例
    # start_time = datetime.now() - timedelta(hours=1)
    # end_time = datetime.now()


buffer = bytearray()
last_processed_second = None  # 记录上次处理的秒数

try:
    while True:
        # 从标准输入读取数据
        data = sys.stdin.buffer.read(4096)
        if not data:
            break
        buffer.extend(data)

        # 处理所有完整数据包
        while len(buffer) >= 3080:  # 3080 = 8(d) + 768*4(f)
            # 提取并移除一个数据包
            packet = buffer[:3080]
            del buffer[:3080]

            try:
                # 解析二进制数据
                unpacked = struct.unpack("<d768f", packet)
            except struct.error as e:
                print(f"数据解析失败: {e}", file=sys.stderr)
                continue

            timestamp = unpacked[0]
            current_second = int(timestamp)  # 取整数秒
            temps = unpacked[1:]  # 768个温度值

            # 如果是新的一秒则处理
            if last_processed_second != current_second:
                last_processed_second = current_second

                # 计算统计值
                temp_max = numpy.max(temps)
                temp_min = numpy.min(temps)
                temp_avg = numpy.mean(temps)

                # 格式化输出
                # print(
                #     f"[{timestamp:.6f}] "
                #     f"MAX: {temp_max:.2f}℃ | "
                #     f"MIN: {temp_min:.2f}℃ | "
                #     f"AVG: {temp_avg:.2f}℃"
                # )
                insert_data(timestamp, temp_avg, temp_min, temp_max)
                # print(query_recent())  # 打印前n个数据
except KeyboardInterrupt:
    print("\n程序已终止")
except BrokenPipeError:
    pass  # 避免管道关闭时的错误
