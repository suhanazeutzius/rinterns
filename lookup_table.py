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


def makeLookupTable(d, wavelength, max_el, max_az, step=2):
    """ ! Generates a lookup table of expected phase shifts between a reference element and all other
            elements in an isosceles right triangle array for all angles in range.

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
            table[elevation_angle, azim_angle] = [round(p2, 3), round(p3, 3)]
    return table


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


def find_nearest_index(arr, value):
    """ ! Finds the index of the closest matching value in a table

    @param arr      An array of values to iterate over.
    @param value    The value to match to something in the array.

    @return         The index of the array with the closest matching value.
    """
    diffs = []
    for i in range(0, len(arr)):
        diff = 0
        for j in range(len(value)):
            diff += np.abs(arr[i][j] - value[j])
        # diff = np.abs(arr[i][0] - value[0]) + np.abs(arr[i][1] - value[1]) + np.abs(arr[i][2] - value[2])
        diffs.append(diff)
    return diffs.index(min(diffs))


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


def gen_shifted_signals(sig1, elevation, azimuth):
    """ ! Simulate a phase shifted signal for an incoming wave.

    @param sig1         Reference signal.
    @param elevation    Elevation angle of incoming wave
    @param azimuth      Azimuth angle of incoming wave

    @return             Array of four phase shifted signals
    """
    wavelength = 1
    d = wavelength / 2
    az_angle_input = np.deg2rad(azimuth)
    elev_angle_input = np.deg2rad(elevation)
    # calculate phase shift for each antenna, using antenna 1 as a reference
    d2 = d * np.cos(az_angle_input)
    phase2 = ((2 * np.pi * d2) / wavelength) * np.sin(elev_angle_input)
    sig2 = [sig1[i] * np.exp(-phase2 * 1j) for i in range(len(sig1))]

    d3 = d * np.sin(az_angle_input)
    phase3 = ((2 * np.pi * d3) / wavelength) * np.sin(elev_angle_input)
    sig3 = [sig1[i] * np.exp(-phase3 * 1j) for i in range(len(sig1))]

    d4 = d * np.sqrt(2) * np.sin(az_angle_input + np.pi / 4)
    phase4 = ((2 * np.pi * d4) / wavelength) * np.sin(elev_angle_input)
    sig4 = [sig1[i] * np.exp(-phase4 * 1j) for i in range(len(sig1))]

    sig = [sig1, sig2, sig3, sig4]

    return sig


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


def calc_corr_phase_shift(corr1, corr2, plot_corr=True):
    """ ! Calculates the phase shift between two antennas using the phases of their correlation vectors.

    @param corr1        Correlation output of reference antenna
    @param corr2        Correlation output of second antenna
    @param plot_corr    If true, plot the normalized absolute value of the correlations

    @return             The phase difference between the two correlation vectors.

    @note               Return the opposite of the phase difference that is calculated, because the correlations use
                        complex conjugates of the signals.
    """
    corr1_abs = np.abs(corr1)
    corr2_abs = np.abs(corr2)
    c1 = corr1_abs / np.median(corr1_abs)
    c2 = corr2_abs / np.median(corr2_abs)

    peak_height = 7.5
    c1_indices, _ = signal.find_peaks(c1, height=peak_height)
    c2_indices = []
    to_delete = []
    for i in range(len(c1_indices)):
        c2_index = np.array(corr2_abs[c1_indices[i]-5:c1_indices[i]+6]).argmax() + (c1_indices[i] - 5)
        if c2[c2_index] > peak_height:
            c2_indices.append(c2_index)
        else:
            to_delete.append(i)
    c1_indices = np.delete(c1_indices, to_delete)

    phase_corr1 = []
    phase_corr2 = []
    for i in range(len(c1_indices)):
        phase_corr1.append(np.angle(corr1[c1_indices[i]]))
        phase_corr2.append(np.angle(corr2[c2_indices[i]]))

    # phase_diff = [0] * len(c1)
    phase_diff = [phase_corr1[i] - phase_corr2[i] for i in range(len(phase_corr1))]

    for i in range(len(phase_diff)):
        if phase_diff[i] < 0:
            phase_diff[i] += (2 * np.pi)

    # print([np.rad2deg(phase_diff[i]) for i in range(len(phase_diff))])
    # print("standard deviation of phase difference: " + str(np.rad2deg(np.std(phase_diff))))
    if plot_corr:
        fig2, ax2 = plt.subplots(2)
        ax2[0].set_xlabel('Correlation Index')
        ax2[0].set_ylabel('Correlation Peak Strength')
        ax2[0].set_title('Absolute Value of Correlations')
        ax2[0].set_xlim(0, len(c1))
        # ax2.plot(range(len(corr1)), corr1)
        # ax2.plot(range(len(corr2)), corr2, '--')
        ax2[0].plot(range(len(c1)), c1)
        ax2[0].plot(range(len(c2)), c2, '--')
        ax2[0].axhline(y=7.5, color='k', linestyle=':')
        ax2[0].legend(['Channel 1', 'Channel 2'])
        ax2[1].set_xlim(0, len(c1))
        ax2[1].plot(c1_indices, np.rad2deg(phase_diff), 'o-')
        plt.show()

    if max(phase_diff) > np.deg2rad(345) and min(phase_diff) < np.deg2rad(15):
        for i in range(len(phase_diff)):
            if phase_diff[i] < np.pi / 2:
                phase_diff[i] += 2 * np.pi

    print([np.rad2deg(phase_diff[i]) for i in range(len(phase_diff))])
    print("standard deviation of phase difference: " + str(np.rad2deg(np.std(phase_diff))))

    phase_diff_avg = np.average(phase_diff) % (2 * np.pi)
    phase_diff_med = np.median(phase_diff) % (2 * np.pi)

    print("Average phase: " + str(np.rad2deg(phase_diff_avg)))
    print("Median phase: " + str(np.rad2deg(phase_diff_med)))

    # get phase diff median between -pi and pi
    if (phase_diff_med < -np.pi and phase_diff_med > (-2 * np.pi)):
        phase_diff_med += (2 * np.pi)
    elif (phase_diff_med > np.pi and phase_diff_med < (2 * np.pi)):
        phase_diff_med -= (2 * np.pi)

    # get phase diff average between -pi and pi
    if (phase_diff_avg < -np.pi and phase_diff_avg > (-2 * np.pi)):
        phase_diff_avg += (2 * np.pi)
    elif (phase_diff_avg > np.pi and phase_diff_avg < (2 * np.pi)):
        phase_diff_avg -= (2 * np.pi)

    return -phase_diff_med  # return the opposite of the calculated phase shift


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


def calc_corr_AoA(file12, file13, prn, phase_ch_2, lookup_table, plot_corr=False):
    """ ! Calculates the angle of arrival from the lookup table.

    @param file12               Data from antenna 1 and 2
    @param file13               Data from antenna 1 and 3
    @param prn                  PRN code to correlate to
    @param phase_ch_2           Phase offset between blade channels
    @param lookup_table         Table of expected phase shifts for each angle of arrival
    @param plot_corr            Option to plot correlation graphs

    @return                     Elevation and azimuth angles of incoming signals
    """
    # split up dictionary into angles and phases
    angle_list = list(lookup_table.keys())
    phase_list = list(lookup_table.values())

    # calculate phase shifts between antennas
    corr1, corr2 = prepareDataForMonopulse(file12, prn, False, phase_ch_2)
    phase12 = calc_corr_phase_shift(corr1, corr2, plot_corr=plot_corr)
    corr1, corr3 = prepareDataForMonopulse(file13, prn, False, phase_ch_2)
    phase13 = calc_corr_phase_shift(corr1, corr3, plot_corr=plot_corr)

    position = find_nearest_index(phase_list, [round(phase12, 3), round(phase13, 3)])
    elevation_angle = angle_list[position][0]
    azimuth_angle = (angle_list[position][1] + 270) % 360
    return elevation_angle, azimuth_angle


def calc_Aoa_corr_2d(corr1, corr2, plot=False):
    phase_diff = calc_corr_phase_shift(corr1, corr2, plot_corr=plot)
    elevation_angle = np.arcsin((phase_diff * wavelength) / (2 * np.pi * d))
    return phase_diff, elevation_angle


if __name__ == "__main__":
    # configuration of antennas:
    # 1  2
    # 3  4

    # setup
    wavelength = 0.1905  # meters
    d = wavelength / 2  # antennas are placed
    lookup_table = makeLookupTable(d, wavelength, 35, 360)

    # parameters for calc_corr_AoA
    file12 = 'data/Samples_Jul_24/PRN10_copper9.csv(2)'  # data for antennas 1 and 2
    file13 = 'data/Samples_Jul_24/PRN10_copper9.csv'  # data for antennas 1 and 3
    phase_ch_2 = np.deg2rad(25)  # 25 for copper, 19 for gray
    prn = 32

    e, a = calc_corr_AoA(file12, file13, prn, phase_ch_2, lookup_table)
    print("Elevation angle: " + str(e))
    print("Azimuth angle: " + str(a))
