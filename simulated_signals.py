# Import required python packages
import numpy as np
import math
import matplotlib.pyplot as plt
import scipy.signal

# Import custom python packages
from flatirons.gps_gen import *
from flatirons.gps_dsp import *
from flatirons.parse import *

# Create clean simulated GPS signal
sig = makeGPSClean(13, 0, sample_rate=3.069e6)

# Add noise to signal
noise_power_AWGN_dB = 16
noise_power_AWGN = math.pow(10,(noise_power_AWGN_dB/10))
sig = makeGPSNoisy(sig, noise_power_AWGN)

# Visualize signal
visualizeGPS(sig, 0, 3.069e6, 'Simulated PRN 13')
