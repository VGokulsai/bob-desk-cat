"""Bob's cat-shaped shell, shaped after Gokul's drawing (face/art/bob-idle.png):
heart-shaped head with a round window for the 1.28" screen, tall pointy ears on the
two ear servos, a sitting body that holds the 73 x 62.5 mm board, front paws, a tail on
the tail servo, and a bottom plate with the 3 M2.5 standoffs.

Units mm. Body frame: x = right, y = back (front face is -y), z = up, origin = bottom centre.
Board sits flat, centred, USB-C facing +x. Numbers come from ../../SHELL-SPEC.md.
usage: py -3 make_cat.py  -> bob-body.stl bob-head.stl bob-ear.stl (print x2) bob-tail.stl bob-bottom.stl
"""
import os
import numpy as np
import trimesh
from trimesh.creation import icosphere, cylinder, box

HERE = os.path.dirname(os.path.abspath(__file__))
WALL = 2.4
# --- CHANGE THESE ----------------------------------------------------------------
BODY_HALF = (34.0, 29.0)        # centres of the body's corner spheres (x, y)
BODY_R = 10.0                   # corner roundness of the body
CHEST = (0.0, -12.0, 44.0, 24.0)  # chest sphere: x, y, z, radius (makes the sitting slope)
HEAD_Z = 88.0                   # head centre height
HEAD_CHEEK = (15.0, 21.0)       # cheek sphere x offset, radius (wide top of the heart)
HEAD_CHIN = (-22.0, 9.0)        # chin sphere z offset, radius (pointy bottom of the heart)
HEAD_DEPTH = 0.78               # squash front-to-back
WINDOW_D = 34.0                 # face window for the GC9A01 (viewing area 32.4)
EAR_H = 42.0                    # ear height
SERVO = (23.5, 12.5)            # SG90 body footprint
STANDOFF_H, STANDOFF_D, SCREW_D = 5.0, 5.2, 2.2
# ---------------------------------------------------------------------------------

def sphere(c, r, sub=3):
    s = icosphere(subdivisions=sub, radius=r)
    s.apply_translation(c)
    return s

def hull(meshes):
    return trimesh.util.concatenate(meshes).convex_hull

def rounded_block(hx, hy, z0, z1, r, sub=3):
    pts = [sphere((sx * hx, sy * hy, z), r, sub) for sx in (-1, 1) for sy in (-1, 1) for z in (z0, z1)]
    return hull(pts)

def at(m, x, y, z):
    m = m.copy(); m.apply_translation((x, y, z)); return m

# ---------- body ----------
def body_shape(shrink):
    r = BODY_R - shrink
    block = rounded_block(BODY_HALF[0], BODY_HALF[1], BODY_R, 24.0, r)
    chest = sphere(CHEST[:3], CHEST[3] - shrink)
    return hull([block, chest])

outer = body_shape(0.0)
inner = body_shape(WALL)
inner_open = hull([inner, at(inner, 0, 0, -30)])          # extend the cavity down: open bottom
body = outer.difference(inner_open)
body = body.difference(at(box((300, 300, 100)), 0, 0, -50))  # flat bottom at z = 0

# neck hole (screen wires go up into the head)
body = body.difference(at(cylinder(radius=11, height=40), CHEST[0], CHEST[1], CHEST[2] + CHEST[3]))
# USB-C slot, right wall: board USB centre is at board y 5.68 -> body y = 31.25 - 5.68; z = plate + standoff + board
usb_y, usb_z = 31.25 - 5.68, WALL + STANDOFF_H + 1.6 + 1.6
body = body.difference(at(box((20, 13, 7)), BODY_HALF[0] + BODY_R, usb_y, usb_z))
# tail servo slot, back wall, low down
tail_x, tail_z = 0.0, 22.0
body = body.difference(at(box((SERVO[0], 20, SERVO[1])), tail_x, BODY_HALF[1] + BODY_R, tail_z))

