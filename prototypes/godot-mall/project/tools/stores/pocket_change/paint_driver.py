#!/usr/bin/env python3
"""Texture painter for the Pocket Change `driver` prop module (driver.gd):
the twin sit-down racer (2 styles) and the pinball machine (3 styles).

Writes every texture the module uses to tex/pc/driver_<name>.png. Deterministic:
every random draw is seeded, so re-running reproduces the same files.

All titles and artwork are invented (BAYOU 500, TORQUE STORM, NEBULA RUN,
DEEP REEF, MAGMA MADNESS); nothing is copied from a real machine.

    python3 tools/stores/pocket_change/paint_driver.py
"""
import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "..", "tex", "pc"))

FONT_DIRS = ["/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/truetype/liberation",
             "/usr/share/fonts/truetype/freefont", "/usr/share/fonts/truetype/google-fonts"]


def font(name, size):
    for d in FONT_DIRS:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return ImageFont.truetype(p, int(size))
    return ImageFont.load_default()


F_HEAVY_IT = "DejaVuSans-BoldOblique.ttf"
F_HEAVY = "DejaVuSans-Bold.ttf"
F_COND = "DejaVuSansCondensed-Bold.ttf"
F_COND_IT = "DejaVuSansCondensed-BoldOblique.ttf"
F_POP_IT = "Poppins-BoldItalic.ttf"
F_POP = "Poppins-Bold.ttf"
F_SANS = "LiberationSans-Bold.ttf"
F_SANSR = "LiberationSans-Regular.ttf"
F_MONO = "DejaVuSansMono-Bold.ttf"

SIZES = {}


# ------------------------------------------------------------------ basics
def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def vnoise(w, h, cell, seed):
    """Smooth value noise in [0,1], feature size `cell` px."""
    r = np.random.default_rng(seed)
    gw, gh = max(2, w // cell + 3), max(2, h // cell + 3)
    a = (r.random((gh, gw)) * 255).astype(np.uint8)
    im = Image.fromarray(a, "L").resize((gw * cell, gh * cell), Image.BICUBIC)
    return np.asarray(im, np.float32)[cell:cell + h, cell:cell + w] / 255.0


def fbm(w, h, cell, seed, oct=4):
    t = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for i in range(oct):
        c = max(1, cell >> i)
        t += vnoise(w, h, c, seed + i * 17) * amp
        tot += amp
        amp *= 0.5
    return t / tot


def arr(im):
    return np.asarray(im.convert("RGB"), np.float32) / 255.0


def img(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")


def grime(a, amt, seed, cell=48):
    n = fbm(a.shape[1], a.shape[0], cell, seed)
    return a * (1.0 - amt * n[..., None])


def grain(a, amt, seed):
    r = np.random.default_rng(seed)
    return a + (r.random(a.shape[:2], np.float32)[..., None] - 0.5) * amt


def scuffs(im, n, seed, col=(255, 255, 255), alpha=40, maxlen=30, width=1, region=None):
    r = np.random.default_rng(seed)
    w, h = im.size
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x0, y0, x1, y1 = region if region else (0, 0, w, h)
    for _ in range(n):
        x = r.uniform(x0, x1)
        y = r.uniform(y0, y1)
        a = r.uniform(-0.6, 0.6) + (0 if r.random() < 0.7 else math.pi / 2)
        L = r.uniform(3, maxlen)
        pts = []
        bend = r.uniform(-0.15, 0.15)
        for k in range(4):
            t = k / 3
            pts.append((x + math.cos(a + bend * t) * L * t, y + math.sin(a + bend * t) * L * t))
        d.line(pts, fill=col + (int(r.uniform(0.25, 0.7) * alpha),), width=width)
    lay = lay.filter(ImageFilter.GaussianBlur(0.45))
    return Image.alpha_composite(im.convert("RGBA"), lay).convert("RGB")


def smudges(im, n, seed, alpha=18, rmax=22, region=None, col=(255, 255, 255)):
    """Greasy fingerprint ovals."""
    r = np.random.default_rng(seed)
    w, h = im.size
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x0, y0, x1, y1 = region if region else (0, 0, w, h)
    for _ in range(n):
        x, y = r.uniform(x0, x1), r.uniform(y0, y1)
        rr = r.uniform(rmax * 0.4, rmax)
        for k in range(int(rr / 2)):
            q = rr - k * 2
            d.ellipse([x - q * 0.75, y - q, x + q * 0.75, y + q], outline=col + (int(alpha * r.uniform(0.3, 1)),))
    lay = lay.filter(ImageFilter.GaussianBlur(0.6))
    return Image.alpha_composite(im.convert("RGBA"), lay).convert("RGB")


def vgrad(w, h, stops):
    """Vertical gradient; stops = [(t, (r,g,b)), ...]."""
    t = np.linspace(0, 1, h)[:, None]
    out = np.zeros((h, w, 3), np.float32)
    ts = [s[0] for s in stops]
    for c in range(3):
        vs = [s[1][c] / 255.0 for s in stops]
        out[:, :, c] = np.interp(t, ts, vs)
    return out


def save(im, name, quant=256):
    p = os.path.join(OUT, "driver_%s.png" % name)
    if quant and im.mode != "RGBA":
        im = im.convert("RGB").quantize(quant, method=Image.MEDIANCUT, dither=Image.NONE)
    if False:
        if im.mode == "RGBA":
            im = im.quantize(quant, method=Image.FASTOCTREE, dither=Image.NONE)
        else:
            im = im.convert("RGB").quantize(quant, method=Image.MEDIANCUT, dither=Image.NONE)
    im.save(p, optimize=True)
    SIZES[name] = os.path.getsize(p)


def text_mask(size, text, fnt, cx, cy, max_w=None, skew=0.0, anchor="mm", spacing=0):
    """L mask of `text` centred at (cx, cy), shrunk to fit max_w, italic-skewed."""
    w, h = size
    f = fnt
    if max_w:
        bb = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), text, font=f)
        if bb[2] - bb[0] > max_w:
            f = ImageFont.truetype(f.path, int(f.size * max_w / (bb[2] - bb[0])))
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).text((cx, cy), text, font=f, fill=255, anchor=anchor)
    if skew:
        m = m.transform(size, Image.AFFINE, (1, skew, -skew * cy, 0, 1, 0), Image.BICUBIC)
    return m


def dilate(m, r):
    if r <= 0:
        return m
    out = m
    while r > 0:
        k = min(r, 4)
        out = out.filter(ImageFilter.MaxFilter(2 * k + 1))
        r -= k
    return out


def fancy_text(im, text, fnt, cx, cy, fill, outlines=(), shadow=None, max_w=None, skew=0.0, glow=None):
    """fill: (r,g,b) or list of vertical gradient stops across the glyph height.
    outlines: [(rgb, px), ...] outermost first. shadow: (dx, dy, rgb)."""
    w, h = im.size
    m = text_mask(im.size, text, fnt, cx, cy, max_w, skew)
    bb = m.getbbox() or (0, 0, w, h)
    base = im.convert("RGBA")
    layers = []
    if glow:
        gm = dilate(m, glow[1]).filter(ImageFilter.GaussianBlur(glow[1]))
        layers.append((glow[0], gm))
    if shadow:
        r0 = outlines[0][1] if outlines else 0
        sm = ImageChops.offset(dilate(m, r0), shadow[0], shadow[1])
        layers.append((shadow[2], sm))
    for col, r in outlines:
        layers.append((col, dilate(m, r)))
    for col, mm in layers:
        solid = Image.new("RGBA", im.size, col + (255,))
        base.paste(solid, (0, 0), mm)
    if isinstance(fill, list):
        g = vgrad(w, bb[3] - bb[1] + 1, fill)
        full = np.zeros((h, w, 3), np.float32)
        full[bb[1]:bb[3] + 1] = g[:min(h, bb[3] + 1) - bb[1]]
        fimg = img(full).convert("RGBA")
    else:
        fimg = Image.new("RGBA", im.size, fill + (255,))
    base.paste(fimg, (0, 0), m)
    return base.convert("RGB")


def checker_flag(d, x, y, w, h, n=6, wave=0.0, phase=0.0, c1=(250, 250, 250), c2=(15, 15, 15)):
    """A waving chequered flag on ImageDraw d: n columns, n*h/w rows."""
    cols = n
    rows = max(2, int(round(n * h / w)))
    cw, ch = w / cols, h / rows

    def P(i, j):
        u = i / cols
        dy = math.sin(u * math.pi * 2 + phase) * wave * h
        return (x + i * cw, y + j * ch + dy)
    for i in range(cols):
        for j in range(rows):
            c = c1 if (i + j) % 2 == 0 else c2
            d.polygon([P(i, j), P(i + 1, j), P(i + 1, j + 1), P(i, j + 1)], fill=c)


# a side-view race car (unit length 1, faces left: nose at x=0)
CAR_BODY = [(0.00, 0.07), (0.03, 0.115), (0.30, 0.15), (0.42, 0.17), (0.50, 0.245), (0.63, 0.265), (0.73, 0.20),
            (0.97, 0.19), (1.00, 0.15), (0.99, 0.065), (0.90, 0.045), (0.10, 0.045)]
CAR_GLASS = [(0.515, 0.235), (0.625, 0.252), (0.70, 0.203), (0.555, 0.192)]


