from ultralytics import YOLO

model = YOLO(f"./models/best-train2.pt", task="detect")


def inference_screenshot(last_frame, filename):
    results = model(last_frame)
    results[0].save(f"~/Photos/analyzed/{filename}.jpg")
