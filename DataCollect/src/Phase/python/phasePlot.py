import matplotlib.pyplot as plt
from scipy import signal
import numpy as np
import os

import sampleAdjust as SA
import phaseCSV as CSV

def plot(fsample, signal1, signal2, signal3=None, signal4=None):
    """Plot two (to four) signals IQ constellation & time behavior

    @param signal1,2,3,4 -- complex sample lists (at least 1 and 2 are required)
    @param fsample -- samplerate of sampled signals
    @return none
    """
    plt.style.use(os.getcwd() + "/flatirons.mplstyle")

    # get number of signals passed
    numsignals = 2
    if(signal3):
        numsignals+=1
    if(signal4):
        numsignals+=1

    # Plot IQ constellations
    fig1, ax1 = plt.subplots(numsignals, 1, sharex=True)
    ax1[0].hexbin(np.real(signal1), np.imag(signal1), bins='log', cmap='Blues')
    ax1[0].axis('square')
    ax1[1].hexbin(np.real(signal2), np.imag(signal2), bins='log', cmap='Reds')
    ax1[1].axis('square')
    if(signal3):
        ax1[2].hexbin(np.real(signal3), np.imag(signal3), bins='log', cmap='Greens')
        ax1[2].axis('square')
    if(signal4):
        ax1[3].hexbin(np.real(signal4), np.imag(signal3), bins='log', cmap='Grays')
        ax1[3].axis('square')
    ax1[0].set_title('IQ Constellation of Sample')

    # Plot IQ signal time series
    dt = 1/fsample
    t1 = np.linspace(0, dt*(len(signal1)-1), num=len(signal1)) * (1e3)
    t2 = np.linspace(0, dt*(len(signal2)-1), num=len(signal2)) * (1e3)
    if(signal3):
        t3 = np.linspace(0, dt*(len(signal3)-1), num=len(signal3)) * (1e3)
    if(signal4):
        t4 = np.linspace(0, dt*(len(signal3)-1), num=len(signal4)) * (1e3)


    fig2, ax2 = plt.subplots(2, 1, sharex=True)

    # Plot un-altered channels on one axis
    ax2[0].plot(t1,np.real(signal1), label="Channel1")
    ax2[0].plot(t2,np.real(signal2), label="Channel2")
    if(signal3):
        ax2[0].plot(t3,np.real(signal3), label="Channel3")
    if(signal4):
        ax2[0].plot(t4,np.real(signal4), label="Channel4")
    ax2[0].grid(True)
    ax2[0].set_ylabel('I')
    ax2[0].legend()

    ax2[1].plot(t1,np.imag(signal1), label="Channel1")
    ax2[1].plot(t2,np.imag(signal2), label="Channel2")
    if(signal3):
        ax2[1].plot(t3, np.imag(signal3), label="Channel3")
    if(signal4):
        ax2[1].plot(t4, np.imag(signal4), label="Channel4")
    ax2[1].grid(True)
    ax2[1].set_ylabel('Q')
    ax2[1].set_xlabel('Time [ms]')
    ax2[1].legend()

    fig2.suptitle('Time Behavior of Sine Wave Sample')

    # Display plots
    plt.show()




def correlationPlot(filename, fsample, fcenter):
    """Plot correlations of a 2 channel sample pre
    and post sample alignment

    @param filename -- csv file to read
    @param fsample -- samplerate of sample
    @param fcenter -- center frequency of sample
    @return sample offset adjusted signals
    """

    figure, ax = plt.subplots(1, 1, sharex=True)

    # get signals lists
    signals = CSV.readcsv(filename)

    # get correlation
    cor1 = signal.correlate(signals[0], signals[1])
    t1 = np.arange(1-len(signals[0]), len(signals[0]))

    # get sample delta & impose delta
    delta_sample = SA.sampleDeltaCalculate(signals[0], signals[1])
    signals = SA.sampleDeltaImpose(signals[0], signals[1], delta_sample)

    # normalize correlations
    cor2 = signal.correlate(signals[0], signals[1])
    sum_cor2 = sum(cor2)
    cor2 = [i/sum_cor2 for i in cor2]
    t2 = np.arange(1-len(signals[0]), len(signals[0]))

    cor1 = cor1[:len(cor2)]
    sum_cor1 = sum(cor1)
    cor1 = [i/sum_cor1 for i in cor2]
    t1 = t1[:len(t2)]

    # plot correlations on same axis
    ax.plot(t1, cor2, "b", label="Pre-Adjustment")
    ax.plot(t2, cor2, "r", label="Post-Adjustment")
    ax.legend()
    ax.set_title("Correlation of BladeRF RX Channels 1 & 2")
    ax.set_xlabel("Sample Distance from 0")
    ax.set_ylabel("Normalized Correlation Value")

    plt.show()

    return signals
