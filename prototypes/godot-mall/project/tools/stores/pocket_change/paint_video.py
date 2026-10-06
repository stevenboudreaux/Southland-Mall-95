#!/usr/bin/env python3
"""Paints every texture of the Pocket Change video cabinets (tools/stores/pocket_change/video.gd)
into tex/pc/video_*.png. Deterministic: all randomness is seeded.

Atlases (cell index = style index 0..7, layout must match video.gd):
  video_sides.png     1024x1024  4x2 cells of 256x512   side art over the profile (z -> u, y -> v)
  video_panels.png    1024x1024  2x4 cells of 512x256   control panel overlay: top 512x192, front 512x64
  video_bezels.png    1024x512   4x2 cells of 256x256   monitor bezel (black card, printed text)
  video_marquees.png  1024x1024  2x6 cells of 512x170   backlit marquee
  video_screens.png   1024x768   3x3 cells of 341x256   CRT picture (336x251 at +2,+2)
Shared: video_lam.png (body laminate, tinted), video_tmold.png, video_kick.png, video_door.png,
video_entry.png / video_entry_e.png (coin entry and its lit reject button), video_speaker.png,
video_glass.png (fingerprints, alpha), video_scan.png (scanline overlay).

All game titles, artwork and characters are invented. Run: python3 paint_video.py
"""
import json
import math
import os
import re

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "tex", "pc")

FD = "/usr/share/fonts/truetype/dejavu/"
FONTS = {
    "sans": FD + "DejaVuSans-Bold.ttf",
    "cond": FD + "DejaVuSansCondensed-Bold.ttf",
    "condo": FD + "DejaVuSansCondensed-BoldOblique.ttf",
    "serif": FD + "DejaVuSerif-Bold.ttf",
    "serifc": FD + "DejaVuSerifCondensed-Bold.ttf",
    "mono": FD + "DejaVuSansMono-Bold.ttf",
    "lib": FD + "LiberationSans-Bold.ttf",
    "libi": FD + "LiberationSans-BoldItalic.ttf",
    "pop": "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
    "popi": "/usr/share/fonts/truetype/google-fonts/Poppins-BoldItalic.ttf",
    "black": "/usr/share/fonts/opentype/inter/Inter-Black.otf",
    "blacki": "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf",
}
_fc = {}


def font(name, size):
    k = (name, int(size))
    if k not in _fc:
        _fc[k] = ImageFont.truetype(FONTS[name], int(size))
    return _fc[k]


def fit(name, txt, maxw, size):
    """The largest font size <= size whose text fits maxw pixels."""
    d = ImageDraw.Draw(Image.new("L", (8, 8)))
    while size > 8 and d.textlength(txt, font=font(name, size)) > maxw:
        size -= 2
    return font(name, size)


def load_styles():
    src = open(os.path.join(HERE, "video.gd")).read()
    m = re.search(r"# --- STYLES ---\s*const STYLES = (.*?)# --- end STYLES ---", src, re.S)
    return json.loads(m.group(1))


STY = load_styles()
T = 0.019


def rgb(h, a=None):
    h = h.lstrip("#")
    c = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    return c if a is None else c + (a,)


# ------------------------------------------------------------------ helpers
def rng(seed):
    return np.random.default_rng(seed)


def vnoise(w, h, cell, seed, tile=False):
    """Smooth value noise in 0..1 (bicubic upsampled random grid)."""
    r = rng(seed)
    gw, gh = max(2, w // cell + 3), max(2, h // cell + 3)
    g = r.random((gh, gw)).astype(np.float32)
    if tile:
        gw, gh = max(2, w // cell), max(2, h // cell)
        g = r.random((gh, gw)).astype(np.float32)
        g = np.tile(g, (3, 3))
        im = Image.fromarray((g * 255).astype(np.uint8)).resize((w * 3, h * 3), Image.BICUBIC)
        a = np.asarray(im, np.float32)[h:2 * h, w:2 * w] / 255.0
        return a
    im = Image.fromarray((g * 255).astype(np.uint8)).resize((gw * cell, gh * cell), Image.BICUBIC)
    a = np.asarray(im, np.float32)[cell:cell + h, cell:cell + w] / 255.0
    return a


def fbm(w, h, seed, cells=(64, 24, 8), amps=(0.55, 0.3, 0.15), tile=False):
    a = np.zeros((h, w), np.float32)
    for i, (c, k) in enumerate(zip(cells, amps)):
        a += vnoise(w, h, c, seed + i * 17, tile) * k
    return a


def to_arr(im):
    return np.asarray(im.convert("RGB"), np.float32) / 255.0


def to_img(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))


def vgrad(w, h, stops):
    """Vertical gradient; stops = [(pos 0..1, (r,g,b)), ...]."""
    ys = np.linspace(0, 1, h)
    out = np.zeros((h, w, 3), np.float32)
    ps = [s[0] for s in stops]
    for c in range(3):
        col = np.interp(ys, ps, [s[1][c] / 255.0 for s in stops])
        out[:, :, c] = col[:, None]
    return out


def radial(w, h, cx, cy, r):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    return np.clip(1.0 - np.hypot(xx - cx, yy - cy) / r, 0, 1)


def text_mask(size, xy, txt, f, anchor="mm", stroke=0):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).text(xy, txt, font=f, fill=255, anchor=anchor, stroke_width=stroke, stroke_fill=255)
    return m


def comp(base, color, mask):
    """Paint a solid colour (or an RGB image) through an L mask onto base (RGB image)."""
    if isinstance(color, tuple):
        layer = Image.new("RGB", base.size, color[:3])
    else:
        layer = color
    return Image.composite(layer, base, mask)


def fancy_text(img, xy, txt, f, fill_top, fill_bot, stroke_col=(0, 0, 0), stroke=4, glow=None, glow_r=8,
               shadow=None, anchor="mm", skew=0.0, inner=None):
    """Gradient-filled title with outline, optional drop shadow, outer glow and inner highlight."""
    W, H = img.size
    m = text_mask((W, H), xy, txt, f, anchor)
    ms = text_mask((W, H), xy, txt, f, anchor, stroke)
    if skew:
        mat = (1, skew, -skew * xy[1], 0, 1, 0)
        m = m.transform((W, H), Image.AFFINE, mat, Image.BICUBIC)
        ms = ms.transform((W, H), Image.AFFINE, mat, Image.BICUBIC)
    bb = ms.getbbox() or (0, 0, W, H)
    if glow:
        gm = ms.filter(ImageFilter.GaussianBlur(glow_r))
        g = to_arr(img) + np.asarray(gm, np.float32)[:, :, None] / 255.0 * np.array(glow, np.float32)[None, None, :] / 255.0 * 1.4
        img = to_img(g)
    if shadow:
        sh = ms.transform((W, H), Image.AFFINE, (1, 0, -shadow[0], 0, 1, -shadow[1]))
        img = comp(img, (0, 0, 0), sh)
    img = comp(img, stroke_col, ms)
    gr = to_img(vgrad(W, max(1, bb[3] - bb[1]), [(0, fill_top), (1, fill_bot)]))
    full = Image.new("RGB", (W, H))
    full.paste(gr, (0, bb[1]))
    img = comp(img, full, m)
    if inner:
        # a thin bright band across the upper third of the letters (chrome / gloss)
        band = Image.new("L", (W, H), 0)
        hh = bb[3] - bb[1]
        ImageDraw.Draw(band).rectangle([0, bb[1] + int(hh * 0.30), W, bb[1] + int(hh * 0.42)], fill=int(inner[3]) if len(inner) > 3 else 150)
        band = ImageChops.multiply(band, m)
        img = comp(img, inner[:3], band)
    return img


def save(img, name, colors=None):
    path = os.path.join(OUT, name)
    if colors:
        img = img.convert("RGB").quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
    img.save(path, optimize=True)
    return path


def ss(w, h, k=2, col=(0, 0, 0), mode="RGB"):
    return Image.new(mode, (w * k, h * k), col)


def down(img, w, h):
    return img.resize((w, h), Image.LANCZOS)


def poly(d, pts, fill, ox=0, oy=0, k=1.0, outline=None, width=1):
    d.polygon([(ox + x * k, oy + y * k) for x, y in pts], fill=fill, outline=outline, width=width)


def star_pts(cx, cy, r0, r1, n, rot=-90):
    p = []
    for i in range(n * 2):
        r = r0 if i % 2 == 0 else r1
        a = math.radians(rot + i * 180.0 / n)
        p.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return p


def bolt_pts(x, y, s):
    return [(x + px * s, y + py * s) for px, py in
            [(0, 0), (14, 0), (6, 22), (16, 22), (-4, 58), (2, 30), (-8, 30)]]


# ------------------------------------------------------------- profile math
def chain(s):
    c = [(s["kz"], 0.0, "kick"), (s["kz"], s["kh"], "lower"), (s["kz"], s["lo"], "hid"),
         (s["cp"][2], s["cp"][3], "bezel"), (s["bz"][0], s["bz"][1], "speaker")]
    if s["flare"] > 0:
        c += [(s["mq"][0], s["mq"][1], "hid"), (s["D"], s["mq"][1], "back")]
    else:
        c += [(s["mq"][0], s["mq"][1], "marquee"), (s["mq"][2], s["mq"][3], "cap"),
              (s["top"][0], s["top"][1], "top"), (s["D"], s["H"], "back")]
    c.append((s["D"], 0.0, "end"))
    return c


def panel_dims(s):
    tf = s["cp"][1]
    d = s["cp"][2] + 0.012
    tb = s["cp"][3] + 0.006
    return s["W"] + 0.010, math.hypot(d, tb - tf)


def bezel_len(s):
    return math.hypot(s["bz"][0] - s["cp"][2], s["bz"][1] - s["cp"][3])


# =================================================================== shared
def paint_lam():
    """Body laminate, grey ~0.4 so the tint (body colour / 0.4) can show lighter abrasion."""
    w = h = 256
    n = fbm(w, h, 11, (64, 16, 4), (0.5, 0.3, 0.2), tile=True)
    base = 0.40 + (n - 0.5) * 0.05
    r = rng(12)
    base += (r.random((h, w)).astype(np.float32) - 0.5) * 0.025
    img = to_img(np.dstack([base] * 3))
    d = ImageDraw.Draw(img)
    for i in range(14):
        x, y = r.integers(0, w), r.integers(0, h)
        L = r.integers(6, 30)
        a = r.uniform(-0.5, 0.5) + (0 if r.random() < 0.7 else 1.57)
        v = int(r.integers(112, 126))
        for ox in (-w, 0, w):
            for oy in (-h, 0, h):
                d.line([(x + ox, y + oy), (x + ox + L * math.cos(a), y + oy + L * math.sin(a))], fill=(v, v, v), width=1)
    for i in range(6):
        x, y = r.integers(0, w), r.integers(0, h)
        rr = r.integers(6, 16)
        v = int(r.integers(94, 100))
        for ox in (-w, 0, w):
            for oy in (-h, 0, h):
                d.ellipse([x + ox - rr, y + oy - rr * 0.6, x + ox + rr, y + oy + rr * 0.6], fill=(v, v, v))
    img = img.filter(ImageFilter.GaussianBlur(1.0))
    save(img, "video_lam.png")


def paint_tmold():
    w, h = 32, 256
    u = np.linspace(0, 1, w)
    prof = 0.34 + 0.10 * np.sin(np.clip((u - 0.2) / 0.6, 0, 1) * math.pi)
    prof[(u > 0.47) & (u < 0.53)] -= 0.05
    a = np.tile(prof[None, :], (h, 1)).astype(np.float32)
    r = rng(21)
    a += (vnoise(w, h, 8, 22, tile=True) - 0.5) * 0.04
    img = to_img(np.dstack([a] * 3))
    d = ImageDraw.Draw(img)
    for i in range(14):
        y = int(r.integers(0, h))
        L = int(r.integers(2, 10))
        v = int(r.integers(140, 200))
        x0 = int(r.integers(4, 20))
        d.rectangle([x0, y, x0 + int(r.integers(2, 10)), y + L], fill=(v, v, v))
    save(img, "video_tmold.png")


def paint_kick():
    w, h = 384, 64
    n = fbm(w, h, 31, (48, 12, 3), (0.4, 0.35, 0.25))
    a = 0.07 + (n - 0.5) * 0.03
    img = to_img(np.dstack([a, a, a * 1.04]))
    d = ImageDraw.Draw(img)
    r = rng(32)
    # shoe scuffs: grey smears concentrated at the bottom middle, rubber marks darker
    for i in range(160):
        x = r.normal(w * 0.5, w * 0.22)
        y = r.uniform(h * 0.25, h - 2)
        L = r.uniform(4, 34)
        v = int(r.integers(50, 120))
        d.line([(x, y), (x + L, y + r.uniform(-3, 3))], fill=(v, v, v + 4), width=int(r.integers(1, 3)))
    for i in range(30):
        x = r.normal(w * 0.5, w * 0.2)
        y = r.uniform(h * 0.3, h - 4)
        d.ellipse([x - 9, y - 3, x + 9, y + 3], fill=(14, 14, 15))
    img = img.filter(ImageFilter.GaussianBlur(0.5))
    d = ImageDraw.Draw(img)
    for x in (10, w - 10):
        for y in (9, h - 9):
            d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(120, 120, 124))
            d.line([(x - 3, y), (x + 3, y)], fill=(40, 40, 40), width=1)
    d.line([(0, 1), (w, 1)], fill=(150, 150, 154), width=2)
    save(img, "video_kick.png")


