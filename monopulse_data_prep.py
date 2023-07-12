# Import required python packages
import numpy as np
import math
import matplotlib.pyplot as plt
import scipy.signal

# Import custom python packages
from flatirons.gps_gen import *
from flatirons.gps_dsp import *
from flatirons.parse import *
from lookup_table import gen_shifted_signals

# Use custom matplotlib styling
plt.style.use('flatirons/flatirons.mplstyle')


def gen_sim_signals():
    # prns = [1, 7, 13, 22, 27]
    prns = [1, 7, 13]
    doppler_shifts = [-500, 1000, 1350, -1830, 400]
    # a1_phase_shifts = [-5, 22, 10, 50, 105]
    # a2_phase_shifts = [45, 60, -45, 75, 24]
    elevation_angles = [0, 5, 10, 15, 20]
    azimuth_angles = [0, 45, 60, 135, 180]
    fsample = 2 * 1.023e6  # [Hz]
    a1_signals = []
    a2_signals = []
    a3_signals = []
    a4_signals = []
    for i in range(0, len(prns)):
        # make clean gps signal
        sig = makeGPSClean(prns[i], num_periods=3, sample_rate=fsample)
        all_sigs = gen_shifted_signals(sig, elevation_angles[i], azimuth_angles[i])
        for j in range(len(all_sigs)):
            # Shift signal by doppler shift frequency
            t = np.linspace(0, len(sig) / fsample, num=len(sig), endpoint=False)
            all_sigs[j] = all_sigs[j] * np.exp(-1j * 2 * np.pi * doppler_shifts[i] * t)
            # sig2 = sig2 * np.exp(-1j * 2 * np.pi * doppler_shifts[i] * t)

        # # shift antenna 1 signal by some phase
        # sig1 = [sig[k] * np.exp(np.deg2rad(a1_phase_shifts[i]) * 1j) for k in range(len(sig))]
        # # shift antenna 2 signal by some phase relative to antenna 1
        # sig2 = [sig1[k] * np.exp(np.deg2rad(a2_phase_shifts[i]) * 1j) for k in range(len(sig1))]

        # # Shift signal by doppler shift frequency
        # t = np.linspace(0, len(sig) / fsample, num=len(sig), endpoint=False)
        # sig1 = sig1 * np.exp(-1j * 2 * np.pi * doppler_shifts[i] * t)
        # sig2 = sig2 * np.exp(-1j * 2 * np.pi * doppler_shifts[i] * t)

        a1_signals.append(all_sigs[0])
        a2_signals.append(all_sigs[1])
        a3_signals.append(all_sigs[2])
        a4_signals.append(all_sigs[3])

    a1_total_signal = np.zeros(len(a1_signals[0]))
    a2_total_signal = np.zeros(len(a1_signals[0]))
    a3_total_signal = np.zeros(len(a1_signals[0]))
    a4_total_signal = np.zeros(len(a1_signals[0]))
    for i in range(len(a1_signals)):
        a1_total_signal = a1_total_signal + a1_signals[i]
        a2_total_signal = a2_total_signal + a2_signals[i]
        a3_total_signal = a3_total_signal + a3_signals[i]
        a4_total_signal = a4_total_signal + a4_signals[i]

    return a1_total_signal, a2_total_signal, a3_total_signal, a4_total_signal

