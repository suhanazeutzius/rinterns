# Import required python packages
from skyfield.api import load, wgs84, EarthSatellite
import numpy as np
import matplotlib.pyplot as plt

# Import custom python packages
from flatirons.orbits_error import *

# Load mplystyle file
plt.style.use('flatirons/flatirons.mplstyle')

#stations_url = 'http://celestrak.org/NORAD/elements/gp.php?GROUP=gps-ops&FORMAT=tle'
#satellites = load.tle_file(url=stations_url, filename='tle-gps.txt', reload=True)
gps_file = 'tle-gps.txt'
ts = load.timescale()
#t = ts.utc(2023, 7, 6, 10, 20, 0)
t = ts.now()
print(t.utc_datetime())

get_overhead_satellites(t, gps_file, 26.2, [+39.58709, -104.82873], debug=True)