def paint_door():
    w, h = 256, 352
    n = fbm(w, h, 41, (40, 10, 3), (0.4, 0.35, 0.25))
    a = 0.075 + (n - 0.5) * 0.035
    img = to_img(np.dstack([a, a, a * 1.05]))
    d = ImageDraw.Draw(img)
    # pressed border and a highlight on the top edge
    d.rectangle([3, 3, w - 4, h - 4], outline=(46, 46, 50), width=2)
    d.rectangle([0, 0, w - 1, h - 1], outline=(10, 10, 12), width=3)
    d.line([(3, 3), (w - 4, 3)], fill=(90, 90, 96), width=1)
    pxm = w / 0.30
    for ex in (-0.062, 0.062):
        cx = w / 2 + ex * pxm
        cy = 0.105 * h / 0.41
        d.rectangle([cx - 30, cy - 52, cx + 30, cy + 52], fill=(6, 6, 7))
    # sticker between the entries
    y = 0.105 * h / 0.41
    d.rectangle([w / 2 - 19, y - 36, w / 2 + 19, y + 36], fill=(232, 196, 44))
    d.rectangle([w / 2 - 17, y - 34, w / 2 + 17, y + 34], outline=(170, 30, 30), width=2)
    for i, t in enumerate(["1", "TOKEN", "PER", "PLAY"]):
        f = font("cond", 22 if i == 0 else 9)
        d.text((w / 2, y - 22 + i * 15 + (0 if i else -2)), t, font=f, fill=(150, 20, 20), anchor="mm")
    # lock
    lx, ly = w / 2, h * 0.55
    d.ellipse([lx - 15, ly - 15, lx + 15, ly + 15], fill=(150, 150, 156))
    d.ellipse([lx - 11, ly - 11, lx + 11, ly + 11], fill=(196, 196, 200))
    d.rectangle([lx - 2, ly - 8, lx + 2, ly + 8], fill=(30, 30, 30))
    # arcade sticker under the lock
    d.rectangle([w / 2 - 70, h * 0.63, w / 2 + 70, h * 0.71], fill=(236, 232, 220))
    d.text((w / 2, h * 0.655), "TOKENS ONLY - NO QUARTERS", font=font("cond", 10), fill=(30, 30, 30), anchor="mm")
    d.text((w / 2, h * 0.69), "PROBLEMS? SEE ATTENDANT", font=font("cond", 9), fill=(170, 30, 30), anchor="mm")
    # coin return cups
    for ex in (-0.062, 0.062):
        cx = w / 2 + ex * pxm
        cy = h * 0.83
        d.rectangle([cx - 30, cy - 20, cx + 30, cy + 20], fill=(150, 150, 156))
        d.rectangle([cx - 24, cy - 13, cx + 24, cy + 15], fill=(8, 8, 8))
        d.line([(cx - 30, cy - 20), (cx + 30, cy - 20)], fill=(210, 210, 214), width=2)
        d.text((cx, cy + 28), "COIN RETURN", font=font("cond", 8), fill=(170, 170, 170), anchor="mm")
    # wear: scratches around the lock, faded sticker, fingerprints
    r = rng(42)
    for i in range(60):
        a = r.uniform(0, 6.28)
        rr = r.uniform(16, 40)
        x0 = lx + math.cos(a) * rr
        y0 = ly + math.sin(a) * rr
        d.line([(x0, y0), (x0 + r.uniform(-12, 12), y0 + r.uniform(-12, 12))], fill=(int(r.integers(70, 130)),) * 3, width=1)
    for i in range(80):
        x, y = r.uniform(0, w), r.uniform(0, h)
        L = r.uniform(3, 20)
        v = int(r.integers(40, 80))
        d.line([(x, y), (x + L, y + r.uniform(-4, 4))], fill=(v, v, v), width=1)
    img = img.filter(ImageFilter.GaussianBlur(0.4))
    save(img, "video_door.png")


def paint_entry():
    w, h = 64, 128
    x = np.linspace(0, 1, w)
    a = 0.55 + 0.25 * np.sin(x * math.pi) + (rng(51).random((h, w)) - 0.5) * 0.05
    img = to_img(np.dstack([a, a, a * 1.02]))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, h - 1], outline=(90, 90, 96), width=2)
    d.rounded_rectangle([18, 10, 46, 52], radius=6, fill=(70, 70, 74))
    d.rectangle([29, 14, 35, 48], fill=(5, 5, 5))          # coin slot
    d.rectangle([12, 62, 52, 112], fill=(40, 10, 6))        # reject button housing
    em = Image.new("RGB", (w, h), (0, 0, 0))
    de = ImageDraw.Draw(em)
    for dd, (c, t) in ((d, ((255, 120, 40), (90, 20, 10))), (de, ((255, 110, 30), (60, 10, 0)))):
        dd.rectangle([14, 64, 50, 110], fill=c)
        dd.text((32, 80), "TOKEN", font=font("cond", 10), fill=t, anchor="mm")
        dd.text((32, 96), "PUSH", font=font("cond", 8), fill=t, anchor="mm")
    em = em.filter(ImageFilter.GaussianBlur(0.8))
    save(img, "video_entry.png")
    save(em, "video_entry_e.png")


def paint_speaker():
    w, h = 256, 64
    n = fbm(w, h, 61, (32, 8, 2), (0.4, 0.35, 0.25))
    a = 0.06 + (n - 0.5) * 0.02
    img = to_img(np.dstack([a] * 3))
    d = ImageDraw.Draw(img)
    for cx in (w * 0.18, w * 0.82):
        d.ellipse([cx - 34, 6, cx + 34, h - 6], fill=(22, 22, 24), outline=(55, 55, 58), width=2)
        for yy in range(10, h - 8, 4):
            for xx in range(int(cx - 30), int(cx + 31), 4):
                if ((xx - cx) / 30.0) ** 2 + ((yy - h / 2) / (h / 2 - 9)) ** 2 < 1:
                    d.point((xx, yy), fill=(4, 4, 4))
    save(img, "video_speaker.png")


def paint_glass():
    w = h = 256
    r = rng(71)
    a = np.full((h, w), 0.035, np.float32)
    # dust haze toward the bottom
    a += np.linspace(0, 0.03, h)[:, None]
    # fingerprints: clusters of small concentric ovals, mostly low and at the sides
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    for i in range(26):
        cx = r.choice([r.uniform(10, 70), r.uniform(186, 246), r.uniform(60, 196)])
        cy = r.uniform(120, 250) if r.random() < 0.7 else r.uniform(20, 120)
        rr = r.uniform(4, 8)
        for k in range(5):
            d.ellipse([cx - rr + k, cy - rr * 1.3 + k, cx + rr - k, cy + rr * 1.3 - k], outline=int(r.integers(14, 34)))
    # a wiped arc
    d.arc([30, 40, 230, 300], 200, 330, fill=26, width=8)
    m = m.filter(ImageFilter.GaussianBlur(1.6))
    a += np.asarray(m, np.float32) / 255.0 * 0.35
    a += (r.random((h, w)).astype(np.float32) > 0.997) * 0.4
    rgba = np.dstack([np.full((h, w), 0.86)] * 3 + [np.clip(a, 0, 1)])
    Image.fromarray((rgba * 255).astype(np.uint8), "RGBA").save(os.path.join(OUT, "video_glass.png"), optimize=True)


def paint_scan():
    a = np.zeros((4, 4, 4), np.uint8)
    a[2, :, 3] = 110
    a[3, :, 3] = 170
    Image.fromarray(a, "RGBA").save(os.path.join(OUT, "video_scan.png"), optimize=True)


# ================================================================ characters
def fighter(d, ox, oy, k, gi, skin=(214, 160, 110), belt=(20, 20, 20), hair=(30, 20, 15), pose="stance", flip=False):
    """A sprite-like martial artist: feet at (ox, oy), height ~100*k px."""
    P = {
        "stance": dict(head=(2, -90), neck=(0, -79), sh=(0, -74), hip=(0, -46), kL=(-14, -24), fL=(-22, 0),
                       kR=(14, -24), fR=(24, 0), eL=(14, -60), hL=(26, -70), eR=(18, -52), hR=(30, -56)),
        "kick": dict(head=(-10, -86), neck=(-8, -76), sh=(-7, -71), hip=(0, -46), kL=(-6, -24), fL=(-10, 0),
                     kR=(22, -58), fR=(52, -70), eL=(-22, -62), hL=(-30, -52), eR=(8, -62), hR=(18, -70)),
        "punch": dict(head=(6, -88), neck=(4, -78), sh=(4, -73), hip=(0, -46), kL=(-16, -24), fL=(-26, 0),
                      kR=(16, -26), fR=(28, 0), eL=(24, -72), hL=(46, -74), eR=(10, -58), hR=(18, -64)),
        "walk": dict(head=(3, -90), neck=(1, -79), sh=(1, -74), hip=(0, -46), kL=(-8, -24), fL=(-16, 0),
                     kR=(10, -22), fR=(12, 0), eL=(8, -58), hL=(16, -52), eR=(-6, -58), hR=(-12, -48)),
        "hit": dict(head=(-14, -84), neck=(-10, -75), sh=(-9, -70), hip=(0, -45), kL=(-12, -24), fL=(-24, 0),
                    kR=(10, -24), fR=(16, 0), eL=(-22, -78), hL=(-30, -90), eR=(4, -78), hR=(2, -92)),
    }[pose]
    s = -1 if flip else 1

    def p(n):
        x, y = P[n]
        return (ox + s * x * k, oy + y * k)
    lw = max(2, int(9 * k))
    shade = tuple(int(c * 0.7) for c in gi)
    # back limbs first (darker)
    d.line([p("hip"), p("kL"), p("fL")], fill=shade, width=lw, joint="curve")
    d.line([p("sh"), p("eR"), p("hR")], fill=tuple(int(c * 0.8) for c in skin), width=max(2, int(7 * k)), joint="curve")
    # torso
    sh, hip = p("sh"), p("hip")
    tw = 11 * k
    d.polygon([(sh[0] - tw, sh[1]), (sh[0] + tw, sh[1]), (hip[0] + tw * 0.8, hip[1]), (hip[0] - tw * 0.8, hip[1])], fill=gi)
    d.line([(hip[0] - tw * 0.9, hip[1] - 3 * k), (hip[0] + tw * 0.9, hip[1] - 3 * k)], fill=belt, width=max(2, int(4 * k)))
    d.line([p("hip"), p("kR"), p("fR")], fill=gi, width=lw, joint="curve")
    d.line([p("sh"), p("eL"), p("hL")], fill=skin, width=max(2, int(7 * k)), joint="curve")
    for n, rr in (("hL", 4.5), ("hR", 4.5)):
        x, y = p(n)
        d.ellipse([x - rr * k, y - rr * k, x + rr * k, y + rr * k], fill=skin)
    for n in ("fL", "fR"):
        x, y = p(n)
        d.ellipse([x - 6 * k, y - 3 * k, x + 7 * k, y + 2 * k], fill=skin)
    x, y = p("neck")
    d.line([p("neck"), p("sh")], fill=skin, width=max(2, int(6 * k)))
    hx, hy = p("head")
    d.ellipse([hx - 8 * k, hy - 9 * k, hx + 8 * k, hy + 9 * k], fill=skin)
    d.pieslice([hx - 9 * k, hy - 11 * k, hx + 9 * k, hy + 7 * k], 180, 360, fill=hair)


def car_rear(d, cx, by, wdt, body=(200, 20, 24)):
    """A generic sports car seen from behind; bottom centre at (cx, by), width wdt."""
    h = wdt * 0.42
    k = wdt / 100.0
    d.rounded_rectangle([cx - 46 * k, by - 16 * k, cx - 30 * k, by], radius=int(3 * k), fill=(12, 12, 12))
    d.rounded_rectangle([cx + 30 * k, by - 16 * k, cx + 46 * k, by], radius=int(3 * k), fill=(12, 12, 12))
    d.polygon([(cx - 50 * k, by - 6 * k), (cx + 50 * k, by - 6 * k), (cx + 48 * k, by - 24 * k), (cx + 30 * k, by - 30 * k),
               (cx - 30 * k, by - 30 * k), (cx - 48 * k, by - 24 * k)], fill=body)
    d.polygon([(cx - 28 * k, by - 30 * k), (cx + 28 * k, by - 30 * k), (cx + 20 * k, by - 42 * k), (cx - 20 * k, by - 42 * k)],
              fill=tuple(int(c * 0.75) for c in body))
    d.polygon([(cx - 24 * k, by - 31 * k), (cx + 24 * k, by - 31 * k), (cx + 18 * k, by - 40 * k), (cx - 18 * k, by - 40 * k)], fill=(40, 50, 70))
    d.rectangle([cx - 52 * k, by - 33 * k, cx + 52 * k, by - 30 * k], fill=(20, 20, 20))  # wing
    d.rectangle([cx - 44 * k, by - 22 * k, cx - 26 * k, by - 17 * k], fill=(255, 60, 40))
    d.rectangle([cx + 26 * k, by - 22 * k, cx + 44 * k, by - 17 * k], fill=(255, 60, 40))
    d.rectangle([cx - 12 * k, by - 18 * k, cx + 12 * k, by - 12 * k], fill=(230, 230, 210))
    d.ellipse([cx - 22 * k, by - 10 * k, cx - 14 * k, by - 5 * k], fill=(60, 60, 60))


# ================================================================== screens
SW, SH = 336, 251


