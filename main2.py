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

while True:
    states = Robot.readState(conn_robot)
    q, xyz_euler = states["q"], states["xyz_euler"]
    print(states)