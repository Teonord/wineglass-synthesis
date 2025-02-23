import numpy as np
import sounddevice
from scipy.signal import butter, filtfilt

from curvefit import model, wg1_coefficients, wg2_coefficients


GLASS_ONE: bool = True
FINGER_RPM: float = 40
WATER_VOLUME_ML: float = 152.786
SUSTAIN_DURATION: float = 3
SAMPLE_RATE: int = 41100
PARTIALS_NUM: int = 10


# MIDI semitones to frequency
def st_to_f(st: float) -> float:
    return 8.18 * pow(2, st / 12)


# Frequency to MIDI semitones
def f_to_st(f: float) -> float:
    return np.log2(f / 8.18) * 12


# Decibels to absolute amplitude
def db_to_a(db: float) -> float:
    return pow(10, db / 20)


#  Absolute amplitude to decibels
def a_to_db(a: float) -> float:
    return 20 * np.log10(a)


#  Simple amplitude normalization
def normalize_audio(sound: np.ndarray):
    return sound / max(np.abs(sound))


# Create a partial
def generate_partial(time: np.ndarray, frequency: float):
    return np.sin(2 * np.pi * frequency * time)


# Make the amplitude oscillation
def rotation_envelope(sound: np.ndarray, time: np.ndarray, rpm: float, nodes: float, depth: float = 0.8) -> np.ndarray:
    nps = nodes * rpm / 60  # nodes per second
    sound *= np.abs(np.sin(np.pi * nps * time)) * depth + 1 - depth  # 2 sine nodes per wavelength due to abs
    return sound


def main():
    coefficients = wg1_coefficients() if GLASS_ONE == 1 else wg2_coefficients()

    f0 = model(WATER_VOLUME_ML, *coefficients[0])

    note_time = np.linspace(0, SUSTAIN_DURATION, int(SAMPLE_RATE * SUSTAIN_DURATION))

    sound = np.zeros_like(note_time)

    for i in range(PARTIALS_NUM):
        partial = generate_partial(note_time, f0 * (i + 1)) * (1 / (i + 1)) ** 3.8
        sound += rotation_envelope(partial, note_time, FINGER_RPM, 4 + 2 * i, 0.8)

    sound = normalize_audio(sound)

    sounddevice.play(sound, SAMPLE_RATE)
    sounddevice.wait()


if __name__ == "__main__":
    main()



