import sqlite3
import inference
from datetime import datetime

conn = sqlite3.connect("~/Documents/databases/photos-timestamp-data.db")
cursor = conn.cursor()


def screenshot_process(timestamp, last_frame):
    cursor.execute(
        """
    INSERT INTO "photos-timestamp-data" (timestamp)
    VALUES (?)
    """,
        (timestamp),
    )
    conn.commit()
    filename = datetime.fromtimestamp(int(timestamp))  # 记录并转换拍照时间
    with open(f"~/Photos/captured/{filename}.jpg", "wb") as f:
        f.write(last_frame)
    inference.inference_screenshot(last_frame, filename)
