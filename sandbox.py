# Import required python packages
import numpy as np
import math
import matplotlib.pyplot as plt
import scipy.signal

# Import custom python packages
from flatirons.gps_gen import *
from flatirons.gps_dsp import *
from flatirons.parse import *

# Use custom matplotlib styling
plt.style.use('flatirons/flatirons.mplstyle')

#signal = makeGPSClean(13, 0, 30)
##visualizeGPS(signal, 0, 1.023e6, 'Signal 1')
#
#noise_power_AWGN_dB = 16
#noise_power_AWGN = math.pow(10,(noise_power_AWGN_dB/10))
#
##signal = makeGPSNoisy(signal, noise_power_AWGN)
##visualizeGPS(signal, 0, 1.023e6, 'Simulated GPS Signal')

fcenter_SDR = 1567.42e6
fsample = 30.72e6
fGPS = 1575.42e6

I, Q = csv_parse('data/Samples_Jun_23/sample_1567.42M_307200_Wed_21_Jun_2023_11_19_52_AM_UTC.csv')
#I, Q = csv_parse('data/Samples_Jun_22/sample_1575.418M_10ms_2.csv')
signal = I + 1j*Q
#visualizeGPS(signal, fcenter_SDR, fsample, 'Signal 1')

#signal = filterSignal((fGPS-fcenter_SDR), fsample, signal, ['fir', 'bandpass'], bandwidth=2e6, order=100)
#visualizeGPS(signal, fcenter_SDR, fsample, 'Signal 1')

signal = tuneSignal(fcenter_SDR, fsample, signal)
#visualizeGPS(signal, fGPS, fsample, 'Signal 1')

signal = scipy.signal.decimate(signal, 30)

prns = range(1,32)
[corr0, corr1] = correlateSignal(signal, fsample, 'Signal 1', prns=prns, plot=True)
