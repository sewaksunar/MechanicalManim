import numpy as np
import matplotlib.pyplot as plt

# Parameters (you can change these values)
sigma_x = 10
sigma_y = 2
tau_xy = 4

# Theta from 0 to 2pi
theta = np.linspace(0, 2 * np.pi, 400)

# Compute sigma_xx' for each theta
sigma_xx_prime = sigma_x * np.cos(theta) ** 2 + sigma_y * np.sin(theta) ** 2 + 2 * tau_xy * np.sin(theta) * np.cos(theta)

plt.figure(figsize=(8, 5))
plt.plot(np.degrees(theta), sigma_xx_prime, label=r"$\sigma_{xx}'$")
plt.xlabel(r"$\theta$ (degrees)")
plt.ylabel(r"$\sigma_{xx}'$")
plt.title(r"$\sigma_{xx}'$ vs $\theta$")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
