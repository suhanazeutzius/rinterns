import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
from scipy import signal, fftpack
from monopulse_data_prep import *


def __cacode(prn):
    """
    Generate CA Code for any PRN

    :param int prn: satellite PRN (1-32)
    :returns numpy array: 1023 element ca code for chosen SV
    """

    def _get_g2s(prn):
        # Shifts for PRNs can be used as g2s[prn]. pnr=0 is not valid. For EGNOS and WAAS use g2s[prn - 87]
        g2s = np.array(
            [0, 5, 6, 7, 8, 17, 18, 139, 140, 141, 251, 252, 254, 255, 256, 257, 258, 469, 470, 471, 472, 473,
             474, 509, 512, 513, 514, 515, 516, 859, 860, 861, 862,
             # End of GPS following are shift for EGNOS and WASS
             145, 175, 52, 21, 237, 235, 886, 657, 634, 762, 355, 1012, 176, 603, 130, 359, 595, 68, 386])
        if 0 < prn <= 32:
            return g2s[prn]
        elif 120 <= prn <= 138:
            return g2s[prn - 87]
        else:
            return np.NAN
            # raise ValueError("PRN {} not allowed. Valid range: [1-32, 120-138]".format(prn))

    g2shift = _get_g2s(prn)

    # Preload registers
    g1 = np.zeros(1023)
    reg = -1 * np.ones(10)
    # Generate G1 signal chips
    for i in range(1023):
        g1[i] = reg[9]
        sBit = reg[2] * reg[9]
        reg[1:10] = reg[0:9]
        reg[0] = sBit

    # Generate G2 code
    g2 = np.zeros(1023)
    reg = -1 * np.ones(10)
    # Generate G2 chips
    for i in range(1023):
        g2[i] = reg[9]
        sBit = reg[1] * reg[2] * reg[5] * reg[7] * reg[8] * reg[9]
        reg[1:10] = reg[0:9]
        reg[0] = sBit
    # shift G2 code

    g2 = np.concatenate((g2[(1022 - g2shift + 1):1023], g2[0:(1023 - g2shift)]))
    return -np.multiply(g1, g2)


def cacode(prn, sample_rate=None):
    """
    Return cacode with oversampled rate.
    param prns int, prn # to generate cacode for
    param sample_rate: float, default = 1.023e6, Sample rate for prncode output
    :return: numpy array, PRN code for given sample rate
    """

    if sample_rate is None:
        return __cacode(prn)
    samplesPerCode = round(sample_rate / 1.023e6 / 1023)
    ts = 1 / sample_rate  # Sampling period
    tc = 1 / 1.023e6  # Code period

    ca_code = cacode(prn)
    codevalueind = np.ceil(ts * np.arange(1, samplesPerCode + 1) / tc).astype(int) - 1
    codevalueind[-1] = 1022  # fix last index
    return ca_code[codevalueind]


# Define function to generate GPS IQ signal
def makeGPSSignal(prn_num, sample_ratio, noise=True, plot=False):
    # Generate PRN (C/A) code
    prn = cacode(prn_num)

    # Convert PRN code to 0s and 1s
    prn = (prn > 0).astype(int)

    # Generate vector for data bit
    data_bit = 1
    if data_bit == 0:
        dat = np.zeros(len(prn))
    elif data_bit == 1:
        dat = np.ones(len(prn))
    dat = dat.astype(int)

    # Perform modulo-2 addition
    comp_binary_signal = np.zeros(len(prn))
    for i in np.arange(len(comp_binary_signal)):
        if prn[i] == dat[i]:
            comp_binary_signal[i] = 0
        else:
            comp_binary_signal[i] = 1
    comp_binary_signal = comp_binary_signal.astype(int)

    # Perform BPSK modulation and convert to IQ data
    I = np.ones(len(comp_binary_signal))
    I[comp_binary_signal == 1] = -1
    Q = np.zeros(len(comp_binary_signal))
    BPSK_signal = I + 1j * Q

    # Tile signal
    BPSK_signal = np.tile(BPSK_signal, 2)

    # Resample signal up to bladeRF sampling frequency
    downsample = 2
    BPSK_signal = scipy.signal.resample_poly(BPSK_signal, sample_ratio * downsample, downsample)

    if noise:
        # Add noise to BPSK signal
        n = (np.random.randn(len(BPSK_signal)) + 1j * np.random.randn(len(BPSK_signal)) / np.sqrt(2))
        noise_power = 0.5
        BPSK_signal = BPSK_signal + (n * np.sqrt(noise_power))
        phase_noise = np.random.randn(len(BPSK_signal)) * 0.5
        BPSK_signal = BPSK_signal * np.exp(1j * phase_noise)

    if plot:
        # Plot IQ constellation of signal
        plt.plot(np.real(BPSK_signal), np.imag(BPSK_signal), '.')
        plt.grid(True)
        plt.title("IQ Constellation for PRN " + str(prn_num))
        plt.show()

    # Return signal
    return BPSK_signal


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


if __name__ == "__main__":
    # configuration of antennas:
    # 1  2
    # 3  4

    # setup
    wavelength = 1
    d = wavelength / 2
    # lookup_table = makeLookupTable(d, wavelength, 27, 360)
    # sig1 = makeGPSSignal(22, 30)  # generate a reference signal
    # signals = gen_shifted_signals(sig1, elevation=10, azimuth=15)  # simulate a phase shift for other elements

    # testing for lookup table implementation
    # aoa = calc_AoA(signals, lookup_table)  # find angle of arrival of simulated signal in lookup table
    # print("Lookup table: " + str(aoa))

    # testing for 2D monopulse implementation
    # a1, a2 = calc_AoA_monopulse(signals)
    # print("Monopulse: (" + str(a2) + ", " + str(a1) + ")")

    # testing monopulse algorithm with correlation algorithm output
    sig1, sig2 = prepareDataForMonopulse('data/Samples_Jul_6/sat12_1009.csv', 7, 8.13e-9, plot_correlation=False)
    phi = calc_phase_shift(sig1, sig2)
    print("Calculated phase shift: " + str(np.rad2deg(phi)))
    theta = np.arcsin((phi * wavelength) / (2 * np.pi * d))
    print("Calculated elevation angle: " + str(np.rad2deg(theta)))

