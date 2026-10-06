"""Paints the textures of the Pocket Change basketball cage game (module `hoops`).

A 1990s ticket-redemption basketball cage: black laminate cabinet, red powder-coated
steel cage with red wire mesh, white backboard with an orange rim and white net,
red 7-segment LED SCORE / TIME displays, a fluorescent-lit header with original art.
The invented title is "BAYOU BUCKETS"; no real game's name, logo or artwork is used.

Every texture is drawn for a known physical size (see hoops.gd for the UVs).
Run from the project folder:  python3 tools/stores/pocket_change/paint_hoops.py
Writes tex/pc/hoops_*.png. Seeded, so re-running reproduces the same files.
"""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(PROJ, "tex", "pc")
os.makedirs(OUT, exist_ok=True)

F_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_BC = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"
F_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_BI = "/usr/share/fonts/truetype/google-fonts/Poppins-BoldItalic.ttf"
F_LB = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def font(p, s):
    return ImageFont.truetype(p, s)


def save(im, name):
    p = os.path.join(OUT, "hoops_%s.png" % name)
    im.save(p, optimize=True)
    print("hoops_%s.png" % name, im.size, os.path.getsize(p))


def noise(w, h, cell, seed, octaves=3):
    """Smooth value noise in [0, 1], shape (h, w)."""
    rs = np.random.RandomState(seed)
    acc = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        c = max(1, int(cell / (2 ** o)))
        gw, gh = w // c + 2, h // c + 2
        g = rs.rand(gh, gw).astype(np.float32)
        im = Image.fromarray((g * 255).astype(np.uint8)).resize((gw * c, gh * c), Image.BICUBIC)
        acc += np.asarray(im, np.float32)[:h, :w] / 255.0 * amp
        tot += amp
        amp *= 0.5
    return acc / tot


def grain(w, h, seed, k):
    rs = np.random.RandomState(seed)
    return (rs.rand(h, w).astype(np.float32) - 0.5) * k


