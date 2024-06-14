import random
import sys
from simulator import AirSimCarSimulation

if __name__ == "__main__":
    sys.tracebacklimit = 0
    random.seed(7)
    simulation = AirSimCarSimulation(
        client_ip='192.168.1.61',
        directory = './run/',
        cv_mode='light',
        inf_time=1,
        channel_params=[20e6, 5, -15],
        image_format='JPEG',
        image_quality=80,
        decision_params={'slowdown_coeff': [1,1,0.55,0.17], 'normal_threshold': 5, 'emergency_threshold': [5,5,80]}
    )
    simulation.run_simulation(obstacle="fence")
    simulation.run_simulation(obstacle="car")