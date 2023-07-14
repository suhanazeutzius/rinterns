import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
from scipy import signal

import phaseCSV as CSV
import phasePlot as PLOT
import sampleAdjust as SA


def sampleDeltaCalculate(signal1, signal2):
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




def phaseCalculate(signal1, signal2, fsample, fcenter):
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
    delta_t = sampleDeltaCalculate(signal1, signal2) / fsample
    delta_phase = np.rad2deg((delta_t * 2 * np.pi * fcenter) % 2*np.pi)
    return delta_phase




def phaseImpose(signals, phases):
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




def phaseCalculator(filename, fsample, fcenter, write=False):
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

    if(write):
        fout = open("./.phases", "w")

    for i in range(len(signals) - 1):
        phase = phaseCalculate(signals[0], signals[i+1], fsample, fcenter)
        phases.append(phase)
        if(write):
            fout.write(str(phase) + "\n")

    if(write):
        fout.close()

    return phases




def phaseCalculatorAverage(filenames, fsample, fcenter):
    """calculate phase difference average over multiple 2-channel samples

    @param filenames -- list of filenames to get phase diffs from
    @fsample -- samplerate of samples in files
    @fcenter -- tuning frequency of samples in files
    @return average phase across all files/channels
    """
    phases = []
    for file in filenames:

        # read csv data
        signals = CSV.readcsv(filename)

        # calculate phase differences & store
        phase = phaseCalculate(signals[0], signals[1], fsample, fcenter)
        phases.append(phase)

    return np.mean(phases)




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
    signals = phaseImpose(signals, phases)

    # write back to csv
#    writecsv(filename, signals)

    return signals




def printDeltas(signals, fs, fc):
    """Print sample and time deltas for a given 2 channel sample csv

    @param signals -- list of lists of complex samples
    @param fs -- sample rate of sample
    @return none
    """
    # calculate signal sample offsets
    delta_sample = sampleDeltaCalculate(signals[0], signals[1])
    delta_t = delta_sample/fs
    delta_phase = np.rad2deg(2 * np.pi * delta_t * fc)
    print("Sample offset: " + str(delta_sample))
    print("Time offsest (us): " + str(delta_t*1e6))
    print("Phase offset (deg): " + str(delta_phase))

    # sample shift and re-calculate sample offsets
    signals = SA.sampleDeltaImpose(signals[0], signals[1], delta_sample)
    delta_sample = sampleDeltaCalculate(signals[0], signals[1])
    delta_t = delta_sample/fs
    delta_phase = np.rad2deg(2 * np.pi * delta_t * fc)
    print("Sample offset: " + str(delta_sample))
    print("Time offsest (us): " + str(delta_t*1e6))
    print("Phase offset (deg): " + str(delta_phase))




### MAIN PROGRAMS ###


def nonSplitMultiSample():

    # inputs
    filename = "./test/samples/channeltest.csv"
    fs = 20.48e6
    fc = 1575.42e6

    signals = CSV.readcsv(filename)
    PLOT.plot(fs, signals[0], signals[1], name="Pre-Adjustment")
    printDeltas(signals, fs, fc)
    signals = PLOT.correlationPlot(signals, fs, fc)
    PLOT.plot(fs, signals[0], signals[1], name="Post-Adjustment")

    filename = "./test/samples/3_23_channeltest.csv"
    signals = CSV.readcsv(filename)
    PLOT.plot(fs, signals[0], signals[1], name="Pre-Adjustment")
    printDeltas(signals, fs, fc)
    signals = PLOT.correlationPlot(signals, fs, fc) 
    PLOT.plot(fs, signals[0], signals[1], name="Post-Adjustment")

    filename = "./test/samples/3_25_channeltest.csv"
    signals = CSV.readcsv(filename)
    PLOT.plot(fs, signals[0], signals[1], name="Pre-Adjustment")
    printDeltas(signals, fs, fc)
    signals = PLOT.correlationPlot(signals, fs, fc)
    PLOT.plot(fs, signals[0], signals[1], name="Post-Adjustment")




def splitSingleSample(plot=False):

    filename = "./test/samples/3_23_channeltest.csv"
    fs = 20.48e6
    fc = 1575.42e6

    rawsignals = CSV.readcsv(filename)
    splitsignals = CSV.splitSignals(rawsignals, 10)
    for signals in splitsignals:
        if(plot):
            PLOT.plot(fs, signals[0], signals[1], name="Pre-Adjustment")
            signals = PLOT.correlationPlot(signals, fs, fc, name="Pre-Adjustment")
        else:
            delta_sample = SA.sampleDeltaCalculate(signals[0], signals[1])
            signals = SA.sampleDeltaImpose(signals[0], signals[1], delta_sample)
        printDeltas(signals, fs, fc)
        if(plot):
            PLOT.plot(fs, signals[0], signals[1], name="Post-Adjustment")



if __name__ == '__main__':
    nonSplitMultiSample()