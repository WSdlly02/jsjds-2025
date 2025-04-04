from picamera2 import Picamera2
from flask import (
    Flask,
    render_template,
    Response,
    request,
    jsonify,
    send_from_directory,
    abort,
)
import waitress
import sys
import cv2
import numpy as np
import psutil
import time
import threading
import screenshotAnalyzer
import os
from datetime import datetime
import sqlite3

app = Flask(__name__)

# Global variables
frame_lock = threading.Lock()
thermal_lock = threading.Lock()
latest_frame = None
sys_info = {"cpu": "0%", "memory": "0%", "temp": "N/A", "fps": "0"}
alarm_playing = False  # 是否警报
alarm_status = True  # 是否开启警报
capture_status = False  # 是否分析图片
selected_model = "best-train1.pt"  # 默认使用的模型
latest_temp_data = 0
self_file_path = os.path.dirname(os.path.realpath(__file__))
# Initialize camera
picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={"size": (2592, 1944)},  # Native resolution
    lores={"size": (1296, 972)},  # Preview stream
    display="main",
    encode="main",
    use_case="video",
    controls={"FrameRate": 30},
    queue=False,
)
picam2.configure(config)
picam2.start()

# 修改照片存储路径
CAPTURED_PATH = os.path.expanduser("~/Pictures/captured")
ANALYZED_PATH = os.path.expanduser("~/Pictures/analyzed")
# os.makedirs(CAPTURED_PATH, exist_ok=True) 已在ensure-runtimes-existence中定义
# os.makedirs(ANALYZED_PATH, exist_ok=True)


def generate_thermal():
    delimiter = b"--FRAME--\n"
    delimiter_len = len(delimiter)
    buffer = bytearray()  # 使用可变缓冲区

    # 预分配内存参数
    frame_header = b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
    frame_footer = b"\r\n"

    while True:
        data = sys.stdin.buffer.read(778)

        if not data:
            break

        buffer.extend(data)  # 避免内存重复分配

        while True:
            idx = buffer.find(delimiter)
            if idx == -1:
                break

            # 使用内存视图零拷贝操作
            frame_data = bytes(memoryview(buffer)[:idx])
            del buffer[: idx + delimiter_len]  # 原地删除已处理数据

            if frame_data:
                try:
                    # 直接输出JPEG二进制流
                    yield frame_header + frame_data + frame_footer
                except Exception as e:
                    print(f"Stream error: {e}")


def stop_alarm():
    global alarm_status
    alarm_status = not alarm_status  # 反转警报开启状态


def adaptive_quality():
    cpu = psutil.cpu_percent()
    # net = psutil.net_io_counters().bytes_sent
    return 90 if cpu < 70 else 75


def capture_camera_frames():
    global latest_frame
    while True:
        with frame_lock:
            frame = picam2.capture_array("main")
            frame = cv2.cvtColor(src=frame, code=cv2.COLOR_RGB2BGR)

            # Sharpen
            # kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
            # frame = cv2.filter2D(frame, -1, kernel)

            quality = adaptive_quality()
            _, jpeg = cv2.imencode(
                ".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality]
            )
            latest_frame = jpeg.tobytes()
        time.sleep(0.03)


def generate_camera():
    while True:
        if latest_frame:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + latest_frame + b"\r\n\r\n"
            )


def get_system_info():
    while True:
        cpu_percent = psutil.cpu_percent()
        mem = psutil.virtual_memory()

        try:
            with open("/sys/class/thermal/thermal_zone0/temp") as f:
                temp = f"{float(f.read()) / 1000:.1f}°C"
        except:
            temp = "N/A"

        with thermal_lock:
            sys_info.update(
                {
                    "cpu": f"{cpu_percent}%",
                    "memory": f"{mem.percent}%",
                    "temp": temp,
                    "fps": f"{np.random.randint(15, 30):02d}",
                }
            )
        time.sleep(1)


