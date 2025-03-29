# 从属于screen-analyzer.py，被它调用
import os
from ultralytics import YOLO

model = YOLO(os.path.abspath("./Python/models/best-train1.pt"), task="detect")


def inference_screenshot(filename):  # ai分析图片并输出
    results = model(os.path.expanduser(f"~/Pictures/captured/{filename}"))
    results[0].save(os.path.expanduser(f"~/Pictures/analyzed/{filename}"))
