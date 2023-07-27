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


def gen_sim_signals(e1, a1, fsample):
    """
    ! Simulates what 4 antennas in a square array would receive if there were 5 satellites in range.

    @param fsample  Sample rate of the signal to generate

    @note           No noise added to signals
    """
    prns = [1, 7, 13, 22, 27]
    # prns = [1, 7, 13]
    doppler_shifts = [-500, 1000, 1350, -1830, 400]
    elevation_angles = [e1, 5, 10, 15, 20]
    azimuth_angles = [a1, 45, 60, 135, 180]
    noise_power_AWGN_dB = 20
    noise_power_AWGN = math.pow(10, (noise_power_AWGN_dB / 10))
    a1_signals = []
    a2_signals = []
    a3_signals = []
    a4_signals = []
    for i in range(0, len(prns)):
        # make clean gps signal
        sig = makeGPSClean(prns[i], num_periods=10, sample_rate=fsample)
        sig = makeGPSNoisy(sig, noise_power_AWGN)
        all_sigs = gen_shifted_signals(sig, elevation_angles[i], azimuth_angles[i])
        for j in range(len(all_sigs)):
            # Shift signal by doppler shift frequency
            t = np.linspace(0, len(sig) / fsample, num=len(sig), endpoint=False)
            all_sigs[j] = all_sigs[j] * np.exp(1j * 2 * np.pi * doppler_shifts[i] * t)

        a1_signals.append(all_sigs[0])
        a2_signals.append(all_sigs[1])
        a3_signals.append(all_sigs[2])
        a4_signals.append(all_sigs[3])

    a1_total_signal = np.zeros(len(a1_signals[0]))
    a2_total_signal = np.zeros(len(a1_signals[0]))
    a3_total_signal = np.zeros(len(a1_signals[0]))
    a4_total_signal = np.zeros(len(a1_signals[0]))
    # each antenna is receiving the sum of all satellite signals
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
def prepareDataForMonopulse(file_name, prn, plot_correlation, rx2_offset=0, rx3_offset=0, rx4_offset=0):
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
    
    # Read in data
    I1, Q1, I2, Q2, I3, Q3, I4, Q4 = csv_parse(file_name)
    sig1 = I1 + 1j*Q1
    sig2 = I2 + 1j*Q2
    sig3 = I3 + 1j*Q3
    sig4 = I4 + 1j*Q4

    # Remove first 2 ms of signal
    sig1 = trimSignal(sig1, fsample, trim_length=0.002)
    sig2 = trimSignal(sig2, fsample, trim_length=0.002)
    sig3 = trimSignal(sig3, fsample, trim_length=0.002)
    sig4 = trimSignal(sig4, fsample, trim_length=0.002)

    # Remove phase offset between channels
    sig2_corrected = [sig2[i] * np.exp(rx2_offset * 1j) for i in range(len(sig2))]
    sig2 = np.array(sig2_corrected)
    del sig2_corrected
    sig3_corrected = [sig3[i] * np.exp(rx3_offset * 1j) for i in range(len(sig3))]
    sig3 = np.array(sig3_corrected)
    del sig3_corrected
    sig4_corrected = [sig4[i] * np.exp(rx4_offset * 1j) for i in range(len(sig4))]
    sig4 = np.array(sig4_corrected)
    del sig4_corrected

    # Lowpass filter signal
    sig1 = filterSignal((fGPS-fcenter_SDR), fsample, sig1, ['fir', 'lowpass'], bandwidth=1e6, order=100)
    sig2 = filterSignal((fGPS-fcenter_SDR), fsample, sig2, ['fir', 'lowpass'], bandwidth=1e6, order=100)
    sig3 = filterSignal((fGPS - fcenter_SDR), fsample, sig3, ['fir', 'lowpass'], bandwidth=1e6, order=100)
    sig4 = filterSignal((fGPS - fcenter_SDR), fsample, sig4, ['fir', 'lowpass'], bandwidth=1e6, order=100)

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
    _, fdoppler3 = correlateSignal(sig3, fsample, 'Rx 3', fdoppler, 10, prns=prns, plot_CAF=plot_correlation)
    print("The doppler frequency shift for Rx 3 is: " + str(fdoppler3) + " Hz")
    _, fdoppler4 = correlateSignal(sig4, fsample, 'Rx 4', fdoppler, 10, prns=prns, plot_CAF=plot_correlation)
    print("The doppler frequency shift for Rx 4 is: " + str(fdoppler4) + " Hz")
    fdoppler = np.mean([fdoppler1, fdoppler2, fdoppler3, fdoppler4])

    # Extract correlation data for monopulse algorithm
    corr1 = correlateForMonopulse(sig1, fsample, fdoppler, prn, 'Rx 1', plot=False)
    corr2 = correlateForMonopulse(sig2, fsample, fdoppler, prn, 'Rx 2', plot=False)
    corr3 = correlateForMonopulse(sig3, fsample, fdoppler, prn, 'Rx 3', plot=False)
    corr4 = correlateForMonopulse(sig4, fsample, fdoppler, prn, 'Rx 4', plot=False)
    # corr1_abs = np.abs(corr1)
    # corr2_abs = np.abs(corr2)
    # c1 = corr1_abs / np.median(corr1_abs)
    # c2 = corr2_abs / np.median(corr2_abs)
    # fig2, ax2 = plt.subplots()
    # ax2.plot(range(len(c2)), c2, '--')
    # ax2.plot(range(len(c1)), c1)
    # plt.title("absolute value of correlations")
    # plt.show()

    # Return data for monopulse algorithm
    return corr1, corr2, corr3, corr4


