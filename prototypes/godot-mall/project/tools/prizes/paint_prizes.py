#!/usr/bin/env python3
"""Textures for Pocket Change's ticket prizes (scripts/prizes.gd; Steven, Oct 15 2026).

Writes prizes/*.png (outside tex/, so a prize change never makes a wing's stand-in stale).
All generic: no brand names or logos. Run from the project folder.
The packaging and price-card art carries no words: scripts/prizes.gd draws them over it at load
time from scripts/prizes.json ("text", "art") and the owner's published edits
(play/prize_text.json), so Steven can change any of them in the game (Oct 15 2026).
"""
import math, random
from PIL import Image, ImageDraw, ImageFont

OUT = "prizes/"
F = "fonts/sans.otf"
def font(sz): return ImageFont.truetype(F, sz)
rnd = random.Random(1995)

def save(im, name):
    im.save(OUT + name + ".png")

# Pog pack: a blister card, a header band, five caps and a slammer behind the bubble
def pog_card():
    im = Image.new("RGB", (256, 384), (24, 40, 140))
    d = ImageDraw.Draw(im)
    for y in range(384):
        d.line([(0, y), (256, y)], fill=(24 + y // 8, 40 + y // 10, 140 - y // 6))
    d.rectangle([0, 0, 256, 70], fill=(250, 210, 30))
    d.ellipse([110, 6, 146, 20], fill=(24, 40, 140))      # the hang hole
    cols = [(230, 60, 40), (40, 170, 70), (250, 200, 40), (140, 50, 180), (30, 140, 220)]
    for k, c in enumerate(cols):
        cx = 60 + (k % 3) * 68; cy = 140 + (k // 3) * 90
        d.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=(250, 246, 230))
        d.ellipse([cx - 25, cy - 25, cx + 25, cy + 25], fill=c)
        for i in range(6):
            a = i * math.pi / 3 + k
            d.line([(cx, cy), (cx + 22 * math.cos(a), cy + 22 * math.sin(a))], fill=(255, 255, 255), width=3)
    d.ellipse([170, 240, 236, 306], fill=(40, 40, 46)); d.ellipse([180, 250, 226, 296], fill=(190, 190, 200))
    save(im, "pog_card")

# Candy cigarettes: a white box, red band, a little cartoon on the front
def candy_box():
    im = Image.new("RGB", (192, 288), (248, 246, 240))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 70, 192, 140], fill=(210, 30, 40))
    d.rectangle([0, 250, 192, 288], fill=(30, 60, 160))
    save(im, "candy_box")

# A chocolate chew's wax-paper wrapper: brown with a white band, wraps round a cylinder
def chew():
    im = Image.new("RGB", (128, 64), (88, 50, 30))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 22, 128, 42], fill=(245, 240, 230))
    for x in range(0, 128, 32):
        d.line([(x, 22), (x + 16, 42)], fill=(200, 40, 40), width=3)
    save(im, "chew")

# A woven finger trap: a diagonal two-tone weave (multiplied by each trap's colour)
def weave():
    im = Image.new("RGB", (64, 128), (255, 255, 255))
    d = ImageDraw.Draw(im)
    for k in range(-128, 128, 12):
        d.line([(0, k), (64, k + 64)], fill=(150, 150, 150), width=4)
        d.line([(0, k + 64), (64, k)], fill=(200, 200, 200), width=3)
    save(im, "weave")

