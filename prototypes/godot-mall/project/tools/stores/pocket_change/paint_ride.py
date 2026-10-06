"""Paints the textures of the Pocket Change motion-ride cabinet (ride.gd) into tex/pc/ride_*.png.

The machine is the TYPE that stood in mid-90s arcades: a deluxe enclosed two-seat motion
cabin with a dinosaur light-gun game. Everything here is original: the invented title
"TALON CREEK", a sunset-orange / charcoal / chrome body, and painted canyon art with generic
dinosaurs of several kinds (no vehicles, no chase).
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

PAINT = (206, 94, 36)      # the cabin's sunset-orange gloss fibreglass (lower body charcoal)
CHAR = (34, 34, 37)


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


def logo(w, h, seed=3, sub=True):
    """The invented title in a 90s chrome-and-sunset style: chrome letters split by a
    horizon line, a purple keyline, an orange glow, a purple subtitle bar."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    s = h / 256.0
    txt = "TALON CREEK"
    fs = int(150 * s)
    f = font(F_LOGO, fs)
    while f.getbbox(txt)[2] - f.getbbox(txt)[0] > w * 0.92:
        fs -= 2
        f = font(F_LOGO, fs)
    cy = h * (0.40 if sub else 0.5)

    def mask(stroke):
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).text((w / 2, cy), txt, font=f, fill=255, anchor="mm", stroke_width=stroke)
        return m
    m = mask(0)
    outer = mask(int(13 * s))
    inner = mask(int(6 * s))
    glow = outer.filter(ImageFilter.GaussianBlur(9 * s))
    im.paste(Image.new("RGBA", (w, h), (255, 110, 30, 255)), (0, 0), glow.point(lambda v: int(min(255, v * 1.3))))
    im.paste(Image.new("RGBA", (w, h), (255, 150, 50, 255)), (0, 0), outer)
    im.paste(Image.new("RGBA", (w, h), (38, 14, 60, 255)), (0, 0), inner)
    bb = m.getbbox()
    t0, t1 = bb[1] / h, bb[3] / h
    hz = t0 + (t1 - t0) * 0.56
    g = grad_v(w, h, [(0, (240, 246, 255)), (t0, (236, 244, 255)), (t0 + (t1 - t0) * 0.35, (150, 172, 214)), (hz - 0.01, (90, 104, 150)),
                      (hz, (44, 28, 70)), (hz + 0.02, (255, 214, 130)), (t1, (214, 84, 40)), (1, (180, 60, 30))])
    im.paste(g.convert("RGBA"), (0, 0), m)
    hl = ImageChops.subtract(m, ImageChops.offset(m, 0, int(3 * s))).filter(ImageFilter.GaussianBlur(0.8))
    im.paste(Image.new("RGBA", (w, h), (255, 255, 255, 255)), (0, 0), hl.point(lambda v: int(v * 0.9)))
    # a few star glints on the chrome
    d = ImageDraw.Draw(im)
    rng = R(seed)
    for _ in range(3):
        x, y = rng.uniform(bb[0], bb[2]), bb[1] + rng.uniform(0.05, 0.3) * (bb[3] - bb[1])
        r = 12 * s
        d.line([(x - r, y), (x + r, y)], fill=(255, 255, 255, 255), width=max(1, int(2 * s)))
        d.line([(x, y - r), (x, y + r)], fill=(255, 255, 255, 255), width=max(1, int(2 * s)))
    if sub:
        ry0, ry1 = h * 0.72, h * 0.94
        d.rectangle([w * 0.16 - 4 * s, ry0 - 4 * s, w * 0.84 + 4 * s, ry1 + 4 * s], fill=(255, 140, 40, 255))
        bar = grad_v(w, h, [(0, (120, 60, 180)), (ry0 / h, (120, 60, 180)), (ry1 / h, (52, 20, 90)), (1, (52, 20, 90))])
        bm = Image.new("L", (w, h), 0)
        ImageDraw.Draw(bm).rectangle([w * 0.16, ry0, w * 0.84, ry1], fill=255)
        im.paste(bar.convert("RGBA"), (0, 0), bm)
        f2 = font(F_HEAVY, int(30 * s))
        d.text((w / 2, (ry0 + ry1) / 2), "A  PREHISTORIC  MOTION  RIDE", font=f2, fill=(255, 236, 200), anchor="mm")
    return im