def draw_car(d, x, y, L, body, stripe, num, facing=-1, f_num=None):
    """x, y: rear-wheel ground point region; L: car length in px; facing -1 = left."""
    def P(px, py):
        if facing > 0:
            px = 1.0 - px
        return (x + px * L, y - py * L)
    d.polygon([P(0.08, 0.02), P(0.95, 0.02), P(0.95, 0.04), P(0.08, 0.04)], fill=(10, 10, 12))
    d.polygon([P(*p) for p in CAR_BODY], fill=body)
    # shading under the side
    d.polygon([P(0.04, 0.075), P(0.97, 0.075), P(0.98, 0.055), P(0.10, 0.05)], fill=tuple(int(c * 0.55) for c in body))
    # livery stripe
    d.polygon([P(0.05, 0.105), P(0.98, 0.135), P(0.98, 0.155), P(0.05, 0.123)], fill=stripe)
    d.polygon([P(*p) for p in CAR_GLASS], fill=(30, 40, 60))
    d.line([P(0.56, 0.20), P(0.62, 0.245)], fill=(140, 170, 210), width=max(1, int(L * 0.008)))
    # wing
    d.polygon([P(0.92, 0.19), P(0.94, 0.19), P(0.95, 0.29), P(0.93, 0.29)], fill=(20, 20, 24))
    d.polygon([P(0.86, 0.29), P(1.01, 0.30), P(1.01, 0.325), P(0.87, 0.318)], fill=stripe)
    # wheels
    for wx in (0.20, 0.80):
        cx, cy = P(wx, 0.075)
        r = 0.077 * L
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(14, 14, 16))
        r2 = 0.042 * L
        d.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], fill=(170, 172, 178))
        r3 = 0.016 * L
        d.ellipse([cx - r3, cy - r3, cx + r3, cy + r3], fill=(60, 60, 64))
    # number roundel
    cx, cy = P(0.40, 0.105)
    r = 0.042 * L
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(245, 245, 240))
    fn = f_num or font(F_HEAVY, r * 1.4)
    d.text((cx, cy), num, font=fn, fill=(10, 10, 10), anchor="mm")


def speed_lines(d, x0, x1, y, h, n, seed, col):
    r = np.random.default_rng(seed)
    for _ in range(n):
        yy = y + r.uniform(0, h)
        a = r.uniform(x0, x1)
        L = r.uniform(0.2, 0.6) * abs(x1 - x0)
        w = max(1, int(r.uniform(1, 4)))
        d.line([(a, yy), (a + L, yy)], fill=col, width=w)


def ss_new(w, h, s, col=(0, 0, 0)):
    return Image.new("RGB", (w * s, h * s), col)


# ------------------------------------------------------------------ shared
def paint_coin():
    """Coin door, 256x288: two token entries with reject buttons, lock, returns."""
    W, H, S = 256, 288, 2
    im = ss_new(W, H, S, (18, 18, 20))
    d = ImageDraw.Draw(im)
    s = S
    # outer frame (steel, rounded)
    d.rounded_rectangle([0, 0, W * s - 1, H * s - 1], 14 * s, fill=(122, 124, 128))
    d.rounded_rectangle([7 * s, 7 * s, W * s - 8 * s, H * s - 8 * s], 10 * s, fill=(28, 28, 31))
    # door seam
    d.rounded_rectangle([12 * s, 12 * s, W * s - 13 * s, H * s - 13 * s], 8 * s, outline=(8, 8, 9), width=2 * s)
    for i, cx in enumerate((78, 178)):
        # coin entry plate (chrome)
        d.rounded_rectangle([(cx - 30) * s, 30 * s, (cx + 30) * s, 132 * s], 5 * s, fill=(170, 172, 176))
        d.rounded_rectangle([(cx - 26) * s, 34 * s, (cx + 26) * s, 128 * s], 4 * s, fill=(140, 142, 146))
        # slot
        d.rectangle([(cx - 2) * s, 44 * s, (cx + 2) * s, 74 * s], fill=(6, 6, 6))
        # reject button (lit red-orange; the lamp is a separate emissive part)
        d.rounded_rectangle([(cx - 17) * s, 84 * s, (cx + 17) * s, 118 * s], 4 * s, fill=(196, 52, 30))
        d.text((cx * s, 101 * s), "PUSH", font=font(F_COND, 10 * s), fill=(255, 210, 190), anchor="mm")
        # token sticker (brass)
        d.rounded_rectangle([(cx - 28) * s, 140 * s, (cx + 28) * s, 166 * s], 3 * s, fill=(206, 162, 66))
        d.text((cx * s, 149 * s), "1 TOKEN", font=font(F_COND, 11 * s), fill=(40, 22, 0), anchor="mm")
        d.text((cx * s, 160 * s), "PER CREDIT", font=font(F_COND, 7 * s), fill=(60, 34, 0), anchor="mm")
        # coin return pocket
        d.rounded_rectangle([(cx - 24) * s, 218 * s, (cx + 24) * s, 262 * s], 5 * s, fill=(150, 152, 156))
        d.rounded_rectangle([(cx - 19) * s, 224 * s, (cx + 19) * s, 256 * s], 3 * s, fill=(8, 8, 9))
        d.text((cx * s, 268 * s), "COIN RETURN", font=font(F_COND, 7 * s), fill=(160, 160, 160), anchor="mm")
    # lock
    d.ellipse([(128 - 13) * s, 180 * s, (128 + 13) * s, 206 * s], fill=(176, 178, 182))
    d.ellipse([(128 - 9) * s, 184 * s, (128 + 9) * s, 202 * s], fill=(120, 120, 124))
    d.rectangle([(128 - 1.5) * s, 186 * s, (128 + 1.5) * s, 200 * s], fill=(20, 20, 20))
    d.text((128 * s, 22 * s), "TOKENS ONLY", font=font(F_COND, 10 * s), fill=(230, 196, 90), anchor="mm")
    im = im.resize((W, H), Image.LANCZOS)
    a = arr(im)
    a = grime(a, 0.25, 101, 24)
    a = grain(a, 0.03, 102)
    im = img(a)
    im = scuffs(im, 140, 103, (230, 230, 230), 55, 14)
    im = smudges(im, 10, 104, 14, 14)
    save(im, "coin")


def paint_vinyl():
    """Light worn vinyl (tinted per style), 256x256 over a 0.5 m x 1.2 m seat:
    two stitched pleat seams, crazing and pale wear at the centre."""
    W = H = 256
    base = np.full((H, W, 3), 0.82, np.float32)
    n = fbm(W, H, 24, 201)
    base *= (0.9 + 0.12 * n)[..., None]
    # leather-ish fine grain
    base = grain(base, 0.05, 202)
    im = img(base)
    d = ImageDraw.Draw(im)
    for x in (70, 186):
        d.line([(x, 0), (x, H)], fill=(120, 120, 120), width=3)
        for y in range(0, H, 6):
            d.line([(x - 4, y), (x - 4, y + 3)], fill=(160, 160, 160), width=1)
            d.line([(x + 4, y), (x + 4, y + 3)], fill=(160, 160, 160), width=1)
    # horizontal pleats in the centre panel
    for y in range(20, H, 40):
        d.line([(72, y), (184, y)], fill=(140, 140, 140), width=2)
    a = arr(im)
    # wear: lighter, less saturated in the middle of the pan and back
    yy, xx = np.mgrid[0:H, 0:W]
    wear = np.exp(-((xx - 128) / 55.0) ** 2) * (0.5 + 0.5 * fbm(W, H, 16, 203))
    a = a * (1 + 0.18 * wear[..., None])
    im = img(a)
    # cracks
    r = np.random.default_rng(204)
    d = ImageDraw.Draw(im)
    for _ in range(26):
        x, y = r.uniform(80, 176), r.uniform(0, H)
        pts = [(x, y)]
        for k in range(5):
            x += r.uniform(-6, 6)
            y += r.uniform(-4, 4)
            pts.append((x, y))
        d.line(pts, fill=(70, 70, 70), width=1)
    im = smudges(im, 12, 205, 10, 20, region=(60, 0, 196, 256), col=(255, 255, 255))
    save(im, "vinyl")


