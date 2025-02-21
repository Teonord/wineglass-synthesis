from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import sounddevice

AMT_PARTIALS = 15
SOUND_DURATION = 3

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


def create_tone(time, env_freqs, p_amps, p_freqs, env_params, semitones=0):
    additive_base = np.zeros_like(time)
    for i in range(len(env_freqs)):
        freq = env_freqs[i]
        if freq * pow(2, semitones / 12) > (len(time) / SOUND_DURATION) / 2:  # nyquist limit
            continue
        envelope = p_amps[p_freqs.index(freq)] * np.exp(-env_params[i] * time)
        partial = envelope * np.sin(2 * np.pi * freq * pow(2, semitones / 12) * time)
        additive_base += partial

    additive_base = additive_base / np.max(np.abs(additive_base))
    return additive_base


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
f_env_params = []

p_env_freqs = []
p_env_params = []

for i in range(AMT_PARTIALS):
    if pf1f[i] in pf2f:
        f_env_freqs.append(pf1f[i])
        j = pf2f.index(pf1f[i])
        f_env_params.append(compute_envelope_params(ps1f[i], ps2f[j], time_difff))

    if pf1p[i] in pf2p:
        p_env_freqs.append(pf1p[i])
        j = pf2p.index(pf1p[i])
        p_env_params.append(compute_envelope_params(ps1p[i], ps2p[j], time_diffp))

note_time = np.linspace(0, SOUND_DURATION, int(ratef * SOUND_DURATION))

song_length = 10
# F   G    A   B   C   D   E  F  G  A  B  C  D  E  F
#-12 -10  -8  -6  -5  -3  -1  0  2  4  6  7  9  11 12
pitches = [12, -8, -6, -3, -1, -1, 2, 9, 14,-1, 2, 9, 14]
times = [0, 0.6, 0.94, 1.27, 1.86, 3.02, 3.05, 3.10, 3.12, 3.91, 3.94, 3.97, 4]
vers = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1]

song_base = np.zeros(int(ratef * song_length))
for i in range(len(pitches)):
    start_ind = int(ratef * times[i])
    sound = create_tone(note_time, f_env_freqs, ps1f, pf1f, f_env_params, pitches[i]) if vers[i] == 1 else \
        create_tone(note_time, p_env_freqs, ps1p, pf1p, p_env_params, pitches[i])
    song_base[start_ind:start_ind+len(sound)] += sound

song = song_base / np.max(np.abs(song_base))

wavfile.write("song_a5.wav", ratef, (song * 32767).astype(np.int16))

sounddevice.play(song)
sounddevice.wait()
