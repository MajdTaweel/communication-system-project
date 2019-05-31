import os

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from scipy.fftpack import *
from scipy.io import wavfile

from AudioSignal import AudioSignal
from AudioSignal import lpf

matplotlib.use("QT5Agg")
new_signal = {}


def display_filtered_spectrum(signal, bandwidth):
    """
    Return filtered signal and its figure

    Parameters
    ----------
    :type signal: AudioSignal
    :type bandwidth: float
    """
    fig = plt.figure()
    plt.xlabel("Frequency (kHz)")
    plt.ylabel("Amplitude")
    signal_ft = signal.get_fourier_transform()
    signal_ft = lpf(signal_ft, bandwidth * len(signal.get_amplitudes()) // signal.get_sample_rate())
    plt.plot(fftshift(fftfreq(len(signal_ft), 1000 / signal.get_sample_rate())), signal_ft)

    return fig, signal_ft


def filter_and_plot(key, track, x_percentage, t, pb):
    t += 2
    pb.setValue(t)
    figs = []
    fig = plt.figure()
    figs.append(fig)
    sr = track.get_sample_rate()
    x = np.linspace(0, len(track.get_amplitudes()) // sr, num=len(track.get_amplitudes()))
    plt.plot(x, track.get_amplitudes())
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.title(key + "'s signal in time domain")
    t += 5
    pb.setValue(t)

    fig2 = plt.figure()
    figs.append(fig2)
    ft = track.get_fourier_transform()
    ax = fig2.add_subplot(111)
    length = len(ft)
    freq = fftshift(fftfreq(length, 1000 / track.get_sample_rate()))
    plot, = ax.plot(freq, ft)
    plt.xlabel("Frequency (kHz)")
    plt.ylabel("Amplitude")
    plt.title(key + "'s signal in frequency domain")
    t += 5
    pb.setValue(t)

    energy = track.get_energy()
    total_energy = sum(abs(track.get_amplitudes().astype(float)) ** 2) * float(length)
    # or - with only a relatively small error: total_energy = sum(energy)
    filtered_total_energy = 0
    bandwidth = 0
    cut_count = [0, 0, 0]
    t += 2
    pb.setValue(t)

    while total_energy != 0 and filtered_total_energy < (x_percentage / 100) * total_energy:
        bandwidth += 1000 * length // sr
        filtered_energy = lpf(energy, bandwidth)
        filtered_total_energy = sum(filtered_energy)
        cut_count[0] += 1

    t += 10
    pb.setValue(t)

    while total_energy != 0:
        if filtered_total_energy > ((x_percentage + 1) / 100) * total_energy:
            bandwidth -= 100 * length // sr
            cut_count[1] += 1
        elif filtered_total_energy < (x_percentage / 100) * total_energy:
            bandwidth += length // sr
            cut_count[2] += 1
        else:
            break
        filtered_energy = lpf(energy, bandwidth)
        filtered_total_energy = sum(filtered_energy)

    t += 20
    pb.setValue(t)

    temp = cut_count.copy()
    temp_bw = [0]

    def update(frame):
        if sum(cut_count) == 0:
            cut_count[0] = temp[0]
            cut_count[1] = temp[1]
            cut_count[2] = temp[2]
            temp_bw[0] = 0

        if frame != 0:
            if cut_count[0] > 0:
                temp_bw[0] += 1000 * length // sr
                cut_count[0] -= 1

            elif cut_count[1] > 0:
                temp_bw[0] -= 100 * length // sr
                cut_count[1] -= 1

            elif cut_count[2] > 0:
                temp_bw[0] += length // sr
                cut_count[2] -= 1

            lp = np.linspace(-length // 2, length // 2, num=length)
            lp = np.where(abs(lp) <= temp_bw, 1, 0)
            plot.set_ydata(lp * ft)

        else:
            plot.set_ydata(ft)

        return plot,

    new_signal[key] = ifft(ifftshift(lpf(ft, bandwidth)))
    fig3 = plt.figure()
    figs.append(fig3)
    plt.plot(x, new_signal[key])
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.title("Filtered " + key + "'s signal in time domain")

    if not os.path.isdir('./Filtered'):
        os.mkdir('Filtered')

    wavfile.write("./Filtered/" + key + " (Filtered).wav", sr, np.asarray(new_signal[key], dtype=np.int16))
    t += 15
    pb.setValue(t)

    # noinspection PyTypeChecker
    return figs, filtered_total_energy / total_energy, freq[length // 2 + bandwidth], [update, np.arange(sum(temp) + 1),
                                                                                       5000]