def to_img(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def shade(im, mult):
    """Multiplies an RGB image by a (h, w) array."""
    a = np.asarray(im, np.float32)
    a[..., :3] *= mult[..., None]
    return to_img(a)


def text_c(d, xy, s, f, fill, anchor="mm", **kw):
    d.text(xy, s, font=f, fill=fill, anchor=anchor, **kw)


def scuffs(im, seed, n, area=None, col=(150, 150, 150), alpha=60, lmax=40):
    """Thin pale scratches."""
    rnd = random.Random(seed)
    w, h = im.size
    x0, y0, x1, y1 = area or (0, 0, w, h)
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        a = rnd.uniform(-0.6, 0.6) + (math.pi if rnd.random() < 0.5 else 0)
        l = rnd.uniform(4, lmax)
        d.line([x, y, x + math.cos(a) * l, y + math.sin(a) * l], fill=col + (rnd.randint(alpha // 3, alpha),), width=1)
    return Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")


def smudges(im, seed, n, area=None, col=(255, 255, 255), alpha=18, rmax=14):
    """Soft greasy fingerprints / ball marks."""
    rnd = random.Random(seed)
    w, h = im.size
    x0, y0, x1, y1 = area or (0, 0, w, h)
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        r = rnd.uniform(rmax * 0.4, rmax)
        d.ellipse([x - r, y - r * 0.8, x + r, y + r * 0.8], fill=col + (rnd.randint(alpha // 2, alpha),))
    ov = ov.filter(ImageFilter.GaussianBlur(2))
    return Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")


def laminate(w, h, seed, base=(26, 25, 28), k=6):
    """Black textured (orange-peel) laminate."""
    n = noise(w, h, 24, seed, 3)
    g = grain(w, h, seed + 1, 3)
    a = np.zeros((h, w, 3), np.float32)
    for i in range(3):
        a[..., i] = base[i] + (n - 0.5) * k + g
    return to_img(a)


# ---------------------------------------------------------------- 7-segment digits
SEG = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd",
       "6": "afgedc", "7": "abc", "8": "abcdefg", "9": "abcdfg", "-": "g", " ": ""}


def seg_digit(d, x, y, w, h, ch, on, off, t=None, slant=0.12):
    """One 7-segment digit, top-left (x, y), w x h px, slanted like real LED digits."""
    t = t or max(3, int(w * 0.17))
    def P(px, py):   # slant: top leans right
        return (x + px + (h - py) * slant, y + py)
    hm = h / 2
    segs = {
        "a": [(t, 0), (w - t, 0), (w - t * 1.6, t), (t * 1.6, t)],
        "d": [(t * 1.6, h - t), (w - t * 1.6, h - t), (w - t, h), (t, h)],
        "g": [(t, hm), (t * 1.6, hm - t / 2), (w - t * 1.6, hm - t / 2), (w - t, hm), (w - t * 1.6, hm + t / 2), (t * 1.6, hm + t / 2)],
        "f": [(0, t), (t, t * 1.6), (t, hm - t * 0.8), (0, hm - t * 0.3)],
        "b": [(w, t), (w, hm - t * 0.3), (w - t, hm - t * 0.8), (w - t, t * 1.6)],
        "e": [(0, hm + t * 0.3), (t, hm + t * 0.8), (t, h - t * 1.6), (0, h - t)],
        "c": [(w, hm + t * 0.3), (w, h - t), (w - t, h - t * 1.6), (w - t, hm + t * 0.8)],
    }
    lit = SEG.get(ch, "")
    for k, pts in segs.items():
        d.polygon([P(px, py) for px, py in pts], fill=on if k in lit else off)


# ---------------------------------------------------------------- textures
def paint_mesh():
    """Red powder-coated welded wire mesh, 50 mm squares, 4 x 4 per tile (0.20 m)."""
    S = 256
    cell = S // 4
    a = np.zeros((S, S, 4), np.float32)
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    wr = 3.1   # wire half-width, px (about 4 mm wire)
    def wire(dist):
        m = np.clip(1.0 - np.maximum(dist - wr + 1.0, 0.0), 0, 1)
        # round wire: brighter in the middle
        hl = np.clip(1.0 - dist / wr, 0, 1)
        return m, hl
    dx = np.abs(((xx + cell / 2) % cell) - cell / 2)
    dy = np.abs(((yy + cell / 2) % cell) - cell / 2)
    mx, hx = wire(dx)
    my, hy = wire(dy)
    al = np.maximum(mx, my)
    hl = np.maximum(hx * mx, hy * my)
    col = np.array([150, 18, 22], np.float32)
    n = noise(S, S, 32, 11, 2)
    for i in range(3):
        a[..., i] = col[i] * (0.55 + 0.75 * hl) * (0.85 + 0.3 * n)
    # welds: little dark blobs at crossings
    cross = (dx < wr * 1.4) & (dy < wr * 1.4)
    a[..., :3][cross] *= 0.8
    a[..., 3] = al * 255
    save(to_img(a), "mesh")


def paint_net():
    """White nylon net, diamond knots. u wraps the hoop (12 loops), v runs down 0.34 m."""
    W, H = 256, 256
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    loops, rows = 6, 5          # per texture; hoops.gd repeats u twice around the ring
    cw, rh = W / loops, H / rows
    rnd = random.Random(5)
    col = (236, 234, 226, 255)
    for r in range(rows + 1):
        for c in range(loops + 1):
            off = (cw / 2) if r % 2 else 0
            x, y = c * cw + off, r * rh
            for dx in (-cw / 2, cw / 2):
                jx = rnd.uniform(-2, 2)
                d.line([x, y, x + dx + jx, y + rh], fill=col, width=5)
    # cord shading
    a = np.asarray(im, np.float32)
    n = noise(W, H, 20, 6, 2)
    a[..., :3] *= (0.78 + 0.25 * n)[..., None]
    im = to_img(a)
    # the top band where the net loops over the rim hooks
    d = ImageDraw.Draw(im)
    for c in range(loops * 2):
        x = (c + 0.5) * W / (loops * 2)
        d.ellipse([x - 5, 0, x + 5, 12], outline=col, width=3)
    save(im, "net")


def paint_ball():
    """Orange rubber mini basketball, equirectangular (u around, v pole to pole)."""
    W, H = 512, 256
    n = noise(W, H, 3, 21, 1)
    g = grain(W, H, 22, 26)
    base = np.array([214, 92, 28], np.float32)
    a = np.zeros((H, W, 3), np.float32)
    dirt = noise(W, H, 64, 23, 3)
    for i in range(3):
        a[..., i] = base[i] * (0.9 + 0.14 * n) + g * 0.25
    a *= (0.86 + 0.18 * dirt)[..., None]
    im = to_img(a)
    d = ImageDraw.Draw(im)
    blk = (22, 16, 14)
    lw = 5
    # equator and the meridian circle (u = 0 / 0.5 and 0.25 / 0.75)
    d.line([0, H / 2, W, H / 2], fill=blk, width=lw)
    for u in (0.0, 0.5, 1.0):
        d.line([u * W, 0, u * W, H], fill=blk, width=lw * 2 if u in (0.0, 1.0) else lw)
    # the two curved seams: small circles of angular radius rho round (lat 0, u = 0.25 / 0.75)
    rho = math.radians(52)
    for uc in (0.25, 0.75):
        for sgn in (-1, 1):
            line = []
            for k in range(121):
                lat = (k / 120.0 * 2 - 1) * rho * 0.999
                dl = math.acos(min(1.0, math.cos(rho) / math.cos(lat)))
                line.append(((uc + sgn * dl / (2 * math.pi)) * W, (0.5 - lat / math.pi) * H))
            d.line(line, fill=blk, width=lw)
    # a faded generic stamp
    f = font(F_BC, 14)
    text_c(d, (W * 0.37, H * 0.42), "OFFICIAL", f, (120, 50, 20))
    text_c(d, (W * 0.37, H * 0.58), "SIZE 3", f, (120, 50, 20))
    im = im.filter(ImageFilter.GaussianBlur(0.6))
    save(im, "ball")


def paint_marquee():
    """Header: 0.98 x 0.34 m translucent backlit plastic. Original art: BAYOU BUCKETS."""
    W, H = 1024, 352
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # night-sky gradient
    top = np.array([16, 22, 92], np.float32)
    bot = np.array([58, 10, 70], np.float32)
    t = (yy / H)[..., None]
    a = top * (1 - t) + bot * t
    # starburst rays from the ball
    bx, by = 168, 168
    ang = np.arctan2(yy - by, xx - bx)
    rays = (np.sin(ang * 18) > 0.25).astype(np.float32)
    dist = np.hypot(xx - bx, yy - by)
    fall = np.clip(1.0 - dist / 900.0, 0, 1)
    a += (rays * fall * 50)[..., None] * np.array([1.0, 0.7, 0.9])
    glow = np.exp(-(dist / 190.0) ** 2)
    a += glow[..., None] * np.array([150, 90, 30])
    im = to_img(a)
    d = ImageDraw.Draw(im, "RGBA")
    rnd = random.Random(31)
    # sparkle stars
    def star(cx, cy, r, col):
        pts = []
        for k in range(8):
            rr = r if k % 2 == 0 else r * 0.28
            aa = k * math.pi / 4
            pts.append((cx + math.cos(aa) * rr, cy + math.sin(aa) * rr))
        d.polygon(pts, fill=col)
    for _ in range(26):
        x, y = rnd.uniform(330, 1010), rnd.uniform(8, 340)
        star(x, y, rnd.uniform(4, 11), (255, 250, 210, rnd.randint(150, 240)))
    # speed lines behind the ball
    for k in range(6):
        y = by - 70 + k * 28
        d.line([20, y + 18, bx - 120 + k * 6, y], fill=(255, 210, 90, 120), width=6)
    # the basketball
    R = 128
    ball = Image.new("RGBA", (2 * R + 4, 2 * R + 4), (0, 0, 0, 0))
    bd = ImageDraw.Draw(ball)
    bd.ellipse([2, 2, 2 * R + 2, 2 * R + 2], fill=(236, 110, 24, 255))
    ba = np.asarray(ball, np.float32)
    by_, bx_ = np.mgrid[0:2 * R + 4, 0:2 * R + 4].astype(np.float32)
    shade_ = np.clip(1.25 - np.hypot(bx_ - R * 0.7, by_ - R * 0.6) / (2.1 * R), 0.45, 1.25)
    ba[..., :3] *= shade_[..., None]
    ball = to_img(ba)
    bd = ImageDraw.Draw(ball)
    k = (30, 14, 8, 255)
    c = R + 2
    bd.line([c - R * 0.98, c + 10, c + R * 0.98, c - 10], fill=k, width=7)
    bd.line([c + 12, c - R, c - 12, c + R], fill=k, width=7)
    bd.arc([c - R * 1.9, c - R * 1.2, c - R * 0.15, c + R * 1.2], -50, 50, fill=k, width=7)
    bd.arc([c + R * 0.15, c - R * 1.2, c + R * 1.9, c + R * 1.2], 130, 230, fill=k, width=7)
    bd.ellipse([2, 2, 2 * R + 2, 2 * R + 2], outline=(30, 14, 8, 255), width=5)
    im.paste(ball, (bx - c, by - c), ball)
    # title
    def title(txt, cx, cy, size):
        f = font(F_BI, size)
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).text((cx, cy), txt, font=f, fill=255, anchor="mm")
        outer = m.filter(ImageFilter.MaxFilter(17))
        inner = m.filter(ImageFilter.MaxFilter(9))
        sh = outer.filter(ImageFilter.GaussianBlur(4))
        sh = ImageChops.offset(sh, 6, 7)
        im.paste((0, 0, 0), (0, 0), sh.point(lambda v: v * 0.7))
        im.paste((12, 8, 30), (0, 0), outer)
        im.paste((210, 24, 30), (0, 0), inner)
        gy = np.clip((np.mgrid[0:H, 0:W][0] - (cy - size * 0.45)) / (size * 0.9), 0, 1)
        g = np.zeros((H, W, 3), np.float32)
        g[..., 0] = 255
        g[..., 1] = 246 - 120 * gy
        g[..., 2] = 120 - 100 * gy
        im.paste(to_img(g), (0, 0), m)
        # highlight line across the top of the letters
        hl = ImageChops.subtract(m, ImageChops.offset(m, 0, 5))
        im.paste((255, 255, 235), (0, 0), hl.point(lambda v: v * 0.8))
    title("BAYOU", 610, 92, 118)
    title("BUCKETS", 664, 212, 118)
    # banner strip
    d = ImageDraw.Draw(im, "RGBA")
    d.polygon([(318, 278), (1004, 278), (990, 334), (304, 334)], fill=(14, 10, 26, 255))
    d.polygon([(324, 282), (998, 282), (986, 330), (310, 330)], fill=(220, 30, 30, 255))
    text_c(d, (650, 306), "BASKETBALL  ★  WIN TICKETS  ★  SCORE BIG", font(F_BC, 30), (255, 244, 200))
    # fluorescent backlight: two tubes behind, darker ends, a dim spot
    lum = 0.78 + 0.22 * np.exp(-((yy - H * 0.3) / 70) ** 2) + 0.18 * np.exp(-((yy - H * 0.72) / 70) ** 2)
    lum *= 0.82 + 0.18 * np.clip(np.minimum(xx, W - xx) / 140.0, 0, 1)
    lum *= 0.94 + 0.08 * noise(W, H, 90, 33, 2)
    im = shade(im, lum)
    # dust and fade toward warm
    a = np.asarray(im, np.float32)
    a = a * 0.93 + np.array([12, 8, 4])
    save(to_img(a), "marquee")


def paint_led():
    """Red 7-segment LED windows. 4 rows (machines 1-4), each 512 x 128:
    SCORE window = u 0..0.625 (3 digits), TIME window = u 0.6406..1.0 (2 digits)."""
    W, H = 512, 512
    im = Image.new("RGB", (W, H), (14, 2, 3))
    d = ImageDraw.Draw(im)
    rows = [("000", "60"), ("046", "17"), ("112", "00"), ("000", "60")]
    on, off = (255, 46, 30), (26, 4, 4)
    for r, (sc, tm) in enumerate(rows):
        y0 = r * 128
        # smoked acrylic: faint vertical gradient
        for yy in range(128):
            v = int(10 + 8 * (1 - yy / 128))
            d.line([0, y0 + yy, W, y0 + yy], fill=(v + 6, 2, 3))
        d.rectangle([320, y0, 328, y0 + 127], fill=(4, 1, 1))     # gap between windows
        dw, dh = 62, 92
        for i, ch in enumerate(sc):
            seg_digit(d, 40 + i * 86, y0 + 18, dw, dh, ch, on, off)
        for i, ch in enumerate(tm):
            seg_digit(d, 358 + i * 74, y0 + 18, dw - 6, dh, ch, on, off)
    a = np.asarray(im, np.float32)
    # LED bloom inside the acrylic + glare streak
    bl = np.asarray(im.filter(ImageFilter.GaussianBlur(6)), np.float32)
    a = a + bl * 0.45
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    glare = np.exp(-(((xx * 0.4 + (yy % 128) * 1.0) - 120) / 18) ** 2) * 18
    a += glare[..., None]
    save(to_img(a), "led")


def paint_panel():
    """Score panel face, 1.02 x 0.37 m (y 1.05..1.42), 512 x 186 -> 502 px/m."""
    W, H = 512, 186
    ppm = W / 1.02
    def X(x): return (x + 0.51) * ppm
    def Y(y): return (1.42 - y) * ppm
    im = laminate(W, H, 41, (22, 22, 26), 8)
    d = ImageDraw.Draw(im)
    # red pinstripe border
    d.rectangle([6, 6, W - 7, H - 7], outline=(170, 26, 30), width=3)
    # LED window bezels (the LED quads sit on top): score x -0.36..-0.035, time 0.065..0.26
    for (x0, x1) in ((-0.36, -0.035), (0.065, 0.26)):
        d.rectangle([X(x0) - 7, Y(1.335) - 7, X(x1) + 7, Y(1.205) + 7], fill=(8, 8, 9), outline=(90, 90, 96), width=2)
    f = font(F_B, 17)
    text_c(d, (X(-0.1975), Y(1.375)), "SCORE", f, (236, 232, 220))
    text_c(d, (X(0.1625), Y(1.375)), "TIME", f, (236, 232, 220))
    # speakers: round perforated grilles
    for sx in (-0.43, 0.405):
        cx, cy, r = X(sx), Y(1.27), 0.058 * ppm
        d.ellipse([cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4], fill=(60, 60, 66))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(12, 12, 14))
        for gy in range(-int(r), int(r) + 1, 5):
            for gx in range(-int(r), int(r) + 1, 5):
                if gx * gx + gy * gy < (r - 3) ** 2:
                    d.point([cx + gx, cy + gy], fill=(64, 64, 70))
        for s in range(4):   # four screws
            aa = s * math.pi / 2 + math.pi / 4
            d.ellipse([cx + math.cos(aa) * (r + 1) - 2, cy + math.sin(aa) * (r + 1) - 2, cx + math.cos(aa) * (r + 1) + 2, cy + math.sin(aa) * (r + 1) + 2], fill=(150, 150, 150))
    # bottom strip: instructions in the panel's silkscreen
    f2 = font(F_BC, 15)
    text_c(d, (X(0.0), Y(1.165)), "INSERT TOKEN  •  PUSH START  •  SHOOT!", f2, (250, 196, 40))
    f3 = font(F_BC, 12)
    text_c(d, (X(0.0), Y(1.10)), "2 POINTS EACH BASKET  •  3 POINTS LAST 10 SECONDS", f3, (210, 206, 196))
    # small orange ball logo left of the text
    for lx in (-0.43, 0.43):
        cx, cy, r = X(lx), Y(1.13), 10
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(232, 110, 26), outline=(20, 10, 6), width=2)
        d.line([cx - r, cy, cx + r, cy], fill=(20, 10, 6), width=2)
        d.line([cx, cy - r, cx, cy + r], fill=(20, 10, 6), width=2)
    im = smudges(im, 42, 40, (40, 40, W - 40, H), (200, 200, 210), 14, 12)
    im = scuffs(im, 43, 60, None, (130, 130, 136), 70, 18)
    save(im, "panel")


def paint_front():
    """Front of the lower cabinet, 1.02 x 0.90 m (y 0..0.90), 512 x 452 -> 502 px/m.
    The coin door, ticket bezel and START button are 3D parts placed over it."""
    W, H = 512, 452
    ppm = W / 1.02
    def X(x): return (x + 0.51) * ppm
    def Y(y): return (0.90 - y) * ppm
    im = laminate(W, H, 51, (24, 23, 27), 8)
    d = ImageDraw.Draw(im)
    # kick plate: scuffed black-painted steel, shoe marks
    d.rectangle([0, Y(0.11), W, H], fill=(30, 30, 33))
    d.line([0, Y(0.11), W, Y(0.11)], fill=(70, 70, 74), width=2)
    # red stripe band and white pinstripe, as on the sides
    d.rectangle([0, Y(0.20), W, Y(0.16)], fill=(178, 22, 28))
    d.rectangle([0, Y(0.225), W, Y(0.215)], fill=(230, 228, 220))
    # instruction card, left
    cx0, cy0, cx1, cy1 = X(-0.46), Y(0.74), X(-0.17), Y(0.36)
    d.rectangle([cx0, cy0, cx1, cy1], fill=(232, 226, 206), outline=(120, 116, 104), width=2)
    d.rectangle([cx0 + 4, cy0 + 4, cx1 - 4, cy0 + 26], fill=(196, 30, 34))
    text_c(d, ((cx0 + cx1) / 2, cy0 + 15), "HOW TO PLAY", font(F_B, 15), (255, 250, 240))
    lines = ["1. INSERT 1 TOKEN", "2. PUSH START", "3. SHOOT BASKETS UNTIL", "    TIME RUNS OUT", "4. SCORE MORE,", "    WIN MORE TICKETS!", "NO CLIMBING ON GAME"]
    f = font(F_BC, 10)
    for i, s in enumerate(lines):
        d.text((cx0 + 8, cy0 + 32 + i * 13), s, font=f, fill=(30, 28, 26))
    # ticket table under the card
    d.text((cx0 + 8, cy1 - 30), "20 PTS = 1  40 PTS = 3", font=font(F_BC, 10), fill=(60, 50, 40))
    d.text((cx0 + 8, cy1 - 17), "60 PTS = 6  80 PTS = 10", font=font(F_BC, 10), fill=(60, 50, 40))
    # TICKETS decal over the dispenser + START label
    text_c(d, (X(0.355), Y(0.66)), "TICKETS", font(F_B, 17), (250, 150, 30))
    d.polygon([(X(0.355) - 7, Y(0.635)), (X(0.355) + 7, Y(0.635)), (X(0.355), Y(0.62))], fill=(250, 150, 30))
    text_c(d, (X(0.355), Y(0.855)), "PUSH TO START", font(F_BC, 12), (240, 236, 220))
    # serial plate, bottom right
    sx, sy = X(0.30), Y(0.30)
    d.rectangle([sx, sy, sx + 60, sy + 26], fill=(168, 168, 160), outline=(90, 90, 86))
    d.text((sx + 4, sy + 3), "MODEL BB-4", font=font(F_BC, 9), fill=(30, 30, 30))
    d.text((sx + 4, sy + 13), "SER 950417", font=font(F_BC, 9), fill=(30, 30, 30))
    # wear: shoe scuffs low, fingerprints high, edges worn pale
    im = scuffs(im, 52, 140, (0, Y(0.11), W, H), (120, 116, 110), 90, 30)
    im = scuffs(im, 53, 70, (0, 0, W, Y(0.11)), (120, 120, 126), 60, 16)
    im = smudges(im, 54, 30, (0, 0, W, Y(0.6)), (200, 200, 210), 12, 14)
    a = np.asarray(im, np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    edge = np.clip(1 - np.minimum(xx, W - 1 - xx) / 6.0, 0, 1) * (0.6 + 0.4 * noise(W, H, 8, 55, 1))
    a += edge[..., None] * 60
    save(to_img(a), "front")


def paint_door():
    """Coin door plate, 0.30 x 0.44 m, 256 x 376. Two token entries, reject buttons,
    lock, coin-return cup. Pocket Change took its own brass tokens."""
    W, H = 256, 376
    ppm = W / 0.30
    n = noise(W, H, 40, 61, 2)
    brush = np.asarray(Image.fromarray((np.random.RandomState(62).rand(H, W) * 255).astype(np.uint8)).resize((W, H)).filter(ImageFilter.BoxBlur(0)), np.float32)
    brush = np.asarray(Image.fromarray(brush.astype(np.uint8)).filter(ImageFilter.GaussianBlur((6, 0)) if False else ImageFilter.BoxBlur(1)), np.float32)
    a = np.zeros((H, W, 3), np.float32)
    for i, c in enumerate((122, 124, 128)):
        a[..., i] = c * (0.82 + 0.25 * n) + (brush - 128) * 0.06
    im = to_img(a)
    d = ImageDraw.Draw(im)
    d.rectangle([2, 2, W - 3, H - 3], outline=(60, 60, 64), width=3)
    # two coin entries
    for k, cx in enumerate((0.085 * ppm, 0.215 * ppm)):
        y0 = 0.05 * ppm
        d.rounded_rectangle([cx - 30, y0, cx + 30, y0 + 120], 6, fill=(56, 56, 60), outline=(30, 30, 32), width=2)
        d.rectangle([cx - 3, y0 + 14, cx + 3, y0 + 46], fill=(6, 6, 6))           # slot
        d.ellipse([cx - 13, y0 + 62, cx + 13, y0 + 88], fill=(20, 20, 22))       # reject button seat
        # token sticker
        d.rectangle([cx - 26, y0 + 94, cx + 26, y0 + 116], fill=(232, 196, 64))
        text_c(d, (cx, y0 + 101), "1 TOKEN", font(F_BC, 10), (40, 26, 8))
        text_c(d, (cx, y0 + 111), "ONLY", font(F_BC, 9), (40, 26, 8))
    # brass token sticker in the middle: Pocket Change's own token
    cx, cy = W / 2, 0.255 * ppm
    d.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=(196, 160, 72), outline=(120, 92, 30), width=3)
    text_c(d, (cx, cy - 6), "POCKET", font(F_BC, 9), (70, 50, 14))
    text_c(d, (cx, cy + 6), "CHANGE", font(F_BC, 9), (70, 50, 14))
    text_c(d, (cx, cy + 34), "USE TOKENS ONLY", font(F_BC, 11), (20, 20, 20))
    # lock
    lx, ly = 0.24 * ppm, 0.31 * ppm
    d.ellipse([lx - 11, ly - 11, lx + 11, ly + 11], fill=(180, 176, 160), outline=(60, 60, 60), width=2)
    d.rectangle([lx - 2, ly - 7, lx + 2, ly + 7], fill=(30, 30, 30))
    # coin return cup
    rx, ry = W / 2, 0.385 * ppm
    d.rounded_rectangle([rx - 46, ry - 22, rx + 46, ry + 22], 8, fill=(40, 40, 44), outline=(20, 20, 20), width=2)
    d.rounded_rectangle([rx - 38, ry - 12, rx + 38, ry + 16], 6, fill=(6, 6, 7))
    text_c(d, (rx, ry - 30), "COIN RETURN", font(F_BC, 10), (30, 30, 30))
    im = smudges(im, 63, 50, (0, 0, W, H * 0.6), (40, 36, 30), 40, 10)
    im = scuffs(im, 64, 120, None, (200, 200, 200), 70, 20)
    save(im, "door")


def paint_ramp():
    """Ball floor (tray and ramp): black painted plywood under clear coat, balls have worn
    pale paths down the middle. 256 x 640 over 0.94 x 2.57 m (v = 0 at the back)."""
    W, H = 256, 640
    a = np.asarray(laminate(W, H, 71, (30, 30, 33), 10), np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    wear = np.zeros((H, W), np.float32)
    rnd = random.Random(72)
    for _ in range(9):
        cx = rnd.uniform(40, W - 40)
        wear += np.exp(-((xx - cx) / rnd.uniform(10, 28)) ** 2) * rnd.uniform(0.3, 0.8)
    wear *= 0.6 + 0.6 * noise(W, H, 40, 73, 2)
    a += (wear * 30)[..., None]
    im = to_img(a)
    im = scuffs(im, 74, 300, None, (110, 110, 110), 80, 30)
    im = smudges(im, 75, 60, None, (150, 140, 120), 20, 12)
    save(im, "ramp")


def paint_side():
    """Outer side panel, u along the machine (front at u=0), v from y=1.45 (top) to 0.
    1024 x 512 over 2.90 x 1.45 m (353 px/m)."""
    W, H = 1024, 512
    ppm = W / 2.90
    def U(z): return z * ppm
    def Y(y): return (1.45 - y) * ppm
    im = laminate(W, H, 81, (24, 23, 27), 8)
    d = ImageDraw.Draw(im)
    # kick and stripes (as on the reference: a red base and a white band)
    d.rectangle([0, Y(0.11), W, H], fill=(150, 18, 24))
    d.rectangle([0, Y(0.20), W, Y(0.16)], fill=(178, 22, 28))
    d.rectangle([0, Y(0.225), W, Y(0.215)], fill=(230, 228, 220))
    # side decal: orange ball and swoosh with the title, on the ramp section
    cx, cy = U(1.05), Y(0.62)
    d.line([U(0.75), cy + 30, U(2.6), cy - 40], fill=(232, 110, 26), width=10)
    d.line([U(0.78), cy + 46, U(2.5), cy - 18], fill=(250, 196, 40), width=5)
    r = 0.17 * ppm
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(232, 110, 26), outline=(16, 10, 6), width=3)
    d.line([cx - r, cy + 4, cx + r, cy - 4], fill=(16, 10, 6), width=3)
    d.line([cx + 4, cy - r, cx - 4, cy + r], fill=(16, 10, 6), width=3)
    d.arc([cx - r * 1.9, cy - r, cx - r * 0.2, cy + r], -55, 55, fill=(16, 10, 6), width=3)
    d.arc([cx + r * 0.2, cy - r, cx + r * 1.9, cy + r], 125, 235, fill=(16, 10, 6), width=3)
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).text((U(1.85), Y(0.55)), "BAYOU BUCKETS", font=font(F_BI, 62), fill=255, anchor="mm")
    im.paste((10, 8, 20), (0, 0), m.filter(ImageFilter.MaxFilter(7)))
    im.paste((250, 200, 40), (0, 0), m)
    # decal edges peeling/faded a bit, and wear: kicks at the bottom, worn front edge
    im = scuffs(im, 82, 260, (0, Y(0.25), W, H), (110, 100, 96), 90, 34)
    im = scuffs(im, 83, 120, (0, 0, W, Y(0.25)), (110, 110, 116), 50, 20)
    im = smudges(im, 84, 25, (0, Y(1.0), U(0.6), Y(0.6)), (200, 200, 210), 14, 16)
    a = np.asarray(im, np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    edge = np.clip(1 - xx / 8.0, 0, 1) * (0.5 + 0.5 * noise(W, H, 8, 85, 1))
    a += edge[..., None] * 50
    a *= (0.92 + 0.1 * noise(W, H, 120, 86, 2))[..., None]
    save(to_img(a), "side")


def paint_board():
    """Backboard face, 0.90 x 0.60 m, 512 x 342. Off-white, red border and target square,
    grey ball marks where shots hit."""
    W, H = 512, 342
    ppm = W / 0.90
    n = noise(W, H, 60, 91, 2)
    a = np.zeros((H, W, 3), np.float32)
    for i, c in enumerate((236, 234, 226)):
        a[..., i] = c * (0.93 + 0.08 * n)
    im = to_img(a)
    d = ImageDraw.Draw(im)
    d.rectangle([8, 8, W - 9, H - 9], outline=(200, 26, 30), width=12)
    # target square above the rim (rim at the bottom centre)
    tw, th = 0.30 * ppm, 0.22 * ppm
    cx = W / 2
    d.rectangle([cx - tw / 2, H - 16 - th, cx + tw / 2, H - 16], outline=(200, 26, 30), width=8)
    text_c(d, (cx, 44), "2 POINTS EVERY BASKET", font(F_BC, 22), (200, 26, 30))
    # ball marks: grey round smudges clustered round the target
    rnd = random.Random(92)
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for _ in range(140):
        x = rnd.gauss(cx, 70)
        y = rnd.gauss(H - 120, 50)
        r = rnd.uniform(14, 26)
        od.ellipse([x - r, y - r, x + r, y + r], outline=(70, 60, 50, rnd.randint(8, 30)), width=rnd.randint(2, 6))
        od.ellipse([x - r * 0.7, y - r * 0.7, x + r * 0.7, y + r * 0.7], fill=(90, 80, 70, rnd.randint(4, 14)))
    ov = ov.filter(ImageFilter.GaussianBlur(1.5))
    im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
    im = scuffs(im, 93, 80, None, (150, 140, 130), 60, 20)
    save(im, "board")


def paint_ticket():
    """Strip of orange redemption tickets, 64 x 256 = 2 tickets (29 x 51 mm each)."""
    W, H = 64, 256
    im = Image.new("RGBA", (W, H), (240, 136, 40, 255))
    d = ImageDraw.Draw(im)
    for k in range(2):
        y0 = k * 128
        d.line([0, y0, W, y0], fill=(190, 96, 24, 255), width=2)     # perforation
        for x in range(0, W, 5):
            d.point([x, y0 + 1], fill=(120, 60, 16, 255))
        d.ellipse([-4, y0 - 4, 4, y0 + 4], fill=(0, 0, 0, 0))        # side notches
        d.ellipse([W - 4, y0 - 4, W + 4, y0 + 4], fill=(0, 0, 0, 0))
        t = Image.new("RGBA", (120, 40), (0, 0, 0, 0))
        td = ImageDraw.Draw(t)
        td.text((60, 12), "TICKET", font=font(F_B, 17), fill=(120, 36, 12, 255), anchor="mm")
        td.text((60, 30), "AMUSEMENT ONLY", font=font(F_BC, 9), fill=(120, 36, 12, 255), anchor="mm")
        t = t.rotate(90, expand=True)
        im.paste(t, (12, y0 + 4), t)
    a = np.asarray(im, np.float32)
    a[..., :3] *= (0.9 + 0.12 * noise(W, H, 16, 101, 2))[..., None]
    save(to_img(a), "ticket")


def paint_plate():
    """Machine number plates 1-4: 4 cells of 64 x 64 (u = (n - 1) / 4)."""
    W, H = 256, 64
    im = Image.new("RGB", (W, H), (20, 20, 20))
    d = ImageDraw.Draw(im)
    for k in range(4):
        x0 = k * 64
        d.rounded_rectangle([x0 + 2, 2, x0 + 61, 61], 8, fill=(238, 234, 222), outline=(140, 140, 140), width=2)
        text_c(d, (x0 + 32, 33), str(k + 1), font(F_B, 44), (190, 24, 28))
        for sx, sy in ((x0 + 8, 8), (x0 + 55, 55)):
            d.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(150, 150, 150))
    im = scuffs(im, 111, 40, None, (120, 120, 120), 80, 10)
    save(im, "plate")


def paint_paint():
    """Red powder-coated steel, 256 px per metre, tileable-ish, with chips and grime."""
    S = 256
    n = noise(S, S, 32, 121, 3)
    a = np.zeros((S, S, 3), np.float32)
    for i, c in enumerate((168, 22, 28)):
        a[..., i] = c * (0.86 + 0.2 * n)
    im = to_img(a)
    rnd = random.Random(122)
    d = ImageDraw.Draw(im)
    for _ in range(14):
        x, y = rnd.uniform(0, S), rnd.uniform(0, S)
        r = rnd.uniform(0.6, 1.4)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(70, 62, 60))
    im = scuffs(im, 123, 50, None, (210, 130, 130), 70, 12)
    save(im, "paint")


def paint_lam():
    """Plain black laminate tile for inner walls and backs, 256 px per metre."""
    im = laminate(256, 256, 131, (24, 23, 27), 8)
    im = scuffs(im, 132, 40, None, (90, 90, 96), 50, 16)
    save(im, "lam")


if __name__ == "__main__":
    paint_mesh(); paint_net(); paint_ball(); paint_marquee(); paint_led(); paint_panel()
    paint_front(); paint_door(); paint_ramp(); paint_side(); paint_board(); paint_ticket()
    paint_plate(); paint_paint(); paint_lam()
    tot = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT) if f.startswith("hoops_"))
    print("total", tot)
