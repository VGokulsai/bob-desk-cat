"""Bob's yawn: the sound (yawn.wav) and the mouth the firmware draws over his sleepy face.

The ESP32's flash is nearly full (each face picture costs 115 KB), so the yawn is NOT a new picture.
The firmware shows his eyes-shut face (bob-blink), rubs out his little smile and draws an open mouth
on top, growing it a bit each frame. This script draws the exact same shapes, so the previews here
match the real screen.

usage: py -3 make_yawn.py -> yawn.wav, preview-yawn.png (strip), yawn.gif
Mouth numbers are in 240 px screen pixels and must match MOUTH_* in firmware/bob/bob.ino.
"""
import math, os, random, struct, wave
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
RATE = 22050

# --- the mouth (same numbers as bob.ino) ---
MOUTH_X, MOUTH_Y = 111, 163      # centre of the open mouth
MOUTH_RX, MOUTH_RY = 15, 18      # fully open
SMILE_X, SMILE_Y, SMILE_W, SMILE_H = 92, 150, 52, 14     # white box (just under the nose) that rubs out his smile
SKIN = (255, 255, 255)
INSIDE = (58, 30, 37)
TONGUE = (232, 120, 140)
INK = (25, 25, 25)
CROP = (45, 285, 335, 575)       # same crop as make_faces_h.py


def rgb565(c):                   # what the screen can actually show
    r, g, b = c
    v = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    return ((v >> 8) & 0xF8, (v >> 3) & 0xFC, (v << 3) & 0xF8), v


def sleepy_face():
    im = Image.open(os.path.join(HERE, "art", "bob-blink.png")).convert("RGBA").crop(CROP)
    im = im.resize((240, 240), Image.LANCZOS)
    flat = Image.new("RGB", im.size, (255, 255, 255))
    flat.paste(im, mask=im.split()[3])
    return to565(flat)


def to565(im):                   # show the picture in the screen's own colours
    return Image.merge("RGB", [b.point(lambda v, m=m: v & m) for b, m in zip(im.split(), (0xF8, 0xFC, 0xF8))])


def ellipse(d, x, y, rx, ry, fill=None, outline=None):
    d.ellipse([x - rx, y - ry, x + rx, y + ry], fill=fill, outline=outline)


def yawn_frame(base, ry):
    """Mirror of drawYawn(ry) in bob.ino: rub out the smile, then mouth, tongue, 2 px ink edge."""
    im = base.copy()
    d = ImageDraw.Draw(im)
    d.rectangle([SMILE_X, SMILE_Y, SMILE_X + SMILE_W - 1, SMILE_Y + SMILE_H - 1], fill=rgb565(SKIN)[0])
    if ry > 0:
        rx = max(3, MOUTH_RX * ry // MOUTH_RY)
        ellipse(d, MOUTH_X, MOUTH_Y, rx, ry, fill=rgb565(INSIDE)[0])
        if ry >= 6:
            ellipse(d, MOUTH_X, MOUTH_Y + ry * 6 // 10, rx * 6 // 10, ry * 4 // 10, fill=rgb565(TONGUE)[0])
        for k in (0, 1):
            ellipse(d, MOUTH_X, MOUTH_Y, rx - k, ry - k, outline=rgb565(INK)[0])
    return im


# --- the sound: a long "haaa-oww-mm", sliding down in pitch ---
def glide(t, points):
    for (t0, v0), (t1, v1) in zip(points, points[1:]):
        if t <= t1:
            x = (t - t0) / (t1 - t0)
            return v0 + (v1 - v0) * (0.5 - 0.5 * math.cos(math.pi * x))
    return points[-1][1]


def yawn_sound(name="yawn.wav", length=1.5, seed=7):
    random.seed(seed)
    n = int(RATE * length)
    phases = [0.0] * 40
    wobble = 0.0
    out = []
    for i in range(n):
        t = i / n
        wobble = wobble * 0.995 + random.uniform(-1, 1) * 0.002
        pitch = glide(t, [(0, 300), (0.15, 340), (0.8, 170), (1, 150)]) * (1 + wobble)
        f1 = glide(t, [(0, 500), (0.2, 850), (0.7, 600), (1, 300)])     # "h-aaa" -> "ow" -> "mm"
        f2 = glide(t, [(0, 1500), (0.2, 1250), (0.7, 900), (1, 700)])
        open_ = glide(t, [(0, 0.2), (0.2, 1), (0.75, 0.8), (1, 0)])     # mouth opens wide, then closes
        s = 0.0
        for k in range(1, 40):
            f = pitch * k
            if f > 5000:
                break
            phases[k] += 2 * math.pi * f / RATE
            loud = math.exp(-((f - f1) / 260) ** 2) + 0.6 * math.exp(-((f - f2) / 380) ** 2) + 0.04
            loud = loud * open_ + (1 - open_) * (0.6 if k == 1 else 0.0)
            s += math.sin(phases[k]) * loud
        s += random.uniform(-1, 1) * 0.18 * open_          # a yawn is breathy
        fade_in = min(1, (i / RATE) / 0.12)
        fade_out = min(1, (1 - t) / 0.25) ** 2
        out.append(s * fade_in * fade_out)
    peak = max(abs(x) for x in out)
    with wave.open(os.path.join(HERE, name), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE)
        w.writeframes(b"".join(struct.pack("<h", int(x / peak * 0.8 * 32767)) for x in out))
    return out


if __name__ == "__main__":
    base = sleepy_face()
    steps = [0, 3, 6, 10, 14, 18]                                    # YAWN_STEPS in bob.ino
    frames = [yawn_frame(base, r) for r in steps]
    # strip for the log: smile rubbed out -> mouth fully open
    strip = Image.new("RGB", (len(frames) * 250 + 10, 260), (247, 241, 230))
    for k, f in enumerate(frames):
        strip.paste(f, (10 + k * 250, 10))
    strip.save(os.path.join(HERE, "preview-yawn.png"))
    # gif: open, hold, close
    seq = frames + [frames[-1]] * 6 + frames[::-1]
    big = [f.resize((480, 480), Image.LANCZOS) for f in seq]
    big[0].save(os.path.join(HERE, "yawn.gif"), save_all=True, append_images=big[1:], duration=90, loop=0)
    samples = yawn_sound()
    assert len(samples) == int(RATE * 1.5)
    print("wrote yawn.wav, preview-yawn.png, yawn.gif")
    print("RGB565:", {k: hex(rgb565(c)[1]) for k, c in (("skin", SKIN), ("inside", INSIDE), ("tongue", TONGUE), ("ink", INK))})
