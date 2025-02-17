from utils import *

import numpy as np
from trajectory_following import TrajFollower





waypoints = np.array([
					  [0.5, 0.0, 0.05, 3.1413, 0.0014, 0.0007, 0.],
					  [0.45, 0.25, 0.1, 3.1413, 0.0014, 0.0007, 1.],
                      [0.75, 0.25, 0.2, 3.1413, 0.0014, 0.0007, 1.],
                      [0.25, 0., 0.4, 3.1413, 0.0014, 0.0007, 0.],
					  ])


trajFollower = TrajFollower()
trajFollower._move(waypoints)



## initialize robot
# Robot = Franka3()
# print('[*] Connecting to robot...')
# conn_robot = Robot.connect2robot()
# print('    Successfully connected')

# Robot.go2home(conn_robot)
# Robot.go2pose(conn_robot, [0.8, 0.55, 0.05, 3.1413, 0.0014, 0.0007], _xyz=False, fix_orient=False)
# states = Robot.readState(conn_robot)
# print(states["xyz_euler"])
