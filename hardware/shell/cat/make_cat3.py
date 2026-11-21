"""Bob v3 shell: traced from Gokul's drawing (face/art/bob-idle.png). From the front the
outline IS the drawing; the depth is "inflated" so it's round like a toy.

How: the drawing's outline -> a 2D mask at 1 mm per pixel -> each point gets a depth from
how far it is from the edge (rounded edges) -> a voxel volume -> hollowed (2.4 mm walls)
-> smooth mesh. Ears are cut off as separate parts (they ride on the ear servos).
The board lies flat in the bottom, turned so its USB-C faces the BACK wall.

Units mm: x = right, y = back (face looks to -y), z = up. Outputs bob3-*.stl
usage: py -3 make_cat3.py
"""
import os
import numpy as np
from PIL import Image
from scipy import ndimage as nd
from skimage import measure
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "..", "..", "..", "face", "art", "bob-idle.png")
# --- CHANGE THESE ------------------------------------------------------------------
SCALE = 0.34            # mm per drawing pixel: 900 px tall drawing -> 306 mm to the ear tips
WALL = 2.4
EAR_CUT_Z = 204.0       # above this the ears are separate parts (drawing row ~300)
NECK_CUT_Z = 124.0      # head / body split (middle of the neck)
# half-depth (front-to-back) caps and edge-rounding radii per height band: (z_top, cap, r)
BANDS = [(61, 45.0, 8.0), (119, 20.0, 12.0), (129, 12.0, 6.0), (999, 26.0, 14.0)]
FACE = (0.0, 163.0)     # screen window centre (x, z): centre of the drawn face
WINDOW_D = 34.0
EAR_SLOT_X = 28.0      # ear servo slots at x = +-31 through the head top
SERVO = (23.5, 12.5, 22.7)   # SG90 body
LEG_X, LEG_R = (-10.0, 10.0), 6.5   # front legs from the drawing (px ~162 and ~220)
HEAD_SPLIT_Y = 8.0      # head = front shell + removable back cover (screen + ear servos go in from the back)
BXS = 3.0              # board shifted right (the drawing is narrower on the left)
STANDOFF_H, STANDOFF_D, SCREW_D = 5.0, 5.2, 2.2
# ------------------------------------------------------------------------------------

# ---------- 1. the drawing's outline -> mask at 1 mm per cell ----------
a = np.array(Image.open(ART))[..., 3] > 100
a = nd.binary_fill_holes(a)
lab, _ = nd.label(a)
a = lab == (np.argmax(np.bincount(lab.ravel())[1:]) + 1)
H_px, W_px = a.shape
Wmm, Hmm = int(round(W_px * SCALE)), int(round(H_px * SCALE))
m2 = np.array(Image.fromarray((a * 255).astype(np.uint8)).resize((Wmm, Hmm), Image.BILINEAR)) > 127
m2 = m2[::-1].T                              # -> m2[x, z], z = 0 at the bottom (paws)
X0 = Wmm / 2.0                               # x = 0 at the drawing's centre column
xs = np.arange(Wmm) - X0 + 0.5
zs = np.arange(Hmm) + 0.5

# drop empty rows under the paws so the bottom sits at z = 0
first = int(np.flatnonzero(m2.any(0))[0])
m2 = np.concatenate([m2[:, first:], np.zeros((Wmm, first), bool)], axis=1)
# flat base: the bottom 12 mm takes the width of the row at 12 mm (the paw tips curve in below that),
# and the gaps between the paws in the bottom 40 mm are filled so the board has a solid base
m2[:, :12] = m2[:, 12:13]
for k in range(40):
    col = np.flatnonzero(m2[:, k])
    if len(col):
        m2[col.min():col.max() + 1, k] = True

ears2d = m2 & (zs[None, :] > EAR_CUT_Z)
body2d = m2 & (zs[None, :] <= EAR_CUT_Z)
# distance from the outline, but the floor is not an edge (pad below so the base isn't rounded underneath)
PAD = 20
dist = nd.distance_transform_edt(np.concatenate([np.repeat(body2d[:, :1], PAD, 1), body2d], axis=1))[:, PAD:]

# ---------- 2. depth per point (rounded like a plush toy) ----------
cap = np.zeros(Hmm); rad = np.zeros(Hmm)
for k in range(Hmm):
    for ztop, c, r in BANDS:
        if zs[k] <= ztop:
            cap[k], rad[k] = c, r; break
t = np.clip(dist / rad[None, :], 0, 1)
D = cap[None, :] * np.sqrt(1 - (1 - t) ** 2) * body2d          # half-depth at (x, z)
D = nd.gaussian_filter(D, 5.0) * body2d                          # blend the depth bands smoothly

Ymax = int(max(cap)) + 20                    # room for the legs and paws that stick out in front
ys = np.arange(-Ymax, Ymax) + 0.5
vol = np.abs(ys[None, :, None]) < D[:, None, :]                  # vol[x, y, z]

