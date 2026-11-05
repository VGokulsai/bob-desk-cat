# Makes Bob's meow sounds from scratch (no recording needed) -> meow1.wav, meow2.wav, meow3.wav
# A meow is a voice going "mm-ee-a-ow": the pitch goes up then down, and the mouth shape changes.
# Each mouth shape (vowel) makes some frequencies louder; those loud bands are called formants.
# We build the voice from many harmonics and make the ones near the formants louder.
import math, random, struct, wave

RATE = 22050

def glide(t, points):
    # smooth path through (time, value) points
    for (t0, v0), (t1, v1) in zip(points, points[1:]):
        if t <= t1:
            x = (t - t0) / (t1 - t0)
            return v0 + (v1 - v0) * (0.5 - 0.5 * math.cos(math.pi * x))
    return points[-1][1]

def meow(name, length, low, high, seed):
    random.seed(seed)
    n = int(RATE * length)
    phases = [0.0] * 40
    wobble = 0.0
    samples = []
    for i in range(n):
        t = i / n
        sec = i / RATE
        wobble = wobble * 0.995 + random.uniform(-1, 1) * 0.0015   # tiny random pitch drift, like a real throat
        pitch = (low + (high - low) * math.sin(math.pi * t ** 0.7)) * (1 + wobble)
        f1 = glide(t, [(0, 350), (0.35, 900), (1, 450)])     # "ee" -> "a" -> "ow"
        f2 = glide(t, [(0, 2300), (0.35, 1500), (1, 900)])
        open_ = math.sin(math.pi * t) ** 0.6                  # mouth closed -> open -> closed
        s = 0.0
        for k in range(1, 40):
            f = pitch * k
            if f > 5000:
                break
            phases[k] += 2 * math.pi * f / RATE
            loud = math.exp(-((f - f1) / 260) ** 2) + 0.6 * math.exp(-((f - f2) / 380) ** 2) + 0.04
            loud = loud * open_ + (1 - open_) * (0.6 if k == 1 else 0.0)   # closed mouth = just a hum ("mm")
            s += math.sin(phases[k]) * loud
        s += random.uniform(-1, 1) * 0.04 * open_            # a bit of breath
        fade_in = min(1, sec / 0.03)
        fade_out = min(1, (1 - t) / 0.3) ** 2
        samples.append(s * fade_in * fade_out)
    peak = max(abs(x) for x in samples)
    with wave.open(name, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE)
        w.writeframes(b"".join(struct.pack("<h", int(x / peak * 0.8 * 32767)) for x in samples))
    print("made", name)

meow("meow1.wav", 0.65, 480, 800, 1)   # normal meow
meow("meow2.wav", 0.45, 560, 900, 2)   # short happy one
meow("meow3.wav", 0.90, 420, 720, 3)   # long lazy one
