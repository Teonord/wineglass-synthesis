from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import numpy as np


def model(x, o, a, b, c, d, e):
    return o * x ** 5 + a * x ** 4 + b * x ** 3 + c * x ** 2 + d * x + e


def wg1_coefficients(plot: bool = False) -> list[list[float]]:
    mls = [0, 50, 100, 150, 200, 250, 300, 320]  # amount of water in glass 1 (ml)
    f0 = [850, 847, 830, 786, 706, 582, 448, 417]  # fundamental frequency of glass 1
    f1 = [1700, 1696, 1661, 1575, 1413, 1165, 895, 833]  # second partial of glass 1
    f2 = [2550, 2534, 2490, 2362, 2118, 1737, 1343, 1259]  # third partial of glass 1

    coefficients = fit_model(mls, f0, f1, f2)
    if not plot:
        return coefficients

    plot_model(1, mls, f0, f1, f2, coefficients)
    return coefficients


def wg2_coefficients(plot: bool = False) -> list[list[float]]:
    mls = [0, 50, 100, 150, 200, 250, 300, 350]  # amount of water in glass 2 (ml)
    f0 = [674, 672, 664, 642, 600, 532, 351, 267]  # fundamental frequency of glass 2
    f1 = [1347, 1346, 1327, 1286, 1204, 1067, 712, 540]  # second partial of glass 2
    f2 = [2037, 2016, 2002, 1929, 1809, 1595, 1055, 767]  # third partial of glass 2

    coefficients = fit_model(mls, f0, f1, f2)
    if not plot:
        return coefficients

    plot_model(2, mls, f0, f1, f2, coefficients)
    return coefficients


def fit_model(mls: list[float], f0: list[float], f1: list[float], f2: list[float]):
    # Do curve fit to fourth degree polynomial with values
    parameters_f0, cov_f0 = curve_fit(model, mls, f0)
    parameters_f1, cov_f1 = curve_fit(model, mls, f1)
    parameters_f2, cov_f2 = curve_fit(model, mls, f2)

    return [parameters_f0, parameters_f1, parameters_f2]


def plot_model(glass_nr: int, mls: list[float],
               f0: list[float], f1: list[float], f2: list[float],
               coefficients: list[list[float]]):
    func_x = np.linspace(0, max(mls), int(max(mls) + 1))
    f0_fit = model(func_x, *coefficients[0])  # apparently * unpacks list to arguments, crazy
    f1_fit = model(func_x, *coefficients[1])
    f2_fit = model(func_x, *coefficients[2])

    # Plot results
    plt.scatter(mls, f0, label="f0", color='red')
    plt.scatter(mls, f1, label="f1", color='green')
    plt.scatter(mls, f2, label="f2", color='blue')
    plt.plot(func_x, f0_fit, color='red')
    plt.plot(func_x, f1_fit, color='green')
    plt.plot(func_x, f2_fit, color='blue')
    plt.legend()
    plt.xlabel("Water volume (ml)")
    plt.ylabel("Frequency")
    plt.title(f"Fifth degree polynomial fit for Glass {glass_nr}.")
    plt.show()


if __name__ == "__main__":
    print(wg1_coefficients(True))
    print(wg2_coefficients(True))

