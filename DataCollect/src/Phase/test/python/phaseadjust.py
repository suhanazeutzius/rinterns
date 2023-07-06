import numpy as np
import csv

def readcsv(filename):
    """read csv data into lists

    @param filename -- name of csv file to read
    @return list of 4 complex lists

    @brief automatically determines how many lists to fill
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
    return signals




def writecsv(filename, signals):
    """write signals to csv

    @param filename -- name of csv file to write to
    @param signals -- list of signals to write
    @return none

    @brief
    """
    fout = open(filename, "w")

    fclose()

    return





def phasecalculator(signal1, signal2):
    """Calculate phase bewteen two signals

    @param signal1 -- list of complex samples
    @param signal2 -- list of complex samples
    @return phase difference in radians

    @brief TODO
    """
    # TODO
    return None





def phaseimposer(signal1, signal2, signal3, phase1, phase2, phase3):
    """Add phase shift to signals

    @param signal1,2,3 -- list of complex samples
    @param phase1,2,3 -- radian phase shift to impose
    @return signal1, signal2, signal3 -- adjusted list of complex samples

    @brief Multiplies each sample of the list by e^{-j * phase}
    """
    signal1 = [s * np.exp(-1j * phase1) for x in signal1]
    signal2 = [s * np.exp(-1j * phase2) for x in signal2]
    signal3 = [s * np.exp(-1j * phase3) for x in signal3]
    return signal1, signal2, signal3




sigs = readcsv("signal.csv")
writecsv("signalout.csv", sigs)
