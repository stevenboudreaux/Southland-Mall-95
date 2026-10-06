"""Paints the textures of the Pocket Change light-ring ticket game (module `cyclone`).

The machine type is the mid-1990s round "light chase" redemption game: a square cabinet
with grey stainless sides and big die-cut side decals, yellow corner posts, a hot-pink
front door and top deck, and a clear dome over a yellow playfield with a ring of lamps
next to numbered ticket squares. The game's invented title is WHIRLWIND. No real game's
name, logo, maker's mark or artwork is used: every design here is original.

Every texture is drawn for a known physical size (see cyclone.gd for the UVs).
Run from the project folder:  python3 tools/stores/pocket_change/paint_cyclone.py
Writes tex/pc/cyclone_*.png. Seeded, so re-running reproduces the same files.
"""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(PROJ, "tex", "pc")
os.makedirs(OUT, exist_ok=True)

F_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_BC = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"
F_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_PB = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
F_PBI = "/usr/share/fonts/truetype/google-fonts/Poppins-BoldItalic.ttf"
F_PMI = "/usr/share/fonts/truetype/google-fonts/Poppins-MediumItalic.ttf"
F_LB = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

# palette (sampled from the 1995 machine in Steven's video)
YEL = (246, 214, 52)
YEL_D = (214, 170, 30)
PINK = (244, 62, 156)
PINK_L = (250, 160, 200)
NAVY = (40, 36, 120)
INK = (70, 24, 88)
TEAL = (96, 210, 200)
LILAC = (180, 156, 226)
RED = (222, 44, 58)
BLUE_L = (130, 198, 232)
WHITE = (250, 250, 246)


def font(p, s):
    return ImageFont.truetype(p, s)


SIZES = {}