def get_temperature_history(limit=100):
    conn = sqlite3.connect(
        os.path.expanduser("~/Documents/databases/thermal-sensor-data.db")
    )
    cursor = conn.cursor()
    cursor.execute(
        "SELECT timestamp, avg_temp, min_temp, max_temp FROM 'thermal-sensor-data' ORDER BY timestamp DESC LIMIT ?",
        (limit,),
    )
    temp_data = cursor.fetchall()
    global latest_temp_data
    latest_temp_data = round(temp_data[0][1], 2)
    conn.close()
    global alarm_playing
    if latest_temp_data > 30:
        alarm_playing = True
        alarm_playing = alarm_playing and alarm_status
    else:
        alarm_playing = False
    return temp_data


def get_captured_photos():
    photos = []
    for filename in os.listdir(CAPTURED_PATH):
        if filename.endswith(".jpg"):
            photos.append(
                {
                    "original": f"captured/{filename}",
                    "analyzed": f"analyzed/{filename}",
                    "timestamp": os.path.splitext(filename)[0],
                }
            )
    return sorted(photos, key=lambda x: x["timestamp"], reverse=True)


def analyzing_screenshots():
    global latest_frame, self_file_path, capture_status, selected_model
    latest_analyzed_frame = None
    while True:
        if capture_status and latest_frame:
            time.sleep(1)
            timestamp = time.time()
            filename = f"{datetime.fromtimestamp(int(timestamp))}.jpg"
            filepath = os.path.join(CAPTURED_PATH, filename)
            model_path = None
            with open(filepath, "wb") as f:
                f.write(latest_frame)
            if selected_model == "best-train1.pt":
                # 选择的模型路径
                model_path = self_file_path + "/models/best-train1.pt"
            elif selected_model == "best-train2.pt":
                model_path = self_file_path + "/models/best-train2.pt"
            latest_analyzed_frame = screenshotAnalyzer.screenshot_process(
                timestamp, latest_frame, filename, model_path
            )
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n"
                + latest_analyzed_frame
                + b"\r\n\r\n"
            )

        elif latest_frame:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + latest_frame + b"\r\n\r\n"
            )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/static/<filename>")
def serve_static(filename):
    return send_from_directory(
        os.path.join(os.path.dirname(__file__), "static"), filename
    )


@app.route("/video_feed")
def video_feed():
    return Response(
        generate_camera(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/thermal_feed")
def thermal_feed():
    return Response(
        generate_thermal(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/system_info")
def system_info():
    return jsonify(sys_info)


@app.route("/start_capture_screenshot")
def start_capture_screenshot():
    global capture_status, selected_model
    selected_model = request.args.get("model")
    capture_status = not capture_status
    return jsonify({"status": "success"})


@app.route("/continuously_analyzing_screenshots")
def continuously_analyzing_screenshots():
    return Response(
        analyzing_screenshots(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# 摁下开始分析按钮，才开始截取画面


@app.route("/check_temperature")
def check_temperature():
    global latest_temp_data
    global alarm_playing
    return jsonify({"max_temp": latest_temp_data, "alarm": alarm_playing})


@app.route("/stop_alarm")
def stop_alarm_route():
    stop_alarm()
    return jsonify({"status": "success"})


@app.route("/get_temperature_data")
def get_temperature_data():
    data = get_temperature_history()
    return jsonify(data)


@app.route("/get_captured_photos")
def get_captured_photos_route():
    photos = get_captured_photos()
    return jsonify(photos)


@app.route("/photos/<path:subdir>/<filename>")
def serve_external_photos(subdir, filename):
    if subdir == "captured":
        return send_from_directory(CAPTURED_PATH, filename)
    elif subdir == "analyzed":
        return send_from_directory(ANALYZED_PATH, filename)
    abort(404)


@app.route("/restart_server")
def restart_server():
    os.system("systemctl --user restart central-compositor.service")
    return jsonify({"status": "success"})


if __name__ == "__main__":
    threading.Thread(target=capture_camera_frames, daemon=True).start()
    threading.Thread(target=get_system_info, daemon=True).start()
    threading.Thread(target=analyzing_screenshots, daemon=True).start()
    waitress.serve(app, host="0.0.0.0", port=8080, threads=12)

# !!! TODO: CHANGE THERMAL THRESHOLD
