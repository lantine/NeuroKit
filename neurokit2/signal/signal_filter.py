# -*- coding: utf-8 -*-
import numpy as np
import scipy.signal


def signal_filter(signal, sampling_rate=1000, lowcut=None, highcut=None, method="butterworth", order=2, window_length="default"):
    """Filter a signal using 'butterworth', 'fir' or 'savgol' filters.

    Apply a lowpass (if 'highcut' frequency is provided), highpass (if 'lowcut' frequency is provided) or bandpass (if both are provided) filter to the signal.

    Parameters
    ----------
    signal : list, array or Series
        The signal channel in the form of a vector of values.
        or "bandstop".
    sampling_rate : int
        The sampling frequency of the signal (in Hz, i.e., samples/second).
    lowcut : float
        Lower cutoff frequency in Hz. The default is None.
    highcut : float
        Upper cutoff frequency in Hz. The default is None.
    method : str
        Can be one of 'butterworth', 'fir', 'bessel' or 'savgol'. Note that for Butterworth, the function uses the SOS method from `scipy.signal.sosfiltfilt`, recommended for general purpose filtering. One can also specify "butterworth_ba' for a more traditional and legacy method (often implemented in other software).
    order : int
        Only used if method is 'butterworth' or 'savgol'. Order of the filter (default is 2).
    window_length : int
        Only used if method is 'savgol'. The length of the filter window (i.e. the number of coefficients). Must be an odd integer. If 'default', will be set to the sampling rate divided by 10 (101 if the sampling rate is 1000 Hz).

    See Also
    --------
    signal_detrend, signal_psd

    Returns
    -------
    array
        Vector containing the filtered signal.

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import neurokit2 as nk
    >>>
    >>> signal = nk.signal_simulate(duration=10, frequency=0.5) # Low freq
    >>> signal += nk.signal_simulate(duration=10, frequency=5) # High freq
    >>>
    >>> # Lowpass
    >>> pd.DataFrame({"Raw": signal,
                      "Butter_2": nk.signal_filter(signal, highcut=3, method='butterworth', order=2),
                      "Butter_2_BA": nk.signal_filter(signal, highcut=3, method='butterworth_ba', order=2),
                      "Butter_5": nk.signal_filter(signal, highcut=3, method='butterworth', order=5),
                      "Butter_5_BA": nk.signal_filter(signal, highcut=3, method='butterworth_ba', order=5),
                      "Bessel_2": nk.signal_filter(signal, highcut=3, method='bessel', order=2),
                      "Bessel_5": nk.signal_filter(signal, highcut=3, method='bessel', order=5),
                      "FIR": nk.signal_filter(signal, highcut=3, method='fir')}).plot(subplots=True)

    >>> # Highpass
    >>> pd.DataFrame({"Raw": signal,
                      "Butter_2": nk.signal_filter(signal, lowcut=2, method='butterworth', order=2),
                      "Butter_2_ba": nk.signal_filter(signal, lowcut=2, method='butterworth_ba', order=2),
                      "Butter_5": nk.signal_filter(signal, lowcut=2, method='butterworth', order=5),
                      "Butter_5_BA": nk.signal_filter(signal, lowcut=2, method='butterworth_ba', order=5),
                      "Bessel_2": nk.signal_filter(signal, lowcut=2, method='bessel', order=2),
                      "Bessel_5": nk.signal_filter(signal, lowcut=2, method='bessel', order=5),
                      "FIR": nk.signal_filter(signal, lowcut=2, method='fir')}).plot(subplots=True)

    >>> # Bandpass in real-life scenarios
    >>> original = nk.rsp_simulate(duration=30, method="breathmetrics", noise=0)
    >>> signal = nk.signal_distord(original, noise_frequency=[0.1, 2, 10, 1000], noise_amplitude=1, powerline_amplitude=1)
    >>>
    >>> # Bandpass between 10 and 30 breaths per minute (respiratory rate range)
    >>> pd.DataFrame({"Raw": signal,
                      "Butter_2": nk.signal_filter(signal, lowcut=10/60, highcut=30/60, method='butterworth', order=2),
                      "Butter_2_BA": nk.signal_filter(signal, lowcut=10/60, highcut=30/60, method='butterworth_ba', order=2),
                      "Butter_5": nk.signal_filter(signal, lowcut=10/60, highcut=30/60, method='butterworth', order=5),
                      "Butter_5_BA": nk.signal_filter(signal, lowcut=10/60, highcut=30/60, method='butterworth_ba', order=5),
                      "Bessel_2": nk.signal_filter(signal, lowcut=10/60, highcut=30/60, method='bessel', order=2),
                      "Bessel_5": nk.signal_filter(signal, lowcut=10/60, highcut=30/60, method='bessel', order=5),
                      "FIR": nk.signal_filter(signal, lowcut=10/60, highcut=30/60, method='fir'),
                      "Savgol": nk.signal_filter(signal, method='savgol')}).plot(subplots=True)
    """
    method = method.lower()

    # Sanity checks
    if method != "powerline":
        if lowcut is None and highcut is None:
            return signal

    if method in ["sg", "savgol", "savitzky-golay"]:
        filtered = _signal_filter_savgol(signal, sampling_rate, order, window_length=window_length)
    else:
        if method in ["butter", "butterworth"]:
            filtered = _signal_filter_butterworth(signal, sampling_rate, lowcut, highcut, order)
        elif method in ["butter_ba", "butterworth_ba"]:
            filtered = _signal_filter_butterworth_ba(signal, sampling_rate, lowcut, highcut, order)
        elif method in ["bessel"]:
            filtered = _signal_filter_bessel(signal, sampling_rate, lowcut, highcut, order)
        elif method in ["fir"]:
            filtered = _signal_filter_fir(signal, sampling_rate, lowcut, highcut, window_length=window_length)
        elif method in ["powerline"]:
            filtered = _signal_filter_powerline(signal, sampling_rate)
        else:
            raise ValueError("NeuroKit error: signal_filter(): 'method' should be "
                             "one of 'butterworth', 'butterworth_ba', 'bessel',"
                             " 'savgol' or 'fir'.")
    return filtered


