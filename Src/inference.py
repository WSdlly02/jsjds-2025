# 从属于screen-analyzer.py，被它调用
import os
from ultralytics import YOLO


def inference_screenshot(filename, model_path):  # ai分析图片并输出
    model = YOLO(model=model_path, task="detect")
    results = model(os.path.expanduser(f"~/Pictures/captured/{filename}"))
    results[0].save(os.path.expanduser(f"~/Pictures/analyzed/{filename}"))
