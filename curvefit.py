from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import numpy as np


def model(x, a, b, c, d, e):
    return a * x ** 4 + b * x ** 3 + c * x ** 2 + d * x + e


mls_wg1 = (0, 50, 100, 150, 200, 250, 300, 320)  # amount of water in glass 1 (ml)
f0_wg1 = (850, 847, 830, 786, 706, 582, 448, 417)  # fundamental frequency of glass 1
f1_wg1 = (1700, 1696, 1661, 1575, 1413, 1165, 895, 833)  # second partial of glass 1
f2_wg1 = (2550, 2534, 2490, 2362, 2118, 1737, 1343, 1259)  # third partial of glass 1

mls_wg2 = (0, 50, 100, 150, 200, 250, 300, 350)  # amount of water in glass 2 (ml)
f0_wg2 = (674, 672, 664, 642, 600, 532, 351, 267)  # fundamental frequency of glass 2
f1_wg2 = (1347, 1346, 1327, 1286, 1204, 1067, 712, 540)  # second partial of glass 2
f2_wg2 = (2037, 2016, 2002, 1929, 1809, 1595, 1055, 767)  # third partial of glass 2


# Do curve fit to fourth degree polynomial with values
parameters_f0_wg1, cov_f0_wg1 = curve_fit(model, mls_wg1, f0_wg1)
parameters_f1_wg1, cov_f1_wg1 = curve_fit(model, mls_wg1, f1_wg1)
parameters_f2_wg1, cov_f2_wg1 = curve_fit(model, mls_wg1, f2_wg1)

parameters_f0_wg2, cov_f0_wg2 = curve_fit(model, mls_wg2, f0_wg2)
parameters_f1_wg2, cov_f1_wg2 = curve_fit(model, mls_wg2, f1_wg2)
parameters_f2_wg2, cov_f2_wg2 = curve_fit(model, mls_wg2, f2_wg2)

func_x = np.linspace(0, 350, 351)
f0_fit_wg1 = model(func_x, *parameters_f0_wg1)  # apparently * unpacks list to arguments, crazy
f1_fit_wg1 = model(func_x, *parameters_f1_wg1)
f2_fit_wg1 = model(func_x, *parameters_f2_wg1)

print(parameters_f0_wg1)
print(parameters_f1_wg1)
print(parameters_f2_wg1)

# Plot results
plt.scatter(mls_wg1, f0_wg1, label="f0", color='red')
plt.scatter(mls_wg1, f1_wg1, label="f1", color='green')
plt.scatter(mls_wg1, f2_wg1, label="f2", color='blue')
plt.plot(func_x, f0_fit_wg1, color='red')
plt.plot(func_x, f1_fit_wg1, color='green')
plt.plot(func_x, f2_fit_wg1, color='blue')
plt.legend()
plt.xlabel("Water volume (ml)")
plt.ylabel("Frequency")
plt.title("Fourth degree polynomial fit for glass 1 (small glass)")
plt.show()

func_x = np.linspace(0, 350, 351)
f0_fit_wg2 = model(func_x, *parameters_f0_wg2)
f1_fit_wg2 = model(func_x, *parameters_f1_wg2)
f2_fit_wg2 = model(func_x, *parameters_f2_wg2)

print(parameters_f0_wg2)
print(parameters_f1_wg2)
print(parameters_f2_wg2)

# Plot results
plt.scatter(mls_wg2, f0_wg2, label="f0", color='red')
plt.scatter(mls_wg2, f1_wg2, label="f1", color='green')
plt.scatter(mls_wg2, f2_wg2, label="f2", color='blue')
plt.plot(func_x, f0_fit_wg2, color='red')
plt.plot(func_x, f1_fit_wg2, color='green')
plt.plot(func_x, f2_fit_wg2, color='blue')
plt.legend()
plt.xlabel("Water volume (ml)")
plt.ylabel("Frequency")
plt.title("Fourth degree polynomial fit for glass 2 (big glass)")
plt.show()

