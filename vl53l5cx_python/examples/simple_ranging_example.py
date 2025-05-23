import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.collections as coll
import matplotlib.animation as animation
# import torch
# import torch.nn as nn

from vl53l5cx.vl53l5cx import VL53L5CX

def dist_to_color(dist):
    if dist == -1:
        return "#800080"
    
    # Clamp dist between 0 and 4000
    dist = max(0, min(dist, 4000))

    # Compute interpolation factor
    t = dist / 4000  # 0.0 (white) to 1.0 (purple)

    # Linear interpolation between white and purple
    r = int((1 - t) * 255 + t * 128)
    g = int((1 - t) * 255 + t * 0)
    b = int((1 - t) * 255 + t * 128)

    return f'#{r:02x}{g:02x}{b:02x}'

# Create figure and axis
fig, ax = plt.subplots(figsize=(6, 6))
ax.set_aspect('equal')
plt.axis('off')

# Create 8x8 grid of squares and store them
squares = []
for i in range(8):
    for j in range(8):
        sq = patches.Rectangle((i, j), 1, 1, edgecolor='black')
        ax.add_patch(sq)
        squares.append(sq)

# Set limits
ax.set_xlim(0, 8)
ax.set_ylim(0, 8)

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
print(driver.get_resolution)

# Ranging:
driver.start_ranging()

# Update function for animation also where sensor data is pulled
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
                distances.append(-1)

    for idx, sq in enumerate(squares):
        dist = distances[idx]
        color = dist_to_color(dist)
        sq.set_facecolor(color)

    return squares

# Create animation
ani = animation.FuncAnimation(fig, update, frames=100, interval=500, blit=False)

plt.show()

