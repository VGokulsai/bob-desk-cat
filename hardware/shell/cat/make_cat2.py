"""Bob v2 shell, built to match Gokul's drawing (face/art/bob-idle.png): a tall, slim
sitting cat. Wide haunches + paws at the bottom (the board lives in there), a slim
torso, two straight front legs, a big heart-shaped head with the round screen window,
very tall pointy ears on the ear servos, and a tail on the tail servo.

Units mm. x = right, y = back (the face looks toward -y), z = up, origin = bottom centre.
Board (73 x 62.5) lies flat in the base, shifted BX to the right so the USB-C is near the wall.
Prints as separate parts: body (base + torso + legs), head, ear (x2), tail, bottom plate.
usage: py -3 make_cat2.py
"""
import os
import numpy as np
import trimesh
from trimesh.creation import icosphere, cylinder, box

HERE = os.path.dirname(os.path.abspath(__file__))
WALL = 2.4
# --- CHANGE THESE ------------------------------------------------------------------
BASE = dict(hx=40.0, hy=34.0, r=8.0, z0=8.0, z1=26.0)   # base block: outer 96 x 84 x 34 mm
BX = 6.0                                                 # board shift to the right (USB side)
HAUNCH = dict(x=24.0, y=6.0, z=28.0, a=(22.0, 30.0, 26.0))  # back haunches (ellipsoid semi-axes)
TORSO_LO = ((0.0, -2.0, 40.0), (25.0, 22.0, 6.0))      # torso bottom ellipse: centre, semi-axes
TORSO_HI = ((0.0, -6.0, 120.0), (17.0, 15.0, 6.0))     # torso top (neck)
CHEST = ((0.0, -12.0, 92.0), (18.0, 14.0, 30.0))       # chest bulge
HEAD = dict(z=163.0, y=-6.0, cheek_x=18.0, cheek_r=27.0, chin_z=-34.0, chin_r=9.0, depth=0.72)
WINDOW_D, WINDOW_DZ = 34.0, -4.0                       # GC9A01 window (viewing area 32.4 mm)
EAR = dict(h=85.0, w=30.0, t=6.0, x=20.0)              # ear height, base width, thickness, x position
SERVO = (23.5, 12.5)                                    # SG90 body
STANDOFF_H, STANDOFF_D, SCREW_D = 5.0, 5.2, 2.2
# ------------------------------------------------------------------------------------

def sphere(c, r, sub=3):
    s = icosphere(subdivisions=sub, radius=r); s.apply_translation(c); return s

def ellipsoid(c, axes, sub=3):
    s = icosphere(subdivisions=sub, radius=1.0); s.apply_scale(axes); s.apply_translation(c); return s

def hull(ms):
    return trimesh.util.concatenate(ms).convex_hull

def at(m, x, y, z):
    m = m.copy(); m.apply_translation((x, y, z)); return m

def rblock(hx, hy, z0, z1, r):
    return hull([sphere((sx * hx, sy * hy, z), r, 2) for sx in (-1, 1) for sy in (-1, 1) for z in (z0, z1)])

def shrink(axes, w):
    return tuple(max(a - w, 1.0) for a in axes)

def union(ms):
    out = ms[0]
    for m in ms[1:]:
        out = out.union(m)
    return out

# ---------------- body: base + haunches + torso ----------------
B = BASE
base_out = rblock(B["hx"], B["hy"], B["z0"], B["z1"], B["r"])
base_in = rblock(B["hx"], B["hy"], B["z0"], B["z1"], B["r"] - WALL)
base_in = hull([base_in, at(base_in, 0, 0, -40)])                # open bottom

haunch_out = [ellipsoid((sx * HAUNCH["x"], HAUNCH["y"], HAUNCH["z"]), HAUNCH["a"]) for sx in (-1, 1)]
haunch_in = [ellipsoid((sx * HAUNCH["x"], HAUNCH["y"], HAUNCH["z"]), shrink(HAUNCH["a"], WALL)) for sx in (-1, 1)]

torso_out = hull([ellipsoid(*TORSO_LO), ellipsoid(*TORSO_HI), ellipsoid(*CHEST)])
torso_in = hull([ellipsoid(TORSO_LO[0], shrink(TORSO_LO[1], WALL)), ellipsoid(TORSO_HI[0], shrink(TORSO_HI[1], WALL)),
                 ellipsoid(CHEST[0], shrink(CHEST[1], WALL))])
neck_open = at(cylinder(radius=10.0, height=30.0), TORSO_HI[0][0], TORSO_HI[0][1], TORSO_HI[0][2] + 4)

body = union([base_out] + haunch_out + [torso_out])
body = body.difference(union([base_in] + haunch_in + [torso_in, neck_open]))

# front legs + paws (solid), back paws on the haunches
for sx in (-1, 1):
    leg = hull([sphere((sx * 11.0, -18.0, 100.0), 7.0, 2), sphere((sx * 12.0, -36.0, 12.0), 6.0, 2)])
    paw = ellipsoid((sx * 13.0, -40.0, 5.0), (9.0, 11.0, 5.0), 2)
    bpaw = ellipsoid((sx * 40.0, -18.0, 5.0), (10.0, 14.0, 5.0), 2)
    body = body.union(leg).union(paw).union(bpaw)
