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



def getPhaseOffset(ch1, ch2, angle=True):
    """Get phase offset between two channels

    @param ch1, ch2 -- complex correlation time output for ch1 and ch2
    @return list of phase offsets calculated from peaks above threshold
    """
    phaseOffsets = []

    median = abs(np.median(ch1))
    max = abs(np.max(ch1))
    max_median = max / median

    threshold = 0.90 * max_median

    for i in range(len(ch1)):
        if(abs(ch1[i]/median) > threshold and abs(ch2[i]/median) > threshold):
            if(not(angle)):
                p1 = np.arctan(np.imag(ch1[i]) / np.real(ch1[i]))
                p2 = np.arctan(np.imag(ch2[i]) / np.real(ch2[i]))
            else:
                p1 = np.angle(ch1[i])
                p2 = np.angle(ch2[i])
            phaseOffsets.append(p2 - p1)

    return phaseOffsets




def plotPhases(ch1, ch2):
    figure, ax = plt.subplots(2, 1, sharex=True)

    phase1 = [np.arctan(np.imag(ch1[i])/np.real(ch1[i])) for i in range(len(ch1))]
    phase2 = [np.arctan(np.imag(ch2[i])/np.real(ch2[i])) for i in range(len(ch2))]

    phase1 = [np.rad2deg(phase) for phase in phase1]
    phase2 = [np.rad2deg(phase) for phase in phase2]

    t1 = np.linspace(1-len(ch1), len(ch1), len(ch1))
    t2 = np.linspace(1-len(ch2), len(ch2), len(ch2))

    ax[0].plot(t1, phase1)
    ax[0].set_title("Phases of Two Channel PRN Correlation")
    ax[0].set_ylabel("Phase of Rx1 Correlation")
    ax[1].plot(t2, phase2)
    ax[1].set_ylabel("Phase of Rx2 Correlation")
    ax[1].set_xlabel("Index")

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

    file_name = '/home/empire/Desktop/sample_46.csv'
    prn = 3
    plot_correlation = True
    wire_delay = 0
    
    Rx1, Rx2 = prepareDataForMonopulse(file_name, prn, wire_delay, plot_correlation)

    print("Using Angle()...")
    pOffsets = getPhaseOffset(Rx1, Rx2, angle=True)
    pOffsets = [np.rad2deg(p) for p in pOffsets]
    print("NUM: " + str(len(pOffsets)))
    print("MEAN: " + str(np.mean(pOffsets)))
    print("MEDIAN: " + str(np.median(pOffsets)))
    print("STD_DEV: " + str(np.std(pOffsets)))

    print("Using arctan()...")
    pOffsets = getPhaseOffset(Rx1, Rx2, angle=False)
    pOffsets = [np.rad2deg(p) for p in pOffsets]
    print("NUM: " + str(len(pOffsets)))
    print("MEAN: " + str(np.mean(pOffsets)))
    print("MEDIAN: " + str(np.median(pOffsets)))
    print("STD_DEV: " + str(np.std(pOffsets)))
