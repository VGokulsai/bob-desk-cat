"""Bob's dreams as GIFs for posts: asleep -> the camera dives into his eye -> one dream plays -> back out.
The dream pixels come from sim/dream.js itself (run with node), so the GIFs always match browser Bob.
usage: py -3 make_dream_gif.py [city home sky] -> dream-<name>.gif (500 px) + dream-<name>-strip.png
needs: node on PATH, Pillow
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
DREAM_JS = os.path.join(HERE, "..", "sim", "dream.js")
CROP = (45, 285, 335, 575)
EYE = (60, 128)           # his closed left eye on the 240 px screen: the camera dives in here
STEP = 0.08               # seconds per GIF frame

NODE = """const D = require(process.argv[1]); const [scene, ts] = [process.argv[2], JSON.parse(process.argv[3])];
const n = D.N * D.N, out = Buffer.alloc(n * 3 * ts.length);
ts.forEach((t, j) => { const b = D.frame(scene, t); for (let i = 0; i < n; i++) for (let c = 0; c < 3; c++) out[(j * n + i) * 3 + c] = b[i * 4 + c]; });
process.stdout.write(out); console.log(JSON.stringify(D.PERIOD));"""


def dreams(scene, ts):
    """dream frames at times ts (seconds), each 240x240 (80x80 grid, 3 px per pixel), plus the scene's loop length"""
    raw = subprocess.run(["node", "-e", NODE, DREAM_JS, scene, json.dumps(ts)], capture_output=True, check=True).stdout
    size = 80 * 80 * 3
    period = json.loads(raw[size * len(ts):])[scene]
    return [Image.frombytes("RGB", (80, 80), raw[i * size:(i + 1) * size]).resize((240, 240), Image.NEAREST) for i in range(len(ts))], period


FACE = None


def face(s):
    global FACE
    if FACE is None:
        f = Image.open(os.path.join(HERE, "art", "bob-blink.png")).convert("RGBA").crop(CROP).resize((240, 240), Image.LANCZOS)
        FACE = Image.new("RGB", (240, 240), (255, 255, 255)); FACE.paste(f, mask=f.split()[3])
    cx, cy = EYE
    big = FACE.resize((int(240 * s), int(240 * s)), Image.LANCZOS)
    out = Image.new("RGB", (240, 240), (255, 255, 255))
    out.paste(big, (int(cx - cx * s), int(cy - cy * s)))
    return out


def ease(x):
    return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2


def iris(base, dream, r):
    m = Image.new("L", (240, 240), 0)
    ImageDraw.Draw(m).ellipse([EYE[0] - r, EYE[1] - r, EYE[0] + r, EYE[1] + r], fill=255)
    return Image.composite(dream, base, m)


def round_mask(im):
    """show it like his round screen in a ring, on the warm page colour (2x, so dream pixels stay square)"""
    big = im.resize((480, 480), Image.NEAREST)
    out = Image.new("RGB", (500, 500), (247, 241, 230))
    ring = Image.new("L", (500, 500), 0); ImageDraw.Draw(ring).ellipse([0, 0, 499, 499], fill=255)
    out.paste(Image.new("RGB", (500, 500), (154, 148, 141)), (0, 0), ring)
    m = Image.new("L", (480, 480), 0); ImageDraw.Draw(m).ellipse([0, 0, 479, 479], fill=255)
    out.paste(big, (10, 10), m)
    return out


def make(scene):
    _, period = dreams(scene, [0])
    n = round(period / STEP)                                                       # one whole dream loop
    dr, _ = dreams(scene, [k * STEP for k in range(n)])
    frames = [face(1)] * 8                                                         # asleep
    frames += [face(1 + ease(k / 13) * 4) for k in range(14)]                     # dive into his eye
    frames += [iris(face(5), dr[k], ease(k / 7) * 250) for k in range(8)]         # dream opens
    frames += dr[8:n - 8]                                                          # dreaming
    frames += [iris(face(5), dr[n - 8 + k], (1 - ease(k / 7)) * 250) for k in range(8)]   # dream closes
    frames += [face(5 - ease(k / 9) * 4) for k in range(10)]                      # back out
    frames += [face(1)] * 6
    out = [round_mask(f) for f in frames]
    path = os.path.join(HERE, f"dream-{scene}.gif")
    out[0].save(path, save_all=True, append_images=out[1:], duration=int(STEP * 1000), loop=0, optimize=True)
    # strip for a quick look: asleep, diving in, opening, four beats of the dream, closing
    keys = [0, 15, 26] + [30 + (n - 16) * k // 4 for k in range(4)] + [30 + n - 16 + 4]
    strip = Image.new("RGB", (250 * len(keys), 250), (247, 241, 230))
    for i, k in enumerate(keys):
        strip.paste(out[k].resize((250, 250), Image.LANCZOS), (250 * i, 0))
    strip.save(os.path.join(HERE, f"dream-{scene}-strip.png"))
    print("wrote", path, len(out), "frames,", round(os.path.getsize(path) / 1024), "KB")


if __name__ == "__main__":
    for s in sys.argv[1:] or ["city", "home", "sky"]:
        make(s)
