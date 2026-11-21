"""Exploded view of Bob v3: every printed part pulled apart so you can see how he goes together.
usage: py -3 render_cat3_exploded.py -> bob3-exploded.png
"""
import os
import numpy as np
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

HERE = os.path.dirname(os.path.abspath(__file__))
L = lambda n: trimesh.load(os.path.join(HERE, n + ".stl"))
WHITE, GREY, PINK, DARK = [0.97, 0.97, 0.97], [0.80, 0.80, 0.83], [0.94, 0.42, 0.62], [0.33, 0.32, 0.34]
spec = [("bob3-bottom", DARK, (0, 0, -45)), ("bob3-body", WHITE, (0, 0, 0)), ("bob3-head", WHITE, (0, 0, 35)),
        ("bob3-head-back", WHITE, (0, 55, 35)), ("bob3-ear-L", PINK, (-15, 0, 75)), ("bob3-ear-R", PINK, (15, 0, 75))]
parts = []
for name, c, off in spec:
    m = L(name); m.apply_translation(off); parts.append((m, c))
tail = L("bob2-tail"); tail.apply_translation((-15.0, 75.0, 14.0)); parts.append((tail, GREY))

light = np.array([0.35, -0.85, 0.8]); light /= np.linalg.norm(light)
fig = plt.figure(figsize=(9, 11), facecolor="#f7f1e6")
ax = fig.add_subplot(111, projection="3d", facecolor="#f7f1e6")
for m, c in parts:
    k = 0.42 + 0.58 * np.clip(m.face_normals @ light, 0, 1)
    ax.add_collection3d(Poly3DCollection(m.triangles, facecolors=np.clip(np.outer(k, c), 0, 1), edgecolors="none"))
allv = np.vstack([m.vertices for m, _ in parts]); lo, hi = allv.min(0), allv.max(0); mid = (lo + hi) / 2; s = (hi - lo).max() / 2
ax.set_xlim(mid[0] - s, mid[0] + s); ax.set_ylim(mid[1] - s, mid[1] + s); ax.set_zlim(mid[2] - s, mid[2] + s)
ax.set_box_aspect((1, 1, 1), zoom=1.25); ax.view_init(elev=14, azim=-50); ax.set_axis_off()
ax.set_title("Bob v3, exploded: bottom plate, body, head + back cover, 2 ears, tail", color="#2a2420")
fig.savefig(os.path.join(HERE, "bob3-exploded.png"), dpi=110, bbox_inches="tight", facecolor=fig.get_facecolor())
print("ok")
