import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

r = np.arange(1, 0, -0.1)

fig, ax = plt.subplots(1)
ax.set_xlim([-1.1, 1.1])
ax.set_ylim([-1.1, 1.1])
patches = []

colors = np.array([0.9, 0.8, 0.1, 0.1, 0.1, 0.4, 0.2, 0.8, 0.1, 0.9])

phi = np.linspace(0, 2*np.pi, 200)

for radius in r:
    x = radius * np.cos(phi)
    y = radius * np.sin(phi)
    points = np.vstack([x, y]).T
    # print(points)
    polygon = Polygon(points, False)
    print(polygon)
    patches.append(polygon)
print(patches)
p = PatchCollection(patches, cmap="Blues")
p.set_array(colors)

ax.add_collection(p)

plt.show()