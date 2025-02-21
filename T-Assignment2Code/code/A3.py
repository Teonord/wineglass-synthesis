from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

AMT_PARTIALS = 15

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

    peak_f = peak_f[:AMT_PARTIALS]  # highest partials
    peak_m = peak_m[:AMT_PARTIALS]

    peak_m = [x for _,x in sorted(zip(peak_f, peak_m))]  # Restore to frequency order
    peak_f = sorted(peak_f)

    return peak_m, peak_f


def compute_envelope_params(amp1, amp2, t_diff):
    return (np.log(amp1) - np.log(amp2)) / t_diff


ratef, dataf = wavfile.read("A2-Glockenspiel-samples/A2-Glockenspiel-samples/Gsp_ME_f_L-sus_F#5.wav")
ratep, datap = wavfile.read("A2-Glockenspiel-samples/A2-Glockenspiel-samples/Gsp_ME_p_L-sus_F#5.wav")

dataf = dataf[:, 0]
datap = datap[:, 0]

windowf = int(ratef * 0.1)
windowp = int(ratep * 0.1)

startf = int(ratef * 0.0014)  # From zooming in in Audacity
startp = int(ratep * 0.00127)

time_difff = 0.7 - 0.0014
time_diffp = 0.7 - 0.00127

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

f_env_freqs = []
f_env_amps = []
f_env_params = []

p_env_freqs = []
p_env_amps = []
p_env_params = []

for i in range(AMT_PARTIALS):
    if pf1f[i] in pf2f:
        f_env_freqs.append(pf1f[i])
        j = pf2f.index(pf1f[i])
        f_env_amps.append(ps1f[j])
        f_env_params.append(compute_envelope_params(ps1f[i], ps2f[j], time_difff))

    if pf1p[i] in pf2p:
        p_env_freqs.append(pf1p[i])
        j = pf2p.index(pf1p[i])
        p_env_amps.append(ps1p[j])
        p_env_params.append(compute_envelope_params(ps1p[i], ps2p[j], time_diffp))


figure, axis = plt.subplots(len(f_env_freqs), 2)
tf = np.linspace(0, 5, int(ratef * 5))
tp = np.linspace(0, 5, int(ratep * 5))

for i in range(len(f_env_freqs)):

    Af = f_env_amps[i] * np.exp(-f_env_params[i] * tf)
    axis[i, 0].plot(tf, Af)
    axis[i, 0].set_title(f"F#f at {f_env_freqs[i]}Hz")

    Ap = p_env_amps[i] * np.exp(-p_env_params[i] * tp)
    axis[i, 1].plot(tp, Ap)
    axis[i, 1].set_title(f"F#p at {f_env_freqs[i]}Hz")

figure.supxlabel("Time (s)")
figure.supylabel("Amplitude")
plt.show()