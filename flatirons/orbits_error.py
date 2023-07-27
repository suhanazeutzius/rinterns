# Import required python packages
from skyfield.api import load, wgs84, EarthSatellite
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mpl_dates
from datetime import datetime
import time

# Import custom packages
from monopulse_data_prep import *
from lookup_table import *

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
#   do_plot         : optional flag controlling whether to generate plots                      [T/F]
#
# Outputs:
#   prn_dict        : dictionary of GPS satellites               [dictionary of type EarthSatellite]
#   [fig, ax]       : figure and axes objects for plot (only returned if do_plot is set to True)
def getOverheadSatellites(t, tle_file, field_of_view, receiver_latlon, debug=False, show_plot=True, do_plot=True):
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
    if do_plot:
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
            if do_plot:
                if el <= field_of_view:
                    ax.scatter(np.deg2rad(az.degrees), el, color='#DBB40C', zorder=2)
                    ax.annotate(prn, (np.deg2rad(az.degrees), el), fontweight='bold', zorder=2)
                else:
                    ax.scatter(np.deg2rad(az.degrees), el, color='#C0C0C0')

    if do_plot:
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
    else:
        return prn_dict

# calcErrorSingle() calculates the error between truth data and measured data for a single data 
#   collect
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
#   results             : dictionary storing error information. The key is the PRN            [dict]
#                         and the entry is an array with the following elements:
#                         Element 0 --> azimuth error in degrees
#                         Element 1 --> elevation error in degrees
#                         Element 2 --> range error in km
#                         Element 3 --> position error in km
def calcErrorSingle(t, tle_file, field_of_view, receiver_latlon, direction_estimates, debug=False, show_plot=True):
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
    ax.set_xticklabels(['N','45°','E','135°','S','225°','W','315°'])
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_rmax(30)
    ax.set_rticks([10,20,30])
    ax.set_rlabel_position(-202.5)
    ax.legend(['True Position', 'Estimated Position'])
    ax.set_title('Comparison of Estimated and True Satellite Positions')
    fig.savefig('satellite_estimates.png')
    if show_plot:
        plt.show()
        
    # Return results
    results = {int(errors[i,0]): errors[i,1:] for i in np.arange(errors.shape[0])}
    return results
