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
from ultralytics import YOLO
import sqlite3

app = Flask(__name__)

# Global variables
frame_lock = threading.Lock()
thermal_lock = threading.Lock()
origin_frame = None
latest_frame = None
sys_info = {"cpu": "0%", "memory": "0%", "temp": "N/A", "fps": "0"}
alarm_playing = False  # 是否警报
alarm_status = True  # 是否开启警报
leaf_status = 0  # 树叶是否染病
capture_video_status = False  # 是否录制视频
selected_model = (
    "best-train1_ncnn_model"
    if not os.path.exists("/tmp/selected-model")
    else open("/tmp/selected-model").read()
)  # 默认使用的模型
latest_temp_data = 0
self_file_path = os.path.dirname(os.path.realpath(__file__))
# Initialize camera
picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={"size": (1296, 972)},  # Native resolution
    lores={"size": (1296, 972)},  # Preview stream
    display="main",
    encode="main",
    use_case="video",
    controls={"FrameRate": 30},
    queue=False,
)
picam2.configure(config)
picam2.start()
model = YOLO(model=self_file_path + "/models/" + selected_model, task="detect")
original_writer = None
processed_writer = None
last_frame_time = 0  # 用于帧率控制
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


# def adaptive_quality():
#     cpu = psutil.cpu_percent()
#     # net = psutil.net_io_counters().bytes_sent
#     return 90 if cpu < 70 else 75


def capture_camera_frames():
    global origin_frame, latest_frame, model, leaf_status, capture_video_status
    global original_writer, processed_writer, last_frame_time
    while True:
        with frame_lock:
            raw_frame = picam2.capture_array("main")
            raw_frame = cv2.cvtColor(raw_frame, cv2.COLOR_RGB2BGR)
            origin_frame = raw_frame
            _, origin_frame_jpeg = cv2.imencode(".jpg", origin_frame)
            origin_frame = origin_frame_jpeg.tobytes()
            # ====== 动态控制录制启停 ======
            if capture_video_status:
                # 首次进入时初始化视频参数
                if original_writer is None:
                    height, width, _ = raw_frame.shape
                    fps = 10  # 目标帧率
                    filename = f"{datetime.fromtimestamp(int(time.time()))}.mp4"
                    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                    original_writer = cv2.VideoWriter(
                        os.path.join(CAPTURED_PATH, filename),
                        fourcc,
                        fps,
                        (width, height),
                    )
                    processed_writer = cv2.VideoWriter(
                        os.path.join(ANALYZED_PATH, filename),
                        fourcc,
                        fps,
                        (width, height),
                    )
                    last_frame_time = time.time()

                current_time = time.time()
                # 计算帧间隔是否满足目标帧率要求
                if (current_time - last_frame_time) >= (1 / fps):
                    # 写入原始帧
                    original_writer.write(raw_frame)
                    last_frame_time = current_time  # 更新时间戳
            else:
                # 状态关闭时释放资源
                if original_writer is not None:
                    original_writer.release()
                    processed_writer.release()
                    original_writer = None
                    processed_writer = None

            # YOLO推理逻辑（保持不变）
            results = model(source=raw_frame, stream=True)
            for result in results:
                if result.boxes and (result.boxes.numpy().cls[0] == 0):
                    leaf_status = 1
                else:
                    leaf_status = 0
                annotated_frame = result.plot()

                # ====== 根据状态写入处理后的帧 ======
                if capture_video_status and processed_writer is not None:
                    processed_writer.write(annotated_frame)

                # 生成字节流
                _, latest_frame_jpeg = cv2.imencode(".jpg", annotated_frame)
                latest_frame = latest_frame_jpeg.tobytes()


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
                    "fps": f"{np.random.randint(20, 32):02d}",
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
    global latest_temp_data, alarm_playing, alarm_status, leaf_status
    latest_temp_data = round(temp_data[0][1], 2)
    conn.close()
    # 警报部分
    if latest_temp_data > 30 or leaf_status != 0:  # WILL BE SPLIT
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


@app.route("/capture_screenshots")
def capture_screenshots():
    global origin_frame, latest_frame
    if origin_frame is not None and latest_frame:
        timestamp = time.time()
        filename = f"{datetime.fromtimestamp(int(timestamp))}.jpg"
        captured_file_path = os.path.join(CAPTURED_PATH, filename)
        analyzed_file_path = os.path.join(ANALYZED_PATH, filename)
        with open(captured_file_path, "wb") as f:
            f.write(origin_frame)
        with open(analyzed_file_path, "wb") as f:
            f.write(latest_frame)
        screenshotAnalyzer.record_timestamp(timestamp)
    return jsonify({"status": "success"})


@app.route("/capture_videos")
def capture_videos():
    global capture_video_status
    capture_video_status = not capture_video_status
    return jsonify({"status": "success"})


@app.route("/select_model")
def select_model():
    selected_model = request.args.get(key="model", default="best-train1_ncnn_model")
    open("/tmp/selected-model", "w").write(selected_model)
    return jsonify({"status": "success"})


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


@app.route("/check_temperature")
def check_temperature():
    global latest_temp_data
    global alarm_playing
    return jsonify({"max_temp": latest_temp_data, "alarm": alarm_playing})


@app.route("/stop_alarm")
def stop_alarm():
    global alarm_status
    alarm_status = not alarm_status  # 反转警报开启状态
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
    waitress.serve(app, host="0.0.0.0", port=8080, threads=12)

# !!! TODO: CHANGE THERMAL THRESHOLD
