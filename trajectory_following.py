from utils import *



class TrajFollower(object):
	
	## connect to Franka3 and gripper
	## In low-level computer
		# navigate to /libfranka/build/raadlab
		# run ./arm_control to connect to robot
		# run ./gripper_control to connect to gripper

	def __init__(self):
		## load workspace boundaries
		with open('config.yaml', 'r') as ymlfile:
			cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
		self.limit_x = cfg['workspace']['LIMIT_X']
		self.limit_y = cfg['workspace']['LIMIT_Y']
		self.limit_z = cfg['workspace']['LIMIT_Z']
	
		## initialize robot
		self.Robot = Franka3()
		print('[*] Connecting to robot...')
		self.conn_robot = self.Robot.connect2robot()
		print('    Successfully connected')

		## initialize gripper
		print('[*] Connecting to gripper...')
		self.conn_gripper = self.Robot.connect2gripper()
		print('    Successfully connected', '\n')
		
		## initialize joystick
		self.joystick = JoystickControl()

		## send robot home
		self._reset()

		## hyperparameters
		self.speed_gain = 5
		self.step = 0.25
		self.extra_steps = 60
		self.t_start, self.t_end = 0, 10



	"""
	- This method moves robot along a timed trajectory
	- a trajectory includes waypoints (>= 1)
	- input : xyz, eulers, gripper state
		- type: np.ndarray
		- dims: (1, 7)
	"""
	def _move(self, waypoints):
		## build a traj for each waypoint
		## trajectory (1, 8): time step, xyz, eulers, gripper state
		num_wp = waypoints.shape[0]
		for wp_idx in range(num_wp):

			print("\n[*] Reaching waypoint: {}".format(waypoints[wp_idx]))

			## trajectory timing
			traj = waypoints[wp_idx].reshape(1, 7)
			t_steps = np.arange(self.t_start, self.t_end + (self.extra_steps * self.step), self.step)
			total_wp_idx = len(t_steps) - 1
			times = np.linspace(self.t_start, self.t_end, 2)

			## binary gripper inputs
			traj[:, -1] = np.where(traj[:, -1] <= 0 , 0, 1)

			## inserting current state waypoint to row 0
			init_gripper_state = 0
			states = self.Robot.readState(self.conn_robot)
			start_waypoint = np.hstack((states["xyz_euler"], init_gripper_state))
			traj = np.insert(traj, 0, start_waypoint, axis=0) 

			## inserting time stamps
			traj = np.insert(traj, 0, times, axis=1)
			trajectory = TrajectoryBuilder(traj)

			run = True
			last_time = time.time()
			for idx, t in enumerate(t_steps):
				## robot's current state
				states = self.Robot.readState(self.conn_robot)
				curr_pose = states["xyz_euler"]
				## workspace violation check
				if not self._inWorkspace(curr_pose):
					print("[*] Workspace violation!!")
					break
				## sample ee positions
				w = trajectory.get_waypoint(t)
				w_pose, w_gripper = w[1:-1], w[-1]

				## operator external control
				last_time, run = self._operatorInput(last_time, run)

				## compute and send joint velocities
				if not run:
					self.Robot.send2robot(self.conn_robot, [0] * 7, mode="d")
				else:
					if int(0.7 * total_wp_idx) <= idx <= total_wp_idx:
						if (self.Robot.gripper_state != int(w_gripper)):
							self.Robot.send2gripper(self.conn_gripper, w_gripper, pause=True)
						xdot = np.zeros(6)
					else:
						xdot = self.Robot.robotAction(w_pose, curr_pose, traj_following=True)
					
					qdot = self.Robot.xdot2qdot(xdot, states) * self.speed_gain
					self.Robot.send2robot(self.conn_robot, qdot, mode="v")



	def _operatorInput(self, last_time, run, time_thresh=0.1):
			A, B, X, Y, _, _ = self.joystick.getInput()
			if A and run and (time.time() - last_time >= time_thresh):
				tqdm.write('[*] self.Robot paused!')
				last_time = time.time()
				run = False
			if B and not run:
				tqdm.write("[*] self.Robot moving!")
				last_time = time.time()
				run = True
			if X and not run:
				tqdm.write("[*] Opening gripper!")
				self.Panda.send2gripper(self.conn_gripper, 0, pause=True)
			if Y and not run:
				tqdm.write("[*] Closing gripper!")
				self.Panda.send2gripper(self.conn_gripper, 1, pause=True)

			return last_time, run


	def _inWorkspace(self, pose):
		outside = False
		if (self.limit_x[0] <= pose[0] <= self.limit_x[1]) and \
		   (self.limit_y[0] <= pose[1] <= self.limit_y[1]) and \
		   (self.limit_z[0] <= pose[2] <= self.limit_z[1]):
			outside = True
		return outside


	def _reset(self):
		## send robot home and open gripper
		self.Robot.send2gripper(self.conn_gripper, 0, pause=True)
		self.Robot.go2home(self.conn_robot)