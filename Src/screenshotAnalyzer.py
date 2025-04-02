# 应当从属于central-compositor.py，被它调用
import os
import sqlite3
import inference

conn = sqlite3.connect(
    os.path.expanduser("~/Documents/databases/photos-timestamp-data.db"),
    check_same_thread=False,
)  # 连接照片数据库
cursor = conn.cursor()


def screenshot_process(timestamp, last_frame, filename, model_path):
    cursor.execute(
        """
    INSERT INTO "photos-timestamp-data" (timestamp)
    VALUES (?)
    """,
        (timestamp,),
    )
    conn.commit()  # 记录并转换拍照时间
    with open(
        os.path.expanduser(f"~/Pictures/captured/{filename}"), "wb"
    ) as f:  # 保存截图
        f.write(last_frame)
    model_path = model_path
    inference.inference_screenshot(filename, model_path)  # 将截图交给被调用函数推理
