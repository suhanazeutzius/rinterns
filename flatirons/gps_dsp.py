# Import required python packages
import numpy as np
import scipy.signal
import matplotlib.pyplot as plt
import math

# Import custom packages
from flatirons.gps_gen import *

# correlateWithGPS() correlates an input signal with a GPS C/A code determined by 
# the provided prn number
#
# Inputs:
#   prn          : prn number of the satellite, between 1 and 31               [int]
#   signal       : signal that is being correlated [numpy array of type np.complex_]
#                  against C/A code for provided prn
#   signal_name  : name of the signal (for plotting)                        [string]
#   freq         : frequency shift of the signal in Hz                       [float]
#   sample_rate  : sampling rate of the signal in Hz                         [float]
#   plot         : parameter controlling whether to display individual         [T/F]
#                  correlation plots
#
# Outputs:
#   corr         : correlation coefficient vector     [numpy array of type complex_]
def correlateWithGPS(prn, signal, signal_name, freq=None, sample_rate=None, plot=False):
    # Generate expected C/A code for provided prn number for both data bits
    ca = makeGPSClean(prn, num_periods=20, sample_rate=sample_rate)

    # Perform correlation
    corr = scipy.signal.correlate(ca, signal)

    # Create shift vector
    max_shift = int((len(ca)+len(signal)-2)/2)
    shift = np.arange(-max_shift, max_shift+1)
    
    # Plot results
    if plot:
        fig, ax = plt.subplots()
        ax.plot(shift, corr)
        ax.grid(True)
        ax.set_ylabel('Correlation Coefficient')
        ax.set_xlabel('Shift')
        if freq is not None:
            fig.suptitle('C/A = ' + str(prn) + ' and Fdoppler = ' + str(freq) + ' Hz')
        else:
            fig.suptitle('Correlation of C/A ' + str(prn) + ' and ' + signal_name)
        # this plots the vector positively and negatively index shifted
        plt.show()

    # Return correlation results
    return corr

# filterSignal() applies a filter to an input signal
#
# Inputs:
#   fcenter     : filter center frequency in Hz                              [float]
#   fsample     : sampling rate in Hz                                        [float]
#   signal      : signal that is being filtered    [numpy array of type np.complex_]
#   filter_type : two element array, specifies filter type    [array of type string]
#                   0 --> 'fir' (FIR)  or 'butter' (butterworth)
#                   1 --> 'lowpass' or 'bandpass'
#   bandwidth   : bandwidth of filter in Hz                                  [float]
#   order       : order of filter                                              [int]
#
# Outputs:
#   signal      : filtered signal                  [numpy array of type np.complex_]
def filterSignal(fcenter, fsample, signal, filter_type, bandwidth=2e6, order=4):
    # Detect type of filter
    if filter_type[1] == 'lowpass':
        if filter_type[0] == 'fir':
            # Create FIR lowpass filter
            FIR_filter = scipy.signal.firwin(order+1, bandwidth, fs=fsample)

            # Apply filter to signal
            signal = np.convolve(signal, FIR_filter, 'valid')
        elif filter_type[0] == 'butter':
            # Create butterworth filter coefficients
            b, a = scipy.signal.butter(order, bandwidth, btype='lowpass', fs=fsample)
            
            # Apply filter to signal
            signal = scipy.signal.filtfilt(b, a, signal)
    elif filter_type[1] == 'bandpass':
        if filter_type[0] == 'fir':
            # Create FIR bandpass filter
            FIR_filter = scipy.signal.firwin(order+1, [fcenter-(bandwidth/2), fcenter+(bandwidth/2)], fs=fsample, pass_zero=False)

            # Apply filter to signal
            signal = np.convolve(signal, FIR_filter, 'valid')
        elif filter_type[0] == 'butter':
            # Create butterworth filter coefficients
            b, a = scipy.signal.butter(order, [fcenter-(bandwidth/2), fcenter+(bandwidth/2)], btype='bandpass', fs=fsample)
            
            # Apply filter to signal
            signal = scipy.signal.filtfilt(b, a, signal)

    # Return filtered signal
    return signal

