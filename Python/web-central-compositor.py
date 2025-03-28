from picamera2 import Picamera2
from flask import (
    Flask,
    render_template_string,
    Response,
    jsonify,
    send_from_directory,
    abort,
)
import sys
import io
import cv2
import numpy as np
import psutil
import time
import threading
from PIL import Image
import screenshotAnalyzer
import os
from datetime import datetime
import sqlite3
import simpleaudio as sa

app = Flask(__name__)

# Global variables
frame_lock = threading.Lock()
thermal_lock = threading.Lock()
latest_frame = None
sys_info = {"cpu": "0%", "memory": "0%", "temp": "N/A", "fps": "0"}
alarm_playing = False
alarm_sound = None

# Initialize camera
picam2 = Picamera2()
config = picam2.create_video_configuration(
    main={"size": (2592, 1944)},  # Native resolution
    lores={"size": (1296, 972)},  # Preview stream
    display="main",
    encode="main",
    controls={"FrameRate": 30},
)
picam2.configure(config)
picam2.start()

# 修改照片存储路径
CAPTURED_PATH = os.path.expanduser("~/Pictures/captured")
ANALYZED_PATH = os.path.expanduser("~/Pictures/analyzed")
os.makedirs(CAPTURED_PATH, exist_ok=True)
os.makedirs(ANALYZED_PATH, exist_ok=True)


def generate_thermal():
    delimiter = b"--FRAME--\n"
    buffer = b""

    while True:
        data = sys.stdin.buffer.read(4096)
        if not data:
            break

        buffer += data

        while True:
            idx = buffer.find(delimiter)
            if idx == -1:
                break

            frame_data = buffer[:idx]
            buffer = buffer[idx + len(delimiter) :]

            if frame_data:
                try:
                    img = Image.open(io.BytesIO(frame_data))
                    img_io = io.BytesIO()
                    img.save(img_io, "JPEG")
                    img_io.seek(0)

                    # Check temperature for alarm
                    temp_data = np.array(img)
                    max_temp = np.max(temp_data)
                    if max_temp > 60 and not alarm_playing:
                        play_alarm()

                    yield (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n"
                        + img_io.getvalue()
                        + b"\r\n"
                    )
                except Exception as e:
                    print(f"Decoding error: {e}")


def play_alarm():
    global alarm_playing, alarm_sound
    alarm_playing = True
    wave_obj = sa.WaveObject.from_wave_file("alarm.wav")  # Make sure you have this file
    alarm_sound = wave_obj.play()
    alarm_sound.wait_done()
    alarm_playing = False


def stop_alarm():
    global alarm_playing, alarm_sound
    if alarm_sound and alarm_playing:
        alarm_sound.stop()
    alarm_playing = False


def adaptive_quality():
    cpu = psutil.cpu_percent()
    net = psutil.net_io_counters().bytes_sent
    return 90 if cpu < 70 and net < 1e6 else 75


def capture_camera_frames():
    global latest_frame
    while True:
        with frame_lock:
            frame = picam2.capture_array("main")
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # Sharpen
            kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
            frame = cv2.filter2D(frame, -1, kernel)

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
    data = cursor.fetchall()
    conn.close()
    return data


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
        <title>智能监控系统</title>
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
                right: 20px;
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
        </style>
    </head>
    <body>
        <h1>智能监控系统</h1>
        
        <div class="menu">
            <div class="menu-item" onclick="showSection('monitor')">实时监控</div>
            <div class="menu-item" onclick="showSection('thermal')">热成像监测</div>
            <div class="menu-item" onclick="showSection('database')">数据库</div>
            <div class="menu-item" onclick="showSection('system')">信息系统</div>
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
                    <button onclick="stopAlarm()">停止警报</button>
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
            function zoomIn() {
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
            
            // Capture screenshot
            function captureScreenshot() {
                fetch('/capture_screenshot')
                    .then(response => response.json())
                    .then(data => {
                        alert('截图已保存: ' + data.filename);
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
                        } else {
                            document.getElementById('alarm-indicator').classList.add('hidden');
                        }
                    });
            }
            
            function stopAlarm() {
                fetch('/stop_alarm');
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
            setInterval(checkTemperature, 1000);
        </script>
    </body>
    </html>
    """
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
    if latest_frame:
        timestamp = time.time()
        filename = f"{datetime.fromtimestamp(int(timestamp))}.jpg"
        filepath = os.path.join(CAPTURED_PATH, filename)

        with open(filepath, "wb") as f:
            f.write(latest_frame)

        # 修改分析结果保存路径
        screenshotAnalyzer.screenshot_process(timestamp, latest_frame, filename)

        return jsonify({"status": "success", "filename": filename})
    return jsonify({"status": "error", "message": "No frame available"})


@app.route("/check_temperature")
def check_temperature():
    # This is a simplified version - in a real app you'd get actual temperature data
    return jsonify({"max_temp": 45.2, "alarm": alarm_playing})


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


if __name__ == "__main__":
    threading.Thread(target=capture_camera_frames, daemon=True).start()
    threading.Thread(target=get_system_info, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, threaded=True)

# !!! DATABASE LOCK : capture_screenshot() conflicts with get_temperature_history() :: SOLVED && READ PHOTOS OUTSIDE FROM /static && web scale index adjust