# =============================================================================
# Savitzky-Golay (savgol)
# =============================================================================

def _signal_filter_savgol(signal, sampling_rate=1000, order=2, window_length="default"):
    """Filter a signal using the Savitzky-Golay method.

    Default window size is chosen based on `Sadeghi, M., & Behnia, F. (2018). Optimum window length of Savitzky-Golay filters with arbitrary order. arXiv preprint arXiv:1808.10489. <https://arxiv.org/ftp/arxiv/papers/1808/1808.10489.pdf>`_.
    """
    window_length = _signal_filter_windowlength(window_length=window_length, sampling_rate=sampling_rate)

    filtered = scipy.signal.savgol_filter(signal, window_length=window_length, polyorder=order)
    return filtered

# =============================================================================
# FIR
# =============================================================================
def _signal_filter_fir(signal, sampling_rate=1000, lowcut=None, highcut=None, window_length="default"):
    """Filter a signal using a FIR filter.
    """
    try:
        import mne
    except ImportError:
        raise ImportError("NeuroKit error: signal_filter(): the 'mne' "
                          "module is required for this method to run. ",
                          "Please install it first (`pip install mne`).")

    if isinstance(window_length, str):
        window_length = "auto"

    filtered = mne.filter.filter_data(
            signal,
            sfreq=sampling_rate,
            l_freq=lowcut,
            h_freq=highcut,
            method='fir',
            fir_window='hamming',
            filter_length=window_length,
            l_trans_bandwidth='auto',
            h_trans_bandwidth='auto',
            phase='zero-double',
            fir_design='firwin',
            pad='reflect_limited',
            verbose=False)
    return filtered


# =============================================================================
# Butterworth
# =============================================================================

def _signal_filter_butterworth(signal, sampling_rate=1000, lowcut=None, highcut=None, order=5):
    """Filter a signal using IIR Butterworth SOS method.
    """
    freqs, filter_type = _signal_filter_sanitize(lowcut=lowcut, highcut=highcut, sampling_rate=sampling_rate)

    sos = scipy.signal.butter(order, freqs, btype=filter_type, output='sos', fs=sampling_rate)
    filtered = scipy.signal.sosfiltfilt(sos, signal)
    return filtered


def _signal_filter_butterworth_ba(signal, sampling_rate=1000, lowcut=None, highcut=None, order=5):
    """Filter a signal using IIR Butterworth B/A method.
    """
    # Get coefficients
    freqs, filter_type = _signal_filter_sanitize(lowcut=lowcut, highcut=highcut, sampling_rate=sampling_rate)

    b, a = scipy.signal.butter(order, freqs, btype=filter_type, output='ba', fs=sampling_rate)
    try:
        filtered = scipy.signal.filtfilt(b, a, signal, method="gust")
    except ValueError:
        filtered = scipy.signal.filtfilt(b, a, signal, method="pad")

    return filtered


# =============================================================================
# Bessel
# =============================================================================

def _signal_filter_bessel(signal, sampling_rate=1000, lowcut=None, highcut=None, order=5):
    freqs, filter_type = _signal_filter_sanitize(lowcut=lowcut, highcut=highcut, sampling_rate=sampling_rate)

    sos = scipy.signal.bessel(order, freqs, btype=filter_type, output='sos', fs=sampling_rate)
    filtered = scipy.signal.sosfiltfilt(sos, signal)
    return filtered

# =============================================================================
# Poweline
# =============================================================================

def _signal_filter_powerline(signal, sampling_rate):
    """This is a way of smoothing out 50Hz power-line noise from the signal as
    implemented in BioSPPy. Effectively a notch filter."""
    b = np.ones(int(0.02 * sampling_rate)) / 50.
    a = [1]
    y = scipy.signal.filtfilt(b, a, signal, method="pad")
    return y


# =============================================================================
# Utility
# =============================================================================
def _signal_filter_sanitize(lowcut=None, highcut=None, sampling_rate=1000, normalize=False):

    # Sanity checks
    if isinstance(highcut, int):
        if sampling_rate <= 2 * highcut:
            print("NeuroKit warning: the sampling rate is too low. Sampling rate"
                  " must exceed the Nyquist rate to avoid aliasing problem. "
                  "In this analysis, the sampling rate has to be higher than",
                  2 * highcut, "Hz.")

    # Replace 0 by none
    if lowcut is not None and lowcut == 0:
        lowcut = None
    if highcut is not None and highcut == 0:
        highcut = None

    # Format
    if lowcut is not None and highcut is not None:
        if lowcut > highcut:
            filter_type = "bandstop"
        else:
            filter_type = "bandpass"
        freqs = [lowcut, highcut]
    elif lowcut is not None:
        freqs = [lowcut]
        filter_type = "highpass"
    elif highcut is not None:
        freqs = [highcut]
        filter_type = "lowpass"

    # Normalize frequency to Nyquist Frequency (Fs/2).
    # However, no need to normalize if `fs` argument is provided to the scipy filter
    if normalize is True:
        freqs = np.array(freqs) / (sampling_rate / 2)

    return freqs, filter_type


def _signal_filter_windowlength(window_length="default", sampling_rate=1000):
    if isinstance(window_length, str):
        window_length = int(np.round(sampling_rate/3))
        if (window_length % 2) == 0:
            window_length + 1
    return window_length