def scr_fighter():
    k = 2
    W, H = SW * k, SH * k
    img = to_img(vgrad(W, H, [(0, (40, 20, 70)), (0.35, (200, 80, 60)), (0.55, (250, 170, 80)), (0.62, (120, 70, 60)), (1, (70, 50, 45))]))
    d = ImageDraw.Draw(img)
    # sun and distant hills
    d.ellipse([W * 0.62, H * 0.28, W * 0.78, H * 0.48], fill=(255, 220, 140))
    hills = [(0, H * 0.58)] + [(x, H * (0.50 + 0.05 * math.sin(x * 0.012) + 0.03 * math.sin(x * 0.031))) for x in range(0, W + 8, 8)] + [(W, H * 0.62), (0, H * 0.62)]
    d.polygon(hills, fill=(90, 50, 70))
    # temple gate silhouette
    gx = W * 0.22
    d.rectangle([gx - 70, H * 0.36, gx + 70, H * 0.38], fill=(40, 16, 24))
    d.polygon([(gx - 90, H * 0.33), (gx + 90, H * 0.33), (gx + 76, H * 0.36), (gx - 76, H * 0.36)], fill=(40, 16, 24))
    for px in (gx - 55, gx + 55):
        d.rectangle([px - 6, H * 0.36, px + 6, H * 0.62], fill=(40, 16, 24))
    d.rectangle([gx - 60, H * 0.42, gx + 60, H * 0.435], fill=(40, 16, 24))
    # stone floor in perspective
    fy = H * 0.62
    d.rectangle([0, fy, W, H], fill=(120, 100, 90))
    for i in range(1, 9):
        y = fy + (H - fy) * (i / 9.0) ** 1.6
        d.line([(0, y), (W, y)], fill=(90, 74, 68), width=2)
    for i in range(-12, 13):
        d.line([(W / 2 + i * 26, fy), (W / 2 + i * 90, H)], fill=(96, 80, 72), width=2)
    # shadows and fighters
    d.ellipse([W * 0.30 - 40, H * 0.90 - 6, W * 0.30 + 40, H * 0.90 + 6], fill=(80, 64, 58))
    d.ellipse([W * 0.62 - 40, H * 0.90 - 6, W * 0.62 + 40, H * 0.90 + 6], fill=(80, 64, 58))
    fighter(d, W * 0.30, H * 0.90, 2.35, (236, 236, 228), belt=(20, 20, 20), pose="punch")
    fighter(d, W * 0.62, H * 0.90, 2.35, (40, 70, 170), skin=(200, 140, 96), belt=(230, 200, 40), pose="hit", flip=True)
    # impact spark
    sx, sy = W * 0.30 + 46 * 2.35, H * 0.90 - 74 * 2.35
    d.polygon(star_pts(sx + 12, sy, 26, 9, 8), fill=(255, 250, 200))
    # HUD
    for side in (-1, 1):
        x0 = W / 2 + side * 34
        x1 = W / 2 + side * 300
        a, b = min(x0, x1), max(x0, x1)
        d.rectangle([a - 3, 22, b + 3, 46], fill=(20, 20, 30))
        d.rectangle([a, 25, b, 43], fill=(200, 20, 20))
        fill = 0.82 if side < 0 else 0.38
        if side < 0:
            d.rectangle([b - (b - a) * fill, 25, b, 43], fill=(250, 220, 40))
        else:
            d.rectangle([a, 25, a + (b - a) * fill, 43], fill=(250, 220, 40))
    d.text((W / 2, 40), "62", font=font("mono", 40), fill=(255, 255, 255), anchor="mm", stroke_width=3, stroke_fill=(30, 30, 60))
    d.text((W / 2 - 300, 64), "MARCO", font=font("sans", 18), fill=(255, 255, 255), anchor="lm", stroke_width=2, stroke_fill=(0, 0, 0))
    d.text((W / 2 + 300, 64), "SHUN", font=font("sans", 18), fill=(255, 255, 255), anchor="rm", stroke_width=2, stroke_fill=(0, 0, 0))
    d.text((20, 10), "1P  024300", font=font("mono", 16), fill=(255, 255, 255), anchor="lt")
    d.text((W - 20, 10), "2P  008100", font=font("mono", 16), fill=(255, 255, 255), anchor="rt")
    return down(img, SW, SH)


def scr_brawler():
    k = 2
    W, H = SW * k, SH * k
    img = to_img(vgrad(W, H, [(0, (10, 12, 40)), (0.5, (40, 30, 80)), (0.52, (30, 26, 40)), (1, (30, 26, 34))]))
    d = ImageDraw.Draw(img)
    r = rng(301)
    # skyline with lit windows
    x = 0
    while x < W:
        bw = int(r.integers(50, 110))
        bh = int(r.integers(100, 230))
        d.rectangle([x, H * 0.52 - bh, x + bw, H * 0.52], fill=(24, 22, 46))
        for wy in range(int(H * 0.52 - bh + 10), int(H * 0.52 - 10), 16):
            for wx in range(x + 8, x + bw - 8, 14):
                if r.random() < 0.35:
                    d.rectangle([wx, wy, wx + 6, wy + 8], fill=(240, 210, 110))
        x += bw + int(r.integers(2, 10))
    # brick wall
    d.rectangle([0, H * 0.38, W, H * 0.62], fill=(110, 46, 38))
    for row in range(10):
        y = H * 0.38 + row * 13
        off = 0 if row % 2 else 20
        d.line([(0, y), (W, y)], fill=(60, 30, 26), width=2)
        for bx in range(-off, W, 40):
            d.line([(bx, y), (bx, y + 13)], fill=(60, 30, 26), width=2)
    # neon sign on the wall
    d.rounded_rectangle([W * 0.58, H * 0.41, W * 0.86, H * 0.49], radius=8, outline=(255, 70, 160), width=4)
    d.text((W * 0.72, H * 0.45), "BAR", font=font("sans", 26), fill=(255, 140, 210), anchor="mm")
    # sidewalk and street
    d.rectangle([0, H * 0.62, W, H * 0.70], fill=(90, 88, 96))
    d.rectangle([0, H * 0.70, W, H], fill=(44, 42, 50))
    for i in range(0, W, 120):
        d.rectangle([i, H * 0.86, i + 60, H * 0.875], fill=(200, 190, 120))
    # heroes and thugs
    cols = [(210, 40, 36), (50, 90, 220), (230, 190, 40), (50, 170, 70)]
    xs = [0.14, 0.30, 0.46, 0.22]
    ys = [0.86, 0.80, 0.90, 0.96]
    poses = ["punch", "stance", "kick", "walk"]
    for c, x0, y0, ps in zip(cols, xs, ys, poses):
        d.ellipse([W * x0 - 30, H * y0 - 5, W * x0 + 30, H * y0 + 5], fill=(26, 24, 30))
        fighter(d, W * x0, H * y0, 1.55, c, skin=(220, 170, 120), belt=(30, 30, 30), pose=ps)
    for x0, y0, ps in ((0.66, 0.84, "hit"), (0.78, 0.92, "stance"), (0.90, 0.80, "walk")):
        d.ellipse([W * x0 - 30, H * y0 - 5, W * x0 + 30, H * y0 + 5], fill=(26, 24, 30))
        fighter(d, W * x0, H * y0, 1.6, (100, 100, 110), skin=(190, 140, 100), belt=(60, 20, 20), pose=ps, flip=True, hair=(150, 40, 160))
    # HUD: four player boxes
    names = ["1P", "2P", "3P", "4P"]
    for i in range(4):
        x0 = 14 + i * (W - 28) / 4.0
        d.rectangle([x0, 8, x0 + 150, 50], fill=(0, 0, 0))
        d.text((x0 + 6, 18), names[i], font=font("sans", 16), fill=cols[i], anchor="lm")
        d.rectangle([x0 + 40, 12, x0 + 144, 24], fill=(60, 20, 20))
        d.rectangle([x0 + 40, 12, x0 + 40 + 104 * (0.9 - i * 0.18), 24], fill=(250, 220, 50))
        d.text((x0 + 6, 38), "%06d" % (14300 + i * 7710), font=font("mono", 13), fill=(255, 255, 255), anchor="lm")
    d.text((W - 60, H * 0.64), "GO", font=font("black", 34), fill=(255, 230, 40), anchor="mm", stroke_width=3, stroke_fill=(120, 20, 0))
    d.polygon([(W - 30, H * 0.64 - 16), (W - 8, H * 0.64), (W - 30, H * 0.64 + 16)], fill=(255, 230, 40))
    return down(img, SW, SH)


def scr_gun():
    k = 2
    W, H = SW * k, SH * k
    img = to_img(vgrad(W, H, [(0, (110, 170, 230)), (0.4, (230, 200, 160)), (0.45, (200, 150, 100)), (1, (170, 120, 70))]))
    d = ImageDraw.Draw(img)
    # mesas
    d.polygon([(0, H * 0.42), (60, H * 0.30), (160, H * 0.30), (190, H * 0.42)], fill=(170, 90, 60))
    d.polygon([(W - 240, H * 0.42), (W - 200, H * 0.33), (W - 100, H * 0.33), (W - 60, H * 0.42)], fill=(160, 84, 58))
    # building facades
    fac = [(10, 150, (120, 70, 40), "SALOON"), (170, 130, (90, 60, 40), "BANK"), (466, 120, (110, 80, 50), "HOTEL"), (596, 70, (80, 54, 36), "")]
    for x0, bw, c, sign in fac:
        top = H * 0.16 if sign else H * 0.30
        d.rectangle([x0, top, x0 + bw, H * 0.70], fill=c)
        for wx in range(x0 + 14, x0 + bw - 20, 40):
            d.rectangle([wx, top + 50, wx + 22, top + 86], fill=(30, 20, 14))
        d.rectangle([x0, H * 0.55, x0 + bw, H * 0.57], fill=tuple(int(v * 0.6) for v in c))
        if sign:
            d.rectangle([x0 + 10, top + 10, x0 + bw - 10, top + 36], fill=(230, 210, 160))
            d.text((x0 + bw / 2, top + 23), sign, font=font("serif", 18), fill=(80, 30, 20), anchor="mm")
        for px in range(x0 + 4, x0 + bw, 30):
            d.rectangle([px, H * 0.57, px + 4, H * 0.70], fill=tuple(int(v * 0.5) for v in c))
    # street
    d.polygon([(320, H * 0.42), (360, H * 0.42), (W, H), (0, H)], fill=(190, 140, 90))
    # pop-up targets: wooden boards with painted bullseyes
    for tx, ty, tr in ((90, H * 0.47, 26), (250, H * 0.36, 20), (530, H * 0.40, 22), (420, H * 0.72, 40), (150, H * 0.82, 36)):
        d.rectangle([tx - 3, ty, tx + 3, ty + tr * 2.2], fill=(90, 60, 30))
        for i, c in enumerate([(240, 240, 230), (200, 30, 30), (240, 240, 230), (200, 30, 30)]):
            rr = tr * (1 - i * 0.24)
            d.ellipse([tx - rr, ty - rr, tx + rr, ty + rr], fill=c)
    # bullet holes on one target
    for hx, hy in ((412, H * 0.70), (430, H * 0.735), (418, H * 0.75)):
        d.ellipse([hx - 4, hy - 4, hx + 4, hy + 4], fill=(20, 10, 6))
    # crosshairs
    for cx, cy, c in ((420, H * 0.72, (255, 40, 30)), (250, H * 0.37, (60, 120, 255))):
        d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], outline=c, width=4)
        for a in range(4):
            dx, dy = [(1, 0), (-1, 0), (0, 1), (0, -1)][a]
            d.line([(cx + dx * 14, cy + dy * 14), (cx + dx * 38, cy + dy * 38)], fill=c, width=4)
    # HUD
    d.rectangle([0, H - 52, W, H], fill=(20, 14, 10))
    d.text((16, H - 26), "1P 008750", font=font("mono", 20), fill=(255, 80, 60), anchor="lm")
    d.text((W - 16, H - 26), "2P 004200", font=font("mono", 20), fill=(110, 160, 255), anchor="rm")
    for i in range(6):
        d.rectangle([220 + i * 14, H - 40, 228 + i * 14, H - 14], fill=(230, 190, 60))
    d.text((W / 2 + 70, H - 26), "RELOAD", font=font("sans", 20), fill=(255, 60, 40), anchor="mm")
    d.text((W / 2, 24), "STAGE 3  -  MAIN STREET", font=font("sans", 18), fill=(255, 255, 255), anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0))
    return down(img, SW, SH)