# ------------------------------------------------------------------ painted creatures
def bez(p0, p1, p2, n=14):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])
            for t in np.linspace(0, 1, n)]


def tube(spine, w0, w1):
    """Polygon round a spine polyline, half-width tapering w0 -> w1."""
    left, right = [], []
    n = len(spine)
    for i, (x, y) in enumerate(spine):
        a, b = spine[max(i - 1, 0)], spine[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        w = w0 + (w1 - w0) * i / (n - 1)
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    return left + right[::-1]


def creature(kind):
    """Generic dinosaurs in side view facing right, in a 1000 x 500 box:
    (near shapes, far-side shapes, bone shapes, eye). Shapes: ("poly", pts) / ("ell", box)."""
    if kind == "cera":    # a horned, frilled plant-eater
        near = [("ell", (260, 170, 720, 390)),
                ("poly", tube(bez((310, 250), (150, 300), (40, 350)), 62, 6)),
                ("poly", [(650, 130), (675, 62), (735, 30), (790, 52), (800, 120), (770, 200), (720, 250), (660, 250)]),
                ("poly", [(730, 160), (820, 168), (900, 215), (952, 266), (944, 298), (900, 312), (820, 302), (748, 282), (690, 250)]),
                ("poly", [(620, 320), (700, 320), (712, 466), (650, 470)]), ("ell", (636, 450, 722, 482)),
                ("poly", [(320, 300), (430, 300), (440, 466), (360, 470)]), ("ell", (346, 450, 452, 482))]
        far = [("poly", [(560, 330), (620, 330), (628, 458), (578, 460)]), ("poly", [(420, 320), (480, 320), (490, 452), (440, 456)])]
        bone = [("poly", [(818, 186), (958, 142), (826, 208)]), ("poly", [(796, 192), (924, 162), (806, 214)]),
                ("poly", [(904, 238), (926, 202), (934, 250)]), ("poly", [(936, 270), (974, 288), (944, 304)])]
        return near, far, bone, (832, 214)
    if kind == "sauro":   # a long-necked giant
        near = [("ell", (300, 200, 640, 340)),
                ("poly", tube(bez((600, 250), (720, 210), (800, 50)), 42, 15)), ("ell", (782, 26, 852, 62)),
                ("poly", tube(bez((330, 262), (160, 300), (10, 330)), 46, 3)),
                ("poly", [(560, 300), (612, 300), (616, 470), (566, 470)]), ("poly", [(340, 290), (410, 290), (420, 470), (352, 470)])]
        far = [("poly", [(510, 310), (556, 310), (560, 462), (516, 462)]), ("poly", [(400, 300), (452, 300), (458, 462), (408, 462)])]
        return near, far, [], (830, 40)
    if kind == "hadro":   # a crested duck-billed herd animal
        near = [("ell", (330, 170, 640, 320)),
                ("poly", tube(bez((360, 235), (200, 225), (40, 195)), 56, 4)),
                ("poly", tube(bez((610, 232), (680, 190), (718, 130)), 42, 22)),
                ("poly", [(690, 105), (760, 108), (810, 132), (832, 150), (800, 162), (740, 160), (700, 150)]),
                ("poly", tube(bez((712, 116), (660, 66), (596, 58)), 14, 5)),
                ("poly", tube([(470, 270), (505, 370), (472, 458)], 50, 18)), ("poly", [(440, 452), (520, 452), (530, 474), (436, 474)]),
                ("poly", tube([(610, 285), (640, 350), (650, 452)], 15, 9))]
        far = [("poly", tube([(420, 280), (440, 380), (418, 458)], 40, 14)), ("poly", tube([(580, 290), (600, 360), (606, 452)], 12, 8))]
        return near, far, [], (742, 128)
    raise ValueError(kind)


def _shape_mask(shapes, size, P):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    for kind, data in shapes:
        if kind == "poly":
            d.polygon([P(p) for p in data], fill=255)
        else:
            a, b = P((data[0], data[1])), P((data[2], data[3]))
            d.ellipse([min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])], fill=255)
    return m


