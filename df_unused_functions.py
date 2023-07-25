import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
from scipy import signal, fftpack
from monopulse_data_prep import *
import math
# Import custom python packages
from flatirons.gps_gen import *
from flatirons.gps_dsp import *
from flatirons.parse import *

# Use custom matplotlib styling
plt.style.use('flatirons/flatirons.mplstyle')


def makeLookupTable_4element(d, wavelength, max_el, max_az, step=2):
    """ ! Generates a lookup table of expected phase shifts between a reference element and all other
        elements in a 2x2 square array for all angles in range.

    @param d            The distance between antennas.
    @param wavelength   The wavelength of the signal to be received.
    @param max_el       The maximum elevation angle to calculate.
    @param max_az       The maximum azimuth angle to calculate.
    @param step         The step size between angles. Defaults to 2.

    @return            A dictionary with keys of form (elevation, azimuth) and values of the expected
                        phase shifts from a reference antenna to all other antennas.
    """
    table = {}
    # calculate phase shift for each antenna, using antenna 1 as a reference
    for elevation_angle in range(0, max_el, step):  # elevation angles
        for azim_angle in range(0, max_az, step):  # azimuth angles
            az_angle = np.deg2rad(azim_angle)
            elev_angle = np.deg2rad(elevation_angle)
            d2 = d * np.cos(az_angle)
            p2 = ((2 * np.pi * d2) / wavelength) * np.sin(elev_angle)
            d3 = d * np.sin(az_angle)
            p3 = ((2 * np.pi * d3) / wavelength) * np.sin(elev_angle)
            d4 = d * np.sqrt(2) * np.sin(az_angle + np.pi / 4)
            p4 = ((2 * np.pi * d4) / wavelength) * np.sin(elev_angle)
            table[elevation_angle, azim_angle] = [round(p2, 3), round(p3, 3), round(p4, 3)]
    return table


def calc_phase_shift(sig1, sig2):
    """ ! Calculates the phase shift between two antennas using sum and difference beams.

    @param sig1     Signal defined to have phase shift of 0.
    @param sig2     Signal to calculate phase shift of with respect to sig1.

    @return         The phase difference between the two input signals.
    """
    sum_vector = [sig1[i] + sig2[i] for i in range(len(sig1))]
    diff_vector = [sig1[i] - sig2[i] for i in range(len(sig1))]
    sum_avg = np.mean(sum_vector)
    diff_avg = np.mean(diff_vector)
    r = diff_avg / sum_avg
    phase = 2 * np.arctan(-np.imag(r))

    return phase


def calc_AoA(signals, lookup_table):
    """ ! Calculates the angle of arrival from the lookup table.

    @param signals          Array of four received signals.
    @param lookup_table     Lookup table of expected phase shifts for each angle of arrival.

    @return                 Angle of arrival of the signal as a tuple.
    """
    # split up dictionary into angles and phases
    angle_list = list(lookup_table.keys())
    phase_list = list(lookup_table.values())
    # calculate phase shifts
    phase12 = calc_phase_shift(signals[0], signals[1])
    phase13 = calc_phase_shift(signals[0], signals[2])
    phase14 = calc_phase_shift(signals[0], signals[3])
    position = find_nearest_index(phase_list, [round(phase12, 3), round(phase13, 3), round(phase14, 3)])
    return angle_list[position]


def calc_AoA_monopulse(signals):
    """ ! Calculates the angle of arrival using 2-D monopulse algorithm.

    @param signals          Array of four received signals.

    @return                 Azimuth angle of the signal.
    @return                 Elevation angle of the signal.

    @note broken
    """
    sum_beam = [(signals[0][i] + signals[2][i]) + (signals[1][i] + signals[3][i]) for i in range(len(signals[1]))]
    delta_az = [(signals[0][i] + signals[2][i]) - (signals[1][i] + signals[3][i]) for i in range(len(signals[1]))]
    delta_el = [(signals[0][i] - signals[2][i]) + (signals[1][i] - signals[3][i]) for i in range(len(signals[1]))]
    sum_avg = np.mean(sum_beam)
    delta_az_avg = np.mean(delta_az)
    delta_el_avg = np.mean(delta_el)
    r_az = delta_az_avg / sum_avg
    r_el = delta_el_avg / sum_avg
    theta_az = np.rad2deg(np.arccos((2 / np.pi) * np.arctan(-np.imag(sum_avg / delta_az_avg))))
    theta_el = np.rad2deg(np.arccos((2 / np.pi) * np.arctan(-np.imag(1 / r_el))))
    return theta_az, theta_el


def calc_AoA_corr_4element(corr1, corr2, corr3, corr4, lookup_table, plot_corr=False):
    """ ! Calculates the angle of arrival from the lookup table.

    @param corr1            Correlation vector for signal 1
    @param corr2            Correlation vector for signal 2
    @param corr3            Correlation vector for signal 3
    @param corr4            Correlation vector for signal 4
    @param lookup_table     Lookup table of expected phase shifts for each angle of arrival.

    @return                 Angle of arrival of the signal as a tuple.
    """
    # split up dictionary into angles and phases
    angle_list = list(lookup_table.keys())
    phase_list = list(lookup_table.values())
    # calculate phase shifts
    phase12 = calc_corr_phase_shift(corr1, corr2)
    phase13 = calc_corr_phase_shift(corr1, corr3)
    phase14 = calc_corr_phase_shift(corr1, corr4)
    position = find_nearest_index(phase_list, [round(phase12, 3), round(phase13, 3), round(phase14, 3)])
    elevation_angle = angle_list[position][0]
    azimuth_angle = angle_list[position][1]
    return elevation_angle, azimuth_angle


