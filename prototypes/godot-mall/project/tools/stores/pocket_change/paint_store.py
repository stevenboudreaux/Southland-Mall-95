"""Textures for Pocket Change's front and room (store.gd), written to tex/pc/store_*.png.

From Steven's 2009 photo of the Southland front (unchanged since the 1990s):
pale blue-green glossy 12-inch wall tile, clear glass-block columns. The room
is guessed from other Pocket Change arcades of the time (Steven's references):
a black ceiling, dark walls, and a dark patterned arcade carpet.
  python3 tools/stores/pocket_change/paint_store.py   (from the project folder)
"""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "..", "tex", "pc")
os.makedirs(OUT, exist_ok=True)


def save(im, name):
    im.save(os.path.join(OUT, "store_" + name + ".png"), optimize=True)


def noise(w, h, amp, seed, blur=0):
    r = np.random.default_rng(seed)
    a = r.normal(0, amp, (h, w)).astype(np.float32)
    if blur:
        im = Image.fromarray(np.clip(a * 4 + 128, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(blur))
        a = (np.asarray(im).astype(np.float32) - 128) / 4
    return a


def tile():
    """1.2 m x 1.2 m: 4 x 4 twelve-inch glazed tiles, pale blue-green, thin light-grey grout."""
    N = 512
    px = N / 1.2
    rng = random.Random(7)
    base = np.array([176, 208, 207], np.float32)   # pale powder blue-green (photo, corrected for the dim exposure)
    img = np.zeros((N, N, 3), np.float32)
    for j in range(4):
        for i in range(4):
            tone = rng.uniform(-6, 6)
            tint = np.array([rng.uniform(-3, 3), rng.uniform(-2, 2), rng.uniform(-2, 3)])
            x0, x1 = int(i * N / 4), int((i + 1) * N / 4)
            y0, y1 = int(j * N / 4), int((j + 1) * N / 4)
            img[y0:y1, x0:x1] = base + tone + tint
            # a soft glaze bloom toward one corner of each tile
            yy, xx = np.mgrid[y0:y1, x0:x1]
            cx, cy = x0 + (x1 - x0) * rng.uniform(0.3, 0.7), y0 + (y1 - y0) * rng.uniform(0.3, 0.7)
            d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / (N / 4)
            img[y0:y1, x0:x1] += (np.clip(1 - d, 0, 1) ** 2 * 6)[..., None]
    img += noise(N, N, 2.0, 3)[..., None]
    g = int(round(0.003 * px)) + 1     # ~5 mm light grout, clearly visible in the photo
    for k in range(5):
        c = int(k * N / 4)
        for o in range(-g, g):
            img[:, (c + o) % N] = [214, 216, 210]
            img[(c + o) % N, :] = [214, 216, 210]
    save(Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)), "tile")


