# 应当从属于central-compositor.py，被它调用
import os
import sqlite3

conn = sqlite3.connect(
    os.path.expanduser("~/Documents/databases/photos-timestamp-data.db"),
    check_same_thread=False,
)  # 连接照片数据库
cursor = conn.cursor()


def record_timestamp(timestamp):
    cursor.execute(
        """
    INSERT INTO "photos-timestamp-data" (timestamp)
    VALUES (?)
    """,
        (timestamp,),
    )
    conn.commit()  # 记录并转换拍照时间
