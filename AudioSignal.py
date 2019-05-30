from scipy.fftpack import *
import numpy as np


class AudioSignal:
    __count = 0

    def __init__(self, filename, sample_rate, amplitudes):
        self.__filename = filename
        self.__sample_rate = sample_rate
        if len(amplitudes.shape) == 2:
            amplitudes = (amplitudes.sum(axis=1) / 2)
        self.__amplitudes = amplitudes
        AudioSignal.__count += 1

    def get_filename(self):
        return self.__filename

    def get_sample_rate(self):
        return self.__sample_rate

    def get_amplitudes(self):
        return self.__amplitudes

    def set_amplitudes(self, amplitudes):
        self.__amplitudes = amplitudes

    def get_fourier_transform(self):
        return fftshift(fft(self.get_amplitudes()))

    def get_energy(self):
        return np.abs(self.get_fourier_transform()) ** 2

    @staticmethod
    def display_count():
        return AudioSignal.__count

    def __len__(self):
        return len(self.get_amplitudes())


def lpf(signal, bandwidth):
    """
    Return a base-band signal

    Parameters
    ----------
    :type signal: array_like
    :type bandwidth: float
    """

    length = len(signal)
    low_pass = np.linspace(-length // 2, length // 2, num=length)
    low_pass = np.where(abs(low_pass) <= bandwidth, 1, 0)

    return signal * low_pass


def bpf(signal, frequency, bandwidth):
    """
    Return a bandpass signal

    Parameters
    ----------
    :type signal: array_like
    :type frequency: float
    :type bandwidth: float
    """

    if len(signal.shape) == 2:
        signal = signal.sum(axis=1) / 2

    length = len(signal)
    band_pass = np.linspace(-length // 2, length // 2, num=length)
    band_pass = np.where(abs(band_pass) <= frequency + bandwidth or abs(band_pass) >= frequency - bandwidth, 1, 0)

    return signal * band_pass
