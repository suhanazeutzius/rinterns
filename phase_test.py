import numpy as np
import math
import matplotlib.pyplot as plt


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


t = np.arange(0, 20, 0.1)
wave = np.sin(t)
wave2 = wave * np.exp(1j * np.pi/4)
wave3 = wave * np.exp(1j * np.pi/2)

p2 = calc_phase_shift(wave, wave2)
print("Phase shift between wave 1 and wave 2: " + str(np.rad2deg(p2)))
p3 = calc_phase_shift(wave, wave3)
print("Phase shift between wave 1 and wave 3: " + str(np.rad2deg(p3)))
p4 = calc_phase_shift(wave2, wave3)
print("Phase shift between wave 2 and wave 3: " + str(np.rad2deg(p4)))

plt.plot(t, wave)
plt.plot(t, wave2)
plt.plot(t, wave3)
plt.show()