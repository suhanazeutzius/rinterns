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
    signals = []
    signals.append(signal1) 
    signals.append(signal2) 
    signals.append(signal3) 
    signals.append(signal4) 

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

    # extract real data
    i = 0
    while (i < len(signals)):
        if (len(signals[i]) <= 0):
            signals.pop(i)
            i-=1
        i+=1

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




def splitSignals(signals, n):
    """splits all lists of signals into n new signals

    @param signals -- signals to split
    @param n -- number of output signals per input signal
    @return new list of signals

    @brief TODO
    """

    # TODO
    return None
