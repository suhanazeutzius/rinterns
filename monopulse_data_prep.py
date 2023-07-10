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


def gen_sim_signals():
    prns = [1, 7, 13, 22, 27]
    doppler_shifts = [-500, 1000, 1350, -1830, 400]
    a1_phase_shifts = [10, 0, -13, 4, 20]
    a2_phase_shifts = [10, 60, -35, -75, 24]
    fsample = 10 * 1.023e6  # [Hz]
    a1_signals = []
    a2_signals = []
    for i in range(0, len(prns)):
        # make clean gps signal
        sig = makeGPSClean(prns[i], num_periods=2, sample_rate=fsample)
        # make noisy gps signal
        noise_power_AWGN_dB = 16
        noise_power_AWGN = math.pow(10, (noise_power_AWGN_dB / 10))
        sig = makeGPSNoisy(sig, noise_power_AWGN)
        # Shift signal by doppler shift frequency
        t = np.linspace(0, len(sig) / fsample, num=len(sig), endpoint=False)
        sig = sig * np.exp(-1j * 2 * np.pi * doppler_shifts[i] * t)
        # shift antenna 1 signal by some phase
        sig = [sig[j] * np.exp(a1_phase_shifts[i] * 1j) for j in range(len(sig))]
        a1_signals.append(sig)
        sig = [sig[j] * np.exp(a2_phase_shifts[i] * 1j) for j in range(len(sig))]
        a2_signals.append(sig)

    a1_total_signal = np.zeros(len(a1_signals[0]))
    a2_total_signal = np.zeros(len(a1_signals[0]))
    for i in range(len(a1_signals)):
        a1_total_signal = a1_total_signal + a1_signals[i]
        a2_total_signal = a2_total_signal + a2_signals[i]

    return a1_total_signal, a2_total_signal

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
    # sig2 = I2 + 1j*Q2
    
    # Remove first 2 ms of signal
    sig1 = trimSignal(sig1, fsample)
    # sig2 = trimSignal(sig2, fsample)
    
    # Remove wire delay from faster channel
    sig1 = trimSignal(sig1, fsample, trim_length=wire_delay)
    
    # Lowpass filter signal
    # sig1 = filterSignal((fGPS-fcenter_SDR), fsample, sig1, ['fir', 'lowpass'], bandwidth=1e6, order=100)
    # sig2 = filterSignal((fGPS-fcenter_SDR), fsample, sig2, ['fir', 'lowpass'], bandwidth=1e6, order=100)
    #

    sig1, sig2 = gen_sim_signals()
    # Calculate maximum doppler shift
    Rgps = Rearth + hGPS # [m]
    Rsat = np.sqrt((Rearth**2)+(Rgps**2)-(2*Rearth*Rgps*np.cos(max_elevation_angle)))
    alpha = math.pi-np.arcsin(np.sin(max_elevation_angle)*Rgps/Rsat) # [rad]
    slant_angle = alpha-(math.pi/2) # [rad]
    fdoppler = np.floor(Vsat*np.cos(slant_angle)*fGPS/c) # [Hz]
    
    # Perform correlation analysis
    prns = [prn]
    _, fdoppler1 = correlateSignal(sig1, fsample, 'Rx 1', fdoppler, 10, prns=prns, plot_CAF=plot_correlation)
    print("The doppler frequency shift for Rx 1 is: " + str(fdoppler1) + " Hz")
    _, fdoppler2 = correlateSignal(sig2, fsample, 'Rx 2', fdoppler, 10, prns=prns, plot_CAF=plot_correlation)
    print("The doppler frequency shift for Rx 2 is: " + str(fdoppler2) + " Hz")
    fdoppler = np.mean([fdoppler1, fdoppler2])
    # fdoppler = fdoppler1

    # phase2 = np.deg2rad(10)
    # sig2 = [sig1[i] * np.exp(phase2 * 1j) for i in range(len(sig1))]
    # print("Expected phase shift (deg): " + str(np.rad2deg(phase2)))

    # Extract correlation data for monopulse algorithm
    corr1 = correlateForMonopulse(sig1, fsample, fdoppler, prn, 'Rx 1', plot=True)
    corr2 = correlateForMonopulse(sig2, fsample, fdoppler, prn, 'Rx 2', plot=True)

    # Return data for monopulse algorithm
    return corr1, corr2

if __name__ == "__main__":
    # Define data properties
    file_name = 'data/Samples_Jul_6/sat12_1012.csv'
    prn = 12
    plot_correlation = True
    wire_delay = 7.13e-9
    
    # Call function
    Rx1, Rx2 = prepareDataForMonopulse(file_name, prn, wire_delay, plot_correlation)