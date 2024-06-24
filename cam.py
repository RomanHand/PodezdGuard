import argparse
import cv2
from ultralytics import YOLO
import time
from datetime import datetime
import os
import yaml

parser = argparse.ArgumentParser(description='Приложение для охраны подъезда')
parser.add_argument('--config', type=str, default='config.yml', help='Путь к файлу конфига')
args = parser.parse_args()

with open(args.config, 'r') as f:
    config = yaml.safe_load(f)


video_dir = config['app']['video_dir']
os.makedirs(video_dir, exist_ok=True)

cap = cv2.VideoCapture(0)
camera_info = cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
print(f"Using camera with resolution: {camera_info}")

model = YOLO(config['model']['path'])

is_recording = False
start_time = 0

while True:
    ret, frame = cap.read()
    results = model(frame, verbose=False)

    person_detected = False
    for result in results:
        boxes = result.boxes
        for box in boxes:
            if result.names[int(box.cls[0])] == 'person':
                person_detected = True
                if config['app']['show_bounding_boxes']:
                    x1, y1, x2, y2 = box.xyxy[0]
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                break
    if person_detected:
        if not is_recording:
            now = datetime.now()
            video_name = f"{now.year}-{now.month:02d}-{now.day:02d}-{now.hour:02d}-{now.minute:02d}-{now.second:02d}.mp4"
            video_path = os.path.join(video_dir, video_name)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(video_path, fourcc, 30.0, (frame.shape[1], frame.shape[0]))
            is_recording = True
            start_time = time.time()
            print(f"Started recording video: {video_name}")
    else:
        if is_recording:
            if time.time() - start_time >= 5:
                out.release()
                is_recording = False
                print("Stopped recording video")

    if is_recording:
        out.write(frame)

    if config['app']['show_video']:
        cv2.imshow('Object Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break