def paint_creature(im, kind, x0, y0, s, seed, base, rim=(250, 160, 80), flip=False, detail=True, outline=True):
    w, h = im.size

    def P(p):
        return (x0 + ((1000 - p[0]) if flip else p[0]) * s, y0 + p[1] * s)
    near, far, bone, eye = creature(kind)
    fm = _shape_mask(far, (w, h), P)
    im.paste(Image.new("RGB", (w, h), tuple(int(c * 0.5) for c in base)), (0, 0), fm)
    m = _shape_mask(near, (w, h), P)
    bb = m.getbbox()
    if bb is None:
        return
    y_a, y_b = bb[1] / h, bb[3] / h
    g = grad_v(w, h, [(0, tuple(int(c * 0.6) for c in base)), (y_a, tuple(int(c * 0.62) for c in base)),
                      (y_a + (y_b - y_a) * 0.45, base), (y_a + (y_b - y_a) * 0.7, tuple(min(255, int(c * 1.3)) for c in base)),
                      (1, tuple(int(c * 0.7) for c in base))])
    if detail:
        g = mul(g, 0.8 + 0.4 * fbm(w, h, seed, max(2.0, 24 * s), 4))
    im.paste(g, (0, 0), m)
    d = ImageDraw.Draw(im)
    if detail:
        rng = R(seed)
        # mottled skin: soft darker blotches and pale speckle
        bl = Image.new("L", (w, h), 0)
        db = ImageDraw.Draw(bl)
        for _ in range(int(60 + 400 * s)):
            x, y = rng.uniform(bb[0], bb[2]), rng.uniform(bb[1], bb[1] + (bb[3] - bb[1]) * 0.6)
            r = rng.uniform(3, 14) * s * 2
            db.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], fill=int(rng.uniform(40, 110)))
        bl = ImageChops.multiply(bl.filter(ImageFilter.GaussianBlur(2 * s + 0.5)), m)
        im.paste(Image.new("RGB", (w, h), tuple(int(c * 0.45) for c in base)), (0, 0), bl)
        if kind == "cera":
            # frill colour patch
            fr = _shape_mask([("ell", (676, 56, 786, 196))], (w, h), P).filter(ImageFilter.GaussianBlur(6 * s))
            im.paste(Image.new("RGB", (w, h), (170, 70, 50)), (0, 0), ImageChops.multiply(fr, m).point(lambda v: int(v * 0.6)))
        bm = _shape_mask(bone, (w, h), P)
        im.paste(Image.new("RGB", (w, h), (226, 214, 184)), (0, 0), bm)
        ex, ey = P(eye)
        r = max(1.5, 8 * s)
        d.ellipse([ex - r, ey - r * 0.8, ex + r, ey + r * 0.8], fill=(24, 18, 10))
        d.ellipse([ex - r * 0.35, ey - r * 0.5, ex + r * 0.15, ey], fill=(220, 200, 150))
    top = ImageChops.subtract(m, ImageChops.offset(m, 0, max(2, int(10 * s)))).filter(ImageFilter.GaussianBlur(max(1, 3 * s)))
    im.paste(Image.new("RGB", (w, h), rim), (0, 0), top.point(lambda v: int(v * 0.8)))
    bot = ImageChops.subtract(m, ImageChops.offset(m, 0, -max(2, int(16 * s)))).filter(ImageFilter.GaussianBlur(max(1, 5 * s)))
    im.paste(Image.new("RGB", (w, h), (24, 14, 20)), (0, 0), bot.point(lambda v: int(v * 0.6)))
    if outline:
        edge = ImageChops.subtract(m.filter(ImageFilter.MaxFilter(3)), m)
        im.paste(Image.new("RGB", (w, h), (28, 16, 24)), (0, 0), edge)


