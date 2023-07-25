import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
from scipy import signal, fftpack
from monopulse_data_prep import *
import math
from scipy.stats import norm
# Import custom python packages
from flatirons.gps_gen import *
from flatirons.gps_dsp import *
from flatirons.parse import *

# Use custom matplotlib styling
plt.style.use('flatirons/flatirons.mplstyle')


elevation_differences = [-5, 1, -1,
                         6,
                         19, 13, -1, -5, -6, 8, 14, 4, 1,
                         3, 2, 2, 4, 3, 1, 1, 0, 6,
                         0, 3, -1, -4, -4, -2, -4, 2, 3,
                         4, 0, -1, -1, 2, 0, 0, 5, 3]
azimuth_differences = [-12, -20, 26,
                       6,
                       -8, -4, 12, 0, -14, -24, -20, -12, -18,
                       -23, -12, -2, 11, -14, -20, -12, -3, 20,
                       5, -12, -7, -16, -8, -8, -8, -16, -20,
                       -2, -2, 4, -2, -14, 7, 21, 32, 3]

elev_stddev = np.std(elevation_differences)
azim_stddev = np.std(azimuth_differences)

print("elevation standard deviation: " + str(elev_stddev))
print("azimuth standard deviation: " + str(azim_stddev))
elev_mean, elev_std = norm.fit(elevation_differences)

fig, ax = plt.subplots(2)
ax[0].set_title("Elevation Angle")
ax[0].set_xlabel("Difference Between Calculated and True Value (degrees)")
ax[0].hist(elevation_differences, range=[-4*elev_stddev, 4*elev_std], bins=16)
# xmin = -15
# xmax = 15
# x = np.linspace(xmin, xmax, 100)
# ax[0].plot(x, p, 'k', linewidth=2)
ax[1].set_title("Azimuth Angle")
ax[1].set_xlabel("Difference Between Calculated and True Value (degrees)")
ax[1].hist(azimuth_differences, range=[-4*azim_stddev, 4*azim_stddev], bins=16)
plt.tight_layout()
plt.show()

