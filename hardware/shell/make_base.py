"""Bob's base tray as an STL for Tinkercad: 81 x 70.5 x 25 mm, 2 mm walls and floor,
3 M2.5 screw posts at the board's holes, and a USB-C slot in the right wall.
Coordinates: x right, y up (Tinkercad), origin at the tray's outer front-left corner.
Board sits 2 mm in from the inner walls, so board (bx, by) [by measured DOWN from the board top]
-> tray x = 4 + bx, y = 66.5 - by.
usage: py -3 make_base.py   -> bob-base.stl
"""
import math, os, struct

L, W, H, T = 81.0, 70.5, 25.0, 2.0        # outer size, wall/floor thickness
POST_R, HOLE_R, POST_H = 2.5, 1.25, 5.0
HOLES_BOARD = [(3.4, 3.5), (3.5, 52.0), (70.0, 59.5)]   # from SHELL-SPEC.md
USB_W, USB_H = 13.0, 7.0
USB_Y = 66.5 - 5.68                        # centre, from SHELL-SPEC.md (5.68 mm below board top)
USB_Z = T + POST_H + 1.6 + 1.6             # floor + post + board + half the connector
tris = []


def quad(a, b, c, d):
    tris.extend([(a, b, c), (a, c, d)])


def box(x0, y0, z0, x1, y1, z1):
    p = [(x, y, z) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    for f in ((0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)):
        quad(*(p[i] for i in f))


def tube(cx, cy, z0, z1, ro, ri, n=40):
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        o0 = (cx + ro * math.cos(a0), cy + ro * math.sin(a0)); o1 = (cx + ro * math.cos(a1), cy + ro * math.sin(a1))
        i0 = (cx + ri * math.cos(a0), cy + ri * math.sin(a0)); i1 = (cx + ri * math.cos(a1), cy + ri * math.sin(a1))
        quad((*o0, z0), (*o1, z0), (*o1, z1), (*o0, z1))          # outer wall
        quad((*i1, z0), (*i0, z0), (*i0, z1), (*i1, z1))          # inner wall
        quad((*o0, z1), (*o1, z1), (*i1, z1), (*i0, z1))          # top ring
        quad((*i0, z0), (*i1, z0), (*o1, z0), (*o0, z0))          # bottom ring


box(0, 0, 0, L, W, T)                                 # floor
box(0, 0, T, T, W, H)                                 # left wall
box(0, 0, T, L, T, H)                                 # front wall
box(0, W - T, T, L, W, H)                             # back wall
# right wall with the USB-C slot cut out (3 pieces around the slot)
ys0, ys1 = USB_Y - USB_W / 2, USB_Y + USB_W / 2
zs0, zs1 = USB_Z - USB_H / 2, USB_Z + USB_H / 2
box(L - T, 0, T, L, ys0, H)
box(L - T, ys1, T, L, W, H)
box(L - T, ys0, T, L, ys1, zs0)
box(L - T, ys0, zs1, L, ys1, H)
for bx, by in HOLES_BOARD:                            # screw posts on the floor
    tube(4 + bx, 66.5 - by, T, T + POST_H, POST_R, HOLE_R)

# sanity checks
for bx, by in HOLES_BOARD:
    x, y = 4 + bx, 66.5 - by
    assert T <= x - POST_R and x + POST_R <= L - T and T <= y - POST_R and y + POST_R <= W - T, "post outside tray"
assert T < ys0 < ys1 < W - T and T < zs0 < zs1 < H, "USB slot outside wall"

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bob-base.stl")
with open(out, "wb") as f:
    f.write(b"bob base tray".ljust(80, b"\0")); f.write(struct.pack("<I", len(tris)))
    for a, b, c in tris:
        f.write(struct.pack("<3f", 0, 0, 0))
        for v in (a, b, c):
            f.write(struct.pack("<3f", *v))
        f.write(b"\0\0")
print("wrote", out, len(tris), "triangles; USB slot z", round(zs0, 1), "-", round(zs1, 1))