def pterosaur(im, cx, cy, s, col, flip=False):
    d = ImageDraw.Draw(im)
    k = -1 if flip else 1

    def P(x, y):
        return (cx + k * x * s, cy + y * s)
    d.polygon([P(-10, 0), P(-120, -60), P(-260, -40), P(-150, -10), P(-60, 20)], fill=col)
    d.polygon([P(10, 0), P(110, -70), P(250, -60), P(140, -12), P(60, 18)], fill=col)
    d.ellipse([min(P(-40, -10)[0], P(40, 14)[0]), P(-40, -10)[1], max(P(-40, -10)[0], P(40, 14)[0]), P(40, 14)[1]], fill=col)
    d.polygon([P(30, -6), P(110, 2), P(36, 8)], fill=col)
    d.polygon([P(36, -4), P(10, -36), P(26, -2)], fill=col)


def lightning(im, x0, y0, x1, y1, seed, width=3):
    rng = R(seed)
    pts = [(x0, y0)]
    n = 12
    for i in range(1, n):
        t = i / n
        pts.append((x0 + (x1 - x0) * t + rng.uniform(-28, 28), y0 + (y1 - y0) * t + rng.uniform(-8, 8)))
    pts.append((x1, y1))
    glow = Image.new("L", im.size, 0)
    dg = ImageDraw.Draw(glow)
    dg.line(pts, fill=255, width=width * 6, joint="curve")
    br = pts[5]
    bp = [br, (br[0] + 40, br[1] + 40), (br[0] + 30, br[1] + 90)]
    dg.line(bp, fill=200, width=width * 4)
    glow = glow.filter(ImageFilter.GaussianBlur(width * 4))
    im.paste(Image.new("RGB", im.size, (190, 150, 255)), (0, 0), glow.point(lambda v: int(v * 0.7)))
    d = ImageDraw.Draw(im)
    d.line(pts, fill=(250, 246, 255), width=width, joint="curve")
    d.line(bp, fill=(236, 226, 255), width=max(1, width - 1))


def mesa(im, pts, seed, base=(196, 92, 52), shade=(110, 44, 46), rim=(255, 170, 90), strata=True):
    """A layered sandstone butte; lit from the sunset on its left edge."""
    w, h = im.size
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    bb = m.getbbox()
    rng = np.random.default_rng(seed)
    yy = np.arange(h)[:, None]
    band = 0.84 + 0.16 * np.sin(yy / 7.0 + rng.random() * 6) * np.sin(yy / 23.0)
    xx = np.arange(w)[None, :]
    shadef = np.clip((xx - (bb[0] + (bb[2] - bb[0]) * 0.55)) / ((bb[2] - bb[0]) * 0.3 + 1), 0, 1)
    a = np.zeros((h, w, 3), np.float32)
    for c in range(3):
        a[:, :, c] = (base[c] * (1 - shadef) + shade[c] * shadef) * (band if strata else 1)
    a *= (0.85 + 0.3 * fbm(w, h, seed + 3, 20, 3))[:, :, None]
    im.paste(Image.fromarray(a.clip(0, 255).astype(np.uint8)), (0, 0), m)
    top = ImageChops.subtract(m, ImageChops.offset(m, 0, 5)).filter(ImageFilter.GaussianBlur(1.5))
    im.paste(Image.new("RGB", (w, h), rim), (0, 0), top)


def canyon_sky(W, H, horizon):
    im = grad_v(W, H, [(0, (26, 14, 52)), (horizon * 0.45, (66, 30, 96)), (horizon * 0.8, (190, 70, 96)), (horizon, (250, 150, 70)), (1, (250, 150, 70))])
    d = ImageDraw.Draw(im)
    rng = R(int(W + horizon * 100))
    for _ in range(int(W / 12)):
        y = rng.uniform(0.04, 0.6) * horizon * H
        x = rng.uniform(-80, W)
        L = rng.uniform(60, 240) * W / 1024
        t = y / (horizon * H)
        c = (int(40 + 120 * t), int(22 + 40 * t), int(60 + 30 * t))
        d.line([(x, y), (x + L, y + rng.uniform(-5, 5))], fill=c, width=int(rng.uniform(5, 16) * W / 1024) + 1)
    return im