# calcErrorAll() calculates error for multiple data collects
#
# Inputs:
#   tle_file            : text file storing TLE data                                        [string]
#   error_file          : csv file storing data to perform error analysis on                [string]
#   field_of_view       : field of view of receiver in degrees                               [float]
#   receiver_latlon     : list containing lattitude and longitude of receiver        [list of float]
#                         Element 0 --> lattitude
#                         Element 1 --> longitude
#
# Returns: None
def calcErrorAll(tle_file, error_file, field_of_view, receiver_latlon):
    # Define average GPS altitutde
    hGPS = 20200 # [km]

    # Read in results
    results = np.loadtxt(open(error_file), delimiter=",")

    # Create arrays to store truth values
    azimuths = np.zeros(results.shape[0])
    elevations = np.zeros(results.shape[0])

    # Create arrays to store errors
    errors_azimuth = np.zeros(results.shape[0])
    errors_elevation = np.zeros(results.shape[0])
    errors_range = np.zeros(results.shape[0])
    errors_position = np.zeros(results.shape[0])
    
    for i in np.arange(results.shape[0]):
        # Create UTC datetime
        ts = load.timescale()
        t = ts.utc(2023, 7, results[i,0], results[i,1], results[i,2], 0)

        # Get orbit positions of overhead satellites
        prn_dict = getOverheadSatellites(t, tle_file, field_of_view, receiver_latlon, debug=False, show_plot=False, do_plot=False)
    
        # Extract truth data corresponding to current PRN
        receiver = wgs84.latlon(receiver_latlon[0], receiver_latlon[1])
        sat_range = prn_dict[results[i,5]] - receiver
        alt, az, distance = sat_range.at(t).altaz()
        el = 90-alt.degrees
    
        # Calculate errors
        az_error = az.degrees-results[i,4]
        if az_error < -180:
            az_error = az_error + 360
        elif az_error > 180:
            az_error = az_error - 360
        errors_azimuth[i] = az_error # [deg]
        errors_elevation[i] = el-results[i,3] # [deg]
        errors_range[i] = distance.km-hGPS # [km]
        pos_true = [hGPS*np.sin(np.deg2rad(el))*np.cos(np.deg2rad(360-az.degrees)),hGPS*np.sin(np.deg2rad(el))*np.sin(np.deg2rad(360-az.degrees)),hGPS*np.cos(np.deg2rad(el))]
        pos_estimate = [hGPS*np.sin(np.deg2rad(results[i,3]))*np.cos(np.deg2rad(360-results[i,4])),hGPS*np.sin(np.deg2rad(results[i,3]))*np.sin(np.deg2rad(360-results[i,4])),hGPS*np.cos(np.deg2rad(results[i,3]))]
        errors_position[i] = np.linalg.norm(np.array(pos_true)-np.array(pos_estimate))
        
        # Save truth values
        azimuths[i] = az.degrees
        elevations[i] = el
    
    # Create histogram plots of angle error
    elev_stddev = np.std(errors_elevation)
    azim_stddev = np.std(errors_azimuth)
    print("Elevation Angle Standard Deviation: " + str(elev_stddev))
    print("Azimuth Angle Standard Deviation: " + str(azim_stddev))
    fig1, ax1 = plt.subplots(2,1)
    ax1[0].hist(errors_elevation, range=[-4*elev_stddev, 4*elev_stddev], bins=32)
    ax1[0].set_xticks(np.linspace(-4*elev_stddev,4*elev_stddev,num=9,endpoint=True))
    ax1[0].set_xticklabels([r'$-4\sigma$', r'$-3\sigma$', r'$-2\sigma$', r'$-\sigma$', r'$0$', r'$\sigma$', r'$2\sigma$', r'$3\sigma$', r'$4\sigma$'])
    ax1[0].set_xlabel("Elevation Error [deg]")
    ax1[0].set_ylabel("Count")
    ax1[1].hist(errors_azimuth, range=[-4*azim_stddev, 4*azim_stddev], bins=32)
    ax1[1].set_xticks(np.linspace(-4*azim_stddev,4*azim_stddev,num=9,endpoint=True))
    ax1[1].set_xticklabels([r'$-4\sigma$', r'$-3\sigma$', r'$-2\sigma$', r'$-\sigma$', r'$0$', r'$\sigma$', r'$2\sigma$', r'$3\sigma$', r'$4\sigma$'])
    ax1[1].set_xlabel("Azimuth Error [deg]")
    ax1[1].set_ylabel("Count")
    ax1[0].set_title("Angle Error Distributions")

    # Create histogram plots of range and position error
    range_stddev = np.std(errors_range)
    position_stddev = np.std(errors_position)
    print("Range Standard Deviation: " + str(range_stddev))
    print("Position Standard Deviation: " + str(position_stddev))
    fig2, ax2 = plt.subplots(2,1)
    ax2[0].hist(errors_range, range=[-4*range_stddev, 4*range_stddev], bins=32)
    ax2[0].set_xticks(np.linspace(-4*range_stddev,4*range_stddev,num=9,endpoint=True))
    ax2[0].set_xticklabels([r'$-4\sigma$', r'$-3\sigma$', r'$-2\sigma$', r'$-\sigma$', r'$0$', r'$\sigma$', r'$2\sigma$', r'$3\sigma$', r'$4\sigma$'])
    ax2[0].set_xlabel("Range Error [km]")
    ax2[0].set_ylabel("Count")
    ax2[1].hist(errors_position, range=[-4*position_stddev, 4*position_stddev], bins=32)
    ax2[1].set_xticks(np.linspace(-4*position_stddev,4*position_stddev,num=9,endpoint=True))
    ax2[1].set_xticklabels([r'$-4\sigma$', r'$-3\sigma$', r'$-2\sigma$', r'$-\sigma$', r'$0$', r'$\sigma$', r'$2\sigma$', r'$3\sigma$', r'$4\sigma$'])
    ax2[1].set_xlabel("Position Error [deg]")
    ax2[1].set_ylabel("Count")
    ax2[0].set_title("Range and Position Error Distributions")

    # Make scatter plots of error versus elevation angle
    fig3, ax3 = plt.subplots(2,1, sharex=True)
    ax3[0].scatter(elevations, np.abs(errors_elevation))
    ax3[0].grid(True)
    ax3[0].set_ylabel('Elevation Error [deg]')
    ax3[0].set_title('Angle Error Versus Elevation Angle')
    ax3[1].scatter(elevations, np.abs(errors_azimuth))
    ax3[1].grid(True)
    ax3[1].set_xlabel('Elevation Angle [deg]')
    ax3[1].set_ylabel('Azimuth Error [deg]')

    # Create time error plot
    prn = 32
    days = [24,25]
    hour = 22
    fig4, ax4 = plt.subplots(2,2, sharex=True)
    fig5, ax5 = plt.subplots(2,1, sharex=True)
    for day in days:
        # Only select data corresponding to specific prn, day, and hour
        data = results[(results[:,0] == day) & (results[:,1] == hour) & (results[:,5] == prn),:]
        
        # Create arrays to store errors
        time_errors_azimuth = np.zeros(data.shape[0])
        time_errors_elevation = np.zeros(data.shape[0])
        time_errors_range = np.zeros(data.shape[0])
        time_errors_position = np.zeros(data.shape[0])

        # Create arrays to store truth and estimate angles
        truth_elevations = np.zeros(data.shape[0])
        truth_azimuths = np.zeros(data.shape[0])
    
        # Create array to store times
        times = []

        for i in np.arange(data.shape[0]):
            # Create UTC datetime
            ts = load.timescale()
            t = ts.utc(2023, 7, data[i,0], data[i,1], data[i,2], 0)
            t2 = ts.utc(2023, 7, 25, data[i,1], data[i,2], 0)
            times.append(datetime(*tuple(map(int,tuple(t2.utc)))))

            # Get orbit positions of overhead satellites
            prn_dict = getOverheadSatellites(t, tle_file, field_of_view, receiver_latlon, debug=False, show_plot=False, do_plot=False)
    
            # Extract truth data corresponding to current PRN
            receiver = wgs84.latlon(receiver_latlon[0], receiver_latlon[1])
            sat_range = prn_dict[data[i,5]] - receiver
            alt, az, distance = sat_range.at(t).altaz()
            el = 90-alt.degrees
    
            # Calculate errors
            az_error = az.degrees-data[i,4]
            if az_error < -180:
                az_error = az_error + 360
            elif az_error > 180:
                az_error = az_error - 360
            time_errors_azimuth[i] = az_error # [deg]
            time_errors_elevation[i] = el-data[i,3] # [deg]
            time_errors_range[i] = distance.km-hGPS # [km]
            pos_true = [hGPS*np.sin(np.deg2rad(el))*np.cos(np.deg2rad(360-az.degrees)),hGPS*np.sin(np.deg2rad(el))*np.sin(np.deg2rad(360-az.degrees)),hGPS*np.cos(np.deg2rad(el))]
            pos_estimate = [hGPS*np.sin(np.deg2rad(data[i,3]))*np.cos(np.deg2rad(360-data[i,4])),hGPS*np.sin(np.deg2rad(data[i,3]))*np.sin(np.deg2rad(360-data[i,4])),hGPS*np.cos(np.deg2rad(data[i,3]))]
            time_errors_position[i] = np.linalg.norm(np.array(pos_true)-np.array(pos_estimate))

            # Save truth and estimate data
            truth_elevations[i] = el
            truth_azimuths[i] = az.degrees

        # Graph errors
        ax4[0,0].plot_date(times,time_errors_elevation, '.--')
        ax4[0,1].plot_date(times,time_errors_range, '.--')
        ax4[1,0].plot_date(times,time_errors_azimuth, '.--')
        ax4[1,1].plot_date(times,time_errors_position, '.--')

        # Make lines of best fit
        times_seconds = np.array([dt.timestamp() for dt in times])
        a_elev, b_elev = np.polyfit(times_seconds, data[:,3], 1)
        a_azim, b_azim = np.polyfit(times_seconds, data[:,4], 1)

        # Plot truth and estimate of moving satellite
        if day == 24:
            ax5[0].plot(times,  truth_elevations, '.-', color='#1f77b4', label='July 24 (True)')
            ax5[0].plot(times, data[:,3], 'x', color='#1f77b4', label='_nolegend_')
            ax5[0].plot(times, a_elev*times_seconds+b_elev, '--', color='#1f77b4', label='July 24 (Estimate)') 
            ax5[1].plot(times, truth_azimuths, '.-', color='#1f77b4')
            ax5[1].plot(times, data[:,4], 'x', color='#1f77b4')
            ax5[1].plot(times, a_azim*times_seconds+b_azim, '--', color='#1f77b4')
        elif day == 25:
            ax5[0].plot(times,  truth_elevations, '.-', color='#ff7f0e', label='July 25 (True)')
            ax5[0].plot(times, data[:,3], 'x', color='#ff7f0e', label='_nolegend_')
            ax5[0].plot(times, a_elev*times_seconds+b_elev, '--', color='#ff7f0e', label='July 25 (Estimate)') 
            ax5[1].plot(times, truth_azimuths, '.-', color='#ff7f0e')
            ax5[1].plot(times, data[:,4], 'x', color='#ff7f0e')
            ax5[1].plot(times, a_azim*times_seconds+b_azim, '--', color='#ff7f0e')

    # Make plots like nice
    format_date = mpl_dates.DateFormatter('%H:%M')
    ax4[0,0].xaxis.set_major_formatter(format_date)
    ax4[0,1].xaxis.set_major_formatter(format_date)
    ax4[1,0].xaxis.set_major_formatter(format_date)
    ax4[1,1].xaxis.set_major_formatter(format_date)
    ax4[1,0].set_xlabel('Time')
    ax4[1,1].set_xlabel('Time')
    ax4[0,0].set_ylabel('Elevation Error [deg]')
    ax4[0,1].set_ylabel('Range Error [km]')
    ax4[1,0].set_ylabel('Azimuth Error [deg]')
    ax4[1,1].set_ylabel('Position Error [km]')
    ax4[0,0].grid(True)
    ax4[0,1].grid(True)
    ax4[1,0].grid(True)
    ax4[1,1].grid(True)
    ax4[0,1].legend(['July 24','July 25'])
    fig4.suptitle('Errors Versus Time for PRN 32')
    ax5[0].xaxis.set_major_formatter(format_date)
    ax5[1].xaxis.set_major_formatter(format_date)
    ax5[0].grid(True)
    ax5[1].grid(True)
    ax5[1].set_xlabel('Time')
    ax5[0].set_ylabel('Elevation Angle [deg]')
    ax5[1].set_ylabel('Azimuth Angle [deg]')
    ax5[0].set_title('Estimated Versus True Satellite Movement (PRN 32)')
    ax5[0].legend()

    # Show plots
    plt.show() 
    