def prepareDataForMonopulse_2(file_name, prn, plot_correlation, rx2_offset=0, rx3_offset=0, rx4_offset=0):
    # Define frequencies
    fcenter_SDR = 1575.42e6  # [Hz]
    fsample = 2.046e6  # [Hz]
    fGPS = 1575.42e6  # [Hz]

    # Define physical properties of system
    Rearth = 6378e3  # [m]
    hGPS = 20200e3  # [m]
    Vsat = 929  # [m/s]
    max_elevation_angle = np.deg2rad(26.3)

    # Define constants
    c = 299792458  # [m/s]

    # Read in data
    I1, Q1, I2, Q2 = csv_parse(file_name)
    sig1 = I1 + 1j * Q1
    sig2 = I2 + 1j * Q2

    # Remove first 2 ms of signal
    sig1 = trimSignal(sig1, fsample, trim_length=0.002)
    sig2 = trimSignal(sig2, fsample, trim_length=0.002)

    # Remove phase offset between channels
    sig2_corrected = [sig2[i] * np.exp(rx2_offset * 1j) for i in range(len(sig2))]
    sig2 = np.array(sig2_corrected)
    del sig2_corrected

    # Lowpass filter signal
    sig1 = filterSignal((fGPS - fcenter_SDR), fsample, sig1, ['fir', 'lowpass'], bandwidth=1e6, order=100)
    sig2 = filterSignal((fGPS - fcenter_SDR), fsample, sig2, ['fir', 'lowpass'], bandwidth=1e6, order=100)

    # Calculate maximum doppler shift
    Rgps = Rearth + hGPS  # [m]
    Rsat = np.sqrt((Rearth ** 2) + (Rgps ** 2) - (2 * Rearth * Rgps * np.cos(max_elevation_angle)))
    alpha = math.pi - np.arcsin(np.sin(max_elevation_angle) * Rgps / Rsat)  # [rad]
    slant_angle = alpha - (math.pi / 2)  # [rad]
    fdoppler = np.floor(Vsat * np.cos(slant_angle) * fGPS / c)  # [Hz]

    # Perform correlation analysis
    prns = [prn]
    _, fdoppler1 = correlateSignal(sig1, fsample, 'Rx 1', fdoppler, 10, prns=prns, plot_CAF=plot_correlation)
    print("The doppler frequency shift for Rx 1 is: " + str(fdoppler1) + " Hz")
    _, fdoppler2 = correlateSignal(sig2, fsample, 'Rx 2', fdoppler, 10, prns=prns, plot_CAF=plot_correlation)
    print("The doppler frequency shift for Rx 2 is: " + str(fdoppler2) + " Hz")
    fdoppler = np.mean([fdoppler1, fdoppler2])

    # Extract correlation data for monopulse algorithm
    corr1 = correlateForMonopulse(sig1, fsample, fdoppler, prn, 'Rx 1', plot=False)
    corr2 = correlateForMonopulse(sig2, fsample, fdoppler, prn, 'Rx 2', plot=False)

    # Return data for monopulse algorithm
    return corr1, corr2


