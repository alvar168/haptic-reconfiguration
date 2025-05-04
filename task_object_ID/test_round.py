from __future__ import annotations
import numpy as np
import argparse
import pickle
import time
import yaml
import os
import serial
import random
import json
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from utils import *


"""
Functionalities defined in this script:

- Initialize robot
- User moves to home position
- Haptic feedback instructions sent to Arduino
- User moves based on haptic feedback
- Position & time data recorded

Instructions:

- Set robot to Execution mode
- Run main_B.py in terminal
- Run ./return_home in low-level computer
- Switch robot to Programming mode
- Move robot to home position
- Press A to start trial
- User moves robot
- Press B to end trial
- Press X to record trial
- Move robot to home position and repeat...

"""

## initialize robot
Robot = Franka3()
print('[*] Connecting to robot...')
conn_robot = Robot.connect2robot(mode="d")
print('    Successfully connected')

## initialize joystick
joystick = JoystickControl()

# Initialize serial communication with Arduino
arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
print('[*] Connecting to Arduino')
time.sleep(2)  # Wait for Arduino to initialize
print('[*] Arduino connected')

CONFIG_MODALITIES = {
	5: ("P", "A"), # Overload, judge by P although it is P+F
	2: ("P", "A"), 
	3: ("P", "F"), 
	4: ("A", "F")
}

# Define fixed bowl and plate positions
PLATES = np.array([
	[0.399, 0.080],
	[0.579, 0.080],
	[0.759, 0.080],
])
BOWLS = np.array([
	[0.449, -0.195],
	[0.579, -0.195],
	[0.709, -0.195],
	[0.389, -0.320],
	[0.519, -0.320],
	[0.649, -0.320],
	[0.779, -0.320],
])

familiarization_signals = [
	{"modality": "Pressure", "signal": [2, 1, 0]},
	{"modality": "Pressure", "signal": [2, 3, 0]},
	{"modality": "Pressure", "signal": [2, 5, 0]},
	{"modality": "Pressure", "signal": [2, 7, 0]},
	{"modality": "Area", "signal": [4, 1, 0]},
	{"modality": "Area", "signal": [4, 4, 0]},
	{"modality": "Area", "signal": [4, 7, 0]},
	{"modality": "Frequency", "signal": [4, 0, 1]},
	{"modality": "Frequency", "signal": [4, 0, 3]},
]

def loadHapticSignals(config_id: int) -> list:
	"""Load haptic signals for a selected configuration."""
	config_map = {
		
		2: "pressure_area_signals.json",
		3: "pressure_frequency_signals.json",
		4: "area_frequency_signals.json",
		5: "overload_signals.json"
	}

	filename = config_map.get(config_id)
	if not filename:
		raise ValueError("Invalid configuration selected.")

	filepath = os.path.join("signals_7x3", filename)
	with open(filepath, 'r', encoding="utf-8") as f:
		data = json.load(f)

	signals = data.get("haptic_signals", [])
	# Randomly (IID) select 10 signals from the set
	n = 3
	if n > len(signals):
		raise ValueError(f"Requested {n} signals, but only {len(signals)} available.")
	signals = random.sample(signals,n)
	
	# random.shuffle(signals)
	return signals



def send_haptic_signal(haptic_signal):
	"""Send haptic signal to Arduino via serial."""
	signal_str = ",".join(map(str, haptic_signal["signal"]))
	arduino.flush()
	time.sleep(0.1)
	arduino.write((signal_str + "\n").encode())  # Send to Arduino
	print(f"[*] Sending haptic signal: {signal_str}")

def send_end_signal():
	"""Send '0' to Arduino to deflate all solenoids."""
	arduino.write(b"0\n")
	print("[*] Sending deflate signal: 0")

def save_trial_order():
	trial_order_file = os.path.join(save_path, "trial_order.json")
	with open(trial_order_file, "w") as f:
		json.dump(haptic_signals, f, indent=4)
	print(f"[*] Saved trial order to {trial_order_file}")
	
def load_or_generate_trials(save_path, config_id: int):
	trial_order_file = os.path.join(save_path, "trial_order.json")
	
	if os.path.exists(trial_order_file):
		print("[*] Loading saved trial order.")
		with open(trial_order_file, "r") as f:
			haptic_signals = json.load(f)
	else:
		print("[*] Generating new randomized trial order.")
		haptic_signals = loadHapticSignals(config_id)
		with open(trial_order_file, "w") as f:
			json.dump(haptic_signals, f, indent=4)
		print(f"[*] Saved new trial order to {trial_order_file}")

	return haptic_signals


