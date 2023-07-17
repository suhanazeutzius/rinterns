# Import required python packages
from skyfield.api import load, wgs84, EarthSatellite
import numpy as np
import matplotlib.pyplot as plt

# Load mplstyle file
plt.style.use('flatirons/flatirons.mplstyle')

# getOverheadSatellites() displays the GPS satellites currently overhead of the receiver
#
# Inputs:
#   t               : time in UTC                                                             [Time]
#   tle_file        : text file storing TLE data                                            [string]
#   field_of_view   : field of view of receiver in degrees                                   [float]
#   receiver_latlon : list containing lattitude and longitude of receiver            [list of float]
#                        Element 0 --> lattitude
#                        Element 1 --> Longitude
#   debug           : optional flag controlling whether to print debug info                    [T/F]
#   show_plot       : optional flag controlling whether to display plot                        [T/F]
#
# Outputs:
#   prn_dict        : dictionary of GPS satellites               [dictionary of type EarthSatellite]
#   [fig, ax]       : figure and axes objects for plot
def getOverheadSatellites(t, tle_file, field_of_view, receiver_latlon, debug=False, show_plot=True):
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
                ax.annotate(prn, (np.deg2rad(az.degrees), el), fontweight='bold', zorder=2)
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
    ax.set_title('Overhead Satellites')
    fig.savefig('overhead_satellites.png')
    if show_plot:
        plt.show()

    # Return dictionary of satellite objects
    return prn_dict, [fig, ax]

# calcError() calculates the error between truth data and measured data
#
# Inputs:   
#   t                   : time in UTC                                                         [Time]
#   tle_file            : text file storing TLE data                                        [string]
#   field_of_view       : field of view of receiver in degrees                               [float]
#   receiver_latlon     : list containing lattitude and longitude of receiver        [list of float]
#                         Element 0 --> lattitude
#                         Element 1 --> longitude
#   direction_estimates : dictionary storing estimate information. The key is the PRN         [dict]
#                         and the entry is an array with the following elements:
#                         Element 0 --> estimated azimuth in degrees
#                         Element 1 --> estiamted elevation in degrees
#   debug               : optional flag controlling whether to print debug info                [T/F]
#   show_plot           : optional flag controlling whether to display plot                    [T/F]
#
# Outputs:
#   errors              : dictionary storing error information. The key is the PRN            [dict]
#                         and the entry is an array with the following elements:
#                         Element 0 --> azimuth error in degrees
#                         Element 1 --> elevation error in degrees
#                         Element 2 --> range error in km
#                         Element 3 --> position error in km
def calcError(t, tle_file, field_of_view, receiver_latlon, direction_estimates, debug=False, show_plot=True):
    # Define average GPS altitutde
    hGPS = 20200 # [km]

    # Get orbit positions of overhead satellites
    prn_dict, [fig, ax] = getOverheadSatellites(t, tle_file, field_of_view, receiver_latlon, debug=debug, show_plot=False)
    plt.cla()

    # Create array to store errors
    errors = np.zeros((len(direction_estimates.keys()),5))

    # Iterate over all PRNs in direction_estimates
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    color_idx = 0
    for i, prn in enumerate(direction_estimates.keys()):
        # Extract estimate corresponding to current PRN
        estimate = direction_estimates[prn]
        
        # Extract truth data corresponding to current PRN
        receiver = wgs84.latlon(receiver_latlon[0], receiver_latlon[1])
        sat_range = prn_dict[prn] - receiver
        alt, az, distance = sat_range.at(t).altaz()
        el = 90-alt.degrees

        # Calculate errors
        errors[i,0] = prn
        errors[i,1] = az.degrees-estimate[0] # [deg]
        errors[i,2] = el-estimate[1] # [deg]
        errors[i,3] = distance.km-hGPS # [km]
        pos_true = [hGPS*np.sin(np.deg2rad(el))*np.cos(np.deg2rad(360-az.degrees)),hGPS*np.sin(np.deg2rad(el))*np.sin(np.deg2rad(360-az.degrees)),hGPS*np.cos(np.deg2rad(el))]
        pos_estimate = [hGPS*np.sin(np.deg2rad(estimate[1]))*np.cos(np.deg2rad(360-estimate[0])),hGPS*np.sin(np.deg2rad(estimate[1]))*np.sin(np.deg2rad(360-estimate[0])),hGPS*np.cos(np.deg2rad(estimate[1]))]
        errors[i,4] = np.linalg.norm(np.array(pos_true)-np.array(pos_estimate))

        # Plot estimated satellite position
        ax.scatter(np.deg2rad(az.degrees), el, color=colors[color_idx], zorder=2)
        ax.annotate(prn, (np.deg2rad(az.degrees), el), fontweight='bold', zorder=2)
        ax.scatter(np.deg2rad(estimate[0]), estimate[1], marker='X', color=colors[color_idx], zorder=2)
        ax.annotate(prn, (np.deg2rad(estimate[0]), estimate[1]), fontweight='bold', zorder=2)
        color_idx += 1
    
    # Make plot look nice
    ax.set_yticklabels([])
    ax.set_xticklabels(['N','45°','E','135°','S','225°','W','315°'])
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_rmax(field_of_view)
    ax.legend(['True Position', 'Estimated Position'])
    ax.set_title('Comparison of Estimated and True Satellite Positions')
    fig.savefig('satellite_estimates.png')
    if show_plot:
        plt.show()
        
    # Return results
    results = {int(errors[i,0]): errors[i,1:] for i in np.arange(errors.shape[0])}
    return results
