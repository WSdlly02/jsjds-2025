from flask import Flask, render_template, jsonify
import random

app = Flask(__name__)


# 模拟传感器数据
def get_sensor_data():
    # 这里可以替换为实际的传感器数据读取逻辑
    temperature = random.randint(20, 100)  # 模拟温度在20到100之间
    return temperature


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get_temperature")
def get_temperature():
    temperature = get_sensor_data()
    return jsonify({"temperature": temperature})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
