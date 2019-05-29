from AudioSignal import *
from scipy.io import wavfile
import numpy as np


class DSBSC(object):
    __modulated_signals = {}
    __channel = np.zeros(0)
    __sample_rate = 0

    def __init__(self, fc, signal):
        """
        Modulates a message signal using AM DSB-SC and adds it to the channel

        Parameters
        ----------
        :type fc: float
        :type signal: AudioSignal
        """

        length = signal.__len__()
        carrier = np.cos(2 * np.pi * fc * np.arange(length) / signal.get_sample_rate())
        modulated = carrier * signal
        self.__modulated_signals[fc] = modulated

        if len(self.__channel) < length:
            self.__channel = np.zeros(length)

        sr = signal.get_sample_rate()
        if self.__sample_rate != sr:
            import os
            if not os.path.isdir('./temp'):
                os.mkdir('temp')

            if self.__sample_rate < sr:
                self.__sample_rate = sr
                for fc in self.__modulated_signals:
                    wavfile.write("./temp/" + str(fc) + ".wav", sr,
                                  np.asarray(self.__modulated_signals[fc], dtype=np.int16))
                    fs, self.__modulated_signals[fc] = wavfile.read("./temp/" + str(fc) + ".wav")
            else:
                wavfile.write("./temp/" + str(fc) + ".wav", self.__sample_rate, np.asarray(modulated, dtype=np.int16))
                fs, self.__modulated_signals[fc] = wavfile.read("./temp/" + str(fc) + ".wav")

            import shutil
            shutil.rmtree("./temp")

        for signal in self.__modulated_signals:
            self.__channel += signal

        wavfile.write("FDMA.wav", self.__sample_rate, np.asarray(self.__channel, dtype=np.int16))

    def demodulate(self, fc):
        """
        Return a demodulated signal from the channel using the frequency of its carrier fc

        Parameters
        ----------
        :type fc: float
        """

        ft_channel = fftshift(fft(self.__channel))
        bandwidth = len(self.__modulated_signals[fc]) / self.__sample_rate
        filtered = ifftshift(ifft(bpf(ft_channel, fc, bandwidth)))
        demodulated = fftshift(fft(filtered * np.cos(2 * np.pi * fc * np.arange(bandwidth) / self.__sample_rate)))

        return ifftshift(ifft(lpf(demodulated, bandwidth)))