def prepareDataForMonopulse_sim(prn, elevation, azimuth, plot_correlation=False):
    # Define frequencies
    fcenter_SDR = 1575.42e6  # [Hz]
    fsample = 2 * 1.023e6  # [Hz]
    fGPS = 1575.42e6  # [Hz]

    # Define physical properties of system
    Rearth = 6378e3  # [m]
    hGPS = 20200e3  # [m]
    Vsat = 929  # [m/s]
    max_elevation_angle = np.deg2rad(26.3)

    # Define constants
    c = 299792458  # [m/s]

    sig1, sig2, sig3, sig4 = gen_sim_signals(elevation, azimuth, fsample)

    # sig1 = makeGPSClean(1, num_periods=5, sample_rate=fsample)
    # phase2 = ((2 * np.pi * 0.5) / 1) * np.sin(np.deg2rad(10))
    # sig2 = [sig1[i] * np.exp(phase2 * 1j) for i in range(len(sig1))]

    # Calculate maximum doppler shift
    Rgps = Rearth + hGPS  # [m]
    Rsat = np.sqrt((Rearth ** 2) + (Rgps ** 2) - (2 * Rearth * Rgps * np.cos(max_elevation_angle)))
    alpha = math.pi - np.arcsin(np.sin(max_elevation_angle) * Rgps / Rsat)  # [rad]
    slant_angle = alpha - (math.pi / 2)  # [rad]
    fdoppler = np.floor(Vsat * np.cos(slant_angle) * fGPS / c)  # [Hz]

    # Perform correlation analysis
    prns = [prn]
    _, fdoppler1 = correlateSignal(sig1, fsample, 'Rx 1', fdoppler, 10, prns=prns, plot_CAF=plot_correlation)
    print("The doppler frequency shift for Rx 1 is: " + str(fdoppler1) + " Hz")
    _, fdoppler2 = correlateSignal(sig2, fsample, 'Rx 2', fdoppler, 10, prns=prns, plot_CAF=plot_correlation)
    print("The doppler frequency shift for Rx 2 is: " + str(fdoppler2) + " Hz")
    _, fdoppler3 = correlateSignal(sig3, fsample, 'Rx 3', fdoppler, 10, prns=prns, plot_CAF=plot_correlation)
    print("The doppler frequency shift for Rx 3 is: " + str(fdoppler3) + " Hz")
    _, fdoppler4 = correlateSignal(sig4, fsample, 'Rx 4', fdoppler, 10, prns=prns, plot_CAF=plot_correlation)
    print("The doppler frequency shift for Rx 4 is: " + str(fdoppler4) + " Hz")
    if None not in [fdoppler1, fdoppler2, fdoppler3, fdoppler4]:
        fdoppler = np.mean([fdoppler1, fdoppler2, fdoppler3, fdoppler4])

        # Extract correlation data for monopulse algorithm
        corr1 = correlateForMonopulse(sig1, fsample, fdoppler, prn, 'Rx 1', plot=False)
        corr2 = correlateForMonopulse(sig2, fsample, fdoppler, prn, 'Rx 2', plot=False)
        corr3 = correlateForMonopulse(sig3, fsample, fdoppler, prn, 'Rx 3', plot=False)
        corr4 = correlateForMonopulse(sig4, fsample, fdoppler, prn, 'Rx 4', plot=False)
    else:
        corr1 = None
        corr2 = None
        corr3 = None
        corr4 = None

    # Return data for monopulse algorithm
    return corr1, corr2, corr3, corr4
    # return corr1, corr2

if __name__ == "__main__":
    # Define data properties
    file_name = 'data/Samples_Jul_17/PRN_18_Rx2_Rx1.csv'
    prn = 18
    plot_correlation = True
    wire_delay = 0
    
    # Call function
    Rx1, Rx2 = prepareDataForMonopulse(file_name, prn, wire_delay, plot_correlation)
