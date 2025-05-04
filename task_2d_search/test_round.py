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
	1: ("P", "A"), # Overload, judge by Area although it is A+F
	2: ("P", "A"), 
	3: ("P", "F"), 
	4: ("A", "F")
}

familiarization_signals = [
	{"modality": "Pressure", "signal": [2, 1, 0]},
	{"modality": "Pressure", "signal": [2, 2, 0]},
	{"modality": "Pressure", "signal": [2, 3, 0]},
	{"modality": "Pressure", "signal": [2, 4, 0]},
	{"modality": "Area", "signal": [4, 1, 0]},
	{"modality": "Area", "signal": [4, 2, 0]},
	{"modality": "Area", "signal": [4, 4, 0]},
	{"modality": "Frequency", "signal": [4, 0, 1]},
	{"modality": "Frequency", "signal": [4, 0, 4]},
]

def loadHapticSignals(config_id: int) -> list:
	"""Load haptic signals for a selected configuration."""
	config_map = {
		1: "overload_signals.json",
		2: "pressure_area_signals.json",
		3: "pressure_frequency_signals.json",
		4: "area_frequency_signals.json"
	}

	filename = config_map.get(config_id)
	if not filename:
		raise ValueError("Invalid configuration selected.")

	filepath = os.path.join("signals", filename)
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
	
	config_id = trial_data["config_id"]
	signal = trial_data["haptic_signal"]["signal"]
	x_modality, y_modality = CONFIG_MODALITIES[config_id]

	# Grid parameters
	spacing = 0.075
	origin_xy = np.array(trial_data["start_position"][:2])
	end_xy = np.array(trial_data["end_position"][:2])
	
	# Guessed grid index from origin position
	guessed_x = round((end_xy[0] - origin_xy[0]) / spacing)
	guessed_y = round((end_xy[1] - origin_xy[1]) / spacing)

	# Correct signal indices
	correct_x = signal[1]
	correct_y = signal[2]

	# Manhattan error
	manhattan_error = abs(guessed_x - correct_x) + abs(guessed_y- correct_y)
	
	# Euclidean error
	correct_xy = np.array([
		origin_xy[0] + correct_x*spacing,
		origin_xy[1] + correct_y * spacing
	])
	euclidean_error = np.linalg.norm(end_xy - correct_xy)

	# Feedback
	print("\n TRIAL FEEDBACK: ")
	print(f" - Target Position  : ({correct_x}, {correct_y})")
	print(f" - Your response    : ({guessed_x}, {guessed_y})")
	print(f" - Manhattan Distance: {manhattan_error} grid cells")
	print("----------------------------------------------------\n")

	# Plot
	fig, ax = plt.subplots()
	ax.set_title("Trial Feedback")
	ax.set_xlabel("X")
	ax.set_ylabel("Y")
	ax.set_aspect('equal')

	# Plot grid lines (assuming a 5x5 grid for generality)
	grid_size = 5
	x_ticks = [origin_xy[0] + i * spacing for i in range(grid_size)]
	y_ticks = [origin_xy[1] + i * spacing for i in range(grid_size)]

	ax.set_xticks(x_ticks)
	ax.set_yticks(y_ticks)
	ax.grid(True, linestyle='--', color='lightgray')

	# Set axis limits to frame the full grid + margin
	ax.set_xlim(min(x_ticks) - spacing/2, max(x_ticks) + spacing/2)
	ax.set_ylim(min(y_ticks) - spacing/2, max(y_ticks) + spacing/2)

	for i in range(1, grid_size):
		for j in range(1, grid_size):
			gx = origin_xy[0] + i * spacing
			gy = origin_xy[1] + j * spacing
			# ax.plot(gx, gy, marker='o', color='lightgray', markersize=4, alpha=0.6)
			plt.text(gx, gy, f"{i},{j}", fontsize=10, ha='center', va='center', color='gray')

	# Plot trajectory
	trajectory = np.array(trial_data["xyz_euler"])[:, :2]
	ax.plot(trajectory[:, 0], trajectory[:, 1], linestyle='-', color='gray', label='Trajectory')

	# Mark origin
	ax.plot(origin_xy[0], origin_xy[1], marker='o', color='blue', label='Origin')

	# Mark correct and guessed
	ax.scatter(correct_xy[0], correct_xy[1], color='green', s=100, marker='s', label='Correct')
	ax.scatter(end_xy[0], end_xy[1], color='red', s=100, marker='x', label='Guessed')


	# Flip Y-axis to match layout
	# ax.invert_yaxis()

	# Text annotation
	text_str= (
		f"Trial {trial_data['trial_number']}\n"
		f"Correct position: ({correct_x}, {correct_y})\n"
		f"Guessed position: ({guessed_x}, {guessed_y})\n"
		f"Manhattan Distance: {manhattan_error} grid cells"
	)
	# plt.text(0.01, 0.99, text_str, transform=plt.gca().transAxes,
	# 	  verticalalignment='top', horizontalalignment='left',
	# 	  bbox=dict(facecolor='white', alpha=0.8))
	
	# Place it outside the axes — for example, top-right margin of the figure
	fig.text(0.98, 0.98, text_str, ha='right', va='top', fontsize=10,
		 bbox=dict(facecolor='white', alpha=0.9, edgecolor='gray'))

	plt.tight_layout()
	
	plot_name = f"trial_{trial_data['trial_number']}.png"
	plot_path = os.path.join(save_path, plot_name)
	plt.savefig(plot_path, dpi=300, bbox_inches='tight')
	print(f"[+] Plot saved to {plot_path}")
	
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

				give_user_feedback(data_serializable)
				print(f"--- Saved Trial as {trial_filename}")
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