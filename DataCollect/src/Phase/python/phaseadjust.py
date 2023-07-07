import numpy as np
from scipy import signal
import csv


def readcsv(filename):
    """read csv data into lists

    @param filename -- name of csv file to read
    @return list of lists of complex samples

    @brief determines how many channel lists to fill and
    returns parsed IQ data as complex floats
    """

    signal1 = []
    signal2 = []
    signal3 = []
    signal4 = []
    signals = [signal1, signal2, signal3, signal4]

    with open(filename, "r") as fin:

        # parse csv into lines, then further into values
        csvfile = csv.reader(fin)

        # check number of channels & append values to lists accordinly
        for line in csvfile:
            numch = len(line) // 2
            if(numch > 4):
                print("CSV Read Error: Too many channels")
                fin.close()
                return None

            j = 0
            while(j < len(line)-1):
                for i in range(numch):
                    signals[i].append(complex(float(line[j]), float(line[j+1])))
                    j+=2
    fin.close()

    # extract useful data
    for i in range(len(signals)):
        if len(signals[i]) <= 0:
            signals.pop(i)

    return signals





def writecsv(filename, signals):
    """write signals to csv

    @param filename -- name of csv file to write to
    @param signals -- list of signals to write
    @return none

    @brief TODO
    """

    # TODO: FUNCTION IS CURRENTY NON-FUNCTIONAL

    I = []
    Q = []

    for signal in signals:
        I.append([np.real(s) for s in signal])
        Q.append([np.imag(s) for s in signal])

    fout = open(filename, "w")
    csvwriter = csv.writer(fout)

    fout.close() 

    return





def __phasecalculate__(signal1, signal2, fsample, fcenter):
    """Calculate phase bewteen two signals

    @param signal1 -- list of complex samples
    @param signal2 -- list of complex samples
    @param fsample -- sample rate of samples
    @param fcenter -- center frequency of samples
    @return phase difference in radians

    @brief TODO
    """

    correlation = signal.correlate(signal1, signal2)
    t = np.arange(1-len(signal1), len(signal2))
    delta_sample = t[np.argmax(correlation)]
    delta_t = delta_samples / fsample
    delta_phase = 180 - np.rad2deg((delta_t * 2 * np.pi * fcenter) % 2*np.pi)

    return delta_phase





def __phaseimpose__(signals, phases):
    """Add phase shift to signals

    @param signal -- list of lists of complex samples
    @param phase -- list of radian phase shifts to impose
    @return signal1, signal2, signal3 -- adjusted list of complex samples

    @brief Multiplies each sample of each list by e^{-j * phase}
    """
    s = []
    for i in range(len(signals)):
        s.append([sample * np.exp(-1j * phases[i]) for sample in signals[i]])
    return s





def phasecalculator(filename, fsample, fcenter):
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
    signals = readcsv(filename)

    # calculate phase differences & store
    phases = []
    fout = fopen(WORKING_DIR + "/.phases", "w")

    for i in range(len(signals) - 1):
        phase = __phasecalculate__(signals[0], signals[i+1], fsample, fcenter)
        phases.append(phase)
        fout.write(str(phase) + "\n")

    fout.close()
    return phases





def phaseadjust(filename, fsample, fcenter):
    """Phase adjust a file

    @param filename -- csv file to adjust
    @param fsample -- sample rate of data
    @param fcenter -- center frequency of data
    @return none

    @brief read data from a csv file and get phases from
    .phases, impose those phases, then write back the phase
    adjusted data to the csv file
    """

    # read csv data
    signals = readcsv(filename)

    # get phases
    fin = fopen(WORKING_DIR + "/.phases", "r")
    phases = [float(str_phase) for str_phase in fin.readlines()]
    fin.close()

    # impose phases
    signals = __phaseimpose__(signals, phases)

    # write back to csv
    writecsv(filename, signals)

    return
