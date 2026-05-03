import control as ct
import matplotlib.pyplot as plt

num = [1]
den = [1, 2, 1]
W = ct.tf(num, den)

plt.figure(figsize=(10, 10))

# return_contour=True returns frequency data and stability info
count, contour = ct.nyquist_plot(W, return_contour=True)

plt.xlabel('Real Axis', fontsize=12)
plt.ylabel('Imaginary Axis', fontsize=12)
plt.xlim([-2, 2])
plt.ylim([-2, 2])

plt.savefig('nyquist.png', dpi=300)
plt.show()