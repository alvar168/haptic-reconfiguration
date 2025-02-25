import matplotlib.pyplot as plt
import numpy as np
import pickle
import glob

# Load all trial files
trial_files = sorted(glob.glob("user_data/none/trial_*.pkl"))

plt.figure(figsize=(8, 6))

for file in trial_files:
    with open(file, "rb") as f:
        data = pickle.load(f)

    xyz_positions = np.array(data["xyz_euler"])  # Extract XYZ positions
    plt.plot(xyz_positions[:, 0], xyz_positions[:, 1], marker="o", linestyle="-", label=file)

plt.xlabel("X Position")
plt.ylabel("Y Position")
plt.title("Robot End-Effector Trajectories (X-Y)")
plt.legend()
plt.grid()
plt.show()
