# Import required python packages
import numpy as np
import math
import matplotlib.pyplot as plt
import scipy.signal as signal

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
    prns = [prn]
    _, fdoppler1 = correlateSignal(sig1, fsample, 'Rx 1', fdoppler, 10, prns=prns, plot_CAF=plot_correlation)
    print("The doppler frequency shift for Rx 1 is: " + str(fdoppler1) + " Hz")
    _, fdoppler2 = correlateSignal(sig2, fsample, 'Rx 2', fdoppler, 10, prns=prns, plot_CAF=plot_correlation)
    print("The doppler frequency shift for Rx 2 is: " + str(fdoppler2) + " Hz")
    fdoppler = np.mean([fdoppler1, fdoppler2])
    
    # Extract correlation data for monopulse algorithm
    corr1 = correlateForMonopulse(sig1, fsample, fdoppler, prn, 'Rx 1', plot=True)
    corr2 = correlateForMonopulse(sig2, fsample, fdoppler, prn, 'Rx 2', plot=True)

    # Return data for monopulse algorithm
    return corr1, corr2


def calc_corr_phase_shift(corr1, corr2, plot_corr=False):
    """ ! Calculates the phase shift between two antennas using the phases of their correlation vectors.

    @param corr1        Correlation output of reference antenna
    @param corr2        Correlation output of second antenna
    @param plot_corr    If true, plot the normalized absolute value of the correlations

    @return             The phase difference between the two correlation vectors.

    @note               Return the opposite of the phase difference that is calculated, because the correlations use
                        complex conjugates of the signals.
    """
    corr1_abs = np.abs(corr1)
    corr2_abs = np.abs(corr2)
    c1 = corr1_abs / np.median(corr1_abs)
    c2 = corr2_abs / np.median(corr2_abs)

    peak_height = 8

    if plot_corr:
        fig2, ax2 = plt.subplots()
        ax2.set_xlabel('Correlation Index')
        ax2.set_ylabel('Correlation Peak Strength')
        ax2.set_title('Absolute Value of Correlations')
        # ax2.plot(range(len(corr1)), corr1)
        # ax2.plot(range(len(corr2)), corr2, '--')
        ax2.plot(range(len(c1)), c1)
        ax2.plot(range(len(c2)), c2, '--')
        plt.axhline(y=peak_height, color='k', linestyle=':')
        ax2.legend(['Channel 1', 'Channel 2'])
        plt.show()

    c1_indices, _ = signal.find_peaks(c1, height=peak_height)
    c2_indices = []
    to_delete = []
    for i in range(len(c1_indices)):
        c2_index = np.array(corr2_abs[c1_indices[i]-5:c1_indices[i]+6]).argmax() + (c1_indices[i] - 5)
        if c2[c2_index] > peak_height:
            c2_indices.append(c2_index)
        else:
            to_delete.append(i)
    c1_indices = np.delete(c1_indices, to_delete)

    phase_corr1 = []
    phase_corr2 = []
    for i in range(len(c1_indices)):
        phase_corr1.append(np.angle(corr1[c1_indices[i]]))
        phase_corr2.append(np.angle(corr2[c2_indices[i]]))

    phase_diff = [phase_corr1[i] - phase_corr2[i] for i in range(len(phase_corr1))]

    for i in range(len(phase_diff)):
        if phase_diff[i] < 0:
            phase_diff[i] += (2 * np.pi)

    # print([np.rad2deg(phase_diff[i]) for i in range(len(phase_diff))])
    print("standard deviation of phase difference: " + str(np.rad2deg(np.std(phase_diff))))
    # plt.hist(np.rad2deg(phase_diff))
    # plt.show()
    phase_diff_avg = np.average(phase_diff)
    phase_diff_med = np.median(phase_diff)

    print("Average phase: " + str(np.rad2deg(phase_diff_avg)))
    print("Median phase: " + str(np.rad2deg(phase_diff_med)))

    # get phase diff median between -pi and pi
    if (phase_diff_med < -np.pi and phase_diff_med > (-2 * np.pi)):
        phase_diff_med += (2 * np.pi)
    elif (phase_diff_med > np.pi and phase_diff_med < (2 * np.pi)):
        phase_diff_med -= (2 * np.pi)

    # get phase diff average between -pi and pi
    if (phase_diff_avg < -np.pi and phase_diff_avg > (-2 * np.pi)):
        phase_diff_avg += (2 * np.pi)
    elif (phase_diff_avg > np.pi and phase_diff_avg < (2 * np.pi)):
        phase_diff_avg -= (2 * np.pi)

    return -phase_diff_med  # return the opposite of the calculated phase shift




