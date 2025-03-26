import sqlite3
import time

# 连接数据库（不存在则新建）
conn = sqlite3.connect("thermal-sensor-data.db")
cursor = conn.cursor()


def insert_data(avg_temp, min_temp, max_temp):
    current_time = int(time.time())  # ISO8601格式
    cursor.execute(
        """
    INSERT INTO "thermal-sensor-data" (timestamp, avg_temp, min_temp, max_temp)
    VALUES (?, ?, ?, ?)
    """,
        (current_time, avg_temp, min_temp, max_temp),
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


def query_recent(n):
    cursor.execute(
        """
    SELECT * FROM "thermal-sensor-data"
    ORDER BY timestamp DESC
    LIMIT ?
    """,
        (n,),
    )

    return cursor.fetchall()


# 使用示例
# start_time = datetime.now() - timedelta(hours=1)
# end_time = datetime.now()
insert_data(20, 15, 30)
print(query_recent(1))  # 打印前n个数据