# ------------------------------------------------------------------ textures
def side_art():
    """Side panel: covers the flat side, 1.965 m (z) x 1.46 m (y = 1.80 .. 0.34) -> 1024 x 692.
    Art down to y = 0.72 (row 512); charcoal lower body below (chrome strip on the line).
    Front of the machine (screen end) at u = 1; the left side shows it mirrored."""
    W, H = 1024, 692
    ART = 512
    hz = 300
    im = canyon_sky(W, H, hz / H)
    d = ImageDraw.Draw(im)
    d.ellipse([600, 250, 700, 350], fill=(255, 214, 140))
    lightning(im, 720, 40, 790, 250, 7, 3)
    lightning(im, 150, 70, 110, 240, 8, 2)
    # distant volcano with a lava glow and ash plume
    d = ImageDraw.Draw(im)
    rng = R(12)
    for i in range(30):
        t = i / 30
        x = 430 + t * 120 + rng.uniform(-14, 14)
        y = 196 - t * 170
        r = 14 + t * 46
        c = int(70 + 30 * t)
        d.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], fill=(c, c - 20, c + 20))
    d.polygon([(320, 320), (410, 210), (446, 196), (470, 202), (560, 320)], fill=(92, 54, 96))
    d.polygon([(410, 210), (446, 196), (470, 202), (452, 230), (430, 260)], fill=(250, 110, 40))
    im = im.filter(ImageFilter.GaussianBlur(1.2))
    # buttes and the canyon walls
    mesa(im, [(-10, 330), (-10, 170), (90, 160), (200, 168), (210, 190), (250, 330)], 21)
    mesa(im, [(560, 330), (610, 230), (700, 220), (720, 240), (760, 330)], 22, base=(176, 84, 60), rim=(250, 160, 100))
    mesa(im, [(770, 340), (800, 150), (900, 140), (1034, 150), (1034, 340)], 23)
    d = ImageDraw.Draw(im)
    # canyon floor and river
    d.rectangle([0, 320, W, ART], fill=(176, 112, 70))
    d.polygon([(0, 330), (W, 322), (W, 344), (0, 352)], fill=(140, 84, 64))
    d.polygon([(330, 335), (560, 335), (700, 380), (1024, 400), (1024, 440), (640, 420), (420, 380), (300, 350)], fill=(150, 110, 170))
    d.polygon([(380, 345), (540, 345), (650, 380), (900, 405), (650, 395), (430, 368)], fill=(236, 170, 140))
    # far giants, herd, a big horned plant-eater in front, fliers
    for (x, s, fl) in [(330, 0.10, False), (440, 0.08, True)]:
        paint_creature(im, "sauro", x, 286, s, 31, (120, 82, 112), rim=(250, 170, 120), flip=fl, detail=False, outline=False)
    for i, (x, y, s) in enumerate([(640, 300, 0.20), (760, 316, 0.22), (880, 300, 0.19)]):
        paint_creature(im, "hadro", x, y, s, 40 + i, (150, 104, 70), rim=(255, 190, 120), flip=True, detail=True)
    paint_creature(im, "cera", 40, 214, 0.58, 50, (118, 104, 70), rim=(255, 176, 96))
    for (x, y, s, fl) in [(560, 110, 0.18, False), (640, 80, 0.12, True), (930, 210, 0.10, False)]:
        pterosaur(im, x, y, s, (34, 18, 40), fl)
    # foreground cycads and boulders
    d = ImageDraw.Draw(im)
    for (x, y, r) in [(560, 500, 40), (980, 492, 50), (300, 506, 30)]:
        d.ellipse([x - r * 1.4, y - r, x + r * 1.4, y + r], fill=(84, 46, 44))
        d.ellipse([x - r * 1.2, y - r * 0.95, x + r * 0.6, y - r * 0.2], fill=(140, 76, 60))
    foliage(im, 24, ART + 10, 10, (36, 44, 30), 120, 8)
    im = im.filter(ImageFilter.ModeFilter(3))
    im = brushwork(im, 41, 16000, 4, 12, 2, 4, 8, angle=-0.2, spread=1.4)
    im = im.filter(ImageFilter.SMOOTH)
    # lower body charcoal, chrome line, top silver pinstripe
    a = np.asarray(im).astype(np.float32)
    ch = (34 + 10 * fbm(W, H - ART, 61, 30, 3))
    a[ART:, :, 0] = ch
    a[ART:, :, 1] = ch
    a[ART:, :, 2] = ch * 1.06
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    for i, c in enumerate([(120, 120, 126), (210, 212, 218), (250, 250, 252), (170, 172, 178), (90, 90, 96)]):
        d.line([(0, ART - 4 + i * 2), (W, ART - 4 + i * 2)], fill=c, width=2)
    d.rectangle([0, ART + 20, W, ART + 24], fill=(120, 60, 170))
    for i, c in enumerate([(150, 150, 156), (240, 240, 244), (130, 130, 136)]):
        d.line([(0, i * 2), (W, i * 2)], fill=c, width=2)
    # wear: scuffs on the lower body, chips at the bottom, a faded patch
    wear = Image.new("L", (W, H), 0)
    dw = ImageDraw.Draw(wear)
    for _ in range(90):
        x = rng.uniform(0, W)
        y = H - abs(rng.gauss(0, 60)) - 4
        if rng.random() < 0.25:
            x = abs(rng.gauss(0, 40))
            y = rng.uniform(ART - 100, H)
        L = rng.uniform(4, 24)
        an = rng.uniform(-0.4, 0.4)
        dw.line([(x, y), (x + math.cos(an) * L, y + math.sin(an) * L)], fill=int(rng.uniform(20, 70)), width=1)
    for _ in range(14):
        x, y = rng.uniform(0, W), rng.uniform(H - 50, H - 4)
        r = rng.uniform(1.0, 2.5)
        dw.ellipse([x - r, y - r, x + r, y + r], fill=110)
    im.paste(Image.new("RGB", (W, H), (190, 188, 182)), (0, 0), wear)
    fade = (fbm(W, H, 77, 200, 2) * 0.10).astype(np.float32)
    a = np.asarray(im).astype(np.float32)
    a = a * (1 - fade[:, :, None]) + 200 * fade[:, :, None]
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    save(im, "ride_side.png", colors=256)