# tuneSignal() tunes a signal so the GPS signal band is centered at 0 Hz
#
# Inputs:
#   fcenter_SDR      : center frequency (in Hz) the SDR sampled at           [float]
#   fsample          : sampling rate (in Hz) of the SDR                      [float]
#   signal           : signal to tune              [numpy array of type np.complex_]
#   filter_bandwidth : bandwidth (Hz) for the lowpass filter used for tuning   [int]
#
# Outputs:
#   signal           : tuned signal                [numpy array of type np.complex_]
def tuneSignal(fshift, fsample, signal, filter_bandwidth=0.5e6):
    # Downshift signal to be centered at 0 Hz
    t = np.linspace(0, len(signal)/fsample, num=len(signal), endpoint=False)
    signal = signal * np.exp(-1j*2*np.pi*fshift*t)

    # Pass filter through lowpass filter
    signal = filterSignal(0, fsample, signal, ['butter', 'lowpass'], bandwidth=filter_bandwidth, order=3)

    # Return signal
    return signal

# correlateSignal() performs correlation analysis on a GPS signal
#
# Inputs:
#   signal              : signal that is being     [numpy array of type np.complex_]
#                         correlated
#   fsample             : sampling rate of signal in Hz                      [float]
#   signal_name         : signal name (for plotting)                        [string]
#   fdoppler            : maximum possible doppler shift in Hz               [float]
#   freq_step           : frequency step size for correlation algorithm (Hz) [float]
#   tracked_prn         : desired prn to color                                 [int]
#   prns                : prns to test in correlation algorithm   [list of type int]
#   freq_range          : optional argument to overwrite range  [list of type float]
#                         of frequencies to test (Hz)
#   plot...             : parameters controlling whether to display various    [T/F]
#                         plots
#
# Outputs:
#   prn                 : prn of signal with maximum correlation peak          [int]
#   fdoppler_correction : doppler frequency shift of signal with maximum     [float]
#                         correlation peak
def correlateSignal(signal, fsample, signal_name, fdoppler, freq_step, tracked_prn, prns=range(1,32), freq_range=None, plot_CAF=True, plot_each=False, plot_3D=False):
    # Define constants
    c = 299792458 # [m/s]
    fGPS = 1575.42e6 # [Hz]
    Rearth = 6378e3 # [m]
    hGPS = 20200e3 # [m]
    Vsat = 929 # [m/s]

    # Update sample_rate variable
    if fsample == 1.023e6:
        sample_rate = None
    else:
        sample_rate = fsample

    # Define doppler frequency shift range
    if freq_range is None:
        freq_range = np.arange(-fdoppler, fdoppler, freq_step)

    # Instantiate matrix to store maximum correlation values
    corr_max = np.zeros((len(prns),len(freq_range)))

    # Iterate over all prns
    for i, prn in enumerate(prns):
        # Instantiate matrix to store correlation values
        if plot_3D:
            N_shifts = (int(fsample/(1.023e6))*1023*2)+len(signal)-1
            corr_mat = np.zeros((len(freq_range), N_shifts))
        
        # Iterate over all frequencies
        for j, freq in enumerate(freq_range):
            # Shift signal by frequency
            t = np.linspace(0, len(signal)/fsample, num=len(signal), endpoint=False)
            signal_shifted = signal * np.exp(-1j*2*np.pi*freq*t)

            # Correlate signal with C/A code corresponding to current prn
            corr = correlateWithGPS(prn, signal_shifted, signal_name, freq=freq, sample_rate=sample_rate, plot=plot_each)
            corr = np.abs(corr)
 
            # Save correlation data
            if plot_3D:
                corr_mat[j,:] = corr
            corr_max[i,j] = corr.max()/np.median(corr)

        if plot_3D:
            # Plot results for current prn
            max_shift = int(math.floor((N_shifts-1)/2))
            if (N_shifts % 2) == 0:
                shifts = np.concatenate(np.arange(-max_shift, 1), np.arange(0, max_shift+1))
            else:
                shifts = np.arange(-max_shift, max_shift+1)
            X, Y = np.meshgrid(shifts[::1000], freq_range)
            fig2, ax2 = plt.subplots(subplot_kw={"projection": "3d"})
            ax2.plot_surface(X, Y, corr_mat[:,::1000])
            ax2.set_title('PRN = ' + str(prn))
            #plt.show()

    # Extract prn and doppler frequency shift correction corresponding to maximum peak
    prn_idx, fdoppler_correction_idx = np.where(corr_max == np.amax(np.amax(corr_max)))
    prn = prns[prn_idx[0]]
    fdoppler_correction = freq_range[fdoppler_correction_idx[0]]

    if plot_CAF:
        # Finish up plotting
        fig1, ax1 = plt.subplots(figsize=(8, 5))
        for i in np.arange(corr_max.shape[0]):
            if prns[i] == tracked_prn:
                ax1.plot(freq_range, corr_max[i,:], '.--', label=str(prns[i]), color='#774D77')
            else:
                ax1.plot(freq_range, corr_max[i,:], '.--', color='#A9A9A9')
        ax1.set_yscale('log')
        ax1.grid(True)
        ax1.legend()
        ax1.set_xlabel('Doppler Frequency Shift', fontsize=10)
        ax1.set_ylabel('Max/Median Ratio', fontsize=10)
        fig1.suptitle('Max/Median Ratio Versus Doppler Frequency Shift For Selected PRNs', fontsize=14)
        fig1.savefig('fig1.png')
        #plt.show()

    # Return results
    return prn, fdoppler_correction