def get_completed_trials(save_path):
	"""Check which trials have already been saved, ignoring trial_order.json."""
	completed_trials = set()
	if os.path.exists(save_path):
		for filename in os.listdir(save_path):
			if filename.startswith("trial_") and filename.endswith(".json"):
				try:
					trial_num = int(filename.split("_")[1].split(".")[0])  # Extract trial number
					completed_trials.add(trial_num)
				except ValueError:
					print(f"[*] Skipping non-trial file: {filename}")
	return completed_trials

def give_user_feedback(trial_data):
	"""Provides trajectory-based feedback for object ID task (7x3 layout)."""
	trajectory = np.array(trial_data["xyz_euler"])[:, :2]

	# Detect bowl pickup point by velocity analysis
	window = 10
	vels = []
	for i in range(0, len(trajectory) - window, window):
		curr = trajectory[i + window][1]
		past = trajectory[i][1]
		vels.append(curr - past)
	vels = np.array(vels)
	idx = np.argmin(vels)
	candidate = np.argmax(vels[idx:] > 0.0)
	pickup_point = trajectory[window * (idx + candidate)]

	# Identify selected bowl and plate
	bowl_idx = np.argmin(np.linalg.norm(pickup_point - BOWLS, axis=1))
	plate_idx = np.argmin(np.linalg.norm(trajectory[-1] - PLATES, axis=1))

	# Ground truth from signal (1-indexed → 0-indexed)
	true_bowl_idx = trial_data["haptic_signal"]["signal"][1] - 1
	true_plate_idx = trial_data["haptic_signal"]["signal"][2] - 1

	# Compute errors
	classification_error = int(bowl_idx != true_bowl_idx) + int(plate_idx != true_plate_idx)
	euclidean_index_error = np.sqrt((bowl_idx - true_bowl_idx)**2 + (plate_idx - true_plate_idx)**2)

	# --- Plotting ---
	fig, ax = plt.subplots()
	ax.set_title(f"Trial {trial_data['trial_number']} Feedback (Object ID)")
	ax.plot(trajectory[:, 0], trajectory[:, 1], color="gray", label="Trajectory")
	ax.plot(trajectory[0, 0], trajectory[0, 1], "bo")

	# # Plot all bowl and plate positions
	# for i, (x, y) in enumerate(BOWLS):
	# 	ax.plot(x, y, "o", color="orange", alpha=0.4)
	# 	ax.text(x, y, f"B{i+1}", ha="center", va="center", fontsize=8, color="black")

	# for i, (x, y) in enumerate(PLATES):
	# 	ax.plot(x, y, "o", color="purple", alpha=0.4)
	# 	ax.text(x, y, f"P{i+1}", ha="center", va="center", fontsize=8, color="black")

	# Plot all bowl and plate positions
	for i, (x, y) in enumerate(BOWLS):
		circle = patches.Circle((x, y), radius=0.065, color='orange', alpha=0.4)
		ax.add_patch(circle)
		ax.text(x, y, f"B{i+1}", ha="center", va="center", fontsize=8, color="black")

	for i, (x, y) in enumerate(PLATES):
		circle = patches.Circle((x, y), radius=0.09, color='purple', alpha=0.4)
		ax.add_patch(circle)
		ax.text(x, y, f"P{i+1}", ha="center", va="center", fontsize=8, color="black")

	# Mark guessed and correct positions
	ax.scatter(BOWLS[bowl_idx][0], BOWLS[bowl_idx][1], color='red', marker='x', s=80, label="Guessed Ingredient")
	ax.scatter(PLATES[plate_idx][0], PLATES[plate_idx][1], color='red', marker='x', s=80, label="Guessed Plate")
	ax.scatter(BOWLS[true_bowl_idx][0], BOWLS[true_bowl_idx][1], color='green', marker='s', s=80, label="Correct Ingredient")
	ax.scatter(PLATES[true_plate_idx][0], PLATES[true_plate_idx][1], color='green', marker='s', s=80, label="Correct Plate")

	ax.set_xlabel("X (m)")
	ax.set_ylabel("Y (m)")
	ax.set_aspect("equal")
	ax.grid(True)
	ax.legend(loc="upper left", fontsize=8)

	ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), frameon=True)


	# Add annotation
	text = (
		f"Correct: Ingredient {true_bowl_idx+1}, Plate {true_plate_idx+1}\n"
		# f"Bowl (True/Guess): {true_bowl_idx} / {bowl_idx}\n"
		# f"Plate (True/Guess): {true_plate_idx} / {plate_idx}\n"
		f"Guessed: Ingredient {bowl_idx+1}, Plate {plate_idx+1}"
		# f"Classification Error: {classification_error}\n"
		# f"Index Euclidean Error: {euclidean_index_error:.2f}"
	)
	plt.text(1.02, 0.95, text, transform=ax.transAxes,
			 verticalalignment='top', bbox=dict(facecolor='white', alpha=0.8))

	plt.tight_layout()
	plt.subplots_adjust(right=0.75)  # adjust as needed for space


	plot_name = f"trial_{trial_data['trial_number']}.png"
	full_path = os.path.join(save_path, plot_name)
	plt.savefig(full_path, dpi=300, bbox_inches='tight')
	print(f"[+] Saved object ID plot to {full_path}")

	plt.show()