def scr_sidescroller():
    """Horizontal side-scrolling shooter: ship flies right over a rocky ridge, nebula behind."""
    k = 2
    W, H = SW * k, SH * k
    a = vgrad(W, H, [(0, (6, 4, 20)), (0.7, (20, 10, 40)), (1, (30, 14, 44))])
    for cx, cy, rr, c in ((W * 0.70, H * 0.30, 300, (170, 40, 120)), (W * 0.30, H * 0.55, 260, (30, 110, 150)), (W * 0.9, H * 0.7, 180, (90, 40, 170))):
        a += (radial(W, H, cx, cy, rr) ** 2)[:, :, None] * np.array(c, np.float32)[None, None, :] / 255.0 * 0.55
    n = fbm(W, H, 351, (90, 30, 10), (0.5, 0.3, 0.2))
    a *= (0.75 + 0.5 * n)[:, :, None]
    img = to_img(a)
    d = ImageDraw.Draw(img)
    r = rng(352)
    for i in range(90):
        x, y = r.uniform(0, W), r.uniform(0, H * 0.8)
        L = r.uniform(2, 26)
        v = int(r.integers(120, 255))
        d.line([(x, y), (x + L, y)], fill=(v, v, v), width=1 if L < 14 else 2)
    # rocky ridge along the bottom, two layers
    for layer, (col, base, amp) in enumerate((((60, 36, 70), 0.80, 40), ((96, 60, 50), 0.88, 30))):
        pts = [(0, H)]
        x = 0
        while x <= W + 20:
            pts.append((x, H * base - amp * abs(math.sin(x * 0.013 + layer)) - r.uniform(0, amp * 0.6)))
            x += 18
        pts.append((W, H))
        d.polygon(pts, fill=col)
    # armoured cruiser entering from the right
    cx, cy = W * 0.92, H * 0.34
    d.polygon([(cx - 120, cy), (cx - 60, cy - 46), (cx + 120, cy - 46), (cx + 120, cy + 46), (cx - 60, cy + 46)], fill=(120, 126, 140))
    d.rectangle([cx - 40, cy - 60, cx + 120, cy - 46], fill=(90, 96, 110))
    d.rectangle([cx - 30, cy + 46, cx + 120, cy + 58], fill=(90, 96, 110))
    for j in range(5):
        d.rectangle([cx - 30 + j * 28, cy - 8, cx - 16 + j * 28, cy + 4], fill=(255, 200, 60))
    d.ellipse([cx - 96, cy - 10, cx - 76, cy + 10], fill=(255, 60, 40))
    # wedge gunships on a sine path
    for j in range(5):
        ex = W * 0.48 + j * 46
        ey = H * 0.58 + 50 * math.sin(j * 0.9)
        d.polygon([(ex - 22, ey), (ex + 18, ey - 14), (ex + 10, ey), (ex + 18, ey + 14)], fill=(240, 130, 40))
        d.polygon([(ex - 4, ey - 4), (ex + 8, ey - 4), (ex + 8, ey + 4), (ex - 4, ey + 4)], fill=(80, 30, 20))
    # player ship, facing right, engine flame behind
    sx, sy = W * 0.18, H * 0.48
    d.polygon([(sx - 50, sy - 6), (sx + 46, sy), (sx - 50, sy + 10)], fill=(220, 226, 236))
    d.polygon([(sx - 30, sy - 4), (sx - 10, sy - 24), (sx + 4, sy - 2)], fill=(170, 176, 190))
    d.polygon([(sx - 30, sy + 6), (sx - 10, sy + 24), (sx + 4, sy + 4)], fill=(170, 176, 190))
    d.ellipse([sx - 6, sy - 9, sx + 18, sy + 1], fill=(60, 170, 255))
    d.polygon([(sx - 52, sy - 5), (sx - 82, sy + 2), (sx - 52, sy + 9)], fill=(255, 170, 50))
    d.polygon([(sx - 52, sy - 2), (sx - 68, sy + 2), (sx - 52, sy + 6)], fill=(255, 250, 200))
    for j in range(4):
        d.rectangle([sx + 60 + j * 70, sy - 2, sx + 100 + j * 70, sy + 4], fill=(120, 220, 255))
    # explosion and a power capsule
    d.polygon(star_pts(W * 0.62, H * 0.42, 30, 12, 9), fill=(255, 190, 60))
    d.polygon(star_pts(W * 0.62, H * 0.42, 15, 7, 7), fill=(255, 255, 220))
    d.ellipse([W * 0.40 - 14, H * 0.30 - 10, W * 0.40 + 14, H * 0.30 + 10], fill=(220, 40, 40), outline=(255, 220, 220), width=2)
    d.text((W * 0.40, H * 0.30), "P", font=font("sans", 14), fill=(255, 255, 255), anchor="mm")
    # HUD
    d.rectangle([0, H - 34, W, H], fill=(0, 0, 0))
    d.text((16, H - 17), "1P 0052300", font=font("mono", 18), fill=(255, 255, 255), anchor="lm")
    d.text((W / 2 + 40, H - 17), "HI 0100000", font=font("mono", 18), fill=(255, 80, 80), anchor="mm")
    for j in range(3):
        d.polygon([(W - 90 + j * 26, H - 24), (W - 70 + j * 26, H - 17), (W - 90 + j * 26, H - 10)], fill=(220, 226, 236))
    d.text((W / 2, 18), "STAGE 2", font=font("sans", 16), fill=(255, 230, 80), anchor="mm")
    return down(img, SW, SH)


def scr_football():
    k = 2
    W, H = SW * k, SH * k
    img = Image.new("RGB", (W, H), (20, 20, 30))
    d = ImageDraw.Draw(img)
    # field in perspective (camera behind the offence)
    hy = H * 0.16
    d.polygon([(W * 0.22, hy), (W * 0.78, hy), (W * 1.25, H), (-W * 0.25, H)], fill=(40, 130, 50))
    for i in range(12):
        t0 = i / 12.0
        t1 = (i + 0.5) / 12.0
        y0 = hy + (H - hy) * t0 ** 1.5
        y1 = hy + (H - hy) * t1 ** 1.5
        w0 = W * 0.28 + (W * 0.75 - W * 0.28) * ((y0 - hy) / (H - hy))
        w1 = W * 0.28 + (W * 0.75 - W * 0.28) * ((y1 - hy) / (H - hy))
        d.polygon([(W / 2 - w0, y0), (W / 2 + w0, y0), (W / 2 + w1, y1), (W / 2 - w1, y1)], fill=(52, 146, 60))
    for i in range(13):
        t = i / 12.0
        y = hy + (H - hy) * t ** 1.5
        w = W * 0.28 + (W * 0.75 - W * 0.28) * ((y - hy) / (H - hy))
        d.line([(W / 2 - w, y), (W / 2 + w, y)], fill=(235, 240, 230), width=2 if t < 0.5 else 3)
        if i in (4, 8):
            d.text((W / 2 - w * 0.7, y + 10), "40" if i == 4 else "30", font=font("sans", int(10 + 18 * t)), fill=(235, 240, 230), anchor="mm")
            d.text((W / 2 + w * 0.7, y + 10), "40" if i == 4 else "30", font=font("sans", int(10 + 18 * t)), fill=(235, 240, 230), anchor="mm")
    # line of scrimmage and players
    ly = hy + (H - hy) * 0.55 ** 1.5
    d.line([(W * 0.1, ly), (W * 0.9, ly)], fill=(80, 140, 255), width=3)
    r = rng(305)
    for team, dy, col in ((0, 18, (210, 30, 30)), (1, -16, (240, 240, 240))):
        for i in range(11):
            x = W / 2 + (i - 5) * 30 + r.uniform(-6, 6)
            y = ly + dy + (r.uniform(0, 30) if team == 0 and i in (5, 6) else 0) - (r.uniform(0, 40) if team == 1 and i in (0, 10) else 0)
            sz = 0.8 + (y - hy) / (H - hy) * 0.6
            d.ellipse([x - 9 * sz, y - 30 * sz, x + 9 * sz, y], fill=col)
            d.ellipse([x - 6 * sz, y - 40 * sz, x + 6 * sz, y - 28 * sz], fill=(220, 200, 40) if team == 0 else (40, 40, 140))
            d.rectangle([x - 7 * sz, y - 4 * sz, x + 7 * sz, y + 2 * sz], fill=(30, 30, 30))
    # scoreboard
    d.rectangle([0, 0, W, 44], fill=(10, 10, 20))
    d.text((20, 22), "HOME 14", font=font("mono", 22), fill=(255, 80, 60), anchor="lm")
    d.text((W / 2, 22), "4TH  0:42", font=font("mono", 22), fill=(255, 230, 60), anchor="mm")
    d.text((W - 20, 22), "VIS 10", font=font("mono", 22), fill=(220, 220, 255), anchor="rm")
    d.rectangle([W / 2 - 90, H - 44, W / 2 + 90, H - 12], fill=(0, 0, 0))
    d.text((W / 2, H - 28), "3RD & 4", font=font("sans", 20), fill=(255, 255, 255), anchor="mm")
    return down(img, SW, SH)


def scr_bowling():
    """Trackball bowling: a lane in perspective, the ten pins, the ball, a ten-frame score sheet."""
    k = 2
    W, H = SW * k, SH * k
    img = to_img(vgrad(W, H, [(0, (10, 6, 30)), (1, (24, 10, 44))]))
    d = ImageDraw.Draw(img)
    r = rng(356)
    # blacklight neon on the masking wall
    for j, c in enumerate([(255, 60, 180), (60, 230, 255), (255, 230, 60)]):
        d.arc([W * 0.1 - j * 30, H * 0.10 - j * 10, W * 0.9 + j * 30, H * 0.62 + j * 10], 190, 350, fill=c, width=5)
    for j in range(40):
        x, y = r.uniform(0, W), r.uniform(H * 0.15, H * 0.45)
        d.ellipse([x, y, x + 3, y + 3], fill=(200, 200, 255))
    hy = H * 0.40
    def lx(t, off):
        half = 46 + (W * 0.58 - 46) * t
        return W / 2 + off * half, hy + (H - hy) * t
    # gutters then the lane boards
    d.polygon([lx(0, -1.25), lx(0, 1.25), lx(1, 1.25), lx(1, -1.25)], fill=(40, 40, 50))
    for b in range(16):
        o0, o1 = -1 + b / 8.0, -1 + (b + 1) / 8.0
        c = (205, 150, 90) if b % 2 else (190, 136, 80)
        d.polygon([lx(0, o0), lx(0, o1), lx(1, o1), lx(1, o0)], fill=c)
    # aiming arrows and dots
    for j in range(-3, 4):
        x, y = lx(0.62, j * 0.25)
        d.polygon([(x, y - 14), (x - 6, y + 6), (x + 6, y + 6)], fill=(110, 60, 30))
    # pin deck and pins (back to front)
    d.polygon([lx(0, -1), lx(0, 1), lx(0.07, 1), lx(0.07, -1)], fill=(230, 200, 150))
    rows = [(-0.6, -0.2, 0.2, 0.6), (-0.4, 0.0, 0.4), (-0.2, 0.2), (0.0,)]
    for ri, row in enumerate(rows):
        t = 0.012 + ri * 0.016
        for o in row:
            x, y = lx(t, o * 0.8)
            ph = 30 + ri * 2
            d.ellipse([x - 6, y - ph, x + 6, y - ph * 0.55], fill=(250, 250, 245))
            d.ellipse([x - 8, y - ph * 0.6, x + 8, y], fill=(250, 250, 245))
            d.rectangle([x - 5, y - ph * 0.66, x + 5, y - ph * 0.58], fill=(220, 30, 30))
    # the ball, rolling with a hook
    bx, by = lx(0.45, 0.18)
    d.ellipse([bx - 24, by - 40, bx + 24, by + 6], fill=(30, 60, 200))
    d.arc([bx - 18, by - 34, bx + 10, by - 6], 200, 340, fill=(130, 170, 255), width=4)
    d.ellipse([bx - 12, by - 30, bx - 2, by - 22], fill=(10, 10, 30))
    # score sheet across the top
    d.rectangle([10, 8, W - 10, 66], fill=(240, 240, 230))
    fw = (W - 20) / 10.0
    marks = ["X", "9 /", "8 1", "X", "7 /", "", "", "", "", ""]
    tot = ["20", "38", "47", "67", "", "", "", "", "", ""]
    for j in range(10):
        x0 = 10 + j * fw
        d.rectangle([x0, 8, x0 + fw, 66], outline=(30, 30, 60), width=2)
        d.text((x0 + fw / 2, 16), str(j + 1), font=font("sans", 11), fill=(30, 30, 90), anchor="mm")
        d.text((x0 + fw / 2, 34), marks[j], font=font("mono", 16), fill=(200, 20, 20), anchor="mm")
        d.text((x0 + fw / 2, 55), tot[j], font=font("mono", 15), fill=(20, 20, 20), anchor="mm")
    d.text((20, H - 22), "PLAYER 1", font=font("sans", 18), fill=(255, 230, 60), anchor="lm", stroke_width=2, stroke_fill=(0, 0, 0))
    d.text((W - 20, H - 22), "FRAME 6", font=font("sans", 18), fill=(255, 255, 255), anchor="rm", stroke_width=2, stroke_fill=(0, 0, 0))
    return down(img, SW, SH)


def scr_racer():
    k = 2
    W, H = SW * k, SH * k
    hy = H * 0.42
    img = to_img(vgrad(W, H, [(0, (40, 60, 150)), (0.30, (240, 120, 90)), (0.42, (255, 200, 120)), (0.43, (60, 120, 60)), (1, (40, 100, 40))]))
    d = ImageDraw.Draw(img)
    mt = [(0, hy)] + [(x, hy - 30 - 34 * abs(math.sin(x * 0.009)) - 18 * abs(math.sin(x * 0.027))) for x in range(0, W + 10, 10)] + [(W, hy)]
    d.polygon(mt, fill=(110, 70, 110))
    # road with a gentle right bend
    def rx(t, off):
        y = hy + (H - hy) * t
        cx = W / 2 + 60 * (1 - t) ** 2.2
        half = 8 + (W * 0.62) * t
        return cx + off * half, y
    N = 40
    for i in range(N):
        t0, t1 = (i / N) ** 1.0, ((i + 1) / N) ** 1.0
        stripe = int((t0 ** 0.5) * 30) % 2
        for off0, off1, col in ((-1.15, -1.0, (230, 30, 30) if stripe else (240, 240, 240)), (1.0, 1.15, (230, 30, 30) if stripe else (240, 240, 240)),
                                 (-1.0, 1.0, (96, 96, 104) if stripe else (106, 106, 112))):
            d.polygon([rx(t0, off0), rx(t0, off1), rx(t1, off1), rx(t1, off0)], fill=col)
        if stripe:
            d.polygon([rx(t0, -0.03), rx(t0, 0.03), rx(t1, 0.03), rx(t1, -0.03)], fill=(250, 250, 240))
    # roadside poles and palms
    for t in (0.08, 0.18, 0.34, 0.6):
        for side in (-1.5, 1.5):
            x, y = rx(t, side)
            h = 10 + 220 * t
            d.rectangle([x - 1 - 4 * t, y - h, x + 1 + 4 * t, y], fill=(90, 60, 40))
            for a in range(5):
                ang = math.radians(200 + a * 35)
                d.line([(x, y - h), (x + math.cos(ang) * h * 0.35, y - h + math.sin(ang) * h * 0.2 + h * 0.08)], fill=(30, 110, 40), width=max(2, int(10 * t)))
    # rival car ahead and the player's car
    x, y = rx(0.22, 0.25)
    car_rear(d, x, y, 70, body=(30, 80, 200))
    car_rear(d, W / 2 - 10, H - 18, 230, body=(210, 24, 30))
    # HUD
    d.text((20, 18), "TIME", font=font("sans", 18), fill=(255, 230, 60), anchor="lt")
    d.text((20, 40), "38", font=font("black", 40), fill=(255, 255, 255), anchor="lt", stroke_width=3, stroke_fill=(0, 0, 0))
    d.text((W - 20, 18), "LAP 2/3", font=font("sans", 18), fill=(255, 255, 255), anchor="rt", stroke_width=2, stroke_fill=(0, 0, 0))
    d.text((W - 20, H * 0.80), "187", font=font("black", 40), fill=(255, 230, 60), anchor="rm", stroke_width=3, stroke_fill=(0, 0, 0))
    d.text((W - 20, H * 0.80 + 30), "MPH", font=font("sans", 16), fill=(255, 255, 255), anchor="rm")
    for i in range(12):
        c = (60, 220, 60) if i < 7 else ((250, 220, 40) if i < 10 else (250, 40, 30))
        d.rectangle([W - 210 + i * 15, H * 0.66, W - 200 + i * 15, H * 0.70], fill=c)
    d.text((W / 2, 24), "1ST", font=font("blacki", 30), fill=(255, 255, 255), anchor="mm", stroke_width=3, stroke_fill=(200, 20, 20))
    return down(img, SW, SH)


