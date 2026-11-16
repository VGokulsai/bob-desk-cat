"""Bob's head as an STL: a hollow box that sits on the base tray (open at the bottom),
a square face window for the 1.28" round screen, 2 ear-servo slots on top.
AI-assisted (Gokul was in hospital); dimensions from SHELL-SPEC.md.
usage: py -3 make_head.py -> bob-head.stl
"""
import os, struct
L, W, H, T = 81.0, 70.5, 50.0, 2.0          # same footprint as the base, 50 mm tall
WIN = 34.0                                   # face window (screen viewing area 32.4 mm)
EAR = (23.5, 12.5)                           # SG90 body slot
tris = []


def quad(a, b, c, d): tris.extend([(a, b, c), (a, c, d)])


def box(x0, y0, z0, x1, y1, z1):
    p = [(x, y, z) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    for f in ((0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)):
        quad(*(p[i] for i in f))


def plate_with_holes(u0, u1, v0, v1, holes, make):
    """Fill rectangle [u0,u1]x[v0,v1] minus rectangular holes, using vertical strips."""
    us = sorted({u0, u1, *[h[0] for h in holes], *[h[1] for h in holes]})
    for a, b in zip(us, us[1:]):
        cuts = sorted((h[2], h[3]) for h in holes if h[0] <= a and b <= h[1])
        v = v0
        for c0, c1 in cuts:
            if c0 > v: make(a, b, v, c0)
            v = max(v, c1)
        if v < v1: make(a, b, v, v1)


# side walls: left, right, back (front has the window)
box(0, 0, 0, T, W, H)
box(L - T, 0, 0, L, W, H)
box(0, W - T, 0, L, W, H)
# front wall (y = 0..T) with the face window centred, window centre at 30 mm height
wz = 30.0
plate_with_holes(T, L - T, 0, H, [((L - WIN) / 2, (L + WIN) / 2, wz - WIN / 2, wz + WIN / 2)],
                 lambda a, b, c, d: box(a, 0, c, b, T, d))
# top (z = H-T..H) with two ear slots near the front corners
ex = [(12.0, 12.0 + EAR[0]), (L - 12.0 - EAR[0], L - 12.0)]
ey = (14.0, 14.0 + EAR[1])
plate_with_holes(T, L - T, T, W - T, [(x0, x1, ey[0], ey[1]) for x0, x1 in ex],
                 lambda a, b, c, d: box(a, c, H - T, b, d, H))

assert WIN / 2 < wz < H - T - WIN / 2
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bob-head.stl")
with open(out, "wb") as f:
    f.write(b"bob head".ljust(80, b"\0")); f.write(struct.pack("<I", len(tris)))
    for a, b, c in tris:
        f.write(struct.pack("<3f", 0, 0, 0))
        for v in (a, b, c): f.write(struct.pack("<3f", *v))
        f.write(b"\0\0")
print("wrote", out, len(tris))
