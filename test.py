# Import required python packages
import numpy as np
import math
import matplotlib.pyplot as plt
import scipy.signal

# Import custom python packages
from flatirons.gps_gen import *
from flatirons.gps_dsp import *
from flatirons.parse import *

# Import custom matplotlib styling
plt.style.use('flatirons/flatirons.mplstyle')

# Create clean simulated GPS signal2
fsample = 2*(1.023e6) # [Hz]
sig13 = makeGPSClean(13, num_periods=2, sample_rate=fsample)
sig8 = makeGPSClean(8, num_periods=2, sample_rate=fsample)

# Add noise to signal 13
noise_power_AWGN_dB = 16
noise_power_AWGN = math.pow(10,(noise_power_AWGN_dB/10))
sig13_noisy = makeGPSNoisy(sig13, noise_power_AWGN)

corr_same = scipy.signal.correlate(sig13, sig13_noisy)
corr_diff = scipy.signal.correlate(sig8, sig13_noisy)
max_shift = int((len(sig13)+len(sig8)-2)/2)
shift = np.arange(-max_shift,max_shift+1)
fig1, ax1 = plt.subplots()
ax1.plot(shift,corr_same)
ax1.plot(shift,corr_diff)
ax1.grid(True)
ax1.set_ylabel('Correlation Coefficient')
ax1.set_title('Autocorrelation and Crosscorrelation of Noisy C/A Code')
ax1.set_xlabel('Shift')
ax1.legend(['PRN 13', 'PRN 8'])
ax1.set_ylim([-1000, 5000])

max_corr = []
tmp = []
for i in np.arange(len(sig13_noisy)):
    corr = scipy.signal.correlate(sig13, np.roll(sig13_noisy, i))
    tmp.append(scipy.signal.correlate(sig8, np.roll(sig13_noisy, i)).max())
    max_corr.append(corr.max())
delay = (np.arange(len(sig13_noisy))/fsample)*(1e6)
fig2, ax2 = plt.subplots()
ax2.plot(delay,max_corr)
ax2.plot(delay, tmp)
ax2.legend(['PRN 13', 'PRN 8'])
ax2.set_xlabel('Time Delay [us]')
ax2.set_ylabel('Maximum Correlation Coefficient')
ax2.set_title('Time Delay Versus Maximum Correlation Coefficients')
ax2.set_ylim([-1000, 5000])
ax2.grid(True)

plt.show()