def scr_bricks():
    k = 2
    W, H = SW * k, SH * k
    img = Image.new("RGB", (W, H), (6, 6, 14))
    d = ImageDraw.Draw(img)
    # play field walls
    x0, x1 = W * 0.18, W * 0.82
    for xx in (x0 - 16, x1):
        d.rectangle([xx, 40, xx + 16, H], fill=(70, 90, 170))
        for yy in range(40, H, 24):
            d.line([(xx, yy), (xx + 16, yy)], fill=(130, 150, 220), width=2)
    d.rectangle([x0 - 16, 40, x1 + 16, 56], fill=(70, 90, 170))
    cols = [(200, 200, 200), (230, 40, 40), (240, 200, 30), (60, 120, 240), (220, 60, 200), (60, 200, 80)]
    bw = (x1 - x0) / 11.0
    r = rng(307)
    for row, c in enumerate(cols):
        for i in range(11):
            if row > 3 and r.random() < 0.3:
                continue
            bx = x0 + i * bw
            by = 100 + row * 22
            d.rectangle([bx + 1, by + 1, bx + bw - 2, by + 19], fill=c)
            d.line([(bx + 1, by + 1), (bx + bw - 2, by + 1)], fill=tuple(min(255, v + 70) for v in c), width=2)
    # paddle and ball
    px, py = W * 0.46, H - 40
    d.rounded_rectangle([px - 44, py - 8, px + 44, py + 8], radius=8, fill=(190, 190, 200))
    d.rectangle([px - 44, py - 8, px - 34, py + 8], fill=(230, 50, 40))
    d.rectangle([px + 34, py - 8, px + 44, py + 8], fill=(230, 50, 40))
    d.ellipse([W * 0.56 - 7, H * 0.62 - 7, W * 0.56 + 7, H * 0.62 + 7], fill=(255, 255, 255))
    d.text((24, 14), "1UP", font=font("mono", 18), fill=(255, 60, 60), anchor="lt")
    d.text((24, 34), "003450", font=font("mono", 18), fill=(255, 255, 255), anchor="lt")
    d.text((W - 24, 14), "HIGH SCORE", font=font("mono", 18), fill=(255, 60, 60), anchor="rt")
    d.text((W - 24, 34), "050000", font=font("mono", 18), fill=(255, 255, 255), anchor="rt")
    for i in range(2):
        d.rounded_rectangle([20 + i * 40, H - 20, 52 + i * 40, H - 12], radius=4, fill=(190, 190, 200))
    return down(img, SW, SH)


def crt_finish(img, seed):
    """Phosphor bloom, slight softness, darkened rounded corners (overscan)."""
    a = to_arr(img.filter(ImageFilter.GaussianBlur(0.45)))
    bloom = to_arr(img.filter(ImageFilter.GaussianBlur(4)))
    a = a * 0.92 + bloom * 0.28
    w, h = img.size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    u = (xx / (w - 1)) * 2 - 1
    v = (yy / (h - 1)) * 2 - 1
    vig = 1.0 - 0.32 * (u * u + v * v) ** 1.5
    a *= vig[:, :, None]
    # rounded overscan edge
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([3, 3, w - 4, h - 4], radius=16, fill=255)
    m = np.asarray(m.filter(ImageFilter.GaussianBlur(2.0)), np.float32) / 255.0
    a *= m[:, :, None]
    # a touch of colour gain, as arcade monitors were run hot
    a = np.clip(a * 1.08, 0, 1)
    return to_img(a)


SCREENS = [scr_fighter, scr_brawler, scr_gun, scr_sidescroller, scr_football, scr_bowling, scr_racer, scr_bricks]


def paint_screens():
    atlas = Image.new("RGB", (1024, 768), (0, 0, 0))
    for i, fn in enumerate(SCREENS):
        img = crt_finish(fn(), 400 + i)
        col, row = i % 3, i // 3
        atlas.paste(img, (col * 341 + 2, row * 256 + 2))
    save(atlas, "video_screens.png", colors=256)


# ================================================================= marquees
MW, MH = 512, 170


def mq_finish(img, seed):
    """Fluorescent backlight: bright middle band, dim tube ends, a cream cast, a little dust."""
    a = to_arr(img)
    w, h = img.size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    band = 0.80 + 0.28 * np.exp(-((yy / h - 0.42) / 0.30) ** 2) + 0.06 * np.exp(-((yy / h - 0.75) / 0.12) ** 2)
    ends = np.clip(np.minimum(xx, w - 1 - xx) / (w * 0.07), 0, 1) * 0.22 + 0.78
    a = a * (band * ends)[:, :, None]
    a = a * np.array([1.0, 0.98, 0.92], np.float32)[None, None, :]
    r = rng(seed)
    dust = (r.random((h, w)) > 0.996).astype(np.float32)
    a *= (1 - dust * 0.4)[:, :, None]
    return to_img(np.clip(a, 0, 1))


def mq_thunder():
    k = 2
    W, H = MW * k, MH * k
    img = to_img(vgrad(W, H, [(0, (20, 0, 0)), (0.5, (120, 10, 10)), (1, (10, 0, 0))]))
    a = to_arr(img)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    ang = np.arctan2(yy - H * 0.5, xx - W * 0.5)
    rays = (np.sin(ang * 14) > 0.3).astype(np.float32) * radial(W, H, W / 2, H / 2, W * 0.6) * 0.5
    a += rays[:, :, None] * np.array([1.0, 0.45, 0.05], np.float32)[None, None, :]
    img = to_img(a)
    d = ImageDraw.Draw(img)
    for x, s in ((60, 4.4), (W - 130, 4.4)):
        poly(d, bolt_pts(0, 0, 1)[:], (255, 240, 120), x, 30, s)
    img = fancy_text(img, (W / 2, H * 0.45), "THUNDER DOJO", fit("blacki", "THUNDER DOJO", W * 0.70, 150), (255, 250, 170), (250, 120, 10),
                     stroke_col=(20, 0, 0), stroke=10, glow=(255, 120, 0), glow_r=16, inner=(255, 255, 230, 120))
    d = ImageDraw.Draw(img)
    d.rectangle([W * 0.32, H * 0.80, W * 0.68, H * 0.93], fill=(10, 0, 0))
    d.text((W / 2, H * 0.865), "2 PLAYER COMBAT", font=font("sans", 34), fill=(255, 210, 60), anchor="mm")
    return down(img, MW, MH)


def mq_alley():
    k = 2
    W, H = MW * k, MH * k
    img = Image.new("RGB", (W, H), (70, 30, 26))
    d = ImageDraw.Draw(img)
    r = rng(311)
    for row in range(0, H, 34):
        off = 0 if (row // 34) % 2 else 50
        for bx in range(-off, W, 100):
            c = int(r.integers(90, 130))
            d.rectangle([bx + 3, row + 3, bx + 97, row + 31], fill=(c, int(c * 0.42), int(c * 0.34)))
    a = to_arr(img) * 0.75
    img = to_img(a)
    d = ImageDraw.Draw(img)
    # skyline silhouette along the bottom
    x = 0
    while x < W:
        bw = int(r.integers(40, 90))
        bh = int(r.integers(40, 120))
        d.rectangle([x, H - bh, x + bw, H], fill=(16, 10, 30))
        for wy in range(H - bh + 8, H - 6, 14):
            for wx in range(x + 6, x + bw - 6, 12):
                if r.random() < 0.3:
                    d.rectangle([wx, wy, wx + 5, wy + 7], fill=(250, 220, 120))
        x += bw
    img = fancy_text(img, (W / 2, H * 0.40), "IRON ALLEY", fit("black", "IRON ALLEY", W * 0.66, 170), (235, 240, 250), (110, 120, 140),
                     stroke_col=(10, 10, 14), stroke=10, shadow=(10, 10), inner=(255, 255, 255, 170))
    d = ImageDraw.Draw(img)
    for x in (W * 0.09, W * 0.91):
        d.ellipse([x - 70, H * 0.26, x + 70, H * 0.26 + 140], fill=(250, 200, 30), outline=(20, 20, 20), width=6)
        d.text((x, H * 0.26 + 52), "4", font=font("black", 70), fill=(20, 20, 20), anchor="mm")
        d.text((x, H * 0.26 + 104), "PLAYER", font=font("sans", 22), fill=(20, 20, 20), anchor="mm")
    return down(img, MW, MH)


def mq_bullseye():
    k = 2
    W, H = MW * k, MH * k
    img = to_img(vgrad(W, H, [(0, (20, 60, 160)), (1, (6, 16, 60))]))
    d = ImageDraw.Draw(img)
    cx, cy = 120, H / 2
    for i, c in enumerate([(240, 240, 235), (210, 20, 20), (240, 240, 235), (210, 20, 20), (240, 240, 235)]):
        rr = 140 - i * 28
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=c)
    d.line([(cx - 160, cy), (cx + 160, cy)], fill=(20, 20, 20), width=6)
    d.line([(cx, cy - 160), (cx, cy + 160)], fill=(20, 20, 20), width=6)
    poly(d, star_pts(W - 130, H / 2, 120, 60, 6), (230, 180, 40))
    poly(d, star_pts(W - 130, H / 2, 96, 48, 6), (250, 210, 80))
    d.ellipse([W - 160, H / 2 - 30, W - 100, H / 2 + 30], fill=(200, 150, 30))
    img = fancy_text(img, (W * 0.53, H * 0.40), "BULLSEYE", fit("serif", "BULLSEYE", W * 0.52, 132), (255, 255, 255), (210, 220, 235),
                     stroke_col=(170, 20, 20), stroke=10, shadow=(8, 8))
    img = fancy_text(img, (W * 0.53, H * 0.78), "PATROL", font("serif", 84), (255, 220, 80), (230, 150, 20),
                     stroke_col=(20, 10, 0), stroke=7)
    return down(img, MW, MH)


def mq_orbit():
    k = 2
    W, H = MW * k, MH * k
    a = vgrad(W, H, [(0, (4, 2, 16)), (1, (30, 6, 50))])
    for cx, cy, rr, c in ((W * 0.25, H * 0.5, 300, (140, 30, 160)), (W * 0.75, H * 0.4, 260, (30, 70, 170))):
        a += (radial(W, H, cx, cy, rr) ** 2)[:, :, None] * np.array(c, np.float32)[None, None, :] / 255.0 * 0.7
    img = to_img(a)
    d = ImageDraw.Draw(img)
    r = rng(313)
    for i in range(300):
        x, y = r.uniform(0, W), r.uniform(0, H)
        v = int(r.integers(140, 255))
        d.ellipse([x, y, x + 2, y + 2], fill=(v, v, v))
    px, py = W - 110, H * 0.55
    d.ellipse([px - 90, py - 90, px + 90, py + 90], fill=(220, 120, 60))
    d.chord([px - 90, py - 90, px + 90, py + 90], 110, 290, fill=(140, 60, 40))
    d.arc([px - 160, py - 34, px + 160, py + 34], 190, 530, fill=(240, 220, 180), width=8)
    # comet ship streak
    d.polygon([(40, H * 0.85), (260, H * 0.62), (270, H * 0.66), (60, H * 0.9)], fill=(120, 200, 255))
    img = fancy_text(img, (W * 0.47, H * 0.46), "ORBIT RAIDER", fit("blacki", "ORBIT RAIDER", W * 0.70, 140), (190, 240, 255), (40, 90, 220),
                     stroke_col=(240, 240, 255), stroke=5, glow=(80, 140, 255), glow_r=18, inner=(255, 255, 255, 160))
    return down(img, MW, MH)


