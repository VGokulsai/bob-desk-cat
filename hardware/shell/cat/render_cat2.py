"""Render Bob v2 assembled (front, 3/4, side) next to Gokul's drawing.
usage: py -3 render_cat2.py -> bob2-render.png
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
body, head, ear, tail, bottom = (L(n) for n in ("bob2-body", "bob2-head", "bob2-ear", "bob2-tail", "bob2-bottom"))

hb = head.bounds
ears = []
for sx in (-1, 1):                                   # ears on the servo slots, splayed out like the drawing
    e = ear.copy()
    e.apply_transform(trimesh.transformations.rotation_matrix(sx * 0.22, (0, 1, 0)))
    e.apply_translation((sx * 20.0, (hb[0][1] + hb[1][1]) / 2, hb[1][2] - 4))
    ears.append(e)
tail.apply_translation((6.0, 42.0, 14.0))

WHITE, GREY, PINK, DARK = [0.97, 0.97, 0.97], [0.80, 0.80, 0.83], [0.94, 0.42, 0.62], [0.33, 0.32, 0.34]
parts = [(bottom, DARK), (body, WHITE), (head, WHITE), (tail, GREY)] + [(e, PINK) for e in ears]
light = np.array([0.4, -0.85, 0.8]); light /= np.linalg.norm(light)

fig = plt.figure(figsize=(16, 8), facecolor="#f7f1e6")
art = plt.imread(os.path.join(HERE, "..", "..", "..", "face", "art", "bob-idle.png"))
ax0 = fig.add_subplot(1, 4, 1); ax0.imshow(art); ax0.set_axis_off(); ax0.set_title("your drawing", color="#2a2420")
allv = np.vstack([m.vertices for m, _ in parts]); lo, hi = allv.min(0), allv.max(0); mid = (lo + hi) / 2; s = (hi - lo).max() / 2
for i, (elev, azim, title) in enumerate([(5, -90, "front"), (15, -60, "front 3/4"), (5, 0, "side")]):
    ax = fig.add_subplot(1, 4, i + 2, projection="3d", facecolor="#f7f1e6")
    for m, c in parts:
        k = 0.42 + 0.58 * np.clip(m.face_normals @ light, 0, 1)
        ax.add_collection3d(Poly3DCollection(m.triangles, facecolors=np.clip(np.outer(k, c), 0, 1), edgecolors="none"))
    ax.set_xlim(mid[0] - s, mid[0] + s); ax.set_ylim(mid[1] - s, mid[1] + s); ax.set_zlim(mid[2] - s, mid[2] + s)
    ax.set_box_aspect((1, 1, 1), zoom=2.0); ax.view_init(elev=elev, azim=azim); ax.set_axis_off(); ax.set_title(title, color="#2a2420")
fig.suptitle(f"Bob v2 shell: {hi[0]-lo[0]:.0f} mm wide, {hi[2]-lo[2]:.0f} mm tall to the ear tips", color="#6b5f52")
fig.savefig(os.path.join(HERE, "bob2-render.png"), dpi=120, bbox_inches="tight", facecolor=fig.get_facecolor())
print("ok", round(float(hi[2] - lo[2]), 1))