def title_decal():
    """Title decal on each side and the screen end: 1.40 x 0.35 m -> 1024 x 256 RGBA (alpha-scissored)."""
    im = logo(1024, 256, sub=True)
    rng = R(5)
    a = im.getchannel("A")
    d = ImageDraw.Draw(a)
    for _ in range(30):
        x, y = rng.uniform(0, 1024), rng.uniform(0, 256)
        d.ellipse([x - 2, y - 1, x + 2, y + 1], fill=0)
    im.putalpha(a)
    save(im, "ride_title.png", colors=128)


def marquee():
    """Backlit translucent marquee: 1.20 x 0.30 m -> 1024 x 256."""
    W, H = 1024, 256
    im = canyon_sky(W, H, 0.82)
    lightning(im, 120, 0, 70, 150, 9, 3)
    lightning(im, 930, 0, 980, 120, 10, 2)
    mesa(im, [(-10, 256), (-10, 150), (60, 140), (150, 150), (170, 256)], 51, base=(120, 50, 60), shade=(60, 24, 40), strata=False)
    mesa(im, [(850, 256), (880, 130), (960, 124), (1034, 130), (1034, 256)], 52, base=(120, 50, 60), shade=(60, 24, 40), strata=False)
    paint_creature(im, "sauro", 840, 120, 0.26, 53, (40, 24, 40), rim=(255, 170, 110), flip=True, detail=False)
    paint_creature(im, "cera", -30, 132, 0.24, 54, (40, 24, 40), rim=(255, 170, 110), detail=False)
    pterosaur(im, 180, 40, 0.14, (30, 14, 36))
    pterosaur(im, 860, 50, 0.10, (30, 14, 36), True)
    lg = logo(820, 205, sub=True)
    im.paste(lg, (102, 14), lg)
    yy = np.linspace(0, 1, H)[:, None]
    xx = np.linspace(0, 1, W)[None, :]
    tubes = 0.84 + 0.18 * np.exp(-((yy - 0.3) / 0.12) ** 2) + 0.18 * np.exp(-((yy - 0.72) / 0.12) ** 2)
    edge = np.minimum(1, np.minimum(xx, 1 - xx) * 14) * 0.25 + 0.75
    im = mul(im, (tubes * edge).astype(np.float32))
    save(gamma(im, 1.1), "ride_marquee.png", colors=220)


