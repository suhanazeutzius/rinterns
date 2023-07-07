import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import csv

import sys
sys.path.append("../");
import phaseadjust as pa



def plot2(signal1, signal2, fsample, fcenter):
    """Plot two signals IQ constellation & time behavior

    @param signal1,2 -- complex sample lists
    @param fsample -- samplerate of sampled signals
    @param fcenter -- center frequency of sampled signals
    @return none
    """
    # Plot IQ constellation
    fig1, ax1 = plt.subplots()
    ax1.hexbin(np.real(signal1), np.imag(signal1), bins='log', cmap='Blues')
    ax1.hexbin(np.real(signal2), np.imag(signal2), bins='log', cmap='Greens')
    ax1.set_title('IQ Constellation of Sample')
    ax1.axis('square')

    # Plot IQ signal time series
    dt = 1/fsample
    t1 = np.linspace(0, dt*(len(signal1)-1), num=len(signal1)) * (1e3)
    t2 = np.linspace(0, dt*(len(signal2)-1), num=len(signal2)) * (1e3)
    fig3, ax3 = plt.subplots(2, 1, sharex=True)
    ax3[0].plot(t1,np.real(signal1), label="Channel1")
    ax3[0].plot(t2,np.real(signal2), label="Channel2")
    ax3[0].grid(True)
    ax3[0].set_ylabel('I')
    ax3[0].legend()
    ax3[1].plot(t2,np.imag(signal1), label="Channel1")
    ax3[1].plot(t2,np.imag(signal2), label="Channel2")
    ax3[1].grid(True)
    ax3[1].set_ylabel('Q')
    ax3[1].set_xlabel('Time [ms]')
    ax3[1].legend()
    fig3.suptitle('Time Behavior of Sine Wave Sample')

    # Display plots
    plt.show()





def plot4(signal1, signal2, signal3, signal4, fsample, fcenter):
    """Plot two signals IQ constellation & time behavior

    @param signal1,2 -- complex sample lists
    @param signal3,4 -- complex sample lists
    @param fsample -- samplerate of sampled signals
    @param fcenter -- center frequency of sampled signals
    @return none
    """
    # Plot IQ constellation
    fig1, ax1 = plt.subplots(1, 1)
    ax1.hexbin(np.real(signal1), np.imag(signal1), bins='log', cmap='Blues')
    ax1.hexbin(np.real(signal2), np.imag(signal2), bins='log', cmap='Greens')
    ax1.set_title('IQ Constellation of Samples')
    ax1.axis('square')

    # Plot IQ signal time series
    dt = 1/fsample
    t1 = np.linspace(0, dt*(len(signal1)-1), num=len(signal1)) * (1e3)
    t2 = np.linspace(0, dt*(len(signal2)-1), num=len(signal2)) * (1e3)
    fig3, ax3 = plt.subplots(4, 1, sharex=True)

    ax3[0].plot(t1,np.real(signal1), label="Channel1")
    ax3[0].plot(t2,np.real(signal2), label="Channel2")
    ax3[0].grid(True)
    ax3[0].set_ylabel('Original I')
    ax3[0].legend()

    ax3[1].plot(t2,np.imag(signal1), label="Channel1")
    ax3[1].plot(t2,np.imag(signal2), label="Channel2")
    ax3[1].grid(True)
    ax3[1].set_ylabel('Original Q')
    ax3[1].legend()

    ax3[2].plot(t1,np.real(signal3), label="Channel1")
    ax3[2].plot(t2,np.real(signal4), label="Channel2")
    ax3[2].grid(True)
    ax3[2].set_ylabel('Adjusted I')
    ax3[2].legend()

    ax3[3].plot(t2,np.imag(signal3), label="Channel1")
    ax3[3].plot(t2,np.imag(signal4), label="Channel2")
    ax3[3].grid(True)
    ax3[3].set_ylabel('Adjusted Q')
    ax3[3].set_xlabel('Time [ms]')
    ax3[3].legend()

    fig3.suptitle('Time Behavior of Sine Wave Sample')

    # Display plots
    plt.show()





def plot_phase_shift(phase, fsample, fcenter):

    x = np.arange(0, 2e-9, fsample/100)
    A = [np.cos(2 * np.pi * t) for t in x]
    B = [np.cos(2 * np.pi * t + phase) for t in x]

    fig3, ax3 = plt.subplots(1, 1, sharex=True)

    ax3.plot(x,np.real(A), label="In Phase")
    ax3.plot(x,np.real(B), label="Out of Phase: " + str(phase))
    ax3.grid(True)
    ax3.set_ylabel('Simulated Phase Shift')
    ax3.legend()

    plt.show()




def get2ch(filename):
    """read csv file into 2 channels

    @param filename -- name of csv file
    @return 2 signal lists
    """
    signal1 = []
    signal2 = []

    with open(filename, "r") as csvfile:
        reader = csv.reader(csvfile)

        for line in reader:
            signal1.append(complex(int(line[0]), int(line[1])))
            signal2.append(complex(int(line[2]), int(line[3])))
    return signal1, signal2



if __name__ == "__main__":
    plt.style.use("flatirons.mplstyle")

    filename = "./sample_mgc.csv"
    fcenter = 1575.42e6
    fsample = 2.048e6
    signal_name = "sample"

    signal1, signal2 = get2ch(filename)
    pa.phaseCalculator(filename, fsample, fcenter)

    phase = pa.__phaseCalculate__(signal1, signal2, fsample, fcenter)
    plot_phase_shift(phase, fsample, fcenter)

    signal3, signal4 = pa.phaseAdjust(filename, fsample, fcenter)
    plot4(signal1, signal2, signal3, signal4, fsample, fcenter)
