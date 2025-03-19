# video_server.py
from flask import Flask, Response
import sys
import io
from PIL import Image

app = Flask(__name__)


def generate_mjpeg():
    delimiter = b"--FRAME--\n"
    buffer = b""

    while True:
        # 从标准输入读取数据
        data = sys.stdin.buffer.read(4096)
        if not data:
            break

        buffer += data

        while True:
            # 查找帧分隔符
            idx = buffer.find(delimiter)
            if idx == -1:
                break

            # 提取完整帧数据
            frame_data = buffer[:idx]
            buffer = buffer[idx + len(delimiter) :]

            if frame_data:
                try:
                    img = Image.open(io.BytesIO(frame_data))
                    img_io = io.BytesIO()
                    img.save(img_io, "JPEG")
                    img_io.seek(0)
                    yield (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n"
                        + img_io.getvalue()
                        + b"\r\n"
                    )
                except Exception as e:
                    print(f"解码错误: {e}")


@app.route("/stream")
def video_feed():
    return Response(
        generate_mjpeg(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/")
def index():
    return """
    <html>
      <head><title>实时视频流</title></head>
      <body>
        <img src="/stream" style="width:640px;height:480px;">
      </body>
    </html>
    """


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
