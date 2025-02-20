from tqdm import tqdm
import numpy as np
import pygame
import socket
import time
import yaml

from scipy.interpolate import splprep, splev, interp1d
from scipy.spatial.transform import Rotation 
from scipy.spatial.transform import Slerp

np.set_printoptions(precision=4, suppress=True)



with open('config.yaml', 'r') as ymlfile:
	cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
HOME = cfg['positions']['robot_home_q']


########## Joystick ##########
class JoystickControl(object):

	def __init__(self):
		pygame.init()
		self.gamepad = pygame.joystick.Joystick(0)
		self.gamepad.init()
		self.deadband = 0.1
		self.timeband = 0.5
		self.lastpress = time.time()

	def getInput(self):
		pygame.event.get()
		curr_time = time.time()
		left_analog_x = self.gamepad.get_axis(1)
		left_analog_y = self.gamepad.get_axis(0)
		right_analog = self.gamepad.get_axis(4)
		left_analog_x = 0.0 if abs(left_analog_x) < self.deadband else left_analog_x
		left_analog_y = 0.0 if abs(left_analog_y) < self.deadband else left_analog_y
		right_analog = 0.0 if abs(right_analog) < self.deadband else right_analog
		A_pressed = self.gamepad.get_button(0) and (curr_time - self.lastpress > self.timeband)
		B_pressed = self.gamepad.get_button(1) and (curr_time - self.lastpress > self.timeband)
		X_pressed = self.gamepad.get_button(2) and (curr_time - self.lastpress > self.timeband)
		Y_pressed = self.gamepad.get_button(3) and (curr_time - self.lastpress > self.timeband)
		START_pressed = self.gamepad.get_button(7) and (curr_time - self.lastpress > self.timeband)
		BACK_pressed = self.gamepad.get_button(6) and (curr_time - self.lastpress > self.timeband)
		pressed_keys = [A_pressed, B_pressed, X_pressed, Y_pressed, START_pressed, left_analog_x, left_analog_y, right_analog]
		if any(pressed_keys):
			self.lastpress = curr_time
		return A_pressed, B_pressed, X_pressed, Y_pressed, (-left_analog_x, -left_analog_y, -right_analog), BACK_pressed


