import math
import airsim
import random
import numpy as np
import os
class ChannelCapacityCalculator:
        def __init__(self, available_bandwidth, frequency, P_tx):
            self.available_bandwidth = available_bandwidth  # Bandwidth in Hz
            self.frequency = frequency  # Frequency in GHz
            self.P_tx = P_tx  # Transmitted power in dBm
            self.P_n = random.uniform(-105, -120)  # Noise power in dBm, randomly generated
            self.modulation_order = 1024  # Modulation order for 1024-QAM
            self.n = math.log2(self.modulation_order)  # Bits per symbol for 1024-QAM
        def Car_state(self):
            client = airsim.CarClient()
            client.confirmConnection()

            car_state= client.getCarState()
            position = car_state.kinematics_estimated.orientation
            array_pos = np.array([position.x_val,position.y_val,position.z_val])
            print(array_pos)

            distance = np.linalg.norm(array_pos) * 10**3

            return distance
        def calculate_fspl(self,distance):
            fspl = 20 * math.log10(distance) + 20 * math.log10(self.frequency) + 32.4
            return fspl

        def calculate_snr(self, fspl):
            std = random.uniform(8,12)
            X_s = np.random.normal(0,std) #shadowing component
            snr = self.P_tx - self.P_n - fspl -X_s

            return snr
        def calculate_channel_capacity(self, snr_linear):
            C = self.available_bandwidth * math.log2(1 + snr_linear)
            return C

        def calculate_bitrate(self, C):
            Rb = C * 5/6 *random.uniform(0.8,1)
            return Rb
        def compute_Bandwidth_usage(self,C,Rb):
            Bandwidth_usage=Rb/C *100;
            return Bandwidth_usage
        
        def compute_tx(self,Image_size,Rb):

            latency = Rb/Image_size
            return latency
        
        def perform_calculations(self):
            distance = self.Car_state()
            fspl = self.calculate_fspl(distance)
            snr_db = self.calculate_snr(fspl)
            snr_linear = 10 ** (snr_db / 10)
            capacity = self.calculate_channel_capacity(snr_linear)
            bitrate = self.calculate_bitrate(capacity)
            Usage=self.compute_Bandwidth_usage(capacity,bitrate)
            tx_time = self.compute_tx(Image_size,bitrate)

            # Convert values to Mbps for display
            capacity_mbps = capacity * 10**-6
            bitrate_mbps = bitrate * 10**-6

            return {
                "P_tx": self.P_tx,
                "P_n": self.P_n,
                "FSPL": fspl,
                "SNR_dB": snr_db,
                "SNR_linear": snr_linear,
                "Channel_Capacity_Mbps": capacity_mbps,
                "Bitrate_Mbps": bitrate_mbps,
                "Bandwidth usage" : Usage    
                }

if __name__ == "__main__":
    random.seed()  # Set seed for reproducibility
    available_bandwidth = 80e6  # 80 MHz
    frequency = 5  # 5 GHz
    distance = 18  # Distance in meters

    calculator = ChannelCapacityCalculator(available_bandwidth, frequency, distance)
    results = calculator.perform_calculations()

    print(f"Transmitted Power: {results['P_tx']:.2f} m/s")  # Speed is used as transmitted power
    print(f"Free Space Path Loss (FSPL): {results['FSPL']:.2f} dB")
    print(f"SNR (linear): {results['SNR_linear']:.2f}")
    print(f"Channel Capacity: {results['Channel_Capacity_Mbps']:.2f} Mbps")
    print(f"Bitrate: {results['Bitrate_Mbps']:.2f} Mbps")
    print(f"Bandwidth usage: {results['Bandwidth usage']:.2f}")
