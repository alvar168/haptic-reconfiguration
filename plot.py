import pickle
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Set folder name
folder_name = "none"
data_path = f"user_data/{folder_name}/"

# Get list of all saved recordings
files = sorted([f for f in os.listdir(data_path) if f.endswith(".pkl")])

# Initialize 3D plot
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

# Loop through all recordings
for i, file in enumerate(files):
    file_path = os.path.join(data_path, file)
    
    # Load data
    with open(file_path, "rb") as f:
        data = pickle.load(f)
    
    # Extract trajectory
    trajectory = np.array(data["xyz_euler"])  
    target = data["target"][0]
    
    # Plot trajectory
    ax.plot(trajectory[:, 0], trajectory[:, 1], trajectory[:, 2], label=f"Trajectory {i+1}")
    
    # Plot start & end points
    ax.scatter(trajectory[0, 0], trajectory[0, 1], trajectory[0, 2], c='green', marker='o', s=50)  # Start
    ax.scatter(trajectory[-1, 0], trajectory[-1, 1], trajectory[-1, 2], c='red', marker='x', s=50)  # End
    
    # Plot target position
    ax.scatter(target[0], target[1], target[2], c='blue', marker='*', s=80, label=f"Target {i+1}")

# Labels and legend
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
ax.set_title("Robot Arm End-Effector Trajectories")
ax.legend()
plt.show()
