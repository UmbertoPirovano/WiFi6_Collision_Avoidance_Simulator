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

from EdgeService.cvEdgeService import CVEdgeService
from Wireless_simulation.Wi_fi6 import Channel_802_11

class AirSimCarSimulation:
    def __init__(self, gui=None, directory = "./run/", client_ip = "", cv_mode=3, inf_time=None, channel_params=[20e6, 5, -15], image_format='JPEG', image_quality=80, decision_params={'slowdown_coeff': [1,1,0.55,0.17], 'normal_threshold': 5, 'emergency_threshold': [5,5,80]}, target_throttle=0.5):
        self.gui = gui
        self.client = airsim.CarClient(ip=client_ip)
        self.client.confirmConnection()
        self.car_controls = airsim.CarControls()
        self.directory = directory
        self.received_dir = os.path.join(directory, 'received/')
        self.processed_dir = os.path.join(directory, 'processed/')
        self.log_dir = os.path.join(directory, 'log/')
        self.image_format = image_format
        self.image_quality = image_quality
        self.decision_params = decision_params
        self.inf_time = inf_time
        self.target_throttle = target_throttle

        camera_pose = airsim.Pose(airsim.Vector3r(0, 0, 0), airsim.to_quaternion(0.05, 0, 0))  #PRY in radians
        self.client.simSetCameraPose(0, camera_pose)

        self.scenarios = {
            "fence": {
                "position": (0 + 50, 0, -0.79),
                "orientation": (1, 0, 0, 0)
            },
            "car": {
                "position": (0, 0, -0.79),
                "orientation": (1, 0, 0, 0.028)
            }
        }

        # Initialize other components
        with contextlib.redirect_stdout(io.StringIO()):
            self.edge_service = CVEdgeService(mode=cv_mode, out_dir=self.processed_dir, decision_params=self.decision_params, target_throttle=self.target_throttle)
        self.channel_calculator = Channel_802_11(available_bandwidth=channel_params[0], frequency=channel_params[1], P_tx=channel_params[2])

        # Timing records
        self.chronos_capture = []
        self.chronos_tx = []
        self.chronos_inference = []
        self.chronos_speed = []

    def __init_simulation(self):
        self.client.enableApiControl(True)
        try:
            shutil.rmtree(self.received_dir)
            shutil.rmtree(self.processed_dir)
        except FileNotFoundError:
            pass
        os.makedirs(self.received_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)

    def __cleanup(self):
        try:
            print("Simulation terminated. Resetting AirSim.")
            self.client.reset()
            self.client.enableApiControl(False)
            self.client.armDisarm(False)
            self.__print_timings()
        except Exception as e:
            print(f"Cleanup failed: {e}")

    def __capture_image(self, save=True, output_format='JPEG', quality=80):
        response = self.client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene, pixels_as_float=False, compress=False)])
        img = np.frombuffer(response[0].image_data_uint8, dtype=np.uint8)
        img = img.reshape(response[0].height, response[0].width, 3)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(self.received_dir, f'image_{timestamp}.{output_format.lower()}')
        
        if save:
            img.save(output_file, format=output_format, quality=quality)
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

    def get_available_scenarios(self):
        return list(self.scenarios.keys())
    
    def add_scenario(self, name, position, orientation):
        self.scenarios[name] = {
            "position": position,
            "orientation": orientation
        }

    def run_simulation(self, obstacle="car"):
        self.__init_simulation()        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.log_dir + f"output_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            with contextlib.redirect_stdout(f):
                print(f"{timestamp} >>Starting simulation with obstacle: {obstacle}\n")
                try:
                    self.client.reset()

                    # Set initial position of the car
                    print(f"Setting initial position for scenario: {obstacle}")
                    coordinates = self.scenarios[obstacle]
                    position = coordinates["position"]
                    orientation = coordinates["orientation"]

                    self.client.simSetVehiclePose(
                        airsim.Pose(
                            airsim.Vector3r(position[0], position[1], position[2]),
                            airsim.Quaternionr(orientation[1], orientation[2], orientation[3], orientation[0])  # Order: x, y, z, w
                        ),
                        ignore_collision=True,
                        vehicle_name="PhysXCar"
                    )

                    # Get initial state of the car
                    car_state = self.client.getCarState()
                    print("Speed %d, Gear %d" % (car_state.speed, car_state.gear))

                    # Set initial controls for the car
                    self.car_controls.throttle = 0.5
                    self.car_controls.steering = 0
                    self.client.setCarControls(self.car_controls)

                    # Let the car drive a bit
                    time.sleep(1)
                    
                    while True:
                        start_time = time.time()
                        img_path = self.__capture_image(output_format=self.image_format, quality=self.image_quality)
                        self.chronos_capture.append(time.time() - start_time)

                        # Transmission img -> edge
                        start_time = time.time()
                        tx_time = self.channel_calculator.perform_calculations(
                            file_size=os.path.getsize(img_path),
                            distance=self.__compute_distance(self.client.getCarState())
                        )["tx_time"]
                        time.sleep(float(tx_time))
                        self.chronos_tx.append(time.time() - start_time)

                        # EDGE SERVICE
                        start_time = time.time()
                        if self.inf_time is not None:
                            self.client.simPause(True)
                        self.edge_service.perform_inference(img_path)
                        if self.inf_time is not None:
                            self.client.simPause(False)
                            time.sleep(self.inf_time)
                            self.chronos_inference.append(self.inf_time)
                        else:
                            self.chronos_inference.append(time.time() - start_time)
                        detected = self.edge_service.perform_detection(self.processed_dir, steering=0)
                        action = self.edge_service.perform_decision(detected)
                        
                        # ACTUATION
                        self.client.setCarControls(action)

                        # UPDATE GUI
                        self.chronos_speed.append(self.client.getCarState().speed)
                        if self.gui is not None:
                            self.gui.update_gui(times={
                                "capture": self.chronos_capture,
                                "tx": self.chronos_tx,
                                "inference": self.chronos_inference},
                                speeds=self.chronos_speed)

                        if self.client.getCarState().speed < 0.1:
                            print("Car stopped. Exiting simulation.")
                            raise Exception("Car stopped. Exiting simulation.")
                except Exception as e:
                    print(f"Error during simulation loop: {e}")
                finally:
                    collision = self.client.simGetCollisionInfo(vehicle_name='PhysXCar').has_collided
                    print(f"COLLISION: {collision}")
                    time.sleep(3)
                    self.__cleanup()
                    return collision

if __name__ == "__main__":
    sys.tracebacklimit = 0
    random.seed(7)
    simulation = AirSimCarSimulation(
        client_ip='192.168.1.21',
        directory = './run/',
        cv_mode='Light',
        inf_time=1,
        channel_params=[20e6, 5, -15],
        image_format='JPEG',
        image_quality=80,
        decision_params={'slowdown_coeff': [1,1,0.55,0.17], 'normal_threshold': 5, 'emergency_threshold': [5,5,80]}
    )
    simulation.run_simulation(obstacle="fence")
    simulation.run_simulation(obstacle="car")
