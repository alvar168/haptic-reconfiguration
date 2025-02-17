import numpy as np
import argparse
import pickle
import time
import os

from utils import *
np.set_printoptions(suppress=True)




## initialize robot
Robot = Franka3()
print('[*] Connecting to robot...')
conn_robot = Robot.connect2robot()
print('    Successfully connected')

## initialize gripper
print('[*] Connecting to gripper...')
conn_gripper = Robot.connect2gripper()
print('    Successfully connected', '\n')

## initialize joystick
joystick = JoystickControl()





def main(save_path, num):

	'''
	A: start recording
	B: stop recording
	'''
	## parameters	
	done = False
	record = False
	shutdown = False
	step_time = 0.1
	gripper_state = 0

	data = {"joint_positions":[],
			"xyz_euler":[],
			"rotation_matrices":[],
			"gripper":[]
			}
	while not shutdown:
		## read robot states
		states = Robot.readState(conn_robot)
		q, xyz_euler = states["q"], states["xyz_euler"]
		_, R, _ = Robot.joint2pose(q)

		## read joystick commands
		A_pressed, B_pressed, X_pressed, Y_pressed, _, BACK_pressed = joystick.getInput()
		
		if A_pressed and not record:
			record = True
			last_time = time.time()
			print("---Ready to Record")
		
		if B_pressed and record and (time.time() - last_time > step_time):
			print("---Finished Recording")
			data["joint_positions"].append(q)
			data["xyz_euler"].append(xyz_euler)
			data["rotation_matrices"].append(R)
			data["gripper"].append(gripper_state)
			record = False
			done = True

		if BACK_pressed and done:
			with open(save_path + "/dem_" + str(num+1) + ".pkl", "wb") as file:
				pickle.dump(data, file)
			print("---Saved Demonstration")
			Robot.go2home(conn_robot)

			# if gripper_state == 1:
			Robot.send2gripper(conn_gripper, 0)

			print('---Panda returned home...', '\n')
			shutdown = True

		if Y_pressed and record:
			gripper_state = 0
			Robot.send2gripper(conn_gripper, gripper_state, False)

		if X_pressed and record:
			gripper_state = 1
			Robot.send2gripper(conn_gripper, gripper_state, False)
		

if __name__=="__main__": 
	parser = argparse.ArgumentParser(description='Collecting demonstrations')
	parser.add_argument('--name', help='choose folder name', type=str, default="none")
	parser.add_argument('--num', help='how many demonstrations?', type=str, default="1")
	args = parser.parse_args()
	
	
	for num in range(int(args.num)):
		print("[*] Recording Demonstration ", num + 1)
		## saving directory			
		save_path = "dems/{}/".format(args.name)
		if not os.path.exists(save_path):
			os.makedirs(save_path)
		main(save_path, num)