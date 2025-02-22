from matplotlib import pyplot as plt
from scipy.io import wavfile
import numpy as np

rate2, data2 = wavfile.read("hallelujahrefrain.wav")
rate, data = wavfile.read("hallelujahrefrainme.wav")

if len(data.shape) > 1:
    data = np.mean(data, axis=1)  # Convert to mono by averaging channels


if len(data2.shape) > 1:
    data2 = np.mean(data2, axis=1)  # Convert to mono by averaging channels


fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].specgram(data, Fs=rate, cmap="inferno")
axes[0].set_title("Spectrogram of Me Singing")
axes[0].set_xlabel("Time (s)")
axes[0].set_ylabel("Frequency (Hz)")

axes[1].specgram(data2, Fs=rate2, cmap="inferno")
axes[1].set_title("Spectrogram of Synthesized Singing")
axes[1].set_xlabel("Time (s)")
axes[1].set_ylabel("Frequency (Hz)")

plt.tight_layout()
plt.show()