from flask import Flask, jsonify, render_template
import random  # 假设我们用随机数模拟温度传感器

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get_temperature")
def get_temperature():
    temperature = random.randint(50, 70)  # 模拟温度传感器数据
    return jsonify({"temperature": temperature})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