# Slap bracelets: zebra, neon splatter, leopard, rainbow stripe
def slap():
    for i in range(4):
        im = Image.new("RGB", (256, 32), (255, 255, 255))
        d = ImageDraw.Draw(im)
        if i == 0:
            for x in range(0, 256, 14):
                d.polygon([(x, 0), (x + 7, 0), (x + 12, 32), (x + 4, 32)], fill=(10, 10, 10))
        elif i == 1:
            im.paste((20, 20, 30), (0, 0, 256, 32))
            for k in range(40):
                c = rnd.choice([(255, 60, 200), (60, 255, 80), (255, 240, 40), (40, 200, 255)])
                x = rnd.randrange(256); y = rnd.randrange(32); r = rnd.randrange(2, 6)
                d.ellipse([x - r, y - r, x + r, y + r], fill=c)
        elif i == 2:
            im.paste((235, 180, 80), (0, 0, 256, 32))
            for k in range(30):
                x = rnd.randrange(256); y = rnd.randrange(32)
                d.ellipse([x - 5, y - 4, x + 5, y + 4], outline=(40, 25, 10), width=2)
        else:
            cols = [(230, 40, 40), (250, 140, 30), (250, 220, 40), (50, 180, 70), (40, 110, 220), (130, 60, 190)]
            for k, c in enumerate(cols):
                d.rectangle([0, k * 32 // 6, 256, (k + 1) * 32 // 6], fill=c)
        save(im, "slap%d" % i)

# Rainbow coil spring: bands of colour round the coil, a dark groove between each
def rainbow():
    im = Image.new("RGB", (32, 256), (0, 0, 0))
    d = ImageDraw.Draw(im)
    cols = [(230, 40, 40), (250, 140, 30), (250, 220, 40), (50, 180, 70), (40, 110, 220), (130, 60, 190)]
    n = 24
    for k in range(n):
        y0 = k * 256 // n
        d.rectangle([0, y0, 32, y0 + 256 // n - 3], fill=cols[(k * 6) // n])
    save(im, "rainbow")

# A fuzzy die: pips on each of the BoxMesh's six cells (3 x 2 layout), on fuzz
def die():
    im = Image.new("RGB", (384, 256), (255, 255, 255))
    d = ImageDraw.Draw(im)
    for i in range(6000):
        x = rnd.randrange(384); y = rnd.randrange(256); g = rnd.randrange(200, 256)
        d.point((x, y), fill=(g, g, g))
    P = {1: [(0, 0)], 2: [(-1, -1), (1, 1)], 3: [(-1, -1), (0, 0), (1, 1)], 4: [(-1, -1), (1, -1), (-1, 1), (1, 1)],
         5: [(-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)], 6: [(-1, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)]}
    for f in range(6):
        cx = (f % 3) * 128 + 64; cy = (f // 3) * 128 + 64
        for (px, py) in P[f + 1]:
            x = cx + px * 34; y = cy + py * 34
            d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=(20, 20, 20))
    save(im, "die")

# A virtual pet's face: the LCD with a little pixel creature and three icons
def vpet_screen():
    im = Image.new("RGB", (64, 56), (170, 186, 150))
    d = ImageDraw.Draw(im)
    blob = ["..XXXX..", ".X....X.", "X.X..X.X", "X......X", "X.XXXX.X", ".X....X.", "..X..X.."]
    for y, row in enumerate(blob):
        for x, c in enumerate(row):
            if c == "X": d.rectangle([20 + x * 3, 14 + y * 3, 22 + x * 3, 16 + y * 3], fill=(30, 40, 30))
    for i in range(4):
        d.rectangle([6 + i * 15, 3, 12 + i * 15, 8], fill=(60, 70, 55))
    save(im, "vpet_screen")

# The price-tag card behind each bin's number
# (256 x 204: the number, the prize's name, a red band for "TICKETS"; words drawn by prizes.gd)
def tag():
    im = Image.new("RGB", (256, 204), (252, 252, 248))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 255, 203], outline=(30, 30, 30), width=5)
    d.rectangle([5, 162, 250, 198], fill=(200, 24, 36))
    save(im, "tag")

# A basketball on a SphereMesh's UV: pebbled orange, black seams (four meridians, the equator, two curves)
def ball():
    im = Image.new("RGB", (512, 256), (214, 100, 36))
    d = ImageDraw.Draw(im)
    for i in range(9000):
        x = rnd.randrange(512); y = rnd.randrange(256); g = rnd.randrange(-18, 10)
        d.point((x, y), fill=(214 + g, 100 + g // 2, 36))
    for x in [0, 128, 256, 384, 511]:
        d.line([(x, 0), (x, 256)], fill=(25, 15, 10), width=4)
    d.line([(0, 128), (512, 128)], fill=(25, 15, 10), width=4)
    for c in [64, 320]:
        pts = [(c + 52 * math.sin(math.pi * y / 256.0), y) for y in range(0, 257, 8)]
        d.line(pts, fill=(25, 15, 10), width=4)
    save(im, "ball")

for fn in [pog_card, candy_box, chew, weave, slap, rainbow, die, vpet_screen, tag, ball]:
    fn()
print("prizes painted")