body = body.difference(union([base_in] + haunch_in + [torso_in]))   # legs/paws stay outside, cavities stay clear

# keep the board space clear (legs/paws must not poke into it): board + 1.5 mm, up to 22 mm above the board
board_top = WALL + STANDOFF_H + 1.6
body = body.difference(at(box((73.0 + 3, 62.5 + 3, board_top + 22.0)), BX, 0, (board_top + 22.0) / 2 - 0.01))
# USB-C slot (right wall). Board USB centre: board y 5.68 from its back edge -> body y = 31.25 - 5.68
body = body.difference(at(box((30, 13, 7)), B["hx"] + B["r"], 31.25 - 5.68, board_top + 1.6))
# tail servo slot (back wall)
body = body.difference(at(box((SERVO[0], 30, SERVO[1])), 0, B["hy"] + B["r"], 18.0))
body = body.difference(at(box((400, 400, 100)), 0, 0, -50))      # flat bottom

# ---------------- head (heart: two cheeks + chin), separate part ----------------
H = HEAD
def head_shape(w):
    h = hull([sphere((sx * H["cheek_x"], 0, 0), H["cheek_r"] - w) for sx in (-1, 1)] +
             [sphere((0, 0, H["chin_z"]), H["chin_r"] - w)])
    h.apply_scale((1, H["depth"], 1)); return h

head = head_shape(0).difference(head_shape(WALL))
rot_y = trimesh.transformations.rotation_matrix(np.pi / 2, (1, 0, 0))
head = head.difference(at(cylinder(radius=WINDOW_D / 2, height=60, transform=rot_y), 0, -30, WINDOW_DZ))
head = head.difference(at(cylinder(radius=10.0, height=20), 0, 0, H["chin_z"] - H["chin_r"] + 4))      # neck hole
for sx in (-1, 1):
    head = head.difference(at(box((SERVO[0], SERVO[1], 14)), sx * EAR["x"], 0, H["cheek_r"] - 3))     # ear servo slots
head.apply_translation((0, H["y"], H["z"]))

# ---------------- ear (print 2): tall flat pointed triangle ----------------
E = EAR
ear = hull([at(box((E["w"], E["t"], 2.0)), 0, 0, 1.0), at(cylinder(radius=1.0, height=1.0), 0, 0, E["h"])])
ear = ear.difference(at(cylinder(radius=1.1, height=10), 0, 0, 3))          # horn screw
ear = ear.difference(at(box((7, 3.5, 6)), 0, 0, 1.5))                       # horn arm pocket

# ---------------- tail ----------------
t = np.linspace(0, 1, 16)
pts = np.c_[10 * np.sin(t * np.pi * 0.8), 4 + 22 * t, 2 + 80 * t ** 1.3]
tail = hull([sphere(pts[0], 5.5, 2), sphere(pts[1], 5.3, 2)])
for a, b in zip(pts[1:-1], pts[2:]):
    tail = tail.union(hull([sphere(a, 5.0, 2), sphere(b, 4.4, 2)]))
tail = tail.union(at(box((12, 6, 8)), 0, 0, 4)).difference(at(cylinder(radius=1.1, height=10), 0, 0, 4))

# ---------------- bottom plate + standoffs ----------------
plate = rblock(B["hx"], B["hy"], 0, 0, B["r"] - WALL - 0.3).intersection(at(box((400, 400, WALL)), 0, 0, WALL / 2))
for bxh, byh in ((3.4, 3.5), (3.5, 52.0), (70.0, 59.5)):                   # board mounting holes
    x, y = bxh - 36.5 + BX, 31.25 - byh
    plate = plate.union(at(cylinder(radius=STANDOFF_D / 2, height=STANDOFF_H), x, y, WALL + STANDOFF_H / 2))
    plate = plate.difference(at(cylinder(radius=SCREW_D / 2, height=20), x, y, WALL + 5))

parts = {"bob2-body": body, "bob2-head": head, "bob2-ear": ear, "bob2-tail": tail, "bob2-bottom": plate}
for name, m in parts.items():
    m.export(os.path.join(HERE, name + ".stl"))
    print(f"{name:12s} watertight={m.is_watertight} size={np.round(m.extents, 1)} mm vol={m.volume / 1000:.1f} cm3")

# fit checks: the board box must not hit the body, the plate must fit in the opening
board = at(box((73.0, 62.5, 1.6 + 22.0)), BX, 0, WALL + STANDOFF_H + (1.6 + 22.0) / 2)
print("board-vs-body overlap cm3:", round(board.intersection(body).volume / 1000, 3))
print("plate-vs-body overlap cm3:", round(plate.intersection(body).volume / 1000, 3))
print("head bottom z:", round(head.bounds[0][2], 1), "| torso top z:", round(TORSO_HI[0][2] + TORSO_HI[1][2], 1))
