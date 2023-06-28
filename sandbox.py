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

fcenter_SDR = 1573.42e6
fsample = 30.69e6
fGPS = 1575.42e6

I, Q = dat_parse('data/Samples_Jun_28/Data11.dat', 306900)
signal = I + 1j*Q
#visualizeGPS(signal, fcenter_SDR, fsample, 'Signal 1')

#signal = filterSignal((fGPS-fcenter_SDR), fsample, signal, ['fir', 'bandpass'], bandwidth=2e6, order=100)
#visualizeGPS(signal, fcenter_SDR, fsample, 'Signal 1')

#signal = tuneSignal(fGPS-fcenter_SDR, fsample, signal)
#visualizeGPS(signal, fGPS, fsample, 'Signal 1')

signal = scipy.signal.decimate(signal, 10)

prns = [8,10,15,18,23,24,27,32]
[corr0, corr1] = correlateSignal(signal, 3.069e6, 'Signal 1', np.deg2rad(26.3), 100, prns=prns, plot=False)
