# 从属于screen-analyzer.py，被它调用
import os
import cv2
from ultralytics import YOLO

model = None


def inference_screenshot(filename, model_path):  # ai分析图片并输出
    model = YOLO(model=model_path, task="detect")
    results = model(os.path.expanduser(f"~/Pictures/captured/{filename}"))
    results[0].save(os.path.expanduser(f"~/Pictures/analyzed/{filename}"))
    annotated_image = results[0].plot()  # 返回BGR格式的Numpy数组

    # 将Numpy数组转为二进制
    _, encoded_image = cv2.imencode(".jpg", annotated_image)
    binary_data = encoded_image.tobytes()
    return binary_data
