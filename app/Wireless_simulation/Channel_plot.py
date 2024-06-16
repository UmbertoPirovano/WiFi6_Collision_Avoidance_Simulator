import numpy as np
import random
import matplotlib.pyplot as plt
from Wi_fi6 import Channel_802_11 

# Define a function to perform calculations and plot results
def plot_tx_time_vs_distance(available_bandwidths, frequency, distance, file_size, num_runs):
    plt.figure(figsize=(10, 6))

    for bandwidth in available_bandwidths:
        calculator = Channel_802_11(bandwidth, frequency, P_tx=-15)
        tx_times_all = []

        # Perform calculations for each distance
        for d in distance:
            tx_times = []
            for _ in range(num_runs):
                results = calculator.perform_calculations(file_size, d)
                tx_times.append(float(results['tx_time'] * 10**3))
            tx_times_all.append(np.mean(tx_times))

        # Plot the results
        plt.plot(distance, tx_times_all, label=f'Bandwidth = {bandwidth / 1e6} MHz')

    plt.xlabel('Distance (m)')
    plt.ylabel('tx_time (ms)')
    plt.ylim(0,14)
    plt.title('Average Transmission Time of the image vs Distance (Application layer)')
    plt.legend()
    plt.grid(True)
    plt.show()

# Parameters
random.seed(42)  # Set seed for reproducibility
available_bandwidths = [20e6,80e6, 40e6,160e6]  # Available bandwidths in Hz
frequency = 5  # 5 GHz
distance = np.linspace(0.1, 100, 100)  # Distance in meters
file_size = 765 * 10**3
num_runs = 100  # Number of runs for each distance

# Plot for each available bandwidth
plot_tx_time_vs_distance(available_bandwidths, frequency, distance, file_size, num_runs)