def screen():
    """The game on the projection screen: 1.00 x 0.75 m (4:3) -> 512 x 384. An original canyon
    river level: fliers swooping, a horned plant-eater on the far bank. No vehicle."""
    W, H = 512, 384
    im = canyon_sky(W, H, 0.45)
    lightning(im, 400, 0, 430, 120, 11, 2)
    mesa(im, [(-10, 200), (-10, 90), (80, 80), (140, 90), (160, 200)], 61)
    mesa(im, [(360, 200), (380, 100), (470, 96), (522, 100), (522, 200)], 62)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 172, W, H], fill=(170, 110, 70))
    # the river coming toward the viewer
    d.polygon([(220, 176), (300, 176), (480, H), (40, H)], fill=(110, 90, 160))
    d.polygon([(246, 178), (276, 178), (330, H), (190, H)], fill=(200, 150, 170))
    paint_creature(im, "cera", 320, 132, 0.15, 63, (124, 108, 70), rim=(255, 190, 120), flip=True)
    paint_creature(im, "hadro", 30, 148, 0.10, 64, (150, 104, 70), rim=(255, 190, 120))
    pterosaur(im, 250, 120, 0.42, (60, 34, 50))
    pterosaur(im, 120, 70, 0.18, (50, 30, 50), True)
    # foreground rocks (the riders are in a boat-less canyon gully: just rocks and ferns)
    for (x, y, r) in [(40, 370, 70), (470, 362, 80), (140, 384, 50)]:
        d.ellipse([x - r * 1.3, y - r, x + r * 1.3, y + r], fill=(90, 50, 46))
        d.ellipse([x - r * 1.1, y - r * 0.95, x + r * 0.5, y - r * 0.2], fill=(150, 86, 64))
    foliage(im, 65, H + 20, 5, (30, 50, 30), 110, 0)
    d = ImageDraw.Draw(im)
    for (x, y, c) in [(258, 112, (255, 60, 40)), (180, 250, (60, 140, 255))]:
        d.ellipse([x - 14, y - 14, x + 14, y + 14], outline=c, width=3)
        for dx, dy in [(-22, 0), (22, 0), (0, -22), (0, 22)]:
            d.line([(x + dx * 0.4, y + dy * 0.4), (x + dx, y + dy)], fill=c, width=3)
    d.ellipse([248, 102, 268, 120], fill=(255, 240, 160))
    f = font(F_COND, 18)
    fs = font(F_COND, 13)
    d.text((14, 8), "1P", font=f, fill=(255, 80, 60))
    d.text((40, 8), "0042650", font=f, fill=(255, 250, 230))
    d.text((W - 14, 8), "2P", font=f, fill=(90, 150, 255), anchor="ra")
    d.text((W - 44, 8), "0018300", font=f, fill=(255, 250, 230), anchor="ra")
    text_c(d, (W / 2, 18), "STAGE 2  RED CANYON", fs, (255, 230, 120))
    for i in range(8):
        d.rectangle([14 + i * 9, 34, 20 + i * 9, 48], fill=(255, 210, 60) if i < 6 else (90, 70, 30))
        d.rectangle([W - 20 - i * 9, 34, W - 14 - i * 9, 48], fill=(255, 210, 60) if i < 3 else (90, 70, 30))
    d.rectangle([150, 360, 362, 372], outline=(255, 255, 255), width=2)
    d.rectangle([152, 362, 290, 370], fill=(240, 60, 30))
    text_c(d, (W / 2, 352), "DANGER", fs, (255, 255, 255))
    im = im.filter(ImageFilter.SMOOTH)
    a = np.asarray(im).astype(np.float32)
    lines = np.where(np.arange(H) % 3 == 2, 0.68, 1.0)[:, None, None]
    yy = np.linspace(-1, 1, H)[:, None]
    xx = np.linspace(-1, 1, W)[None, :]
    vig = 1 - 0.35 * (xx ** 2 + yy ** 2) ** 1.4
    a = a * lines * vig[:, :, None]
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    bloom = im.filter(ImageFilter.GaussianBlur(4))
    im = ImageChops.add(im, bloom.point(lambda v: int(v * 0.25)))
    save(im, "ride_screen.png", colors=180)


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
    d.rectangle([256, 0, 511, 85], fill=(88, 40, 140))
    d.rectangle([262, 6, 505, 79], outline=(255, 150, 50), width=3)
    text_c(d, (384, 44), "2 PLAYERS", font(F_HEAVY, 46), (255, 240, 214))
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
        d.line([(x, y), (x + math.cos(a) * L, y + math.sin(a) * L)], fill=(min(255, c * 5), c * 3, c * 2), width=1)
    save(im, "ride_paint.png", colors=64)


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
    """Seat vinyl, tiles every 0.33 m -> 256 px: deep purple, pleated channels (2 per tile),
    fine grain, rubbed-pale creases where riders slide in."""
    S = 256
    x = np.arange(S)[None, :].astype(np.float32)
    ch = 0.80 + 0.28 * np.sin(x / S * 2 * math.pi * 2 - math.pi / 2) ** 2   # padded channels
    seam = 1 - 0.55 * np.exp(-((((x + 64) % 128) - 64) / 2.2) ** 2)          # stitched seams
    g = noise(S, S, 141, 1.2)
    big = fbm(S, S, 142, 60, 2)
    k = ch * seam * (0.94 + 0.10 * g) * (0.85 + 0.3 * big)
    base = np.array([70, 34, 98], np.float32)
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


