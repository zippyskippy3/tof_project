import time
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D

from vl53l5cx.vl53l5cx import VL53L5CX

# Simulate VL53L5CX data structure
# Replace this with actual driver data when ready

# === ANGLE GRID GENERATION ===
def get_direction_grid(fov_x_deg=45.0, fov_y_deg=45.0, res_x=8, res_y=8):
    angles = []
    for y in range(res_y):
        row = []
        for x in range(res_x):
            theta_x = (x - (res_x - 1) / 2) * (fov_x_deg / res_x)
            theta_y = ((res_y - 1) / 2 - y) * (fov_y_deg / res_y)
            row.append((math.radians(theta_x), math.radians(theta_y)))
        angles.append(row)
    return np.array(angles)

def polar_to_cartesian(dist_mm, theta_x, theta_y):
    dist = dist_mm / 1000.0  # mm to meters
    x = dist * math.tan(theta_x)
    y = dist * math.tan(theta_y)
    z = dist
    return [x, y, z]

angle_grid = get_direction_grid()

# === CONVERT RANGE DATA TO POINT CLOUD ===
def get_point_cloud(ranging_data):
    points = []
    for y in range(8):
        for x in range(8):
            dist = ranging_data[y, x]
            if dist < 4000:
                theta_x, theta_y = angle_grid[y][x]
                pt = polar_to_cartesian(dist, theta_x, theta_y)
                points.append(pt)
    return np.array(points)

# === PLOTTING SETUP ===
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
scat = ax.scatter([], [], [], c='purple')

ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.set_zlim(0, 4)

# Start getting data
driver = VL53L5CX()

alive = driver.is_alive()
if not alive:
    raise IOError("VL53L5CX Device is not alive")

print("Initialising...")
t = time.time()
driver.init()
print(f"Initialised ({time.time() - t:.1f}s)")

# Set resolution to 8x8
driver.set_resolution(64)

# === ANIMATION UPDATE FUNCTION ===
def update(frame):

    if driver.check_data_ready():
        ranging_data = driver.get_ranging_data()
        print(ranging_data)

        for i in range(64):
            
            # Create an array of all ranging data from the 8x8 reading
            distance = ranging_data.distance_mm[driver.nb_target_per_zone * i]
            distances = []

            if distance < 4000:
                distances.append(distance)
                print(distance)
            else:
                # Check if distance is too far to be properly read if so, replace with meaningless point
                distances.append(4000)

    # Simulate an 8x8 array of distances in mm
    #data = np.random.randint(200, 2000, (8, 8))  # random distances between 20cm and 2m
    points = get_point_cloud(distances)

    if len(points) == 0:
        return scat,

    scat._offsets3d = (points[:, 0], points[:, 1], points[:, 2])
    return scat,

ani = animation.FuncAnimation(fig, update, frames=None, interval=75, blit=False)
plt.show()