def mq_football():
    k = 2
    W, H = MW * k, MH * k
    img = Image.new("RGB", (W, H), (30, 110, 40))
    d = ImageDraw.Draw(img)
    for x in range(0, W, 100):
        d.rectangle([x, 0, x + 50, H], fill=(36, 124, 46))
        d.line([(x, 0), (x, H)], fill=(230, 235, 225), width=4)
    d.rectangle([0, 0, W, 40], fill=(10, 10, 10))
    d.rectangle([0, H - 40, W, H], fill=(10, 10, 10))
    # football
    fx, fy = 150, H / 2
    d.ellipse([fx - 110, fy - 64, fx + 110, fy + 64], fill=(120, 60, 30))
    d.arc([fx - 70, fy - 64, fx + 70, fy + 64], 250, 290, fill=(240, 240, 240), width=6)
    d.line([(fx - 50, fy), (fx + 50, fy)], fill=(245, 245, 240), width=6)
    for i in range(-3, 4):
        d.line([(fx + i * 13, fy - 12), (fx + i * 13, fy + 12)], fill=(245, 245, 240), width=5)
    img = fancy_text(img, (W * 0.60, H * 0.47), "FOURTH & GOAL", fit("black", "FOURTH & GOAL", W * 0.62, 118), (255, 255, 255), (220, 220, 220),
                     stroke_col=(10, 10, 10), stroke=9, shadow=(8, 8))
    d = ImageDraw.Draw(img)
    d.text((W * 0.60, H - 20), "ARCADE FOOTBALL  -  1 OR 2 PLAYERS", font=font("sans", 26), fill=(255, 210, 40), anchor="mm")
    return down(img, MW, MH)


def mq_lanes():
    k = 2
    W, H = MW * k, MH * k
    img = to_img(vgrad(W, H, [(0, (8, 4, 24)), (1, (40, 8, 60))]))
    d = ImageDraw.Draw(img)
    for j, c in enumerate([(255, 60, 180), (60, 230, 255), (255, 230, 60)]):
        d.arc([-200 + j * 20, 30 + j * 26, W + 200 - j * 20, H * 2.2], 200, 340, fill=c, width=8)
    # pins scattering at the right, a ball hitting them
    r = rng(357)
    for j in range(7):
        x, y = W - 210 + r.uniform(-60, 120), H * 0.30 + r.uniform(0, 140)
        ang = r.uniform(-0.9, 0.9)
        pin = Image.new("RGBA", (40, 110), (0, 0, 0, 0))
        pd = ImageDraw.Draw(pin)
        pd.ellipse([10, 0, 30, 34], fill=(250, 250, 245, 255))
        pd.ellipse([4, 30, 36, 108], fill=(250, 250, 245, 255))
        pd.rectangle([10, 30, 30, 38], fill=(220, 30, 30, 255))
        pin = pin.rotate(math.degrees(ang), expand=True, resample=Image.BICUBIC)
        img.paste(pin, (int(x), int(y)), pin)
    d = ImageDraw.Draw(img)
    d.ellipse([W - 330, H * 0.38, W - 210, H * 0.38 + 120], fill=(30, 60, 210))
    d.arc([W - 318, H * 0.38 + 10, W - 250, H * 0.38 + 80], 200, 330, fill=(140, 180, 255), width=7)
    for j in range(3):
        d.ellipse([W - 300 + j * 22, H * 0.38 + 30 + (j % 2) * 10, W - 288 + j * 22, H * 0.38 + 42 + (j % 2) * 10], fill=(8, 8, 20))
    img = fancy_text(img, (W * 0.38, H * 0.44), "LUCKY LANES", fit("popi", "LUCKY LANES", W * 0.60, 140), (255, 250, 210), (255, 70, 170),
                     stroke_col=(20, 0, 30), stroke=9, glow=(255, 40, 170), glow_r=16, inner=(255, 255, 255, 150))
    d = ImageDraw.Draw(img)
    d.text((W * 0.38, H * 0.85), "TRACKBALL BOWLING", font=font("sans", 30), fill=(120, 240, 255), anchor="mm")
    return down(img, MW, MH)