# ---------- 2b. legs and paws (in the drawing they are lines inside the outline, so add them as relief) ----------
gx, gy = np.meshgrid(xs, ys, indexing="ij")
for x0 in LEG_X:                                     # front legs: round columns on the chest, down to the paws
    ix = int(round(x0 + X0))
    for k in range(38, 101):
        yc = -D[ix, k] + 2.0
        vol[:, :, k] |= (gx - x0) ** 2 + (gy - yc) ** 2 < LEG_R ** 2
    yp = -D[ix, 8] - 1.0                             # front paw
    for k in range(0, 13):
        vol[:, :, k] |= ((gx - x0) / 9.0) ** 2 + ((gy - yp) / 11.0) ** 2 + ((k - 5) / 7.0) ** 2 < 1
for x0 in (-43.0, 43.0):                             # back paws (the big pink-pad paws at the sides)
    ix = int(round(x0 + X0)); yp = -D[ix, 8] + 2.0
    for k in range(0, 12):
        vol[:, :, k] |= ((gx - x0) / 14.0) ** 2 + ((gy - yp) / 12.0) ** 2 + ((k - 4) / 7.0) ** 2 < 1

# ---------- 3. hollow it ----------
padded = np.concatenate([np.repeat(vol[:, :, :1], 10, 2), vol], axis=2)    # floor isn't a wall: the cavity reaches z = 0
inside = nd.distance_transform_edt(padded)[:, :, 10:] > WALL
inside &= vol
# open the bottom where the cavity is (so the board + plate go in from below)
open_fp = inside[:, :, int(WALL) + 2]
vol[:, :, :int(WALL) + 1] &= ~open_fp[:, :, None]
shell = vol & ~inside
shell0 = shell.copy()                                # before the intentional cut-outs, for the hole check

def box_idx(x0, x1, y0, y1, z0, z1):
    return (slice(int(np.floor(x0 + X0)), int(np.ceil(x1 + X0))), slice(int(np.floor(y0 + Ymax)), int(np.ceil(y1 + Ymax))),
            slice(max(int(np.floor(z0)), 0), int(np.ceil(z1))))

# ---------- 4. cut-outs ----------
XX, YY, ZZ = np.meshgrid(xs, ys, zs, indexing="ij")
window = ((XX - FACE[0]) ** 2 + (ZZ - FACE[1]) ** 2 < (WINDOW_D / 2) ** 2) & (YY < 0)
shell &= ~window
# board: turned 90 deg, USB-C faces +y (back). board (bx, by) -> body x = 31.25 - by, y = bx - 36.5
plate_top = WALL
board_z0 = plate_top + STANDOFF_H
usb_x, usb_z = 31.25 - 5.68 + BXS, board_z0 + 1.6 + 1.6
shell[box_idx(usb_x - 6.5, usb_x + 6.5, 20, Ymax, usb_z - 3.5, usb_z + 3.5)] = False          # USB-C slot, back wall
shell[box_idx(-15 - SERVO[0] / 2, -15 + SERVO[0] / 2, 20, Ymax, 20 - SERVO[1] / 2, 20 + SERVO[1] / 2)] = False  # tail servo slot
def ear_mid(left):                                   # x of each ear's centre, straight from the drawing
    e = ears2d & ((xs < 0) if left else (xs >= 0))[:, None]
    xc = np.flatnonzero(e.any(1)); return float(xs[int((xc.min() + xc.max()) / 2)])
EAR_X = [ear_mid(True), ear_mid(False)]
for cx in EAR_X:                                                                               # ear servo slots under each ear
    shell[box_idx(cx - SERVO[0] / 2, cx + SERVO[0] / 2, -SERVO[1] / 2, SERVO[1] / 2, EAR_CUT_Z - 20, EAR_CUT_Z + 2)] = False

# ---------- 5. fit checks (voxels) ----------
def frac_inside(region):
    v = inside[region]; return v.mean() if v.size else 0.0
board_box = box_idx(-31.25 - 1 + BXS, 31.25 + 1 + BXS, -36.5 - 1, 36.5 + 1, board_z0, board_z0 + 1.6 + 22)
print("board + 22 mm parts inside cavity: %.1f%%" % (100 * frac_inside(board_box)))
screen_box = box_idx(FACE[0] - 20, FACE[0] + 20, -D[int(X0), int(FACE[1])] + WALL, -D[int(X0), int(FACE[1])] + WALL + 10, FACE[1] - 20, FACE[1] + 20)
print("screen module (40x40x10 behind the window) inside head cavity: %.1f%%" % (100 * frac_inside(screen_box)))
for cx in EAR_X:
    sb = box_idx(cx - SERVO[0] / 2, cx + SERVO[0] / 2, -SERVO[1] / 2, SERVO[1] / 2, EAR_CUT_Z - 2 - SERVO[2], EAR_CUT_Z - 2)
    print("ear servo x=%+.1f inside head cavity: %.1f%%" % (cx, 100 * frac_inside(sb)))
front_in = -D[int(X0), int(FACE[1])] + WALL
sx0, sx1, sy0, sy1 = FACE[0] - 20, FACE[0] + 20, front_in, front_in + 10              # screen module box (x, y)
clash = any(max(sx0, cx - SERVO[0] / 2) < min(sx1, cx + SERVO[0] / 2) and
            max(sy0, -SERVO[1] / 2) < min(sy1, SERVO[1] / 2) and EAR_CUT_Z - 2 - SERVO[2] < FACE[1] + 20 for cx in EAR_X)
