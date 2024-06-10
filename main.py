import contextlib
from datetime import datetime
import io
import random
import sys
import airsim
import time
import cv2
import numpy as np
from PIL import Image
import os
import shutil

from Computer_vision.RoI_optimized import RoI
from Computer_vision.cvEdgeService import CVEdgeService
from Wireless_simulation.Wi_fi6 import Channel_802_11
from tools.get_wsl_ip import get_wsl_ip 

class AirSimCarSimulation:
    def __init__(self, client_ip, output_dir, processed_dir, roi_ratio=[100], cv_mode=3, channel_params=[20e6, 5, -15]):
        self.client = airsim.CarClient(ip=client_ip)
        self.client.confirmConnection()
        self.client.enableApiControl(True)
        self.car_controls = airsim.CarControls()
        self.output_dir = output_dir
        self.processed_dir = processed_dir

        camera_pose = airsim.Pose(airsim.Vector3r(0, 0, 0), airsim.to_quaternion(0.05, 0, 0))  #PRY in radians
        self.client.simSetCameraPose(0, camera_pose)

        # Initialize other components
        with contextlib.redirect_stdout(io.StringIO()):
            self.edge_service = CVEdgeService(mode=cv_mode)
        self.roi = RoI(ratios=roi_ratio)
        self.channel_calculator = Channel_802_11(available_bandwidth=channel_params[0], frequency=channel_params[1], P_tx=channel_params[2])

        # Timing records
        self.chronos_capture = []
        self.chronos_tx = []
        self.chronos_inference = []
        self.chronos_actuation = []

    def __capture_image(self, save=True):
        response = self.client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)])
        img = np.frombuffer(response[0].image_data_uint8, dtype=np.uint8)
        img = img.reshape(response[0].height, response[0].width, 3)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)

        os.makedirs(self.output_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(self.output_dir, f'image_{timestamp}.png')
        if save:
            img.save(output_file)
        print(f"Image saved to {output_file}")
        return output_file

    def __compute_distance(self, car_state, bts_position=(0, 0, 0)):
        car_position = car_state.kinematics_estimated.position
        distance = np.sqrt(
            (car_position.x_val - bts_position[0]) ** 2 + 
            (car_position.y_val - bts_position[1]) ** 2 + 
            (car_position.z_val - bts_position[2]) ** 2
        )
        return distance

    def __cleanup(self):
        print("Simulation terminated. Resetting AirSim.")
        shutil.rmtree(self.output_dir)
        shutil.rmtree(self.processed_dir)
        self.client.reset()
        self.client.enableApiControl(False)
        self.client.armDisarm(False)
        self.__print_timings()

    def __print_timings(self):
        print("Average time for capture: ", sum(self.chronos_capture) / len(self.chronos_capture))
        print("Average time for tx: ", sum(self.chronos_tx) / len(self.chronos_tx))
        print("Average time for inference: ", sum(self.chronos_inference) / len(self.chronos_inference))
        #print("Average time for actuation: ", sum(self.chronos_actuation) / len(self.chronos_actuation))
        total_average_time = (
            sum(self.chronos_capture) + sum(self.chronos_tx) + 
            sum(self.chronos_inference) #+ sum(self.chronos_actuation)
        ) / len(self.chronos_capture)
        print("Total average time: ", total_average_time)

    def __car_break(self):
        self.car_controls.throttle = 0
        self.car_controls.brake = 1
        self.client.setCarControls(self.car_controls)

    def __perform_decision(self, detected):
        # detected: list of dictionaries
        # detected[i]: dictionary of detected objects in subarea i. Each value represents the percentage of area covered by the object
        target_throttle = 0.5
        slowdown_coeff = [1,1,0.55,0.17]
        slowdown_coeff = [coeff * target_throttle for coeff in slowdown_coeff]
        normal_threshold = int(5)
        emergency_threshold = [5,5,80]

        slowdown_factors = np.zeros(len(slowdown_coeff))
        for i, counter in enumerate(detected):
            if counter:
                occupied_area = sum(counter.values())
                print(f">>Occupied area in subarea {i + 1}: {occupied_area}")
                if (i+1) <= 3 and occupied_area > emergency_threshold[i]:
                    self.__car_break()
                    print(f"Obstacle detected in subarea {i + 1}! Emergency stop!.")
                    return
                if occupied_area > normal_threshold:
                    slowdown_factors[i] = occupied_area / 100 * slowdown_coeff[i]                    
                if 13 in counter.keys():
                    slowdown_factors[i] *= 2
                elif 2 in counter.keys():
                    slowdown_factors[i] /= 2        

        new_throttle = target_throttle - sum(slowdown_factors)
        if new_throttle < 0: new_throttle = 0
        self.car_controls.throttle = new_throttle
        self.client.setCarControls(self.car_controls)
        if new_throttle != target_throttle:
            print(f"Throttle set to {new_throttle}")
            
        

    def run_simulation(self):
        try:
            # Get initial state of the car
            car_state = self.client.getCarState()
            print("Speed %d, Gear %d" % (car_state.speed, car_state.gear))

            # Set initial controls for the car
            self.car_controls.throttle = 0.5
            self.car_controls.steering = 0
            self.client.setCarControls(self.car_controls)

            # Let the car drive a bit
            time.sleep(2)

            while True:
                start_time = time.time()
                img_path = self.__capture_image()
                self.chronos_capture.append(time.time() - start_time)

                # Transmission img -> edge
                start_time = time.time()
                tx_time = self.channel_calculator.perform_calculations(
                    file_size=os.path.getsize(img_path),
                    distance=self.__compute_distance(self.client.getCarState())
                )["tx_time"]
                time.sleep(float(tx_time))
                self.chronos_tx.append(time.time() - start_time)

                start_time = time.time()
                self.edge_service.perform_inference(img_path, self.processed_dir)
                self.chronos_inference.append(time.time() - start_time)

                # Get the path to the last png added to processed_dir
                mask_files = sorted(os.listdir(os.path.join(self.processed_dir, 'pred')))
                view_files = sorted(os.listdir(os.path.join(self.processed_dir, 'vis')))
                mask_path = os.path.join(self.processed_dir, 'pred', mask_files[-1])
                vis_path = os.path.join(self.processed_dir, 'vis', view_files[-1])
                print(f"Mask path: {mask_path}")

                detected = self.roi.detect_in_roi(mask_path, vis_path, steering=0)
                self.__perform_decision(detected)
                if self.client.getCarState().speed < 0.1:
                    self.roi.draw_roi(vis_path)
                    raise Exception("Car stopped. Exiting simulation.")
        finally:
            self.__cleanup()

if __name__ == "__main__":
    sys.tracebacklimit = 0
    random.seed(7)
    simulation = AirSimCarSimulation(
        client_ip='192.168.1.61',
        output_dir='/home/bert/github/5G_CARS_1/run/received/',
        processed_dir='/home/bert/github/5G_CARS_1/run/processed/',
        roi_ratio=[5,20,40,40],
        cv_mode='light',
        channel_params=[20e6, 5, -15]
    )
    simulation.run_simulation()
