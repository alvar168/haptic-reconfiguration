import json
import numpy as np
import glob
import matplotlib.pyplot as plt
import os

# Load only raw trial JSON files (avoid processed files)
trial_files = sorted(glob.glob("user_data/3PatBracelet/trial_*.json"))
trial_files = [f for f in trial_files if "_processed" not in f]  # Exclude processed files

# Define workspace grid (7x7)
num_divisions = 7
x_bounds = np.linspace(-0.75, -0.3, num_divisions)  # Discretized X (West-East)
y_bounds = np.linspace(-0.4, 0.4, num_divisions)   # Discretized Y (South-North)

# Function to compute Euclidean distance
def compute_distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

# Function to get true position from haptic signal
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

# Process each trial
for file in trial_files:
    with open(file, "r") as f:
        data = json.load(f)

    print(f"--- Processing: {f}")

    # Extract XYZ positions and time
    xyz_positions = np.array(data["xyz_euler"])
    time_stamps = np.array(data["time"])

    # Flip X and Y for correct orientation
    x_plot = -xyz_positions[:, 0]  # Mirror X
    y_plot = -xyz_positions[:, 1]  # Mirror Y

    # Get start and end points
    start_pos = (x_plot[0], y_plot[0])
    end_pos = (x_plot[-1], y_plot[-1])

    # Compute true position from signal
    haptic_signal = data["haptic_signal"]["direction"]
    true_pos = get_true_position(haptic_signal)

    # Compute metrics
    total_travel_dist = sum(compute_distance((x_plot[i], y_plot[i]), (x_plot[i+1], y_plot[i+1])) 
                            for i in range(len(x_plot) - 1))
    trial_duration = time_stamps[-1] - time_stamps[0]  # Duration from first to last timestamp
    distance_to_true = compute_distance(end_pos, true_pos)

    # Create processed data dictionary
    processed_data = {
        "initial_position": start_pos,
        "end_position": end_pos,
        "signal_true_position": true_pos,
        "distance_to_true_position": distance_to_true,
        "total_travel_distance": total_travel_dist,
        "trial_duration": trial_duration,
        "direction": haptic_signal
    }

    # Save processed JSON
    processed_file = file.replace(".json", "_processed.json")
    with open(processed_file, "w") as f:
        json.dump(processed_data, f, indent=4)

    # Create figure
    fig, ax = plt.subplots(figsize=(7, 6))

    # Plot mirrored trajectory
    ax.plot(x_plot, y_plot, marker="o", linestyle="-", label="Trajectory")

    # Mark start and end points
    ax.scatter(*start_pos, color="green", marker="o", s=100, label="Start")  # Start marker
    ax.scatter(*end_pos, color="red", marker="x", s=100, label="End")  # End marker

    # Mark true position of haptic signal
    ax.scatter(*true_pos, color="blue", marker="s", s=150, label="Haptic Signal")  # Signal marker

    # Plot discretized grid points
    for x in x_bounds:
        for y in y_bounds:
            ax.scatter(x, y, color="black", marker=".", s=50)  # Small black dots for grid

    # Set workspace limits
    ax.set_xlim([-0.8, -0.25])
    ax.set_ylim([-0.45, 0.45])

    # Set axis labels based on the mirrored convention
    ax.set_xlabel("West <--> East")
    ax.set_ylabel("South <--> North")

    # Set title with haptic signal
    ax.set_title(f"Trajectory: {os.path.basename(file)}\nHaptic Signal: {haptic_signal}")

    # Adjust legend outside plot
    ax.legend(loc="upper left", bbox_to_anchor=(1, 1))

    # Save the plot as PNG
    plot_filename = file.replace(".json", ".png")
    plt.savefig(plot_filename, bbox_inches="tight", dpi=300)
    plt.close()

print("Processing complete. JSON and PNG files saved for each trial.")
