# Import required python packages
from skyfield.api import load, wgs84, EarthSatellite
import numpy as np
import matplotlib.pyplot as plt

# Import custom python packages
from flatirons.orbits_error import *

# Load mplystyle file
plt.style.use('flatirons/flatirons.mplstyle')

# Specify name of TLE file
gps_file = 'tle-gps.txt'

# Define time
ts = load.timescale()
t = ts.utc(2023, 7, 12, 15, 20, 0) # Set a specific time
# t = ts.now()                       # Grab current time

# Display satellites that are currently overhead receiver
_ = getOverheadSatellites(t, gps_file, 26.2, [+39.58709, -104.82873])

# Define satellite direction estimates
#   Format: PRN: [azimuth, elevation]
estimates = {11: [45,10], 12: [237, 5]}

# Calculate errors
errors = calcError(t, gps_file, 26.2, [+39.58709, -104.82873], estimates)

# Display error information
for prn in errors.keys():
    print("PRN " + str(prn) + ":")
    print(" Azimuth Error [deg]   : " + str(errors[prn][0]))
    print(" Elevation Error [deg] : " + str(errors[prn][2]))
    print(" Range Error [km]      : " + str(errors[prn][3]))
    print(" Position Error [km]   : " + str(errors[prn][3]))
