# Import required python packages
import numpy as np
import math
import matplotlib.pyplot as plt
import scipy.signal

# Import custom python packages
from flatirons.gps_gen import *
from flatirons.gps_dsp import *
from flatirons.parse import *

# Use custom matplotlib styling
plt.style.use('flatirons/flatirons.mplstyle')

# Define frequencies
fcenter_SDR = 1573.42e6 # [Hz]
fsample = 30.69e6 # [Hz]
fGPS = 1575.42e6 # [Hz]

# Define physical properties of system
Rearth = 6378e3 # [m]
hGPS = 20200e3 # [m]
Vsat = 929 # [m/s]
max_elevation_angle = np.deg2rad(26.3)

# Define constants
c = 299792458 # [m/s]

# Define data properties
file_name = 'data/Samples_Jun_28/Data8.dat'
num_samples = 306900

# Read in data
I, Q = dat_parse(file_name, num_samples)
signal = I + 1j*Q
#visualizeSignal(signal, fcenter_SDR, fsample, 'Received Signal 6/28/23')

# Remove first 2 ms of signal
signal = trimSignal(signal, fsample)
#visualizeSignal(signal, fcenter_SDR, fsample, 'Received Signal 6/28/23')

# Bandpass filter signal
signal = filterSignal((fGPS-fcenter_SDR), fsample, signal, ['fir', 'bandpass'], bandwidth=1.5e6, order=100)
#visualizeSignal(signal, fcenter_SDR, fsample, 'Received Signal 6/28/23')

# Tuen filter down to baseband
signal = tuneSignal(fGPS-fcenter_SDR, fsample, signal)
#visualizeSignal(signal, fGPS, fsample, 'Received Signal 6/28/23')

# Decimate signal
signal = scipy.signal.decimate(signal, 10)
#visualizeSignal(signal, fGPS, fsample, 'Received Signal 6/28/23')

# Calculate maximum doppler shift
Rgps = Rearth + hGPS # [m]
Rsat = np.sqrt((Rearth**2)+(Rgps**2)-(2*Rearth*Rgps*np.cos(max_elevation_angle)))
alpha = math.pi-np.arcsin(np.sin(max_elevation_angle)*Rgps/Rsat) # [rad]
slant_angle = alpha-(math.pi/2) # [rad]
fdoppler = np.floor(Vsat*np.cos(slant_angle)*fGPS/c) # [Hz]

# Perform correlation analysis
#prns = [8,10,15,18,23,24,27,32]
prns = [18]
[corr0, corr1] = correlateSignal(signal, 3.069e6, 'Signal 1', fdoppler, 10, prns=prns, freq_range=np.arange(-3e3,3e3,10), plot=False)
