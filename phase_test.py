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


t = np.arange(0,np.pi, 1/30000)

freq = 2 # in Hz
phi = np.pi / 8
amp = 1
k = 2*np.pi*freq*t + phi

cwv = amp * np.exp(-1j* k) # complex sine wave

fig, ax = plt.subplots(2,1, figsize=(8,4), sharex=True)
ax[0].plot(t, np.real(cwv), lw=1.5)
ax[0].plot(t, np.imag(cwv), lw=0.5, color='orange')
ax[0].set_title('real (cosine)', color='C0')

ax[1].plot(t, np.imag(cwv), color='orange', lw=1.5)
ax[1].plot(t, np.real(cwv), lw=0.5, color='C0')
ax[1].set_title('imaginary (sine)', color='orange')

for myax in ax:
    myax.set_yticks(range(-2,2,1))
    myax.set_xlabel('Time (sec)')
    myax.set_ylabel('Amplitude (AU)')

plt.show()

# t = np.arange(0, 10, 0.1)
# wave = np.sin(2 * np.pi * t)
# # wave = (np.exp(1j * t) - np.exp(-1j * t)) / (2 * 1j)
# phase2 = 2
# freq = 1
# wave2 = np.abs(wave) * np.exp(1j * 2 * np.pi * freq * t)
# wave2_angle = np.angle(wave2)
# wave2_plot = np.sin(wave2_angle)
#
# wave2_shift = [np.abs(wave[i]) * np.exp(1j * phase2) for i in range(len(wave))]
# wave2_shift_angle = np.angle(wave2_shift)
# wave2_shift_plot = np.sin(wave2_shift_angle)
#
# freq = 0.5
# wave3 = np.abs(wave) * np.exp(1j * 2 * np.pi * freq * t)
# wave3_angle = np.angle(wave3)
# wave3_plot = np.sin(wave3_angle)
#
#
# p2 = calc_phase_shift(wave, wave2)
# print("Phase shift between wave 1 and wave 2: " + str(np.rad2deg(p2)))
# p3 = calc_phase_shift(wave, wave3)
# print("Phase shift between wave 1 and wave 3: " + str(np.rad2deg(p3)))
# p4 = calc_phase_shift(wave2, wave3)
# print("Phase shift between wave 2 and wave 3: " + str(np.rad2deg(p4)))
#
# fig, ax = plt.subplots(3)
# ax[0].plot(t, wave)
# # ax[0].plot(t, np.imag(wave))
# # ax[1].plot(t, np.real(wave2))
# # ax[1].plot(t, np.imag(wave2))
# ax[1].plot(t, np.real(wave2_plot))
# # ax[1].plot(t, np.real(wave2_shift_plot))
# # ax[1].plot(t, np.imag(wave2_plot))
# ax[2].plot(t, np.real(wave3_plot))
# # ax[2].plot(t, np.imag(wave3))
# # plt.plot(t, wave2)
# # plt.plot(t, wave3)
# plt.show()