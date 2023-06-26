import numpy as np
import struct   

# csv_parse() extracts the IQ data from a .csv data file
#
# Inputs:
#   csv_file : filepath for data file                                                [.csv]
#
# Outputs: IQ data for up to two signals (I1,Q1) and (I2,Q2)     [numpy arrays of type int]
def csv_parse(csv_file):
    """
    Parses a sample csv file into IQ arrays
    """

    with open(csv_file, "r") as fs:
        lines = fs.readlines()

        I1 = []
        I2 = []
        Q1 = []
        Q2 = []

        for line in lines: 
            chunks = line.split(", ")
            chunks[-1] = chunks[-1].replace("\n", "")

            if(len(chunks) == 2):
               I1.append(int(chunks[0]))
               Q1.append(int(chunks[1]))
            elif(len(chunks) == 4):
                I1.append(int(chunks[0]))
                Q1.append(int(chunks[1]))
                I2.append(int(chunks[2]))
                Q2.append(int(chunks[3]))

        if(len(I2) < len(lines)/3):
            return np.array(I1), np.array(Q1)
        else:
            return np.array(I1),np.array(Q1),np.array(I2),np.array(Q2)

# dat_parse() extracts the IQ data from a .dat file
#
# Inputs:
#   dat_file : filepath for data file
#
# Outputs: IQ data for signal (I,Q)                              [numpy arrays of type int]
def dat_parse(dat_file, num_samples):
    with open(dat_file, mode="rb") as fs:
        data = fs.read()
        I = [int.from_bytes(data[i:i+2], byteorder='little', signed=True) for i in range(0, len(data), 4)]
        Q = [int.from_bytes(data[i+2:i+4], byteorder='little', signed=True) for i in range(0, len(data), 4)]
        return np.array(I), np.array(Q)
