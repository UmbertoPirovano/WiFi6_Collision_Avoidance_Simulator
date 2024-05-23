import math
import random
import os

class WiFi6Channel:
    def __init__(self, bandwidth):
        self.bandwidth = bandwidth  # in MHz
        self.guard_band = 2  # in MHz
        self.modulation_scheme = '1024-QAM'  # Assuming 1024-QAM for simplicity

    def compute_bitrate(self):
        # Available bandwidth after excluding guard bands
        Rs = self.bandwidth - self.guard_band * 2  # MHz
        # Number of bits per symbol for 1024-QAM
        N_bit = math.log2(1024)  # 10 bits per symbol
        # Compute the bitrate in Mbps
        bitrate = Rs * N_bit  # Mbps
        return bitrate

    def compute_latency(self, file_size):
        # Compute the bitrate
        bitrate = self.compute_bitrate()
        # Calculate the transmission latency (file size in Megabits / bitrate)
        latency = file_size / bitrate  # seconds
        # Add a random delay to simulate real-world conditions (up to 100 ms)
        return latency + random.uniform(0, 0.05)  # seconds

    def display_parameters(self, file_size):
        bitrate = self.compute_bitrate()
        latency = self.compute_latency(file_size)
        print(f"Bandwidth: {self.bandwidth} MHz")
        print(f"Guard Band: {self.guard_band} MHz on each side")
        print(f"Modulation Scheme: {self.modulation_scheme}")
        print(f"Bitrate: {bitrate:.2f} Mbps")
        print(f"Latency: {latency:.5f} seconds for a file size of {file_size} Megabits")

channel = WiFi6Channel(bandwidth=20)
file_size = os.path.getsize('/home/bert/github/5G_CARS_1/Airsim/images/image_10.png')/10**6  # Megabits

print("Channel:")
random.seed(42)
channel.display_parameters(file_size)
