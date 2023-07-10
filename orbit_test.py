# Import required python packages
from skyfield.api import load, wgs84
import numpy as np
import matplotlib.pyplot as plt

stations_url = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=gps-ops&FORMAT=tle'
satellites = load.tle_file(stations_url)
gps_prns = {int(sat.name[-3:-1]): sat for sat in satellites}
print('Loaded', len(satellites), 'satellites:')
for prn in gps_prns.keys():
    print("PRN " + str(prn))

receiver = wgs84.latlon(+39.58709, -104.82873)
    
ts = load.timescale()
t = ts.utc(2023, 7, 10, 20, 5, 30)

fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
for prn in range(33):
    if prn in gps_prns.keys():
        sat = gps_prns[prn]
        sat_range = sat - receiver
    
        alt, az, distance = sat_range.at(t).altaz()
        el = 90-alt.degrees
        if el  <= 26.2:
            ax.scatter(az.degrees, el)
        else:
            ax.scatter(az.degrees, el, color='#808080')

theta = np.linspace(0,360,num=1000)
r = 26.2*np.ones(1000)

ax.plot(theta,r)
ax.set_rmax(90)
plt.show()