def paint_grille():
    W = H = 128
    im = Image.new("RGB", (W, H), (22, 22, 24))
    d = ImageDraw.Draw(im)
    for y in range(0, H, 8):
        for x in range(0, W, 8):
            ox = 4 if (y // 8) % 2 else 0
            d.ellipse([x + ox - 2.6, y + 1.4, x + ox + 2.6, y + 6.6], fill=(2, 2, 3))
    a = grime(arr(im), 0.2, 301, 32)
    save(img(a), "grille")


def paint_lam():
    """Black textured cabinet laminate, tileable-ish, 256 px per metre."""
    W = H = 256
    a = np.full((H, W, 3), 0.085, np.float32)
    a *= (0.85 + 0.3 * fbm(W, H, 32, 401))[..., None]
    a = grain(a, 0.03, 402)
    im = img(a)
    im = scuffs(im, 50, 403, (200, 200, 205), 40, 12)
    save(im, "lam")


def paint_steel():
    W = H = 128
    r = np.random.default_rng(501)
    rows = r.random((H, 1)).astype(np.float32)
    streak = np.asarray(Image.fromarray((r.random((H, W)) * 255).astype(np.uint8)).filter(
        ImageFilter.BoxBlur(0)).resize((W, H)), np.float32) / 255.0
    line = np.asarray(Image.fromarray((r.random((H, 8)) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32) / 255
    a = 0.62 + 0.10 * line + 0.05 * streak
    a = np.repeat(a[..., None], 3, 2) * np.array([1.0, 1.0, 1.03])
    a = grime(a, 0.18, 502, 32)
    save(img(a), "steel")


def paint_tmold():
    W, H = 64, 64
    a = np.full((H, W, 3), 0.75, np.float32)
    a[:, :, :] *= (0.9 + 0.12 * fbm(W, H, 8, 601))[..., None]
    a[H // 2 - 2:H // 2 + 2] *= 0.6  # centre rib
    im = img(a)
    im = scuffs(im, 50, 602, (255, 255, 255), 90, 10)
    save(im, "tmold")


def paint_diamond():
    W = H = 128
    a = np.full((H, W, 3), 0.42, np.float32)
    im = img(a)
    d = ImageDraw.Draw(im)
    for j in range(0, H + 16, 16):
        for i in range(0, W + 16, 16):
            ox = 8 if (j // 16) % 2 else 0
            cx, cy = i + ox, j
            d.polygon([(cx - 6, cy + 2), (cx + 2, cy - 6), (cx + 6, cy - 2), (cx - 2, cy + 6)], fill=(170, 172, 176))
            d.line([(cx - 6, cy + 2), (cx + 2, cy - 6)], fill=(210, 212, 215), width=1)
    a = grime(arr(im), 0.45, 701, 24)
    a = grain(a, 0.04, 702)
    im = scuffs(img(a), 60, 703, (230, 230, 230), 60, 16)
    save(im, "diamond")


def paint_glass():
    """RGBA: faint fingerprints and wipe streaks for glass; alpha carries them."""
    W = H = 256
    lay = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    r = np.random.default_rng(801)
    d = ImageDraw.Draw(lay)
    for _ in range(20):
        x, y = r.uniform(0, W), r.uniform(0, H)
        rr = r.uniform(5, 13)
        for k in range(int(rr / 1.6)):
            q = rr - k * 1.6
            d.ellipse([x - q * 0.7, y - q, x + q * 0.7, y + q], outline=(255, 255, 255, int(r.uniform(10, 28))))
    for _ in range(6):  # wipe arcs
        x, y = r.uniform(0, W), r.uniform(0, H)
        R = r.uniform(40, 90)
        d.arc([x - R, y - R, x + R, y + R], r.uniform(0, 360), r.uniform(0, 360), fill=(255, 255, 255, 14), width=6)
    lay = lay.filter(ImageFilter.GaussianBlur(0.8))
    a = np.asarray(lay).copy()
    a[:, :, 3] = np.clip(a[:, :, 3].astype(np.int32) + 10, 0, 255)  # base film
    save(Image.fromarray(a, "RGBA"), "glass")


def paint_apron():
    """Pinball apron (0.60 x 0.15 m, flat black painted steel) with two
    instruction cards and the drain notch. 512x128."""
    W, H, S = 512, 128, 2
    im = ss_new(W, H, S, (24, 24, 28))
    d = ImageDraw.Draw(im)
    s = S
    # cards
    for i, cx in enumerate((92, 340)):
        x0, y0, x1, y1 = (cx - 66) * s, 22 * s, (cx + 66) * s, 108 * s
        d.rectangle([x0 - 3 * s, y0 - 3 * s, x1 + 3 * s, y1 + 3 * s], fill=(120, 120, 124))
        d.rectangle([x0, y0, x1, y1], fill=(236, 230, 214))
        if i == 0:
            lines = [("INSTRUCTIONS", 11, True), ("1. INSERT TOKENS", 8, False), ("2. PRESS START BUTTON", 8, False),
                     ("3. PULL PLUNGER TO SERVE", 8, False), ("UP TO 4 PLAYERS", 8, False), ("3 BALLS PER GAME", 8, True)]
        else:
            lines = [("REPLAY AT", 11, True), ("2,500,000", 14, True), ("MATCH AWARDS", 8, False),
                     ("1 REPLAY", 8, False), ("TILT DOES NOT", 7, False), ("DISQUALIFY PLAYER", 7, False)]
        y = y0 + 9 * s
        for t, sz, bold in lines:
            d.text(((x0 + x1) / 2, y), t, font=font(F_COND if bold else F_SANSR, sz * s), fill=(20, 20, 30), anchor="mm")
            y += (sz + 4) * s
    # drain notch shading at the back edge middle
    d.polygon([(190 * s, 0), (222 * s, 0), (214 * s, 10 * s), (198 * s, 10 * s)], fill=(8, 8, 10))
    # shooter lane cutout region (right): darker
    d.rectangle([(W - 38) * s, 0, W * s, H * s], fill=(16, 16, 18))
    im = im.resize((W, H), Image.LANCZOS)
    a = grime(arr(im), 0.25, 901, 20)
    im = scuffs(img(a), 120, 902, (210, 210, 210), 70, 12)
    save(im, "apron")


def paint_inserts():
    """RGBA insert atlas, 4x2 cells of 64x64: lit plastic inserts (arrow,
    circle, triangle, star) in playfield colours; alpha = shape."""
    W, H = 256, 128
    S = 4
    big = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    cells = [("arrow", (255, 60, 40)), ("arrow", (255, 210, 40)), ("arrow", (60, 220, 90)), ("arrow", (60, 150, 255)),
             ("circle", (255, 250, 230)), ("circle", (255, 140, 30)), ("circle", (255, 60, 40)), ("circle", (255, 205, 40))]
    for k, (shape, col) in enumerate(cells):
        ox, oy = (k % 4) * 64 * S, (k // 4) * 64 * S
        c = 32 * S
        if shape == "arrow":
            # same proportions as paint_pf's ins_arrow: origin (32, 42), L = 40 px
            L = 40
            a0 = [(0, -L), (0.5 * L, -0.2 * L), (0.22 * L, -0.2 * L), (0.22 * L, 0.5 * L), (-0.22 * L, 0.5 * L), (-0.22 * L, -0.2 * L), (-0.5 * L, -0.2 * L)]
            pts = [((32 + x) * S, (42 + y) * S) for x, y in a0]
        elif shape == "circle":
            pts = None
            d.ellipse([ox + 6 * S, oy + 6 * S, ox + 58 * S, oy + 58 * S], fill=col + (255,))
            d.ellipse([ox + 18 * S, oy + 14 * S, ox + 40 * S, oy + 32 * S], fill=tuple(min(255, v + 60) for v in col) + (255,))
        elif shape == "star":
            pts = []
            for i in range(10):
                a = -math.pi / 2 + i * math.pi / 5
                rr = (28 if i % 2 == 0 else 12) * S
                pts.append((c + math.cos(a) * rr, c + math.sin(a) * rr + 2 * S))
        else:
            pts = [(c, 6 * S), (58 * S, 56 * S), (6 * S, 56 * S)]
        if pts:
            d.polygon([(ox + x, oy + y) for x, y in pts], fill=col + (255,))
            # hot centre
            cx = sum(p[0] for p in pts) / len(pts)
            cy = sum(p[1] for p in pts) / len(pts)
            d.polygon([(ox + cx + (x - cx) * 0.45, oy + cy + (y - cy) * 0.45) for x, y in pts],
                      fill=tuple(min(255, v + 90) for v in col) + (255,))
    im = big.resize((W, H), Image.LANCZOS)
    save(im, "ins")


# ------------------------------------------------------------------ racer
RACER = [
    dict(title="BAYOU 500", sub="TWIN  LINKED  RACING", bg=[(0, (30, 8, 40)), (0.55, (190, 50, 30)), (0.8, (250, 150, 40)), (1, (255, 214, 120))],
         ink=(255, 218, 40), outline=(160, 12, 12), body=(214, 28, 24), stripe=(255, 210, 40), body2=(30, 90, 210), stripe2=(240, 240, 240),
         side=(16, 14, 18), sideA=(214, 32, 26), sideB=(255, 186, 30), seat=(170, 24, 22)),
    dict(title="TORQUE STORM", sub="2  PLAYER  CHALLENGE", bg=[(0, (4, 6, 20)), (0.6, (16, 40, 120)), (1, (40, 120, 230))],
         ink=(255, 240, 60), outline=(10, 30, 130), body=(250, 200, 20), stripe=(20, 20, 20), body2=(230, 230, 236), stripe2=(30, 120, 240),
         side=(10, 22, 70), sideA=(255, 220, 40), sideB=(240, 244, 255), seat=(26, 40, 92)),
]


def cypress(d, x, base, h, col):
    """A bald cypress silhouette with moss."""
    d.polygon([(x - h * 0.08, base), (x - h * 0.02, base - h * 0.75), (x + h * 0.02, base - h * 0.75), (x + h * 0.08, base)], fill=col)
    r = np.random.default_rng(int(x * 7 + h))
    for k in range(7):
        cx = x + r.uniform(-h * 0.22, h * 0.22)
        cy = base - h * r.uniform(0.6, 1.0)
        rw, rh = h * r.uniform(0.12, 0.22), h * r.uniform(0.05, 0.09)
        d.ellipse([cx - rw, cy - rh, cx + rw, cy + rh], fill=col)
        for m in range(3):
            mx = cx + r.uniform(-rw, rw)
            d.line([(mx, cy), (mx + r.uniform(-2, 2), cy + h * r.uniform(0.06, 0.14))], fill=col, width=2)


def lightning(d, x, y0, y1, seed, col, w):
    r = np.random.default_rng(seed)
    pts = [(x, y0)]
    y = y0
    while y < y1:
        y += r.uniform(8, 22)
        x += r.uniform(-16, 16)
        pts.append((x, y))
    d.line(pts, fill=col, width=w)
    return pts


def paint_racer_marquee(s):
    P = RACER[s]
    W, H, S = 1024, 224, 2
    a = vgrad(W * S, H * S, P["bg"])
    im = img(a)
    d = ImageDraw.Draw(im)
    if s == 0:
        # sun, water, cypress swamp silhouette
        d.ellipse([560 * S, 70 * S, 700 * S, 210 * S], fill=(255, 230, 150))
        for k in range(8):
            yy = (150 + k * 9) * S
            d.rectangle([0, yy, W * S, yy + 3 * S], fill=(120 - k * 6, 30, 30))
        for x, h in ((40, 150), (130, 120), (230, 160), (850, 140), (940, 170), (1000, 120)):
            cypress(d, x * S, 168 * S, h * S, (26, 6, 22))
        d.rectangle([0, 166 * S, W * S, H * S], fill=(40, 10, 28))
    else:
        for k, x in enumerate((80, 300, 760, 960)):
            lightning(d, x * S, 0, 150 * S, 1100 + k, (190, 220, 255), 3 * S)
        d.rectangle([0, 166 * S, W * S, H * S], fill=(6, 10, 30))
    # track edge and speed lines
    d.polygon([(0, 186 * S), (W * S, 170 * S), (W * S, 224 * S), (0, 224 * S)], fill=(34, 34, 40))
    for i in range(0, W, 48):
        d.polygon([(i * S, (186 - i * 16 / W) * S), ((i + 24) * S, (186 - (i + 24) * 16 / W) * S),
                   ((i + 24) * S, (192 - (i + 24) * 16 / W) * S), (i * S, (192 - i * 16 / W) * S)], fill=(220, 30, 30) if s == 0 else (240, 210, 30))
    speed_lines(d, 0, 300 * S, 120 * S, 70 * S, 26, 1200 + s, (255, 255, 255))
    speed_lines(d, 724 * S, W * S, 120 * S, 70 * S, 26, 1300 + s, (255, 255, 255))
    draw_car(d, 40 * S, 206 * S, 300 * S, P["body"], P["stripe"], "5", facing=+1)
    draw_car(d, 690 * S, 206 * S, 300 * S, P["body2"], P["stripe2"], "9", facing=-1)
    # chequered flags in the corners
    checker_flag(d, 6 * S, 8 * S, 120 * S, 64 * S, 8, 0.12, 0.3)
    checker_flag(d, 898 * S, 8 * S, 120 * S, 64 * S, 8, 0.12, 2.1)
    im = im.resize((W, H), Image.LANCZOS)
    # title
    if s == 0:
        im = fancy_text(im, P["title"], font(F_HEAVY_IT, 118), 512, 92, [(0, (255, 255, 220)), (0.45, (255, 214, 40)), (0.55, (230, 120, 10)), (1, (255, 220, 80))],
                        outlines=[((20, 4, 12), 10), (P["outline"], 6), ((255, 255, 255), 2)], shadow=(6, 7, (0, 0, 0)), max_w=640, skew=-0.18)
    else:
        im = fancy_text(im, P["title"], font(F_HEAVY_IT, 104), 512, 90, [(0, (255, 255, 255)), (0.48, (200, 220, 255)), (0.52, (30, 60, 160)), (1, (220, 240, 255))],
                        outlines=[((0, 0, 0), 10), ((255, 220, 40), 6), ((10, 20, 80), 2)], shadow=(6, 7, (0, 0, 0)), max_w=680, skew=-0.2)
    im = fancy_text(im, P["sub"], font(F_HEAVY_IT, 22), 512, 162, (255, 255, 255), outlines=[((0, 0, 0), 3)], skew=-0.2)
    a = arr(im)
    a = grime(a, 0.10, 1400 + s, 40)
    # fluorescent tube banding (two tubes behind the plex)
    yy = np.linspace(0, 1, H)[:, None]
    band = 0.88 + 0.12 * (np.exp(-((yy - 0.3) / 0.18) ** 2) + np.exp(-((yy - 0.72) / 0.18) ** 2))
    xx = np.linspace(0, 1, W)[None, :]
    band = band * (0.86 + 0.14 * np.clip(np.sin(xx * math.pi) * 1.5, 0, 1))
    a = a * band[..., None]
    save(img(a), "rmarq%d" % s)


def paint_racer_screen(s):
    """Two 256x192 CRT frames side by side: player 1 and player 2 views of an
    original road race (chase camera), with HUD."""
    P = RACER[s]
    W, H = 256, 192
    out = Image.new("RGB", (W * 2, H))
    for pl in range(2):
        S = 3
        im = Image.new("RGB", (W * S, H * S))
        d = ImageDraw.Draw(im)
        hz = 78 * S
        if s == 0:
            sky = vgrad(W * S, hz, [(0, (70, 120, 230)), (1, (190, 220, 250))])
        else:
            sky = vgrad(W * S, hz, [(0, (230, 120, 60)), (1, (255, 210, 140))])
        im.paste(img(sky), (0, 0))
        # distant hills / grandstand
        r = np.random.default_rng(1500 + s * 10 + pl)
        pts = [(0, hz)]
        for x in range(0, W * S + 30, 30):
            pts.append((x, hz - r.uniform(6, 22) * S))
        pts.append((W * S, hz))
        d.polygon(pts, fill=(60, 110, 70) if s == 0 else (120, 70, 90))
        gx = (20 if pl == 0 else 130) * S
        d.polygon([(gx, hz), (gx + 10 * S, hz - 18 * S), (gx + 100 * S, hz - 18 * S), (gx + 110 * S, hz)], fill=(150, 150, 160))
        for k in range(5):
            d.line([(gx + 6 * S + k * 2 * S, hz - k * 3.5 * S), (gx + 104 * S - k * 2 * S, hz - k * 3.5 * S)], fill=(200, 60, 60) if k % 2 else (60, 60, 200), width=S)
        # ground
        d.rectangle([0, hz, W * S, H * S], fill=(70, 130, 50) if s == 0 else (150, 120, 70))
        # road (curving to the right for P1, left for P2)
        bend = (40 if pl == 0 else -34) * S
        cx = W * S / 2
        rows = 40
        for i in range(rows):
            t0, t1 = i / rows, (i + 1) / rows
            y0 = hz + (H * S - hz) * t0 ** 1.0
            y1 = hz + (H * S - hz) * t1 ** 1.0
            w0, w1 = 6 * S + 230 * S * t0, 6 * S + 230 * S * t1
            c0 = cx + bend * (1 - t0) ** 2
            c1 = cx + bend * (1 - t1) ** 2
            stripe = int((1 - t0) ** 0.6 * 14) % 2
            d.polygon([(c0 - w0 / 2 - w0 * 0.08, y0), (c0 + w0 / 2 + w0 * 0.08, y0), (c1 + w1 / 2 + w1 * 0.08, y1), (c1 - w1 / 2 - w1 * 0.08, y1)],
                      fill=(230, 230, 230) if stripe else (210, 30, 30))
            d.polygon([(c0 - w0 / 2, y0), (c0 + w0 / 2, y0), (c1 + w1 / 2, y1), (c1 - w1 / 2, y1)], fill=(92, 92, 98) if stripe else (84, 84, 90))
            if stripe:
                d.polygon([(c0 - w0 * 0.012, y0), (c0 + w0 * 0.012, y0), (c1 + w1 * 0.012, y1), (c1 - w1 * 0.012, y1)], fill=(240, 240, 240))
        # rival car ahead (small)
        def rear_car(cx, cy, sc, body, stripe):
            w, h = 60 * sc, 26 * sc
            d.rectangle([cx - w * 0.5, cy - h * 0.25, cx - w * 0.3, cy + h * 0.25], fill=(16, 16, 16))
            d.rectangle([cx + w * 0.3, cy - h * 0.25, cx + w * 0.5, cy + h * 0.25], fill=(16, 16, 16))
            d.polygon([(cx - w * 0.42, cy + h * 0.1), (cx - w * 0.36, cy - h * 0.45), (cx + w * 0.36, cy - h * 0.45), (cx + w * 0.42, cy + h * 0.1)], fill=body)
            d.polygon([(cx - w * 0.2, cy - h * 0.45), (cx - w * 0.14, cy - h * 0.85), (cx + w * 0.14, cy - h * 0.85), (cx + w * 0.2, cy - h * 0.45)], fill=(30, 36, 50))
            d.rectangle([cx - w * 0.46, cy - h * 1.05, cx + w * 0.46, cy - h * 0.9], fill=stripe)
            d.rectangle([cx - w * 0.04, cy - h * 0.92, cx + w * 0.04, cy - h * 0.45], fill=(20, 20, 20))
            d.rectangle([cx - w * 0.36, cy - h * 0.2, cx - w * 0.22, cy - h * 0.06], fill=(255, 60, 40))
            d.rectangle([cx + w * 0.22, cy - h * 0.2, cx + w * 0.36, cy - h * 0.06], fill=(255, 60, 40))
            d.rectangle([cx - w * 0.3, cy - h * 0.02, cx + w * 0.3, cy + h * 0.06], fill=(30, 30, 30))
        tb = 0.45
        yb = hz + (H * S - hz) * tb
        rear_car(cx + bend * (1 - tb) ** 2 + (-14 if pl == 0 else 18) * S, yb, 0.75 * S,
                 P["body2"] if pl == 0 else P["body"], P["stripe2"] if pl == 0 else P["stripe"])
        # own car (chase cam)
        rear_car(cx + (6 if pl == 0 else -6) * S, 168 * S, 2.1 * S, P["body"] if pl == 0 else P["body2"], P["stripe"] if pl == 0 else P["stripe2"])
        im = im.resize((W, H), Image.LANCZOS)
        d = ImageDraw.Draw(im)
        # HUD
        hud = font(F_MONO, 13)
        small = font(F_COND, 9)
        d.text((8, 6), "TIME", font=small, fill=(255, 255, 255))
        d.text((8, 15), "%02d" % (47 - pl * 6), font=font(F_MONO, 20), fill=(255, 230, 40), stroke_width=1, stroke_fill=(0, 0, 0))
        d.text((W - 8, 6), "LAP", font=small, fill=(255, 255, 255), anchor="ra")
        d.text((W - 8, 16), "%d/3" % (2 - pl), font=hud, fill=(255, 255, 255), anchor="ra", stroke_width=1, stroke_fill=(0, 0, 0))
        d.text((W - 8, H - 26), "%d MPH" % (187 - pl * 23), font=hud, fill=(255, 255, 255), anchor="ra", stroke_width=1, stroke_fill=(0, 0, 0))
        d.text((8, H - 26), ("POS 1ST" if pl == 0 else "POS 2ND"), font=hud, fill=(120, 255, 120), stroke_width=1, stroke_fill=(0, 0, 0))
        d.text((W / 2, 8), "PLAYER %d" % (pl + 1), font=small, fill=(255, 255, 255), anchor="ma")
        # tacho bar
        for k in range(12):
            on = k < 9 - pl * 2
            d.rectangle([W - 60 + k * 4, H - 34, W - 58 + k * 4, H - 30], fill=((255, 60, 40) if k > 8 else (255, 220, 40)) if on else (40, 40, 40))
        out.paste(im, (pl * W, 0))
    # CRT: scanlines, slight bloom, vignette per screen
    a = arr(out)
    blur = arr(out.filter(ImageFilter.GaussianBlur(1.5)))
    a = a * 0.85 + blur * 0.3
    sl = np.ones((H, 1), np.float32)
    sl[1::2] = 0.72
    a = a * sl[..., None]
    yy, xx = np.mgrid[0:H, 0:W * 2]
    u = (xx % W) / W - 0.5
    v = yy / H - 0.5
    vig = 1 - 0.55 * (u ** 2 + v ** 2) ** 1.2 * 2.5
    a = a * np.clip(vig, 0.3, 1)[..., None]
    save(img(a), "rscr%d" % s)


# racer side profile (z, y) in metres: must match driver.gd RACER_PROFILE
RP = [(0.86, 0.00), (0.86, 0.22), (1.08, 0.40), (1.08, 0.60), (0.90, 0.78), (0.96, 1.00), (1.24, 1.02), (1.40, 1.62),
      (1.18, 1.70), (1.14, 2.06), (1.62, 2.06), (1.95, 1.84), (1.95, 0.00)]
RZ0, RZ1, RYH = 0.86, 1.95, 2.06


def paint_racer_side(s):
    """Side art over the cabinet profile, 256x512. u: z 0.86..1.95 (front at
    left), v: y 2.06 (top) .. 0."""
    P = RACER[s]
    W, H, S = 256, 512, 2
    im = ss_new(W, H, S, P["side"])
    d = ImageDraw.Draw(im)

    def UV(z, y):
        return ((z - RZ0) / (RZ0 - RZ0 + RZ1 - RZ0) * W * S, (RYH - y) / RYH * H * S)
    # big sweeping stripes from low-front to high-back
    for k, (col, off, wd) in enumerate(((P["sideA"], 0.0, 0.16), (P["sideB"], 0.20, 0.06), (P["sideA"], 0.29, 0.03))):
        pts = [UV(0.86, 0.30 + off), UV(1.95, 1.10 + off), UV(1.95, 1.10 + off + wd), UV(0.86, 0.30 + off + wd)]
        d.polygon(pts, fill=col)
    # chequered band near the top
    checker_flag(d, 0, UV(0, 1.92)[1], W * S, 0.14 / RYH * H * S, 12, 0.0)
    # car silhouette and title, rotated readable text along the stripe
    draw_car(d, UV(1.25, 0)[0] - 120 * S * 0.5, UV(0, 0.62)[1], 150 * S, P["body"], P["stripe"], "5", facing=-1)
    im = im.resize((W, H), Image.LANCZOS)
    t = Image.new("RGB", (480, 90), (0, 0, 0))
    t = fancy_text(t, P["title"], font(F_HEAVY_IT, 60), 240, 45, P["ink"], outlines=[((0, 0, 0), 4)], max_w=440, skew=-0.2)
    tm = text_mask((480, 90), P["title"], font(F_HEAVY_IT, 60), 240, 45, 440, -0.2)
    tm = dilate(tm, 4)
    t = t.rotate(-33, expand=True, resample=Image.BICUBIC)
    tm = tm.rotate(-33, expand=True, resample=Image.BICUBIC)
    t = t.resize((int(t.width * 0.48), int(t.height * 0.48)), Image.LANCZOS)
    tm = tm.resize(t.size, Image.LANCZOS)
    im.paste(t, (int(W * 0.10), int(H * 0.30)), tm)
    a = arr(im)
    a = grime(a, 0.18, 1600 + s, 40)
    # kick scuffs low
    yy = np.linspace(0, 1, H)[:, None, None]
    a = a * (1 - 0.25 * np.clip((yy - 0.85) / 0.15, 0, 1))
    im = scuffs(img(a), 120, 1601 + s, (200, 200, 200), 55, 12, region=(0, int(H * 0.72), W, H))
    im = scuffs(im, 30, 1602 + s, (220, 220, 220), 35, 10)
    save(im, "rside%d" % s)


def paint_racer_panel(s):
    """Atlas 1024x512 across the 1.702 m between the side panels:
    rows 0..288 bezel (top edge = bezel top), with the two CRT openings;
    rows 288..416 console face (wheel and buttons in front of it);
    rows 416..512 kick panels."""
    P = RACER[s]
    W, H, S = 1024, 512, 2
    im = ss_new(W, H, S, (14, 14, 16))
    d = ImageDraw.Draw(im)
    s_ = S
    WM = 1.702
    # --- bezel: smoked black with printed art
    BH = 288
    bez = vgrad(W * S, BH * S, [(0, (34, 34, 40)), (1, (14, 14, 18))])
    im.paste(img(bez), (0, 0))
    d = ImageDraw.Draw(im)
    BL = 0.6210  # slope length g->h (driver.gd RP[6]->RP[7])
    for pi_, sx in enumerate((-0.435, 0.435)):
        cx = (sx + WM / 2) / WM * W
        # screen opening (matches driver.gd SCR_W/SCR_H/SCR_V)
        ow, oh, ov = 0.56, 0.43, 0.32
        x0, x1 = cx - ow / 2 / WM * W, cx + ow / 2 / WM * W
        y0 = (BL - (ov + oh / 2)) / BL * BH
        y1 = (BL - (ov - oh / 2)) / BL * BH
        # printed frame lines around the opening
        for k, col in enumerate((P["sideA"], P["sideB"])):
            g = (8 + k * 7)
            d.rounded_rectangle([(x0 - g) * s_, (y0 - g) * s_, (x1 + g) * s_, (y1 + g) * s_], 12 * s_, outline=col, width=3 * s_)
        d.rectangle([x0 * s_, y0 * s_, x1 * s_, y1 * s_], fill=(4, 4, 5))
        d.text((cx * s_, (y0 - 24) * s_), "PLAYER %d" % (pi_ + 1), font=font(F_HEAVY_IT, 15 * s_), fill=(240, 240, 240), anchor="mm")
        d.text((cx * s_, (y1 + 24) * s_), "STEP ON GAS TO START  ·  SHIFT 1-2-3-4", font=font(F_COND, 10 * s_), fill=(220, 210, 160), anchor="mm")
    # centre divider: vertical chequered strip and small title
    cxm = W / 2
    checker_flag(d, (cxm - 22) * s_, 20 * s_, 44 * s_, 250 * s_, 3, 0.0)
    # --- console face
    CY0 = 288
    con = vgrad(W * S, 128 * S, [(0, (40, 40, 46)), (1, (20, 20, 24))])
    im.paste(img(con), (0, CY0 * S))
    d = ImageDraw.Draw(im)
    for k, col in enumerate((P["sideA"], P["sideB"])):
        y = (CY0 + 10 + k * 8) * S
        d.rectangle([0, y, W * S, y + 3 * S], fill=col)
    for pi_, sx in enumerate((-0.435, 0.435)):
        cx = (sx + WM / 2) / WM * W
        # shift pattern decal (right of the wheel) and start label (left)
        gx = cx + 0.25 / WM * W
        d.rounded_rectangle([(gx - 30) * S, (CY0 + 34) * S, (gx + 30) * S, (CY0 + 104) * S], 6 * S, fill=(220, 220, 214))
        for i, (lx, ly) in enumerate(((-14, 46), (-14, 92), (14, 46), (14, 92))):
            d.text(((gx + lx) * S, (CY0 + ly) * S), str(i + 1), font=font(F_HEAVY, 12 * S), fill=(20, 20, 20), anchor="mm")
        d.line([((gx - 14) * S, (CY0 + 54) * S), ((gx - 14) * S, (CY0 + 84) * S)], fill=(20, 20, 20), width=3 * S)
        d.line([((gx + 14) * S, (CY0 + 54) * S), ((gx + 14) * S, (CY0 + 84) * S)], fill=(20, 20, 20), width=3 * S)
        d.line([((gx - 14) * S, (CY0 + 69) * S), ((gx + 14) * S, (CY0 + 69) * S)], fill=(20, 20, 20), width=3 * S)
        bx = cx - 0.24 / WM * W
        d.text((bx * S, (CY0 + 92) * S), "START", font=font(F_COND, 11 * S), fill=(255, 255, 255), anchor="mm")
        d.text((bx * S, (CY0 + 36) * S), "VIEW", font=font(F_COND, 9 * S), fill=(200, 200, 200), anchor="mm")
    # --- kick panels
    KY0 = 416
    kick = vgrad(W * S, 96 * S, [(0, (26, 26, 30)), (1, (12, 12, 14))])
    im.paste(img(kick), (0, KY0 * S))
    d = ImageDraw.Draw(im)
    d.rectangle([0, (KY0 + 6) * S, W * S, (KY0 + 9) * S], fill=P["sideA"])
    im = im.resize((W, H), Image.LANCZOS)
    im = fancy_text(im, P["title"], font(F_HEAVY_IT, 30), W // 2, 252, P["ink"], outlines=[((0, 0, 0), 3)], max_w=160, skew=-0.2)
    a = arr(im)
    a = grime(a, 0.16, 1700 + s, 32)
    pass
    im = img(a)
    im = scuffs(im, 200, 1702 + s, (190, 190, 190), 60, 12, region=(0, 416, W, 512))
    im = scuffs(im, 80, 1703 + s, (200, 200, 200), 40, 16, region=(0, 288, W, 416))
    im = smudges(im, 30, 1704 + s, 12, 16, region=(0, 300, W, 400))
    save(im, "rpanel%d" % s)


def paint_racer_base(s):
    """Seat-base side and rear panels, 256x160 (0.66 x 0.40 m)."""
    P = RACER[s]
    W, H, S = 256, 160, 2
    im = ss_new(W, H, S, P["side"])
    d = ImageDraw.Draw(im)
    d.polygon([(0, 70 * S), (W * S, 30 * S), (W * S, 70 * S), (0, 110 * S)], fill=P["sideA"])
    d.polygon([(0, 116 * S), (W * S, 76 * S), (W * S, 84 * S), (0, 124 * S)], fill=P["sideB"])
    checker_flag(d, 0, 0, W * S, 18 * S, 16, 0.0)
    im = im.resize((W, H), Image.LANCZOS)
    a = grime(arr(im), 0.22, 1800 + s, 24)
    yy = np.linspace(0, 1, H)[:, None, None]
    a = a * (1 - 0.3 * np.clip((yy - 0.75) / 0.25, 0, 1))
    im = scuffs(img(a), 120, 1801 + s, (210, 210, 210), 60, 10)
    save(im, "rbase%d" % s)


# ------------------------------------------------------------------ pinball
PIN = [
    dict(title="NEBULA RUN", c0=(10, 8, 40), c1=(60, 20, 110), c2=(20, 120, 220), acc=(255, 200, 40), ink=(255, 240, 120),
         cab=(18, 16, 60), cabA=(250, 70, 190), cabB=(60, 200, 255), legs="chrome", rail=(170, 172, 178)),
    dict(title="DEEP REEF", c0=(2, 30, 50), c1=(0, 90, 110), c2=(30, 170, 170), acc=(255, 190, 40), ink=(255, 230, 120),
         cab=(4, 60, 80), cabA=(255, 170, 30), cabB=(250, 90, 70), legs="black", rail=(40, 40, 44)),
    dict(title="MAGMA MADNESS", c0=(20, 4, 4), c1=(110, 20, 8), c2=(250, 120, 20), acc=(255, 230, 60), ink=(255, 220, 60),
         cab=(30, 10, 8), cabA=(250, 90, 10), cabB=(255, 220, 50), legs="chrome", rail=(170, 172, 178)),
]
PF_W, PF_L = 0.60, 1.067


def pf_xy(px, pz, W=512, H=1024):
    return ((px + PF_W / 2) / PF_W * W, (1 - pz / PF_L) * H)


def theme_bg(s, W, H, seed):
    P = PIN[s]
    a = vgrad(W, H, [(0, P["c0"]), (0.5, P["c1"]), (1, P["c0"])])
    n = fbm(W, H, 96, seed)
    if s == 0:
        neb = np.clip((n - 0.45) * 3, 0, 1)
        a = a + neb[..., None] * np.array(P["c2"]) / 255 * 0.7
        a = a + np.clip((fbm(W, H, 48, seed + 1) - 0.55) * 4, 0, 1)[..., None] * np.array((220, 60, 180)) / 255 * 0.5
        r = np.random.default_rng(seed + 2)
        for _ in range(W * H // 900):
            x, y = r.integers(0, W), r.integers(0, H)
            a[y, x] = 1.0
    elif s == 1:
        rays = np.clip(np.sin(np.linspace(0, 14, W))[None, :] * 0.5 + 0.5, 0, 1) ** 4
        a = a + rays[..., None] * np.linspace(0.25, 0, H)[:, None, None] * np.array((0.5, 0.9, 0.9))
        a = a * (0.85 + 0.3 * n)[..., None]
    else:
        veins = 1 - np.abs(fbm(W, H, 64, seed + 3) - 0.5) * 2
        lava = np.clip((veins - 0.86) * 9, 0, 1)
        a = a * (0.7 + 0.5 * n)[..., None] * 0.7
        a = a + lava[..., None] * np.array((1.0, 0.55, 0.1))
    return a


def theme_art(d, s, W, H, sc=1.0, focus=(0.5, 0.5)):
    """The theme's big picture elements on ImageDraw d (coordinates in px)."""
    P = PIN[s]
    fx, fy = focus[0] * W, focus[1] * H
    if s == 0:
        # ringed planet, moon, rocket
        R = 120 * sc
        d.ellipse([fx - R, fy - R, fx + R, fy + R], fill=(220, 120, 60))
        d.chord([fx - R, fy - R, fx + R, fy + R], 200, 380, fill=(250, 170, 90))
        d.ellipse([fx - R * 0.5, fy - R * 0.6, fx + R * 0.1, fy - R * 0.2], fill=(250, 200, 140))
        d.arc([fx - R * 1.8, fy - R * 0.35, fx + R * 1.8, fy + R * 0.35], 160, 380, fill=(255, 230, 160), width=int(10 * sc))
        mx, my = fx - 230 * sc, fy - 200 * sc
        d.ellipse([mx - 40 * sc, my - 40 * sc, mx + 40 * sc, my + 40 * sc], fill=(170, 170, 200))
        rx, ry = fx + 200 * sc, fy - 210 * sc
        body = [(rx, ry - 70 * sc), (rx + 22 * sc, ry - 30 * sc), (rx + 22 * sc, ry + 50 * sc), (rx - 22 * sc, ry + 50 * sc), (rx - 22 * sc, ry - 30 * sc)]
        d.polygon(body, fill=(235, 235, 240))
        d.polygon([(rx - 22 * sc, ry + 10 * sc), (rx - 44 * sc, ry + 60 * sc), (rx - 22 * sc, ry + 50 * sc)], fill=(220, 40, 40))
        d.polygon([(rx + 22 * sc, ry + 10 * sc), (rx + 44 * sc, ry + 60 * sc), (rx + 22 * sc, ry + 50 * sc)], fill=(220, 40, 40))
        d.ellipse([rx - 10 * sc, ry - 25 * sc, rx + 10 * sc, ry - 5 * sc], fill=(60, 140, 230))
        d.polygon([(rx - 14 * sc, ry + 50 * sc), (rx, ry + 120 * sc), (rx + 14 * sc, ry + 50 * sc)], fill=(255, 190, 40))
    elif s == 1:
        # treasure chest, coral, fish
        cx, cy = fx, fy + 60 * sc
        d.rectangle([cx - 90 * sc, cy - 40 * sc, cx + 90 * sc, cy + 50 * sc], fill=(120, 70, 30))
        d.chord([cx - 90 * sc, cy - 100 * sc, cx + 90 * sc, cy + 20 * sc], 180, 360, fill=(140, 84, 36))
        d.rectangle([cx - 90 * sc, cy - 44 * sc, cx + 90 * sc, cy - 32 * sc], fill=(210, 170, 60))
        d.rectangle([cx - 12 * sc, cy - 50 * sc, cx + 12 * sc, cy - 10 * sc], fill=(230, 190, 70))
        for k in range(9):
            gx = cx - 70 * sc + k * 17 * sc
            d.ellipse([gx - 9 * sc, cy - 66 * sc, gx + 9 * sc, cy - 48 * sc], fill=(255, 210, 60))
        for k, (x, col) in enumerate(((0.12, (240, 90, 80)), (0.85, (250, 140, 60)), (0.3, (220, 70, 140)))):
            bx, by = x * W, H * 0.98
            for j in range(6):
                a = -math.pi / 2 + (j - 2.5) * 0.35
                L = (90 + 30 * (j % 2)) * sc
                d.line([(bx, by), (bx + math.cos(a) * L, by + math.sin(a) * L)], fill=col, width=int(14 * sc))
        r = np.random.default_rng(31)
        for k in range(10):
            x, y = r.uniform(0.05, 0.95) * W, r.uniform(0.05, 0.6) * H
            L = r.uniform(20, 40) * sc
            col = (255, 200, 40) if k % 2 else (250, 120, 60)
            d.ellipse([x - L, y - L * 0.45, x + L, y + L * 0.45], fill=col)
            d.polygon([(x + L * 0.8, y), (x + L * 1.5, y - L * 0.5), (x + L * 1.5, y + L * 0.5)], fill=col)
            d.ellipse([x - L * 0.7, y - L * 0.15, x - L * 0.45, y + L * 0.1], fill=(10, 10, 10))
    else:
        # volcano with eruption
        bx, by = fx, fy + 140 * sc
        d.polygon([(bx - 260 * sc, by + 60 * sc), (bx - 60 * sc, by - 150 * sc), (bx + 60 * sc, by - 150 * sc), (bx + 260 * sc, by + 60 * sc)], fill=(40, 16, 12))
        d.polygon([(bx - 60 * sc, by - 150 * sc), (bx + 60 * sc, by - 150 * sc), (bx + 30 * sc, by - 120 * sc), (bx - 20 * sc, by - 110 * sc)], fill=(255, 120, 20))
        for k in range(4):
            x0 = bx + (-40 + k * 25) * sc
            d.line([(x0, by - 140 * sc), (x0 + (-60 + 40 * k) * sc, by + 50 * sc)], fill=(255, 110 + k * 25, 20), width=int(9 * sc))
        r = np.random.default_rng(41)
        for k in range(14):
            a = -math.pi / 2 + r.uniform(-0.9, 0.9)
            L = r.uniform(80, 220) * sc
            x, y = bx + math.cos(a) * L, by - 160 * sc + math.sin(a) * L
            rr = r.uniform(6, 16) * sc
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(255, 200 - k * 6, 40))
        # ash plume: overlapping puffs, lit orange from below
        r2 = np.random.default_rng(43)
        for k in range(16):
            t = k / 15.0
            px = bx + r2.uniform(-70, 70) * sc * (0.4 + t)
            py = by - (180 + 190 * t) * sc
            rr = (34 + 40 * t) * sc * r2.uniform(0.8, 1.2)
            d.ellipse([px - rr, py - rr * 0.8, px + rr, py + rr * 0.8], fill=(int(150 - 90 * t), int(60 - 30 * t), int(30 - 10 * t)))
            d.ellipse([px - rr * 0.8, py - rr * 0.85, px + rr * 0.7, py + rr * 0.3], fill=(int(70 - 30 * t), int(44 - 20 * t), int(40 - 16 * t)))


def paint_pf(s):
    """Playfield 512x1024 (0.60 x 1.067 m). Must match driver.gd's layout."""
    P = PIN[s]
    W, H = 512, 1024
    a = theme_bg(s, W, H, 2000 + s * 10)
    im = img(a)
    d = ImageDraw.Draw(im)
    theme_art(d, s, W, H, 0.85, (0.45, 0.44))
    X = lambda px, pz: pf_xy(px, pz, W, H)
    # dark zones around flippers / slings / lanes (the lower third is busy)
    lo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lo)
    dl.polygon([X(-0.30, 0.0), X(0.253, 0.0), X(0.253, 0.42), X(-0.30, 0.42)], fill=(0, 0, 0, 120))
    im = Image.alpha_composite(im.convert("RGBA"), lo).convert("RGB")
    d = ImageDraw.Draw(im)
    # shooter lane
    d.polygon([X(0.253, 0), X(0.30, 0), X(0.30, 0.94), X(0.253, 0.94)], fill=(18, 18, 22))
    d.line([X(0.2765, 0.05), X(0.2765, 0.9)], fill=(40, 40, 46), width=2)
    # the top arch (painted border)
    cx0, R = X(-0.0235, 0)[0], (0.30 - 0.0235) / PF_W * W + 4
    d.arc([X(-0.30, 1.067)[0], X(0, 1.067)[1] - 20, X(0.30, 1.067)[0], X(0, 1.067 - 0.55)[1]], 180, 360, fill=P["acc"], width=4)
    # inlane / outlane art
    for x in (-0.245, -0.205, 0.158, 0.198):
        d.line([X(x, 0.22), X(x, 0.40)], fill=(230, 230, 230), width=3)
    for x0, z0, x1, z1 in ((-0.205, 0.29, -0.14, 0.235), (0.158, 0.29, 0.093, 0.235)):
        d.line([X(x0, z0), X(x1, z1)], fill=(230, 230, 230), width=3)
    for x, lab in ((-0.2725, "SPECIAL"), (-0.225, "LITE"), (0.178, "LITE"), (0.2255, "SPECIAL")):
        px, py = X(x, 0.31)
        tl = Image.new("L", (90, 18), 0)
        ImageDraw.Draw(tl).text((45, 9), lab, font=font(F_COND, 13), fill=255, anchor="mm")
        tl = tl.rotate(90, expand=True)
        im.paste(Image.new("RGB", tl.size, (255, 255, 255)), (int(px - 9), int(py - 45)), tl)
    d = ImageDraw.Draw(im)
    # lane rollover inserts
    def ins_circle(px, pz, r, col, lab=None, fs=11):
        x, y = X(px, pz)
        d.ellipse([x - r - 3, y - r - 3, x + r + 3, y + r + 3], fill=(10, 10, 10))
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)
        d.ellipse([x - r * 0.5, y - r * 0.6, x + r * 0.2, y - r * 0.1], fill=tuple(min(255, c + 70) for c in col))
        if lab:
            d.text((x, y + r + 9), lab, font=font(F_COND, fs), fill=(255, 255, 255), anchor="mm")

    def ins_arrow(px, pz, ang, L, col, lab=None):
        x, y = X(px, pz)
        ca, sa = math.cos(ang), math.sin(ang)
        pts0 = [(0, -L), (L * 0.5, -L * 0.2), (L * 0.22, -L * 0.2), (L * 0.22, L * 0.5), (-L * 0.22, L * 0.5), (-L * 0.22, -L * 0.2), (-L * 0.5, -L * 0.2)]
        pts = [(x + px_ * ca - py_ * sa, y + px_ * sa + py_ * ca) for px_, py_ in pts0]
        d.polygon(pts, fill=(8, 8, 8))
        pts_in = [(x + (px_ * 0.8) * ca - (py_ * 0.8) * sa, y + (px_ * 0.8) * sa + (py_ * 0.8) * ca) for px_, py_ in pts0]
        d.polygon(pts_in, fill=col)
        if lab:
            d.text((x - L * 0.9 * sa, y + L * 0.95 * ca), lab, font=font(F_COND, 10), fill=(255, 255, 255), anchor="mm")
    for x in (-0.2725, -0.225, 0.178, 0.2255):
        ins_circle(x, 0.36, 8, (255, 240, 200))
    # shoot again
    ins_circle(-0.0235, 0.085, 14, (255, 60, 40))
    x, y = X(-0.0235, 0.04)
    d.text((x, y), "SHOOT AGAIN", font=font(F_COND, 12), fill=(255, 255, 255), anchor="mm")
    # bonus multiplier arc
    for i, lab in enumerate(("2X", "3X", "4X", "5X")):
        ang = math.radians(-50 + i * 33)
        ins_circle(-0.0235 + math.sin(ang) * 0.085, 0.27 + math.cos(ang) * 0.06 - 0.02, 9, P["acc"], lab, 10)
    # centre arrows toward ramp, orbit and targets
    ins_arrow(-0.13, 0.45, math.radians(-14), 34, (255, 60, 40), None)
    ins_arrow(-0.075, 0.46, math.radians(-6), 30, (255, 210, 40), None)
    ins_arrow(0.02, 0.47, math.radians(10), 30, (60, 150, 255), None)
    ins_arrow(0.09, 0.45, math.radians(28), 34, (60, 220, 90), None)
    x, y = X(-0.03, 0.39)
    d.text((x, y), "JACKPOT", font=font(F_HEAVY, 16), fill=P["ink"], anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0))
    # small insert rows
    for i in range(5):
        ins_circle(-0.17 + i * 0.035, 0.585, 7, (255, 140, 30) if i % 2 else (255, 240, 200))
    x, y = X(-0.10, 0.62)
    d.text((x, y), "EXTRA BALL", font=font(F_COND, 11), fill=(255, 255, 255), anchor="mm")
    for i, lab in enumerate(("LOCK", "BONUS", "MULTIBALL")):
        ins_arrow(0.17, 0.48 + i * 0.06, math.radians(-78), 20, (255, 210, 40), None)
    # bumper rings and top lanes
    for bx, bz in ((-0.11, 0.80), (0.05, 0.82), (-0.03, 0.705)):
        x, y = X(bx, bz)
        r = 0.052 / PF_W * W
        d.ellipse([x - r, y - r, x + r, y + r], outline=P["acc"], width=3)
    for i, x in enumerate((-0.11, -0.03, 0.05)):
        ins_circle(x, 0.955, 8, (255, 240, 200))
        xx, yy = X(x, 0.995)
        d.text((xx, yy), "ABC"[i], font=font(F_HEAVY, 14), fill=(255, 255, 255), anchor="mm")
    # title on the playfield
    tx, ty = X(-0.035, 0.66)
    im = fancy_text(im, P["title"], font(F_HEAVY_IT, 40), int(tx), int(ty), P["ink"], outlines=[((0, 0, 0), 3)], max_w=250, skew=-0.2)
    a = arr(im)
    # clear-coat wear: ball trails and flipper-area wear
    yy, xx = np.mgrid[0:H, 0:W]
    trail = np.zeros((H, W), np.float32)
    for x0, x1 in ((0.0, -0.2), (-0.05, 0.2), (-0.02, -0.03)):
        cx_ = (np.interp(yy / H, [0.3, 1.0], [x1, x0]) + PF_W / 2) / PF_W * W
        trail += np.exp(-((xx - cx_) / 26.0) ** 2) * np.clip((yy / H - 0.3) / 0.7, 0, 1)
    a = a * (1 - 0.10 * np.clip(trail, 0, 1)[..., None] * fbm(W, H, 8, 2100 + s)[..., None])
    a = grime(a, 0.1, 2101 + s, 64)
    save(img(a), "pfield%d" % s)


def paint_translight(s):
    """Backbox translight, 512x416 (0.54 x 0.44 m)."""
    P = PIN[s]
    W, H, S = 512, 416, 2
    a = theme_bg(s, W * S, H * S, 2200 + s)
    im = img(a)
    d = ImageDraw.Draw(im)
    theme_art(d, s, W * S, H * S, 1.25 * S / 2 * 1.2, (0.5, 0.62))
    # border
    d.rectangle([0, 0, W * S - 1, H * S - 1], outline=P["acc"], width=10 * S)
    d.rectangle([14 * S, 14 * S, W * S - 15 * S, H * S - 15 * S], outline=(0, 0, 0), width=3 * S)
    im = im.resize((W, H), Image.LANCZOS)
    if s == 0:
        fill = [(0, (255, 255, 255)), (0.5, (120, 220, 255)), (0.55, (40, 80, 200)), (1, (200, 240, 255))]
        outl = [((0, 0, 0), 9), ((250, 70, 190), 6), ((255, 255, 255), 2)]
    elif s == 1:
        fill = [(0, (255, 255, 220)), (0.5, (255, 210, 60)), (0.55, (200, 120, 10)), (1, (255, 230, 120))]
        outl = [((0, 0, 0), 9), ((0, 110, 140), 6), ((255, 255, 255), 2)]
    else:
        fill = [(0, (255, 255, 200)), (0.45, (255, 220, 40)), (0.6, (240, 80, 10)), (1, (255, 180, 40))]
        outl = [((0, 0, 0), 9), ((140, 10, 0), 6), ((255, 240, 200), 2)]
    im = fancy_text(im, P["title"], font(F_HEAVY_IT, 74), W // 2, 78, fill, outlines=outl, shadow=(5, 6, (0, 0, 0)), max_w=440, skew=-0.18)
    a = arr(im)
    a = grime(a, 0.08, 2210 + s, 48)
    # a lamp hot-spot behind the centre (fluorescent backlight unevenness)
    yy, xx = np.mgrid[0:H, 0:W]
    a = a * (0.85 + 0.2 * np.exp(-(((xx - W / 2) / (W * 0.5)) ** 2 + ((yy - H * 0.45) / (H * 0.6)) ** 2)))[..., None]
    save(img(a), "ptrans%d" % s)


def dmd_lines(s):
    return [("NEBULA RUN", "PLAYER 1   2,450,180"), ("DEEP REEF", "FIND THE TREASURE"), ("MAGMA MADNESS", "1 CREDIT  PRESS START")][s]


def paint_dmd(s):
    """Orange 128x32 dot-matrix display, 4 px per dot -> 512x128; 4 shades."""
    t1, t2 = dmd_lines(s)
    m = Image.new("L", (128, 32), 0)
    d = ImageDraw.Draw(m)
    f1 = font(F_HEAVY, 15)
    bb = d.textbbox((0, 0), t1, font=f1)
    if bb[2] - bb[0] > 124:
        f1 = font(F_HEAVY, int(15 * 124 / (bb[2] - bb[0])))
    d.text((64, 9), t1, font=f1, fill=255, anchor="mm")
    f2 = font(F_COND, 9)
    d.text((64, 25), t2, font=f2, fill=200, anchor="mm")
    v = np.asarray(m, np.float32) / 255.0
    v = np.round(v * 3) / 3  # 4 brightness levels like the real panels
    W, H = 512, 128
    out = np.zeros((H, W, 3), np.float32)
    dot = np.zeros((4, 4), np.float32)
    for y in range(4):
        for x in range(4):
            r = math.hypot(x - 1.5, y - 1.5)
            dot[y, x] = np.clip(1.6 - r * 0.75, 0, 1)
    lit = np.kron(v, dot)
    off = np.kron(np.ones_like(v), dot) * 0.06  # unlit dots faintly visible
    lev = np.maximum(lit, off)
    col = np.array([1.0, 0.45, 0.06])
    out = lev[..., None] * col
    save(img(out), "pdmd%d" % s)


def paint_pside(s):
    """Cabinet side art 512x256 over the side (z 0..1.30 m, y 1.07..0.53);
    u = 0 at the front, v = 0 at the top of the back."""
    P = PIN[s]
    W, H, S = 512, 256, 2
    a = vgrad(W * S, H * S, [(0, P["cab"]), (1, tuple(int(c * 0.6) for c in P["cab"]))])
    im = img(a)
    d = ImageDraw.Draw(im)
    # sweeping bands
    d.polygon([(0, 150 * S), (W * S, 40 * S), (W * S, 90 * S), (0, 210 * S)], fill=P["cabA"])
    d.polygon([(0, 216 * S), (W * S, 96 * S), (W * S, 108 * S), (0, 228 * S)], fill=P["cabB"])
    theme_art(d, s, W * S, H * S, 0.55 * S / 2 * 1.3, (0.72, 0.42))
    im = im.resize((W, H), Image.LANCZOS)
    im = fancy_text(im, P["title"], font(F_HEAVY_IT, 40), 170, 120, P["ink"], outlines=[((0, 0, 0), 4)], max_w=280, skew=-0.2)
    a = arr(im)
    a = grime(a, 0.2, 2300 + s, 40)
    # leg-bolt plates and wear at the bottom and front edge
    yy, xx = np.mgrid[0:H, 0:W]
    a = a * (1 - 0.2 * np.clip((yy / H - 0.8) / 0.2, 0, 1))[..., None]
    im = img(a)
    d = ImageDraw.Draw(im)
    for x in (18, W - 30):
        d.rectangle([x, H - 66, x + 14, H - 2], fill=(150, 150, 154) if P["legs"] == "chrome" else (24, 24, 26))
    im = scuffs(im, 120, 2301 + s, (220, 220, 220), 55, 10)
    save(im, "pside%d" % s)


def paint_pbox(s):
    """512x128: x 0..128 backbox side art (0.23 x 0.80 m), x 128..512 the
    speaker panel (0.58 x 0.22 m) with grilles and the DMD window (black)."""
    P = PIN[s]
    W, H, S = 512, 128, 2
    im = ss_new(W, H, S, P["cab"])
    d = ImageDraw.Draw(im)
    # side: two vertical bands
    d.rectangle([20 * S, 0, 44 * S, H * S], fill=P["cabA"])
    d.rectangle([52 * S, 0, 60 * S, H * S], fill=P["cabB"])
    # speaker panel
    x0 = 128
    sp = vgrad((W - x0) * S, H * S, [(0, (30, 30, 34)), (1, (14, 14, 16))])
    im.paste(img(sp), (x0 * S, 0))
    d = ImageDraw.Draw(im)
    PW = 0.58
    def PX(u):
        return (x0 + (u + PW / 2) / PW * (W - x0)) * S
    for sx in (-0.228, 0.228):
        cx, cy, r = PX(sx), H / 2 * S, 34 * S
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(60, 60, 64))
        d.ellipse([cx - r + 4 * S, cy - r + 4 * S, cx + r - 4 * S, cy + r - 4 * S], fill=(10, 10, 12))
        for yy in range(int(cy - r + 8 * S), int(cy + r - 6 * S), 6 * S):
            for xx in range(int(cx - r + 8 * S), int(cx + r - 6 * S), 6 * S):
                if (xx - cx) ** 2 + (yy - cy) ** 2 < (r - 8 * S) ** 2:
                    d.ellipse([xx - 1.6 * S, yy - 1.6 * S, xx + 1.6 * S, yy + 1.6 * S], fill=(40, 40, 44))
    # DMD window frame (the dots are a separate emissive quad behind)
    dw, dh = 0.34, 0.088
    d.rectangle([PX(-dw / 2) - 6 * S, (H / 2 - dh / 0.22 * H / 2) * S - 6 * S, PX(dw / 2) + 6 * S, (H / 2 + dh / 0.22 * H / 2) * S + 6 * S], fill=P["acc"])
    d.rectangle([PX(-dw / 2), (H / 2 - dh / 0.22 * H / 2) * S, PX(dw / 2), (H / 2 + dh / 0.22 * H / 2) * S], fill=(0, 0, 0))
    im = im.resize((W, H), Image.LANCZOS)
    a = grime(arr(im), 0.15, 2400 + s, 24)
    im = scuffs(img(a), 60, 2401 + s, (200, 200, 200), 50, 14)
    save(im, "pbox%d" % s)


def main():
    os.makedirs(OUT, exist_ok=True)
    paint_coin(); paint_vinyl(); paint_grille(); paint_lam(); paint_steel(); paint_tmold()
    paint_diamond(); paint_glass(); paint_apron(); paint_inserts()
    for s in range(2):
        paint_racer_marquee(s); paint_racer_screen(s); paint_racer_side(s); paint_racer_panel(s); paint_racer_base(s)
    for s in range(3):
        paint_pf(s); paint_translight(s); paint_dmd(s); paint_pside(s); paint_pbox(s)
    tot = 0
    for k in sorted(SIZES):
        tot += SIZES[k]
        print("%-10s %7.1f KB" % (k, SIZES[k] / 1024))
    print("total %.1f KB" % (tot / 1024))


if __name__ == "__main__":
    main()
