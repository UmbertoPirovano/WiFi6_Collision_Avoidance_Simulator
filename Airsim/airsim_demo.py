# ready to run example: PythonClient/car/hello_car.py

import airsim
import time

# connect to the AirSim simulator
client = airsim.CarClient(ip="192.168.1.51")    # connect to the AirSim simulator, leave the IP blank to connect to the local machine or set it to the IP of the remote machine
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
time.sleep(3)

start_time = time.time()

car_controls.steering = 0.20
client.setCarControls(car_controls)
time.sleep(1)
car_controls.steering = 0
client.setCarControls(car_controls)
time.sleep(2)
car_controls.steering = -0.20
client.setCarControls(car_controls)
time.sleep(1)
car_controls.steering = 0
client.setCarControls(car_controls)
time.sleep(3)
car_controls.steering = -0.20
client.setCarControls(car_controls)
time.sleep(1)
car_controls.steering = 0
client.setCarControls(car_controls)
time.sleep(3)
car_controls.steering = 0.20
client.setCarControls(car_controls)
time.sleep(1)
car_controls.throttle = 1
car_controls.steering = 0
client.setCarControls(car_controls)
time.sleep(3)

car_controls.throttle = 0
car_controls.steering = 0
car_controls.brake = 1
client.setCarControls(car_controls)
print("Stopping! The simulation is over.")
print("Speed %d, Gear %d" % (car_state.speed, car_state.gear))