def rear_tex():
    """Two-tone end walls (rear and screen end) and the shell's flat lower sides:
    u = x in metres (tiles), v = (2.10 - y) / 1.76 -> 256 x 512. Orange above y = 0.72
    (row 401), a chrome line and purple pinstripe, charcoal below."""
    W, H = 256, 512
    cut = int((2.10 - 0.72) / 1.76 * H)
    n = fbm(W, H, 181, 64, 2)
    peel = noise(W, H, 182, 1.5)
    a = np.zeros((H, W, 3), np.float32)
    for c in range(3):
        a[:cut, :, c] = PAINT[c] * (0.9 + 0.16 * n[:cut] + 0.05 * peel[:cut])
        a[cut:, :, c] = CHAR[c] * (0.9 + 0.3 * n[cut:])
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    d.rectangle([0, cut - 12, W, cut - 9], fill=(120, 60, 170))
    for i, c in enumerate([(120, 120, 126), (210, 212, 218), (250, 250, 252), (170, 172, 178), (90, 90, 96)]):
        d.line([(0, cut - 4 + i * 2), (W, cut - 4 + i * 2)], fill=c, width=2)
    rng = R(183)
    for _ in range(60):
        x, y = rng.uniform(0, W), rng.uniform(cut + 8, H)
        L = rng.uniform(3, 16)
        c = int(rng.uniform(60, 100))
        d.line([(x, y), (x + L, y + rng.uniform(-2, 2))], fill=(c, c, c), width=1)
    save(im, "ride_rear.png", colors=64)


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
    rear_tex()
    old = os.path.join(OUT, "ride_hazard.png")   # retired with the green/hazard look
    if os.path.exists(old):
        os.remove(old)
    tot = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT) if f.startswith("ride_"))
    print("total %.0f KB" % (tot / 1024))
