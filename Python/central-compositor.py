from picamera2 import Picamera2
from flask import (
    Flask,
    render_template_string,
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


@app.route("/")
def index():
    return render_template_string(
        """
    <!DOCTYPE html>
    <html>
        <head>
            <meta charset="UTF-8">
            <title>智能监控系统</title>
            <link rel="icon" type="image/png" sizes="16x16"  href="/static/favicons/favicon-16x16.png">
            <link rel="icon" type="image/png" sizes="32x32"  href="/static/favicons/favicon-32x32.png">
            <link rel="apple-touch-icon" sizes="57x57" href="/static/favicons/apple-touch-icon-57x57.png">
            <link rel="apple-touch-icon" sizes="60x60" href="/static/favicons/apple-touch-icon-60x60.png">
            <link rel="apple-touch-icon" sizes="72x72" href="/static/favicons/apple-touch-icon-72x72.png">
            <link rel="apple-touch-icon" sizes="76x76" href="/static/favicons/apple-touch-icon-76x76.png">
            <link rel="icon" type="image/png" sizes="96x96"  href="/static/favicons/apple-touch-icon-96x96.png">
            <link rel="apple-touch-icon" sizes="114x114" href="/static/favicons/apple-touch-icon-114x114.png">
            <link rel="apple-touch-icon" sizes="120x120" href="/static/favicons/apple-touch-icon-120x120.png">
            <link rel="apple-touch-icon" sizes="144x144" href="/static/favicons/apple-touch-icon-144x144.png">
            <link rel="apple-touch-icon" sizes="152x152" href="/static/favicons/apple-touch-icon-152x152.png">
            <link rel="apple-touch-icon" sizes="180x180" href="/static/favicons/apple-touch-icon-180x180.png">
            <link rel="icon" type="image/png" sizes="192x192"  href="/static/favicons/android-icon-192x192.png">
            <meta name="msapplication-TileColor" content="#ffffff">
            <meta name="theme-color" content="#ffffff">
            <style>
                body {
                    margin: 0;
                    padding: 20px;
                    background: #1a1a1a;
                    color: white;
                    font-family: Arial, sans-serif;
                }
                .menu {
                    display: grid;
                    grid-template-columns: repeat(5, 1fr);
                    gap: 10px;
                    margin-bottom: 20px;
                }
                .menu-item {
                    background: #2a2a2a;
                    padding: 20px;
                    text-align: center;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: all 0.3s;
                }
                .menu-item:hover {
                    background: #4CAF50;
                    transform: scale(1.05);
                }
                .content {
                    background: #2a2a2a;
                    border-radius: 8px;
                    padding: 20px;
                    min-height: 70vh;
                }
                .hidden {
                    display: none;
                }
                .video-container {
                    position: relative;
                    width: 100%;
                    height: 80vh;
                }
                .video-controls {
                    position: absolute;
                    right: 40px;
                    top: 240px;
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                    z-index: 1000;
                }
                button {
                    padding: 8px 16px;
                    background: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                }
                th, td {
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #444;
                }
                th {
                    background-color: #333;
                }
                .photo-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                    gap: 20px;
                }
                .photo-item {
                    position: relative;
                    overflow: hidden;
                    border-radius: 8px;
                }
                .photo-item img {
                    width: 100%;
                    height: auto;
                    transition: transform 0.3s;
                }
                .photo-item:hover img {
                    transform: scale(1.05);
                }
                .photo-info {
                    padding: 10px;
                    background: rgba(0,0,0,0.7);
                    position: absolute;
                    bottom: 0;
                    width: 100%;
                }
                .alarm {
                    color: red;
                    font-weight: bold;
                    animation: blink 1s infinite;
                }
                @keyframes blink {
                    0% { opacity: 1; }
                    50% { opacity: 0.5; }
                    100% { opacity: 1; }
                }
                .option-list {
                    width: 100%;
                    margin: 10px 0;
                    border-radius: 4px;
                    overflow: hidden;
                }
                .option-item {
                    padding: 8px 16px;
                    background: #3a3a3a;
                    color: white;
                    cursor: pointer;
                    transition: all 0.3s;
                    border-bottom: 1px solid #444;
                }
                .option-item:hover {
                    background: #4CAF50;
                }
                .option-item:last-child {
                    border-bottom: none;
                }
            </style>
        </head>
        <body>
            <h1>智能监控系统</h1>

            <audio id="alarm-audio" src="/static/alarm.wav"></audio>

            <div class="menu">
                <div class="menu-item" onclick="showSection('monitor')">实时监控</div>
                <div class="menu-item" onclick="showSection('thermal')">热成像监测</div>
                <div class="menu-item" onclick="showSection('database')">数据库</div>
                <div class="menu-item" onclick="showSection('system')">系统信息</div>
                <div class="menu-item" onclick="showSection('gallery')">照片墙</div>
            </div>
            
            <div class="content">
                <!-- Monitor Section -->
                <div id="monitor">
                    <h2>实时监控</h2>
                    <div class="video-container">
                        <img id="monitor-video" src="/video_feed" style="width:60%;">
                    </div>
                    <div class="video-controls">
                        <button onclick="zoomIn()">放大</button>
                        <button onclick="zoomOut()">缩小</button>
                        <button onclick="captureScreenshot()">截屏</button>
                        <div class="option-list">
                            <div class="option-item" data-value="best-train1.pt" onclick="handleSelection(this)">best-train1.pt</div>
                            <div class="option-item" data-value="best-train2.pt" onclick="handleSelection(this)">best-train2.pt</div>
                        </div>
                        <select id="zoom-level" onchange="changeZoom()">
                            <option value="100">100%</option>
                            <option value="150">150%</option>
                            <option value="200">200%</option>
                            <option value="50">50%</option>
                        </select>
                    </div>
                </div>
                
                <!-- Thermal Section -->
                <div id="thermal" class="hidden">
                    <h2>热成像监测 <span id="alarm-indicator" class="hidden alarm">高温警报!</span></h2>
                    <div class="video-container">
                        <img id="thermal-video" src="/thermal_feed" style="width:60%;">
                    </div>
                    <div class="video-controls">
                        <button onclick="stopAlarm()">关闭/开启警报</button>
                        <button onclick="restartThermal()">重启热成像摄像头</button>
                        <div id="max-temp">当前最高温度: 加载中...</div>
                    </div>
                </div>
                
                <!-- Database Section -->
                <div id="database" class="hidden">
                    <h2>温度历史数据</h2>
                    <table id="temp-data">
                        <thead>
                            <tr>
                                <th>时间戳</th>
                                <th>平均温度 (°C)</th>
                                <th>最低温度 (°C)</th>
                                <th>最高温度 (°C)</th>
                            </tr>
                        </thead>
                        <tbody id="temp-data-body">
                            <!-- Data will be loaded here -->
                        </tbody>
                    </table>
                </div>
                
                <!-- System Info Section -->
                <div id="system" class="hidden">
                    <h2>系统信息</h2>
                    <div class="stat-item">
                        <h3>CPU 使用率</h3>
                        <div id="cpu">Loading...</div>
                    </div>
                    <div class="stat-item">
                        <h3>内存使用</h3>
                        <div id="memory">Loading...</div>
                    </div>
                    <div class="stat-item">
                        <h3>系统温度</h3>
                        <div id="temp">Loading...</div>
                    </div>
                    <div class="stat-item">
                        <h3>视频FPS</h3>
                        <div id="fps">Loading...</div>
                    </div>
                </div>
                
                <!-- Gallery Section -->
                <div id="gallery" class="hidden">
                    <h2>照片墙</h2>
                    <div class="photo-grid" id="photo-grid">
                        <!-- Photos will be loaded here -->
                    </div>
                </div>
            </div>

            <script>
                // Show the selected section
                function showSection(sectionId) {
                    document.querySelectorAll('.content > div').forEach(div => {
                        div.classList.add('hidden');
                    });
                    document.getElementById(sectionId).classList.remove('hidden');
                    
                    // Load data for certain sections
                    if (sectionId === 'database') {
                        loadTemperatureData();
                    } else if (sectionId === 'gallery') {
                        loadGallery();
                    }
                }
                
                // Video controls
                let currentZoom = 100;
                function zoomIn() {45.2
                    currentZoom += 25;
                    document.getElementById('monitor-video').style.width = currentZoom + '%';
                }
                
                function zoomOut() {
                    if (currentZoom > 25) {
                        currentZoom -= 25;
                        document.getElementById('monitor-video').style.width = currentZoom + '%';
                    }
                }
                
                function changeZoom() {
                    currentZoom = parseInt(document.getElementById('zoom-level').value);
                    document.getElementById('monitor-video').style.width = currentZoom + '%';
                }
                
                let currentModel = 'best-train1.pt';
                function handleSelection(element) {
                    // 清除所有选项的选中状态
                    document.querySelectorAll('.option-item').forEach(item => {
                        item.style.backgroundColor = '#3a3a3a';
                    });

                    // 设置当前选中状态
                    element.style.backgroundColor = '#2d7030';
                    // 获取选择值
                    currentModel = element.dataset.value;
                }

                // Capture screenshot
                function captureScreenshot() {
                    fetch(`/capture_screenshot?model=${currentModel}`)
                        .then(response => response.json())
                        .then(data => {
                            alert(`截图已保存，使用模型: ${currentModel}，文件名: ${data.filename}`);
                        });
                }

                // Temperature alarm
                function checkTemperature() {
                    fetch('/check_temperature')
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById('max-temp').innerHTML = '当前最高温度: ' + data.max_temp + '°C';
                        if (data.alarm) {
                            document.getElementById('alarm-indicator').classList.remove('hidden');
                            document.getElementById('alarm-audio').play();
                        } else {
                            document.getElementById('alarm-indicator').classList.add('hidden');
                            document.getElementById('alarm-audio').pause();
                            document.getElementById('alarm-audio').currentTime = 0;
                        }
                    });
                }
                
                // Stop or enable alarm
                function stopAlarm() {
                    fetch('/stop_alarm');
                    document.getElementById('alarm-audio').pause();
                    document.getElementById('alarm-audio').currentTime = 0;
                    document.getElementById('alarm-indicator').classList.add('hidden');
                }

                // restart whole service
                function restartThermal() {
                    alert('正在重启热成像摄像头，请等待几秒并刷新页面！');
                    fetch('/restart_server');
                }

                // Load temperature data
                function loadTemperatureData() {
                    fetch('/get_temperature_data')
                        .then(response => response.json())
                        .then(data => {
                            const tbody = document.getElementById('temp-data-body');
                            tbody.innerHTML = '';
                            data.forEach(row => {
                                const tr = document.createElement('tr');
                                const date = new Date(row[0] * 1000).toLocaleString();
                                tr.innerHTML = `
                                    <td>${date}</td>
                                    <td>${row[1].toFixed(2)}</td>
                                    <td>${row[2].toFixed(2)}</td>
                                    <td>${row[3].toFixed(2)}</td>
                                `;
                                tbody.appendChild(tr);
                            });
                        });
                }
                
                // Load gallery
                function loadGallery() {
                    fetch('/get_captured_photos')
                        .then(response => response.json())
                        .then(data => {
                            const grid = document.getElementById('photo-grid');
                            grid.innerHTML = '';
                            data.forEach(photo => {
                                const item = document.createElement('div');
                                item.className = 'photo-item';
                                item.innerHTML = `
                                    <img src="/photos/${photo.original}" alt="Captured photo">
                                    <div class="photo-info">
                                        ${photo.timestamp}<br>
                                        <a href="/photos/${photo.analyzed}" target="_blank">查看分析结果</a>
                                    </div>
                                `;
                                grid.appendChild(item);
                            });
                        });
                }

                // 添加自动刷新功能
                function autoRefreshGallery() {
                    if (!document.getElementById('gallery').classList.contains('hidden')) {
                        loadGallery();
                    }
                }
                setInterval(autoRefreshGallery, 2000);  // 每2秒刷新
                
                // Update system info
                function updateSystemInfo() {
                    fetch("/system_info")
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById("cpu").innerHTML = data.cpu;
                            document.getElementById("memory").innerHTML = data.memory;
                            document.getElementById("temp").innerHTML = data.temp;
                            document.getElementById("fps").innerHTML = data.fps;
                        });
                }
                
                // Initialize
                showSection('monitor');
                setInterval(updateSystemInfo, 1000);
                setInterval(checkTemperature, 1000); // 负责警报
                setInterval(loadTemperatureData, 1000);  // 每1秒刷新
            </script>
        </body>
    </html>
    """
    )


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


@app.route("/capture_screenshot")
def capture_screenshot():
    global self_file_path
    model = request.args.get("model")
    if latest_frame:
        timestamp = time.time()
        filename = f"{datetime.fromtimestamp(int(timestamp))}.jpg"
        filepath = os.path.join(CAPTURED_PATH, filename)

        with open(filepath, "wb") as f:
            f.write(latest_frame)
        if model == "best-train1.pt":
            # 选择的模型路径
            model_path = self_file_path + "/models/best-train1.pt"
            screenshotAnalyzer.screenshot_process(
                timestamp, latest_frame, filename, model_path
            )
        elif model == "best-train2.pt":
            model_path = self_file_path + "/models/best-train2.pt"
            screenshotAnalyzer.screenshot_process(
                timestamp, latest_frame, filename, model_path
            )
        return jsonify({"status": "success", "filename": filename})
    return jsonify({"status": "error", "message": "No frame available"})


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
    waitress.serve(app, host="0.0.0.0", port=8080, threads=12)

# !!! TODO: CHANGE THERMAL THRESHOLD
