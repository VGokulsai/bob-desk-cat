"""Body shell alone, from 3 angles. usage: py -3 render_body.py -> bob-body-views.png"""
import os, numpy as np, trimesh, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
HERE = os.path.dirname(os.path.abspath(__file__))
m = trimesh.load(os.path.join(HERE, "bob-body.stl"))
L = np.array([0.5, -0.8, 0.9]); L = L / np.linalg.norm(L)
col = np.clip(np.outer(0.45 + 0.55 * np.clip(m.face_normals @ L, 0, 1), [0.96, 0.95, 0.93]), 0, 1)
fig = plt.figure(figsize=(15, 5.5), facecolor="#f7f1e6")
lo, hi = m.bounds; mid = (lo + hi) / 2; s = (hi - lo).max() / 2
for i, (e, a, t) in enumerate([(12, -90, "front"), (25, -55, "front 3/4"), (35, 120, "back 3/4 (tail slot, USB-C slot)")]):
    ax = fig.add_subplot(1, 3, i + 1, projection="3d", facecolor="#f7f1e6")
    ax.add_collection3d(Poly3DCollection(m.triangles, facecolors=col, edgecolors="none"))
    ax.set_xlim(mid[0]-s, mid[0]+s); ax.set_ylim(mid[1]-s, mid[1]+s); ax.set_zlim(mid[2]-s, mid[2]+s)
    ax.view_init(elev=e, azim=a); ax.set_axis_off(); ax.set_title(t, color="#2a2420")
fig.suptitle(f"Bob's body shell: {hi[0]-lo[0]:.0f} x {hi[1]-lo[1]:.0f} x {hi[2]-lo[2]:.0f} mm, 2.4 mm walls, open bottom for the board plate", color="#6b5f52")
fig.savefig(os.path.join(HERE, "bob-body-views.png"), dpi=130, bbox_inches="tight", facecolor=fig.get_facecolor())
print("ok")
