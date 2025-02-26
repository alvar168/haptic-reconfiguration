import json
import numpy as np
import glob
import matplotlib.pyplot as plt

# Load only raw trial JSON files (avoid processed files)
trial_files = sorted(glob.glob("user_data/none/trial_*.json"))
trial_files = [f for f in trial_files if "_processed" not in f]  # Exclude processed files

# Define workspace grid (7x7)
num_divisions = 7
x_bounds = np.linspace(-0.75, -0.3, num_divisions)  # Discretized X (West-East)
y_bounds = np.linspace(-0.4, 0.4, num_divisions)   # Discretized Y (South-North)

# Function to compute true position from haptic signal
def get_true_position(haptic_signal):
    signal_mapping = {
        "D1_L": (0, 1), "D1_M": (0, 2), "D1_H": (0, 3),  # North (Negative Y)
        "D2_L": (0, -1), "D2_M": (0, -2), "D2_H": (0, -3),  # South (Positive Y)
        "D3_L": (1, 0), "D3_M": (2, 0), "D3_H": (3, 0),  # East (Negative X)
        "D4_L": (-1, 0), "D4_M": (-2, 0), "D4_H": (-3, 0)  # West (Positive X)
    }
    
    # Compute the summed movement in X and Y directions
    total_shift_x, total_shift_y = 0, 0
    for signal in haptic_signal.split(" + "):
        shift_x, shift_y = signal_mapping.get(signal, (0, 0))
        total_shift_x += shift_x
        total_shift_y += shift_y

    # Find true position on the grid (assuming (0,0) is center)
    center_x = np.mean(x_bounds)
    center_y = np.mean(y_bounds)

    true_x = center_x + total_shift_x * (x_bounds[1] - x_bounds[0])
    true_y = center_y + total_shift_y * (y_bounds[1] - y_bounds[0])

    return (true_x, true_y)

### Plot 1: All Trajectories in One Figure
plt.figure(figsize=(8, 6))

for file in trial_files:
    with open(file, "r") as f:
        data = json.load(f)

    # Extract XYZ positions
    xyz_positions = np.array(data.get("xyz_euler", []))

    # Skip if empty or malformed
    if xyz_positions.size == 0:
        print(f"Skipping {file} due to missing or malformed data.")
        continue

    # Flip X and Y for correct orientation
    x_plot = -xyz_positions[:, 0]  # Mirror X
    y_plot = -xyz_positions[:, 1]  # Mirror Y

    # Plot trajectory
    plt.plot(x_plot, y_plot, marker="o", linestyle="-", alpha=0.7, label=file)

# Set workspace limits
plt.xlim([-0.8, -0.25])
plt.ylim([-0.45, 0.45])

# Set axis labels
plt.xlabel("West <--> East")
plt.ylabel("South <--> North")
plt.title("All Robot End-Effector Trajectories")

plt.legend(fontsize=8, loc="upper left", bbox_to_anchor=(1, 1))
plt.grid()
plt.show()

### Plot 2: End Positions vs. True Positions
plt.figure(figsize=(8, 6))

for file in trial_files:
    with open(file, "r") as f:
        data = json.load(f)

    # Extract XYZ positions
    xyz_positions = np.array(data.get("xyz_euler", []))

    # Skip if empty
    if xyz_positions.size == 0:
        print(f"Skipping {file} due to missing data.")
        continue

    # Flip X and Y for correct orientation
    x_plot = -xyz_positions[:, 0]  # Mirror X
    y_plot = -xyz_positions[:, 1]  # Mirror Y

    # Get end and true positions
    end_pos = (x_plot[-1], y_plot[-1])
    haptic_signal = data["haptic_signal"]["direction"]
    true_pos = get_true_position(haptic_signal)

    # Plot end and true positions
    plt.scatter(*end_pos, color="red", marker="x", s=100, label="End" if file == trial_files[0] else None)  
    plt.scatter(*true_pos, color="blue", marker="s", s=150, label="Haptic Signal" if file == trial_files[0] else None)  

    # Connect end position to true position with a dotted line
    plt.plot([end_pos[0], true_pos[0]], [end_pos[1], true_pos[1]], linestyle="dotted", color="gray", linewidth=1.5)

# Set workspace limits
plt.xlim([-0.8, -0.25])
plt.ylim([-0.45, 0.45])

# Set axis labels
plt.xlabel("West <--> East")
plt.ylabel("South <--> North")
plt.title("End Positions vs. True Positions")

plt.legend(fontsize=8, loc="upper left", bbox_to_anchor=(1, 1))
plt.grid()
plt.show()
