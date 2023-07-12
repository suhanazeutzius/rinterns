# Import required python packages
from skyfield.api import load, wgs84, EarthSatellite
import numpy as np
import matplotlib.pyplot as plt

# Load mplstyle file
plt.style.use('flatirons/flatirons.mplstyle')

def get_overhead_satellites(t, tle_file, field_of_view, receiver_latlon, debug=False):
    # Load satellite ephemeris data from TLE file
    satellites = load.tle_file(tle_file)

    # Create dictionary of GPS PRNs
    prn_dict = {int(sat.name[-3:-1]): sat for sat in satellites}

    if debug:
        # Display which satellites were loaded
        print("Loaded", len(satellites), "satellites:")
        for prn in prn_dict.keys():
            print("PRN " + str(prn) + " | days away from epoch: " + str(t-prn_dict[prn].epoch))

    # Create object to store receiver position
    receiver = wgs84.latlon(receiver_latlon[0], receiver_latlon[1])

    # Iterate over all satellites
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    for prn in range(33):
        if prn in prn_dict.keys():
            # Extract satellite object corresponding to current prn
            sat = prn_dict[prn]
            
            # Calculate distance between satellite and reciever
            sat_range = sat - receiver

            # Calculate elevation, azimuth, and distance to satellite
            alt, az, distance = sat_range.at(t).altaz()
            el = 90-alt.degrees

            # Plot satellite
            if el <= field_of_view:
                ax.scatter(np.deg2rad(az.degrees), el, color='#DBB40C', zorder=2)
                ax.annotate(prn, (np.deg2rad(az.degrees), el+3), color='#DBB40C', fontweight='bold', zorder=2)
            else:
                ax.scatter(np.deg2rad(az.degrees), el, color='#C0C0C0')

    # Plot FOV
    theta = np.linspace(0, 2*np.pi, num=1000)
    r = field_of_view*np.ones(1000)
    ax.plot(theta, r, zorder=1)

    # Make plot look nice
    ax.set_yticklabels([])
    ax.set_xticklabels(['N','45°','E','135°','S','225°','W','315°'])
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_rmax(90)
    plt.show()