def glassblock():
    """0.4 m x 0.8 m: 2 x 4 clear glass blocks (~19 cm + 1 cm mortar): wavy refraction, a grey mortar grid."""
    W, H = 256, 512
    px = W / 0.4
    img = np.zeros((H, W, 3), np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    bx = (xx % (W / 2)) / (W / 2)
    by = (yy % (H / 4)) / (H / 4)
    # the face's wave pattern: soft vertical flutes plus the dome's light falloff
    wave = 0.5 + 0.5 * np.sin(bx * math.pi * 7 + np.sin(by * math.pi * 2) * 0.8)
    dome = 1 - (((bx - 0.5) * 2) ** 2 + ((by - 0.5) * 2) ** 2) * 0.35
    v = 135 + wave * 70 * dome + dome * 35
    img[..., 0] = v * 0.94
    img[..., 1] = v * 1.0
    img[..., 2] = v * 0.99
    # the block's pressed rim (darker, then a bright edge)
    rim = np.minimum(np.minimum(bx, 1 - bx), np.minimum(by, 1 - by))
    img *= np.clip(0.75 + rim * 6, 0.75, 1.0)[..., None]
    img += (np.exp(-((rim - 0.06) / 0.015) ** 2) * 40)[..., None]
    img += noise(W, H, 3, 11)[..., None]
    m = int(round(0.01 * px))
    for k in range(3):
        c = int(k * W / 2)
        img[:, max(0, c - m // 2):min(W, c + m // 2 + 1)] = [196, 194, 188]
    for k in range(5):
        c = int(k * H / 4)
        img[max(0, c - m // 2):min(H, c + m // 2 + 1), :] = [196, 194, 188]
    save(Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)), "glassblock")


def carpet():
    """2 m x 2 m, seamless: a 1990s arcade carpet, near-black with scattered neon squiggles,
    triangles, dots and zigzags (an original pattern in the style of the time)."""
    N = 1024
    rng = random.Random(1995)
    im = Image.new("RGB", (N, N), (14, 12, 20))
    d = ImageDraw.Draw(im)
    cols = [(214, 36, 138), (30, 190, 196), (240, 206, 46), (120, 64, 236), (60, 120, 240), (236, 112, 40)]

    def wrap(fn):
        for ox in (-N, 0, N):
            for oy in (-N, 0, N):
                fn(ox, oy)

    for _ in range(70):   # squiggles
        c = rng.choice(cols)
        x, y = rng.uniform(0, N), rng.uniform(0, N)
        ang = rng.uniform(0, math.tau)
        L = rng.uniform(50, 110)
        pts = []
        for k in range(14):
            t = k / 13
            px_ = x + math.cos(ang) * L * t - math.sin(ang) * math.sin(t * math.pi * 3) * 10
            py_ = y + math.sin(ang) * L * t + math.cos(ang) * math.sin(t * math.pi * 3) * 10
            pts.append((px_, py_))
        wrap(lambda ox, oy: d.line([(p[0] + ox, p[1] + oy) for p in pts], fill=c, width=6, joint="curve"))
    for _ in range(55):   # triangles (outlined)
        c = rng.choice(cols)
        x, y = rng.uniform(0, N), rng.uniform(0, N)
        r = rng.uniform(16, 30)
        a0 = rng.uniform(0, math.tau)
        tri = [(x + r * math.cos(a0 + k * math.tau / 3), y + r * math.sin(a0 + k * math.tau / 3)) for k in range(3)]
        wrap(lambda ox, oy: d.polygon([(p[0] + ox, p[1] + oy) for p in tri], outline=c, width=5))
    for _ in range(140):  # dots
        c = rng.choice(cols)
        x, y = rng.uniform(0, N), rng.uniform(0, N)
        r = rng.uniform(4, 9)
        wrap(lambda ox, oy: d.ellipse([x - r + ox, y - r + oy, x + r + ox, y + r + oy], fill=c))
    for _ in range(35):   # zigzags
        c = rng.choice(cols)
        x, y = rng.uniform(0, N), rng.uniform(0, N)
        ang = rng.uniform(0, math.tau)
        pts = []
        for k in range(6):
            s = 14 * k
            o = 10 if k % 2 else -10
            pts.append((x + math.cos(ang) * s - math.sin(ang) * o, y + math.sin(ang) * s + math.cos(ang) * o))
        wrap(lambda ox, oy: d.line([(p[0] + ox, p[1] + oy) for p in pts], fill=c, width=5))
    a = np.asarray(im).astype(np.float32)
    # cut-pile texture: per-pixel fibre noise, a little softness, a hint of traffic wear
    a = np.asarray(Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.1))).astype(np.float32)
    a *= (1 + noise(N, N, 0.10, 5))[..., None]
    a += noise(N, N, 3, 6, blur=6)[..., None]
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "carpet")


def wall():
    """1 m x 1 m, seamless: flat dark charcoal-navy paint, roller stipple."""
    N = 256
    a = np.zeros((N, N, 3), np.float32) + np.array([30, 30, 40], np.float32)
    a += noise(N, N, 2.5, 21)[..., None]
    a += noise(N, N, 3.0, 22, blur=3)[..., None]
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "wall")


def ceiling():
    """1.22 m x 2.44 m: two black 2' x 4' lay-in tiles side by side, matte black grid."""
    W, H = 256, 512
    a = np.zeros((H, W, 3), np.float32) + 22
    a += noise(W, H, 4, 31)[..., None] * np.array([1, 1, 1])
    a += noise(W, H, 3, 32, blur=2)[..., None]
    g = 3
    for c in (0, W // 2, W - 1):
        a[:, max(0, c - g):c + g] = 40
    for c in (0, H - 1):
        a[max(0, c - g):c + g, :] = 40
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "ceiling")


def main():
    tile()
    glassblock()
    carpet()
    wall()
    ceiling()
    print("wrote tex/pc/store_*.png")


if __name__ == "__main__":
    main()
