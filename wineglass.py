import numpy as np
from curvefit import model, wg1_coefficients, wg2_coefficients


GLASS_ONE: bool = True
FINGER_RPM: float = 60
WATER_VOLUME_ML: float = 152.786
SUSTAIN_DURATION: float = 10


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


coefficients = wg1_coefficients() if GLASS_ONE == 1 else wg2_coefficients()

f0 = model(WATER_VOLUME_ML, *coefficients)