def getPhaseOffset(ch1, ch2, angle=True):
    """Get phase offset between two channels

    @param ch1, ch2 -- complex correlation time output for ch1 and ch2
    @return list of phase offsets calculated from peaks above threshold
    """
    phaseOffsets = []

    max_median1 = abs(np.max(ch1)) / abs(np.median(ch1))
    max_median2 = abs(np.max(ch2)) / abs(np.median(ch2))
    median1 =  abs(np.median(ch1))
    median2 = abs(np.median(ch2))
    threshold1 = 0.90 * max_median1
    threshold2 = 0.90 * max_median2

    for i in range(len(ch1)):
        if(abs(ch1[i]/median1) > threshold1 and abs(ch2[i]/median2) > threshold2):
            if(not(angle)):
                p1 = np.arctan(np.imag(ch1[i]) / np.real(ch1[i]))
                p2 = np.arctan(np.imag(ch2[i]) / np.real(ch2[i]))
            else:
                p1 = np.angle(ch1[i])
                p2 = np.angle(ch2[i])
            phaseOffsets.append(p2 - p1)

    return phaseOffsets




def plotPhases(phases):

    figure, axis = plt.subplots(1, 1)
    axis.set_title("")
    axis.set_xlabel("")
    axis.set_ylabel("")

    #axis.hist(phases)
    plt.show()



def combineDevices(filename1, filename2, fileout):
    """Combine a master & a slave csv to a single file

    @param filename1 -- input file 1 (will be first in line)
    @param filename2 -- input file 2 (will be second in line)
    @param fileout -- output csv file name
    @return none
    """
    import csv

    fout = open(fileout, "w")
    csvout = csv.writer(fout)

    fin1 = open(filename1, "r") 
    fin2 = open(filename2, "r")

    csv1 = csv.reader(fin1)
    csv2 = csv.reader(fin2)
    
    lines1 = []
    lines2 = []

    for line in csv1:
        lines1.append(line)
    for line in csv2:
        line[0] = (' ' + line[0])
        lines2.append(line)

    for i in range(min(len(lines1), len(lines2))):
        lines1[i].extend(lines2[i])
        csvout.writerow(lines1[i])

    fin1.close()
    fin2.close()
    fout.close()
    return


## MAIN PROGRAM ##

if __name__ == "__main__":
    # Define data properties
    #combineDevices("/mnt/c/users/ninja/desktop/samples/PRN_5_copper_slave.csv", "/mnt/c/users/ninja/desktop/samples/PRN_5_gray_master.csv", "/mnt/c/users/ninja/desktop/combo.csv")

    file_name = '/mnt/c/users/ninja/desktop/samples/PRN10_copper9.csv'
    prn = 10
    plot_correlation = True
    wire_delay = 0
    
    Rx1, Rx2 = prepareDataForMonopulse(file_name, prn, wire_delay, plot_correlation)

    print("Channel Phase:")
    calc_corr_phase_shift(Rx1, Rx2, True)

#    print("Using Angle()...")
#    pOffsets = getPhaseOffset(Rx1, Rx2, angle=True)
#    pOffsets = [np.rad2deg(p) for p in pOffsets]

#    print("NUM: " + str(len(pOffsets)))
#    print("MEAN: " + str(np.mean(pOffsets)))
#    print("MEDIAN: " + str(np.median(pOffsets)))
#    print("STD_DEV: " + str(np.std(pOffsets)))

#    print("Using arctan()...")
#    pOffsets = getPhaseOffset(Rx1, Rx2, angle=False)
#    pOffsets = [np.rad2deg(p) for p in pOffsets]
#    print("NUM: " + str(len(pOffsets)))
#    print("MEAN: " + str(np.mean(pOffsets)))
#    print("MEDIAN: " + str(np.median(pOffsets)))
#    print("STD_DEV: " + str(np.std(pOffsets)))
