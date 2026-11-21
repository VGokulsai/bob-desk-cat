"""Render Bob v3 (all parts in place) next to Gokul's drawing.
usage: py -3 render_cat3.py -> bob3-render.png
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
body, head, earL, earR, bottom, hback = (L(n) for n in ("bob3-body", "bob3-head", "bob3-ear-L", "bob3-ear-R", "bob3-bottom", "bob3-head-back"))
tail = L("bob2-tail")
tail.apply_translation((-15.0, body.bounds[1][1] - 6, 14.0))      # on the tail servo slot, back wall

WHITE, GREY, PINK, DARK = [0.97, 0.97, 0.97], [0.80, 0.80, 0.83], [0.94, 0.42, 0.62], [0.33, 0.32, 0.34]
parts = [(bottom, DARK), (body, WHITE), (head, WHITE), (hback, WHITE), (tail, GREY), (earL, PINK), (earR, PINK)]
light = np.array([0.35, -0.85, 0.8]); light /= np.linalg.norm(light)

fig = plt.figure(figsize=(18, 8), facecolor="#f7f1e6")
art = plt.imread(os.path.join(HERE, "..", "..", "..", "face", "art", "bob-idle.png"))
ax0 = fig.add_subplot(1, 5, 1); ax0.imshow(art); ax0.set_axis_off(); ax0.set_title("your drawing", color="#2a2420")
allv = np.vstack([m.vertices for m, _ in parts]); lo, hi = allv.min(0), allv.max(0); mid = (lo + hi) / 2; s = (hi - lo).max() / 2
for i, (elev, azim, title) in enumerate([(3, -90, "front"), (15, -55, "front 3/4"), (3, 0, "side"), (15, 125, "back 3/4")]):
    ax = fig.add_subplot(1, 5, i + 2, projection="3d", facecolor="#f7f1e6")
    for m, c in parts:
        k = 0.42 + 0.58 * np.clip(m.face_normals @ light, 0, 1)
        ax.add_collection3d(Poly3DCollection(m.triangles, facecolors=np.clip(np.outer(k, c), 0, 1), edgecolors="none"))
    ax.set_xlim(mid[0] - s, mid[0] + s); ax.set_ylim(mid[1] - s, mid[1] + s); ax.set_zlim(mid[2] - s, mid[2] + s)
    ax.set_box_aspect((1, 1, 1), zoom=1.55); ax.view_init(elev=elev, azim=azim); ax.set_axis_off(); ax.set_title(title, color="#2a2420")
fig.suptitle(f"Bob v3, traced from your drawing: {hi[0]-lo[0]:.0f} mm wide, {hi[2]-lo[2]:.0f} mm tall to the ear tips", color="#6b5f52")
fig.savefig(os.path.join(HERE, "bob3-render.png"), dpi=115, bbox_inches="tight", facecolor=fig.get_facecolor())
print("ok", np.round(hi - lo, 1))
