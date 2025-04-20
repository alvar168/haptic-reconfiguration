from __future__ import annotations
from scipy.spatial import KDTree
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import numpy as np
import pickle


from utils import *

"""
This script:

- Generates 10 target positions in robot workspace
- Plots target positions
- Saves target positions

"""


## target positions
with open('config.yaml', 'r') as ymlfile:
	cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
limit_x = cfg['workspace']['LIMIT_X']
limit_y = cfg['workspace']['LIMIT_Y']
limit_z = cfg['workspace']['LIMIT_Z']
limit_z[1] = limit_z[0]


def generatePoints(n_points: str, limit_x: list, limit_y: list, limit_z: list, min_dist: float=0.1) -> np.ndarray:
	points = []
	ll, ul = np.array([limit_x[0], limit_y[0], limit_z[0]]), np.array([limit_x[1], limit_y[1], limit_z[1]])
	
	while len(points) < n_points:
		candidate = np.random.uniform(ll, ul)
		if all(np.linalg.norm(candidate - p) > min_dist for p in points):
			points.append(candidate)
	return np.array(points)


def plot(points: np.ndarray):
	fig = plt.figure(figsize=(8, 6))
	ax = fig.add_subplot(111, projection='3d')
	ax.scatter(*points.T, c='b', marker='o')

	theta = np.linspace(0, 2 * np.pi, 30)
	z = np.linspace(0, 0.6, 30) 
	theta, z = np.meshgrid(theta, z)

	r = 0.05
	x, y, z = r * np.cos(theta), r * np.sin(theta), z

	ax.plot_surface(x, y, z, color='r', alpha=0.6)
	ax.text(0, 0, 0.8, "Robot", color='black', fontsize=12, ha='center')
	ax.set_xlabel('X [m]')
	ax.set_ylabel('Y [m]')
	ax.set_zlabel('Z [m]')
	ax.set_title('Generated Target Points')
	ax.set_xlim(0, limit_x[1])
	ax.set_ylim(limit_y[0], limit_y[1])
	ax.set_zlim(limit_z[0], 1)
	plt.savefig("targets.png", dpi=300)
	plt.show()


def saveTargets(points: np.ndarray):
	with open('targets.pkl', 'wb') as f:
		pickle.dump(points, f)


n_points = 10
points = generatePoints(n_points, limit_x, limit_y, limit_z)
saveTargets(points)
plot(points)