# correlateForMonopulse() returns the correlation results required by the monopulse algorithm
#
# Inputs:
#   sig                 : GPS signal                  [numpy array of type complex_]
#   fsample             : sampling rate in Hz                                [float]
#   fdoppler_correction : doppler frequency shift of the signal in Hz        [float]
#   prn                 : PRN that is being tracked                            [int]
#   signal_name         : name of the signal                                [string]
#   plot                : parameter controlling whether to display             [T/F]
#                         individual correlation plots
#
# Returns:
#   corr                : correlation results         [numpy array of type complex_]
def correlateForMonopulse(sig, fsample, fdoppler, prn, signal_name, plot=False):
    # Update sample_rate variable
    if fsample == 1.023e6:
        sample_rate = None
    else:
        sample_rate = fsample
    
    # Shift signal by doppler shift frequency
    t = np.linspace(0, len(sig)/fsample, num=len(sig), endpoint=False)
    sig = sig * np.exp(-1j*2*np.pi*fdoppler*t)

    # Correlate signal with C/A code corresponding to tracked  prn
    corr = correlateWithGPS(prn, sig, signal_name, freq=fdoppler, sample_rate=sample_rate, plot=plot)

    # Return correlation results
    return corr


# trimSignal() removes the first part of a signanl
#
# Inputs:
#   sig         : signal to trim                      [numpy array of type complex_]
#   fsample     : sampling rate of signal in Hz                              [float]
#   trim_length : length of time to remove from signal in s                  [float]
#
# Outputs:
#   sig         : the trimmed signal
def trimSignal(sig, fsample, trim_length=2e-3):
    # Calculate number of samples to remove
    trim_samples = int(trim_length*fsample)

    # Trim signal
    sig = sig[trim_samples:]

    # Return trimmed signal
    return sig

# visualizeGPS() visualizes an input GPS signal
#
# Inputs:
#   signal      : signal to visaluze               [numpy array of type np.complex_]
#   fcenter     : center frequency of signal in Hz (for FFT)                 [float]
#   fsample     : sampling rate of the SDR in Hz                             [float]
#   signal_name : name of the signal (for plotting)                         [string]
#
# Outputs: None
def visualizeSignal(signal, fcenter, fsample, signal_name):
    # Graph PSD
    PSD = np.abs(np.fft.fft(signal))**2 / (len(signal)*(fsample))
    PSD = 10.0*np.log10(PSD)
    PSD = np.fft.fftshift(PSD)
    f = np.arange(fsample/-2.0, fsample/2.0, fsample/len(signal))
    f += fcenter
    fig1, ax1 = plt.subplots()
    ax1.plot(f, PSD)
    ax1.grid(True)
    ax1.set_xlabel('Frequency [Hz]')
    ax1.set_ylabel('PSD Magnitude [dB]')
    ax1.set_title('PSD of ' + signal_name) 

    # Plot IQ constellation
    fig2, ax2 = plt.subplots()
    ax2.hexbin(np.real(signal), np.imag(signal), bins='log', cmap='inferno')
    ax2.set_title('IQ Constellation of ' + signal_name)
    ax2.axis('square')

    # Plot time series
    dt = 1/fsample
    t = np.linspace(0, dt*(len(signal)-1), num=len(signal)) * (1e3)
    fig3, ax3 = plt.subplots(2, 1, sharex=True)
    ax3[0].plot(t,np.real(signal))
    ax3[0].grid(True)
    ax3[0].set_ylabel('I')
    ax3[1].plot(t,np.imag(signal))
    ax3[1].grid(True)
    ax3[1].set_ylabel('Q')
    ax3[1].set_xlabel('Time [ms]')
    fig3.suptitle('Time Behavior of ' + signal_name)

    # Display plots
    #plt.show()