def mq_redline():
    k = 2
    W, H = MW * k, MH * k
    img = to_img(vgrad(W, H, [(0, (10, 10, 12)), (0.6, (120, 10, 14)), (1, (230, 50, 20))]))
    d = ImageDraw.Draw(img)
    s = 26
    for row in range(3):
        for col in range(0, W // s + 1):
            if (row + col) % 2 == 0:
                d.rectangle([col * s, H - 3 * s + row * s, col * s + s, H - 2 * s + row * s], fill=(240, 240, 240))
            else:
                d.rectangle([col * s, H - 3 * s + row * s, col * s + s, H - 2 * s + row * s], fill=(14, 14, 14))
    for i in range(14):
        y = 30 + i * 12
        d.line([(0, y), (W * (0.25 + 0.04 * (i % 4)), y)], fill=(255, 200, 40), width=3)
    car_rear(d, W - 160, H - 3 * s - 4, 200, body=(230, 230, 235))
    img = fancy_text(img, (W * 0.40, H * 0.36), "RED LINE RUSH", fit("blacki", "RED LINE RUSH", W * 0.62, 128), (255, 250, 200), (255, 110, 10),
                     stroke_col=(10, 10, 10), stroke=9, glow=(255, 60, 0), glow_r=14, inner=(255, 255, 255, 150))
    return down(img, MW, MH)


def mq_paddle():
    k = 2
    W, H = MW * k, MH * k
    img = Image.new("RGB", (W, H), (12, 8, 6))
    d = ImageDraw.Draw(img)
    stripes = [(250, 220, 40), (250, 150, 30), (230, 80, 30), (190, 30, 40)]
    for i, c in enumerate(stripes):
        y = 40 + i * 26
        d.rectangle([0, y, W, y + 18], fill=c)
        y2 = H - 40 - i * 26
        d.rectangle([0, y2 - 18, W, y2], fill=c)
    d.rectangle([W * 0.10, H * 0.25, W * 0.90, H * 0.75], fill=(12, 8, 6))
    img = fancy_text(img, (W / 2, H * 0.50), "PADDLE PANIC", fit("cond", "PADDLE PANIC", W * 0.64, 130), (255, 250, 220), (255, 200, 60),
                     stroke_col=(200, 40, 30), stroke=6, glow=(255, 120, 0), glow_r=10)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([W * 0.86, H * 0.66, W * 0.94, H * 0.71], radius=8, fill=(220, 220, 230))
    d.ellipse([W * 0.83, H * 0.33, W * 0.85, H * 0.39], fill=(255, 255, 255))
    return down(img, MW, MH)


MARQUEES = [mq_thunder, mq_alley, mq_bullseye, mq_orbit, mq_football, mq_lanes, mq_redline, mq_paddle]


def paint_marquees():
    atlas = Image.new("RGB", (1024, 1024), (0, 0, 0))
    for i, fn in enumerate(MARQUEES):
        img = mq_finish(fn(), 500 + i)
        atlas.paste(img, ((i % 2) * 512, (i // 2) * 170))
    save(atlas, "video_marquees.png", colors=256)


def paint_marquees_blank():
    """The same marquee art with every word left off: the owner-editable titles are drawn
    over it live in the game (scripts/signs.gd), so a renamed cabinet keeps its artwork."""
    global fancy_text
    keep_fancy, keep_text = fancy_text, ImageDraw.ImageDraw.text
    fancy_text = lambda img, *a, **k: img
    ImageDraw.ImageDraw.text = lambda self, *a, **k: None
    try:
        atlas = Image.new("RGB", (1024, 1024), (0, 0, 0))
        for i, fn in enumerate(MARQUEES):
            img = mq_finish(fn(), 500 + i)
            atlas.paste(img, ((i % 2) * 512, (i // 2) * 170))
        save(atlas, "video_marquees_blank.png", colors=256)
    finally:
        fancy_text, ImageDraw.ImageDraw.text = keep_fancy, keep_text


# =================================================================== bezels
def paint_bezels():
    atlas = Image.new("RGB", (1024, 512), (10, 10, 12))
    accents = [(250, 180, 30), (250, 200, 40), (240, 60, 40), (120, 160, 255), (250, 250, 250), (255, 70, 180), (250, 120, 20), (250, 200, 40)]
    lines = [("INSERT TOKEN - PUSH 1 OR 2 PLAYER START", "WINNER STAYS ON"),
             ("UP TO 4 PLAYERS - JOIN IN ANY TIME", "1 TOKEN PER PLAYER"),
             ("PULL TRIGGER TO SHOOT - SHOOT OFF SCREEN TO RELOAD", "1 OR 2 PLAYERS"),
             ("1 OR 2 PLAYERS - ALTERNATING", "COLLECT POWER PODS"),
             ("PUSH START - CHOOSE YOUR TEAM", "BUY IN AT ANY TIME"),
             ("ROLL THE TRACKBALL TO BOWL", "UP TO 4 PLAYERS TAKE TURNS"),
             ("STEER - SHIFT - FLOOR IT", "CONTINUE? INSERT TOKEN"),
             ("TURN KNOB TO MOVE PADDLE", "BONUS PADDLE EVERY 20,000")]
    for i, s in enumerate(STY):
        k = 2
        W = H = 256 * k
        Wi = s["W"] - 2 * T
        Lb = bezel_len(s)
        sw, sh, sb = s["scr"]
        n = fbm(W, H, 600 + i, (60, 12, 3), (0.4, 0.35, 0.25))
        a = 0.045 + (n - 0.5) * 0.02
        img = to_img(np.dstack([a, a, a * 1.06]))
        d = ImageDraw.Draw(img)
        px = lambda x: (x + Wi / 2) / Wi * W
        py = lambda sv: (1 - sv / Lb) * H
        hx0, hx1, hy0, hy1 = px(-sw / 2), px(sw / 2), py(sb + sh), py(sb)
        acc = accents[i]
        if i == 7:
            # early-80s printed bezel: rainbow frame and stars
            for j, c in enumerate([(190, 30, 40), (230, 80, 30), (250, 150, 30), (250, 220, 40)]):
                g = 34 - j * 7
                d.rounded_rectangle([hx0 - g, hy0 - g, hx1 + g, hy1 + g], radius=24, outline=c, width=7)
            for (sx, sy) in ((W * 0.08, H * 0.1), (W * 0.92, H * 0.12), (W * 0.06, H * 0.9), (W * 0.93, H * 0.88)):
                poly(d, star_pts(sx, sy, 18, 7, 5), (250, 230, 120))
        else:
            d.rounded_rectangle([hx0 - 10, hy0 - 10, hx1 + 10, hy1 + 10], radius=10, outline=acc, width=4)
        f1 = fit("cond", lines[i][0], W * 0.92, 20)
        y_bot = (hy1 + H) / 2
        d.text((W / 2, y_bot - 12), lines[i][0], font=f1, fill=(235, 235, 235), anchor="mm")
        d.text((W / 2, y_bot + 14), lines[i][1], font=fit("cond", lines[i][1], W * 0.92, 18), fill=acc, anchor="mm")
        y_top = hy0 / 2
        if y_top > 18:
            d.text((W / 2, y_top), s["title"], font=font("condo", 22), fill=acc, anchor="mm")
        if s["vert"]:
            # wide side margins: game hints down each side
            for x in ((hx0) / 2, (hx1 + W) / 2):
                for j, t in enumerate(["DESTROY", "ALL", "RAIDERS", "", "POWER", "UP", "WITH", "PODS"]):
                    d.text((x, H * 0.25 + j * 30), t, font=font("cond", 18), fill=(220, 220, 220) if j < 3 else acc, anchor="mm")
        img = down(img, 256, 256)
        atlas.paste(img, ((i % 4) * 256, (i // 4) * 256))
    save(atlas, "video_bezels.png", colors=128)


# ==================================================================== panels
PANEL_BG = {
    0: [(0, (30, 8, 8)), (1, (90, 14, 10))],
    1: [(0, (30, 30, 34)), (1, (60, 60, 66))],
    2: [(0, (16, 40, 110)), (1, (30, 70, 160))],
    3: [(0, (24, 10, 40)), (1, (60, 20, 90))],
    4: [(0, (14, 14, 16)), (1, (34, 34, 38))],
    5: [(0, (12, 8, 24)), (1, (40, 12, 56))],
    6: [(0, (20, 20, 22)), (1, (60, 10, 12))],
    7: [(0, (60, 40, 22)), (1, (90, 60, 30))],
}


def paint_panels():
    atlas = Image.new("RGB", (1024, 1024), (0, 0, 0))
    for i, s in enumerate(STY):
        k = 2
        W, H = 512 * k, 256 * k
        Wp, Ls = panel_dims(s)
        TH = 192 * k
        img = to_img(vgrad(W, H, PANEL_BG[i]))
        d = ImageDraw.Draw(img)
        light = False
        ink = (30, 30, 34) if light else (235, 235, 235)
        px = lambda x: (x + Wp / 2) / Wp * W
        py = lambda sv: (1 - sv / Ls) * TH
        # decoration
        if i == 0:
            for j in range(9):
                x = j * W / 8
                d.polygon([(x - 40, TH), (x + 30, 0), (x + 70, 0), (x, TH)], fill=(70, 14, 10))

        elif i == 1:
            for j, x in enumerate([-0.39, -0.13, 0.13, 0.39]):
                c = rgb(s["ctl"][j * 4][3])
                d.rounded_rectangle([px(x - 0.125), py(0.29), px(x + 0.125), py(0.03)], radius=20, outline=c, width=5)
                d.text((px(x - 0.07), py(0.262)), "%dP" % (j + 1), font=font("sans", 22), fill=c, anchor="mm")
                for lbl, bx in zip(("ATTACK", "JUMP", "SPECIAL"), (0.0, 0.04, 0.08)):
                    d.text((px(x + bx + 0.005), py(0.125)), lbl, font=font("cond", 11), fill=(220, 220, 220), anchor="mm")
        elif i == 2:
            for j in range(6):
                rr = 60 + j * 60
                d.ellipse([W / 2 - rr, TH * 0.55 - rr, W / 2 + rr, TH * 0.55 + rr], outline=(40, 90, 190), width=10)
            d.text((W / 2, TH * 0.82), "HOLSTER GUNS AFTER PLAY", font=font("sans", 22), fill=(255, 230, 80), anchor="mm")
        elif i == 3:
            r = rng(330)
            for j in range(120):
                x, y = r.uniform(0, W), r.uniform(0, TH)
                d.ellipse([x, y, x + 3, y + 3], fill=(200, 200, 255))
        elif i == 4:
            for j in range(0, W, 80):
                d.line([(j, 0), (j, TH)], fill=(60, 60, 64), width=3)
            d.text((W / 2, TH * 0.88), "PASS / TACKLE       JUMP / BLOCK       TURBO", font=font("cond", 18), fill=(200, 200, 200), anchor="mm")
        elif i == 5:
            for j, c in enumerate([(255, 60, 180), (60, 230, 255), (255, 230, 60)]):
                d.arc([-W * 0.2, TH * (0.25 + j * 0.12), W * 1.2, TH * 2.4], 200, 340, fill=c, width=6)
            d.text((W / 2, TH * 0.86), "1 TO 4 PLAYERS  -  ROLL HARDER FOR MORE SPEED", font=font("cond", 18), fill=(230, 230, 240), anchor="mm")
        elif i == 6:
            for j in range(0, W, 28):
                if (j // 28) % 2 == 0:
                    d.rectangle([j, 0, j + 28, 28], fill=(230, 230, 230))
                    d.rectangle([j + 28, 28, j + 56, 56], fill=(230, 230, 230))
            d.text((px(-0.255), py(0.28)), "START", font=font("sans", 18), fill=(255, 220, 40), anchor="mm")
            d.text((px(-0.255), py(0.06)), "VIEW", font=font("sans", 18), fill=(255, 80, 60), anchor="mm")
            d.text((px(0.255), py(0.27)), "HI", font=font("sans", 20), fill=(255, 255, 255), anchor="mm")
            d.text((px(0.255), py(0.03)), "LO", font=font("sans", 20), fill=(255, 255, 255), anchor="mm")
        elif i == 7:
            for j, c in enumerate([(250, 220, 40), (250, 150, 30), (230, 80, 30), (190, 30, 40)]):
                d.rectangle([0, TH - 60 - j * 22, W, TH - 44 - j * 22], fill=c)
        # controls: printed rings, start labels, joystick arrows
        for c in s["ctl"]:
            kind, x, sv = c[0], c[1], c[2]
            cx, cy = px(x), py(sv)
            if kind == "btn":
                rr = 0.0215 / Wp * W
                d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(250, 250, 250) if not light else (40, 40, 40), width=3)
            elif kind == "start":
                rr = 0.019 / Wp * W
                d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(10, 10, 10))
                n = 1 if x < 0 else 2
                if i == 1:
                    n = [-0.350, -0.090, 0.170, 0.430].index(x) + 1
                d.text((cx, cy + rr + 16), "%d PLAYER" % n if i != 6 else "", font=font("cond", 15), fill=ink, anchor="mm")
            elif kind == "stick":
                rr = 0.030 / Wp * W
                d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=ink, width=3)
                for a in range(8):
                    ang = a * math.pi / 4
                    r0, r1 = rr + 8, rr + 22
                    d.polygon([(cx + math.cos(ang) * r1, cy + math.sin(ang) * r1),
                               (cx + math.cos(ang + 0.16) * r0, cy + math.sin(ang + 0.16) * r0),
                               (cx + math.cos(ang - 0.16) * r0, cy + math.sin(ang - 0.16) * r0)], fill=ink)
            elif kind == "ball":
                rr = 0.062 / Wp * W
                d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(20, 20, 20), outline=(200, 40, 40), width=6)
                d.text((cx, cy - rr - 18), "ROLL TO BOWL", font=font("cond", 16), fill=(240, 240, 240), anchor="mm")
            elif kind == "spin":
                rr = 0.045 / Wp * W
                d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(20, 14, 8), outline=(250, 200, 40), width=5)
                d.text((cx, cy - rr - 14), "<  SPIN  >", font=font("cond", 16), fill=(250, 220, 120), anchor="mm")
            elif kind == "gun":
                rr = 0.06 / Wp * W
                d.rectangle([cx - rr, cy - rr, cx + rr, cy + rr], fill=(10, 10, 10))
                d.text((cx, cy + rr + 18), "PLAYER %d" % (1 if x < 0 else 2), font=font("sans", 18), fill=rgb(c[3]), anchor="mm")
        if i in (0, 3, 4):
            for x, lbl in ((-0.142, "PUNCH"), (0.188, "PUNCH")) if i == 0 else ():
                d.text((px(x), py(0.205)), lbl, font=font("cond", 13), fill=(240, 200, 120), anchor="mm")
                d.text((px(x - 0.003), py(0.093)), "KICK", font=font("cond", 13), fill=(240, 200, 120), anchor="mm")
            if i == 3:
                for x in (-0.12, 0.145):
                    d.text((px(x), py(0.180)), "FIRE", font=font("cond", 13), fill=(240, 220, 120), anchor="mm")
                    d.text((px(x + 0.045), py(0.190)), "BOMB", font=font("cond", 13), fill=(120, 230, 140), anchor="mm")
        # front strip
        fy0 = TH
        d.rectangle([0, fy0, W, H], fill=PANEL_BG[i][0][1])
        d.line([(0, fy0 + 3), (W, fy0 + 3)], fill=(200, 200, 200) if not light else (120, 120, 120), width=3)
        d.text((W / 2, fy0 + 34 * k / 2 + 16), s["title"], font=font("condo", 34), fill=(255, 210, 60) if not light else (200, 30, 30), anchor="mm")
        for x in (W * 0.12, W * 0.88):
            d.text((x, fy0 + 32 * k / 2 + 16), "INSERT TOKEN", font=font("cond", 18), fill=ink, anchor="mm")
        img = down(img, 512, 256)
        img = wear_panel(img, i, s, light)
        atlas.paste(img, ((i % 2) * 512, (i // 2) * 256))
    save(atlas, "video_panels.png", colors=256)


def wear_panel(img, i, s, light):
    """Faded, rubbed overlay: palm-worn front edge, rub rings at the controls, scratches."""
    a = to_arr(img)
    h, w = a.shape[:2]
    Wp, Ls = panel_dims(s)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    grey = a.mean(axis=2, keepdims=True)
    # palms rest on the front 4 cm and the top of the front strip
    edge = np.clip(1 - np.abs(yy - 192) / 26.0, 0, 1) ** 2.0
    n = fbm(w, h, 700 + i, (40, 12, 4), (0.5, 0.3, 0.2))
    rub = edge * (0.45 + 0.6 * n)
    for c in s["ctl"]:
        if c[0] in ("stick", "btn", "ball", "spin"):
            cx = (c[1] + Wp / 2) / Wp * 508 + 2
            cy = (1 - c[2] / Ls) * 192
            rub += np.clip(1 - np.hypot(xx - cx, yy - cy) / 30.0, 0, 1) * 0.5 * n
    rub = np.clip(rub, 0, 1)[:, :, None]
    target = grey * 0.6 + 0.30 if not light else grey * 0.85
    a = a * (1 - rub * 0.35) + target * rub * 0.35
    a = a * (0.94 + 0.06 * n[:, :, None])
    img = to_img(a)
    d = ImageDraw.Draw(img)
    r = rng(720 + i)
    img = img.convert("RGBA")
    sc = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(sc)
    for j in range(28):
        x, y = r.uniform(0, w), r.uniform(60, 192)
        L = r.uniform(3, 16)
        ang = r.uniform(-0.5, 0.5)
        v = 200 if not light else 90
        d.line([(x, y), (x + L * math.cos(ang), y + L * math.sin(ang))], fill=(v, v, v, 70), width=1)
    return Image.alpha_composite(img, sc).convert("RGB")


# ===================================================================== sides
def woodgrain(w, h, seed, base=(96, 60, 34)):
    """Simulated walnut vinyl: straight grain running up the side, a few darker figure lines."""
    r = rng(seed)
    # streaks: a random grid stretched along y
    g1 = r.random((max(2, h // 90), w // 2)).astype(np.float32)
    s1 = np.asarray(Image.fromarray((g1 * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255.0
    g2 = r.random((max(2, h // 30), w)).astype(np.float32)
    s2 = np.asarray(Image.fromarray((g2 * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR), np.float32) / 255.0
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    warp = xx + 6 * np.sin(yy * 0.012 + xx * 0.02) + (vnoise(w, h, 120, seed + 3) - 0.5) * 30
    fig = 0.5 + 0.5 * np.sin(warp * 0.16)
    fig = fig ** 6
    v = 0.86 + (s1 - 0.5) * 0.22 + (s2 - 0.5) * 0.10 - fig * 0.22
    a = np.array(base, np.float32)[None, None, :] / 255.0 * v[:, :, None]
    return a


SIDE_BASE = {0: (22, 22, 24), 1: (24, 24, 27), 2: (28, 62, 140), 3: (20, 16, 28), 4: (22, 22, 24), 5: (20, 18, 26), 6: (168, 20, 26)}


def side_art(i, s, W, H, px, py):
    """Returns the side art (RGB image W x H, full cell, z -> x, y -> up)."""
    if i == 7:
        img = to_img(woodgrain(W, H, 800 + i, (128, 82, 44)))
    else:
        b = np.array(SIDE_BASE[i], np.float32) / 255.0
        n = fbm(W, H, 810 + i, (60, 16, 4), (0.5, 0.3, 0.2))
        img = to_img(b[None, None, :] * (0.96 + 0.08 * n)[:, :, None])
    d = ImageDraw.Draw(img)
    r = rng(820 + i)
    D, Hh = s["D"], s["H"]
    if i == 0:
        # flames from the floor, a lightning bolt, red slashes
        for j in range(5):
            y0 = py(0.95 + j * 0.16)
            d.polygon([(px(0.12), y0), (px(D), y0 - 60), (px(D), y0 - 40), (px(0.12), y0 + 18)], fill=(150, 16, 12))
        for j in range(26):
            x = px(r.uniform(0.1, D))
            hgt = r.uniform(70, 200)
            wdt = r.uniform(18, 34)
            for c, sc in (((200, 30, 10), 1.0), ((250, 120, 20), 0.7), ((255, 220, 80), 0.4)):
                d.polygon([(x - wdt * sc, H), (x + wdt * sc, H), (x + r.uniform(-10, 10), H - hgt * sc)], fill=c)
        poly(d, bolt_pts(0, 0, 1), (230, 110, 10), px(D * 0.5) - 3, py(1.62) - 3, 5.2)
        poly(d, bolt_pts(0, 0, 1), (255, 214, 40), px(D * 0.5), py(1.62), 5.0)
    elif i == 1:
        x = 0
        while x < W:
            bw = int(r.integers(14, 34))
            bh = int(r.integers(60, 190))
            d.rectangle([x, py(0.55) - bh, x + bw, py(0.55)], fill=(70, 50, 120))
            for wy in range(int(py(0.55) - bh + 6), int(py(0.55) - 4), 9):
                for wx in range(x + 3, x + bw - 3, 7):
                    if r.random() < 0.3:
                        d.rectangle([wx, wy, wx + 2, wy + 3], fill=(250, 220, 120))
            x += bw
        for j in range(0, W + 60, 40):
            d.polygon([(j, py(0.14)), (j + 20, py(0.14)), (j - 10, py(0.02)), (j - 30, py(0.02))], fill=(240, 200, 30))
        for j in range(6):
            cx, cy = px(r.uniform(0.3, D)), py(r.uniform(0.9, 1.6))
            for q in range(14):
                ex, ey = cx + r.normal(0, 12), cy + r.normal(0, 12)
                d.ellipse([ex, ey, ex + 4, ey + 4], fill=(230, 60, 150))
        d.rectangle([0, py(0.62), W, py(0.58)], fill=(240, 200, 30))
    elif i == 2:
        cx, cy = px(D * 0.58), py(0.62)
        for j, c in enumerate([(240, 240, 235), (210, 20, 20), (240, 240, 235), (210, 20, 20), (240, 240, 235)]):
            rr = 105 - j * 21
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=c)
        for j in range(4):
            d.polygon([(0, py(1.20 + j * 0.06)), (W, py(1.45 + j * 0.06)), (W, py(1.47 + j * 0.06)), (0, py(1.22 + j * 0.06))], fill=(235, 235, 240))
        poly(d, star_pts(px(D * 0.62), py(1.62), 48, 24, 6), (230, 180, 40))
    elif i == 3:
        a = to_arr(img)
        for cx, cy, rr, c in ((px(D * 0.4), py(1.3), 160, (170, 40, 170)), (px(D * 0.7), py(0.6), 180, (40, 70, 190))):
            a += (radial(W, H, cx, cy, rr) ** 2)[:, :, None] * np.array(c, np.float32)[None, None, :] / 255.0 * 0.6
        img = to_img(a)
        d = ImageDraw.Draw(img)
        for j in range(160):
            x, y = r.uniform(0, W), r.uniform(0, H)
            v = int(r.integers(150, 255))
            d.rectangle([x, y, x + 1, y + 1], fill=(v, v, v))
        x0, y0 = px(D * 0.55), py(0.95)
        d.ellipse([x0 - 70, y0 - 70, x0 + 70, y0 + 70], fill=(220, 130, 70))
        d.chord([x0 - 70, y0 - 70, x0 + 70, y0 + 70], 110, 290, fill=(140, 70, 50))
        d.arc([x0 - 120, y0 - 26, x0 + 120, y0 + 26], 190, 530, fill=(240, 220, 180), width=5)
        for j in range(3):
            yy = py(1.5 - j * 0.12)
            d.line([(px(0.1), yy + 40), (px(D), yy)], fill=(140, 210, 255), width=3)
    elif i == 4:
        # a large die-cut kit decal on the black laminate: turf, yard lines, a football
        z0, z1 = px(s["kz"] + 0.06), px(D - 0.07)
        y0, y1 = py(1.32), py(0.30)
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).rounded_rectangle([z0, y0, z1, y1], radius=26, fill=255)
        turf = Image.new("RGB", (W, H), (34, 120, 44))
        td = ImageDraw.Draw(turf)
        for q in range(0, H, 34):
            td.rectangle([0, q, W, q + 17], fill=(42, 134, 52))
            td.line([(0, q), (W, q)], fill=(235, 240, 230), width=3)
        img = Image.composite(turf, img, m)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([z0, y0, z1, y1], radius=26, outline=(240, 240, 240), width=5)
        d.rounded_rectangle([z0 + 8, y0 + 8, z1 - 8, y1 - 8], radius=20, outline=(200, 30, 30), width=3)
        cx, cy = (z0 + z1) / 2, py(0.88)
        d.ellipse([cx - 62, cy - 38, cx + 62, cy + 38], fill=(110, 56, 28), outline=(20, 10, 4), width=3)
        d.line([(cx - 28, cy), (cx + 28, cy)], fill=(245, 245, 240), width=4)
        for q in range(-2, 3):
            d.line([(cx + q * 10, cy - 8), (cx + q * 10, cy + 8)], fill=(245, 245, 240), width=3)
        for q in range(3):
            d.polygon([(0, py(1.55 + q * 0.05)), (W, py(1.70 + q * 0.05)), (W, py(1.72 + q * 0.05)), (0, py(1.57 + q * 0.05))],
                      fill=[(200, 30, 30), (240, 240, 240), (200, 30, 30)][q])
    elif i == 5:
        # blacklight-bowling side: neon arcs, a ball and pins
        for j, c in enumerate([(255, 60, 180), (60, 230, 255), (255, 230, 60)]):
            d.arc([-W * 0.9, py(1.75) - j * 22, W * 1.6, py(0.2) + 300 - j * 22], 190, 300, fill=c, width=7)
        for (pz, py_, sc) in ((0.55, 0.55, 1.0), (0.66, 0.50, 0.9), (0.45, 0.47, 0.9), (0.75, 0.62, 0.8)):
            x, y = px(D * pz), py(py_)
            d.ellipse([x - 9 * sc, y - 70 * sc, x + 9 * sc, y - 42 * sc], fill=(250, 250, 245))
            d.ellipse([x - 14 * sc, y - 46 * sc, x + 14 * sc, y], fill=(250, 250, 245))
            d.rectangle([x - 9 * sc, y - 48 * sc, x + 9 * sc, y - 42 * sc], fill=(220, 30, 30))
        bx, by = px(D * 0.32), py(0.34)
        d.ellipse([bx - 38, by - 38, bx + 38, by + 38], fill=(40, 70, 220))
        d.arc([bx - 28, by - 28, bx + 20, by + 20], 200, 330, fill=(150, 190, 255), width=5)
        for q in range(3):
            d.ellipse([bx - 12 + q * 10, by - 16 + (q % 2) * 6, bx - 4 + q * 10, by - 8 + (q % 2) * 6], fill=(10, 10, 30))
        for j in range(30):
            x, y = r.uniform(0, W), r.uniform(0, H)
            poly(d, star_pts(x, y, 5, 2, 4), (255, 255, 200) if j % 2 else (120, 240, 255))
    elif i == 6:
        sq = 16
        for q in range(-20, 40):
            for rr in range(3):
                if (q + rr) % 2 == 0:
                    x0 = q * sq
                    y0 = py(0.35) - q * sq * 0.55 + rr * sq
                    d.polygon([(x0, y0), (x0 + sq, y0 - sq * 0.55), (x0 + sq, y0 - sq * 0.55 + sq), (x0, y0 + sq)], fill=(240, 240, 240))
                else:
                    x0 = q * sq
                    y0 = py(0.35) - q * sq * 0.55 + rr * sq
                    d.polygon([(x0, y0), (x0 + sq, y0 - sq * 0.55), (x0 + sq, y0 - sq * 0.55 + sq), (x0, y0 + sq)], fill=(14, 14, 14))
        for j, c in enumerate([(255, 220, 40), (255, 140, 20)]):
            d.polygon([(0, py(1.20 + j * 0.05)), (W, py(1.50 + j * 0.05)), (W, py(1.53 + j * 0.05)), (0, py(1.23 + j * 0.05))], fill=c)
    elif i == 7:
        # painted swoosh stripes over the wood grain
        for j, c in enumerate([(190, 30, 40), (230, 80, 30), (250, 150, 30), (250, 220, 40)]):
            pts = []
            for q in range(21):
                t = q / 20.0
                x = px(0.05 + t * (D - 0.05))
                y = py(0.30 + j * 0.07 + 1.0 * t ** 1.6)
                pts.append((x, y))
            pts2 = [(x, y + 16) for x, y in reversed(pts)]
            d.polygon(pts + pts2, fill=c)
    return img


def wear_side(img, i, s, W, H, px, py, light):
    a = to_arr(img)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    n = fbm(W, H, 900 + i, (40, 10, 3), (0.5, 0.3, 0.2))
    # kick zone: scuffed bottom 15 cm, more at the front
    kick = np.clip((yy - py(0.16)) / (py(0.0) - py(0.16)), 0, 1) * np.clip(1.2 - xx / W, 0, 1)
    scuff = kick * (n > 0.52)
    col = np.array([0.55, 0.53, 0.50], np.float32) if not light else np.array([0.45, 0.42, 0.38], np.float32)
    a = a * (1 - scuff[:, :, None] * 0.6) + col[None, None, :] * scuff[:, :, None] * 0.6
    # grime toward the floor, slight overall fade
    a *= (1 - 0.12 * np.clip((yy - H * 0.8) / (H * 0.2), 0, 1))[:, :, None]
    a = a * 0.95 + a.mean(axis=2, keepdims=True) * 0.05
    img = to_img(a)
    d = ImageDraw.Draw(img)
    r = rng(950 + i)
    for j in range(50):
        x, y = r.uniform(0, W), r.uniform(0, H)
        L = r.uniform(3, 18)
        ang = r.uniform(0, 6.28)
        v = int(r.integers(110, 170)) if not light else int(r.integers(130, 170))
        d.line([(x, y), (x + L * math.cos(ang), y + L * math.sin(ang))], fill=(v, v, v), width=1)
    return img


def paint_sides():
    atlas = Image.new("RGB", (1024, 1024), (0, 0, 0))
    for i, s in enumerate(STY):
        W, H = 256, 512
        D, Hh = s["D"], s["H"]
        # the GD side UVs use a 0.4 % inset of the cell
        px = lambda z: (0.004 + z / D * 0.992) * W
        py = lambda y: (0.004 + (1 - y / Hh) * 0.992) * H
        img = side_art(i, s, W, H, px, py)
        img = wear_side(img, i, s, W, H, px, py, False)
        atlas.paste(img, ((i % 4) * 256, (i // 4) * 512))
    save(atlas, "video_sides.png", colors=256)


FRONT_BASE = {0: (20, 20, 22), 1: (24, 24, 27), 2: (20, 20, 22), 3: (20, 18, 26), 4: (20, 20, 22), 5: (20, 18, 26), 6: (168, 20, 26), 7: (18, 18, 20)}


def paint_fronts():
    """Lower-front panel art (video_fronts.png, 4 x 2 cells of 256 x 256), framing the coin door."""
    atlas = Image.new("RGB", (1024, 512), (0, 0, 0))
    for i, s in enumerate(STY):
        k = 2
        W = H = 256 * k
        Wi = s["W"] - 2 * T
        kh, lo = s["kh"], s["lo"]
        px = lambda x: (x + Wi / 2) / Wi * W
        py = lambda y: (1 - (y - kh) / (lo - kh)) * H
        b = np.array(FRONT_BASE[i], np.float32) / 255.0
        n = fbm(W, H, 1000 + i, (60, 16, 4), (0.5, 0.3, 0.2))
        img = to_img(b[None, None, :] * (0.94 + 0.12 * n)[:, :, None])
        d = ImageDraw.Draw(img)
        r = rng(1010 + i)
        band = (py(0.30), H)            # below the coin door
        title_y = (band[0] + H) / 2 + 6
        tcol = (255, 210, 60)
        if i == 0:
            for j in range(40):
                x = r.uniform(0, W)
                hgt = r.uniform(80, 260)
                wdt = r.uniform(20, 40)
                for c, sc in (((200, 30, 10), 1.0), ((250, 120, 20), 0.7), ((255, 220, 80), 0.4)):
                    d.polygon([(x - wdt * sc, H), (x + wdt * sc, H), (x + r.uniform(-10, 10), H - hgt * sc)], fill=c)
            for x in (0, W):
                for j in range(4):
                    y = py(0.70 - j * 0.09)
                    d.polygon([(x, y), (W / 2 + (x - W / 2) * 0.62, y - 50), (W / 2 + (x - W / 2) * 0.62, y - 30), (x, y + 20)], fill=(150, 16, 12))
            tcol = (255, 240, 160)
        elif i == 1:
            for j in range(-2, 30):
                x = j * 40
                d.polygon([(x, H - 70), (x + 20, H - 70), (x - 10, H), (x - 30, H)], fill=(240, 200, 30))
            d.rectangle([0, H - 74, W, H - 66], fill=(10, 10, 10))
            title_y = band[0] + 30
        elif i == 2:
            for j, c in enumerate([(240, 240, 235), (210, 20, 20), (240, 240, 235), (210, 20, 20)]):
                rr = 210 - j * 45
                for cx in (-40, W + 40):
                    d.ellipse([cx - rr, H * 0.55 - rr, cx + rr, H * 0.55 + rr], fill=c)
            for j in range(3):
                d.rectangle([0, H - 60 + j * 16, W, H - 52 + j * 16], fill=(40, 90, 200))
        elif i == 3:
            a = to_arr(img)
            for cx, cy, rr, c in ((W * 0.15, H * 0.5, 240, (160, 40, 160)), (W * 0.85, H * 0.7, 240, (40, 90, 200))):
                a += (radial(W, H, cx, cy, rr) ** 2)[:, :, None] * np.array(c, np.float32)[None, None, :] / 255.0 * 0.6
            img = to_img(a)
            d = ImageDraw.Draw(img)
            for j in range(120):
                x, y = r.uniform(0, W), r.uniform(0, H)
                d.rectangle([x, y, x + 2, y + 2], fill=(220, 220, 255))
            tcol = (150, 210, 255)
        elif i == 4:
            for q in range(0, 140, 28):
                d.rectangle([0, H - 140 + q, W, H - 126 + q], fill=(40, 130, 50))
                d.rectangle([0, H - 126 + q, W, H - 112 + q], fill=(34, 118, 44))
            for x in range(0, W, 64):
                d.line([(x, H - 140), (x, H)], fill=(235, 240, 230), width=3)
            tcol = (255, 255, 255)
            title_y = band[0] + 22
        elif i == 5:
            for j, c in enumerate([(255, 60, 180), (60, 230, 255), (255, 230, 60)]):
                d.arc([-W * 0.3, H * 0.62 + j * 22, W * 1.3, H * 2.0], 195, 345, fill=c, width=7)
            tcol = (255, 120, 200)
            title_y = band[0] + 26
        elif i == 6:
            sq = 24
            for q in range(W // sq + 1):
                for rr in range(3):
                    c = (240, 240, 240) if (q + rr) % 2 == 0 else (14, 14, 14)
                    d.rectangle([q * sq, H - 3 * sq + rr * sq, q * sq + sq, H - 2 * sq + rr * sq], fill=c)
            tcol = (255, 230, 60)
            title_y = H - 3 * sq - 30
        elif i == 7:
            for j, c in enumerate([(250, 220, 40), (250, 150, 30), (230, 80, 30), (190, 30, 40)]):
                d.rectangle([0, H - 110 + j * 20, W, H - 96 + j * 20], fill=c)
            tcol = (250, 200, 60)
            title_y = H - 140
        img = fancy_text(img, (W / 2, title_y), s["title"], fit("condo", s["title"], W * 0.8, 46), tcol, tuple(int(v * 0.8) for v in tcol),
                         stroke_col=(10, 10, 10), stroke=4)
        # wear: shoe scuffs low, grime toward the floor
        a = to_arr(img)
        yy = np.mgrid[0:H, 0:W][0].astype(np.float32)
        sc = (n > 0.60) * np.clip((yy - H * 0.82) / (H * 0.18), 0, 1)
        a = a * (1 - sc[:, :, None] * 0.22) + 0.30 * sc[:, :, None] * 0.22
        a *= (1 - 0.15 * np.clip((yy - H * 0.85) / (H * 0.15), 0, 1))[:, :, None]
        img = to_img(a)
        d = ImageDraw.Draw(img)
        for j in range(40):
            x, y = r.uniform(0, W), r.uniform(H * 0.6, H)
            L = r.uniform(4, 30)
            v = int(r.integers(90, 150))
            d.line([(x, y), (x + L, y + r.uniform(-4, 4))], fill=(v, v, v), width=1)
        atlas.paste(down(img, 256, 256), ((i % 4) * 256, (i // 4) * 256))
    save(atlas, "video_fronts.png", colors=256)


def main():
    os.makedirs(OUT, exist_ok=True)
    paint_lam()
    paint_tmold()
    paint_kick()
    paint_door()
    paint_entry()
    paint_speaker()
    paint_glass()
    paint_scan()
    paint_screens()
    paint_marquees()
    paint_marquees_blank()
    paint_bezels()
    paint_panels()
    paint_sides()
    paint_fronts()
    tot = 0
    for f in sorted(os.listdir(OUT)):
        if f.startswith("video_") and f.endswith(".png"):
            sz = os.path.getsize(os.path.join(OUT, f))
            tot += sz
            print("%-22s %7d" % (f, sz))
    print("total", tot)


if __name__ == "__main__":
    main()
