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

# prepareDataForMonopulse() outputs the data required for the monopulse argument to run
#
# Inputs:
#   file_name        : name of the data file                                     [string]
#   prn              : PRN that is being tracked                                    [int]
#   wire_delay       : delay caused by a longer second wire (seconds)             [float]
#   plot_correlation : option controlling whether to plot the correlation data      [T/F]
def prepareDataForMonopulse(file_name, prn, wire_delay, plot_correlation):
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
    
    # Read in data
    I1, Q1, I2, Q2 = csv_parse(file_name)
    sig1 = I1 + 1j*Q1
    sig2 = I2 + 1j*Q2
    
    # Remove first 2 ms of signal
    sig1 = trimSignal(sig1, fsample)
    sig2 = trimSignal(sig2, fsample)
    
    # Remove wire delay from faster channel
    sig1 = trimSignal(sig1, fsample, trim_length=wire_delay)
    
    # Lowpass filter signal
    sig1 = filterSignal((fGPS-fcenter_SDR), fsample, sig1, ['fir', 'lowpass'], bandwidth=1e6, order=100)
    sig2 = filterSignal((fGPS-fcenter_SDR), fsample, sig2, ['fir', 'lowpass'], bandwidth=1e6, order=100)
    
    # Calculate maximum doppler shift
    Rgps = Rearth + hGPS # [m]
    Rsat = np.sqrt((Rearth**2)+(Rgps**2)-(2*Rearth*Rgps*np.cos(max_elevation_angle)))
    alpha = math.pi-np.arcsin(np.sin(max_elevation_angle)*Rgps/Rsat) # [rad]
    slant_angle = alpha-(math.pi/2) # [rad]
    fdoppler = np.floor(Vsat*np.cos(slant_angle)*fGPS/c) # [Hz]
    
    # Perform correlation analysis
    #global prns
    prns = [prn]
    _, fdoppler1 = correlateSignal(sig1, fsample, 'Rx 1', fdoppler, 10, prns=prns, plot_CAF=plot_correlation)
    #print("The doppler frequency shift for Rx 1 is: " + str(fdoppler1) + " Hz")
    print("loading...")
    _, fdoppler2 = correlateSignal(sig2, fsample, 'Rx 2', fdoppler, 10, prns=prns, plot_CAF=plot_correlation)
    #print("The doppler frequency shift for Rx 2 is: " + str(fdoppler2) + " Hz")
    fdoppler = np.mean([fdoppler1, fdoppler2])
    
    # Extract correlation data for monopulse algorithm
    corr1 = correlateForMonopulse(sig1, fsample, fdoppler, prn, 'Rx 1', plot=False)
    corr2 = correlateForMonopulse(sig2, fsample, fdoppler, prn, 'Rx 2', plot=False)

    # Return data for monopulse algorithm
    return corr1, corr2

if __name__ == "__main__":
    # Define data properties
    #global prn
    file_name = 'data/Samples_Jul_6/sat12_1009.csv'
    prn = 12
    plot_correlation = True
    wire_delay = 7.13e-9
    
    # Call function
    Rx1, Rx2 = prepareDataForMonopulse(file_name, prn, wire_delay, plot_correlation)

    plt.show()
