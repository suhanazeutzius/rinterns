import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

import phaseCSV as CSV
import phasePlot as PLOT


def sampleDeltaCalculate(signal1, signal2, convolve=False):
    """calculates difference in samples between two signals

    @param signal1, signal2 -- complex sample signals
    @return sample difference between signals
    print("Phase offset (deg): " + str(delta_phase))

    @brief uses scipy signal cross correlation and finds
    the index where the max occurs with reference to the
    center of the correlation output
    """

    correlation = signal.correlate(signal1, signal2)
    t = np.arange(1-len(signal1), len(signal2))

    if(convolve):
        fig, ax = plt.subplots(2, 1, sharex=True)
        ax[0].plot(t, correlation, "b")

        win_size = 2048
        win = [1/win_size for _ in range(win_size)]
        avg_correlation = np.convolve(correlation, win, mode='same')

        ax[1].plot(t, avg_correlation, "r")
        plt.show()

    delta_sample = t[np.argmax(correlation)]
    return delta_sample




def sampleDeltaImpose(signal1, signal2, sampleoffset):
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
        signal1 = signal2[:(len(signal1) - sampleoffset)]
    else:
        signal1 = signal1[sampleoffset:]
        signal2 = signal2[:(len(signal2) - sampleoffset)]
    return signal1, signal2




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
        sampleoffset = sampleCalculate(signals[0], signals[i+1])
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
    signals[0], signals[1] = sampleDeltaImpose(signals[0], signals[1], samples[0])

    # write back to csv
#    writecsv(filename, signals)
    return signals
