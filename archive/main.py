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

- target x,y,z position (randomly generated for now)
- game control using the joystick
- robot's kinesthetic control
- distance between target and robot's end-effector 

"""

## initialize robot
Robot = Franka3()
print('[*] Connecting to robot...')
conn_robot = Robot.connect2robot()
print('    Successfully connected')

## send robot home
print('    Sending robot home')
Robot.go2home(conn_robot)

## initialize joystick
joystick = JoystickControl()



def loadTargets() -> np.ndarray:
	with open('targets.pkl', 'rb') as f:
		targets = pickle.load(f)
	return targets



def main(save_path: str, num: int, target: np.array, thresh: float=0.05):
	'''
	Instructions:
		- Connect to robot (no gripper) and joystick
		- Press A to start recording data
		- Switch to `Programming` mode
		- User moves the robot based on haptic feedback (yet to be implemented)
		- Switch to `Execution` mode
		- Press B to finish recording data
		- Press X to save recording data
		- Press Y to to return the robot home

	'''

	## parameters	
	record = False
	shutdown = False
	step_time = 0.1
	mode = "v"

	data = {"target":[],
		 	"distance":[],
			"joint_positions":[],
			"xyz_euler":[],
			}
	
	while not shutdown:

		## read robot states
		states = Robot.readState(conn_robot)
		q, xyz_euler = states["q"], states["xyz_euler"]
		distance = np.linalg.norm(target[:2] - xyz_euler[:2])
		if distance <= thresh:
			print("---- Reached to target!!")

		## read joystick commands
		A_pressed, B_pressed, X_pressed, Y_pressed, _, _ = joystick.getInput()
		
		if record:

			data["joint_positions"].append(q)
			data["xyz_euler"].append(xyz_euler)
			data["target"].append(target)
			data["distance"].append(distance)

			if B_pressed and (time.time() - last_time > step_time):
				print("---Finished Recording")
				mode = "v"
				record = False
		
		elif not record:

			if A_pressed:
				print("---Started Recording")
				mode = "d"
				record = True
				last_time = time.time()

			if X_pressed:
				with open(save_path + "/dem_" + str(num+1) + ".pkl", "wb") as file:
					pickle.dump(data, file)
				print("---Saved Recording")
			
			if X_pressed:
				print("---Robot Returning Home")
				Robot.go2home(conn_robot)
				shutdown = True
		
		## robot receive zero velocity command
		Robot.send2robot(conn_robot, [0., 0., 0., 0., 0., 0., 0.,], mode)

	print("[*] Recorded data:\n", data["xyz_euler"])



if __name__=="__main__": 
	"""
	You can set name of recordings as input arguments in terminal
	"""

	parser = argparse.ArgumentParser(description='Collecting user data')
	parser.add_argument('--name', help='choose folder name', type=str, default="none")
	args = parser.parse_args()

	targets = loadTargets()

	for num, target in enumerate(targets):
		print("[*] Recording ", num + 1)
		save_path = "user_data/{}/".format(args.name)
		if not os.path.exists(save_path):
			os.makedirs(save_path)
		main(save_path, num + 1, target)