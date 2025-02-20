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
conn_robot = Robot.connect2robot(mode="d")
print('    Successfully connected')

## initialize joystick
joystick = JoystickControl()


## target positions
with open('config.yaml', 'r') as ymlfile:
	cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
limit_x = cfg['workspace']['LIMIT_X']
limit_y = cfg['workspace']['LIMIT_Y']
limit_z = cfg['workspace']['LIMIT_Z']
target = np.random.uniform([limit_x[0], limit_y[0], limit_z[0]], [limit_x[1], limit_y[1], limit_z[1]], 3)



def main(save_path, num):
	'''
	Instructions:
	
		- Connect to robot (no gripper) and joystick
		- Switch off Execution mode on Franka Desk
		- Use preferred Guiding mode (optional)
		- Press A to start recording data
		- User moves the robot based on haptic feedback (yet to be implemented)
		- Press B to finish recording data
		- Press X to save recording data
		- Press Y to send robot home
	
	** this process actually repeates for "num" times
	'''
	## parameters	
	record = False
	shutdown = False
	step_time = 0.1

	data = {"target":[],
		 	"distance":[],
			"joint_positions":[],
			"xyz_euler":[],
			}
	
	while not shutdown:

		## read robot states
		states = Robot.readState(conn_robot)
		q, xyz_euler = states["q"], states["xyz_euler"]
		print(f"XYZ Position: {xyz_euler[:3]}")

		## read joystick commands
		A_pressed, B_pressed, X_pressed, Y_pressed, _, _ = joystick.getInput()
		
		if record:

			data["joint_positions"].append(q)
			data["xyz_euler"].append(xyz_euler)
			data["target"].append(target)
			data["distance"].append(np.linalg.norm(target - xyz_euler[:3]))

			if B_pressed and (time.time() - last_time > step_time):
				print("---Finished Recording")
				record = False
		
		elif not record:

			if A_pressed:
				print("---Started Recording!")
				record = True
				last_time = time.time()

			if X_pressed:
				with open(save_path + "/dem_" + str(num+1) + ".pkl", "wb") as file:
					pickle.dump(data, file)
				print("---Saved Recording")
				
			if Y_pressed:
				print('---Robot Returing Home...', '\n')
				Robot.go2home(conn_robot)
				shutdown = True

	print(data["xyz_euler"])



if __name__=="__main__": 
	"""
	You can set name and number of recordings as input arguments in terminal
	"""

	parser = argparse.ArgumentParser(description='Collecting user data')
	parser.add_argument('--name', help='choose folder name', type=str, default="none")
	parser.add_argument('--num', help='how many demonstrations?', type=str, default="1")
	args = parser.parse_args()

	for num in range(int(args.num)):
		print("[*] Recording ", num + 1)
		## saving directory			
		save_path = "user_data/{}/".format(args.name)
		if not os.path.exists(save_path):
			os.makedirs(save_path)
		main(save_path, num)