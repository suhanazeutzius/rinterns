import numpy as np
import matplotlib.pyplot as plt



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
    samplesPerCode = round(sample_rate / (1.023e6 / 1023))
    ts = 1 / sample_rate  # Sampling period
    tc = 1 / 1.023e6  # Code period

    ca_code = cacode(prn)
    codevalueind = np.ceil(ts * np.arange(1, samplesPerCode + 1) / tc).astype(int) - 1
    codevalueind[-1] = 1022  # fix last index
    return ca_code[codevalueind]



def makeGPSClean(prn, num_periods=1, sample_rate=None):
    # Generate PRN (C/A) code
    signal = cacode(prn, sample_rate=sample_rate)

    # Tile signal
    signal = np.tile(signal, num_periods)

    # Return signal
    return signal



def makeGPSNoisy(signal, noise_power_AWGN, noise_power_phase=0):
    # Add complex AWGN noise
    n = (np.random.randn(len(signal)) + 1j*np.random.randn(len(signal)))*np.sqrt(noise_power_AWGN/2)
    signal = signal + n
     
    # Add phase noise
    p = np.random.randn(len(signal)) * noise_power_phase
    signal_after = signal * np.exp(1j*p)

    # Return noisy signal
    return signal