# front legs and paws (outside, solid), back paws on the haunches
for sx in (-1, 1):
    leg = hull([sphere((sx * 11, -BODY_HALF[1] - BODY_R + 2, 6), 6.0, 2),
                sphere((sx * 9, CHEST[1] - CHEST[3] + 6, CHEST[2] - 4), 6.0, 2)])
    paw = sphere((sx * 12, -BODY_HALF[1] - BODY_R - 2, 4), 7.0, 2)
    paw.apply_scale((1, 1, 0.6)); paw.apply_translation((0, 0, 4 - paw.bounds[0][2]))
    back_paw = sphere((sx * (BODY_HALF[0] + BODY_R - 2), -6, 4), 8.0, 2)
    back_paw.apply_scale((0.8, 1.2, 0.55)); back_paw.apply_translation((0, 0, 3 - back_paw.bounds[0][2]))
    body = body.union(leg).union(paw).union(back_paw)
body = body.difference(at(box((300, 300, 100)), 0, 0, -50))

# ---------- head (heart shape: two cheeks + a chin) ----------
def head_shape(shrink):
    parts = [sphere((sx * HEAD_CHEEK[0], 0, 0), HEAD_CHEEK[1] - shrink) for sx in (-1, 1)]
    parts.append(sphere((0, 0, HEAD_CHIN[0]), HEAD_CHIN[1] - shrink))
    h = hull(parts); h.apply_scale((1, HEAD_DEPTH, 1)); return h

head = head_shape(0).difference(head_shape(WALL))
head = head.difference(at(cylinder(radius=WINDOW_D / 2, height=60,
                                   transform=trimesh.transformations.rotation_matrix(np.pi / 2, (1, 0, 0))), 0, -20, -4))
head = head.difference(at(cylinder(radius=11, height=30), 0, 0, HEAD_CHIN[0] - 4))   # neck hole
ear_x = HEAD_CHEEK[0] + 2
for sx in (-1, 1):   # ear servo slots through the top
    head = head.difference(at(box((SERVO[0], SERVO[1], 30)), sx * ear_x, 0, HEAD_CHEEK[1] - 2))
head.apply_translation((0, CHEST[1], HEAD_Z))

# ---------- ear (print 2): tall pointy flat cone with a socket for the servo horn ----------
ear = hull([at(cylinder(radius=1.0, height=1.0), 0, 0, EAR_H),
            at(box((20, 7, 2)), 0, 0, 1)])
ear = ear.difference(at(cylinder(radius=1.1, height=8), 0, 0, 2))        # horn screw
ear = ear.difference(at(box((6, 3, 6)), 0, 0, 1.5))                      # horn arm pocket

# ---------- tail: a curve of spheres, with a horn socket at the root ----------
t = np.linspace(0, 1, 14)
pts = np.c_[6 * np.sin(t * np.pi), 4 + 30 * t, 2 + 46 * t ** 1.5]
tail = hull([sphere(pts[0], 5.0, 2), sphere(pts[1], 4.8, 2)])
for a, b in zip(pts[1:-1], pts[2:]):
    tail = tail.union(hull([sphere(a, 4.6, 2), sphere(b, 4.0, 2)]))
tail = tail.union(at(box((12, 6, 8)), 0, 0, 4))
tail = tail.difference(at(cylinder(radius=1.1, height=10), 0, 0, 4))

# ---------- bottom plate with the 3 board standoffs ----------
plate = rounded_block(BODY_HALF[0], BODY_HALF[1], 0, 0, BODY_R - WALL - 0.3, 2)
plate = plate.intersection(at(box((300, 300, WALL)), 0, 0, WALL / 2))
for bx, by in ((3.4, 3.5), (3.5, 52.0), (70.0, 59.5)):        # board mounting holes -> body coords
    x, y = bx - 36.5, 31.25 - by
    post = at(cylinder(radius=STANDOFF_D / 2, height=STANDOFF_H), x, y, WALL + STANDOFF_H / 2)
    plate = plate.union(post).difference(at(cylinder(radius=SCREW_D / 2, height=20), x, y, WALL + 5))

parts = {"bob-body": body, "bob-head": head, "bob-ear": ear, "bob-tail": tail, "bob-bottom": plate}
for name, m in parts.items():
    m.export(os.path.join(HERE, name + ".stl"))
    print(f"{name:11s} watertight={m.is_watertight}  size={np.round(m.extents, 1)} mm  volume={m.volume / 1000:.1f} cm3")
