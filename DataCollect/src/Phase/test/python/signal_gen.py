import numpy as np
import matplotlib.pyplot as plt

def phaseShift(signal, phi):
    signal = [sample * np.exp(-1j * phi) for sample in signal]
    return signal

### MAIN PROGRAM ###

fcenter = 1575.42e6
fsample = 2.048e6
tsample = 0.01

phi1 = np.deg2rad(15)
phi2 = np.deg2rad(30)
phi3 = np.deg2rad(45)

samples = np.arange(0, tsample, 1/fsample)

signal1 = [(np.exp(1j * 2 * np.pi * fcenter * t) + np.exp(-1j * 2 * np.pi * fcenter * t))/2 for t in samples]
signal2 = phaseShift(signal1, phi1)
signal3 = phaseShift(signal1, phi2)
signal4 = phaseShift(signal1, phi3)

fout = open("signal.csv", "w")

i = 0
while(i < len(signal1)-1):
    fout.write(str(np.real(signal1[i])) + ", " + str(np.imag(signal1[i+1])) + ", ")
    fout.write(str(np.real(signal2[i])) + ", " + str(np.imag(signal2[i+1])) + ", ")
    fout.write(str(np.real(signal3[i])) + ", " + str(np.imag(signal3[i+1])) + ", ")
    fout.write(str(np.real(signal4[i])) + ", " + str(np.imag(signal4[i+1])) + "\n")
    i+=2

fout.close()
