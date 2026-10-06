"""Paints the textures of the Pocket Change motion-ride cabinet (ride.gd) into tex/pc/ride_*.png.

The machine is the TYPE that stood in mid-90s arcades: a deluxe enclosed two-seat motion
cabin with a dinosaur-safari light-gun game. Everything here is original: the invented
title "TALON CREEK", the painted jungle, the generic theropod and the safari jeep.
No real game's title, logo, characters or artwork.

Every texture is drawn at the physical size of the face it covers (see the sizes noted
per function). Seeded: re-running reproduces the same files.
Run from the project folder: python3 tools/stores/pocket_change/paint_ride.py
"""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(PROJ, "tex", "pc")
os.makedirs(OUT, exist_ok=True)

F_LOGO = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"
F_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_COND = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"
F_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf"
F_HEAVY = "/usr/share/fonts/opentype/inter/Inter-Black.otf"

PAINT = (28, 58, 44)       # the cabin's deep jungle-green fibreglass


def R(seed):
    return random.Random(seed)


def save(im, name, colors=None):
    p = os.path.join(OUT, name)
    if colors:
        if im.mode == "RGBA":
            im = im.quantize(colors=colors, method=Image.FASTOCTREE, dither=Image.Dither.NONE)
        else:
            im = im.quantize(colors=colors, method=Image.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(p, optimize=True)
    print("%-22s %-10s %6.0f KB" % (name, "%dx%d" % im.size, os.path.getsize(p) / 1024))


def gamma(im, g):
    """Darkens the mid-tones of a lit picture (screens, marquees) so it keeps its colour
    under the arcade's glow instead of washing out to white."""
    a = np.asarray(im.convert("RGB")).astype(np.float32) / 255.0
    return Image.fromarray((np.power(a, g) * 255).clip(0, 255).astype(np.uint8))


def font(path, size):
    return ImageFont.truetype(path, size)


def noise(w, h, seed, scale=1.0):
    """Smooth noise in [0, 1], `scale` = feature size in px. Built in the frequency domain,
    so it tiles seamlessly (the tiled materials need that)."""
    rng = np.random.default_rng(seed)
    wn = rng.standard_normal((h, w))
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    sig = 1.0 / (2.5 * max(scale, 0.5))
    lp = np.exp(-(fx ** 2 + fy ** 2) / (2 * sig ** 2))
    a = np.real(np.fft.ifft2(np.fft.fft2(wn) * lp))
    a = (a - a.mean()) / (a.std() + 1e-6)
    return np.clip(0.5 + a * 0.18, 0, 1).astype(np.float32)


def fbm(w, h, seed, base=64.0, octaves=4):
    a = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        a += noise(w, h, seed + o * 17, max(1.0, base / (2 ** o))) * amp
        tot += amp
        amp *= 0.5
    return a / tot


def grad_v(w, h, stops):
    """Vertical gradient; stops = [(t, (r,g,b)), ...] with t in [0, 1]."""
    a = np.zeros((h, w, 3), np.float32)
    ts = np.linspace(0, 1, h)
    for c in range(3):
        col = np.interp(ts, [s[0] for s in stops], [s[1][c] for s in stops])
        a[:, :, c] = col[:, None]
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def mul(im, arr):
    a = np.asarray(im).astype(np.float32)
    if a.ndim == 3:
        a[:, :, :3] *= arr[:, :, None]
    else:
        a *= arr
    return Image.fromarray(a.clip(0, 255).astype(np.uint8), im.mode)


def brushwork(im, seed, n, lmin=5, lmax=16, wmin=2, wmax=5, jitter=10, angle=0.0, spread=0.9):
    """Painterly pass: short strokes in the colour found under them."""
    rng = R(seed)
    src = im.copy()
    px = src.load()
    d = ImageDraw.Draw(im)
    w, h = im.size
    for _ in range(n):
        x, y = rng.uniform(0, w - 1), rng.uniform(0, h - 1)
        c = px[int(x), int(y)]
        c = tuple(max(0, min(255, int(v + rng.uniform(-jitter, jitter)))) for v in c[:3])
        a = angle + rng.uniform(-spread, spread)
        L = rng.uniform(lmin, lmax)
        dx, dy = math.cos(a) * L * 0.5, math.sin(a) * L * 0.5
        d.line([(x - dx, y - dy), (x + dx, y + dy)], fill=c, width=int(rng.uniform(wmin, wmax)))
    return im


def text_c(d, xy, s, f, fill, anchor="mm", **kw):
    d.text(xy, s, font=f, fill=fill, anchor=anchor, **kw)


# ------------------------------------------------------------------ logo
def logo(w, h, seed=3, sub=True):
    """The invented title, 90s-style: claw slashes, gradient letters, double outline."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    s = h / 256.0
    # three claw slashes behind the letters
    sl = Image.new("L", (w, h), 0)
    ds = ImageDraw.Draw(sl)
    for i in range(3):
        x0 = w * (0.60 + i * 0.07)
        pts = []
        for t in np.linspace(0, 1, 24):
            x = x0 - t * w * 0.16 + math.sin(t * 3.1) * 6 * s
            y = h * 0.04 + t * h * 0.62
            wd = (math.sin(t * math.pi) ** 0.7) * 15 * s + 1
            pts.append((x, y, wd))
        for (x, y, wd) in pts:
            ds.ellipse([x - wd, y - wd * 0.6, x + wd, y + wd * 0.6], fill=255)
    sl = sl.filter(ImageFilter.GaussianBlur(1.2 * s))
    slash = Image.new("RGBA", (w, h), (120, 18, 14, 255))
    im.paste(slash, (0, 0), sl)
    # title letters
    txt = "TALON CREEK"
    fs = int(150 * s)
    f = font(F_LOGO, fs)
    while f.getbbox(txt)[2] - f.getbbox(txt)[0] > w * 0.94:
        fs -= 2
        f = font(F_LOGO, fs)
    cy = h * (0.40 if sub else 0.5)
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).text((w / 2, cy), txt, font=f, fill=255, anchor="mm")
    # outer cream outline, inner black outline, drop shadow
    outer = Image.new("L", (w, h), 0)
    ImageDraw.Draw(outer).text((w / 2, cy), txt, font=f, fill=255, anchor="mm", stroke_width=int(12 * s))
    inner = Image.new("L", (w, h), 0)
    ImageDraw.Draw(inner).text((w / 2, cy), txt, font=f, fill=255, anchor="mm", stroke_width=int(6 * s))
    shadow = outer.filter(ImageFilter.GaussianBlur(5 * s))
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 200))
    im.paste(sh, (int(7 * s), int(8 * s)), shadow)
    im.paste(Image.new("RGBA", (w, h), (246, 232, 196, 255)), (0, 0), outer)
    im.paste(Image.new("RGBA", (w, h), (24, 14, 8, 255)), (0, 0), inner)
    bb = m.getbbox()
    g = grad_v(w, h, [(0, (255, 246, 150)), (bb[1] / h, (255, 236, 90)), ((bb[1] + bb[3]) / 2 / h, (255, 150, 30)), (bb[3] / h, (196, 40, 18)), (1, (150, 20, 10))])
    # a little bark/stone texture in the fill
    tx = fbm(w, h, seed, 18, 3)
    g = mul(g, 0.82 + 0.3 * tx)
    im.paste(g.convert("RGBA"), (0, 0), m)
    # a highlight along the letter tops
    hl = ImageChops.subtract(m, ImageChops.offset(m, 0, int(4 * s))).filter(ImageFilter.GaussianBlur(1))
    im.paste(Image.new("RGBA", (w, h), (255, 255, 230, 255)), (0, 0), hl.point(lambda v: int(v * 0.8)))
    if sub:
        # green ribbon with the subtitle
        ry0, ry1 = h * 0.70, h * 0.93
        rib = Image.new("L", (w, h), 0)
        dr = ImageDraw.Draw(rib)
        dr.polygon([(w * 0.17, ry0), (w * 0.83, ry0), (w * 0.80, (ry0 + ry1) / 2), (w * 0.83, ry1), (w * 0.17, ry1), (w * 0.20, (ry0 + ry1) / 2)], fill=255)
        rib_o = rib.filter(ImageFilter.MaxFilter(int(5 * s) | 1))
        im.paste(Image.new("RGBA", (w, h), (20, 12, 6, 255)), (0, 0), rib_o)
        gr = grad_v(w, h, [(0, (60, 150, 70)), (ry0 / h, (90, 180, 80)), (ry1 / h, (24, 90, 40)), (1, (20, 70, 30))])
        im.paste(gr.convert("RGBA"), (0, 0), rib)
        f2 = font(F_HEAVY, int(34 * s))
        ImageDraw.Draw(im).text((w / 2, (ry0 + ry1) / 2), "D I N O S A U R   S A F A R I", font=f2, fill=(255, 244, 200), anchor="mm",
                                stroke_width=int(2 * s), stroke_fill=(16, 40, 18))
    return im


# ------------------------------------------------------------------ painted scene parts
def theropod_poly():
    """A generic big theropod in side view facing right, in a 1000 x 500 box."""
    return [(30, 262), (120, 236), (230, 200), (330, 166), (420, 140), (500, 132), (570, 146), (620, 160),
            (660, 146), (700, 118), (735, 98), (790, 88), (845, 96), (885, 112), (905, 126), (900, 136),
            (870, 140), (830, 150), (790, 160), (772, 168), (800, 182), (850, 196), (874, 206), (868, 216),
            (820, 222), (770, 220), (735, 214), (700, 232), (668, 262), (650, 290), (660, 300), (690, 318),
            (702, 336), (690, 334), (668, 322), (640, 312), (606, 320), (572, 330), (576, 360), (566, 392),
            (540, 420), (528, 444), (552, 470), (590, 480), (602, 490), (500, 492), (494, 478), (502, 452),
            (498, 432), (520, 400), (504, 372), (466, 350), (420, 330), (300, 298), (190, 284), (100, 276)]


def far_leg_poly():
    return [(470, 330), (480, 372), (452, 410), (432, 440), (444, 468), (476, 480), (484, 490), (400, 490),
            (396, 476), (404, 448), (402, 426), (420, 396), (406, 360), (420, 334)]


def far_arm_poly():
    return [(630, 296), (650, 318), (664, 334), (652, 334), (628, 316), (612, 304)]


def map_pts(pts, x0, y0, sx, sy, flip=False):
    if flip:
        return [(x0 + (1000 - p[0]) * sx, y0 + p[1] * sy) for p in pts]
    return [(x0 + p[0] * sx, y0 + p[1] * sy) for p in pts]


def paint_dino(im, x0, y0, sx, sy, seed, base=(104, 92, 58), rim=(236, 150, 70), detail=True):
    w, h = im.size
    d = ImageDraw.Draw(im)
    # far leg and arm, darker
    for poly in (far_leg_poly(), far_arm_poly()):
        d.polygon(map_pts(poly, x0, y0, sx, sy), fill=tuple(int(c * 0.55) for c in base))
    body = map_pts(theropod_poly(), x0, y0, sx, sy)
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon(body, fill=255)
    bb = m.getbbox()
    # belly lighter, back darker
    g = grad_v(w, h, [(0, tuple(int(c * 0.55) for c in base)), (bb[1] / h, tuple(int(c * 0.6) for c in base)),
                      ((bb[1] * 0.6 + bb[3] * 0.4) / h, base), ((bb[1] * 0.3 + bb[3] * 0.7) / h, tuple(min(255, int(c * 1.35)) for c in base)),
                      (1, tuple(int(c * 0.7) for c in base))])
    g = mul(g, 0.75 + 0.45 * fbm(w, h, seed, 30 * sx, 4))
    im.paste(g, (0, 0), m)
    if detail:
        # dorsal stripes
        rng = R(seed)
        st = Image.new("L", (w, h), 0)
        ds = ImageDraw.Draw(st)
        for i in range(16):
            t = 0.08 + i * 0.05
            x = x0 + (100 + t * 600) * sx
            ds.polygon([(x, y0), (x + 30 * sx, y0), (x + 6 * sx + rng.uniform(-6, 6) * sx, y0 + (210 + rng.uniform(-30, 30)) * sy), (x - 10 * sx, y0 + 200 * sy)], fill=150)
        st = ImageChops.multiply(st, m).filter(ImageFilter.GaussianBlur(2 * sx))
        im.paste(Image.new("RGB", (w, h), tuple(int(c * 0.42) for c in base)), (0, 0), st)
        # scales: dark speckle
        sp = (noise(w, h, seed + 5, 2.5 * sx) > 0.72).astype(np.uint8) * 90
        spm = ImageChops.multiply(Image.fromarray(sp), m)
        im.paste(Image.new("RGB", (w, h), tuple(int(c * 0.5) for c in base)), (0, 0), spm)
        # mouth interior, teeth, eye, nostril
        mouth = map_pts([(772, 168), (830, 150), (870, 140), (900, 136), (896, 146), (860, 160), (835, 180), (850, 196), (800, 182)], x0, y0, sx, sy)
        d.polygon(mouth, fill=(92, 20, 22))
        d.polygon(map_pts([(790, 172), (850, 168), (860, 188), (820, 186)], x0, y0, sx, sy), fill=(150, 50, 52))
        for i in range(9):
            t = i / 8.0
            ux, uy = 800 + t * 96, 157 - t * 19
            p = map_pts([(ux - 5, uy), (ux + 5, uy - 2), (ux + 1, uy + 14)], x0, y0, sx, sy)
            d.polygon(p, fill=(236, 226, 196))
        for i in range(7):
            t = i / 6.0
            lx, ly = 806 + t * 62, 186 + t * 12
            p = map_pts([(lx - 5, ly), (lx + 5, ly + 2), (lx + 1, ly - 13)], x0, y0, sx, sy)
            d.polygon(p, fill=(228, 216, 184))
        ex, ey = map_pts([(790, 116)], x0, y0, sx, sy)[0]
        r = 9 * sx
        d.ellipse([ex - r * 1.3, ey - r * 1.0, ex + r * 1.3, ey + r * 1.0], fill=(40, 30, 16))
        d.ellipse([ex - r, ey - r * 0.75, ex + r, ey + r * 0.75], fill=(236, 190, 40))
        d.ellipse([ex - r * 0.22, ey - r * 0.7, ex + r * 0.22, ey + r * 0.7], fill=(10, 8, 4))
        d.line([map_pts([(760, 104)], x0, y0, sx, sy)[0], map_pts([(810, 100)], x0, y0, sx, sy)[0]], fill=tuple(int(c * 0.35) for c in base), width=max(2, int(5 * sx)))
        nx, ny = map_pts([(880, 118)], x0, y0, sx, sy)[0]
        d.ellipse([nx - 5 * sx, ny - 3 * sx, nx + 5 * sx, ny + 3 * sx], fill=(30, 22, 12))
        # claws
        for (cx, cy) in [(598, 484), (572, 488), (548, 488)]:
            p = map_pts([(cx - 6, cy - 6), (cx + 14, cy + 2), (cx - 4, cy + 4)], x0, y0, sx, sy)
            d.polygon(p, fill=(216, 206, 176))
    # sunset rim light along the top edges, a dark core shadow along the bottom
    top = ImageChops.subtract(m, ImageChops.offset(m, 0, max(2, int(9 * sy)))).filter(ImageFilter.GaussianBlur(3 * sx))
    im.paste(Image.new("RGB", (w, h), rim), (0, 0), top.point(lambda v: int(v * 0.85)))
    bot = ImageChops.subtract(m, ImageChops.offset(m, 0, -max(2, int(14 * sy)))).filter(ImageFilter.GaussianBlur(5 * sx))
    im.paste(Image.new("RGB", (w, h), (20, 16, 10)), (0, 0), bot.point(lambda v: int(v * 0.6)))
    # outline
    d.line(body + [body[0]], fill=(26, 20, 12), width=max(1, int(2.5 * sx)), joint="curve")
    return m


def paint_jeep(im, x0, y0, s, flip=False):
    """A generic open-top safari 4x4, side view facing right; (x0, y0) = rear bottom; s = px per unit."""
    d = ImageDraw.Draw(im)

    def P(pts):
        return [(x0 + (-x if flip else x) * s, y0 - y * s) for (x, y) in pts]
    khaki, khaki_d, khaki_l = (170, 150, 96), (110, 96, 60), (214, 196, 140)

    def E(a, b, fill):
        (ax, ay), (bx, by) = a, b
        d.ellipse([min(ax, bx), min(ay, by), max(ax, bx), max(ay, by)], fill=fill)
    # roll bar and spare wheel behind
    d.line(P([(0.55, 0.95), (0.62, 1.55), (1.25, 1.55), (1.30, 0.95)]), fill=(40, 40, 38), width=int(0.07 * s), joint="curve")
    E(P([(-0.12, 1.10)])[0], P([(0.18, 0.62)])[0], (26, 24, 22))
    # body
    body = [(0.0, 0.42), (0.0, 1.00), (1.55, 1.00), (1.75, 0.98), (2.55, 0.86), (2.95, 0.80), (3.05, 0.70), (3.05, 0.42)]
    d.polygon(P(body), fill=khaki)
    d.polygon(P([(0.0, 0.42), (0.0, 0.62), (3.05, 0.62), (3.05, 0.42)]), fill=khaki_d)
    d.line(P([(0.0, 0.98), (1.55, 0.98), (1.75, 0.96), (2.55, 0.84)]), fill=khaki_l, width=max(2, int(0.035 * s)))
    # windshield frame
    d.line(P([(1.72, 0.97), (1.95, 1.48)]), fill=(46, 44, 40), width=int(0.06 * s))
    d.line(P([(1.95, 1.48), (2.03, 1.47)]), fill=(46, 44, 40), width=int(0.06 * s))
    d.polygon(P([(1.76, 0.98), (1.97, 1.44), (2.02, 1.43), (1.82, 0.97)]), fill=(150, 190, 200))
    # door cut, stripe, hood vents, headlamp
    d.line(P([(1.02, 0.98), (1.02, 0.55), (1.60, 0.55), (1.70, 0.96)]), fill=khaki_d, width=max(2, int(0.025 * s)))
    d.polygon(P([(0.05, 0.70), (3.0, 0.70), (3.0, 0.76), (0.05, 0.76)]), fill=(186, 70, 30))
    E(P([(2.92, 0.80)])[0], P([(3.06, 0.68)])[0], (250, 240, 200))
    for i in range(4):
        d.line(P([(2.25 + i * 0.1, 0.84), (2.32 + i * 0.1, 0.92)]), fill=khaki_d, width=max(1, int(0.02 * s)))
    # mounted searchlight on the roll bar
    E(P([(1.12, 1.70)])[0], P([(1.30, 1.55)])[0], (60, 60, 58))
    # wheels with arches
    for wx in (0.55, 2.45):
        E(P([(wx - 0.48, 0.92)])[0], P([(wx + 0.48, -0.02)])[0], (52, 46, 30))
        E(P([(wx - 0.42, 0.42 + 0.42)])[0], P([(wx + 0.42, 0.0)])[0], (18, 18, 18))
        E(P([(wx - 0.22, 0.42 + 0.22)])[0], P([(wx + 0.22, 0.20)])[0], (150, 146, 130))
        E(P([(wx - 0.08, 0.50)])[0], P([(wx + 0.08, 0.34)])[0], (70, 66, 58))
    # two riders: dark silhouettes of heads and shoulders, one aiming back
    for (hx, hy) in [(0.95, 1.30), (1.45, 1.28)]:
        E(P([(hx - 0.13, hy + 0.15)])[0], P([(hx + 0.13, hy - 0.12)])[0], (36, 30, 24))
        d.polygon(P([(hx - 0.22, 0.98), (hx - 0.18, 1.18), (hx + 0.18, 1.18), (hx + 0.24, 0.98)]), fill=(70, 74, 50))
    d.line(P([(0.95, 1.15), (0.25, 1.30)]), fill=(30, 30, 30), width=int(0.05 * s))


def foliage(im, seed, y_base, count, col, size, spread_y=0.0, kind="fern"):
    """Fern fronds and palm crowns as dark painted silhouettes."""
    rng = R(seed)
    d = ImageDraw.Draw(im)
    w, h = im.size
    for _ in range(count):
        cx = rng.uniform(-0.05, 1.05) * w
        cy = y_base + rng.uniform(-spread_y, spread_y)
        c = tuple(max(0, min(255, int(v * rng.uniform(0.8, 1.2)))) for v in col)
        n = rng.randint(6, 10)
        for k in range(n):
            a = -math.pi * (0.08 + 0.84 * k / (n - 1)) + rng.uniform(-0.12, 0.12)
            L = size * rng.uniform(0.6, 1.2)
            pts = []
            for t in np.linspace(0, 1, 14):
                droop = (t ** 2) * L * 0.45
                px = cx + math.cos(a) * L * t
                py = cy + math.sin(a) * L * t + droop
                pts.append((px, py))
            # leaflets along the frond
            for i, (px, py) in enumerate(pts[1:], 1):
                lw = (1 - i / len(pts)) * size * 0.16 + 2
                nx, ny = -math.sin(a), math.cos(a)
                d.line([(px - nx * lw, py - ny * lw - lw * 0.4), (px + nx * lw, py + ny * lw - lw * 0.4)], fill=c, width=max(2, int(size * 0.025)))
            d.line(pts, fill=c, width=max(2, int(size * 0.03)))
        if kind == "palm":
            d.line([(cx, cy), (cx + rng.uniform(-20, 20), h + 10)], fill=c, width=int(size * 0.08))


# ------------------------------------------------------------------ textures
def side_art():
    """Side panel art: covers the flat side, 2.07 m (z) x 1.40 m (y) -> 1024 x 692. Front of the
    machine (screen end) is at the right edge (u = 1); the left side shows it mirrored."""
    W, H = 1024, 692
    im = grad_v(W, H, [(0, (26, 44, 70)), (0.22, (60, 70, 96)), (0.42, (176, 96, 66)), (0.56, (238, 150, 66)), (0.66, (250, 196, 110)), (1, (120, 80, 50))])
    d = ImageDraw.Draw(im)
    # sun and clouds
    d.ellipse([560, 300, 700, 440], fill=(255, 226, 150))
    rng = R(11)
    for _ in range(60):
        y = rng.uniform(80, 330)
        x = rng.uniform(-50, W)
        L = rng.uniform(80, 260)
        t = (y - 80) / 250
        c = (int(90 + 140 * t), int(70 + 60 * t), int(90 - 20 * t))
        d.line([(x, y), (x + L, y + rng.uniform(-6, 6))], fill=c, width=int(rng.uniform(5, 14)))
    # volcano with a smoke plume
    d.polygon([(120, 470), (250, 300), (300, 290), (330, 300), (470, 470)], fill=(78, 58, 86))
    d.polygon([(250, 300), (300, 290), (330, 300), (300, 330)], fill=(230, 110, 40))
    for i in range(40):
        t = i / 40
        x = 290 - t * 160 + rng.uniform(-20, 20)
        y = 290 - t * 240
        r = 18 + t * 60
        g = int(90 + 40 * t)
        d.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], fill=(g, g - 10, g + 6))
    # distant ridge and mid jungle
    d.polygon([(0, 470)] + [(x, 430 + 20 * math.sin(x / 70.0) + 10 * math.sin(x / 23.0)) for x in range(0, W + 1, 16)] + [(W, 470)], fill=(62, 70, 80))
    im = im.filter(ImageFilter.GaussianBlur(1.5))
    foliage(im, 21, 470, 14, (40, 70, 62), 120, 30, kind="palm")
    d = ImageDraw.Draw(im)
    d.rectangle([0, 480, W, H], fill=(44, 62, 40))
    # dirt track
    d.polygon([(0, 600), (W, 560), (W, 640), (0, 680)], fill=(150, 112, 70))
    d.polygon([(0, 640), (W, 600), (W, 612), (0, 652)], fill=(120, 90, 56))
    foliage(im, 22, 520, 16, (30, 58, 40), 100, 40)
    # the dinosaur: big, mid-left, roaring toward the front
    paint_dino(im, 20, 150, 0.82, 0.98, 31)
    # dust behind the jeep, the jeep
    for i in range(30):
        x = 640 + rng.uniform(-60, 80)
        y = 600 - rng.uniform(0, 80)
        r = rng.uniform(16, 40)
        c = int(rng.uniform(170, 210))
        d.ellipse([x - r, y - r * 0.7, x + r, y + r * 0.7], fill=(c, int(c * 0.85), int(c * 0.65)))
    paint_jeep(im, 700, 640, 92)
    # foreground ferns, darkest
    foliage(im, 23, 700, 18, (14, 34, 22), 150, 10)
    foliage(im, 24, 690, 8, (20, 44, 28), 110, 20)
    im = im.filter(ImageFilter.ModeFilter(3))
    im = brushwork(im, 41, 16000, 4, 12, 2, 4, 8, angle=-0.2, spread=1.4)
    im = im.filter(ImageFilter.SMOOTH)
    # frame: yellow pinstripe top, dark band and orange stripe at the bottom
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 6], fill=PAINT)
    d.rectangle([0, 7, W, 13], fill=(232, 182, 40))
    d.rectangle([0, H - 40, W, H], fill=(18, 20, 18))
    d.rectangle([0, H - 52, W, H - 42], fill=(222, 104, 30))
    # wear: scuffs low down and at the entry (rear) edge, chips to white gelcoat, a faded patch
    wear = Image.new("L", (W, H), 0)
    dw = ImageDraw.Draw(wear)
    for _ in range(150):
        x = rng.uniform(0, W)
        y = H - 56 - abs(rng.gauss(0, 40))
        if rng.random() < 0.3:
            x = abs(rng.gauss(0, 40))
            y = rng.uniform(200, H - 40)
        L = rng.uniform(4, 24)
        a = rng.uniform(-0.4, 0.4)
        dw.line([(x, y), (x + math.cos(a) * L, y + math.sin(a) * L)], fill=int(rng.uniform(30, 100)), width=1)
    for _ in range(26):
        x, y = rng.uniform(0, W), rng.uniform(H - 140, H - 44)
        r = rng.uniform(1.5, 4)
        dw.ellipse([x - r, y - r, x + r, y + r], fill=230)
    im.paste(Image.new("RGB", (W, H), (208, 204, 190)), (0, 0), wear)
    fade = (fbm(W, H, 77, 200, 2) * 0.12).astype(np.float32)
    a = np.asarray(im).astype(np.float32)
    a = a * (1 - fade[:, :, None]) + 200 * fade[:, :, None]
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    save(im, "ride_side.png", colors=256)


def title_decal():
    """Title decal on each side: 1.40 x 0.35 m -> 1024 x 256 RGBA (alpha-scissored)."""
    im = logo(1024, 256, sub=True)
    # vinyl decal wear: a few nicks in the alpha
    rng = R(5)
    a = im.getchannel("A")
    d = ImageDraw.Draw(a)
    for _ in range(30):
        x, y = rng.uniform(0, 1024), rng.uniform(0, 256)
        d.ellipse([x - 2, y - 1, x + 2, y + 1], fill=0)
    im.putalpha(a)
    save(im, "ride_title.png", colors=96)


def marquee():
    """Backlit translucent marquee: 1.20 x 0.30 m -> 1024 x 256."""
    W, H = 1024, 256
    im = grad_v(W, H, [(0, (40, 30, 70)), (0.45, (210, 90, 50)), (0.75, (250, 180, 90)), (1, (240, 210, 140))])
    foliage(im, 51, 250, 22, (24, 44, 32), 90, 10, kind="palm")
    im = im.filter(ImageFilter.GaussianBlur(1))
    # a small dinosaur silhouette on the left, the jeep on the right
    sil = Image.new("RGB", (W, H), 0)
    paint_dino(im, 0, 64, 0.30, 0.38, 52, base=(40, 36, 30), rim=(250, 170, 90), detail=False)
    paint_jeep(im, 1010, 236, 34, flip=True)
    lg = logo(820, 205, sub=True)
    im.paste(lg, (102, 8), lg)
    # "2 PLAYERS" tag
    d = ImageDraw.Draw(im)
    # lightbox: two fluorescent tubes behind, darker edges
    yy = np.linspace(0, 1, H)[:, None]
    xx = np.linspace(0, 1, W)[None, :]
    tubes = 0.80 + 0.22 * np.exp(-((yy - 0.3) / 0.12) ** 2) + 0.22 * np.exp(-((yy - 0.72) / 0.12) ** 2)
    edge = np.minimum(1, np.minimum(xx, 1 - xx) * 14) * 0.25 + 0.75
    im = mul(im, (tubes * edge).astype(np.float32))
    save(gamma(im, 1.1), "ride_marquee.png", colors=200)


def screen():
    """The game on the projection screen: 1.00 x 0.75 m (4:3) -> 512 x 384. An original jungle chase."""
    W, H = 512, 384
    im = grad_v(W, H, [(0, (40, 90, 150)), (0.35, (150, 180, 160)), (0.5, (70, 110, 60)), (1, (40, 60, 26))])
    d = ImageDraw.Draw(im)
    # hazy distant trees
    foliage(im, 61, 190, 18, (60, 100, 70), 70, 12, kind="palm")
    im = im.filter(ImageFilter.GaussianBlur(1.2))
    foliage(im, 62, 200, 14, (30, 64, 34), 80, 10, kind="palm")
    d = ImageDraw.Draw(im)
    # the track in perspective
    d.polygon([(236, 196), (276, 196), (470, H), (40, H)], fill=(150, 116, 74))
    d.polygon([(250, 196), (262, 196), (300, H), (210, H)], fill=(126, 98, 62))
    # a dinosaur coming out of the trees ahead
    paint_dino(im, 170, 128, 0.20, 0.24, 63, base=(110, 96, 64), rim=(220, 230, 200), detail=True)
    foliage(im, 64, 250, 8, (36, 70, 36), 110, 10)
    foliage(im, 65, H + 20, 6, (20, 44, 20), 120, 0)
    d = ImageDraw.Draw(im)
    # the jeep's hood at the bottom
    d.polygon([(0, H), (60, 330), (452, 330), (W, H)], fill=(140, 124, 80))
    d.polygon([(60, 330), (452, 330), (440, 338), (72, 338)], fill=(196, 180, 130))
    d.line([(256, 330), (256, H)], fill=(110, 96, 60), width=3)
    # crosshairs P1 (red) on the dinosaur's head, P2 (blue)
    for (x, y, c) in [(282, 160, (255, 60, 40)), (180, 220, (60, 140, 255))]:
        d.ellipse([x - 14, y - 14, x + 14, y + 14], outline=c, width=3)
        for dx, dy in [(-22, 0), (22, 0), (0, -22), (0, 22)]:
            d.line([(x + dx * 0.4, y + dy * 0.4), (x + dx, y + dy)], fill=c, width=3)
    # hit flash
    d.ellipse([272, 146, 296, 164], fill=(255, 240, 160))
    # HUD
    f = font(F_COND, 18)
    fs = font(F_COND, 13)
    d.text((14, 8), "1P", font=f, fill=(255, 80, 60))
    d.text((40, 8), "0042650", font=f, fill=(255, 250, 230))
    d.text((W - 14, 8), "2P", font=f, fill=(90, 150, 255), anchor="ra")
    d.text((W - 44, 8), "0018300", font=f, fill=(255, 250, 230), anchor="ra")
    text_c(d, (W / 2, 18), "STAGE 2  RIVER CROSSING", fs, (255, 230, 120))
    for i in range(8):
        d.rectangle([14 + i * 9, 34, 20 + i * 9, 48], fill=(255, 210, 60) if i < 6 else (90, 70, 30))
        d.rectangle([W - 20 - i * 9, 34, W - 14 - i * 9, 48], fill=(255, 210, 60) if i < 3 else (90, 70, 30))
    # danger meter
    d.rectangle([150, 360, 362, 372], outline=(255, 255, 255), width=2)
    d.rectangle([152, 362, 290, 370], fill=(240, 60, 30))
    text_c(d, (W / 2, 352), "DANGER", fs, (255, 255, 255))
    im = im.filter(ImageFilter.SMOOTH)
    # CRT: scanlines, slight bloom, vignette
    a = np.asarray(im).astype(np.float32)
    lines = np.where(np.arange(H) % 3 == 2, 0.68, 1.0)[:, None, None]
    yy = np.linspace(-1, 1, H)[:, None]
    xx = np.linspace(-1, 1, W)[None, :]
    vig = 1 - 0.35 * (xx ** 2 + yy ** 2) ** 1.4
    a = a * lines * vig[:, :, None]
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    bloom = im.filter(ImageFilter.GaussianBlur(4))
    im = ImageChops.add(im, bloom.point(lambda v: int(v * 0.25)))
    save(gamma(im, 1.0), "ride_screen.png", colors=180)


def grille(d, x0, y0, x1, y1, pitch=5, r=1.4, col=(6, 6, 7), plate=(40, 40, 44)):
    d.rounded_rectangle([x0, y0, x1, y1], radius=6, fill=plate, outline=(70, 70, 76), width=2)
    y = y0 + pitch
    row = 0
    while y < y1 - pitch * 0.6:
        x = x0 + pitch * (1.0 if row % 2 else 0.5)
        while x < x1 - pitch * 0.5:
            d.ellipse([x - r, y - r, x + r, y + r], fill=col)
            x += pitch
        y += pitch * 0.87
        row += 1


def dash():
    """Front wall inside the cabin around the screen shroud: 1.54 x 1.64 m -> 512 x 512.
    u = (x + 0.77) / 1.54, v = (2.05 - y) / 1.65."""
    W, H = 512, 512
    base = np.full((H, W), 26, np.float32) + fbm(W, H, 81, 8, 3) * 14
    im = Image.fromarray(np.stack([base, base, base * 1.06], -1).clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)

    def U(x):
        return (x + 0.77) / 1.54 * W

    def V(y):
        return (2.05 - y) / 1.65 * H
    for sx in (-1, 1):
        x0, x1 = sorted([U(sx * 0.62), U(sx * 0.755)])
        grille(d, x0, V(1.78), x1, V(1.12), pitch=4.2, r=1.2)
    f = font(F_COND, 11)
    text_c(d, (W / 2, V(1.985)), "KEEP HANDS AND FEET INSIDE THE RIDE", f, (220, 196, 90))
    save(im, "ride_dash.png", colors=64)


def console():
    """Gun console top inside: 1.52 x 0.306 m -> 1024 x 256. v = 0 at the screen edge, 1 at the riders."""
    W, H = 1024, 256
    base = 30 + fbm(W, H, 91, 3, 2) * 18
    im = Image.fromarray(np.stack([base, base, base], -1).clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    d.rectangle([6, 6, W - 7, H - 7], outline=(200, 160, 50), width=3)
    d.line([(W / 2, 14), (W / 2, H - 14)], fill=(200, 160, 50), width=2)
    fh = font(F_HEAVY, 34)
    fs = font(F_COND, 18)
    for side, name, col in [(-1, "PLAYER 1", (238, 96, 40)), (1, "PLAYER 2", (70, 190, 90))]:
        cx = W / 2 + side * W * 0.25
        text_c(d, ((side * 0.60 + 0.76) / 1.52 * W - side * 20, 46), name, font(F_HEAVY, 30), col)
        # gun mount plate
        gx = (side * 0.34 + 0.76) / 1.52 * W
        gy = 0.533 * H
        d.ellipse([gx - 52, gy - 40, gx + 52, gy + 40], fill=(56, 56, 60), outline=(14, 14, 14), width=3)
        for k in range(4):
            a = k * math.pi / 2 + 0.6
            d.ellipse([gx + math.cos(a) * 40 - 4, gy + math.sin(a) * 30 - 4, gx + math.cos(a) * 40 + 4, gy + math.sin(a) * 30 + 4], fill=(150, 150, 150))
        # START ring and label
        bx = (side * 0.60 + 0.76) / 1.52 * W
        d.ellipse([bx - 34, gy - 26, bx + 34, gy + 26], fill=(14, 14, 14), outline=col, width=4)
        text_c(d, (bx, gy + 48), "START", fs, (240, 236, 220))
        text_c(d, (cx, H - 30), "AIM  -  PULL TRIGGER  -  SHOOT OFF SCREEN TO RELOAD", font(F_COND, 15), (210, 200, 170))
    # wear at the riders' edge (v = 1): arms rubbed the paint through
    rng = R(92)
    for _ in range(500):
        x = rng.uniform(20, W - 20)
        y = H - 8 - abs(rng.gauss(0, 18))
        L = rng.uniform(3, 18)
        c = int(rng.uniform(70, 130))
        d.line([(x, y), (x + L, y + rng.uniform(-2, 2))], fill=(c, c, c - 6), width=1)
    save(im, "ride_console.png", colors=96)


def wrap(text, f, width, d):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if d.textlength(t, font=f) > width and cur:
            lines.append(cur)
            cur = wd
        else:
            cur = t
    lines.append(cur)
    return lines


def decals():
    """Atlas 512 x 512: placard (0,0)-(256,384), '2 PLAYERS' (256,0)-(512,86),
    coin door (256,96)-(448,448), danger sticker (0,392)-(256,504), vent (256,452)-(512,512)."""
    im = Image.new("RGB", (512, 512), (30, 30, 30))
    d = ImageDraw.Draw(im)
    rng = R(101)
    # --- safety placard: off-white printed plastic, a little yellowed
    d.rectangle([0, 0, 255, 383], fill=(232, 226, 206))
    d.rectangle([0, 0, 255, 48], fill=(196, 30, 30))
    text_c(d, (128, 16), "FOR YOUR SAFETY", font(F_BOLD, 19), (255, 255, 255))
    text_c(d, (128, 37), "PLEASE READ BEFORE RIDING", font(F_COND, 12), (255, 230, 220))
    y = 60
    # height bar
    d.rectangle([12, y, 244, y + 52], outline=(30, 30, 30), width=2)
    text_c(d, (128, y + 17), "RIDERS MUST BE AT LEAST", font(F_COND, 14), (20, 20, 20))
    text_c(d, (128, y + 37), "42 INCHES TALL", font(F_BOLD, 20), (196, 30, 30))
    y += 62
    f = font(F_REG, 11)
    for para in ["THIS IS A MOTION RIDE. Persons with heart conditions, high blood pressure, back or neck problems, expectant mothers and persons prone to motion sickness should not ride.",
                 "Remain seated at all times. Keep hands and feet inside the ride. Hold the gun with both hands.",
                 "Children under 7 must ride with an adult. Maximum 2 riders."]:
        for ln in wrap(para, f, 228, d):
            d.text((14, y), ln, font=f, fill=(24, 24, 24))
            y += 13
        y += 5
    d.rectangle([0, y + 2, 255, y + 24], fill=(30, 30, 30))
    text_c(d, (128, y + 13), "HOW TO PLAY", font(F_BOLD, 14), (250, 210, 60))
    y += 30
    for ln in ["1. INSERT TOKENS.", "2. PUSH START.", "3. AIM AND PULL THE TRIGGER.", "4. SHOOT OFF SCREEN TO RELOAD."]:
        d.text((16, y), ln, font=font(F_COND, 12), fill=(24, 24, 24))
        y += 15
    # yellowing, grime, a torn corner
    a = np.asarray(im).astype(np.float32)
    g = fbm(256, 384, 102, 40, 3)
    a[0:384, 0:256] *= (0.86 + 0.14 * g)[:, :, None]
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    d.polygon([(256, 384), (226, 384), (256, 356)], fill=(30, 30, 30))
    # --- 2 PLAYERS sign
    d.rectangle([256, 0, 511, 85], fill=(232, 182, 40))
    d.rectangle([262, 6, 505, 79], outline=(20, 20, 20), width=3)
    text_c(d, (384, 44), "2 PLAYERS", font(F_HEAVY, 46), (20, 20, 20))
    # --- coin door: black steel frame, chrome inserts, two token slots with lamps, coin returns
    x0, y0, x1, y1 = 256, 96, 447, 447
    d.rectangle([x0, y0, x1, y1], fill=(24, 24, 26))
    d.rectangle([x0 + 8, y0 + 8, x1 - 8, y1 - 8], fill=(46, 46, 50), outline=(80, 80, 86), width=2)
    for i, cx in enumerate([x0 + 58, x0 + 134]):
        cy = y0 + 104
        d.rounded_rectangle([cx - 30, cy - 66, cx + 30, cy + 66], radius=6, fill=(176, 178, 182), outline=(90, 90, 96), width=2)
        d.rectangle([cx - 20, cy - 52, cx + 20, cy - 30], fill=(236, 120, 30))      # lamp lens (the lit part is a dyn quad)
        d.rectangle([cx - 3, cy - 50, cx + 3, cy - 32], fill=(30, 10, 0))           # token slot
        d.rounded_rectangle([cx - 18, cy - 10, cx + 18, cy + 26], radius=4, fill=(130, 20, 18), outline=(60, 10, 10), width=2)
        text_c(d, (cx, cy + 8), "RETURN", font(F_COND, 8), (240, 220, 210))
        d.rectangle([cx - 14, cy + 38, cx + 14, cy + 56], fill=(20, 20, 20))       # return chute
        # brass "TOKENS ONLY" sticker
        d.rectangle([cx - 28, cy + 76, cx + 28, cy + 96], fill=(196, 160, 70))
        text_c(d, (cx, cy + 86), "TOKENS", font(F_COND, 11), (40, 26, 8))
    text_c(d, (x0 + 96, y0 + 232), "1 TOKEN PER PLAYER", font(F_COND, 13), (250, 210, 60))
    d.ellipse([x0 + 84, y0 + 268, x0 + 108, y0 + 292], fill=(170, 170, 176), outline=(60, 60, 60), width=2)  # lock
    d.rectangle([x0 + 94, y0 + 274, x0 + 98, y0 + 286], fill=(40, 40, 40))
    text_c(d, (x0 + 96, y0 + 320), "POCKET CHANGE", font(F_COND, 10), (190, 190, 190))
    for _ in range(140):
        x, y = rng.uniform(x0 + 8, x1 - 8), rng.uniform(y0 + 8, y1 - 8)
        L = rng.uniform(3, 14)
        c = int(rng.uniform(90, 150))
        d.line([(x, y), (x + L, y + rng.uniform(-3, 3))], fill=(c, c, c), width=1)
    # --- high-voltage sticker
    d.rectangle([0, 392, 255, 503], fill=(250, 214, 40))
    d.rectangle([4, 396, 251, 499], outline=(20, 20, 20), width=4)
    d.polygon([(40, 480), (70, 420), (100, 480)], outline=(20, 20, 20), fill=(250, 214, 40), width=5)
    text_c(d, (70, 464), "!", font(F_BOLD, 30), (20, 20, 20))
    text_c(d, (176, 430), "DANGER", font(F_BOLD, 24), (20, 20, 20))
    text_c(d, (176, 458), "HIGH VOLTAGE", font(F_COND, 16), (20, 20, 20))
    text_c(d, (176, 480), "SERVICE ONLY", font(F_COND, 13), (20, 20, 20))
    # --- vent louvres
    d.rectangle([256, 452, 511, 511], fill=(20, 20, 22))
    for i in range(14):
        x = 266 + i * 17.5
        d.rectangle([x, 458, x + 10, 506], fill=(4, 4, 5))
        d.line([(x, 458), (x + 10, 458)], fill=(70, 74, 72), width=2)
    save(im, "ride_decals.png", colors=128)


def paint_tex():
    """Gloss-painted fibreglass, tiles once per metre: 256 px."""
    S = 256
    n = fbm(S, S, 111, 64, 2)
    peel = noise(S, S, 112, 1.5)
    a = np.zeros((S, S, 3), np.float32)
    for c in range(3):
        a[:, :, c] = PAINT[c] * (0.9 + 0.16 * n + 0.05 * peel)
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    rng = R(113)
    for _ in range(14):
        x, y = rng.uniform(0, S), rng.uniform(0, S)
        L = rng.uniform(4, 16)
        a = rng.uniform(-0.6, 0.6)
        c = int(rng.uniform(38, 52))
        d.line([(x, y), (x + math.cos(a) * L, y + math.sin(a) * L)], fill=(c, c + 14, c + 6), width=1)
    save(im, "ride_paint.png", colors=48)


def skirt():
    """Motion-base skirt: black rubber bellows, 1 m wide x 0.30 m -> 256 x 96 (tiles along u)."""
    W, H = 256, 96
    x = np.arange(W)[None, :]
    pleat = 0.55 + 0.45 * np.cos(x / W * 2 * math.pi * 10) ** 2
    y = np.linspace(0, 1, H)[:, None]
    dust = 1 + 0.6 * np.clip((y - 0.6) / 0.4, 0, 1) * fbm(W, H, 121, 20, 2)
    v = 26 * pleat * dust + fbm(W, H, 122, 4, 2) * 8
    im = Image.fromarray(np.stack([v, v, v * 1.04], -1).clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 6], fill=(14, 14, 14))
    d.line([(0, 7), (W, 7)], fill=(60, 60, 60), width=1)
    save(im, "ride_skirt.png", colors=32)


def carpet():
    """Cabin carpet, 0.5 m tile -> 256 px: charcoal loop pile with confetti flecks, worn path."""
    S = 256
    rng = np.random.default_rng(131)
    v = 30 + rng.random((S, S)) * 22 + fbm(S, S, 132, 40, 3) * 10
    a = np.stack([v, v, v * 1.1], -1)
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    r = R(133)
    for _ in range(420):
        x, y = r.uniform(0, S), r.uniform(0, S)
        c = r.choice([(40, 110, 130), (130, 50, 110), (150, 130, 40), (70, 70, 140)])
        d.line([(x, y), (x + r.uniform(-3, 3), y + r.uniform(-3, 3))], fill=c, width=2)
    save(im, "ride_carpet.png", colors=64)


def felt():
    """Cabin lining: black needle-felt carpet glued to the fibreglass, 0.5 m tile -> 128 px."""
    S = 128
    rng = np.random.default_rng(171)
    v = 22 + rng.random((S, S)) * 14 + fbm(S, S, 172, 30, 3) * 10
    im = Image.fromarray(np.stack([v, v, v * 1.08], -1).clip(0, 255).astype(np.uint8))
    save(im, "ride_felt.png", colors=32)


def vinyl():
    """Seat vinyl, tiles every 0.33 m -> 256 px: oxblood, pleated channels (2 per tile),
    fine grain, rubbed-pale creases where riders slide in."""
    S = 256
    x = np.arange(S)[None, :].astype(np.float32)
    ch = 0.80 + 0.28 * np.sin(x / S * 2 * math.pi * 2 - math.pi / 2) ** 2   # padded channels
    seam = 1 - 0.55 * np.exp(-((((x + 64) % 128) - 64) / 2.2) ** 2)          # stitched seams
    g = noise(S, S, 141, 1.2)
    big = fbm(S, S, 142, 60, 2)
    k = ch * seam * (0.94 + 0.10 * g) * (0.85 + 0.3 * big)
    base = np.array([92, 22, 24], np.float32)
    a = base[None, None, :] * k[:, :, None]
    # pale rubbed creases
    cr = np.zeros((S, S), np.float32)
    im0 = Image.fromarray(np.zeros((S, S), np.uint8))
    d0 = ImageDraw.Draw(im0)
    r = R(143)
    for _ in range(26):
        x0, y0 = r.uniform(0, S), r.uniform(0, S)
        L = r.uniform(10, 46)
        an = r.uniform(-0.35, 0.35)
        d0.line([(x0, y0), (x0 + math.cos(an) * L, y0 + math.sin(an) * L)], fill=int(r.uniform(60, 140)), width=2)
    cr = np.asarray(im0.filter(ImageFilter.GaussianBlur(1.0))).astype(np.float32) / 255.0
    a = a * (1 - cr[:, :, None]) + np.array([150, 96, 92])[None, None, :] * cr[:, :, None]
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    save(im, "ride_vinyl.png", colors=64)


def tread():
    """Aluminium diamond plate, 0.25 m tile -> 128 px."""
    S = 128
    v = 150 + fbm(S, S, 151, 20, 2) * 40
    im = Image.fromarray(np.stack([v, v, v * 1.02], -1).clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    for j in range(8):
        for i in range(8):
            cx = i * 16 + (8 if j % 2 else 0)
            cy = j * 16 + 8
            a = math.pi / 4 if (i + j) % 2 == 0 else -math.pi / 4
            dx, dy = math.cos(a) * 6, math.sin(a) * 6
            d.line([(cx - dx, cy - dy), (cx + dx, cy + dy)], fill=(215, 215, 218), width=3)
            d.line([(cx - dx + 1, cy - dy + 2), (cx + dx + 1, cy + dy + 2)], fill=(90, 90, 92), width=1)
    save(im, "ride_tread.png", colors=32)


def hazard():
    """Yellow/black safety stripe tape, 0.5 m x 0.05 m -> 256 x 32 (tiles along u)."""
    W, H = 256, 32
    im = Image.new("RGB", (W, H), (236, 190, 30))
    d = ImageDraw.Draw(im)
    for i in range(-2, 10):
        x = i * 32
        d.polygon([(x, H), (x + 16, H), (x + 16 + H, 0), (x + H, 0)], fill=(20, 18, 16))
    a = np.asarray(im).astype(np.float32) * (0.8 + 0.25 * fbm(W, H, 161, 10, 2))[:, :, None]
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    save(im, "ride_hazard.png", colors=24)


if __name__ == "__main__":
    side_art()
    title_decal()
    marquee()
    screen()
    dash()
    console()
    decals()
    paint_tex()
    skirt()
    carpet()
    felt()
    vinyl()
    tread()
    hazard()
    tot = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT) if f.startswith("ride_"))
    print("total %.0f KB" % (tot / 1024))
