import numpy as np
import sounddevice

from curvefit import model, wg1_coefficients, wg2_coefficients

GLASS_ONE: bool = True
FINGER_RPM: float = 40
WATER_VOLUME_ML: float = 152.786
SUSTAIN_DURATION: float = 2
SAMPLE_RATE: int = 41100
PARTIALS_NUM: int = 10
RELEASE_DURATION: float = 10  # testing


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
    return np.sin(2 * np.pi * frequency * time + generate_offset(time))


# Creates an offset, simulating periodic inharmonicity
def generate_offset(time):
    return np.sin(time * 5 * np.pi)


def asr_envelope(time: np.ndarray, rpm: float, nodes: float, sustain_end: float,
                 osc_depth: float = 0.8, coefficient: float = 0.5) -> np.ndarray:
    envelope = np.ones_like(time)

    nps = nodes * rpm / 60  # nodes per second

    # Attack ( 1 node length )
    att_duration = 1 / nps
    a_criteria = time <= att_duration
    envelope[a_criteria] = (1 - np.cos((np.pi / 2) * (time[a_criteria] / att_duration)))

    # Sustain (oscillation will be during attack too)
    envelope *= np.abs(np.sin(np.pi * nps * time)) * osc_depth + 1 - osc_depth

    # Release (Will begin on first peak after sustain)
    pos = sustain_end * nps % 1
    rel_start = (sustain_end * nps + (0.5 - pos if pos <= 0.5 else 1.5 - pos)) / nps
    r_criteria = time >= rel_start
    envelope[r_criteria] = np.exp(-coefficient * (time[r_criteria] - time[r_criteria][0]))

    return envelope


def main():
    coefficients = wg1_coefficients() if GLASS_ONE == 1 else wg2_coefficients()

    f0 = model(WATER_VOLUME_ML, *coefficients[0])

    note_time = np.linspace(0, SUSTAIN_DURATION + RELEASE_DURATION,
                            int(SAMPLE_RATE * (SUSTAIN_DURATION + RELEASE_DURATION)))

    sound = np.zeros_like(note_time)

    for i in range(PARTIALS_NUM):
        if f0 * i > SAMPLE_RATE / 2:
            break  # Nyquist limit
        frequency = f0 * (i + 1)
        partial = generate_partial(note_time, frequency) * (1 / (i + 1)) ** 3.8

        # Generate the sustained tome (with attack)
        partial *= asr_envelope(note_time, FINGER_RPM, 2 * (i + 1), SUSTAIN_DURATION, 0.8 ** (i + 1), (i + 1))

        sound += partial

    sound = normalize_audio(sound)

    sounddevice.play(sound, SAMPLE_RATE)
    sounddevice.wait()


if __name__ == "__main__":
    main()
