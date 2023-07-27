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
fsample = 2.046e6 # [Hz]
fGPS = 1575.42e6 # [Hz]

# Define physical properties of system
Rearth = 6378e3 # [m]
hGPS = 20200e3 # [m]
Vsat = 929 # [m/s]
max_elevation_angle = np.deg2rad(26.3)

# Define constants
c = 299792458 # [m/s]

SNRs = []
for i in np.arange(11):
    if i == 0:
        # Define data properties
        file_name = 'data/Samples_Jul_25/PRN32_copper.csv'
    else:
        # Define data properties
        file_name = 'data/Samples_Jul_25/PRN32_copper'+str(i)+'.csv'
        
    # Read in data
    I1, Q1, I2, Q2 = csv_parse(file_name)
    signal = I1 + 1j*Q1

    # Remove first 2 ms of signal
    signal = trimSignal(signal, fsample)

    # Tune filter down to baseband
    signal = filterSignal((fGPS-fcenter_SDR), fsample, signal, ['butter', 'lowpass'], bandwidth=1e6, order=3) # ONLY WHEN fGPS = fcenter_SDR
    
    # Calculate maximum doppler shift
    Rgps = Rearth + hGPS # [m]
    Rsat = np.sqrt((Rearth**2)+(Rgps**2)-(2*Rearth*Rgps*np.cos(max_elevation_angle)))
    alpha = math.pi-np.arcsin(np.sin(max_elevation_angle)*Rgps/Rsat) # [rad]
    slant_angle = alpha-(math.pi/2) # [rad]
    fdoppler = np.floor(Vsat*np.cos(slant_angle)*fGPS/c) # [Hz]
    fdoppler = 3500
    
    # Perform correlation analysis
    prns = [32]
    prn, fdoppler = correlateSignal(signal, fsample, 'Signal 1', fdoppler, 10, prns=prns, plot_CAF=False, plot_3D=False)

    # Extract correlation plot for prn and doppler frequency shift
    corr = correlateForMonopulse(signal, fsample, fdoppler, prn, 'Signal 1')
    corr = np.abs(corr)
    corr = corr/np.median(corr)
    peaks = scipy.signal.find_peaks(corr, 7.5)
    average = np.mean(peaks[1]['peak_heights'])
    std = np.std(peaks[1]['peak_heights'])
    SNR = average/std
    SNRs.append(SNR)
    print('SNR: ' + str(SNR))

# Calculate average SNR
print('-----------------------')
print('Average SNR: ' + str(np.mean(SNRs)) + ' (' + str(10*np.log10(np.mean(SNRs))) + ' dB)')
