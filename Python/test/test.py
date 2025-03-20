from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO
import cv2
import numpy as np
import base64
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app)

# 模拟温度传感器
temperature = 25
temperature_threshold = 30

# 模拟摄像头
camera = cv2.VideoCapture(0)


def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


def generate_thermal_frames():
    while True:
        # 模拟热成像数据
        thermal_frame = np.random.randint(0, 256, (480, 640), dtype=np.uint8)
        ret, buffer = cv2.imencode(".jpg", thermal_frame)
        thermal_frame = buffer.tobytes()
        yield (
            b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + thermal_frame + b"\r\n"
        )


def check_temperature():
    global temperature
    while True:
        # 模拟温度变化
        temperature = np.random.randint(20, 35)
        if temperature >= temperature_threshold:
            socketio.emit("temperature_alert", {"temperature": temperature})
        time.sleep(5)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/thermal_feed")
def thermal_feed():
    return Response(
        generate_thermal_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/database")
def database():
    # 这里可以返回数据库中的图片
    return send_from_directory("database", "image.jpg")


if __name__ == "__main__":
    threading.Thread(target=check_temperature).start()
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
