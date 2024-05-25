import contextlib
from datetime import datetime
import io
import airsim
import time
import cv2
import numpy as np
from PIL import Image
import os
from Computer_vision.RoI_optimized import RoI
from Computer_vision.cvEdgeService import CVEdgeService
import shutil

def capture_image(output_dir, save=True): 
        response = client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)]) 
        img = np.frombuffer(response[0].image_data_uint8, dtype=np.uint8) 
        img = img.reshape(response[0].height, response[0].width, 3)        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img) 

        # Save the image with a unique filename based on timestamp
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(output_dir, f'image_{timestamp}.png')
        if save:
            img.save(output_file)
        print(f"Image saved to {output_file}")
        return output_file

def car_break():
    car_controls.throttle = 0
    car_controls.brake = 1
    client.setCarControls(car_controls)
    #time.sleep(3)
    #car_controls.brake = 0
    #client.setCarControls(car_controls)

try:
    client = airsim.CarClient(ip="192.168.1.174")    # connect to the AirSim simulator, leave the IP blank to connect to the local machine or set it to the IP of the remote machine
    client.confirmConnection()
    client.enableApiControl(True)
    car_controls = airsim.CarControls()
    
    # get state of the car
    car_state = client.getCarState()
    print("Speed %d, Gear %d" % (car_state.speed, car_state.gear))
    # set the controls for car
    car_controls.throttle = 0.5
    car_controls.steering = 0
    client.setCarControls(car_controls)
    # let car drive a bit

    with contextlib.redirect_stdout(io.StringIO()):
        edge_service = CVEdgeService()

    time.sleep(3)
    chronos_capture = []
    chronos_tx = []
    chronos_inference = []
    chronos_actuation = []
    while True:
        start_time = time.time()
        output_dir = '/home/bert/github/5G_CARS_1/run/received/'
        img_path = capture_image(output_dir)
        chronos_capture.append(time.time() - start_time)

        start_time = time.time()
        tx_time = 0.010
        time.sleep(tx_time)
        chronos_tx.append(time.time() - start_time)

        out_dir = '/home/bert/github/5G_CARS_1/run/processed/'
        start_time = time.time()
        edge_service.perform_inference(img_path, out_dir)
        chronos_inference.append(time.time() - start_time)

        # Get the path to the last png added to out_dir
        start_time = time.time()
        mask_files = sorted(os.listdir(os.path.join(out_dir, 'pred')))
        mask_path = os.path.join(out_dir, 'pred', mask_files[-1])
        print(f"Mask path: {mask_path}")
        roi = RoI(mask_path, img_path, ratios=[100], steering=0)
        detected = roi.detect_in_roi()
        emergency_stop_triggered = False
        for i, counter in enumerate(detected):
            if any(value > 1500 for value in counter.values()):
                print(f'Emergency stop! Obstacle detected in subarea {i + 1}!')
                car_break()
                break
        chronos_actuation.append(time.time() - start_time)
finally:
    print(f"Simulation terminated. Resetting airsim.")
    # Empty the 'run' folder
    shutil.rmtree('/home/bert/github/5G_CARS_1/run')
    os.makedirs('/home/bert/github/5G_CARS_1/run')
    client.reset()
    client.enableApiControl(False)
    client.armDisarm(False)
    print("Average time for capture: ", sum(chronos_capture) / len(chronos_capture))
    print("Average time for tx: ", sum(chronos_tx) / len(chronos_tx))
    print("Average time for inference: ", sum(chronos_inference) / len(chronos_inference))
    print("Average time for actuation: ", sum(chronos_actuation) / len(chronos_actuation))
    print("Total average time: ", (sum(chronos_capture) + sum(chronos_tx) + sum(chronos_inference) + sum(chronos_actuation)) / len(chronos_capture))