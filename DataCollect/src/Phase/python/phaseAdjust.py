import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

import phaseCSV as CSV
import phasePlot as PLOT


def __sampleDeltaCalculate__(signal1, signal2):
    """calculates difference in samples between two signals

    @param signal1, signal2 -- complex sample signals
    @return sample difference between signals

    @brief uses scipy signal cross correlation and finds
    the index where the max occurs with reference to the
    center of the correlation output
    """

    correlation = signal.correlate(signal1, signal2)
    t = np.arange(1-len(signal1), len(signal2))
    delta_sample = t[np.argmax(correlation)]
    return delta_sample




def __sampleDeltaImpose__(signal1, signal2, sampleoffset):
    """Apply a sample offset to two signals

    @param signal1,2 -- singals to set offsets of
    @param sampleoffset -- integer offset bewteen signals in samples
    @return signal1, signal2 adjusted

    @brief Takes array slices (cuts off leading channel's first samples,
    cuts off the lagging channel's end samples; this reduces the size of
    both lists equally)
    """
    if(sampleoffset < 0):
        sampleoffset = np.abs(sampleoffset)
        signal2 = signal2[sampleoffset:]
        signal1 = singal2[:(len(signal1) - sampleoffset)]
    else:
        signal1 = signal1[sampleoffset:]
        signal2 = signal2[:(len(signal2) - sampleoffset)]
    return signal1, signal2



def __phaseCalculate__(signal1, signal2, fsample, fcenter):
    """Calculate phase bewteen two signals

    @param signal1 -- list of complex samples
    @param signal2 -- list of complex samples
    @param fsample -- sample rate of samples
    @param fcenter -- center frequency of samples
    @return phase difference in radians

    @brief Calculates sample difference, then converts a difference
    in sample numbers to a difference in time, then to a difference
    in phase (using sample rate and center frequency)
    """
    delta_t = __sampleDeltaCalculate__(signal1, signal2) / fsample
    delta_phase = np.rad2deg((delta_t * 2 * np.pi * fcenter) % 2*np.pi)
    return delta_phase




def __phaseImpose__(signals, phases):
    """Add phase shift to signals

    @param signal -- list of lists of complex samples
    @param phase -- list of radian phase shifts to impose
    @return signal1, signal2, signal3 -- adjusted list of complex samples

    @brief Multiplies each sample of each list by e^{j * phase}
    """
    s = []
    s.append(signals[0])
    for i in range(len(signals) - 1):
        s.append([sample * np.exp(1j * phases[i]) for sample in signals[i + 1]])
    return s




def phaseCalculator(filename, fsample, fcenter):
    """Calculate phases between channels

    @param filename -- csv file to get data from
    @param fsample -- sample rate of data
    @param fcenter -- center frequency of data
    @return list of calculated phases

    @brief read data from a csv file and calculate phases,
    storing in .phases file as well as returning a list
    of phases
    """

    # read csv data
    signals = CSV.readcsv(filename)

    # calculate phase differences & store
    phases = []
    fout = open("./.phases", "w")

    for i in range(len(signals) - 1):
        phase = __phaseCalculate__(signals[0], signals[i+1], fsample, fcenter)
        phases.append(phase)
        fout.write(str(phase) + "\n")

    fout.close()
    return phases




def sampleCalculator(filename):
    """Calculate sample offsets between channels

    @param filename -- csv file to get data from
    @return list of sample offsets

    @brief
    """
    # read csv data
    signals = CSV.readcsv(filename)

    # calculate phase differeence & store
    samples = []
    fout = open("./.samples", "w")

    for i in range(len(signals) - 1):
        sampleoffset = __sampleCalculate__(signals[0], signals[i+1])
        samples.append(sampleoffset)
        fout.write(str(sampleoffset) + "\n")

    fout.close()
    return samples




def sampleAdjust(filename):
    """Sample align a file

    @param filename -- csv file to adjust
    @return sample adjusted signals list

    @brief read data from a csv file and get samples from
    .samples, align the samples by offsets, then write back
    the data to the csv file (and return the list of lists)
    """

    # read csv data
    signals = CSV.readcsv(filename)

    # get phases
    fin = open("./.samples", "r")
    samples = [int(str_samples) for str_samples in fin.readlines()]
    fin.close()

    # impose sample offsest
    signals[0], signals[1] = __sampleDeltaImpose__(signals[0], signals[1], samples[0])

    # write back to csv
#    writecsv(filename, signals)
    return signals




def phaseAdjust(filename, fsample, fcenter):
    """Phase adjust a file

    @param filename -- csv file to adjust
    @param fsample -- sample rate of data
    @param fcenter -- center frequency of data
    @return phase adjusted signals list

    @brief read data from a csv file and get phases from
    .phases, impose those phases, then write back the phase
    adjusted data to the csv file (and returns list of lists)
    """

    # read csv data
    signals = CSV.readcsv(filename)

    # get phases
    fin = open("./.phases", "r")
    phases = [float(str_phase) for str_phase in fin.readlines()]
    fin.close()

    # impose phases
    signals = __phaseImpose__(signals, phases)

    # write back to csv
#    writecsv(filename, signals)

    return signals




### MAIN ###

if __name__ == '__main__':

    filename = "./test/sample5.csv"
    fs = 2.048e6
    fc = 1575.42e6

    signals = CSV.readcsv(filename)
    print(phaseCalculator(filename, fs, fc))

    PLOT.plot(fs, signals[0], signals[1])

    signals = phaseAdjust(filename, fs, fc)

    PLOT.plot(fs, signals[0], signals[1])
