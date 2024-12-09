"""Use YOLO to detect objects in images"""

# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/Vision/03_yolo_to_fc.ipynb.

# %% auto 0
__all__ = ['detect_objects']

# %% ../../nbs/Vision/03_yolo_to_fc.ipynb 2
from ultralytics import YOLO
import json
import os

# %% ../../nbs/Vision/03_yolo_to_fc.ipynb 4
def detect_objects(
        image_path: str, # Path/URL of image
        conf: float=0.25 # Confidence threshold
    ) -> str: # JSON format of detection results
    """Detect object in the input image."""
    model = YOLO('yolov8s.pt')
    
    result = model(image_path, conf=conf, exist_ok=True)[0]
    # result.show()
    save_dir = os.getenv("LLMCAM_DATA", "../data")
    output_path = image_path.split("/")[-1]
    result.save(filename=f"{save_dir}/detection_{output_path}")
    dict = {}
    for c in result.boxes.cls:
        dict[model.names[int(c)]] = dict.get(model.names[int(c)], 0) + 1
    return json.dumps(dict)
