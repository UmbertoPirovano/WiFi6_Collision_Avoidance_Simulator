import math
import random
import numpy as np
import decimal

class Channel_802_11:

    def __init__(self, available_bandwidth, frequency, P_tx):
        self.available_bandwidth = decimal.Decimal(str(available_bandwidth))  # Bandwidth in Hz
        self.frequency = decimal.Decimal(str(frequency))  # Frequency in GHz
        self.P_tx = decimal.Decimal(str(P_tx))  # Transmitted power in dBm
        self.P_n = decimal.Decimal(str(random.uniform(-105, -120)))  # Noise power in dBm, randomly generated
        self.modulation_order = decimal.Decimal('1024')  # Modulation order for 1024-QAM
        self.n = decimal.Decimal(math.log2(1024))  # Bits per symbol for 1024-QAM
    
    def calculate_fspl(self, distance):
        distance = decimal.Decimal(str(distance))
        fspl = 20 * distance.log10() + 20 * self.frequency.log10() + decimal.Decimal('32.4')
        return fspl

    def calculate_snr(self, fspl):
        std = random.uniform(1,4)
        X_s = decimal.Decimal(str(np.random.normal(0, std)))  # shadowing component
        snr = self.P_tx - self.P_n - fspl - (X_s *random.randint(0,2))
        return snr
    
    def calculate_channel_capacity(self, snr_linear):
        C = self.available_bandwidth * (1 + snr_linear).log10() / decimal.Decimal(math.log10(2))
        return C

    def calculate_bitrate(self, C):
        Rb = C * decimal.Decimal('5') / decimal.Decimal('6') * decimal.Decimal(str(random.uniform(0.8, 1)))
        return Rb
    
    def compute_Bandwidth_usage(self, C, Rb):
        Bandwidth_usage = Rb / C * decimal.Decimal('100')
        return Bandwidth_usage
    
    def compute_tx(self, Image_size, Rb):
        decimal.getcontext().prec = 50
        Image_size = decimal.Decimal(str(Image_size))
        Rb = decimal.Decimal(str(Rb))
        latency = Image_size / Rb
        return latency
    
    def perform_calculations(self, Image_size, distance):
        fspl = self.calculate_fspl(distance)
        snr_db = self.calculate_snr(fspl)
        snr_linear = 10 ** (snr_db / decimal.Decimal('10'))
        capacity = self.calculate_channel_capacity(snr_linear)
        bitrate = self.calculate_bitrate(capacity)
        usage = self.compute_Bandwidth_usage(capacity, bitrate)
        tx_time = self.compute_tx(Image_size, bitrate)

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


