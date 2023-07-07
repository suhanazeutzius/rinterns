import matplotlib.pyplot as plt
import numpy as np


def plot(fsample, signal1, signal2, signal3=None, signal4=None):
    """Plot two (to four) signals IQ constellation & time behavior

    @param signal1,2,3,4 -- complex sample lists (at least 1 and 2 are required)
    @param fsample -- samplerate of sampled signals
    @return none
    """
    plt.style.use("flatirons.mplstyle")

    # Plot IQ constellations
    fig1, ax1 = plt.subplots()
    ax1.hexbin(np.real(signal1), np.imag(signal1), bins='log', cmap='Blues')
    ax1.hexbin(np.real(signal2), np.imag(signal2), bins='log', cmap='Greens')
    if(signal3):
        ax1.hexbin(np.real(signal3), np.imag(signal3), bins='log', cmap='Reds')
    if(signal4):
        ax1.hexbin(np.real(signal4), np.imag(signal3), bins='log', cmap='Greys')
    ax1.set_title('IQ Constellation of Sample')
    ax1.axis('square')


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
