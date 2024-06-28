import math
import random
import numpy as np
import decimal

class Channel_802_11:

    def __init__(self, available_bandwidth, frequency, P_tx):
        self.available_bandwidth = decimal.Decimal(str(available_bandwidth))  # Bandwidth in Hz
        self.frequency = decimal.Decimal(str(frequency))  # Frequency in GHz
        self.P_tx = decimal.Decimal(str(P_tx))  # Transmitted power in dBm
        self.P_n = decimal.Decimal(str(random.uniform(-70,-75)))  # Noise power in dBw, randomly generated
        self.n = decimal.Decimal(math.log2(1024))  # Bits per symbol for 1024-QAM
    
    def __calculate_fspl(self, distance):
        distance = decimal.Decimal(str(distance))
        fspl = 20 * distance.log10() + 20 * self.frequency.log10() + decimal.Decimal('32.4') 
        return fspl

    def __calculate_snr(self, fspl):
        std = random.uniform(1,3)
        X_s = decimal.Decimal(str(abs(np.random.normal(0, std))))
        print(X_s)  # shadowing component
        snr = self.P_tx - self.P_n - fspl  - (X_s *random.randint(0,2))
        if snr < 0 :
            snr = 0
        return snr
    
    def __calculate_channel_capacity(self, snr_linear):
        C = self.available_bandwidth * (1 + snr_linear).log10() / decimal.Decimal(math.log10(2))
        return C

    def __calculate_bitrate(self, C):
        Rb = C * decimal.Decimal('5') / decimal.Decimal('6') * decimal.Decimal(str(random.uniform(0.8, 1)))
        return Rb
    
    def __compute_Bandwidth_usage(self, C, Rb):
        Bandwidth_usage = Rb / C * decimal.Decimal('100')
        return Bandwidth_usage
    
    def __compute_tx(self, file_size, Rb):
        decimal.getcontext().prec = 50
        file_size = decimal.Decimal(str(file_size))
        Rb = decimal.Decimal(str(Rb))
        latency = file_size / Rb
        return latency
    
    def perform_calculations(self, file_size, distance):
        fspl = self.__calculate_fspl(distance)
        snr_db = self.__calculate_snr(fspl)
        snr_linear = 10 ** (snr_db / decimal.Decimal('10'))
        capacity = self.__calculate_channel_capacity(snr_linear)
        bitrate = self.__calculate_bitrate(capacity)
        usage = self.__compute_Bandwidth_usage(capacity, bitrate)
        tx_time = self.__compute_tx(file_size, bitrate)

        return {
            "P_tx": self.P_tx,
            "P_n": self.P_n,
            "FSPL": fspl,
            "SNR_dB": snr_db,
            "SNR_linear": snr_linear,
            "Channel_Capacity_Mbps": capacity * decimal.Decimal('10')**decimal.Decimal('-6'),
            "Bitrate_Mbps": bitrate * decimal.Decimal('10')**decimal.Decimal('-6'),
            "Bandwidth_usage": usage,
            "tx_time": tx_time    
        }
    
if __name__ == "__main__":
    random.seed()  # Set seed for reproducibility
    available_bandwidth = 80e6  # 80 MHz
    frequency = 5  # 5 GHz
    distance = 100 # Distance in meters

    file_path = "/home/bert/github/5G_CARS_1/Airsim/images/image_3.png"
    import os
    file_size = 100000
    calculator = Channel_802_11(available_bandwidth, frequency, P_tx=20)
    results = calculator.perform_calculations(file_size, distance)

    print(f"Transmitted Power: {results['P_tx']:.2f} dB")  # Speed is used as transmitted power
    print(f"Free Space Path Loss (FSPL): {results['FSPL']:.2f} dB")
    print(f"SNR in Db:  {results['SNR_dB']:.2f} dB" )
    print(f"SNR (linear): {results['SNR_linear']:.2f}")
    print(f"Channel Capacity: {results['Channel_Capacity_Mbps']:.2f} Mbps")
    print(f"Bitrate: {results['Bitrate_Mbps']:.2f} Mbps")
    print(f"Bandwidth usage: {results['Bandwidth_usage']:.2f}")
    print(f"Transmission time: {results['tx_time']:.6f} s")
    print(f"Noise power : {results['P_n']:.6f} dB")

