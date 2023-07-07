import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import csv


def plot(signal1, signal2, fsample, fcenter):
    """Plot two signals in IQ and time

    @param signal1,2 -- complex sample lists
    @param fsample -- samplerate of sampled signals
    @param fcenter -- center frequency of sampled signals
    @return none
    """
    # Plot IQ constellation
    fig1, ax1 = plt.subplots()
    ax1.hexbin(np.real(signal1), np.imag(signal1), bins='log', cmap='blues')
    ax1.hexbin(np.real(signal2), np.imag(signal2), bins='log', cmap='greens')
    ax1.set_title('IQ Constellation of Sample')
    ax1.axis('square')

    # Plot IQ signal time series
    dt = 1/fsample
    t1 = np.linspace(0, dt*(len(signal1)-1), num=len(signal1)) * (1e3)
    t2 = np.linspace(0, dt*(len(signal2)-1), num=len(signal2)) * (1e3)
    fig3, ax3 = plt.subplots(3, 1, sharex=False)
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




plt.style.use("flatirons.mplstyle")

filename = ""
fcenter = 1575.42e6
fsample = 2.048e6
signal_name = "sample"

signal1, signal2 = get2ch(filename)
plot(signal1, signal2, fsample, fcenter)
