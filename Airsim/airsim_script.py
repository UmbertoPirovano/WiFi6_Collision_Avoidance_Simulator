# ready to run example: PythonClient/car/hello_car.py
import airsim
import time
import cv2
import numpy as np
from PIL import Image
import os

# connect to the AirSim simulator
client = airsim.CarClient(ip="192.168.1.104")    # connect to the AirSim simulator, leave the IP blank to connect to the local machine or set it to the IP of the remote machine
client.confirmConnection()
client.enableApiControl(True)
car_controls = airsim.CarControls()

def capture_image(num_images): 
    for i in range(num_images): 

        response=client.simGetImages([airsim.ImageRequest("0",airsim.ImageType.Scene, False, False)]) 
        img = np.frombuffer(response[0].image_data_uint8, dtype=np.uint8) 
        img= img.reshape(response[0].height,response[0].width,3)        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img) 

        
        # Save the image
        output_dir = '/home/bert/github/5G_CARS_1/Airsim/images/'
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f'image_{i}.png')
        img.save(output_file)

        time.sleep(1) 
 

# get state of the car
car_state = client.getCarState()
print("Speed %d, Gear %d" % (car_state.speed, car_state.gear))

# set the controls for car
car_controls.throttle = 0.5
car_controls.steering = 0
client.setCarControls(car_controls)

# let car drive a bit
time.sleep(3)

start_time = time.time()
while time.time() - start_time < 10:
    print("Capturing images...")
    capture_image(20)

car_controls.throttle = 0
car_controls.steering = 0
car_controls.brake = 1
client.setCarControls(car_controls)
print("Stopping! The simulation is over.")
print("Speed %d, Gear %d" % (car_state.speed, car_state.gear))