"""Shaded render of Bob's shell (base + head) from the STLs: assembled and exploded views.
usage: py -3 render_shell.py -> bob-shell-render.png
"""
import os, struct
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

HERE = os.path.dirname(os.path.abspath(__file__))
BASE_H = 25.0          # base tray height: the head sits on top of it
LIFT = 30.0            # extra gap in the exploded view

def read_stl(path):
    data = open(path, "rb").read()
    if data[:5] == b"solid" and b"facet" in data[:300]:       # ASCII STL
        v = [list(map(float, l.split()[1:4])) for l in data.decode().splitlines() if l.strip().startswith("vertex")]
        return np.array(v).reshape(-1, 3, 3)
    n = struct.unpack("<I", data[80:84])[0]
    rec = np.frombuffer(data[84:84 + n * 50], dtype=np.dtype([("n", "<3f4"), ("v", "<9f4"), ("a", "<u2")]))
    return rec["v"].reshape(-1, 3, 3).astype(float)

def shade(tris, rgb, light=np.array([0.4, -0.7, 0.9])):
    nrm = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-9
    k = 0.55 + 0.45 * np.abs(nrm @ (light / np.linalg.norm(light)))     # two-sided so inner walls aren't black
    return np.clip(np.outer(k, rgb), 0, 1)

base = read_stl(os.path.join(HERE, "bob-base.stl"))
head = read_stl(os.path.join(HERE, "bob-head.stl"))
BASE_RGB, HEAD_RGB = np.array([0.88, 0.38, 0.23]), np.array([0.96, 0.78, 0.36])

def draw(ax, lift, title):
    h = head.copy()
    h[:, :, 2] += BASE_H + lift
    for t, c in ((base, BASE_RGB), (h, HEAD_RGB)):
        ax.add_collection3d(Poly3DCollection(t, facecolors=shade(t, c), edgecolors="none"))
    allv = np.concatenate([base.reshape(-1, 3), h.reshape(-1, 3)])
    lo, hi = allv.min(0), allv.max(0)
    span = (hi - lo).max() / 2
    mid = (hi + lo) / 2
    ax.set_xlim(mid[0] - span, mid[0] + span); ax.set_ylim(mid[1] - span, mid[1] + span); ax.set_zlim(mid[2] - span, mid[2] + span)
    ax.view_init(elev=22, azim=-60)
    ax.set_axis_off()
    ax.set_title(title, fontsize=13, color="#2a2420")

fig = plt.figure(figsize=(12, 6), facecolor="#f7f1e6")
for i, (lift, title) in enumerate([(0, "assembled"), (LIFT, "exploded: head lifted off the base")]):
    ax = fig.add_subplot(1, 2, i + 1, projection="3d", facecolor="#f7f1e6")
    draw(ax, lift, title)
fig.suptitle("Bob's shell: base tray 81 x 70.5 x 25 mm + head with face window and ear-servo slots", fontsize=12, color="#6b5f52")
out = os.path.join(HERE, "bob-shell-render.png")
fig.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
print("saved", out, "| base tris", len(base), "| head tris", len(head))