sv = [(cx - SERVO[0] / 2, cx + SERVO[0] / 2) for cx in EAR_X]
print("ear servos at x = %.1f and %.1f, gap between them %.1f mm" % (EAR_X[0], EAR_X[1], sv[1][0] - sv[0][1]))
print("screen vs ear servos (3D boxes):", "CLASH" if clash else "OK, no clash")
print("neck cavity min width: %.1f mm" % (2 * (D[int(X0), int(NECK_CUT_Z)] - WALL)))
# holes: nothing solid may touch the grid's edge (it would be cut open there), and walking in from
# the front or back, every line that reaches the cavity must pass through a wall first
edge = vol[0].any() or vol[-1].any() or vol[:, 0].any() or vol[:, -1].any() or vol[:, :, -1].any()
print("solid touches the grid edge:", "YES (cut open!)" if edge else "no")
n_holes = 0
for xi in range(shell.shape[0]):
    for zi in range(int(WALL) + 1, shell.shape[2]):
        ci = inside[xi, :, zi]
        if not ci.any():
            continue
        f, b = np.argmax(ci), len(ci) - 1 - np.argmax(ci[::-1])
        if not shell0[xi, :f, zi].any() or not shell0[xi, b + 1:, zi].any():
            n_holes += 1
print("accidental wall holes (window/USB/tail slots not counted):", n_holes)

# ---------- 6. meshes ----------
def to_mesh(v, origin):
    v = np.pad(v, 2)
    verts, faces, _, _ = measure.marching_cubes(v.astype(np.float32), 0.5)
    m = trimesh.Trimesh(verts - 2 + origin, faces, process=True)
    trimesh.smoothing.filter_taubin(m, iterations=25)
    m.fix_normals()
    return m

origin = np.array([-X0, -Ymax, 0.0])
zcut = int(NECK_CUT_Z)
body = shell.copy(); body[:, :, zcut:] = False
head = shell.copy(); head[:, :, :zcut] = False
jy = int(HEAD_SPLIT_Y + Ymax)
head_front = head.copy(); head_front[:, jy:, :] = False
head_back = head.copy(); head_back[:, :jy, :] = False
# the opening at the split must let the screen (39 mm) and an SG90 with tabs (32 x 23 mm) through
sec = inside[:, jy, zcut:]
cx_ = np.flatnonzero(sec.any(1)); cz_ = np.flatnonzero(sec.any(0))
print("head back opening: %.0f mm wide x %.0f mm tall (screen needs 39, servo needs 32)" % (len(cx_) and (cx_.max() - cx_.min()), len(cz_) and (cz_.max() - cz_.min())))
parts = {"bob3-body": to_mesh(body, origin), "bob3-head": to_mesh(head_front, origin), "bob3-head-back": to_mesh(head_back, origin)}

# ears: each ear outline extruded 6 mm thick, with a 10 mm tab under it for the servo horn
for left in (True, False):                                   # split the ears by side, not by touching pixels
    e2 = ears2d & ((xs < 0) if left else (xs >= 0))[:, None]
    if e2.sum() < 200:
        continue
    ev = np.zeros((Wmm, 8, Hmm), bool)
    ev[:, 1:7, :] = e2[:, None, :]
    xc = np.flatnonzero(e2.any(1)); zc = np.flatnonzero(e2.any(0))
    mid = int((xc.min() + xc.max()) / 2); z0 = zc.min()
    ev[mid - 5:mid + 5, 2:6, max(z0 - 10, 0):z0 + 1] = True
    side = "L" if (mid - X0) < 0 else "R"
    parts["bob3-ear-" + side] = to_mesh(ev, np.array([-X0, -4.0, 2.0]))   # 2 mm above the head so it can turn freely

# bottom plate: the cavity opening shrunk 0.3 mm, 2.4 mm thick, with the 3 standoffs
fp = nd.binary_erosion(open_fp, iterations=1)
pv = np.zeros((Wmm, 2 * Ymax, int(WALL + STANDOFF_H) + 2), bool)
pv[:, :, :int(WALL)] = fp[:, :, None]
pm = to_mesh(pv, origin)
for bx, by in ((3.4, 3.5), (3.5, 52.0), (70.0, 59.5)):
    x, y = 31.25 - by + BXS, bx - 36.5
    post = trimesh.creation.cylinder(radius=STANDOFF_D / 2, height=STANDOFF_H, sections=24)
    post.apply_translation((x, y, WALL + STANDOFF_H / 2 - 0.2))
    hole = trimesh.creation.cylinder(radius=SCREW_D / 2, height=20, sections=16)
    hole.apply_translation((x, y, WALL + 4))
    pm = pm.union(post).difference(hole)
parts["bob3-bottom"] = pm

for name, m in parts.items():
    m.export(os.path.join(HERE, name + ".stl"))
    print(f"{name:13s} watertight={m.is_watertight} size={np.round(m.extents, 1)} mm")
