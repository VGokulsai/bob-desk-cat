# Bob's face + ears simulator, using the SAME drawings as the website
# The round 240x240 screen is his face. The two ears on top are the real servo ears.
import math, os, random
import pygame

pygame.init()
FACE = 240                       # the round screen is 240x240
K = FACE / 290                   # how much the drawing gets shrunk to fit the screen
OX, OY = 40, 236                 # where the round screen sits in the window
screen = pygame.display.set_mode((320, OY + FACE + 8))
pygame.display.set_caption("Bob")
clock = pygame.time.Clock()

HERE = os.path.dirname(os.path.abspath(__file__))   # this folder: meow sounds live here
ART = os.path.join(HERE, "art") + "/"              # Bob's drawings
CROP = (45, 285, 290, 290)       # x, y, width, height of Bob's whole face inside the drawing
EAR_L = (30, 20, 120, 290)       # his left ear inside the drawing (bottom tucks behind the screen)
EAR_R = (200, 10, 122, 300)      # his right ear inside the drawing

def cut(img, box):
    part = img.subsurface(box)
    return pygame.transform.smoothscale(part, (round(box[2] * K), round(box[3] * K)))

frames = {}
for pose in ("idle", "blink", "talk", "lick"):
    frames[pose] = cut(pygame.image.load(ART + "bob-" + pose + ".png").convert_alpha(), CROP)

half = frames["idle"].copy()               # half-shut eyes: idle and blink mixed 50/50,
lid = frames["blink"].copy()                # shown for one frame on the way down and up
lid.set_alpha(128)
half.blit(lid, (0, 0))
frames["half"] = half

def eyelid(b):
    # b = ms since the blink started: half shut, fully shut, half shut, open
    if 0 <= b < 40 or 130 <= b < 170:
        return "half"
    if 40 <= b < 130:
        return "blink"
    return None

whole = pygame.image.load(ART + "bob-idle.png").convert_alpha()
ears = []
for box in (EAR_L, EAR_R):
    img = cut(whole, box)
    fade = pygame.Surface(img.get_size(), pygame.SRCALPHA)   # fade the bottom 30 px so the ear
    fade.fill((255, 255, 255, 255))                          # melts into his head, no hard cut line
    h = img.get_height()
    for y in range(h - 30, h):
        pygame.draw.line(fade, (255, 255, 255, round(255 * (h - 1 - y) / 30)), (0, y), (img.get_width(), y))
    img.blit(fade, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    base = (OX + (box[0] + box[2] / 2 - CROP[0]) * K,      # bottom middle of the ear = the servo shaft
            OY + (box[1] + box[3] - CROP[1]) * K)
    ears.append([img, base, 0.0])                          # [picture, pivot, current angle]

try:
    pygame.mixer.init()
    meows = [pygame.mixer.Sound(f"{HERE}/meow{i}.wav") for i in (1, 2, 3)]   # run make_meow.py once first
except (pygame.error, FileNotFoundError):
    meows = []                                                         # no speaker: Bob stays quiet

def draw_ear(img, pivot, angle):
    # spin the ear around its bottom middle, like a servo horn
    centre = pygame.math.Vector2(img.get_rect(midbottom=pivot).center)
    spun = pygame.transform.rotate(img, angle)
    new_centre = pivot + (centre - pivot).rotate(-angle)
    screen.blit(spun, spun.get_rect(center=new_centre))

# the round screen: the face is drawn on "disc", then everything outside the circle is cut away
disc = pygame.Surface((FACE, FACE), pygame.SRCALPHA)
round_cut = pygame.Surface((FACE, FACE), pygame.SRCALPHA)
pygame.draw.circle(round_cut, (255, 255, 255, 255), (120, 120), 120)

next_blink = pygame.time.get_ticks() + 3000
blink_start, double = -1000, False
pat_until = 0
meow_until = 0
last_pat = 0
next_twitch = 4000
twitch_ear, twitch_until = 0, 0

running = True
while running:
    now = pygame.time.get_ticks()
    asleep = now - last_pat > 20000          # 20 s with no pat = sleep

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:          # a click = a pat (the touch pad later)
            if meows and (now > meow_until or asleep):    # don't meow over himself
                sound = random.choice(meows)
                sound.play()
                meow_until = now + int(sound.get_length() * 1000)
            pat_until = now + 1500
            last_pat = now

    # blinking: sometimes a double blink, like a real cat
    if now >= next_blink:
        blink_start = now
        double = random.random() < 0.25                  # 1 in 4 blinks is a double
        next_blink = now + random.randint(3000, 6000)
    b = now - blink_start
    eyes = eyelid(b) or (eyelid(b - 300) if double else None)   # a double blink repeats 300 ms later

    # ear twitch: every few seconds one ear flicks for a moment
    if now >= next_twitch and not asleep:
        twitch_ear = random.randint(0, 1)
        twitch_until = now + 140
        next_twitch = now + random.randint(3000, 8000)

    if now < meow_until:
        pose = "talk"                          # mouth open while he meows
    elif now < pat_until:
        pose = "lick"
    elif asleep:
        pose = "blink"
    elif eyes:
        pose = eyes
    else:
        pose = "idle"

    # where each ear wants to be (degrees outward), and how fast it gets there
    for i, ear in enumerate(ears):
        if asleep:
            target, speed = 30, 0.04                               # slowly droop
        elif now < pat_until:
            target, speed = 20 + 6 * math.sin(now / 60), 0.3       # relaxed and wiggly
        elif i == twitch_ear and now < twitch_until:
            target, speed = 22, 0.5                                # quick flick
        else:
            target, speed = 0, 0.2                                 # back up straight
        ear[2] += (target - ear[2]) * speed                        # ease, like a servo catching up

    breath = round(3 * math.sin(now / (1400 if asleep else 700)))   # slower breathing asleep

    screen.fill((0, 0, 0))
    draw_ear(ears[0][0], ears[0][1], ears[0][2])      # ears first, so the screen covers their bottoms
    draw_ear(ears[1][0], ears[1][1], -ears[1][2])     # (right ear turns the other way)
    disc.fill((250, 250, 252, 255))                   # face colour fills the screen
    disc.blit(frames[pose], (0, breath))              # Bob's face, breathing
    disc.blit(round_cut, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)   # cut it round
    screen.blit(disc, (OX, OY))
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
