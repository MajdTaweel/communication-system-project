from AudioSignal import *
from scipy.io import wavfile
import numpy as np
import librosa


class DSBSC(object):
    def __init__(self):
        self.__modulating_signals = {}
        self.bandwidths = {}
        self.__channel = np.zeros(0, dtype=np.complex128)
        self.__sample_rate = 0

    def modulate(self, fc, signal, bandwidth):
        """
        Modulates a message signal using AM DSB-SC FDMA

        Parameters
        ----------
        :type fc: float
        :type signal: AudioSignal
        :type bandwidth: float
        :return None
        """

        self.bandwidths[fc] = bandwidth
        sr = signal.get_sample_rate()
        if self.__sample_rate != sr:
            if self.__sample_rate < sr:
                self.__sample_rate = sr
                for fc_temp in self.__modulating_signals:
                    signal_temp, fs = librosa.load(self.__modulating_signals[fc_temp].get_filename() + ".wav", sr=sr)
                    self.__modulating_signals[fc_temp].set_sample_rate(fs)
                    self.__modulating_signals[fc_temp].set_amplitudes(signal_temp)

                self.__modulating_signals[fc] = signal

            else:
                self.__modulating_signals[fc] = signal
                signal_temp, fs = librosa.load(self.__modulating_signals[fc].get_filename() + ".wav",
                                               sr=self.__sample_rate)
                self.__modulating_signals[fc].set_sample_rate(fs)
                self.__modulating_signals[fc].set_amplitudes(signal_temp)
        else:
            self.__modulating_signals[fc] = signal

        length = len(self.__channel)
        for longest in self.__modulating_signals.values():
            if length < longest.__len__():
                length = longest.__len__()
        self.__channel = np.zeros(length, dtype=np.complex128)

        for key in self.__modulating_signals:
            modulating = self.__modulating_signals[key]
            carrier = np.cos(
                2.0 * np.pi * key * np.arange(self.__modulating_signals[key].__len__()) / self.__sample_rate)
            modulated = carrier * modulating.get_amplitudes()
            for i in range(len(modulated)):
                self.__channel[i] += modulated[i]   # Addition is not working! Weird!!!

        wavfile.write("FDMA.wav", self.__sample_rate, np.asarray(self.__channel, dtype=np.int16))

    def demodulate(self, fc):
        """
        Return a demodulated signal from the channel using the frequency of its carrier fc

        Parameters
        ----------
        :type fc: float
        :return np.core.ndarray
        """

        ratio = self.__modulating_signals[fc].__len__() / self.__modulating_signals[fc].get_sample_rate()
        ft_channel = fftshift(fft(self.__channel))
        frequency = fc * ratio
        bandwidth = self.bandwidths[fc] * ratio
        filtered = ifft(ifftshift(bpf(ft_channel, frequency, bandwidth)))
        demodulated = fftshift(fft(filtered * np.cos(
            2.0 * np.pi * fc * np.arange(self.__modulating_signals[fc].__len__()) / self.__modulating_signals[
                fc].get_sample_rate())))

        return ifft(ifftshift(lpf(demodulated, bandwidth)))

    def get_modulating_signals(self):
        return self.__modulating_signals

    def get_channel(self):
        return self.__channel

    def get_sample_rate(self):
        return self.__sample_rate
