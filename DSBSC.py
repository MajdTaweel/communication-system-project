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
        carrier = np.cos(2 * np.pi * fc * np.arange(0, length / signal.get_sample_rate(), 1 / signal.get_sample_rate()))
        modulated = carrier * signal.get_amplitudes()
        DSBSC.__modulated_signals[fc] = modulated

        if len(DSBSC.__channel) < length:
            DSBSC.__channel = np.zeros(length)
        else:
            DSBSC.__channel = np.zeros(len(DSBSC.__channel))

        sr = signal.get_sample_rate()
        if DSBSC.__sample_rate != sr:
            import os
            if not os.path.isdir('./temp'):
                os.mkdir('temp')

            if DSBSC.__sample_rate < sr:
                DSBSC.__sample_rate = sr
                for fc in DSBSC.__modulated_signals:
                    wavfile.write("./temp/" + str(fc) + ".wav", sr,
                                  np.asarray(DSBSC.__modulated_signals[fc], dtype=np.int16))
                    fs, DSBSC.__modulated_signals[fc] = wavfile.read("./temp/" + str(fc) + ".wav")
            else:
                wavfile.write("./temp/" + str(fc) + ".wav", DSBSC.__sample_rate, np.asarray(modulated, dtype=np.int16))
                fs, DSBSC.__modulated_signals[fc] = wavfile.read("./temp/" + str(fc) + ".wav")

            import shutil
            shutil.rmtree("./temp")

        for key in DSBSC.__modulated_signals:
            for i in range(len(DSBSC.__modulated_signals[key])):
                DSBSC.__channel[i] += DSBSC.__modulated_signals[key][i]

        wavfile.write("FDMA.wav", DSBSC.__sample_rate, np.asarray(DSBSC.__channel, dtype=np.int16))

    @staticmethod
    def demodulate(fc):
        """
        Return a demodulated signal from the channel using the frequency of its carrier fc

        Parameters
        ----------
        :type fc: float
        """

        ft_channel = fftshift(fft(DSBSC.__channel))
        bandwidth = len(DSBSC.__modulated_signals[fc]) / DSBSC.__sample_rate
        filtered = ifft(ifftshift(bpf(ft_channel, fc, bandwidth)))
        demodulated = fftshift(fft(filtered * np.cos(
            2 * np.pi * fc * np.arange(0, len(DSBSC.__modulated_signals[fc]) - 1, 1 / DSBSC.__sample_rate))))

        return ifft(ifftshift(lpf(demodulated, bandwidth)))

    @staticmethod
    def get_channel():
        return DSBSC.__channel

    @staticmethod
    def get_sample_rate():
        return DSBSC.__sample_rate
