import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import csv

def plot(signal1, signal2, fsample, fcenter):

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

    x = np.arange(0, 2e-9, 2e-9/100)
    A = [np.cos(2 * np.pi * fcenter * t) for t in x]
    B = [np.cos(2 * np.pi * fcenter * t + np.deg2rad(24)) for t in x]

    ax3[2].plot(x, A, label="In Phase")
    ax3[2].plot(x, B, label="24 Degree Out of Phase")
    ax3[2].grid(True)
    ax3[2].sest_ylabel('Simulated Cosine Waves')
    ax3[2].set_xlabel('Time [s]')
    ax3[2].legend()

#    ax3[0].set_xlim([0, 2e-9])


    fig3.suptitle('Time Behavior of Sine Wave Sample')

    # Display plots
    plt.show()


fcenter = 1575.42e6
fsample = 2.048e6
signal_name = "sample"

signal1 = []
signal2 = []

with open("/home/ngolding/Project/rinterns/DataCollect/src/Phase/test/python/sample2.csv", "r") as csvfile:
    reader = csv.reader(csvfile)

    for line in reader:
        signal1.append(complex(int(line[0]), int(line[1])))
        signal2.append(complex(int(line[2]), int(line[3])))

corr = signal.correlate(signal1, signal2)
t = np.arange(1-len(signal1), len(signal2))
delta_samples = t[np.argmax(corr)]
delta_t = delta_samples/fsample
delta_phase = 180 - np.rad2deg((delta_t * 2 * np.pi * fcenter) % 2*np.pi)

print(delta_phase)


plot(signal1, signal2, fsample, fcenter)
