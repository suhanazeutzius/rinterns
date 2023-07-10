import numpy as np

from phaseAdjust import *
from phasePlot import *
from gps_gen import *
from phaseCSV import *

import subprocess


def phaseShift(signal, phi):
    """shift a signal by a phase

    @param signal -- complex signal list
    @param phi -- phase in radians to shift
    @return shifted signal
    """
    return [x * np.exp(1j * phi) for x in signal]



def normalizeSamples(signals):
    """normalize magnitudes of complex signals

    @param signals -- list of signals
    @note ***only works for 2 channels currently***
    """
    I1 = [np.real(x) for x in signals[0]]
    Q1 = [np.imag(x) for x in signals[0]]
    I2 = [np.real(x) for x in signals[1]]
    Q2 = [np.imag(x) for x in signals[1]]

    norm = max(np.max(I1), np.max(Q1), np.max(I2), np.max(Q2))

    signals[0] = [x/norm for x in signals[0]]
    signals[1] = [x/norm for x in signals[1]]
    return signals



def averagePS(n):
    phases = []
    for _ in range(n):
        subprocess.run(["bladeRF-cli", "-s", "./test/samples/sample.sh"])
        phase = phaseCalculator("./bpsk_sample.csv", 20.48e6, 1575.42e6)[0]
        print(phase)
        phases.append(phase)

        signals = readcsv("./bpsk_sample.csv")
        signals = normalizeSamples(signals)
        plot(20.48e6, signals[0], signals[1])

        subprocess.run(["rm", "bpsk_sample.csv"])

    x = np.arange(0, len(phases), 1)

    figure, ax = plt.subplots(1, 1)
    plt.style.use(os.getcwd() + "/flatirons.mplstyle")
    ax.plot(x, phases)
    ax.set_xlabel("Data Collection Number")
    ax.set_ylabel("Phase Offset (degrees)")
    ax.set_title("Phase Offset Between Two Channels")
    plt.show()
    return np.median(phases)




def main():
    signals = readcsv("./bpsk_sample.csv")
    sampleDeltaCalculate(signals[0], signals[1]) 

#    print(averagePS(100))


if __name__ == "__main__":
    main()
