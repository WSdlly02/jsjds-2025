# 从属于screen-analyzer.py，被它调用
import os
import cv2
from ultralytics import YOLO

model = None


def inference_screenshot(filename, model_path):  # ai分析图片并输出
    model = YOLO(model=model_path, task="detect")
    results = model.predict(
        source=os.path.expanduser(f"~/Pictures/captured/{filename}"),
        verbose=False,
        stream=True,
    )
    for result in results:
        if result.boxes and (result.boxes.numpy().cls[0] == 0):  # 有病的树叶
            print("Diseased!")
            leaf_status = True
        else:
            print("Healthy!")
            leaf_status = False
        result.save(os.path.expanduser(f"~/Pictures/analyzed/{filename}"))
        annotated_image = result.plot()  # 返回BGR格式的Numpy数组

    # 将Numpy数组转为二进制
    _, encoded_image = cv2.imencode(".jpg", annotated_image)
    binary_data = encoded_image.tobytes()
    return binary_data, leaf_status
