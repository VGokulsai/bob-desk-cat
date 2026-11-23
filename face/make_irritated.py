"""Make Bob's irritated face from Gokul's idle drawing: heavy, flat eyelids that slant down toward the nose.
Nothing is redrawn from scratch: it lowers eyelids over his own eyes and inks the lid edge.
usage: py -3 make_irritated.py  -> art/bob-irritated.png (+ preview-irritated.png)
Tune LIDS if the lids sit too high or low.
"""
import os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
CROP = (45, 285, 335, 575)       # the face, same as make_faces_h.py
UP = 4                            # draw at 4x, then shrink, for smooth ink

# measured on a 480 px view of the face crop: eye ellipse (cx, cy, rx, ry) and the lid line (x0, y0) -> (x1, y1)
# the inner end of each lid (toward the nose) sits lower = annoyed
EYES = [((120, 205, 62, 68), (52, 176), (190, 196)),   # his right eye (on our left)
        ((328, 192, 64, 70), (258, 192), (398, 172))]  # his left eye
INK = (25, 25, 25, 255)
LID_W = 7                         # lid line thickness on the 480 view


def make():
    art = Image.open(os.path.join(HERE, "art", "bob-idle.png")).convert("RGBA")
    face = art.crop(CROP)
    big = face.resize((290 * UP, 290 * UP), Image.LANCZOS)
    s = 290 * UP / 480                                   # 480-view -> big
    skin = big.getpixel((int(225 * s), int(215 * s)))     # the white between his eyes, used as eyelid
    for (cx, cy, rx, ry), (x0, y0), (x1, y1) in EYES:
        # mask = inside the eye AND above the lid line
        m = Image.new("L", big.size, 0)
        d = ImageDraw.Draw(m)
        d.ellipse([(cx - rx) * s, (cy - ry) * s, (cx + rx) * s, (cy + ry) * s], fill=255)
        cut = Image.new("L", big.size, 0)
        ImageDraw.Draw(cut).polygon([(x0 * s, y0 * s), (x1 * s, y1 * s), (x1 * s, 0), (x0 * s, 0)], fill=255)
        m = Image.composite(m, Image.new("L", big.size, 0), cut)
        big.paste(Image.new("RGBA", big.size, skin), (0, 0), m)
        # the inked lid edge
        ImageDraw.Draw(big).line([(x0 * s, y0 * s), (x1 * s, y1 * s)], fill=INK, width=int(LID_W * s))
    face = big.resize((290, 290), Image.LANCZOS)
    out = art.copy()
    out.paste(face, CROP[:2])
    out.save(os.path.join(HERE, "art", "bob-irritated.png"))
    # preview: idle vs irritated, as the 240 px screen shows them
    prev = Image.new("RGB", (500, 250), (247, 241, 230))
    for k, im in enumerate([art, out]):
        f = im.crop(CROP).resize((240, 240), Image.LANCZOS)
        bg = Image.new("RGB", f.size, (255, 255, 255)); bg.paste(f, mask=f.split()[3])
        prev.paste(bg, (5 + k * 250, 5))
    prev.save(os.path.join(HERE, "preview-irritated.png"))


if __name__ == "__main__":
    make()
    print("wrote art/bob-irritated.png and preview-irritated.png")
