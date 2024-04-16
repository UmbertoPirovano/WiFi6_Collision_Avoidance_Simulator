from ultralytics import YOLO
import os

# Load a model
model = YOLO('yolov8m-cls.pt')  # load an official model

# Predict with the model
results = model('/home/bert/github/5G_CARS_1/images/')  # predict on an image folder

results_folder = 'results'
os.makedirs(results_folder, exist_ok=True)

# Iterate through the results and save them in the 'results' folder
for i, result in enumerate(results):
    result.save(filename=os.path.join(results_folder, f'result_{i}.jpg'))