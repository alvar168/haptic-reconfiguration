from __future__ import annotations
import numpy as np
import argparse
import pickle
import time
import yaml
import os

from utils import *


"""
Functionalities defined in this script:

- Initialize robot
- User moves to home position
- Haptic feedback instructions sent to Arduino
- User moves based on haptic feedback
- Position & time data recorded

"""

## initialize robot
Robot = Franka3()
print('[*] Connecting to robot...')
conn_robot = Robot.connect2robot(mode="d")
print('    Successfully connected')

## initialize joystick
joystick = JoystickControl()

def loadHapticSignals() -> list:
    """Load haptic signal parameters for each trial."""
    with open('haptic_signals.pkl', 'rb') as f:
        signals = pickle.load(f)
    return signals

def send_haptic_signal(haptic_signal):
    """Send haptic signal to Arduino (implement this as needed)."""
    print(f"[*] Sending haptic signal: {haptic_signal}")
    # Add code to communicate with Arduino via serial, e.g., using pyserial


def main(save_path: str, num: int, haptic_signal: np.array, thresh: float=0.05):
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
				with open(save_path + "/trial_" + str(num+1) + ".pkl", "wb") as file:
					pickle.dump(data, file)
				print("---Saved Trial")
				shutdown = True

	# print("[*] Recorded data:\n", data["xyz_euler"])
	# print("[*] Recorded data \n")



if __name__=="__main__": 
	"""
	You can set name of recordings as input arguments in terminal
	"""

	parser = argparse.ArgumentParser(description='Collecting haptic feedback data')
	parser.add_argument('--name', help='choose folder name', type=str, default="none")
	args = parser.parse_args()

	haptic_signals = loadHapticSignals()
	total_trials = len(haptic_signals)

	for num, haptic_signal in enumerate(haptic_signals):
		# print("[*] Trial ", num + 1)
		save_path = "user_data/{}/".format(args.name)
		if not os.path.exists(save_path):
			os.makedirs(save_path)
		main(save_path, num, haptic_signal)