def save(im, name, colors=0):
    """Saves tex/pc/cyclone_<name>.png; colors > 0 quantizes to a palette (flat art)."""
    p = os.path.join(OUT, "cyclone_%s.png" % name)
    if colors:
        if im.mode == "RGBA":
            im = im.quantize(colors=colors, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
        else:
            im = im.convert("RGB").quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(p, optimize=True)
    SIZES[name] = os.path.getsize(p)
    print("cyclone_%s.png" % name, im.size, os.path.getsize(p))


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


def to_img(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def shade(im, mult):
    """Multiplies an image's RGB by a (h, w) array."""
    a = np.asarray(im, np.float32).copy()
    a[..., :3] *= mult[..., None]
    return to_img(a)


def flat(w, h, col, seed, k=5.0, cell=40):
    """A plain painted / printed colour with a little mottling."""
    n = noise(w, h, cell, seed, 3)
    a = np.zeros((h, w, 3), np.float32)
    for i in range(3):
        a[..., i] = col[i] + (n - 0.5) * k
    return to_img(a)


def scuffs(im, seed, n, area=None, col=(150, 150, 150), alpha=60, lmax=40, width=1):
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
        d.line([x, y, x + math.cos(a) * l, y + math.sin(a) * l], fill=col + (rnd.randint(alpha // 3, alpha),), width=width)
    return Image.alpha_composite(im.convert("RGBA"), ov).convert(im.mode if im.mode != "P" else "RGB")


def smudges(im, seed, n, area=None, col=(255, 255, 255), alpha=18, rmax=14, blur=2):
    """Soft greasy fingerprints / grime patches."""
    rnd = random.Random(seed)
    w, h = im.size
    x0, y0, x1, y1 = area or (0, 0, w, h)
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        r = rnd.uniform(rmax * 0.4, rmax)
        d.ellipse([x - r, y - r * 0.8, x + r, y + r * 0.8], fill=col + (rnd.randint(alpha // 2, alpha),))
    ov = ov.filter(ImageFilter.GaussianBlur(blur))
    base = im.convert("RGBA")
    out = Image.alpha_composite(base, ov)
    return out if im.mode == "RGBA" else out.convert("RGB")


def text_c(d, xy, s, f, fill, anchor="mm", **kw):
    d.text(xy, s, font=f, fill=fill, anchor=anchor, **kw)


def outlined(d, xy, s, f, fill, outline, ow, anchor="mm"):
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=ow, stroke_fill=outline)


def rrect(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def down(im, k=2):
    return im.resize((im.size[0] // k, im.size[1] // k), Image.LANCZOS)


# ---------------------------------------------------------------- 7-segment digits
SEG = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd",
       "6": "afgedc", "7": "abc", "8": "abcdefg", "9": "abcdfg", "-": "g", " ": ""}


def seg_digit(d, x, y, w, h, ch, on, off, t=None, slant=0.10):
    """One 7-segment digit, top-left (x, y), w x h px, slanted like real LED digits."""
    t = t or max(3, int(w * 0.16))
    def P(px, py):
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


# ================================================================ PLAYFIELD
# Top view of the playfield, as the player sees it from the front: the machine's back is at
# the top of the image, the front (the BONUS slot) at the bottom. 1024 px = 1.06 m
# (local x, z within +-0.53 m of the dome centre). Must match cyclone.gd's ring radii.
FIELD_M = 1.06
R_RIM = 0.53
R_WHITE = 0.505
R_LANE0, R_LANE1 = 0.405, 0.492
R_SQ_OUT, R_SQ_IN = 0.466, 0.427
R_BULB = 0.372
R_STRIPE = 0.350
R_BAND_IN = 0.255
R_DISH = 0.250
N_BULB = 64
SQ = 0.031


def ring_values():
    """Ticket value printed beside each lamp, 0 = the BONUS slot at the front."""
    near = [10, 8, 7, 6, 5, 5, 4, 4, 3, 3, 2, 2, 2, 1, 1, 1, 1, 2, 2, 3, 3, 4, 4, 5, 4, 3, 3, 2, 2, 1, 1, 2]
    v = [0] * N_BULB
    for i in range(1, N_BULB):
        k = min(i, N_BULB - i)
        v[i] = near[k - 1]
    return v


def paint_field():
    K = 2
    S = 1024 * K
    s = S / FIELD_M
    cx = cy = S / 2.0

    def P(th, r):
        t = math.radians(th)
        return (cx - math.sin(t) * r * s, cy + math.cos(t) * r * s)

    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    rr = np.hypot(xx - cx, yy - cy) / s
    n = noise(S, S, 90, 301, 3)
    a = np.zeros((S, S, 3), np.float32)
    for i in range(3):
        a[..., i] = YEL[i] + (n - 0.5) * 10
    # inner band slightly warmer, rim slightly darker (moulded)
    rim = (rr > R_WHITE)
    a[rim] *= 0.94
    im = to_img(a)
    d = ImageDraw.Draw(im)

    def ring(r0, r1, fill):
        d.ellipse([cx - r1 * s, cy - r1 * s, cx + r1 * s, cy + r1 * s], fill=fill)
        if r0 > 0:
            pass

    # ---- the blue lane under the number squares
    def annulus(r0, r1, fill):
        m = Image.new("L", (S, S), 0)
        dm = ImageDraw.Draw(m)
        dm.ellipse([cx - r1 * s, cy - r1 * s, cx + r1 * s, cy + r1 * s], fill=255)
        dm.ellipse([cx - r0 * s, cy - r0 * s, cx + r0 * s, cy + r0 * s], fill=0)
        im.paste(Image.new("RGB", (S, S), fill), (0, 0), m)

    annulus(R_WHITE - 0.012, R_WHITE, WHITE)
    annulus(R_LANE1, R_LANE1 + 0.004, INK)
    annulus(R_LANE0, R_LANE1, BLUE_L)
    annulus(R_LANE0 - 0.004, R_LANE0, INK)
    # darker blue lane band down the middle of the lane, white dash marks
    annulus(0.440, 0.452, (86, 150, 214))
    d = ImageDraw.Draw(im)
    step = 360.0 / N_BULB
    # pink stripe and maroon line inside the lamp row
    annulus(R_STRIPE - 0.005, R_STRIPE, (236, 90, 150))
    annulus(R_STRIPE - 0.0075, R_STRIPE - 0.005, (120, 30, 60))
    # the dish edge curb
    annulus(R_BAND_IN, R_BAND_IN + 0.006, YEL_D)
    d = ImageDraw.Draw(im)

    values = ring_values()

    def rot_paste(src, xy, ang_deg):
        r = src.rotate(ang_deg, resample=Image.BICUBIC, expand=True)
        im.paste(r, (int(xy[0] - r.size[0] / 2), int(xy[1] - r.size[1] / 2)), r)

    fnum = font(F_PB, int(SQ * s * 0.78))
    sqpx = int(SQ * s)
    for i in range(N_BULB):
        th = i * step
        if i == 0:
            continue
        # white dashes between squares on the darker lane
        x0, y0 = P(th + step * 0.5, 0.437)
        x1, y1 = P(th + step * 0.5, 0.455)
        d.line([x0, y0, x1, y1], fill=(236, 244, 250), width=int(0.004 * s))
        rsq = R_SQ_OUT if i % 2 else R_SQ_IN
        # the square: navy drop shadow, ink border, pink face with a lighter centre
        tile = Image.new("RGBA", (sqpx + 16, sqpx + 16), (0, 0, 0, 0))
        dt = ImageDraw.Draw(tile)
        dt.rectangle([10, 10, sqpx + 14, sqpx + 14], fill=(40, 40, 110, 230))
        dt.rectangle([4, 4, sqpx + 8, sqpx + 8], fill=INK + (255,))
        dt.rectangle([8, 8, sqpx + 4, sqpx + 4], fill=(240, 120, 180, 255))
        dt.rectangle([14, 14, sqpx - 2, sqpx - 2], fill=(252, 196, 222, 255))
        text_c(dt, ((sqpx + 12) / 2, (sqpx + 12) / 2 + 1), str(values[i]), fnum if values[i] < 10 else font(F_PB, int(SQ * s * 0.6)), INK)
        rot_paste(tile, P(th, rsq), -th)
        # a yellow pointer under the outer squares, pointing in at the lamp
        if i % 2:
            tp = P(th, R_SQ_IN + 0.004)
            t = math.radians(th)
            inn = (math.sin(t), -math.cos(t))          # toward the centre (image)
            tan = (math.cos(t), math.sin(t))
            L = 0.016 * s
            tip = (tp[0] + inn[0] * L * 0.6, tp[1] + inn[1] * L * 0.6)
            b0 = (tp[0] - inn[0] * L * 0.5 + tan[0] * L * 0.55, tp[1] - inn[1] * L * 0.5 + tan[1] * L * 0.55)
            b1 = (tp[0] - inn[0] * L * 0.5 - tan[0] * L * 0.55, tp[1] - inn[1] * L * 0.5 - tan[1] * L * 0.55)
            d.polygon([tip, b0, b1], fill=YEL, outline=INK)
            d.line([b0, tip, b1, b0], fill=INK, width=3)

    # ---- the lamp sockets: dark wells with a bright chamfer, under the glass domes
    rb = 0.0118 * s
    for i in range(N_BULB):
        x, y = P(i * step, R_BULB)
        d.ellipse([x - rb - 5, y - rb - 5, x + rb + 5, y + rb + 5], fill=(196, 150, 30))
        d.ellipse([x - rb - 2, y - rb - 2, x + rb + 2, y + rb + 2], fill=(250, 232, 120))
        d.ellipse([x - rb, y - rb, x + rb, y + rb], fill=(60, 40, 22))
        d.ellipse([x - rb * 0.55, y - rb * 0.55, x + rb * 0.55, y + rb * 0.55], fill=(96, 70, 34))

    # ---- the BONUS slot at the front: the navy footprint under its raised housing
    # (cyclone.gd builds the housing, 0.054 x 0.07 m, centred at r = 0.435)
    bx, by = P(0, 0.435)
    w2, h2 = 0.029 * s, 0.037 * s
    rrect(d, [bx - w2 - 4, by - h2 - 4, bx + w2 + 4, by + h2 + 4], 10, fill=INK)
    rrect(d, [bx - w2, by - h2, bx + w2, by + h2], 8, fill=(52, 44, 130))
    # the bonus lamp well sits on the lamp ring (index 0)
    x, y = P(0, R_BULB)
    d.ellipse([x - rb - 6, y - rb - 6, x + rb + 6, y + rb + 6], fill=INK)
    d.ellipse([x - rb, y - rb, x + rb, y + rb], fill=(70, 20, 30))

    # ---- the inner band's banner plates, read from the centre (letters' tops point outward)
    def banner(th_c, span, text):
        r0, r1 = 0.286, 0.336
        th0, th1 = th_c - span / 2, th_c + span / 2
        pts_out = [P(th0 + (th1 - th0) * k / 40, r1) for k in range(41)]
        pts_in = [P(th1 - (th1 - th0) * k / 40, r0) for k in range(41)]
        d.polygon(pts_out + pts_in, fill=(255, 240, 130), outline=INK)
        d.line(pts_out, fill=(236, 90, 150), width=7)
        pin = [P(th0 + (th1 - th0) * k / 40, r0 + 0.004) for k in range(41)]
        d.line(pin, fill=NAVY, width=int(0.008 * s))
        # rounded end caps in navy
        for th_e in (th0, th1):
            e = P(th_e, (r0 + r1) / 2)
            d.ellipse([e[0] - 0.012 * s, e[1] - 0.012 * s, e[0] + 0.012 * s, e[1] + 0.012 * s], fill=NAVY)
        f = font(F_BC, int(0.020 * s))
        rmid = 0.314
        # lay out the characters along the arc, centred on th_c
        widths = [f.getlength(ch) / s for ch in text]
        total = sum(widths) * 1.04
        ang_total = math.degrees(total / rmid)
        a = th_c - ang_total / 2
        for ch, wch in zip(text, widths):
            am = a + math.degrees(wch * 0.52 / rmid)
            if ch != " ":
                g = Image.new("RGBA", (int(0.03 * s), int(0.03 * s)), (0, 0, 0, 0))
                dg = ImageDraw.Draw(g)
                text_c(dg, (g.size[0] / 2, g.size[1] / 2), ch, f, NAVY)
                rot_paste(g, P(am, rmid), 180 - am)
            a += math.degrees(wch * 1.04 / rmid)

    banner(160, 40, "BONUS INCREASES")
    banner(-160, 30, "EVERY GAME")
    banner(-62, 40, "BONUS INCREASES")
    banner(62, 30, "EVERY GAME")

    # ---- the dish: a spun-chrome bowl, mirroring the dome and the room in soft streaks
    dm = Image.new("L", (S, S), 0)
    ImageDraw.Draw(dm).ellipse([cx - R_DISH * s, cy - R_DISH * s, cx + R_DISH * s, cy + R_DISH * s], fill=255)
    q = np.clip(rr / R_DISH, 0, 1)
    spun = np.sin(rr * s * 0.9) * 3.0 + np.sin(rr * s * 0.23) * 4.0
    base = 120 + 70 * (1 - q) ** 1.5 + spun
    # broad blurred reflections: the dome's bright rim far side, dark room near side
    refl = Image.new("L", (S, S), 128)
    dr = ImageDraw.Draw(refl)
    dr.ellipse([cx - 0.22 * s, cy - 0.24 * s, cx + 0.22 * s, cy - 0.10 * s], fill=215)
    dr.ellipse([cx - 0.20 * s, cy + 0.10 * s, cx + 0.20 * s, cy + 0.26 * s], fill=70)
    dr.ellipse([cx - 0.08 * s, cy - 0.15 * s, cx + 0.06 * s, cy - 0.04 * s], fill=60)
    dr.ellipse([cx + 0.10 * s, cy - 0.02 * s, cx + 0.20 * s, cy + 0.05 * s], fill=235)
    refl = np.asarray(refl.filter(ImageFilter.GaussianBlur(28)), np.float32) - 128
    base = base + refl * 0.8
    da = np.stack([base * 0.95, base * 0.98, base * 1.04], -1)
    dish = to_img(da)
    im.paste(dish, (0, 0), dm)
    d = ImageDraw.Draw(im)
    d.ellipse([cx - R_DISH * s, cy - R_DISH * s, cx + R_DISH * s, cy + R_DISH * s], outline=(96, 96, 104), width=8)
    # the pink post's foot
    pf = (cx, cy + 0.08 * s)
    d.rectangle([pf[0] - 0.02 * s, pf[1] - 0.02 * s, pf[0] + 0.02 * s, pf[1] + 0.02 * s], fill=(200, 60, 120))

    # ---- arch / post sockets are drawn by the lights (collars); paint their screw holes
    for th in (92, -92, 140, -140, 180):
        for r in (0.33, 0.47):
            x, y = P(th, r)
            d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=(150, 120, 40))

    # ---- wear: dust in the corners of the lane, scratches from the cleaning cloth
    im = scuffs(im, 311, 260, (cx - 0.5 * s, cy - 0.5 * s, cx + 0.5 * s, cy + 0.5 * s), col=(255, 255, 230), alpha=50, lmax=60)
    im = smudges(im, 312, 70, (cx - 0.5 * s, cy - 0.5 * s, cx + 0.5 * s, cy + 0.5 * s), col=(90, 80, 60), alpha=16, rmax=40, blur=8)
    im = down(im, K)
    save(im, "field", 192)


# ================================================================ SIDE PANELS
def paint_side():
    """Brushed stainless side panel, 1.10 m along the side x 0.90 m tall: 512 x 420.
    Horizontal brushing, grime toward the floor, a speaker grille near the top."""
    W, H = 512, 420
    rs = np.random.RandomState(51)
    row = rs.rand(H).astype(np.float32)
    row = np.convolve(row, np.ones(3) / 3, mode="same")
    a = np.zeros((H, W), np.float32) + 168
    a += (row[:, None] - 0.5) * 14
    # long smooth brush streaks: noise stretched along x
    st = np.asarray(Image.fromarray((rs.rand(H // 2, 8) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
    a += (st - 0.5) * 10
    big = noise(W, H, 160, 52, 2)
    a += (big - 0.5) * 14
    yy = np.mgrid[0:H, 0:W][0].astype(np.float32) / H
    a -= np.clip((yy - 0.75) / 0.25, 0, 1) * 22          # grime toward the floor
    a -= np.clip((0.03 - yy) / 0.03, 0, 1) * 30          # shadow under the deck lip
    rgb = np.stack([a * 0.985, a * 0.995, a * 1.02], -1)
    im = to_img(rgb)
    d = ImageDraw.Draw(im)
    # speaker grille: a rounded field of punched holes, top centre
    gx, gy = W * 0.5, H * 0.13
    for j in range(-5, 6):
        for i in range(-11, 12):
            x = gx + i * 6.2 + (3.1 if j % 2 else 0)
            y = gy + j * 5.4
            if ((x - gx) / 74) ** 2 + ((y - gy) / 30) ** 2 < 1:
                d.ellipse([x - 1.6, y - 1.6, x + 1.6, y + 1.6], fill=(40, 40, 44))
    # kick scuffs along the bottom, fingerprints at hand height near the front edge
    im = scuffs(im, 53, 140, (0, H * 0.78, W, H), col=(80, 76, 72), alpha=90, lmax=26, width=2)
    im = scuffs(im, 54, 120, (0, 0, W, H), col=(225, 228, 232), alpha=60, lmax=40)
    im = smudges(im, 55, 30, (0, H * 0.1, W, H * 0.6), col=(120, 110, 100), alpha=14, rmax=14)
    save(im, "side")


# ================================================================ SIDE DECAL
def paint_decal(words=True):
    """The die-cut side decal, 0.86 x 0.54 m: 1024 x 640 RGBA, white cut border.
    Original 90s swoosh design: a teal lightning band, navy/lilac/pink swirl rings, a red
    speed-arc, a yellow crescent, and the title WHIRLWIND in bouncing yellow letters.
    The middle band (u 0.05-0.95, v 0.28-0.74) is always opaque: it is the owner-editable
    sign face (cyclone.gd), so the word-free copy must cover it."""
    K = 2
    W, H = 1024 * K, 640 * K
    shapes = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(shapes)

    def S(*p):
        return [(x * K, y * K) for x, y in p]

    cx, cy = 400, 330
    # swirl rings (concentric arcs) behind the left-centre
    for r, col, w, a0, a1 in [(250, LILAC, 34, 150, 420), (205, PINK, 26, 200, 470), (165, NAVY, 40, 100, 330),
                              (120, (110, 200, 240), 30, 230, 520), (80, NAVY, 28, 40, 300)]:
        d.arc([(cx - r) * K, (cy - r) * K, (cx + r) * K, (cy + r) * K], a0, a1, fill=col + (255,), width=w * K)
    # the teal lightning band: covers the sign band completely
    d.polygon(S((28, 190), (700, 150), (690, 122), (990, 172), (972, 462), (420, 500), (430, 528), (30, 474)), fill=TEAL + (255,))
    d.polygon(S((60, 210), (640, 178), (632, 200), (60, 236)), fill=(170, 240, 232, 255))
    # red speed-arc with white ticks, top left
    d.arc([180 * K, 40 * K, 760 * K, 620 * K], 200, 285, fill=RED + (255,), width=36 * K)
    for k in range(9):
        t = math.radians(206 + k * 7)
        r0, r1 = 254, 290
        d.line([((470 + math.cos(t) * r0) * K, (330 + math.sin(t) * r0) * K), ((470 + math.cos(t) * r1) * K, (330 + math.sin(t) * r1) * K)], fill=WHITE + (255,), width=5 * K)
    # yellow crescent swoosh at the left
    cm = Image.new("L", (W, H), 0)
    dc = ImageDraw.Draw(cm)
    dc.ellipse([30 * K, 70 * K, 380 * K, 570 * K], fill=255)
    dc.ellipse([95 * K, 110 * K, 430 * K, 540 * K], fill=0)
    shapes.paste(Image.new("RGBA", (W, H), YEL + (255,)), (0, 0), cm)
    # lilac and navy tails, bottom right
    d.arc([520 * K, 250 * K, 980 * K, 610 * K], 330, 470, fill=LILAC + (255,), width=30 * K)
    d.arc([560 * K, 290 * K, 940 * K, 580 * K], 340, 460, fill=NAVY + (255,), width=22 * K)
    d.arc([600 * K, 30 * K, 970 * K, 340 * K], 200, 330, fill=PINK + (255,), width=22 * K)
    d.arc([650 * K, 60 * K, 960 * K, 300 * K], 210, 320, fill=(110, 200, 240, 255), width=14 * K)
    # navy diagonal shards
    d.polygon(S((820, 470), (930, 440), (880, 560)), fill=NAVY + (255,))
    d.polygon(S((120, 110), (210, 140), (150, 175)), fill=LILAC + (255,))

    # die-cut white border: dilate the alpha
    al = shapes.split()[3]
    border = al.filter(ImageFilter.MaxFilter(17)).filter(ImageFilter.MaxFilter(17))
    border = border.point(lambda v: 255 if v > 30 else 0)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.paste(Image.new("RGBA", (W, H), (248, 248, 246, 255)), (0, 0), border)
    out = Image.alpha_composite(out, shapes)

    if words:
        f = font(F_PBI, 172 * K)
        word = "WHIRLWIND"
        bounce = [18, -14, 8, -16, 12, -10, 16, -12, 6]
        tilt = [-6, 5, -3, 6, -5, 4, -6, 5, -3]
        scale = [1.10, 0.96, 1.0, 0.96, 1.0, 0.96, 1.0, 0.96, 1.0]
        ws = [f.getlength(ch) * sc * 0.86 for ch, sc in zip(word, scale)]
        x = (W - sum(ws)) / 2
        for ch, wch, b, t, sc in zip(word, ws, bounce, tilt, scale):
            fs = font(F_PBI, int(172 * K * sc))
            g = Image.new("RGBA", (int(260 * K), int(300 * K)), (0, 0, 0, 0))
            dg = ImageDraw.Draw(g)
            gc = (g.size[0] / 2, g.size[1] / 2)
            # navy drop shadow, purple outline, yellow face with a white glint
            dg.text((gc[0] + 10 * K, gc[1] + 12 * K), ch, font=fs, fill=NAVY + (255,), anchor="mm", stroke_width=12 * K, stroke_fill=NAVY + (255,))
            dg.text(gc, ch, font=fs, fill=(255, 226, 60, 255), anchor="mm", stroke_width=10 * K, stroke_fill=(58, 42, 144, 255))
            g = g.rotate(t, resample=Image.BICUBIC)
            out.alpha_composite(g, (int(x + wch / 2 - g.size[0] / 2), int(H * 0.50 + b * K - g.size[1] / 2)))
            x += wch
        # small swirl ticks above the W, like an underline of speed
        dd = ImageDraw.Draw(out)
        for k in range(5):
            dd.line([(120 + k * 22) * K, 236 * K, (132 + k * 22) * K, 222 * K], fill=(58, 42, 144, 255), width=6 * K)
    im = down(out, K)
    # weathering: faint scratches and a lifted, greyed corner
    im = scuffs(im, 71, 90, None, col=(255, 255, 255), alpha=40, lmax=30)
    a = np.asarray(im).copy()
    a[..., 3] = np.where(a[..., 3] > 127, 255, 0)
    im = Image.fromarray(a)
    save(im, "decal" if words else "decal_blank", 96)


# ================================================================ FRONT (door)
def paint_front():
    """The pink front below the console: 1.06 m x 0.665 m (y 0.035-0.70), 768 x 482.
    Door outline with hinge, 25c sticker, 'A Winner Every Game' sticker, screws, lock
    and coin-mech / ticket-slot shadows (their bezels are geometry), kick scuffs."""
    K = 2
    W, H = 768 * K, 482 * K
    s = W / 1.06
    def X(x):   # local x (m) -> px
        return (x + 0.53) * s
    def Y(y):   # local y (m) -> px
        return (0.70 - y) * s
    im = flat(W, H, PINK, 81, k=7, cell=90)
    d = ImageDraw.Draw(im)
    # door seam and hinge
    dx0, dx1, dy0, dy1 = -0.40, 0.44, 0.105, 0.665
    d.rectangle([X(dx0), Y(dy1), X(dx1), Y(dy0)], outline=(150, 20, 80), width=5 * K)
    d.line([X(dx0) + 6 * K, Y(dy1), X(dx0) + 6 * K, Y(dy0)], fill=(255, 140, 196), width=2 * K)
    for k in range(26):
        y = Y(dy1) + k * (Y(dy0) - Y(dy1)) / 26
        d.line([X(dx0 + 0.014), y + 3 * K, X(dx0 + 0.014), y + 9 * K], fill=(160, 30, 90), width=3 * K)
    # cash box door below
    d.rectangle([X(-0.25), Y(0.095), X(0.25), Y(0.045)], outline=(150, 20, 80), width=4 * K)
    d.ellipse([X(0.20) - 7 * K, Y(0.07) - 7 * K, X(0.20) + 7 * K, Y(0.07) + 7 * K], fill=(190, 190, 196), outline=(60, 60, 60), width=2 * K)
    # screws / punched holes on the door
    for (x, y) in [(-0.28, 0.62), (-0.04, 0.60), (-0.28, 0.40), (-0.06, 0.46), (0.36, 0.62), (0.30, 0.15), (-0.30, 0.15)]:
        d.ellipse([X(x) - 7 * K, Y(y) - 7 * K, X(x) + 7 * K, Y(y) + 7 * K], fill=(30, 18, 26))
        d.ellipse([X(x) - 3 * K, Y(y) - 5 * K, X(x) + 1 * K, Y(y) - 2 * K], fill=(110, 80, 96))
    # finger pull indent, scuffed
    d.ellipse([X(-0.21), Y(0.56), X(-0.11), Y(0.535)], fill=(250, 120, 186), outline=(196, 40, 110), width=3 * K)
    # 25c sticker
    d.rectangle([X(-0.02), Y(0.505), X(0.125), Y(0.44)], fill=(250, 250, 248))
    text_c(d, (X(0.052), Y(0.472)), "25¢", font(F_LB, 46 * K), (14, 14, 14))
    # coin mech and ticket slot: dark recess shadows (bezels are geometry)
    d.rectangle([X(0.1575) - 4 * K, Y(0.5025) - 4 * K, X(0.2325) + 8 * K, Y(0.4075) + 8 * K], fill=(150, 30, 90))
    d.rectangle([X(0.135) - 4 * K, Y(0.30) - 4 * K, X(0.215) + 6 * K, Y(0.25) + 6 * K], fill=(150, 30, 90))
    # lock
    d.ellipse([X(0.355) - 13 * K, Y(0.43) - 13 * K, X(0.355) + 13 * K, Y(0.43) + 13 * K], fill=(120, 30, 70))
    # the "A Winner Every Game / One Hit Per Credit" sticker (original drawing)
    st = Image.new("RGBA", (int(0.25 * s), int(0.16 * s)), (0, 0, 0, 0))
    ds = ImageDraw.Draw(st)
    sw, sh = st.size
    shp = Image.new("RGBA", st.size, (0, 0, 0, 0))
    dsh = ImageDraw.Draw(shp)
    dsh.polygon([(sw * 0.05, sh * 0.12), (sw * 0.80, sh * 0.02), (sw * 0.90, sh * 0.55), (sw * 0.12, sh * 0.62)], fill=(250, 128, 140, 255))
    dsh.arc([sw * 0.55, sh * 0.0, sw * 1.05, sh * 1.25], 190, 300, fill=NAVY + (255,), width=int(sw * 0.07))
    dsh.arc([sw * 0.45, sh * 0.3, sw * 0.95, sh * 1.2], 160, 260, fill=TEAL + (255,), width=int(sw * 0.06))
    dsh.polygon([(sw * 0.30, sh * 0.55), (sw * 0.92, sh * 0.45), (sw * 0.88, sh * 0.80), (sw * 0.34, sh * 0.88)], fill=(255, 226, 40, 255))
    al = shp.split()[3].filter(ImageFilter.MaxFilter(11))
    st.paste(Image.new("RGBA", st.size, (255, 255, 255, 255)), (0, 0), al)
    st = Image.alpha_composite(st, shp)
    ds = ImageDraw.Draw(st)
    fa = font(F_PB, int(0.022 * s))
    ds.text((sw * 0.44, sh * 0.20), "A Winner", font=fa, fill=NAVY, anchor="mm")
    ds.text((sw * 0.46, sh * 0.40), "Every Game", font=fa, fill=NAVY, anchor="mm")
    fb = font(F_PBI, int(0.017 * s))
    ds.text((sw * 0.62, sh * 0.60), "One Hit", font=fb, fill=NAVY, anchor="mm")
    ds.text((sw * 0.62, sh * 0.76), "Per Credit", font=fb, fill=NAVY, anchor="mm")
    st = st.rotate(8, resample=Image.BICUBIC, expand=True)
    im.paste(st, (int(X(0.19)), int(Y(0.672))), st)
    # serial plate, bottom left
    d = ImageDraw.Draw(im)
    d.rectangle([X(-0.50), Y(0.10), X(-0.42), Y(0.065)], fill=(196, 196, 190), outline=(110, 110, 110), width=2 * K)
    fs = font(F_B, 7 * K)
    text_c(d, (X(-0.46), Y(0.090)), "MODEL WW-1", fs, (40, 40, 40))
    text_c(d, (X(-0.46), Y(0.076)), "SER 0417", fs, (40, 40, 40))
    im = down(im, K)
    # wear: kick marks along the bottom, fingerprints round the coin mech, sun-faded top
    im = scuffs(im, 82, 220, (0, 482 * 0.80, 768, 482), col=(70, 50, 60), alpha=120, lmax=22, width=2)
    im = scuffs(im, 83, 120, None, col=(255, 210, 230), alpha=70, lmax=30)
    im = smudges(im, 84, 40, (420, 120, 640, 330), col=(120, 40, 80), alpha=22, rmax=16)
    im = smudges(im, 85, 16, (0, 0, 768, 482), col=(255, 255, 255), alpha=12, rmax=40, blur=10)
    save(im, "front", 160)


# ================================================================ CONSOLE (slanted panel)
def paint_console():
    """The slanted control panel across the front top: 1.06 m x 0.30 m, 1024 x 288.
    Top of the image = top (back) edge. INSTRUCTIONS card left, the STOP! button (its cap
    is geometry) in the middle with teal/pink/red swooshes, TICKETS OWED window right
    (its LED quad is geometry), navy band with stripes along the bottom."""
    K = 2
    W, H = 1024 * K, 288 * K
    s = W / 1.06
    im = flat(W, H, (248, 218, 44), 91, k=8, cell=80)
    d = ImageDraw.Draw(im)
    # pink/red rule along the top edge, yellow rolled edge above it
    d.rectangle([0, 0, W, 10 * K], fill=YEL_D)
    d.rectangle([0, 10 * K, W, 18 * K], fill=(232, 40, 80))
    # navy lower band with a pink swoosh and a teal block stripe at the bottom edge
    d.polygon([(0, 200 * K), (W, 186 * K), (W, H), (0, H)], fill=(52, 44, 168))
    d.rectangle([0, 262 * K, W, H], fill=(70, 150, 190))
    for k in range(40):
        x = k * 27 * K
        d.polygon([(x, 266 * K), (x + 18 * K, 266 * K), (x + 14 * K, H - 4 * K), (x - 4 * K, H - 4 * K)], fill=(150, 220, 220))
    d.arc([-80 * K, 210 * K, 420 * K, 420 * K], 200, 300, fill=PINK, width=16 * K)
    d.line([(30 * K, 232 * K), (180 * K, 228 * K)], fill=WHITE, width=4 * K)
    d.line([(36 * K, 242 * K), (160 * K, 239 * K)], fill=WHITE, width=3 * K)
    # right section: lilac panel
    d.polygon([(760 * K, 22 * K), (W, 22 * K), (W, 262 * K), (740 * K, 262 * K)], fill=LILAC)
    d.line([(780 * K, 230 * K), (W, 226 * K)], fill=(140, 110, 200), width=6 * K)
    # swooshes round the button
    bx, by = 548 * K, 112 * K
    d.arc([bx - 150 * K, by - 120 * K, bx + 150 * K, by + 140 * K], 340, 120, fill=TEAL, width=26 * K)
    d.arc([bx - 180 * K, by - 150 * K, bx + 170 * K, by + 160 * K], 310, 80, fill=PINK, width=14 * K)
    d.arc([bx - 110 * K, by - 70 * K, bx + 200 * K, by + 150 * K], 20, 120, fill=RED, width=16 * K)
    d.polygon([(bx - 150 * K, by + 80 * K), (bx - 60 * K, by + 108 * K), (bx - 70 * K, by + 124 * K), (bx - 160 * K, by + 96 * K)], fill=PINK)
    for k in range(4):
        d.line([(bx - 30 * K + k * 20 * K, by + 132 * K), (bx - 26 * K + k * 20 * K, by + 150 * K)], fill=RED, width=6 * K)
    # the button's dark well and chrome-ring shadow
    d.ellipse([bx - 52 * K, by - 52 * K, bx + 52 * K, by + 52 * K], fill=(30, 26, 40))
    # INSTRUCTIONS card
    x0, y0, x1, y1 = 70 * K, 40 * K, 410 * K, 182 * K
    d.rectangle([x0 + 12 * K, y0 + 12 * K, x1 + 12 * K, y1 + 12 * K], fill=NAVY)
    d.rectangle([x0, y0, x1, y1], fill=PINK)
    d.rectangle([x0 + 8 * K, y0 + 26 * K, x1 - 8 * K, y1 - 8 * K], fill=(255, 252, 240))
    rrect(d, [x0 + 70 * K, y0 - 14 * K, x1 - 70 * K, y0 + 22 * K], 16 * K, fill=(255, 230, 60), outline=NAVY, width=3 * K)
    text_c(d, ((x0 + x1) / 2, y0 + 4 * K), "INSTRUCTIONS", font(F_BC, 24 * K), NAVY)
    fi = font(F_BC, 15 * K)
    lines = [("INSERT TOKEN(S)", None), ('HIT THE "STOP!" BUTTON', "TO STOP THE LIGHT"), ("STOP THE LIGHT IN THE", "BONUS SLOT TO WIN BONUS")]
    yy = y0 + 42 * K
    for a, b in lines:
        d.polygon([(x0 + 22 * K, yy - 7 * K), (x0 + 36 * K, yy), (x0 + 22 * K, yy + 7 * K)], fill=(240, 180, 20), outline=NAVY)
        d.text((x0 + 44 * K, yy), a, font=fi, fill=(20, 20, 40), anchor="lm")
        if b:
            yy += 16 * K
            d.text((x0 + 60 * K, yy), b, font=fi, fill=(20, 20, 40), anchor="lm")
        yy += 23 * K
    # TICKETS OWED plate: yellow frame, pink arrow, the LED window (dark), CREDITS
    tx0, ty0, tx1, ty1 = 800 * K, 46 * K, 1000 * K, 176 * K
    d.rectangle([tx0 + 8 * K, ty0 + 8 * K, tx1 + 8 * K, ty1 + 8 * K], fill=NAVY)
    d.rectangle([tx0, ty0, tx1, ty1], fill=(255, 230, 60), outline=NAVY, width=3 * K)
    text_c(d, ((tx0 + tx1) / 2, ty0 + 18 * K), "TICKETS OWED", font(F_BC, 20 * K), NAVY)
    d.rectangle([tx0 + 22 * K, ty0 + 36 * K, tx1 - 22 * K, ty1 - 30 * K], fill=(26, 6, 8))
    text_c(d, ((tx0 + tx1) / 2, ty1 - 14 * K), "CREDITS", font(F_BC, 13 * K), NAVY)
    d.polygon([(tx0 - 50 * K, ty0 + 50 * K), (tx0 - 10 * K, ty0 + 70 * K), (tx0 - 50 * K, ty0 + 90 * K)], fill=PINK, outline=NAVY)
    im = down(im, K)
    im = scuffs(im, 92, 160, None, col=(255, 255, 255), alpha=70, lmax=24)
    im = smudges(im, 93, 50, (380, 40, 720, 220), col=(80, 60, 40), alpha=18, rmax=18)
    # palm-worn front edge
    a = np.asarray(im, np.float32).copy()
    yy = np.mgrid[0:288, 0:1024][0].astype(np.float32)
    a[..., :3] *= (1.0 - np.clip((yy - 270) / 18, 0, 1) * 0.25)[..., None]
    save(to_img(a), "console", 160)


# ================================================================ SMALL PARTS
def paint_bonus():
    """The BONUS display's face, 0.24 x 0.165 m: 256 x 176. The LED window (px 24-232,
    60-136) is covered by an emissive LED quad (cyclone.gd)."""
    K = 2
    W, H = 256 * K, 176 * K
    im = Image.new("RGB", (W, H), (150, 20, 44))
    d = ImageDraw.Draw(im)
    d.rectangle([8 * K, 8 * K, W - 8 * K, H - 8 * K], fill=(246, 222, 70))
    rrect(d, [40 * K, 14 * K, 216 * K, 54 * K], 16 * K, fill=(110, 200, 240), outline=NAVY, width=2 * K)
    d.line([(46 * K, 50 * K), (90 * K, 20 * K)], fill=PINK, width=8 * K)
    outlined(d, (W / 2, 34 * K), "BONUS", font(F_PB, 34 * K), (250, 150, 196), (150, 20, 44), 3 * K)
    d.rectangle([20 * K, 56 * K, 236 * K, 140 * K], fill=(150, 20, 44))
    d.rectangle([24 * K, 60 * K, 232 * K, 136 * K], fill=(30, 4, 6))
    rrect(d, [20 * K, 146 * K, 236 * K, 166 * K], 10 * K, fill=NAVY)
    for k in range(5):
        d.rectangle([(70 + k * 9) * K, 149 * K, (75 + k * 9) * K, 163 * K], fill=(240, 120, 170))
    for k in range(5):
        d.rectangle([(150 + k * 9) * K, 149 * K, (155 + k * 9) * K, 163 * K], fill=(240, 120, 170))
    d.ellipse([118 * K, 147 * K, 138 * K, 165 * K], fill=WHITE)
    im = down(im, K)
    save(im, "bonus", 64)


def paint_led():
    """LED atlas, 256 x 128: top half the BONUS readout '108', bottom half TICKETS OWED '0'."""
    K = 2
    W, H = 256 * K, 128 * K
    im = Image.new("RGB", (W, H), (16, 2, 3))
    d = ImageDraw.Draw(im)
    on = (255, 46, 30)
    off = (28, 5, 5)
    for k, ch in enumerate("108"):
        seg_digit(d, (38 + k * 66) * K, 9 * K, 44 * K, 46 * K, ch, on, off, t=7 * K)
    for k, ch in enumerate("  0"):
        seg_digit(d, (40 + k * 64) * K, 73 * K, 40 * K, 46 * K, ch, on, off, t=7 * K)
    im = im.filter(ImageFilter.GaussianBlur(1.2 * K))
    im = down(im, K)
    save(im, "led", 64)


def paint_button():
    """The big STOP! button's cap, 128 x 128 (disc fills the square)."""
    K = 4
    S = 128 * K
    im = Image.new("RGB", (S, S), (210, 228, 50))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, S, S], fill=(170, 190, 30))
    d.ellipse([6 * K, 6 * K, S - 6 * K, S - 6 * K], fill=(222, 236, 66))
    d.ellipse([18 * K, 14 * K, S - 26 * K, 50 * K], fill=(240, 250, 150))
    outlined(d, (S / 2, S * 0.53), "STOP!", font(F_PBI, 34 * K), (30, 150, 50), (10, 40, 10), 3 * K)
    im = down(im, K)
    save(im, "button", 48)


def paint_coin():
    """Coin mech face, 0.075 x 0.095 m: 128 x 160. Black textured plastic, brass entry
    plate with '25c', token slot, coin-return push."""
    K = 2
    W, H = 128 * K, 160 * K
    im = flat(W, H, (26, 26, 28), 101, k=8, cell=10)
    d = ImageDraw.Draw(im)
    rrect(d, [4 * K, 4 * K, W - 4 * K, H - 4 * K], 10 * K, outline=(60, 60, 64), width=3 * K)
    d.rectangle([34 * K, 34 * K, 94 * K, 110 * K], fill=(150, 120, 30))
    d.rectangle([38 * K, 38 * K, 90 * K, 106 * K], fill=(214, 182, 60))
    text_c(d, (64 * K, 54 * K), "25¢", font(F_B, 18 * K), (60, 40, 10))
    text_c(d, (64 * K, 74 * K), "TOKEN", font(F_BC, 9 * K), (60, 40, 10))
    text_c(d, (64 * K, 86 * K), "ONLY", font(F_BC, 9 * K), (60, 40, 10))
    d.rectangle([60 * K, 92 * K, 68 * K, 104 * K], fill=(20, 16, 10))
    d.rectangle([22 * K, 6 * K, 106 * K, 18 * K], fill=(44, 44, 48))
    d.ellipse([52 * K, 122 * K, 76 * K, 146 * K], fill=(60, 60, 64), outline=(90, 90, 96), width=2 * K)
    im = down(im, K)
    im = scuffs(im, 102, 30, None, col=(140, 140, 140), alpha=60, lmax=14)
    save(im, "coin", 64)


def paint_tower():
    """Lamp tower boxes, 256 x 128: left half the teal-green one, right half the blue one.
    Each half is one face, 0.10 m square: moulded plastic with darker edges."""
    W, H = 256, 128
    im = Image.new("RGB", (W, H))
    for k, col in enumerate([(26, 128, 104), (40, 90, 196)]):
        f = flat(128, 128, col, 111 + k, k=10, cell=30)
        a = np.asarray(f, np.float32).copy()
        yy, xx = np.mgrid[0:128, 0:128].astype(np.float32)
        e = np.minimum(np.minimum(xx, 127 - xx), np.minimum(yy, 127 - yy))
        a *= (0.72 + 0.28 * np.clip(e / 10, 0, 1))[..., None]
        f = scuffs(to_img(a), 113 + k, 30, None, col=(200, 230, 220), alpha=50, lmax=18)
        im.paste(f, (k * 128, 0))
    save(im, "tower", 96)


def paint_slot():
    """The BONUS slot housing's face, 128 x 64."""
    K = 2
    W, H = 128 * K, 64 * K
    im = Image.new("RGB", (W, H), (52, 44, 130))
    d = ImageDraw.Draw(im)
    rrect(d, [3 * K, 3 * K, W - 3 * K, H - 3 * K], 10 * K, outline=INK, width=3 * K)
    d.pieslice([34 * K, -16 * K, 94 * K, 40 * K], 0, 180, fill=(240, 110, 170))
    text_c(d, (W / 2, 46 * K), "BONUS", font(F_BC, 20 * K), WHITE)
    im = down(im, K)
    save(im, "slot", 32)


def paint_ticket():
    """Orange redemption ticket strip, one ticket per tile: 64 x 128 RGBA, notched sides."""
    W, H = 64, 128
    im = Image.new("RGBA", (W, H), (244, 140, 40, 255))
    d = ImageDraw.Draw(im)
    d.line([0, 0, W, 0], fill=(190, 90, 20, 255), width=2)
    for k in range(0, W, 6):
        d.point((k + 2, 1), fill=(120, 50, 10, 255))
    d.ellipse([-5, -5, 5, 5], fill=(0, 0, 0, 0))
    d.ellipse([W - 5, -5, W + 5, 5], fill=(0, 0, 0, 0))
    d.ellipse([-5, H - 5, 5, H + 5], fill=(0, 0, 0, 0))
    d.ellipse([W - 5, H - 5, W + 5, H + 5], fill=(0, 0, 0, 0))
    f = font(F_BC, 13)
    g = Image.new("RGBA", (H, W), (0, 0, 0, 0))
    dg = ImageDraw.Draw(g)
    text_c(dg, (H / 2, W / 2 - 8), "ADMIT ONE", f, (120, 40, 10, 255))
    text_c(dg, (H / 2, W / 2 + 10), "TICKET", font(F_BC, 11), (120, 40, 10, 255))
    g = g.rotate(90, expand=True)
    im.alpha_composite(g)
    save(im, "ticket")


def paint_dome():
    """Dome acrylic: alpha-only smudges and fine scratches, 256 x 256 (u = round, v = up)."""
    S = 256
    im = Image.new("RGBA", (S, S), (235, 242, 255, 26))
    im = smudges(im, 121, 30, (0, S * 0.55, S, S), col=(255, 255, 255), alpha=30, rmax=10, blur=2)
    im = scuffs(im, 122, 70, None, col=(255, 255, 255), alpha=34, lmax=16)
    save(im, "dome")


def paint_deck():
    """Pink top deck, top view, 1.32 x 1.36 m: 512 x 528 (back of the machine at the top).
    Worn pale where hands rest at the front corners, grime ring by the dome flange."""
    W, H = 512, 528
    im = flat(W, H, (238, 64, 154), 131, k=8, cell=60)
    s = W / 1.32
    a = np.asarray(im, np.float32).copy()
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # local (x, z) of each pixel: x = px / s - 0.66, z = 1.32 - py / s   (dome centre z 0.70)
    lx = xx / s - 0.66
    lz = (H - yy) / s - 0.02
    rr = np.hypot(lx, lz - 0.70)
    a *= (1.0 - np.clip((0.63 - rr) / 0.07, 0, 1) * 0.22)[..., None]
    wear = noise(W, H, 30, 132, 3)
    for cxx in (-0.55, 0.55):
        m = np.clip(1.0 - np.hypot(lx - cxx, lz - 0.05) / 0.22, 0, 1) * (wear > 0.52)
        a = a * (1 - m[..., None] * 0.16) + m[..., None] * np.array([250, 170, 210]) * 0.16
    im = scuffs(to_img(a), 133, 160, None, col=(255, 210, 230), alpha=80, lmax=24)
    im = smudges(im, 134, 20, None, col=(60, 30, 40), alpha=16, rmax=20, blur=6)
    save(im, "deck", 128)


def paint_yellow():
    """Yellow painted corner posts and trims: 256 x 256, tiles; chips show grey metal."""
    S = 256
    im = flat(S, S, (246, 206, 30), 141, k=10, cell=40)
    rnd = random.Random(142)
    d = ImageDraw.Draw(im)
    for _ in range(26):
        x, y = rnd.uniform(0, S), rnd.uniform(0, S)
        r = rnd.uniform(1, 4)
        d.ellipse([x - r, y - r * 0.7, x + r, y + r * 0.7], fill=(150, 150, 146))
    im = scuffs(im, 143, 120, None, col=(120, 100, 40), alpha=60, lmax=20)
    save(im, "yellow", 96)


if __name__ == "__main__":
    paint_field()
    paint_side()
    paint_decal(True)
    paint_decal(False)
    paint_front()
    paint_console()
    paint_bonus()
    paint_led()
    paint_button()
    paint_coin()
    paint_tower()
    paint_slot()
    paint_ticket()
    paint_dome()
    paint_deck()
    paint_yellow()
    print("total", sum(SIZES.values()), "bytes")
