#!/usr/bin/env python3
"""Paints every texture of the `skee` prop module (a 1990s ten-foot ticket
redemption roll-down ball alley) into tex/pc/skee_*.png.

Deterministic: all randomness is seeded, so re-running reproduces the files.
Original artwork only: no real game's name, logo or cabinet art.

    python3 tools/stores/pocket_change/paint_skee.py
"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "..", "tex", "pc"))
FONTS = "/usr/share/fonts"
F_BLACK_IT = FONTS + "/opentype/inter/InterDisplay-BlackItalic.otf"
F_BLACK = FONTS + "/opentype/inter/InterDisplay-Black.otf"
F_BOLD = FONTS + "/opentype/inter/Inter-Bold.otf"
F_SEMI = FONTS + "/opentype/inter/Inter-SemiBold.otf"
F_COND = FONTS + "/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"

# geometry shared with skee.gd (metres, local frame: z into the machine, y up)
SIDE_Z, SIDE_Y = 3.12, 1.60          # side texture covers z 0..3.12, y 0..1.60
SIDE_OUTLINE = [(0, 0.28), (0, 0.90), (0.32, 0.90), (2.18, 1.1734), (2.30, 1.40),
                (3.12, 1.52), (3.12, 0.0), (2.18, 0.0), (2.18, 0.28)]


def font(path, size):
    return ImageFont.truetype(path, size)


def rng(seed):
    return np.random.default_rng(seed)


def smooth_noise(h, w, scale, seed):
    """Value noise in [-1, 1], blurred blobs about `scale` px across."""
    r = rng(seed)
    sh, sw = max(2, h // scale + 2), max(2, w // scale + 2)
    small = Image.fromarray(((r.random((sh, sw)) * 255).astype(np.uint8)))
    big = small.resize((w, h), Image.BICUBIC)
    return np.asarray(big, np.float32) / 127.5 - 1.0


def fine_noise(h, w, seed, blur=0.6):
    r = rng(seed)
    im = Image.fromarray((r.random((h, w)) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(im, np.float32) / 127.5 - 1.0


def to_img(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def save(im, name, colors=None):
    if colors:
        im = im.convert("RGB").quantize(colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")
    p = os.path.join(OUT, "skee_%s.png" % name)
    im.save(p, optimize=True)
    return p


def scratches(d, w, h, n, seed, col, length=(10, 60), width=1, angle=None):
    r = random.Random(seed)
    for _ in range(n):
        x, y = r.uniform(0, w), r.uniform(0, h)
        a = angle if angle is not None else r.uniform(0, math.pi)
        a += r.uniform(-0.25, 0.25)
        L = r.uniform(*length)
        d.line([(x, y), (x + math.cos(a) * L, y + math.sin(a) * L)], fill=col, width=width)


# ---------------------------------------------------------------- side panel
def paint_side():
    W, H = 1024, 512
    def P(z, y):
        return (z / SIDE_Z * W, (SIDE_Y - y) / SIDE_Y * H)
    base = np.zeros((H, W, 3), np.float32)
    red = np.array([168, 24, 22], np.float32)
    n1 = smooth_noise(H, W, 40, 11)[..., None]
    n2 = fine_noise(H, W, 12)[..., None]
    base[:] = red * (1.0 + 0.05 * n1 + 0.025 * n2)
    # soft vertical light falloff and grime toward the floor
    yy = np.linspace(0, 1, H)[:, None, None]
    base *= 1.0 - 0.18 * np.clip((yy - 0.62) / 0.38, 0, 1) ** 1.5
    im = to_img(base)
    d = ImageDraw.Draw(im, "RGBA")
    # original side decal near the scoring end: a rolling ball with speed streaks and stars
    def ln(z0, y0, z1, y1, col, wdt):
        d.line([P(z0, y0), P(z1, y1)], fill=col, width=wdt)
    # yellow pinstripe under the rail line, following the incline
    for off, col, wdt in ((0.045, (236, 186, 30, 255), 5), (0.065, (20, 14, 12, 200), 2)):
        pts = [P(0.0, 0.90 - off), P(0.32, 0.90 - off), P(2.18, 1.1734 - off), P(2.26, 1.36 - off), P(3.08, 1.48 - off)]
        d.line(pts, fill=col, width=wdt, joint="curve")
    # streaks
    for i, (y, L) in enumerate(((0.95, 1.05), (0.88, 1.30), (0.81, 0.95), (0.74, 1.15))):
        z1 = 2.55
        ln(z1 - L, y, z1, y, (240, 196, 40, 230 - i * 25), 9 - i)
    # ball (cream circle with a highlight) and stars
    cx, cy = P(2.70, 0.86)
    rr = 54
    d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(232, 206, 150, 255), outline=(30, 20, 14, 255), width=4)
    d.ellipse([cx - rr * 0.55, cy - rr * 0.6, cx - rr * 0.05, cy - rr * 0.15], fill=(250, 236, 200, 200))
    def star(x, y, r1, col, rot=0.0):
        pts = []
        for k in range(10):
            a = rot + k * math.pi / 5 - math.pi / 2
            r_ = r1 if k % 2 == 0 else r1 * 0.42
            pts.append((x + math.cos(a) * r_, y + math.sin(a) * r_))
        d.polygon(pts, fill=col)
    for z, y, r1 in ((2.35, 1.18, 22), (2.95, 1.16, 16), (2.18, 0.60, 14), (2.92, 0.58, 26)):
        x, y_ = P(z, y)
        star(x, y_, r1, (250, 214, 50, 240), 0.2)
    # (the TICKETS lettering is a separate decal, skee_sidetext.png, so it reads right on both sides)
    im = im.filter(ImageFilter.GaussianBlur(0.5))
    a = np.asarray(im, np.float32)
    # fade the decal colours (sun / age), a few lighter abrasions and scuffs
    fade = 0.55 + 0.45 * (0.5 + 0.5 * smooth_noise(H, W, 90, 13))[..., None]
    a = a * (0.85 + 0.15 * fade)
    d2 = ImageDraw.Draw(im := to_img(a), "RGBA")
    # kick marks along the bottom of the front section (shoes, carts, vacuum)
    r = random.Random(14)
    for _ in range(140):
        z = r.uniform(0.0, 3.1)
        ybase = 0.28 if z < 2.18 else 0.0
        y = ybase + abs(r.gauss(0, 0.05))
        x, yp = P(z, y)
        L = r.uniform(6, 30)
        d2.line([(x, yp), (x + L, yp + r.uniform(-3, 3))], fill=(20, 10, 10, r.randint(40, 110)), width=r.randint(1, 3))
    scratches(d2, W, H, 90, 15, (230, 170, 160, 50), (6, 40))
    scratches(d2, W, H, 40, 16, (50, 10, 10, 70), (10, 70))
    # black toe kick on the back section and black T-molding / aluminium corner on edges
    d2.polygon([P(2.18, 0.0), P(3.12, 0.0), P(3.12, 0.07), P(2.18, 0.07)], fill=(22, 18, 18, 255))
    pts = [P(z, y) for z, y in SIDE_OUTLINE]
    d2.line(pts + [pts[0]], fill=(18, 16, 16, 255), width=6)
    # aluminium front-corner angle (as on the reference alleys)
    d2.polygon([P(0, 0.28), P(0.05, 0.28), P(0.05, 0.90), P(0, 0.90)], fill=(170, 170, 168, 255))
    d2.line([P(0.05, 0.28), P(0.05, 0.90)], fill=(90, 90, 90, 255), width=2)
    for y in (0.36, 0.62, 0.84):
        x, yp = P(0.025, y)
        d2.ellipse([x - 3, yp - 3, x + 3, yp + 3], fill=(110, 110, 110, 255))
    # chips in the laminate showing particle board at corners
    r = random.Random(17)
    for z, y in ((0.0, 0.29), (2.18, 0.01), (3.11, 0.02), (3.11, 1.50), (2.31, 1.39), (0.33, 0.89)):
        x, yp = P(z, y)
        for _ in range(3):
            dx, dy = r.uniform(-12, 12), r.uniform(-8, 8)
            d2.ellipse([x + dx - 5, yp + dy - 3, x + dx + 5, yp + dy + 3], fill=(150, 120, 80, 200))
    return save(im, "side")


# ---------------------------------------------------------------- side lettering decal (RGBA, 512x128 for 0.70 x 0.175 m)
def paint_sidetext():
    W, H = 512, 128
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = font(F_BLACK_IT, 104)
    bb = d.textbbox((0, 0), "TICKETS", font=f)
    x, y = (W - (bb[2] - bb[0])) / 2 - bb[0], (H - (bb[3] - bb[1])) / 2 - bb[1]
    d.text((x + 5, y + 5), "TICKETS", font=f, fill=(30, 6, 6, 160))
    d.text((x, y), "TICKETS", font=f, fill=(246, 240, 228, 255), stroke_width=3, stroke_fill=(250, 200, 40, 255))
    a = np.asarray(im, np.float32)
    # worn vinyl: speckled loss of the letters, more at the bottom (kicked), and an overall fade
    loss = 0.5 + 0.5 * smooth_noise(H, W, 6, 18)
    yy = np.linspace(0, 1, H)[:, None]
    keep = np.clip(1.25 - loss * (0.45 + 0.5 * yy), 0, 1)
    a[..., 3] *= keep * 0.92
    a[..., :3] = a[..., :3] * 0.9 + 10
    return save(Image.fromarray(a.astype(np.uint8), "RGBA"), "sidetext")


# ---------------------------------------------------------------- front face (x -0.38..0.38, y 0.28..0.80)
FRONT_W, FRONT_H = 512, 352
def fpx(x, y):
    return ((x + 0.38) / 0.76 * FRONT_W, (0.80 - y) / 0.52 * FRONT_H)

COIN_DOOR = (-0.31, 0.36, -0.07, 0.70)        # x0, y0, x1, y1 metres
TICKET_SLOT = (0.12, 0.575, 0.28, 0.605)
COIN_LAMPS = [(-0.245, 0.585), (-0.135, 0.585)]  # centres of the lit coin entries


def paint_front():
    W, H = FRONT_W, FRONT_H
    red = np.array([166, 23, 21], np.float32)
    a = red * (1.0 + 0.05 * smooth_noise(H, W, 30, 21)[..., None] + 0.025 * fine_noise(H, W, 22)[..., None])
    yy = np.linspace(0, 1, H)[:, None, None]
    a *= 1.0 - 0.25 * np.clip((yy - 0.7) / 0.3, 0, 1)
    im = to_img(a)
    d = ImageDraw.Draw(im, "RGBA")
    # yellow pinstripe near the top and a black kick plate at the bottom
    d.rectangle([0, 10, W, 15], fill=(236, 186, 30, 255))
    x0, y0 = fpx(-0.38, 0.34)
    d.rectangle([0, y0, W, H], fill=(24, 20, 20, 255))
    # coin door: grey steel, two token entries with lit inserts, two return buttons, lock
    cx0, cy0 = fpx(COIN_DOOR[0], COIN_DOOR[3])
    cx1, cy1 = fpx(COIN_DOOR[2], COIN_DOOR[1])
    d.rectangle([cx0, cy0, cx1, cy1], fill=(58, 60, 64, 255), outline=(20, 20, 22, 255), width=3)
    d.rectangle([cx0 + 8, cy0 + 8, cx1 - 8, cy1 - 8], outline=(90, 92, 96, 255), width=2)
    for lx, ly in COIN_LAMPS:
        px, py = fpx(lx, ly)
        d.rounded_rectangle([px - 22, py - 34, px + 22, py + 34], 6, fill=(30, 30, 32, 255), outline=(120, 120, 124, 255), width=2)
        d.rectangle([px - 14, py - 26, px + 14, py + 8], fill=(200, 60, 30, 255))     # lit insert (lamp quad sits here)
        d.rectangle([px - 2, py - 22, px + 2, py + 4], fill=(30, 10, 8, 255))          # slot
        d.ellipse([px - 9, py + 13, px + 9, py + 31], fill=(150, 150, 154, 255), outline=(40, 40, 40, 255), width=2)  # return button
    # lock
    lx, ly = fpx(-0.19, 0.42)
    d.ellipse([lx - 11, ly - 11, lx + 11, ly + 11], fill=(175, 160, 110, 255), outline=(40, 36, 30, 255), width=2)
    d.rectangle([lx - 2, ly - 7, lx + 2, ly + 7], fill=(40, 34, 26, 255))
    # token sticker on the coin door (faded)
    sx, sy = fpx(-0.30, 0.685)
    d.rectangle([sx + 10, sy, sx + 160, sy + 22], fill=(236, 214, 120, 235))
    d.text((sx + 16, sy + 2), "TOKENS ONLY", font=font(F_COND, 16), fill=(60, 30, 10, 255))
    lx, ly = fpx(-0.30, 0.47)
    d.text((lx + 16, ly), "1 TOKEN", font=font(F_COND, 15), fill=(220, 220, 220, 210))
    # ticket dispenser slot: chrome bezel, black slot, label above
    tx0, ty0 = fpx(TICKET_SLOT[0], TICKET_SLOT[3])
    tx1, ty1 = fpx(TICKET_SLOT[2], TICKET_SLOT[1])
    d.rounded_rectangle([tx0 - 8, ty0 - 8, tx1 + 8, ty1 + 8], 5, fill=(185, 186, 188, 255), outline=(60, 60, 60, 255), width=2)
    d.rectangle([tx0 + 4, ty0 + 3, tx1 - 4, ty1 - 3], fill=(8, 8, 8, 255))
    lx, ly = fpx(0.12, 0.66)
    d.rectangle([lx - 6, ly - 4, lx + 116, ly + 26], fill=(18, 16, 16, 230))
    d.text((lx, ly - 1), "TICKETS", font=font(F_BLACK, 24), fill=(244, 196, 40, 255))
    # instruction card (yellowed, a corner peeling) under the ticket slot
    ix0, iy0 = fpx(0.04, 0.53)
    ix1, iy1 = fpx(0.34, 0.37)
    d.rectangle([ix0, iy0, ix1, iy1], fill=(226, 218, 190, 240), outline=(80, 70, 50, 255), width=2)
    f1, f2 = font(F_BLACK, 15), font(F_SEMI, 11)
    d.text((ix0 + 10, iy0 + 6), "HOW TO PLAY", font=f1, fill=(150, 20, 18, 255))
    for i, t in enumerate(("1. INSERT TOKEN", "2. ROLL BALLS UP THE LANE", "3. SCORE IN THE RINGS",
                           "4. TICKETS PAID ON SCORE", "100 POCKETS = BONUS")):
        d.text((ix0 + 10, iy0 + 28 + i * 14), t, font=f2, fill=(40, 34, 28, 255))
    d.polygon([(ix1, iy1), (ix1 - 18, iy1), (ix1, iy1 - 14)], fill=(140, 120, 90, 255))
    # small serial plate
    px, py = fpx(0.26, 0.355)
    d.rectangle([px - 14, py, px + 40, py + 14], fill=(178, 168, 140, 255))
    d.text((px - 11, py + 2), "SN 4417-93", font=font(F_COND, 8), fill=(40, 40, 40, 255))
    im = im.filter(ImageFilter.GaussianBlur(0.45))
    d = ImageDraw.Draw(im, "RGBA")
    # wear: knee scuffs, finger grime around the slot and coin door, scratches
    r = random.Random(23)
    for _ in range(70):
        x, y = r.uniform(0, W), r.uniform(H * 0.55, H * 0.85)
        d.line([(x, y), (x + r.uniform(8, 30), y + r.uniform(-2, 2))], fill=(20, 8, 8, r.randint(30, 90)), width=r.randint(1, 3))
    scratches(d, W, H, 50, 24, (240, 200, 190, 45), (5, 30))
    for (cx, cy, rad) in ((fpx(0.2, 0.59)) + (40,), (fpx(-0.19, 0.53)) + (60,)):
        for _ in range(30):
            x, y = cx + r.gauss(0, rad * 0.6), cy + r.gauss(0, rad * 0.4)
            d.ellipse([x - 4, y - 3, x + 4, y + 3], fill=(40, 20, 16, 24))
    return save(im, "front")


# ---------------------------------------------------------------- lane (dark laminate over cork-ish playfield), hump on top 13%
def paint_lane():
    W, H = 256, 1024
    base = np.array([38, 34, 31], np.float32)
    n = 0.10 * smooth_noise(H, W, 24, 31) + 0.08 * fine_noise(H, W, 32, 0.5) + 0.05 * smooth_noise(H, W, 6, 33)
    a = base * (1.0 + n[..., None])
    xx = np.linspace(-1, 1, W)[None, :]
    yy = np.linspace(0, 1, H)[:, None]
    # polished central path where the balls run (slightly lighter, higher sheen in the albedo)
    path = np.exp(-(xx / 0.45) ** 2) * (0.35 + 0.65 * yy)
    a *= (1.0 + 0.12 * path)[..., None]
    # dust along the rails
    edge = np.clip((np.abs(xx) - 0.82) / 0.18, 0, 1)
    a = a * (1 - 0.3 * edge[..., None]) + np.array([90, 84, 76]) * 0.3 * edge[..., None]
    im = to_img(a)
    d = ImageDraw.Draw(im, "RGBA")
    r = random.Random(34)
    # long faint ball tracks
    for _ in range(60):
        x = r.gauss(W / 2, W * 0.18)
        y0 = r.uniform(H * 0.13, H)
        L = r.uniform(80, 500)
        d.line([(x, y0), (x + r.uniform(-12, 12), y0 - L)], fill=(120, 112, 100, r.randint(5, 14)), width=r.randint(2, 6))
    # impact scuffs near the front where balls are dropped, scratches, a few chips
    for _ in range(90):
        x, y = r.gauss(W / 2, W * 0.22), r.uniform(H * 0.70, H)
        d.ellipse([x - 3, y - 2, x + 3, y + 2], fill=(110, 100, 90, r.randint(25, 70)))
    scratches(d, W, H, 120, 35, (130, 120, 108, 35), (8, 60), 1, math.pi / 2)
    for _ in range(12):
        x, y = r.uniform(0, W), r.uniform(H * 0.15, H)
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(140, 120, 90, 120))
    # hump (v < 0.13): polished hardwood with a worn lip
    hn = 0.10 * smooth_noise(133, W, 12, 36) + 0.05 * fine_noise(133, W, 37, 0.5)
    grain = 0.06 * np.sin(np.linspace(0, 55, W)[None, :] + 4 * smooth_noise(133, W, 30, 38))
    hump = to_img(np.array([52, 38, 28], np.float32) * (1 + hn + grain)[..., None])
    hd = ImageDraw.Draw(hump, "RGBA")
    for i in range(40):
        x = r.uniform(0, W)
        hd.line([(x, 0), (x + r.uniform(-6, 6), 133)], fill=(30, 20, 12, 40), width=1)
    for i in range(30):   # ball strike marks on the ramp
        x, y = r.gauss(W / 2, W * 0.2), r.uniform(10, 120)
        hd.ellipse([x - 3, y - 1.5, x + 3, y + 1.5], fill=(100, 84, 68, 40))
    hd.rectangle([0, 0, W, 8], fill=(120, 96, 70, 140))     # worn lip
    hd.rectangle([0, 128, W, 133], fill=(20, 16, 14, 255))   # seam to lane
    im.paste(hump, (0, 0))
    return save(im.filter(ImageFilter.GaussianBlur(0.4)), "lane")


# ---------------------------------------------------------------- rail cap (yellow), v=0 back, v=1 front
def paint_rail():
    W, H = 64, 1024
    yel = np.array([226, 176, 26], np.float32)
    a = yel * (1 + 0.05 * smooth_noise(H, W, 16, 41)[..., None] + 0.03 * fine_noise(H, W, 42)[..., None])
    yy = np.linspace(0, 1, H)[:, None]
    xx = np.linspace(-1, 1, W)[None, :]
    # hand wear toward the front: paint rubbed thin to grey primer / dark wood
    wear = np.clip((yy - 0.55) / 0.45, 0, 1) * (0.5 + 0.5 * smooth_noise(H, W, 10, 43)) * (1 - 0.6 * np.abs(xx))
    wear = np.clip(wear * 1.6 - 0.35, 0, 1)
    a = a * (1 - wear[..., None]) + np.array([92, 78, 58], np.float32) * wear[..., None]
    # grime on edges
    a *= (1 - 0.25 * (np.abs(xx) ** 6))[..., None]
    im = to_img(a)
    d = ImageDraw.Draw(im, "RGBA")
    scratches(d, W, H, 80, 44, (60, 40, 20, 70), (5, 40), 1, math.pi / 2)
    return save(im.filter(ImageFilter.GaussianBlur(0.4)), "rail")


# ---------------------------------------------------------------- scoring board (u 0..0.64 across, v 0..1.016 up the slope)
BOARD_W, BOARD_L = 0.64, 1.016
RINGS = [  # (label, rim centre u, rim centre v, rim radius, hole u, hole v, label du)
    ("10", 0.32, 0.40, 0.28, 0.32, 0.180, 0.135),
    ("20", 0.32, 0.44, 0.20, 0.32, 0.290, 0.100),
    ("30", 0.32, 0.47, 0.13, 0.32, 0.386, 0.078),
]
HOLES = [("40", 0.32, 0.49, 0.058), ("50", 0.32, 0.79, 0.058), ("100", 0.075, 0.875, 0.052), ("100", 0.565, 0.875, 0.052)]
HOLE_R = 0.046
BALL_R = 0.036


def paint_board():
    W, H = 512, 768
    def P(u, v):
        return (u / BOARD_W * W, (1 - v / BOARD_L) * H)
    def R(rm):
        return rm / BOARD_W * W
    a = np.array([22, 30, 66], np.float32) * (1 + 0.08 * smooth_noise(H, W, 30, 51)[..., None] + 0.03 * fine_noise(H, W, 52)[..., None])
    im = to_img(a)
    d = ImageDraw.Draw(im, "RGBA")
    # ring bands alternate deep blue / black, cream rims are 3D geometry (painted shadow ring here)
    band = [(18, 18, 22), (30, 44, 104), (18, 18, 22)]
    for (lab, cu, cv, rr, hu, hv, du), col in zip(RINGS, band):
        x, y = P(cu, cv)
        rp = R(rr)
        d.ellipse([x - rp, y - rp, x + rp, y + rp], fill=col + (255,))
    for lab, cu, cv, rr in HOLES:
        x, y = P(cu, cv)
        rp = R(rr + 0.012)
        d.ellipse([x - rp, y - rp, x + rp, y + rp], fill=(30, 44, 104, 255))
    # holes: dark throats with a soft lit lip
    def hole(u, v, rad):
        x, y = P(u, v)
        rp = R(rad)
        for k in range(8, 0, -1):
            t = k / 8
            c = int(6 + 26 * t)
            d.ellipse([x - rp * t, y - rp * t * 0.96, x + rp * t, y + rp * t * 0.96], fill=(c, c, c + 4, 255))
        d.ellipse([x - rp * 0.65, y - rp * 0.7, x + rp * 0.65, y + rp * 0.5], fill=(4, 4, 6, 255))
    for lab, cu, cv, rr, hu, hv, du in RINGS:
        hole(hu, hv, HOLE_R)
    for lab, cu, cv, rr in HOLES:
        hole(cu, cv, rr - 0.010)
    # painted score numbers (cream with dark outline) beside each hole
    def label(t, u, v, size):
        f = font(F_BLACK, size)
        x, y = P(u, v)
        bb = d.textbbox((0, 0), t, font=f)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        d.text((x - tw / 2 - bb[0], y - th / 2 - bb[1]), t, font=f, fill=(244, 230, 196, 255), stroke_width=2, stroke_fill=(10, 10, 14, 255))
    for (lab, cu, cv, rr, hu, hv, du), size in zip(RINGS, (40, 34, 24)):
        label(lab, hu - du, hv, size)
        label(lab, hu + du, hv, size)
    label("40", 0.32, 0.574, 22)
    label("50", 0.32, 0.900, 38)
    label("100", 0.075, 0.795, 26)
    label("100", 0.565, 0.795, 26)
    # bottom gutter lip and wear: ball strikes chip the paint at the hole lips and on the 10 band
    d.rectangle([0, H - 26, W, H], fill=(12, 12, 14, 255))
    im = im.filter(ImageFilter.GaussianBlur(0.6))
    d = ImageDraw.Draw(im, "RGBA")
    r = random.Random(53)
    for _ in range(260):
        u = r.uniform(0.03, 0.61)
        v = r.uniform(0.05, 0.95)
        x, y = P(u, v)
        d.ellipse([x - 2, y - 1.5, x + 2, y + 1.5], fill=(180, 170, 150, r.randint(30, 90)))
    scratches(d, W, H, 70, 54, (140, 140, 150, 40), (6, 30), 1, math.pi / 2)
    return save(im, "board")


# ---------------------------------------------------------------- marquee (backlit translucent art), 1024x640 for 0.76 x 0.475
MQ_W, MQ_H = 1024, 640
LED_BOX = (232, 214, 792, 354)     # px: where the LED quad sits on the marquee
NUM_BOX = (52, 46, 124, 118)       # px: lane number badge (separate quad, inside a yellow ring)


def paint_marquee():
    W, H = MQ_W, MQ_H
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = W / 2, H * 0.42
    ang = np.arctan2(yy - cy, xx - cx)
    rays = (np.sin(ang * 14) > 0).astype(np.float32)
    dist = np.hypot(xx - cx, yy - cy) / W
    top = np.array([40, 16, 96], np.float32)
    bot = np.array([8, 10, 40], np.float32)
    t = (yy / H)[..., None]
    a = top * (1 - t) + bot * t
    a += (rays * np.clip(0.8 - dist, 0, 1))[..., None] * np.array([60, 30, 90], np.float32)
    im = to_img(a)
    d = ImageDraw.Draw(im, "RGBA")
    # thin neon-ish border
    d.rounded_rectangle([12, 12, W - 12, H - 12], 26, outline=(250, 200, 40, 255), width=7)
    d.rounded_rectangle([24, 24, W - 24, H - 24], 20, outline=(230, 40, 120, 255), width=3)
    # stars
    def star(x, y, r1, col, rot=0.0):
        pts = []
        for k in range(10):
            ang_ = rot + k * math.pi / 5 - math.pi / 2
            r_ = r1 if k % 2 == 0 else r1 * 0.42
            pts.append((x + math.cos(ang_) * r_, y + math.sin(ang_) * r_))
        d.polygon(pts, fill=col)
    r = random.Random(61)
    for _ in range(26):
        x, y = r.uniform(40, W - 40), r.uniform(40, H - 40)
        if 200 < x < 830 and 60 < y < 520:
            continue
        star(x, y, r.uniform(7, 16), (255, 240, 180, 230), r.uniform(0, 1))
    star(W - 88, 82, 40, (255, 210, 40, 255), 0.1)
    # WINNER (small, top centre, under the beacon)
    f = font(F_BLACK, 40)
    bb = d.textbbox((0, 0), "WINNER", font=f)
    d.text(((W - (bb[2] - bb[0])) / 2, 34), "WINNER", font=f, fill=(255, 230, 90, 255), stroke_width=3, stroke_fill=(120, 10, 30, 255))
    # SCORE: chunky italic, yellow-to-orange fill with a red outline and dark drop
    f = font(F_BLACK_IT, 112)
    txt = "SCORE"
    bb = d.textbbox((0, 0), txt, font=f)
    tw = bb[2] - bb[0]
    tx, ty = (W - tw) / 2 - bb[0], 80 - bb[1]
    d.text((tx + 7, ty + 7), txt, font=f, fill=(0, 0, 0, 170), stroke_width=8, stroke_fill=(0, 0, 0, 170))
    d.text((tx, ty), txt, font=f, fill=(255, 255, 255, 255), stroke_width=8, stroke_fill=(200, 20, 30, 255))
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).text((tx, ty), txt, font=f, fill=255)
    grad = np.zeros((H, W, 3), np.float32)
    g = np.clip((yy - 80) / 110, 0, 1)[..., None]
    grad[:] = np.array([255, 246, 120], np.float32) * (1 - g) + np.array([255, 140, 20], np.float32) * g
    im.paste(to_img(grad), (0, 0), mask)
    d = ImageDraw.Draw(im, "RGBA")
    # LED window surround (the LED quad covers the inside), labels under it
    x0, y0, x1, y1 = LED_BOX
    d.rounded_rectangle([x0 - 14, y0 - 14, x1 + 14, y1 + 14], 10, fill=(12, 12, 14, 255), outline=(180, 180, 190, 255), width=4)
    d.rectangle([x0, y0, x1, y1], fill=(16, 2, 2, 255))
    fl = font(F_BOLD, 26)
    d.text((x0 + 120, y1 + 20), "POINTS", font=fl, fill=(255, 255, 255, 235))
    d.text((x1 - 120, y1 + 20), "BALLS", font=fl, fill=(255, 255, 255, 235))
    # TICKETS banner
    by0, by1 = 452, 560
    d.polygon([(110, by0), (W - 110, by0), (W - 80, (by0 + by1) / 2), (W - 110, by1), (110, by1), (80, (by0 + by1) / 2)],
              fill=(200, 24, 36, 255), outline=(255, 220, 60, 255))
    f = font(F_BLACK_IT, 82)
    txt = "TICKETS"
    bb = d.textbbox((0, 0), txt, font=f)
    d.text(((W - (bb[2] - bb[0])) / 2 - bb[0], (by0 + by1) / 2 - (bb[3] - bb[1]) / 2 - bb[1]), txt, font=f,
           fill=(255, 250, 235, 255), stroke_width=4, stroke_fill=(60, 0, 10, 255))
    star(150, (by0 + by1) / 2, 30, (255, 220, 50, 255))
    star(W - 150, (by0 + by1) / 2, 30, (255, 220, 50, 255))
    # number badge background (the number quad sits inside)
    nx0, ny0, nx1, ny1 = NUM_BOX
    ncx, ncy = (nx0 + nx1) / 2, (ny0 + ny1) / 2
    d.ellipse([ncx - 62, ncy - 62, ncx + 62, ncy + 62], fill=(255, 210, 40, 255))
    d.ellipse([ncx - 52, ncy - 52, ncx + 52, ncy + 52], fill=(20, 16, 60, 255))
    im = im.filter(ImageFilter.GaussianBlur(0.7))
    # backlit plastic: fluorescent tubes behind give a brighter middle band, darker corners;
    # aged plastic and a little dust
    a = np.asarray(im, np.float32)
    tube = 0.78 + 0.22 * np.exp(-((yy - H * 0.30) / (H * 0.35)) ** 2) + 0.12 * np.exp(-((yy - H * 0.75) / (H * 0.2)) ** 2)
    vign = 1 - 0.25 * (np.abs(xx / W - 0.5) * 2) ** 3
    a = a * (tube * vign)[..., None]
    a = a * 0.94 + np.array([12, 10, 4], np.float32)   # slight yellowing
    im = to_img(a)
    d = ImageDraw.Draw(im, "RGBA")
    scratches(d, W, H, 40, 62, (255, 255, 255, 25), (10, 60))
    return save(im, "marquee")


# ---------------------------------------------------------------- red 7-segment LED rows (one per lane number)
LED_ROWS = [("270", "4"), ("150", "7"), (" 90", "8"), ("340", "1")]


def seg_polys(x, y, w, h, t):
    """7 segment polygons (a..g) for a digit cell at x,y of size w,h, stroke t, italic slant."""
    s = 0.12 * w
    def sk(px, py):
        return (px + s * (1 - (py - y) / h), py)
    hw = t / 2
    segs = {}
    def hseg(cy, x0, x1):
        return [sk(x0 + hw, cy), sk(x0 + t, cy - hw), sk(x1 - t, cy - hw), sk(x1 - hw, cy), sk(x1 - t, cy + hw), sk(x0 + t, cy + hw)]
    def vseg(cx, y0, y1):
        return [sk(cx, y0 + hw), sk(cx + hw, y0 + t), sk(cx + hw, y1 - t), sk(cx, y1 - hw), sk(cx - hw, y1 - t), sk(cx - hw, y0 + t)]
    x0, x1, y0, ym, y1 = x + hw, x + w - hw, y + hw, y + h / 2, y + h - hw
    segs["a"] = hseg(y0, x0, x1)
    segs["g"] = hseg(ym, x0, x1)
    segs["d"] = hseg(y1, x0, x1)
    segs["f"] = vseg(x0, y0, ym)
    segs["b"] = vseg(x1, y0, ym)
    segs["e"] = vseg(x0, ym, y1)
    segs["c"] = vseg(x1, ym, y1)
    return segs


DIG = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc",
       "7": "abc", "8": "abcdefg", "9": "abcdfg", " ": ""}


def paint_led():
    W, RH = 512, 128
    im = Image.new("RGB", (W, RH * 4), (14, 2, 2))
    for row, (score, balls) in enumerate(LED_ROWS):
        lit = Image.new("RGB", (W, RH), (0, 0, 0))
        dl = ImageDraw.Draw(lit)
        base = Image.new("RGB", (W, RH), (16, 2, 2))
        db = ImageDraw.Draw(base)
        cells = [(30 + i * 92, score[i]) for i in range(3)] + [(400, balls)]
        for x, ch in cells:
            segs = seg_polys(x, 16, 70, 96, 13)
            for k, poly in segs.items():
                db.polygon(poly, fill=(36, 6, 5))
                if k in DIG[ch]:
                    dl.polygon(poly, fill=(255, 40, 18))
        glow = lit.filter(ImageFilter.GaussianBlur(6))
        a = np.asarray(base, np.float32) + np.asarray(lit, np.float32) * 0.95 + np.asarray(glow, np.float32) * 0.6
        # smoked plexi: faint horizontal reflection band
        yy = np.linspace(0, 1, RH)[:, None, None]
        a += 10 * np.exp(-((yy - 0.2) / 0.08) ** 2)
        im.paste(to_img(a), (0, row * RH))
    return save(im, "led")


# ---------------------------------------------------------------- lane number badges 1..4 (64x64 cells)
def paint_num():
    im = Image.new("RGB", (256, 64), (20, 16, 60))
    d = ImageDraw.Draw(im)
    f = font(F_BLACK, 54)
    for i in range(4):
        cx = i * 64 + 32
        t = str(i + 1)
        bb = d.textbbox((0, 0), t, font=f)
        d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], 32 - (bb[3] - bb[1]) / 2 - bb[1]), t, font=f, fill=(255, 236, 120))
    return save(im.filter(ImageFilter.GaussianBlur(0.4)), "num")


# ---------------------------------------------------------------- brushed aluminium (tileable)
def paint_metal():
    W = H = 256
    r = rng(71)
    streak = r.random((1, W)).repeat(H, 0)
    streak = np.asarray(Image.fromarray((streak * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur((0.0, 0.0))), np.float32) / 255
    rows = r.random((H, 1)) * 0.3
    a = 170 + 26 * (streak - 0.5) + 30 * (rows - 0.15) + 8 * fine_noise(H, W, 72, 0.7)
    a = np.stack([a, a * 1.0, a * 1.02], -1)
    im = to_img(a.transpose(1, 0, 2))   # streaks along u
    d = ImageDraw.Draw(im, "RGBA")
    scratches(d, W, H, 50, 73, (90, 90, 90, 60), (8, 50))
    for _ in range(8):
        x, y = random.Random(_).uniform(0, W), random.Random(_ + 9).uniform(0, H)
        d.ellipse([x - 6, y - 4, x + 6, y + 4], fill=(110, 110, 110, 50))
    return save(im, "metal")


# ---------------------------------------------------------------- welded wire mesh, RGBA, tile = 10 cm (4 x 2.5 cm cells)
def paint_mesh():
    S = 128
    a = np.zeros((S, S, 4), np.float32)
    wire = np.zeros((S, S), np.float32)
    for k in range(4):
        c = k * 32 + 16
        for o, wgt in ((-1, 0.6), (0, 1.0), (1, 0.6)):
            wire[:, (c + o) % S] = np.maximum(wire[:, (c + o) % S], wgt)
            wire[(c + o) % S, :] = np.maximum(wire[(c + o) % S, :], wgt)
    a[..., 0] = 78; a[..., 1] = 80; a[..., 2] = 84
    a[..., 3] = wire * 255
    # weld points brighter
    for i in range(4):
        for j in range(4):
            x, y = i * 32 + 16, j * 32 + 16
            a[y - 1:y + 2, x - 1:x + 2, :3] = 110
    return save(Image.fromarray(a.astype(np.uint8), "RGBA"), "mesh")


# ---------------------------------------------------------------- tickets strip (32 x 256 for 0.028 x 0.22 m)
def paint_ticket():
    W, H = 32, 256
    im = Image.new("RGB", (W, H), (240, 132, 36))
    d = ImageDraw.Draw(im)
    step = 0.044 / 0.22 * H
    f = font(F_COND, 9)
    for i in range(6):
        y = i * step
        for x in range(0, W, 3):
            d.point((x, int(y)), fill=(170, 80, 20))
        d.rectangle([3, y + 4, W - 4, y + step - 4], outline=(200, 90, 20))
        txt = Image.new("RGBA", (int(step) - 10, 14), (0, 0, 0, 0))
        ImageDraw.Draw(txt).text((2, 1), "TICKET", font=f, fill=(120, 40, 10, 255))
        txt = txt.rotate(90, expand=True)
        im.paste(txt, (int(W / 2 - 7), int(y + 6)), txt)
    a = np.asarray(im, np.float32) * (1 + 0.04 * fine_noise(H, W, 81)[..., None])
    return save(to_img(a), "ticket")


# ---------------------------------------------------------------- wooden ball (equirect 128x64)
def paint_ball():
    W, H = 128, 64
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    grain = np.sin(yy * 0.9 + 3 * smooth_noise(H, W, 8, 91)) * 0.5 + 0.5
    base = np.array([196, 150, 98], np.float32)
    a = base * (0.86 + 0.12 * grain[..., None] + 0.05 * fine_noise(H, W, 92)[..., None])
    # grime band and dings from years of rolling
    a *= (0.92 - 0.08 * np.abs(np.sin(xx / W * math.pi * 3)))[..., None]
    im = to_img(a)
    d = ImageDraw.Draw(im, "RGBA")
    r = random.Random(93)
    for _ in range(40):
        x, y = r.uniform(0, W), r.uniform(0, H)
        d.ellipse([x - 1.5, y - 1, x + 1.5, y + 1], fill=(70, 44, 24, 120))
    return save(im, "ball")


def main():
    os.makedirs(OUT, exist_ok=True)
    random.seed(1995)
    paths = [paint_side(), paint_sidetext(), paint_front(), paint_lane(), paint_rail(), paint_board(), paint_marquee(),
             paint_led(), paint_num(), paint_metal(), paint_mesh(), paint_ticket(), paint_ball()]
    tot = 0
    for p in paths:
        s = os.path.getsize(p)
        tot += s
        print("%-40s %7d" % (os.path.basename(p), s))
    print("total", tot)


if __name__ == "__main__":
    main()
