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
fcenter_SDR = 1575.42e6 # [Hz]
fsample = 2.048e6 # [Hz]
fGPS = 1575.42e6 # [Hz]

# Define physical properties of system
Rearth = 6378e3 # [m]
hGPS = 20200e3 # [m]
Vsat = 929 # [m/s]
max_elevation_angle = np.deg2rad(26.3)

# Define constants
c = 299792458 # [m/s]

# Define data properties
file_name = 'data/Samples_Jul_5/Data13.bin'
num_samples = 20480

# Read in data
I, Q = dat_parse(file_name)
signal = I + 1j*Q
#visualizeSignal(signal, fcenter_SDR, fsample, 'Received Signal 7/5/23')

# Remove first 2 ms of signal
signal = trimSignal(signal, fsample)
#visualizeSignal(signal, fcenter_SDR, fsample, 'Received Signal 7/5/23')

# Bandpass filter signal
#signal = filterSignal((fGPS-fcenter_SDR), fsample, signal, ['fir', 'bandpass'], bandwidth=1.5e6, order=100)
#visualizeSignal(signal, fcenter_SDR, fsample, 'Received Signal 6/28/23')

# Tune filter down to baseband
#signal = tuneSignal(fGPS-fcenter_SDR, fsample, signal)
signal = filterSignal((fGPS-fcenter_SDR), fsample, signal, ['butter', 'lowpass'], bandwidth=1e6, order=3) # ONLY WHEN fGPS = fcenter_SDR
#visualizeSignal(signal, fGPS, fsample, 'Received Signal 7/5/23')

## Decimate signal
#signal = scipy.signal.decimate(signal, 10)
##visualizeSignal(signal, fGPS, fsample, 'Received Signal 6/28/23')

# Calculate maximum doppler shift
Rgps = Rearth + hGPS # [m]
Rsat = np.sqrt((Rearth**2)+(Rgps**2)-(2*Rearth*Rgps*np.cos(max_elevation_angle)))
alpha = math.pi-np.arcsin(np.sin(max_elevation_angle)*Rgps/Rsat) # [rad]
slant_angle = alpha-(math.pi/2) # [rad]
fdoppler = np.floor(Vsat*np.cos(slant_angle)*fGPS/c) # [Hz]

# Perform correlation analysis
prns = [5,13,20,29]
#prns = np.arange(1,33)
prn, fdoppler_correction = correlateSignal(signal, fsample, 'Signal 1', fdoppler, 10, prns=prns)

# Extract correlation data for monopulse algorithm
corr = prepareDataForMonopulse(signal, fsample, fdoppler_correction, prn, 'Signal 1', plot=True)