# prepareDataForMonopulse() outputs the data required for the monopulse argument to run
#
# Inputs:
#   file_name        : name of the data file                                     [string]
#   prn              : PRN that is being tracked                                    [int]
#   wire_delay       : delay caused by a longer second wire (seconds)             [float]
#   plot_correlation : option controlling whether to plot the correlation data      [T/F]
#   rx2_offset       : hardware phase offset of channel 2 (radians)               [float]
#   rx3_offset       : hardware phase offset of channel 3 (radians)               [float]
#   rx4_offset       : hardware phase offset of channel 4 (radians)               [float]
def prepareDataForMonopulse(file_name, prn, wire_delay, plot_correlation, rx2_offset, rx3_offset, rx4_offset):
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
    
    # # Read in data
    # I1, Q1, I2, Q2 = csv_parse(file_name)
    # sig1 = I1 + 1j*Q1
    # sig2 = I2 + 1j*Q2
    #
    # # Remove first 2 ms of signal
    # sig1 = trimSignal(sig1, fsample, trim_length=0.003)
    # sig2 = trimSignal(sig2, fsample, trim_length=0.003)
    #
    # # Remove wire delay from faster channel
    # sig1 = trimSignal(sig1, fsample, trim_length=wire_delay)

    # # Remove phase offset between channels
    # sig2_corrected = [sig2[i] * np.exp(-rx2_offset * 1j) for i in range(len(sig2))]
    # sig2 = np.array(sig2_corrected)
    # del sig2_corrected
    # sig3_corrected = [sig3[i] * np.exp(-rx3_offset * 1j) for i in range(len(sig3))]
    # sig3 = np.array(sig3_corrected)
    # del sig3_corrected
    # sig4_corrected = [sig4[i] * np.exp(-rx4_offset * 1j) for i in range(len(sig4))]
    # sig4 = np.array(sig4_corrected)
    # del sig4_corrected

    sig1, sig2, sig3, sig4 = gen_sim_signals()
    # sig1 = makeGPSClean(7, num_periods=2, sample_rate=2.046e6)  # generate a reference signal
    # sig2 = [sig1[i] * np.exp(np.deg2rad(45) * 1j) for i in range(len(sig1))]  # generate a reference signal
    # ph = calc_phase_shift(sig1, sig2)
    # print(np.rad2deg(ph))

    # sig1 = makeGPSClean(7, num_periods=2, sample_rate=2.046e6)  # generate a reference signal
    # sig2 = [sig1[i] * np.exp(np.pi / 4 * 1j) for i in range(len(sig1))]  # generate a reference signal
    # ph = calc_phase_shift(sig1, sig2)
    # print(np.rad2deg(ph))

    # # Lowpass filter signal
    # sig1 = filterSignal((fGPS-fcenter_SDR), fsample, sig1, ['fir', 'lowpass'], bandwidth=1e6, order=100)
    # sig2 = filterSignal((fGPS-fcenter_SDR), fsample, sig2, ['fir', 'lowpass'], bandwidth=1e6, order=100)

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
    _, fdoppler3 = correlateSignal(sig3, fsample, 'Rx 1', fdoppler, 10, prns=prns, plot_CAF=plot_correlation)
    print("The doppler frequency shift for Rx 1 is: " + str(fdoppler3) + " Hz")
    _, fdoppler4 = correlateSignal(sig4, fsample, 'Rx 1', fdoppler, 10, prns=prns, plot_CAF=plot_correlation)
    print("The doppler frequency shift for Rx 1 is: " + str(fdoppler4) + " Hz")
    fdoppler = np.mean([fdoppler1, fdoppler2, fdoppler3, fdoppler4])
    # fdoppler = 0
    # sig1, sig2 = gen_sim_signals()

    # phase2 = np.deg2rad(45)
    # sig2 = [sig1[i] * np.exp(phase2 * 1j) for i in range(len(sig1))]
    # phase2 = calc_phase_shift(sig1, sig2)
    # print("Expected phase shift (deg): " + str(np.rad2deg(phase2)))

    # Extract correlation data for monopulse algorithm
    corr1 = correlateForMonopulse(sig1, fsample, fdoppler, prn, 'Rx 1', plot=False)
    corr2 = correlateForMonopulse(sig2, fsample, fdoppler, prn, 'Rx 2', plot=False)
    corr3 = correlateForMonopulse(sig3, fsample, fdoppler, prn, 'Rx 3', plot=False)
    corr4 = correlateForMonopulse(sig4, fsample, fdoppler, prn, 'Rx 4', plot=False)

    # Return data for monopulse algorithm
    return corr1, corr2, corr3, corr4

if __name__ == "__main__":
    # Define data properties
    file_name = 'data/Samples_Jul_6/sat12_1012.csv'
    prn = 12
    plot_correlation = True
    wire_delay = 8.13e-9
    
    # Call function
    Rx1, Rx2 = prepareDataForMonopulse(file_name, prn, wire_delay, plot_correlation)
