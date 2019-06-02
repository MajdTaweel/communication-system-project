from AudioSignal import *
from scipy.io import wavfile
import numpy as np
import librosa


class DSBSC(object):
    def __init__(self):
        self.__modulating_signals = {}
        self.__bandwidths = {}
        self.__channel = np.zeros(0, dtype=np.float64)
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

        self.__bandwidths[fc] = bandwidth
        self.__modulating_signals[fc] = signal
        sr = signal.get_sample_rate()
        if self.__sample_rate < sr:
            modulated = []
            self.__sample_rate = sr
            for fc_temp in self.__modulating_signals:
                signal_temp, fs = librosa.load(self.__modulating_signals[fc_temp].get_filename() + ".wav", sr=sr)
                self.__modulating_signals[fc_temp].set_sample_rate(fs)
                self.__modulating_signals[fc_temp].set_amplitudes(signal_temp)

                ratio = self.__modulating_signals[fc_temp].__len__() / self.__modulating_signals[
                    fc_temp].get_sample_rate()
                bandwidth2 = self.__bandwidths[fc_temp] * ratio
                filtered = ifft(ifftshift(lpf(fftshift(fft(signal_temp)), bandwidth2)))

                carrier = np.cos(2.0 * np.pi * fc_temp * np.arange(len(filtered)) / sr)
                modulated.append(carrier * filtered)
                # if not os.path.isdir('./temp'):
                #    os.mkdir('temp')

            write = np.asarray(modulated.pop(), dtype=np.float32)
            wavfile.write("FDMA.wav", sr, write)

            while modulated.__len__() > 0:
                fr, fdma = wavfile.read("FDMA.wav")
                temp = modulated.pop()
                if len(fdma) > len(temp):
                    temp = np.append(temp, np.zeros(len(fdma) - len(temp)))
                else:
                    fdma = np.append(fdma, np.zeros(len(temp) - len(fdma)))
                fdma = fdma.astype(np.float64) + temp.astype(np.float64)
                wavfile.write("FDMA.wav", sr, fdma)

        else:
            signal_temp, fs = librosa.load(self.__modulating_signals[fc].get_filename() + ".wav",
                                           sr=self.__sample_rate)
            self.__modulating_signals[fc].set_sample_rate(fs)
            self.__modulating_signals[fc].set_amplitudes(signal_temp)

            ratio = self.__modulating_signals[fc].__len__() / self.__modulating_signals[fc].get_sample_rate()
            bandwidth2 = self.__bandwidths[fc] * ratio
            filtered = ifft(ifftshift(lpf(fftshift(fft(signal_temp)), bandwidth2)))
            carrier = np.cos(2.0 * np.pi * fc * np.arange(len(filtered)) / sr)
            temp = carrier * filtered
            import os
            if os.path.isfile("FDMA.wav"):
                fr, fdma = wavfile.read("FDMA.wav")
                if len(fdma) > len(temp):
                    temp = np.append(temp, np.zeros(len(fdma) - len(temp)))
                else:
                    fdma = np.append(fdma, np.zeros(len(temp) - len(fdma)))
                fdma = fdma.astype(np.float64) + temp.astype(np.float64)
                wavfile.write("FDMA.wav", sr, fdma)
            else:
                wavfile.write("FDMA.wav", sr, signal_temp)

        fr, self.__channel = wavfile.read("FDMA.wav")

        """modulating = self.__modulating_signals[fc]
        carrier = np.cos(
            2.0 * np.pi * fc * np.arange(self.__modulating_signals[fc].__len__()) / self.__sample_rate)
        modulated = carrier * modulating.get_amplitudes()

        length = self.__modulating_signals[fc].__len__()
        if len(self.__channel) < length:
            self.__channel = np.append(self.__channel, np.zeros(length - len(self.__channel), dtype=np.float64))

        self.__channel[:len(modulated)] += modulated  # issue

        wavfile.write("FDMA.wav", self.__sample_rate, np.asarray(self.__channel, dtype=np.int16))"""

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
        bandwidth = self.__bandwidths[fc] * ratio
        filtered = ifft(ifftshift(bpf(ft_channel, frequency, bandwidth)))
        demodulated = fftshift(fft(filtered * np.cos(
            2.0 * np.pi * fc * np.arange(len(filtered)) / self.__modulating_signals[fc].get_sample_rate())))

        return ifft(ifftshift(lpf(demodulated, bandwidth)))

    def get_modulating_signals(self):
        return self.__modulating_signals

    def get_channel(self):
        return self.__channel

    def get_sample_rate(self):
        return self.__sample_rate
