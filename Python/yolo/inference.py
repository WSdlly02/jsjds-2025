import cv2
from ultralytics import YOLO

model = YOLO(f"best-train2.pt", task="detect")
results = model("test_image.jpg")
results[0].save("a.jpg")
