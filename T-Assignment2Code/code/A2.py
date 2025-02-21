from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

def locate_partials(mags, freqs):
    peaks = find_peaks(mags)
    peak_f = []
    peak_m = []
    for peak in peaks[0]:
        if freqs[peak] <= 15000:
            peak_f.append(freqs[peak])
            peak_m.append(mags[peak])

    peak_f = [x for _,x in sorted(zip(peak_m, peak_f))]  # sort by magnitude, https://stackoverflow.com/questions/6618515/sorting-list-according-to-corresponding-values-from-a-parallel-list
    peak_f.reverse()
    peak_m = sorted(peak_m)
    peak_m.reverse()

    peak_f = peak_f[:15]  # highest partials
    peak_m = peak_m[:15]

    peak_m = [x for _,x in sorted(zip(peak_f, peak_m))]  # Restore to frequency order
    peak_f = sorted(peak_f)

    return peak_m, peak_f


ratef, dataf = wavfile.read("A2-Glockenspiel-samples/A2-Glockenspiel-samples/Gsp_ME_f_L-sus_F#5.wav")
ratep, datap = wavfile.read("A2-Glockenspiel-samples/A2-Glockenspiel-samples/Gsp_ME_p_L-sus_F#5.wav")

dataf = dataf[:, 0]
datap = datap[:, 0]

windowf = int(ratef * 0.1)
windowp = int(ratep * 0.1)

startf = int(ratef * 0.0014)  # From zooming in in Audacity
startp = int(ratep * 0.00127)

rect_window_1f = dataf[startf:startf+windowf]
rect_window_1p = datap[startp:startp+windowp]
rect_window_2f = dataf[windowf * 7:windowf * 8]  # Still between 0.5-1s from the first window even if we ignore onset.
rect_window_2p = datap[windowp * 7:windowp * 8]

_, axis = plt.subplots(2, 2)
axis[0, 0].set_title("F#5 f Sound File onset window")
s1f, f1f, _ = axis[0, 0].magnitude_spectrum(rect_window_1f, Fs=ratef, scale="dB")
ps1f, pf1f = locate_partials(abs(s1f), f1f)

axis[0, 1].set_title("F#5 p Sound File onset window")
s1p, f1p, _ = axis[0, 1].magnitude_spectrum(rect_window_1p, Fs=ratep, scale="dB")
ps1p, pf1p = locate_partials(abs(s1p), f1p)

axis[1, 0].set_title("F#5 f Sound File later window")
s2f, f2f, _ = axis[1, 0].magnitude_spectrum(rect_window_2f, Fs=ratef, scale="dB")
ps2f, pf2f = locate_partials(abs(s2f), f2f)

axis[1, 1].set_title("F#5 p Sound File later window")
s2p, f2p, _ = axis[1, 1].magnitude_spectrum(rect_window_2p, Fs=ratep, scale="dB")
ps2p, pf2p = locate_partials(abs(s2p), f2p)

plt.show()

figure, axis = plt.subplots(2, 2)

bar_positions = np.arange(15)

axis[0, 0].set_title("F#5 f Sound File onset window")
axis[0, 0].bar(bar_positions, ps1f)
axis[0, 0].set_xticks(bar_positions)
axis[0, 0].set_xticklabels(pf1f, fontsize=8)
axis[0, 0].set_yscale("log")

axis[0, 1].set_title("F#5 p Sound File onset window")
axis[0, 1].bar(bar_positions, ps1p)
axis[0, 1].set_xticks(bar_positions)
axis[0, 1].set_xticklabels(pf1p, fontsize=8)
axis[0, 1].set_yscale("log")

axis[1, 0].set_title("F#5 f Sound File later window")
axis[1, 0].bar(bar_positions, ps2f)
axis[1, 0].set_xticks(bar_positions)
axis[1, 0].set_xticklabels(pf2f, fontsize=8)
axis[1, 0].set_yscale("log")

axis[1, 1].set_title("F#5 p Sound File later window")
axis[1, 1].bar(bar_positions, ps2p)
axis[1, 1].set_xticks(bar_positions)
axis[1, 1].set_xticklabels(pf2p, fontsize=8)
axis[1, 1].set_yscale("log")

figure.supxlabel("Frequency")
figure.supylabel("Amplitude")

plt.show()