# performSensitivityAnalysis() performs sensitivity analysis on the effect of elevation angle on 
#   azimuth and elevation angle error
#
# Inputs:
#   do_calculations: options parameter controlling whether to perform computations             [T/F]
#
# Outputs: None 
def performSensitivityAnalysis(do_calculations=True):
    # Define wavelength
    wavelength = 0.1905

    # Define array dimensions
    d = wavelength/2

    # Create lookup table
    lookup_table = makeLookupTable(d, wavelength, 27, 360, step=1)

    # Define elevation and azimuth angles to test
    elevations = range(1,28)
    azimuths = [0,45,90,135,180,225,270,315,360]

    if do_calculations:
        # Initialize empty arrays to store results
        error_el = np.zeros((len(azimuths),len(elevations)))
        error_az = np.zeros((len(azimuths), len(elevations)))

        # Iterate over all elevation angles
        for j, el in enumerate(elevations):
            print('Elevation Angle: ' + str(el))

            # Iterate over all azimuth angles
            for i, az in enumerate(azimuths):
                print('Azimuth Angle: ' + str(az))

                # Define number of trials to perform for every permutation of elevation and azimuth angle
                num_trials = 10

                # Create arrays to store results of each trial
                temp_elev = np.zeros(num_trials)
                temp_azim = np.zeros(num_trials)

                for k in np.arange(num_trials):
                    print('Trial ' + str(k+1))

                    # Generate simulated signals and extract correlation data from signals
                    corr1, corr2, corr3, corr4 = prepareDataForMonopulse_sim(1, el, az)

                    # Test if all signals correlated
                    if corr1 is not None and corr2 is not None and corr3 is not None and corr4 is not None:
                        # Estimate elevation and azimuth angles for signals
                        temp_elev[k], temp_azim[k] = calc_AoA_corr(corr1, corr2, corr3, corr4, lookup_table)
                    else:
                        temp_elev[k] = np.nan
                        temp_azim[k] = np.nan

                # Calculate average of all trials
                temp_elev = temp_elev[~np.isnan(temp_elev)]
                temp_azim = temp_azim[~np.isnan(temp_azim)]
                elev = np.mean(temp_elev)
                azim = np.mean(temp_azim)
                error_el[i,j] = np.abs(elev-el)
                error_az[i,j] = np.abs(azim-az)

        # Save data
        np.savetxt("azimuth_error.csv", error_az, delimiter=',')
        np.savetxt("elevation_error.csv", error_el, delimiter=',')
    else: # Load pre-existing data
        error_el = np.loadtxt('elevation_error.csv', delimiter=',')
        error_az = np.loadtxt('azimuth_error.csv', delimiter=',')

    # Remove unnecessary data
    error_az = np.delete(error_az, [0,-1], 0)
