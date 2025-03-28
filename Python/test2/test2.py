from flask import Flask, render_template, Response, request, jsonify
import cv2
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import numpy as np
import base64
import os

app = Flask(__name__)

# 数据库配置
engine = db.create_engine("sqlite:///temperatures.db")
metadata = db.MetaData()

temperature = db.Table(
    "temperature",
    metadata,
    db.Column("id", db.Integer, primary_key=True),
    db.Column("timestamp", db.DateTime),
    db.Column("value", db.Float),
)
metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# 全局变量存储当前温度
current_temp = 0


def get_temperature():
    global current_temp
    current_temp = np.random.uniform(30, 70)  # 模拟温度数据
    return current_temp


# 创建截图保存目录
if not os.path.exists("screenshots"):
    os.makedirs("screenshots")

# 视频捕获
camera = cv2.VideoCapture(0)


def gen_frames():
    while True:
        success, frame = camera.read()
        if success:
            ret, buffer = cv2.imencode(".jpg", frame)
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
            )


def gen_thermal_frames():
    while True:
        temp = get_temperature()
        thermal_image = np.random.randint(0, 255, (480, 640), dtype=np.uint8)
        thermal_colored = cv2.applyColorMap(thermal_image, cv2.COLORMAP_JET)
        cv2.putText(
            thermal_colored,
            f"Temp: {temp:.1f}C",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
        )
        ret, buffer = cv2.imencode(".jpg", thermal_colored)
        session.execute(
            temperature.insert().values(timestamp=datetime.now(), value=temp)
        )
        session.commit()
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
        )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/thermal_feed")
def thermal_feed():
    return Response(
        gen_thermal_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/capture", methods=["POST"])
def capture():
    data = request.get_json()
    img_data = data["image"].split(",")[1]
    img_bytes = base64.b64decode(img_data)
    filename = f"screenshots/{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    with open(filename, "wb") as f:
        f.write(img_bytes)
    return jsonify(status="success")


@app.route("/current_temperature")
def get_current_temp():
    return jsonify(temp=current_temp)


@app.route("/temperature_history")
def temperature_history():
    query = session.query(temperature).order_by(temperature.c.timestamp).all()
    history = [
        {"time": row.timestamp.strftime("%Y-%m-%d %H:%M:%S"), "temp": row.value}
        for row in query
    ]
    return jsonify(history)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