########## Franka Robot ##########
class Franka3(object):

	def __init__(self):
		self.gripper_states = ["o", "c"]
		self.JOINT_LIMITS = [
							(-2.7437, 2.7437),
							(-1.7838, 1.7837),
							(-2.9007, 2.9007),
							(-3.0421, -0.1518),
							(-2.8065, 2.8065),
							(0.5445, 4.5169),
							(-3.0159, 3.0159)]
		self.home_q = HOME
		self.home_pose = self.wrappedPose(HOME)


	def connect2robot(self, mode="v", PORT=8080):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind(('172.16.0.3', PORT))
		s.listen()
		conn, addr = s.accept()
		self.send2robot(conn, [0]*7, mode)
		return conn

	def connect2gripper(self, PORT=8081):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind(('172.16.0.3', PORT))
		s.listen(10)
		conn, addr = s.accept()
		return conn

	def send2gripper(self, conn, idx, pause=True):
		send_msg = "s," + self.gripper_states[int(idx)] + ","
		conn.send(send_msg.encode())
		if pause:
			time.sleep(1)
		self.gripper_state = int(idx)

	def send2robot(self, conn, qdot, mode, limit=1.0):
		qdot = np.asarray(qdot)
		scale = np.linalg.norm(qdot)
		if scale > limit:
			qdot *= limit/scale
		send_msg = np.array2string(qdot, precision=5, separator=',',suppress_small=True)[1:-1]
		if send_msg == '0.,0.,0.,0.,0.,0.,0.':
			send_msg = '0.00000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000'
		send_msg = "s," + send_msg + "," + mode + ","
		conn.send(send_msg.encode())

	def listen2robot(self, conn):
		state_length = 7 + 7 + 42
		message = str(conn.recv(2048))[2:-2]
		state_str = list(message.split(","))
		for idx in range(len(state_str)):
			if state_str[idx] == "s":
				state_str = state_str[idx+1:idx+1+state_length]
				break
		try:
			state_vector = [float(item) for item in state_str]
		except ValueError:
			return None
		if len(state_vector) is not state_length:
			return None
		state_vector = np.asarray(state_vector)
		states = {}
		states["q"] = state_vector[0:7]
		states["tau"] = state_vector[7:14]
		states["J"] = state_vector[14:].reshape((7,6)).T
		# get cartesian pose
		xyz_lin, R, _ = self.joint2pose(state_vector[0:7])
		beta = -np.arcsin(R[2,0])
		alpha = np.arctan2(R[2,1]/np.cos(beta),R[2,2]/np.cos(beta))
		gamma = np.arctan2(R[1,0]/np.cos(beta),R[0,0]/np.cos(beta))
		xyz_ang = [alpha, beta, gamma]
		states["xyz_euler"] = np.array(xyz_lin.tolist() + xyz_ang)
		return states

	def readState(self, conn):
		while True:
			states = self.listen2robot(conn)
			if states is not None:
				break
		return states

	def sampleJointPose(self):
		q_mid = np.array([l+(u-l)/2 for l, u in self.JOINT_LIMITS], dtype=np.float64)
		q_rand = np.array([np.random.uniform(l, u) for l, u in self.JOINT_LIMITS], dtype=np.float64)
		return q_mid, q_rand

	def xdot2qdot(self, xdot, states):
		J_inv = np.linalg.pinv(states["J"])
		return J_inv @ np.asarray(xdot)
	
	def wrappedPose(self, q):
		xyz, R, _ = self.joint2pose(q)
		eulers = self.matrix2euler(R)
		return np.concatenate((xyz, eulers))

	def joint2pose(self, q):
		def RotX(q):
			return np.array([[1, 0, 0, 0], [0, np.cos(q), -np.sin(q), 0], [0, np.sin(q), np.cos(q), 0], [0, 0, 0, 1]])
		def RotZ(q):
			return np.array([[np.cos(q), -np.sin(q), 0, 0], [np.sin(q), np.cos(q), 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
		def TransX(q, x, y, z):
			return np.array([[1, 0, 0, x], [0, np.cos(q), -np.sin(q), y], [0, np.sin(q), np.cos(q), z], [0, 0, 0, 1]])
		def TransZ(q, x, y, z):
			return np.array([[np.cos(q), -np.sin(q), 0, x], [np.sin(q), np.cos(q), 0, y], [0, 0, 1, z], [0, 0, 0, 1]])
		H1 = TransZ(q[0], 0, 0, 0.333)
		H2 = np.dot(RotX(-np.pi/2), RotZ(q[1]))
		H3 = np.dot(TransX(np.pi/2, 0, -0.316, 0), RotZ(q[2]))
		H4 = np.dot(TransX(np.pi/2, 0.0825, 0, 0), RotZ(q[3]))
		H5 = np.dot(TransX(-np.pi/2, -0.0825, 0.384, 0), RotZ(q[4]))
		H6 = np.dot(RotX(np.pi/2), RotZ(q[5]))
		H7 = np.dot(TransX(np.pi/2, 0.088, 0, 0), RotZ(q[6]))
		H_panda_hand = TransZ(-np.pi/4, 0, 0, 0.2105)
		T = np.linalg.multi_dot([H1, H2, H3, H4, H5, H6, H7, H_panda_hand])
		R = T[:,:3][:3]
		A = T[:3,:]
		xyz = T[:,3][:3]
		return xyz, R, A
	
	def go2home(self, conn):
		gain = 10
		total_time = 35.0
		start_time = time.time()
		states = self.readState(conn)
		q = np.asarray(states["q"].tolist())
		dist = np.linalg.norm(q - self.home_q)
		curr_time = time.time()
		action_time = time.time()
		elapsed_time = curr_time - start_time
		while dist > 0.05 and elapsed_time < total_time:
			q = np.asarray(states["q"].tolist())
			action_interval = curr_time - action_time
			if action_interval > 0.005:
				qdot = (self.home_q - q) * gain
				self.send2robot(conn, qdot, "v")
				action_time = time.time()
			states = self.readState(conn)
			dist = np.linalg.norm(q - self.home_q)
			curr_time = time.time()
			elapsed_time = curr_time - start_time
		if dist <= 0.01:
			return True
		elif elapsed_time >= total_time:
			return False

	def go2pose(self, conn_panda, pose, _xyz=False, fix_orient=False):
		goal = np.copy(pose)
		if _xyz:
			goal = np.concatenate((goal, self.home_pose[-3:]))
		run = True
		shutdown = False
		while not shutdown:
			states = self.readState(conn_panda)
			curr_pose = states["xyz_euler"]
			goal_pose = self.constrain2workspce(goal)
			if np.linalg.norm(goal_pose - curr_pose) < 0.015 and run:
				shutdown = True
				run = False
			xdot = self.robotAction(goal_pose, curr_pose, robot_working=run)
			qdot = self.xdot2qdot(xdot, states)
			self.send2robot(conn_panda, qdot, mode="v")
			## jacobian issues
			if fix_orient and self.orientChanged(curr_pose[3:], tol=np.deg2rad(5)):
				self.go2home(conn_panda)
		return curr_pose

	def robotAction(self, goal, cur_pose, action_scale=0.1, traj_following=False, robot_working=True):
		## xyz error
		robot_error_xyz = goal[:3] - cur_pose[:3]
		## orientation error
		curr_quat = Rotation.from_euler('xyz', cur_pose[3:], degrees=False).as_quat()
		goal_quat = Rotation.from_euler('xyz', goal[3:], degrees=False).as_quat()
		q_res = self.quatDiff(curr_quat, goal_quat)
		q_res = Rotation.from_quat(q_res)
		robot_error_orient = q_res.as_euler('xyz', degrees=False)
		## robot error
		robot_error = np.concatenate((robot_error_xyz, robot_error_orient))
		if traj_following:
			robot_action = robot_error
		else:
			if robot_working:
				if np.linalg.norm(robot_error) > 0.08:
					robot_action = robot_error
				else:
					robot_action = robot_error / np.linalg.norm(robot_error) * action_scale
			else:
				robot_action = np.zeros((6,))
		return robot_action

	def orientChanged(self, eulers, tol=np.deg2rad(10)):
		home_quat = Rotation.from_euler('xyz', self.home_pose[-3:], degrees=False).as_quat()
		curr_quat = Rotation.from_euler('xyz', eulers, degrees=False).as_quat()
		q_res = self.quatDiff(home_quat, curr_quat)
		roll_res, pitch_res, yaw_res = self.quat2euler(q_res)
		flag_roll, flag_pitch, flag_yaw = abs(roll_res) > tol, abs(pitch_res) > tol, abs(yaw_res) > tol
		if flag_roll or flag_pitch:
			tqdm.write("[*] Passed orientation limits!!!\n")
			not_oriented = True
		else:
			not_oriented = False
		return not_oriented

	def constrain2workspce(self, waypoints):
		with open('config.yaml', 'r') as ymlfile:
			cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
		limit_x = cfg['workspace']['LIMIT_X']
		limit_y = cfg['workspace']['LIMIT_Y']
		limit_z = cfg['workspace']['LIMIT_Z']
		assert limit_x[0]<limit_x[1] and limit_y[0]<limit_y[1] and limit_z[0]<limit_z[1],\
			"the limits for the workspace constraints are invalid (lower limit greater than higher limit)"
		if len(waypoints.shape) == 1:
			waypoints[0] = np.clip(waypoints[0], limit_x[0], limit_x[1])
			waypoints[1] = np.clip(waypoints[1], limit_y[0], limit_y[1])
			waypoints[2] = np.clip(waypoints[2], limit_z[0], limit_z[1])
		else:
			waypoints[:, 0] = np.clip(waypoints[:, 0], limit_x[0], limit_x[1])
			waypoints[:, 1] = np.clip(waypoints[:, 1], limit_y[0], limit_y[1])
			waypoints[:, 2] = np.clip(waypoints[:, 2], limit_z[0], limit_z[1])
		return waypoints

	def quatDiff(self, q1, q2):
		q1_inv = Rotation.from_quat(q1).inv()
		q2 = Rotation.from_quat(q2)
		diff = q2 * q1_inv
		return diff.as_quat()

	def matrix2quat(self, R):
		R_obj = Rotation.from_matrix(R)
		return R_obj.as_quat()
	
	def matrix2euler(self, R):
		R_obj = Rotation.from_matrix(R)
		return R_obj.as_euler('xyz', degrees=False)
	
	def matrix2rotvec(self, R):
		R_obj = Rotation.from_matrix(R)
		return R_obj.as_rotvec()
	
	def euler2matrix(self, angles):
		eulers_obj = Rotation.from_euler('xyz', angles)
		return eulers_obj.as_matrix()
	
	def euler2rotvec(self, angles):
		eulers_obj = Rotation.from_euler('xyz', angles)
		return eulers_obj.as_rotvec()
	
	def quat2euler(self, quat):
		quat_obj = Rotation.from_quat(quat)
		return quat_obj.as_euler('xyz', degrees=False)
	
	def rotvec2euler(self, rot_vec):
		rot_vec_obj = Rotation.from_rotvec(rot_vec)
		return rot_vec_obj.as_euler('xyz', degrees=False)
	

########## Trajectory ##########
class TrajectoryBuilder():

	def __init__(self, traj):
		self.t_start = traj[0,0]
		self.t_end = traj[-1, 0]
		self.total_time = self.t_end - self.t_start
		self.traj = traj
		self.times = self.traj[:, 0]
		## interpolating xyz
		self.interpolated_xyz = []
		for idx in range(4):
			self.interpolated_xyz.append(interp1d(self.times, self.traj[:, idx], kind='linear'))
		## interpolating ee orientation
		rotations = Rotation.from_euler('xyz', self.traj[:, 4:7], degrees=False)
		self.slerped_eulers = Slerp(self.times, rotations)
		# gripper positions
		self.gripper_state = self.traj[:,-1]   

	def get_gripper_action(self, sample_time):
		if sample_time in self.times:
			closest_gripper_idx = np.where(self.times==sample_time)
		else:
			closest_gripper_idx = np.searchsorted(self.times, sample_time) - 1
			closest_gripper_idx = np.clip(closest_gripper_idx, 0, len(self.times))
		return self.gripper_state[closest_gripper_idx]    
	
	def get_waypoint(self, t):
		t = np.clip(t, 0, self.t_end)
		waypoint = np.zeros(8)
		eulers = self.slerped_eulers(t).as_euler('xyz', degrees=False)
		for idx in range(4):
			waypoint[idx] = self.interpolated_xyz[idx](t)
		waypoint[4:7] = eulers
		waypoint[-1] = self.get_gripper_action(t)
		return waypoint