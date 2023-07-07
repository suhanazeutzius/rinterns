# Import required python packages
from skyfield.api import load, wgs84

stations_url = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=gps-ops&FORMAT=tle'
satellites = load.tle_file(stations_url)
print('Loaded', len(satellites), 'satellites')

gps_prns = {int(sat.name[-3:-1]): sat for sat in satellites}

for i in range(23,32):
    print(i == int(gps_prns[i].name[-3:-1]))
