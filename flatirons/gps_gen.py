# Imort required python packages
import numpy as np
import matplotlib.pyplot as plt

# Import custom functions
from flatirons.prn_gen import *

# makeGPSClean simulated an ideal GPS signal for a given C/A code (prn)
#
# Inputs:
#   prn          : prn number between 1-31 (inclusive)                      [int]
#   num_periods  : number of C/A code periods in signal                     [int]
#
# Outputs:
#   signal       : simulated ideal GPS signal   [numpy array of type np.complex_]
def makeGPSClean(prn, num_periods=1, sample_rate=None):
    # Generate PRN (C/A) code
    signal = cacode(prn, sample_rate=sample_rate)

    # Tile signal
    signal = np.tile(signal, num_periods)

    # Return signal
    return signal

# makeGPSNoisy() adds noise to an ideal GPS signal
#
# Inputs:
#   signal            : ideal GPS signal        [numpy array of type np.complex_]
#   noise_power_AWGN  : AWGN noise power (linear)                         [float]
#   noise_power_phase : phase noise power (linear)                        [float]
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
