"""Render Bob's cat shell assembled (front 3/4 + side) from the STLs make_cat.py wrote.
usage: py -3 render_cat.py -> bob-cat-render.png
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
body, head, ear, tail, bottom = (L(n) for n in ("bob-body", "bob-head", "bob-ear", "bob-tail", "bob-bottom"))

# place the ears on the head's servo slots and the tail on the back slot (same numbers as make_cat.py)
hb = head.bounds
ears = []
for sx in (-1, 1):
    e = ear.copy()
    e.apply_transform(trimesh.transformations.rotation_matrix(sx * 0.18, (0, 1, 0)))   # slight outward tilt
    e.apply_translation((sx * 17.0, (hb[0][1] + hb[1][1]) / 2, hb[1][2] - 3))
    ears.append(e)
tail.apply_translation((0, 39.0, 18.0))

CREAM, GREY, PINK, DARK = [0.96, 0.95, 0.93], [0.78, 0.78, 0.8], [0.93, 0.45, 0.62], [0.35, 0.33, 0.35]
parts = [(bottom, DARK), (body, CREAM), (head, CREAM), (tail, GREY)] + [(e, PINK) for e in ears]

def shade(m, rgb, light=np.array([0.5, -0.8, 0.9])):
    n = m.face_normals
    k = 0.45 + 0.55 * np.clip(n @ (light / np.linalg.norm(light)), 0, 1)
    return np.clip(np.outer(k, rgb), 0, 1)

fig = plt.figure(figsize=(12, 7), facecolor="#f7f1e6")
for i, (elev, azim, title) in enumerate([(14, -62, "front 3/4"), (8, 0, "side")]):
    ax = fig.add_subplot(1, 2, i + 1, projection="3d", facecolor="#f7f1e6")
    for m, c in parts:
        ax.add_collection3d(Poly3DCollection(m.triangles, facecolors=shade(m, c), edgecolors="none"))
    allv = np.vstack([m.vertices for m, _ in parts])
    lo, hi = allv.min(0), allv.max(0); mid = (lo + hi) / 2; s = (hi - lo).max() / 2
    ax.set_xlim(mid[0] - s, mid[0] + s); ax.set_ylim(mid[1] - s, mid[1] + s); ax.set_zlim(mid[2] - s, mid[2] + s)
    ax.view_init(elev=elev, azim=azim); ax.set_axis_off(); ax.set_title(title, color="#2a2420")
fig.suptitle("Bob, cat shell: body + heart head (round screen window) + servo ears + servo tail", color="#6b5f52")
out = os.path.join(HERE, "bob-cat-render.png")
fig.savefig(out, dpi=140, bbox_inches="tight", facecolor=fig.get_facecolor())
print("saved", out, "| height", round(float(hi[2] - lo[2]), 1), "mm")
