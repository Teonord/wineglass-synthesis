from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt

# get sound data and sample rate from files
ratef, dataf = wavfile.read("A2-Glockenspiel-samples/A2-Glockenspiel-samples/Gsp_ME_f_L-sus_F#5.wav")
ratep, datap = wavfile.read("A2-Glockenspiel-samples/A2-Glockenspiel-samples/Gsp_ME_p_L-sus_F#5.wav")

# Make linearly spaced time lists
timef = np.linspace(0, len(dataf) / ratef, num=len(dataf))
timep = np.linspace(0, len(datap) / ratep, num=len(datap))


figure, axis = plt.subplots(2, 2)

axis[0, 0].plot(timef, dataf)
axis[0, 0].set_title("F#5 f Sound File")

axis[0, 1].plot(timep, datap)
axis[0, 1].set_title("F#5 p Sound File")

axis[1, 0].plot(timef[:40000], dataf[:40000])
axis[1, 0].set_title("F#5 f Sound File (first 40k samples)")

axis[1, 1].plot(timep[:40000], datap[:40000])
axis[1, 1].set_title("F#5 p Sound File (first 40k samples)")

figure.supxlabel("Time in seconds (s)")
figure.supylabel("Amplitude")
plt.show()