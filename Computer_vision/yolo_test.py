from ultralytics import YOLO
import os
import time

# Load a model
model = YOLO('yolov8m.pt')  # load an official model

# Predict with the model
img = '/home/bert/github/5G_CARS_1/Computer_vision/images/img_PhysXCar__0_1713713052532274500.png'
dir = '/home/bert/github/5G_CARS_1/Airsim/images'

results = model(dir)  # predict on an image folder
results_folder = 'Computer_vision/yolo_outputs/'

start_time = time.time()

os.makedirs(results_folder, exist_ok=True)

# Iterate through the results and save them in the 'results' folder
for i, result in enumerate(results):
    result.save(filename=os.path.join(results_folder, f'result_{i}.jpg'))

end_time = time.time()
execution_time = end_time - start_time
print("Execution time:", execution_time, "seconds")