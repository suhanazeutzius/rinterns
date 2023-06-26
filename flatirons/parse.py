import numpy as np

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
