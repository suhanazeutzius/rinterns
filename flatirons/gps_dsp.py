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
#   corr0        : correlation coefficient vector when   [numpy array of type float]
#                  data bit = 0
#   corr1        : correlation coefficient vector when   [numpy array of type float]
#                  data bit = 1
def correlateWithGPS(prn, signal, signal_name, freq=None, sample_rate=None, plot=False):
    # Generate expected C/A code for provided prn number for both data bits
    ca0 = makeGPSClean(prn, 0, sample_rate=sample_rate)
    ca1 = makeGPSClean(prn, 1, sample_rate=sample_rate)
    #ca1 = ca1[0:int(len(ca1)/2)]

    # Perform correlation
    corr0 = np.abs(scipy.signal.correlate(ca0, signal))
    corr1 = np.abs(scipy.signal.correlate(ca1, signal))
    
    # Plot results
    if plot:
        fig, ax = plt.subplots(2,1)
        ax[0].plot(corr0)
        ax[1].plot(corr1)
        ax[0].grid(True)
        ax[1].grid(True)
        ax[0].set_ylabel('Data Bit = 0')
        ax[1].set_ylabel('Data Bit = 1')
        if freq is not None:
            fig.suptitle('Correlation of C/A ' + str(prn) + ' and ' + signal_name + ' with Fdoppler = ' + str(freq) + ' Hz')
        else:
            fig.suptitle('Correlation of C/A ' + str(prn) + ' and ' + signal_name)
        plt.show()

    # Return correlation results
    return [corr0, corr1]

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
#   signal      : signal that is being correlated  [numpy array of type np.complex_]
#   fsample     : sampling rate of signal in Hz                              [float]
#   signal_name : signal name (for plotting)                                [string]
#   fdoppler    : maximum possible doppler shift in Hz                       [float]
#   freq_step   : frequency step size for correlation algorithm in Hz        [float]
#   prns        : prns to test in correlation algorithm           [list of type int]
#   freq_range  : optional argument to overwrite range of       [list of type float]
#                 frequencies to test (Hz)
#   plot        : parameter controlling whether to display individual          [T/F]
#                  correlation plots
#
# Outputs:
#   corr0_max   : DEPRECATED
#   corr1_max   : DEPRECATED
def correlateSignal(signal, fsample, signal_name, fdoppler, freq_step, prns=range(1,32), freq_range=None, plot=False):
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

    fig, ax = plt.subplots(2, 1, sharex=True)
    # Iterate over all prns
    for prn in prns:
        # Instantiate empty vectors
        corr0_max = []
        corr1_max = []
        
        # Iterate over all frequencies
        for freq in freq_range:
            # Shift signal by frequency
            t = np.linspace(0, len(signal)/fsample, num=len(signal), endpoint=False)
            signal_shifted = signal * np.exp(-1j*2*np.pi*freq*t)

            # Correlate signal with C/A code corresponding to current prn
            corr0, corr1 = correlateWithGPS(prn, signal_shifted, signal_name, freq=freq, sample_rate=sample_rate, plot=plot)
            
            # Save max correlation coefficients
            corr0_max.append(corr0.max())
            corr1_max.append(corr1.max())

        # Plot results for current prn
        ax[0].plot(freq_range, corr0_max, '.--', label=str(prn))
        ax[1].plot(freq_range, corr1_max, '.--', label=str(prn))

    # Finish up plotting
    ax[0].grid(True)
    ax[1].grid(True)
    ax[0].legend()
    ax[1].legend()
    ax[1].set_xlabel('Doppler Frequency Shift')
    ax[0].set_ylabel('Data Bit = 0')
    ax[1].set_ylabel('Data Bit = 1')
    fig.suptitle('Max Correlation Coefficients Versus Doppler Frequency Shift For Selected PRNs')
    plt.show()
    
    # Return results
    return [corr0_max, corr1_max]

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
    plt.show()
