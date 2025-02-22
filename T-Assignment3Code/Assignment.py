import math
from matplotlib import pyplot as plt
import numpy as np
import sounddevice


def st_to_f(st: float) -> float:
    return 8.18 * pow(2, st / 12)


def f_to_st(f: float) -> float:
    return math.log2(f / 8.18) * 12


def db_to_a(db: float) -> float:
    return pow(10, db / 20)


def a_to_db(a: float) -> float:
    return 20 * math.log10(a)


# Generate a single partial of set amplitude and frequency with optional vibrato.
def make_partial(time: np.ndarray, amplitude: float, frequency: float,
                 vib_f: float = 0, vib_st: float = 0) -> np.ndarray:
    # If vibrato is used, need to use vibrato equations
    if vib_st != 0:
        og_st = f_to_st(frequency)
        vib_a = st_to_f(og_st + vib_st) - frequency
        vib = vib_a * np.sin(2 * np.pi * vib_f * time)
        return amplitude * np.sin(2 * np.pi * frequency * time + vib)
    return amplitude * np.sin(2 * np.pi * frequency * time)


# Create a source file of pitch st, with a number of partials, and a slope in dBs
def make_source(st: float, duration: float, partials: int,
                sample_rate: int, db_slope: float = -6,
                vib_f: float = 0, vib_st:float = 0) -> np.ndarray:
    # Get the base frequency to compare in dB
    f0 = st_to_f(st)
    base_octave = math.log2(f0)

    # Generate time and base sound array
    time = np.linspace(0, duration, int(sample_rate * duration))
    source = np.zeros_like(time)

    # Make the n partials
    for i in range(partials):
        # Nyquist limit
        if i * f0 > sample_rate / 2:
            print("Too many partials!")
            break
        fi = f0 * (i + 1)
        # Check how much amplitude should be reduced based on spectral slope and current pitch
        ai = db_to_a(db_slope * (math.log2(fi) - base_octave))
        source += make_partial(time, ai, fi, vib_f, vib_st)

    return source


# Calculate the coefficients for the filter with equations taken directly from the supplied PDF
def get_filter_coefficients(formant_f: float, formant_bw: float, sample_len: float) -> (float, float, float):
    q = formant_f / formant_bw
    b = 2 * np.pi * formant_f
    b0 = b * math.sqrt(1 + 1 / (4 * pow(q, 2)))
    a = b0 / (2 * q)
    a1 = -2 * math.exp(-a * sample_len) * np.cos(b * sample_len)
    a2 = math.exp(-2 * a * sample_len)
    g = 1 + a1 + a2
    return g, a1, a2


# Use the calculated coefficients to apply the filter to each sample in the sound
def apply_filter(source: np.ndarray, formant_f: float, formant_bw: float, sample_rate: int) -> np.ndarray:
    g, a1, a2 = get_filter_coefficients(formant_f, formant_bw, 1 / sample_rate)
    n1 = 0
    n2 = 0
    for i in range(len(source)):
        source[i] = g * source[i] - a1 * n1 - a2 * n2
        n2 = n1
        n1 = source[i]
    return source


if __name__ == "__main__":

    # Set the dynamics (in dB)
    dynamics = -6

    # Set the other variables for the source synthesis
    semitone = f_to_st(112)
    duration = 5
    max_partials = 30
    sample_rate = 44100
    spectral_slope = dynamics
    vibrato_semitones = 0.1
    vibrato_frequency = 6.5

    # Set the filter parameters
    formants = [240, 800, 2480, 3000, 5400]
    bandwidths = [24, 80, 24, 300, 540]

    source_a = make_source(semitone, duration, max_partials, sample_rate, spectral_slope,
                           vibrato_frequency, vibrato_semitones)

    for j in range(len(formants)):
        source_a = apply_filter(source_a, formants[j], bandwidths[j], sample_rate)

    source_a = source_a / max(abs(source_a))

    sounddevice.play(source_a * db_to_a(dynamics), sample_rate)
    sounddevice.wait()