#     error_az = np.delete(error_az, 0, 1)
    error_el = np.delete(error_el, [0,-1], 0)
#    error_el = np.delete(error_el, 0, 1)
#    elevations = elevations[1:]
    azimuths = azimuths[1:-1]

    # Calculate max error
    max_error = np.amax(np.array([np.amax(np.amax(error_az)), np.amax(np.amax(error_el))]))
 
    # Visualize results
    fig1, ax1 = plt.subplots()
    shw = ax1.imshow(error_az, cmap=plt.cm.get_cmap('RdYlGn').reversed(), vmin=0, vmax=max_error) # add interpolation='bilinear' for SMOOTH graph
    fig1.colorbar(shw, orientation='horizontal')
    ax1.set_xticks(np.arange(len(elevations)))
    ax1.set_yticks(np.arange(len(azimuths)))
    ax1.set_xticklabels(elevations)
    ax1.set_yticklabels(azimuths)
    ax1.invert_yaxis()
    ax1.set_xlabel('Elevation Angle [deg]')
    ax1.set_ylabel('Azimuth Angle [deg]')
    ax1.set_title('Azimuth Angle Error [deg]')
    
    fig2, ax2 = plt.subplots()
    shw = ax2.imshow(error_el, cmap=plt.cm.get_cmap('RdYlGn').reversed(), vmin=0, vmax=max_error) # add interpolation='bilinear' for SMOOTH graph
    fig2.colorbar(shw, orientation='horizontal')
    ax2.set_xticks(np.arange(len(elevations)))
    ax2.set_yticks(np.arange(len(azimuths)))
    ax2.set_xticklabels(elevations)
    ax2.set_yticklabels(azimuths)
    ax2.invert_yaxis()
    ax2.set_xlabel('Elevation Angle [deg]')
    ax2.set_ylabel('Azimuth Angle [deg]')
    ax2.set_title('Elevation Angle Error [deg]')

    # Show results
    plt.show()
