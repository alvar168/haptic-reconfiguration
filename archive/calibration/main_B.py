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


def loadHapticSignals() -> list:
    """Load haptic signal parameters for each trial and shuffle order."""
    with open('haptic_signals_patterns_2.json', 'r', encoding="utf-8") as f:
	# with open('haptic_signals.json', 'r', encoding="utf-8") as f:
        data = json.load(f)  # Load as a dictionary
    
    # Extract the list of haptic signals
    signals = data.get("haptic_signals", [])  # Ensure it exists, or return an empty list
    random.shuffle(signals)  # Shuffle the trials for random order
    return signals


def send_haptic_signal(haptic_signal):
    """Send haptic signal to Arduino via serial."""
    signal_str = ",".join(map(str, haptic_signal["solenoids"]))  # Extract solenoid numbers
    arduino.flush()
    time.sleep(0.1)
    arduino.write((signal_str + "\n").encode())  # Send to Arduino
    print(f"[*] Sending haptic signal: {signal_str} ({haptic_signal['direction']})")

def send_end_signal():
    """Send '0' to Arduino to deflate all solenoids."""
    arduino.write(b"0\n")
    print("[*] Sending deflate signal: 0")

def save_trial_order():
    trial_order_file = os.path.join(save_path, "trial_order.json")
    with open(trial_order_file, "w") as f:
        json.dump(haptic_signals, f, indent=4)
    print(f"[*] Saved trial order to {trial_order_file}")
    
def load_or_generate_trials(save_path):
    """Load randomized trials if they exist, otherwise generate and save them."""
    trial_order_file = os.path.join(save_path, "trial_order.json")
    
    if os.path.exists(trial_order_file):
        print("[*] Loading saved trial order.")
        with open(trial_order_file, "r") as f:
            haptic_signals = json.load(f)
    else:
        print("[*] Generating new randomized trial order.")
        haptic_signals = loadHapticSignals()  # Randomize trials
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
				# Convert NumPy arrays to lists before saving
				data_serializable = {
					"time": data["time"],
					"joint_positions": [list(q) for q in data["joint_positions"]],  # Convert arrays to lists
					"xyz_euler": [list(xyz) for xyz in data["xyz_euler"]],  # Convert arrays to lists
					"haptic_signal": data["haptic_signal"]  # Already a list
				}

				trial_filename = os.path.join(save_path, f"trial_{num+1}.json")
				with open(trial_filename, "w") as file:
					json.dump(data_serializable, file, indent=4)

				print(f"--- Saved Trial as {trial_filename}")
				shutdown = True



if __name__=="__main__": 
	"""
	You can set name of recordings as input arguments in terminal
	"""

	parser = argparse.ArgumentParser(description='Collecting haptic feedback data')
	parser.add_argument('--name', help='choose folder name', type=str, default="none")
	args = parser.parse_args()

	save_path = f"user_data/{args.name}/"
	os.makedirs(save_path, exist_ok=True)
      
	# haptic_signals = loadHapticSignals()
	haptic_signals = load_or_generate_trials(save_path)

	print(f"Total haptic signals loaded: {len(haptic_signals)}")
	total_trials = len(haptic_signals)
      
	completed_trials = get_completed_trials(save_path)

	for num, haptic_signal in enumerate(haptic_signals):
		if (num + 1) in completed_trials:
			print(f"[*] Skipping trial {num + 1}, already completed.")
			continue  # Skip if already done
		main(save_path, num, haptic_signal)