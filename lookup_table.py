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
    sig2 = [sig1[i] * np.exp(phase2 * 1j) for i in range(len(sig1))]

    d3 = d * np.sin(az_angle_input)
    phase3 = ((2 * np.pi * d3) / wavelength) * np.sin(elev_angle_input)
    sig3 = [sig1[i] * np.exp(phase3 * 1j) for i in range(len(sig1))]

    d4 = d * np.sqrt(2) * np.sin(az_angle_input + np.pi / 4)
    phase4 = ((2 * np.pi * d4) / wavelength) * np.sin(elev_angle_input)
    sig4 = [sig1[i] * np.exp(phase4 * 1j) for i in range(len(sig1))]

    sig = [sig1, sig2, sig3, sig4]

    return sig


def calc_AoA_monopulse(signals):
    """ ! Calculates the angle of arrival using 2-D monopulse algorithm.

    @param signals          Array of four received signals.

    @return                 Azimuth angle of the signal.
    @return                 Elevation angle of the signal.

    @note fully broken
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


def calc_corr_phase_shift(corr1, corr2, plot_corr = False):
    """ ! Calculates the phase shift between two antennas using the phases of their correlation vectors.

    @param corr1     Correlation output of reference antenna
    @param corr2     Correlation output of second antenna

    @return         The phase difference between the two correlation vectors.
    """
    corr1_abs = np.abs(corr1)
    corr2_abs = np.abs(corr2)
    c1 = corr1_abs / np.median(corr1_abs)
    c2 = corr2_abs / np.median(corr2_abs)

    c1_index = np.array(corr1_abs).argmax()
    # make sure comparing the same peaks
    c2_index = np.array(corr2_abs[c1_index-5:c1_index+6]).argmax() + (c1_index - 5)

    # print(c1_index)
    # print(c2_index)
    print("Corr1[" + str(c1_index) + "]: " + str(corr1[c1_index]))
    print("Corr2[" + str(c2_index) + "]: " + str(corr2[c2_index]))

    if plot_corr:
        fig2, ax2 = plt.subplots()
        ax2.plot(range(len(c2)), c2, '--')
        ax2.plot(range(len(c1)), c1)
        plt.title("absolute value of correlations")
        plt.show()

    phase_corr1 = np.angle(corr1[c1_index])
    phase_corr2 = np.angle(corr2[c2_index])
    print("Phase channel 1: " + str(np.rad2deg(phase_corr1)))
    print("Phase channel 2: " + str(np.rad2deg(phase_corr2)))

    phase_diff = phase_corr1 - phase_corr2
    if(phase_diff < -np.pi and phase_diff > (-2 * np.pi)):
        phase_diff += (2 * np.pi)
    elif(phase_diff > np.pi and phase_diff < (2 * np.pi)):
        phase_diff -= (2 * np.pi)

    return phase_diff


def calc_AoA_corr(corrs, lookup_table):
    """ ! Calculates the angle of arrival from the lookup table.

    @param corrs            Array of four correlation vectors for a specific PRN.
    @param lookup_table     Lookup table of expected phase shifts for each angle of arrival.

    @return                 Angle of arrival of the signal as a tuple.
    """
    # split up dictionary into angles and phases
    angle_list = list(lookup_table.keys())
    phase_list = list(lookup_table.values())
    # calculate phase shifts
    phase12 = calc_corr_phase_shift(corrs[0], corrs[1])
    phase13 = calc_corr_phase_shift(corrs[0], corrs[2])
    phase14 = calc_corr_phase_shift(corrs[0], corrs[3])
    position = find_nearest_index(phase_list, [round(phase12, 3), round(phase13, 3), round(phase14, 3)])
    return angle_list[position]


if __name__ == "__main__":
    # configuration of antennas:
    # 1  2
    # 3  4

    # setup
    wavelength = 1
    d = wavelength / 2
    lookup_table = makeLookupTable(d, wavelength, 27, 360, step=2)
    # sig1 = makeGPSClean(7, num_periods=2, sample_rate=2.046e6)  # generate a reference signal
    # signals = gen_shifted_signals(sig1, elevation=10, azimuth=15)  # simulate a phase shift for other elements

    # # testing for lookup table implementation
    # aoa = calc_AoA(signals, lookup_table)  # find angle of arrival of simulated signal in lookup table
    # print("Lookup table: " + str(aoa))

    # # testing for 2D monopulse implementation
    # a1, a2 = calc_AoA_monopulse(signals)
    # print("Monopulse: (" + str(a2) + ", " + str(a1) + ")")

    # # testing monopulse algorithm with simulated correlation algorithm output
    # corr1, corr2, corr3, corr4 = prepareDataForMonopulse_sim(27)
    # correlations = [corr1, corr2, corr3, corr4]
    # print(calc_AoA_corr(correlations, lookup_table))

    # testing on real data
    phase_ch_2 = np.deg2rad(25)
    wire_delay = np.deg2rad(-165)
    corr1, corr2 = prepareDataForMonopulse('data/Samples_Jul_12/18_monopulse.csv', 18, wire_delay, False, phase_ch_2)
    phase_diff = calc_corr_phase_shift(corr1, corr2)
    print("Calculated phase difference: " + str(np.rad2deg(phase_diff)))
    # phase_diff = (2 * np.pi) + phase_diff
    theta = np.arcsin((phase_diff * wavelength) / (2 * np.pi * d))
    print("Calculated elevation angle: " + str(np.rad2deg(theta)))
