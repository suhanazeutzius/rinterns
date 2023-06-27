# Imort required python packages
import numpy as np
import matplotlib.pyplot as plt

# Import custom functions
from flatirons.prn_gen import *

# makeGPSClean simulated an ideal GPS signal for a given C/A code (prn)
#
# Inputs:
#   prn          : prn number between 1-31 (inclusive)                      [int]
#   data_bit     : data bit, either 0 or 1                                  [int]
#   sample_ratio : ratio of SDR sampling rate to GPS chip rate              [int]
#                  (fsample/fchip)
#   num_periods  : number of C/A code periods in signal                     [int]
#
# Outputs:
#   signal       : simulated ideal GPS signal   [numpy array of type np.complex_]
def makeGPSClean(prn, data_bit, sample_ratio, num_periods=1, sample_rate=None):
    # Generate PRN (C/A) code
    ca = cacode(prn, sample_rate=sample_rate)

    # Convert PRN code to 0s and 1s
    ca = (ca > 0).astype(int)
    
    # Generate vector for data bit
    if data_bit == 0:
        dat = np.zeros(len(ca))
    elif data_bit == 1:
        dat = np.ones(len(ca))
    dat = dat.astype(int)
    
    # Perform modulo-2 addition
    gps = np.zeros(len(ca))
    for i in np.arange(len(gps)):
        if ca[i] == dat[i]:
            gps[i] = 0
        else:
            gps[i] = 1
    gps = gps.astype(int)
    
    # Perform BPSK modulation and convert to IQ data
    I = np.ones(len(gps))
    I[gps == 1] = -1
    Q = np.zeros(len(gps))
    signal = I + 1j*Q

    # Tile signal
    signal = np.tile(signal, num_periods)

#    # Resample signal up to bladeRF sampling frequency
#    resampled = []
#    for i in np.arange(len(signal)):
#        for _ in range(sample_ratio):
#            resampled.append(signal[i])
#    signal = np.asarray(resampled)
#    del resampled

    # Return signal
    return signal

# makeGPSNoisy() adds noise to an ideal GPS signal
#
# Inputs:
#   signal            : ideal GPS signal        [numpy array of type np.complex_]
#   noise_power_AWGN  : AWGN noise power                                  [float]
#   noise_power_phase : phase noise power                                 [float]
#
# Outputs:
#   signal            : noisy GPS signal        [numpy array of type np.complex_]
def makeGPSNoisy(signal, noise_power_AWGN, noise_power_phase=0):
    # Add complex AWGN noise
    n = (np.random.randn(len(signal)) + 1j*np.random.randn(len(signal)))*np.sqrt(noise_power_AWGN/2)
    signal = signal + n
     
    # Add phase noise
    p = np.random.randn(len(signal)) * noise_power_phase
    signal_after = signal * np.exp(1j*p)

    # Return noisy signal
    return signal
