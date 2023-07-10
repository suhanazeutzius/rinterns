import numpy as np

import sys; sys.path.append("../")
from phaseAdjust import *
from phasePlot import *
from gps_gen import *


def phaseShift(signal, phi):
    """shift a signal by a phase

    @param signal -- complex signal list
    @param phi -- phase in radians to shift
    @return shifted signal
    """
    return [x * np.exp(1j * phi) for x in signal]


def main():
    signal = makeGPSNoisy(makeGPSClean(13), 1)
    shiftedSignal = phaseShift(signal, np.deg2rad(90))
    plot(1.023e6, signal, shiftedSignal)


if __name__ == "__main__":
    main()
