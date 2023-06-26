# Import required python packages
import numpy as np
import scipy.signal
import matplotlib.pyplot as plt

# Import custom packages
from flatirons.gps_gen import *

# correlateWithGPS() correlates an input signal with a GPS C/A code determined by 
# the provided prn number
#
# Inputs:
#   prn          : prn number of the satellite, between 1 and 31               [int]
#   signal       : signal that is being correlated [numpy array of type np.complex_]
#                  against C/A code for provided prn
#   sample_ratio : ratio of SDR sampling rate to GPS chip rate (fsample/fchip) [int]
#   signal_name  : name of the signal (for plotting)                        [string]
#
# Outputs:
#   corr0        : correlation coefficient vector when   [numpy array of type float]
#                  data bit = 0
#   corr1        : correlation coefficient vector when   [numpy array of type float]
#                  data bit = 1
def correlateWithGPS(prn, signal, sample_ratio, signal_name, plot=False):
    # Generate expected C/A code for provided prn number for both data bits
    ca0 = makeGPSClean(prn, 0,  sample_ratio, num_periods=10)
    #ca0 = ca0[0:int(len(ca0)/2)]
    ca1 = makeGPSClean(prn, 1,  sample_ratio, num_periods=10)
    #ca1 = ca1[0:int(len(ca1)/2)]

    # Perform correlation
    corr0 = scipy.signal.correlate(ca0, signal)
    corr1 = scipy.signal.correlate(ca1, signal)
    
    # Plot results
    if plot:
        fig, ax = plt.subplots(2,1)
        ax[0].plot(corr0)
        ax[1].plot(corr1)
        ax[0].grid(True)
        ax[1].grid(True)
        ax[0].set_ylabel('Data Bit = 0')
        ax[1].set_ylabel('Data Bit = 1')
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
def tuneSignal(fcenter_SDR, fsample, signal, filter_bandwidth=0.5e6):
    # Define GPS frequency
    fGPS = 1575.42e6 # [Hz] 

    # Calculate current offset of GPS data
    offset = (fGPS-fcenter_SDR) # [Hz]

    # Downshift signal to be centered at 0 Hz
    signal = signal * np.exp(-(1j*2*np.pi*offset))

    # Pass filter through lowpass filter
    signal = filterSignal(0, fsample, signal, ['butter', 'lowpass'], bandwidth=filter_bandwidth, order=3)

    # Return signal
    return signal

def correlateSignal(signal, fsample, signal_name, prns=range(1,32), plot=False):
    # Instantiate empty vectors
    corr0_ratio = []
    corr1_ratio = []

    # Calculate ratio of SDR sampling rate to GPS chip rate
    sample_ratio = int(fsample/(1.023e6))

    # Iterate over all prns
    for prn in prns:
        # Correlate signal with C/A code corresponding to current prn
        corr0, corr1 = correlateWithGPS(prn, signal, sample_ratio, signal_name, plot=plot)
    
        # Save max correlation coefficients
        corr0_ratio.append(corr0.max())
        #corr0_ratio.append(np.abs(np.real(corr0.max() / np.median(corr0))))
        corr1_ratio.append(corr1.max())
        #corr1_ratio.append(np.abs(np.real(corr1.max() / np.median(corr1))))

    # Calculate max max/median ratio
    max_ratio = max([max(corr0_ratio), max(corr1_ratio)])

    # Plot results
    barWidth = 0.33
    br0 = np.arange(len(corr0_ratio))
    br1 = [x + barWidth for x in br0]
    plt.bar(br0, corr0_ratio, width=barWidth, label='Data Bit = 0')
    plt.text(1, max_ratio+(max_ratio/100), 'Maximum Correlation = ' + str(round(max_ratio,1)))
    plt.bar(br1, corr1_ratio, width=barWidth, label='Data Bit = 1')
    plt.axhline(y=max_ratio, color='k', linestyle='--')
    plt.xlabel('PRN')
    plt.ylabel('Maximum Correlation Coefficient')
    plt.title('Correlation Between ' + signal_name + ' and Various PRNs')
    plt.xticks([r+(barWidth/2) for r in range(len(corr0_ratio))], [str(prn) for prn in prns])
    plt.legend()
    plt.show()
    
    # Return results
    return [corr0_ratio, corr1_ratio]

# visualizeGPS() visualizes an input GPS signal
#
# Inputs:
#   signal      : signal to visaluze               [numpy array of type np.complex_]
#   fcenter     : center frequency of signal in Hz (for FFT)                 [float]
#   fsample     : sampling rate of the SDR in Hz                             [float]
#   signal_name : name of the signal (for plotting)                         [string]
#
# Outputs: None
def visualizeGPS(signal, fcenter, fsample, signal_name):
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