import numpy as np


def freq_from_vol(coefficients: list[float], freqs: list[float]) -> list[list[float]]:
    last = coefficients[-1]

    res = []

    for freq in freqs:
        coefficients[-1] = last - freq
        roots = np.roots(coefficients)
        for r in roots:
            if np.isclose(r.imag, 0, atol=1e-6) and 0 <= r.real <= 350:
                res.append(r.real)
                break
        else:
            print(f"No freq for {freq}!")

    return res


if __name__ == "__main__":
    print(freq_from_vol(
        [7.51933578e-10, -4.69617180e-07, 8.81391937e-05, -9.88539231e-03, 2.87005924e-01, 8.49848104e+02],
        [440, 466.164, 493.883, 523.251, 554.365, 587.33, 622.256, 659.255, 698.456, 739.989, 783.991, 830.609]))

    print(freq_from_vol(
        [1.70256556e-09, -1.35671460e-06,  3.56977104e-04, -3.88252866e-02, 1.31541612e+00, 6.72717358e+02],
        [277.183,293.665,311.127,329.628,349.228,369.994,391.995,415.305
        ,440,466.164,493.883,523.251,554.365,587.33,622.254,659.255]))