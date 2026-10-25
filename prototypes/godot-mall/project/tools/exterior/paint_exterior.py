"""Paints the outside's tiling textures into tex/ex/ (tools/exterior/exterior.gd, wing 3).
Each texture covers the metres noted on it (uvscale in exterior.gd matches).
Run: python3 tools/exterior/paint_exterior.py
"""
import os
import numpy as np
from PIL import Image, ImageFilter

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "tex", "ex")
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(1969)


def save(name, arr):
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(os.path.join(OUT, name + ".png"))
    print("wrote", name)


def noise(h, w, scale, amp):
    """Soft blotchy noise (blurred random), amplitude amp around 0."""
    small = rng.random((max(2, h // scale), max(2, w // scale)))
    im = Image.fromarray((small * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR)
    return (np.asarray(im).astype(np.float32) / 255.0 - 0.5) * 2.0 * amp


def brick(name, px, metres, unit_w, unit_h, base, var, mortar, speckle=0.0, joint=0.012):
    """Running-bond brick: px pixels for `metres` metres. base/var colours, mortar colour."""
    pm = px / metres
    img = np.zeros((px, px, 3), np.float32) + np.array(mortar, np.float32)
    rows = int(round(metres / unit_h))
    cols = int(round(metres / unit_w))
    jw = max(1, int(joint * pm))
    for r in range(rows):
        y0 = int(r * unit_h * pm); y1 = int((r + 1) * unit_h * pm) - jw
        off = (unit_w * 0.5 * pm) if r % 2 else 0.0
        for c in range(-1, cols + 1):
            x0 = int(c * unit_w * pm + off); x1 = int((c + 1) * unit_w * pm + off) - jw
            col = np.array(base, np.float32) + (rng.random(3) - 0.5) * 2.0 * np.array(var, np.float32)
            xa, xb = max(0, x0), min(px, x1)
            if xb > xa:
                img[y0:y1, xa:xb] = col
                if speckle > 0:
                    # dark ironspot flecks
                    n = int((xb - xa) * (y1 - y0) * speckle)
                    ys = rng.integers(y0, y1, n); xs = rng.integers(xa, xb, n)
                    img[ys, xs] *= 0.45
    img += noise(px, px, 16, 6.0)[..., None]
    save(name, img)


def flat(name, px, base, amp, scale, grain=0.0):
    img = np.zeros((px, px, 3), np.float32) + np.array(base, np.float32)
    img += noise(px, px, scale, amp)[..., None]
    if grain:
        img += (rng.random((px, px, 1)) - 0.5) * 2.0 * grain
    save(name, img)


# JCPenney: natural cream face brick with dark ironspot speckles, long thin units ~4:1 (4488 f025)
brick("brick_cream", 1024, 2.0, 0.40, 0.10, (226, 214, 190), (10, 8, 8), (205, 196, 180), speckle=0.004)
# cinema box: salmon-red variegated brick, flat parapet (4486 f014-037)
brick("brick_salmon", 1024, 2.0, 0.20, 0.0667, (196, 118, 96), (22, 16, 12), (190, 176, 160))
# store backs north of the Concourse row: tan-brown brick (4486 f031-052)
brick("brick_tan", 1024, 2.0, 0.20, 0.0667, (172, 136, 100), (18, 14, 12), (184, 172, 154))
# the taller red-brick block (Woolworth's back) and the Dillard's rear lane three-band brick
brick("brick_red", 1024, 2.0, 0.20, 0.0667, (150, 76, 58), (18, 12, 10), (178, 166, 150))
# Sears loading: white painted block
brick("block_white", 1024, 2.0, 0.40, 0.20, (232, 230, 224), (5, 5, 5), (210, 208, 202), joint=0.008)
# the outparcels: brown brick piers
brick("brick_brown", 1024, 2.0, 0.20, 0.0667, (112, 78, 56), (16, 12, 10), (150, 140, 126))

# Cucos: white heavy skip-trowel stucco (4406 f022-026)
flat("stucco_white", 512, (236, 232, 222), 14.0, 6, grain=6.0)
# peach / cream EIFS fields (East facade, the entrances)
flat("stucco_cream", 512, (228, 214, 186), 7.0, 10, grain=2.0)
flat("stucco_peach", 512, (226, 190, 160), 7.0, 10, grain=2.0)
flat("stucco_tan", 512, (196, 170, 130), 7.0, 10, grain=2.0)

# the lot: jointed exposed-aggregate concrete panels ~6 x 6 m, tar-sealed joints (4486 f036-076);
# one texture = one 6 m panel, the joint along its top and left edge
px = 1024
img = np.zeros((px, px, 3), np.float32) + np.array((152, 147, 136), np.float32)
img += noise(px, px, 24, 10.0)[..., None]
img += (rng.random((px, px, 1)) - 0.5) * 2.0 * 14.0        # the aggregate
# a few darker tar patches and tyre marks
for _ in range(6):
    cx, cy = rng.integers(0, px, 2); r = rng.integers(40, 160)
    yy, xx = np.ogrid[:px, :px]
    img[(yy - cy) ** 2 + (xx - cx) ** 2 < r * r] -= 8.0
jw = int(0.05 / 6.0 * px) + 2
img[:jw, :] = (58, 54, 50); img[:, :jw] = (58, 54, 50)
save("concrete_panel", img)

# asphalt roads
flat("asphalt", 512, (78, 76, 74), 6.0, 8, grain=8.0)
# mulch beds and lawn
flat("mulch", 512, (74, 52, 36), 10.0, 6, grain=12.0)
flat("grass", 512, (96, 128, 60), 10.0, 8, grain=10.0)
# exposed-aggregate precast (the cinema-wing exit fascia): brown pebble
flat("aggregate", 512, (128, 104, 82), 8.0, 3, grain=30.0)

# chain-link fence (alpha): a diamond mesh, 1 texture = 1 m
px = 256
a = np.zeros((px, px), np.float32)
yy, xx = np.mgrid[:px, :px]
pitch = px / 18.0
for d in ((xx + yy), (xx - yy)):
    a[np.abs((d % pitch) - pitch * 0.5) < 1.2] = 1.0
rgb = np.zeros((px, px, 4), np.float32); rgb[..., :3] = (150, 150, 148); rgb[..., 3] = a * 255
Image.fromarray(rgb.astype(np.uint8), "RGBA").save(os.path.join(OUT, "chainlink.png")); print("wrote chainlink")
