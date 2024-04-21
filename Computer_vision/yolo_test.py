from ultralytics import YOLO
import os

# Load a model
model = YOLO('yolov8m.pt')  # load an official model

# Predict with the model
results = model('Computer_vision/images')  # predict on an image folder

results_folder = 'Computer_vision/results'
os.makedirs(results_folder, exist_ok=True)

# Iterate through the results and save them in the 'results' folder
for i, result in enumerate(results):
    result.save(filename=os.path.join(results_folder, f'result_{i}.jpg'))