def main(save_path: str, num: int, haptic_signal: dict, thresh: float=0.05):
	'''
	Instructions:
	
		- Connect to robot (no gripper) and joystick
		- After robot connects, switch to Programming mode
		- Move robot to home position.
		- Press A to start trial (sends haptic feedback to Arduino).
		- User moves based on feedback.
		- Press B to finish the trial.
		- Press X to save the data.
	'''

	## parameters	
	record = False
	shutdown = False
	step_time = 0.1

	data = {"time":[],
			"joint_positions":[],
			"xyz_euler":[],
			"haptic_signal": haptic_signal
			}
	
	# Move robot to home position
	print(f"[*] Trial {num + 1} / {total_trials}")
	print("[*] Move the robot to the home position.")
	input("[*] Press Enter when ready.")
	
	assert haptic_signal["signal"][0] == config_id, \
	f"Config ID mismatch: expected {config_id}, got {haptic_signal['signal'][0]}"


	while not shutdown:

		## read robot states
		states = Robot.readState(conn_robot)
		q, xyz_euler = states["q"], states["xyz_euler"]

		## read joystick commands
		A_pressed, B_pressed, X_pressed, Y_pressed, _, _ = joystick.getInput()
		
		if record:

			data["joint_positions"].append(q)
			data["xyz_euler"].append(xyz_euler)
			data["time"].append(time.time() - start_time)

			if B_pressed and (time.time() - last_time > step_time):
				print("---Finished Trial")
				send_end_signal()
				record = False
		
		elif not record:

			if A_pressed:
				print("---Started Trial!")
				record = True
				start_time = time.time()
				last_time = start_time

				# Send haptic feedback signal to Arduino
				send_haptic_signal(haptic_signal)

			if X_pressed:
				end_time = time.time()  # Capture when trial was saved
				duration_sec = end_time - start_time

				start_time_str = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
				end_time_str = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')

				# Convert NumPy arrays to lists before saving
				data_serializable = {
					"trial_number": num+1,
					"config_id": haptic_signal["signal"][0],
					"start_timestamp": start_time_str,
					"end_timestamp": end_time_str,
					"duration_sec": duration_sec,
					"time": data["time"],
					"joint_positions": [list(q) for q in data["joint_positions"]],  # Convert arrays to lists
					"xyz_euler": [list(xyz) for xyz in data["xyz_euler"]],  # Convert arrays to lists
					"start_position": list(data["xyz_euler"][0]) if data["xyz_euler"] else None,
					"end_position": list(data["xyz_euler"][-1]) if data["xyz_euler"] else None,
					"haptic_signal": data["haptic_signal"]  # Already a list
				}

				trial_filename = os.path.join(save_path, f"trial_{num+1}.json")
				with open(trial_filename, "w") as file:
					json.dump(data_serializable, file, indent=4)

				print(f"--- Saved Trial as {trial_filename}")
					
				give_user_feedback(data_serializable)
				
				shutdown = True

def run_familiarization():
	print("\n[*] Starting familiarization phase.")
	print("You will now feel the LOW and HIGH levels of each modality.\n")
	
	for i, sig in enumerate(familiarization_signals):
		print(f"[{i+1}/{len(familiarization_signals)}] Modality: {sig['modality']}, Signal: {sig['signal']}")
		send_haptic_signal(sig)

		print("Press A to proceed to the next signal.")
		while True:
			A_pressed, _, _, _, _, _ = joystick.getInput()
			if A_pressed:
				send_end_signal()
				time.sleep(0.5)
				break
			time.sleep(0.1)

	print("[*] Familiarization complete.\n")

if __name__=="__main__": 
	"""
	You can set name of recordings as input arguments in terminal
	"""
	input("Press ENTER to continue")
	save_path = f"user_data/test_trials/"
	os.makedirs(save_path, exist_ok=True)

	input("Press ENTER to start familiarization round :)")    
	run_familiarization()

	print("TRIALS. Testing configuration 3 (Pressure-Frequency)")
	config_id = 3
	
	# haptic_signals = loadHapticSignals()
	haptic_signals = load_or_generate_trials(save_path, config_id)
	
	print(f"Total haptic signals loaded: {len(haptic_signals)}")
	total_trials = len(haptic_signals)
	
	completed_trials = get_completed_trials(save_path)
	
	for num, haptic_signal in enumerate(haptic_signals):
		if (num + 1) in completed_trials:
			print(f"[*] Skipping trial {num + 1}, already completed.")
			continue  # Skip if already done
		main(save_path, num, haptic_signal)