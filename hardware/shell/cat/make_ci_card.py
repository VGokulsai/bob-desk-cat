"""Picture of the real CI compile result (numbers copied from GitHub Actions run 44917648356, 21 Nov 2026)."""
from PIL import Image, ImageDraw, ImageFont
W, H = 1200, 675
im = Image.new("RGB", (W, H), (22, 27, 34)); d = ImageDraw.Draw(im)
F = lambda s, b=False: ImageFont.truetype(r"C:\Windows\Fonts\consolab.ttf" if b else r"C:\Windows\Fonts\consola.ttf", s)
d.text((60, 50), "Compile Bob firmware  -  GitHub Actions", font=F(36, True), fill=(230, 237, 243))
d.text((60, 105), "VGokulsai/bob-desk-cat  |  21 Nov 2026  |  board: ESP32-S3 (PSRAM OPI, 8 MB flash)", font=F(22), fill=(139, 148, 158))
d.rounded_rectangle((60, 160, 300, 210), radius=24, fill=(35, 134, 54))
d.text((88, 170), "PASSED", font=F(28, True), fill=(255, 255, 255))
lines = [
    "ESP32 core 3.3.0  +  GFX Library for Arduino 1.6.0",
    "",
    "Sketch uses 778123 bytes (59%) of program storage space.",
    "Global variables use 23316 bytes (7%) of dynamic memory.",
    "",
    "Fixed on the way:",
    "  - ESP32Servo broke on the new core -> servos now on the ESP32's own PWM",
    "  - pinned core + screen library to versions that build together",
]
y = 250
for ln in lines:
    d.text((60, y), ln, font=F(26), fill=(201, 209, 217)); y += 40
import os
im.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "bob-ci-pass.png"))
print("ok")
