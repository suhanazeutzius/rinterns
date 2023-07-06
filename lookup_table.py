import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
from scipy import signal, fftpack


def noisy_signal_gen(phi, prn=13):
    """
    Generate a BPSK modulated signal & phase shifted signal
    with noise added

    :param: radian: phase shift for the second signal
    :returns tuple of numpy arrays: (signal, shifted signal)
    """

    SNR = 16  # dB
    SNR_gain = pow(10, 16 / 20)

    signal, shifted_signal = signal_gen(phi, prn)

    noise = np.random.normal(0, 1, len(signal))
    signal = [(SNR_gain) * signal[i] + noise[i] for i in range(len(signal))]
    shifted_signal = [shifted_signal[i] + (SNR_gain * noise[i]) for i in range(len(shifted_signal))]

    return signal, shifted_signal


def signal_gen(phi, prn=13):
    """
    Generate a BPSK modulated signal & phase shfited version of it

    :param: radian: phase shift for the second signal
    :returns tuple of numpy arrays: (signal, shifted signal)
    """

    F_brf_sample = 61.44e6  # Hz
    numseconds = 2048e-6  # s

    bits = cacode(prn)
    numbits = 1023
    chip_rate = 1.023e6  # Hz
    F_c = 1575e6  # Hz

    t = np.linspace(0, numseconds, int(numseconds * (F_brf_sample)))

    s0 = [np.cos(2 * np.pi * F_c * x) for x in t]
    s1 = [np.cos((2 * np.pi * F_c * x) + np.pi / 2) for x in t]
    signal = []

    s0_shifted = [np.cos((2 * np.pi * F_c * x) + phi) for x in t]
    s1_shifted = [np.cos((2 * np.pi * F_c * x) + np.pi / 2 + phi) for x in t]
    shifted_signal = []

    i = 0
    for bit in bits:
        if bit == 1:
            for _ in range(int(numseconds * F_brf_sample) // numbits):
                signal.append(s1[i])
                shifted_signal.append(s1_shifted[i])
                i += 1
        else:
            for _ in range(int(numseconds * F_brf_sample) // numbits):
                signal.append(s0[i])
                shifted_signal.append(s0_shifted[i])
                i += 1

    return np.array(signal), np.array(shifted_signal)


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


# params:
#   none
# return:
#   phase_shift_table: dictionary of expected phase shifts for 2x2 antenna array for every angle in our range
#       indexed as (elevation angle, azimuth angle)
def makeLookupTable():
    phase_shift_table = {}
    # calculate phase shift for each antenna, using antenna 1 as a reference
    for elevation_angle in range(0, 27, 2):  # elevation angles
        for azim_angle in range(0, 360, 2):  # azimuth angles
            az_angle = np.deg2rad(azim_angle)
            elev_angle = np.deg2rad(elevation_angle)
            d2 = d * np.cos(az_angle)
            p2 = ((2 * np.pi * d2) / wavelength) * np.sin(elev_angle)
            d3 = d * np.sin(az_angle)
            p3 = ((2 * np.pi * d3) / wavelength) * np.sin(elev_angle)
            d4 = d * np.sqrt(2) * np.sin(az_angle + np.pi / 4)
            p4 = ((2 * np.pi * d4) / wavelength) * np.sin(elev_angle)
            phase_shift_table[elevation_angle, azim_angle] = [round(p2, 3), round(p3, 3), round(p4, 3)]
    return phase_shift_table


def find_nearest_index(array, value):
    diffs = []
    for i in range(0, len(array)):
        # diff = 0
        # diff = [diff + np.abs(array[i][j] - value[j]) for j in range(len(value))]
        diff = np.abs(array[i][0] - value[0]) + np.abs(array[i][1] - value[1]) + np.abs(array[i][2] - value[2])
        diffs.append(diff)
    return diffs.index(min(diffs))


def calc_phase_shift(sig1, sig2):
    sum_vector = [sig1[i] + sig2[i] for i in range(len(sig1))]
    diff_vector = [sig1[i] - sig2[i] for i in range(len(sig1))]
    sum_avg = np.mean(sum_vector)
    diff_avg = np.mean(diff_vector)
    r = diff_avg / sum_avg
    phase = 2 * np.arctan(-np.imag(r))

    return phase


def calc_AoA(signals, lookup_table):
    # split up dictionary into angles and phases
    angle_list = list(lookup_table.keys())
    phase_list = list(lookup_table.values())
    # calculate phase shifts
    phase12 = calc_phase_shift(signals[0], signals[1])
    phase13 = calc_phase_shift(signals[0], signals[2])
    phase14 = calc_phase_shift(signals[0], signals[3])
    position = find_nearest_index(phase_list, [round(phase12, 3), round(phase13, 3), round(phase14, 3)])
    return angle_list[position]


def gen_shifted_signals(sig1, azimuth, elevation):
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




# configuration:
# 1  2
# 3  4
wavelength = 1
d = wavelength / 2
lookup_table = makeLookupTable()

sig1 = makeGPSSignal(22, 30)
signals = gen_shifted_signals(sig1, elevation=10, azimuth=15)
print("Lookup table: " + str(calc_AoA(signals, lookup_table)))
a1, a2 = calc_AoA_monopulse(signals)
print("Monopulse: (" + str(a2) + ", " + str(a1) + ")")

