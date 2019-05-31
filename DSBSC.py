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
                for fc_temp in DSBSC.__modulated_signals:
                    wavfile.write("./temp/" + str(fc_temp) + ".wav", sr,
                                  np.asarray(DSBSC.__modulated_signals[fc_temp].get_amplitudes(), dtype=np.int16))
                    fs, signal_temp = wavfile.read("./temp/" + str(fc_temp) + ".wav")
                    DSBSC.__modulated_signals[fc_temp].set_sample_rate(fs)
                    DSBSC.__modulated_signals[fc_temp].set_amplitudes(signal_temp)

                DSBSC.__modulated_signals[fc] = signal

            else:
                DSBSC.__modulated_signals[fc] = signal
                wavfile.write("./temp/" + str(fc) + ".wav", DSBSC.__sample_rate,
                              np.asarray(signal.get_amplitudes(), dtype=np.int16))
                fs, signal_temp = wavfile.read("./temp/" + str(fc) + ".wav")
                DSBSC.__modulated_signals[fc].set_sample_rate(fs)
                DSBSC.__modulated_signals[fc].set_amplitudes(signal_temp)

            import shutil
            shutil.rmtree("./temp")

        else:
            DSBSC.__modulated_signals[fc] = signal

        for key in DSBSC.__modulated_signals:
            modulating = DSBSC.__modulated_signals[key]
            carrier = np.cos(
                2 * np.pi * key * np.arange(0, DSBSC.__modulated_signals[key].__len__() / modulating.get_sample_rate(),
                                            1 / modulating.get_sample_rate()))
            modulated = carrier * modulating.get_amplitudes()
            for i in range(len(DSBSC.__modulated_signals[key])):
                DSBSC.__channel[i] += modulated[i]

        wavfile.write("FDMA.wav", DSBSC.__sample_rate, np.asarray(DSBSC.__channel, dtype=np.int16))

    @staticmethod
    def demodulate(fc):
        """
        Return a demodulated signal from the channel using the frequency of its carrier fc

        Parameters
        ----------
        :type fc: float
        """

        ft_channel = fft(DSBSC.__channel)
        bandwidth = len(DSBSC.__modulated_signals[fc].get_amplitudes()) / DSBSC.__sample_rate
        filtered = ifft(bpf(ft_channel, fc, bandwidth))
        demodulated = fft(filtered * np.cos(
            2 * np.pi * fc * np.arange(0, len(DSBSC.__modulated_signals[fc].get_amplitudes()) - 1,
                                       1 / DSBSC.__sample_rate)))

        return ifft(lpf(demodulated, bandwidth))

    @staticmethod
    def get_channel():
        return DSBSC.__channel

    @staticmethod
    def get_sample_rate():
        return DSBSC.__sample_rate
