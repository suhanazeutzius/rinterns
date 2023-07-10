# Import required python packages
import numpy as np
import math
import matplotlib.pyplot as plt
import scipy.signal

# Import custom python packages
from flatirons.gps_gen import *
from flatirons.gps_dsp import *
from flatirons.parse import *

# Import custom matplotlib styling
plt.style.use('flatirons/flatirons.mplstyle')

# Create clean simulated GPS signal
fsample = 10*(1.023e6) # [Hz]
sig = makeGPSClean(29, num_periods=2, sample_rate=fsample)

# Add noise to signal
noise_power_AWGN_dB = 16
noise_power_AWGN = math.pow(10,(noise_power_AWGN_dB/10))
sig = makeGPSNoisy(sig, noise_power_AWGN)
visualizeSignal(sig, 0, fsample, 'Simulated GPS Signal')

# Apply doppler shift
t = np.linspace(0, len(sig)/fsample, num=len(sig), endpoint=False)
sig = sig * np.exp(1j*2*np.pi*890*t)

# Define frequencies
fGPS = 1575.42e6 # [Hz]
#fsample = 3.096e6 # [Hz]

# Define physical properties of system
Rearth = 6378e3 # [m]
hGPS = 20200e3 # [m]
Vsat = 929 # [m/s]
max_elevation_angle = np.deg2rad(26.3)

# Define constants
c = 299792458 # [m/s]

# Calculate maximum doppler shift
Rgps = Rearth + hGPS # [m]
Rsat = np.sqrt((Rearth**2)+(Rgps**2)-(2*Rearth*Rgps*np.cos(max_elevation_angle)))
alpha = math.pi-np.arcsin(np.sin(max_elevation_angle)*Rgps/Rsat) # [rad]
slant_angle = alpha-(math.pi/2) # [rad]
fdoppler = np.floor(Vsat*np.cos(slant_angle)*fGPS/c) # [Hz]

prns = [5,13,20,29]
_ = correlateSignal(sig, fsample, 'Simulated PRN 13', fdoppler, 10, prns=prns)
