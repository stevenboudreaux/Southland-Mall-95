"""Paints the textures of the Pocket Change air hockey table (module `airhockey`).

An 8 ft commercial coin-op air hockey table of the 1990s, from Steven's reference photo:
white/silver-grey laminate cabinet with a royal-blue band, grey corner legs, a medium-blue
perforated playfield, aluminium rails with black rubber bumpers, clear acrylic side guards,
a chrome double-tube arch carrying a silver lamp/score unit with red 7-segment scores.
The only words are generic ("AIR HOCKEY", "TOKENS ONLY", ...). No brand, no logo.

Every texture is drawn for a known physical size (see airhockey.gd for the UVs).
Run from the project folder:  python3 tools/stores/pocket_change/paint_airhockey.py
Writes tex/pc/airhockey_*.png. Seeded, so re-running reproduces the same files.
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
F_BO = "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf"

# physical sizes, metres (keep in step with airhockey.gd)
L = 2.45          # cabinet length
WID = 1.35        # cabinet width
PF_L, PF_W = 2.25, 1.20   # playfield inside the rails
SK_H = 0.48       # skirt: y 0.30 .. 0.78


def font(p, s):
    return ImageFont.truetype(p, s)


def save(im, name):
    p = os.path.join(OUT, "airhockey_%s.png" % name)
    im.save(p, optimize=True)
    print("airhockey_%s.png" % name, im.size, os.path.getsize(p))


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


def text_c(d, xy, s, f, fill, anchor="mm", **kw):
    d.text(xy, s, font=f, fill=fill, anchor=anchor, **kw)


def scuffs(im, seed, n, area=None, col=(150, 150, 150), alpha=60, lmax=40, width=1):
    """Thin scratches."""
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
    return Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")


def smudges(im, seed, n, area=None, col=(255, 255, 255), alpha=18, rmax=14, blur=2):
    """Soft greasy marks."""
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
    return Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")


def laminate(w, h, seed, base, k=6, gk=3):
    """Textured (orange-peel) laminate in a flat colour."""
    n = noise(w, h, 24, seed, 3)
    g = grain(w, h, seed + 1, gk)
    a = np.zeros((h, w, 3), np.float32)
    for i in range(3):
        a[..., i] = base[i] + (n - 0.5) * k + g
    return a


# ---------------------------------------------------------------- 7-segment digits
SEG = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd",
       "6": "afgedc", "7": "abc", "8": "abcdefg", "9": "abcdfg", "-": "g", " ": ""}


def seg_digit(d, x, y, w, h, ch, on, off, t=None, slant=0.12):
    """One slanted 7-segment digit, top-left (x, y), w x h px."""
    t = t or max(3, int(w * 0.17))
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


# ---------------------------------------------------------------- playfield
FIELD_W, FIELD_H = 1024, 512     # u along the table (2.25 m), v across (1.20 m)


def field_rgb():
    """The playfield as a float RGB array (h, w, 3)."""
    W, H = FIELD_W, FIELD_H
    pu, pv = W / PF_L, H / PF_W
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    zm = (xx + 0.5) / pu            # metres along the table from the near end rail
    xm = (yy + 0.5) / pv - PF_W / 2  # metres across, 0 = centre
    base = np.array([32, 74, 152], np.float32)
    n = noise(W, H, 90, 101, 3)
    a = base[None, None, :] * (0.95 + 0.1 * n)[..., None]
    # painted markings: slightly lighter or darker blue, matte silkscreen
    m_light = np.zeros((H, W), np.float32)
    m_dark = np.zeros((H, W), np.float32)
    def ring(cz, cx, r, w):
        d = np.abs(np.hypot(zm - cz, xm - cx) - r)
        return np.clip(1.0 - (d - w / 2) * pu, 0, 1)
    def band(dist, w):
        return np.clip(1.0 - (np.abs(dist) - w / 2) * pu, 0, 1)
    mid = PF_L / 2
    m_dark = np.maximum(m_dark, band(zm - mid, 0.016))                 # centre line
    m_light = np.maximum(m_light, ring(mid, 0.0, 0.16, 0.010))         # centre circle
    m_dark = np.maximum(m_dark, np.clip(1.0 - (np.hypot(zm - mid, xm) - 0.022) * pu, 0, 1))  # centre spot
    for e in (0.0, PF_L):
        cr = ring(e, 0.0, 0.24, 0.010)
        m_light = np.maximum(m_light, cr)                               # goal crease
        fz = abs(e - 0.56)
        m_light = np.maximum(m_light, ring(fz, 0.0, 0.085, 0.008))     # faceoff circles
        m_dark = np.maximum(m_dark, np.clip(1.0 - (np.hypot(zm - fz, xm) - 0.014) * pu, 0, 1))
    # two thin "blue lines" a third of the way along
    for z in (PF_L / 3, 2 * PF_L / 3):
        m_dark = np.maximum(m_dark, band(zm - z, 0.008) * 0.7)
    a = a * (1 - m_light[..., None]) + np.array([96, 150, 222], np.float32) * m_light[..., None]
    a = a * (1 - m_dark[..., None]) + np.array([26, 54, 128], np.float32) * m_dark[..., None]
    # air holes: a ~2.5 cm grid of small dark dots (88 x 47)
    nz, nx = 88, 47
    sz, sx = PF_L / nz, PF_W / nx
    dz = ((zm / sz) % 1.0 - 0.5) * sz
    dx = (((xm + PF_W / 2) / sx) % 1.0 - 0.5) * sx
    hole = np.clip(1.0 - (np.hypot(dz, dx) - 0.0014) * pu * 0.9, 0, 1)
    inside = (np.abs(xm) < PF_W / 2 - 0.02) & (zm > 0.02) & (zm < PF_L - 0.02)
    a *= (1 - 0.42 * hole * inside)[..., None]
    # goal mouths: the field darkens into the slot under the end rails
    for e in (0.0, PF_L):
        gm = np.clip(1.0 - np.abs(zm - e) / 0.02, 0, 1) * (np.abs(xm) < 0.13)
        a *= (1 - 0.7 * gm)[..., None]
    # dirt along the rails
    edge = np.minimum(np.minimum(zm, PF_L - zm), PF_W / 2 - np.abs(xm))
    a *= (0.82 + 0.18 * np.clip(edge / 0.05, 0, 1))[..., None]
    return a, zm, xm, pu


def paint_field():
    a, zm, xm, pu = field_rgb()
    W, H = FIELD_W, FIELD_H
    # mallet wear: a pale abraded haze in the goal halves, strongest round the creases
    for e in (0.0, PF_L):
        d = np.hypot((zm - e) * 1.0, xm * 0.8)
        haze = np.exp(-((d - 0.33) / 0.22) ** 2) * (0.55 + 0.45 * noise(W, H, 40, 111 + int(e), 2))
        a = a * (1 - 0.22 * haze[..., None]) + np.array([150, 180, 220], np.float32) * 0.22 * haze[..., None]
    im = to_img(a)
    # swirl scratches from the mallets near both goals, puck streaks everywhere
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    rnd = random.Random(121)
    for k in range(260):
        e = 0 if k % 2 == 0 else W
        r = rnd.uniform(0.08, 0.55) * pu
        cx = e + (rnd.uniform(0.15, 0.45) * pu if e == 0 else -rnd.uniform(0.15, 0.45) * pu)
        cy = H / 2 + rnd.uniform(-0.4, 0.4) * pu
        a0 = rnd.uniform(0, 360)
        d.arc([cx - r, cy - r, cx + r, cy + r], a0, a0 + rnd.uniform(15, 70), fill=(200, 220, 245, rnd.randint(16, 46)), width=1)
    for k in range(70):   # black puck/rubber streaks
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        ang = rnd.uniform(0, math.pi)
        l = rnd.uniform(6, 40)
        d.line([x, y, x + math.cos(ang) * l, y + math.sin(ang) * l], fill=(10, 14, 30, rnd.randint(30, 80)), width=rnd.choice((1, 1, 2)))
    im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
    im = smudges(im, 122, 60, (0, 0, W, H), (190, 205, 230), 14, 16, 4)
    im = scuffs(im, 123, 160, None, (180, 200, 230), 40, 30)
    save(im, "field")
    # the glow under the lamp: the same field, faded toward both ends (emission texture)
    g = np.asarray(im.resize((256, 128), Image.BILINEAR), np.float32)
    yy, xx = np.mgrid[0:128, 0:256].astype(np.float32)
    zz = (xx + 0.5) / 256 * PF_L - PF_L / 2
    x2 = (yy + 0.5) / 128 * PF_W - PF_W / 2
    fall = 1.0 / (1.0 + (zz / 0.75) ** 2 + (x2 / 0.9) ** 2) ** 1.5
    g = g * (0.10 + 0.90 * fall)[..., None] * np.array([1.05, 1.05, 1.0])
    save(to_img(g), "fieldglow")


# ---------------------------------------------------------------- cabinet
WHITE = (214, 216, 218)
BLUE = (30, 42, 132)
GOLD = (176, 150, 70)


def skirt_bands(a, H, Y, ppm):
    """Royal-blue band with thin gold pinstripes, painted across a skirt array."""
    def fill(y0, y1, col):
        r0, r1 = int(round(Y(y1))), int(round(Y(y0)))
        a[r0:r1, :, :] = np.array(col, np.float32)[None, None, :] + (a[r0:r1, :, :] - np.array(WHITE, np.float32)) * 0.6
    fill(0.405, 0.525, BLUE)
    fill(0.525, 0.531, GOLD)
    fill(0.399, 0.405, GOLD)
    # bottom edge of the skirt: worn darker lip
    fill(0.300, 0.312, (150, 152, 156))
    # top edge under the rail: shadowed seam
    fill(0.770, 0.780, (120, 122, 126))
    return a


def wear_cabinet(im, seed, W, H, ppm, ends=True):
    rnd = random.Random(seed)
    im = scuffs(im, seed + 1, 260, None, (110, 110, 116), 70, 26)
    im = scuffs(im, seed + 2, 60, (0, H * 0.7, W, H), (40, 40, 46), 90, 18, 2)   # shoe kicks
    im = smudges(im, seed + 3, 40, (0, 0, W, H * 0.4), (120, 116, 110), 12, 10, 3)     # hands on the top edge
    a = np.asarray(im, np.float32)
    # grime: low frequency, darker toward the floor
    n = noise(W, H, 60, seed + 4, 3)
    yy = np.mgrid[0:H, 0:W][0].astype(np.float32) / H
    a *= (0.93 + 0.07 * n - 0.06 * yy ** 2)[..., None]
    a = a * 0.97 + np.array([6, 4, 0])   # a little yellowing
    return to_img(a)


def paint_side():
    """Long side skirt, 2.45 x 0.48 m (y 0.78 at the top .. 0.30), 1024 x 200."""
    W, H = 1024, 200
    ppm = W / L
    def Y(y): return (0.78 - y) * H / SK_H
    a = laminate(W, H, 201, WHITE, 8, 4)
    a = skirt_bands(a, H, Y, ppm)
    im = to_img(a)
    d = ImageDraw.Draw(im)
    # the generic AIR HOCKEY label on the band, toward the right-hand end (u 0.66..0.86)
    x0, x1 = 0.66 * W, 0.86 * W
    yc = Y(0.465)
    hh = 0.040 * H / SK_H
    lab = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lab)
    ld.rounded_rectangle([x0, yc - hh, x1, yc + hh], int(hh), fill=(236, 236, 232, 255), outline=(20, 24, 70, 255), width=2)
    ld.text(((x0 + x1) / 2, yc + 1), "AIR HOCKEY", font=font(F_BO, int(hh * 1.35)), fill=(16, 22, 74, 255), anchor="mm")
    lab = lab.transform(lab.size, Image.AFFINE, (1, 0.12, -0.12 * yc, 0, 1, 0), Image.BICUBIC)   # a little italic lean
    im.paste(lab, (0, 0), lab)
    # small serial plate at the left end, low
    d.rectangle([0.14 * W, Y(0.37), 0.14 * W + 26, Y(0.355)], fill=(176, 176, 170), outline=(90, 90, 90))
    im = wear_cabinet(im, 210, W, H, ppm)
    # edge wear where hips and hands rub, both ends
    im = smudges(im, 220, 24, (0, 0, 0.12 * W, H), (90, 88, 84), 16, 12, 3)
    im = smudges(im, 221, 24, (0.88 * W, 0, W, H), (90, 88, 84), 16, 12, 3)
    save(im, "side")


def paint_end():
    """End skirt (bowed), 1.35 x 0.48 m (y 0.78 .. 0.30), 512 x 182. u = player's left to right."""
    W, H = 512, 182
    ppm = W / WID
    def Y(y): return (0.78 - y) * H / SK_H
    def X(x): return (x + WID / 2) * ppm
    a = laminate(W, H, 301, WHITE, 8, 4)
    a = skirt_bands(a, H, Y, ppm)
    im = to_img(a)
    d = ImageDraw.Draw(im)
    # puck-return opening under the goal: a black mouth in a grey moulded surround
    d.rounded_rectangle([X(-0.125), Y(0.715), X(0.125), Y(0.585)], 8, fill=(70, 72, 76))
    d.rounded_rectangle([X(-0.105), Y(0.70), X(0.105), Y(0.625)], 6, fill=(8, 8, 10))
    text_c(d, (X(0.0), Y(0.735)), "PUCK RETURN", font(F_BC, 9), (40, 40, 44))
    im = wear_cabinet(im, 310, W, H, ppm)
    # the mouth gets grubby: dark hand marks round it
    im = smudges(im, 320, 26, (X(-0.2), Y(0.75), X(0.2), Y(0.56)), (40, 38, 36), 50, 10)
    save(im, "end")


def paint_leg():
    """Grey corner legs: tileable textured laminate, 1 repeat per metre, 256 x 256."""
    W = 256
    a = laminate(W, W, 401, (98, 100, 106), 10, 5)
    im = to_img(a)
    im = scuffs(im, 402, 120, None, (190, 190, 196), 60, 30)
    im = scuffs(im, 403, 40, None, (40, 40, 44), 70, 16, 2)
    save(im, "leg")


def paint_rail():
    """Top of the aluminium rails: 2.47 x 0.083 m (side rails; the end rails use u 0..0.55).
    Brushed along the length, a screw every 15 cm near the outer edge, a worn inner edge."""
    W, H = 1024, 36
    ppm = W / 2.474
    rs = np.random.RandomState(501)
    streak = rs.rand(H, 1).astype(np.float32) * 0.6 + rs.rand(H, W).astype(np.float32) * 0.4
    streak = np.asarray(Image.fromarray((streak * 255).astype(np.uint8)).filter(ImageFilter.BoxBlur(0)), np.float32) / 255
    n = noise(W, H, 40, 502, 2)
    a = np.zeros((H, W, 3), np.float32)
    for i, c in enumerate((176, 178, 182)):
        a[..., i] = c * (0.88 + 0.1 * streak + 0.08 * n)
    # bevelled edges: outer edge (v = 0) rolls off darker, inner edge (v = 1) bright worn
    a[0:3] *= 0.7
    a[H - 3:H] = a[H - 3:H] * 0.6 + 90
    im = to_img(a)
    d = ImageDraw.Draw(im)
    z = 0.10
    while z < 2.47:
        x = z * ppm
        d.ellipse([x - 3, 7, x + 3, 13], fill=(70, 70, 74), outline=(40, 40, 42))
        d.line([x - 2, 10, x + 2, 10], fill=(20, 20, 20))
        z += 0.15
    im = smudges(im, 503, 80, None, (60, 56, 50), 30, 6, 1)
    im = scuffs(im, 504, 120, None, (230, 230, 236), 60, 20)
    save(im, "rail")


def paint_acrylic():
    """Clear acrylic side guard, 2.10 x 0.15 m, 512 x 40 RGBA. Rounded top corners at
    both ends, a bright polished edge, fingerprints and scratches."""
    W, H = 512, 40
    ppm = W / 2.10
    S = 4
    big = Image.new("L", (W * S, H * S), 0)
    bd = ImageDraw.Draw(big)
    r = 0.11 * ppm * S
    bd.rounded_rectangle([0, 0, W * S - 1, H * S + r], int(r), fill=255)
    shape = np.asarray(big.resize((W, H), Image.LANCZOS), np.float32) / 255
    edge_big = Image.new("L", (W * S, H * S), 0)
    ImageDraw.Draw(edge_big).rounded_rectangle([0, 0, W * S - 1, H * S + r], int(r), outline=255, width=int(2.2 * S))
    edge = np.asarray(edge_big.resize((W, H), Image.LANCZOS), np.float32) / 255
    a = np.zeros((H, W, 4), np.float32)
    a[..., 0], a[..., 1], a[..., 2] = 225, 238, 236
    alpha = 0.07 + 0.03 * noise(W, H, 40, 601, 2)
    # fingerprints: soft greasy blobs, mostly along the top half where hands grab
    fp = Image.new("L", (W, H), 0)
    fd = ImageDraw.Draw(fp)
    rnd = random.Random(602)
    for _ in range(90):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H * 0.8)
        rr = rnd.uniform(2, 5)
        fd.ellipse([x - rr, y - rr * 1.3, x + rr, y + rr * 1.3], fill=rnd.randint(40, 110))
    fp = np.asarray(fp.filter(ImageFilter.GaussianBlur(1.2)), np.float32) / 255
    sc = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(sc)
    for _ in range(60):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        ang = rnd.uniform(-0.4, 0.4)
        l = rnd.uniform(3, 30)
        sd.line([x, y, x + math.cos(ang) * l, y + math.sin(ang) * l], fill=rnd.randint(60, 160))
    sc = np.asarray(sc, np.float32) / 255
    alpha = alpha + fp * 0.14 + sc * 0.08 + edge * 0.55
    # the bottom edge sits in the rail channel: a darker line
    alpha[H - 2:] = 0.5
    a[H - 2:, :, :3] = 60
    a[..., 3] = np.clip(alpha * shape, 0, 1) * 255
    save(to_img(a), "acrylic")


# ---------------------------------------------------------------- lamp / score unit
def paint_unit():
    """End face of the lamp/score box, 0.36 x 0.135 m, 448 x 168: silver painted steel,
    a black bezel round the LED window (the LED quad is x -0.115..0.115, y 0.025..0.11)."""
    W, H = 448, 168
    ppm = W / 0.36
    a = laminate(W, H, 701, (196, 194, 186), 10, 4)
    im = to_img(a)
    d = ImageDraw.Draw(im)
    def X(x): return (x + 0.18) * ppm
    def Y(y): return (0.135 - y) * ppm
    d.rounded_rectangle([X(-0.128), Y(0.122), X(0.128), Y(0.013)], 6, fill=(18, 18, 20), outline=(90, 90, 94), width=2)
    for sx in (-0.16, 0.16):
        for sy in (0.02, 0.115):
            d.ellipse([X(sx) - 3, Y(sy) - 3, X(sx) + 3, Y(sy) + 3], fill=(120, 120, 120), outline=(70, 70, 70))
    im = scuffs(im, 702, 80, None, (120, 118, 112), 60, 20)
    a = np.asarray(im, np.float32)
    a *= (0.94 + 0.06 * noise(W, H, 50, 703, 2))[..., None]
    save(to_img(a), "unit")


def paint_led():
    """Red LED score windows, 0.24 x 0.12 m each. 2 rows (machines 1, 2) x 2 columns
    (end A, end B), 256 x 128 per cell. Left digit = this end's left player."""
    W, H = 512, 256
    im = Image.new("RGB", (W, H), (10, 2, 3))
    d = ImageDraw.Draw(im)
    scores = [(4, 6), (2, 5)]
    on, off = (255, 44, 28), (30, 5, 5)
    for r, (sa, sb) in enumerate(scores):
        for c in range(2):
            x0, y0 = c * 256, r * 128
            left, right = (sa, sb) if c == 0 else (sb, sa)
            for yy in range(128):
                v = int(8 + 8 * (1 - yy / 128))
                d.line([x0, y0 + yy, x0 + 255, y0 + yy], fill=(v + 6, 2, 3))
            d.rectangle([x0 + 124, y0 + 8, x0 + 131, y0 + 119], fill=(3, 1, 1))     # divider
            dw, dh = 54, 88
            seg_digit(d, x0 + 32, y0 + 20, dw, dh, str(left), on, off)
            seg_digit(d, x0 + 160, y0 + 20, dw, dh, str(right), on, off)
            # tiny red dot "possession" lamp beside the leading score
            lx = x0 + 110 if left > right else x0 + 238
            d.ellipse([lx - 3, y0 + 100, lx + 3, y0 + 106], fill=on)
    a = np.asarray(im, np.float32)
    bl = np.asarray(im.filter(ImageFilter.GaussianBlur(6)), np.float32)
    a = a + bl * 0.45
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    glare = np.exp(-((((xx % 256) * 0.4 + (yy % 128) * 1.0) - 110) / 16) ** 2) * 14
    a += glare[..., None]
    save(to_img(a), "led")


def paint_lamp():
    """Underside lamp face, 0.42 x 0.20 m: a prismatic diffuser over two fluorescent tubes."""
    W, H = 256, 128
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    tubes = np.exp(-((yy - H * 0.32) / 12) ** 2) + np.exp(-((yy - H * 0.68) / 12) ** 2)
    ends = np.clip(np.minimum(xx, W - xx) / 30.0, 0, 1)
    prism = 0.5 + 0.5 * np.cos(xx * 1.4) * np.cos(yy * 1.4)
    lum = (0.62 + 0.38 * tubes) * (0.75 + 0.25 * ends) * (0.93 + 0.07 * prism)
    a = np.zeros((H, W, 3), np.float32)
    a[..., 0], a[..., 1], a[..., 2] = 255 * lum, 250 * lum, 236 * lum
    # dead flies and dust in the diffuser
    im = to_img(a)
    im = smudges(im, 801, 14, None, (60, 56, 50), 70, 3, 0.6)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, H - 1], outline=(150, 150, 150), width=3)
    save(im, "lamp")


def paint_door():
    """Coin door, 0.20 x 0.25 m, 192 x 240: two token entries with lit inserts (the
    lit parts are separate quads), reject buttons, lock, coin-return cup, TOKENS ONLY."""
    W, H = 192, 240
    ppm = W / 0.20
    n = noise(W, H, 30, 901, 2)
    a = np.zeros((H, W, 3), np.float32)
    for i, c in enumerate((70, 72, 76)):
        a[..., i] = c * (0.85 + 0.25 * n)
    im = to_img(a)
    d = ImageDraw.Draw(im)
    d.rectangle([1, 1, W - 2, H - 2], outline=(28, 28, 30), width=3)
    d.rectangle([5, 5, W - 6, H - 6], outline=(110, 110, 116), width=1)
    for cx in (0.055 * ppm, 0.145 * ppm):
        y0 = 0.025 * ppm
        d.rounded_rectangle([cx - 24, y0, cx + 24, y0 + 92], 5, fill=(40, 40, 44), outline=(20, 20, 22), width=2)
        d.rectangle([cx - 11, y0 + 8, cx + 11, y0 + 40], fill=(120, 30, 20))     # coin entry insert (lit quad over it)
        d.rectangle([cx - 2, y0 + 12, cx + 2, y0 + 36], fill=(6, 6, 6))
        d.ellipse([cx - 10, y0 + 50, cx + 10, y0 + 70], fill=(150, 150, 156), outline=(30, 30, 30))
        d.rectangle([cx - 20, y0 + 76, cx + 20, y0 + 90], fill=(226, 190, 60))
        text_c(d, (cx, y0 + 83), "1 TOKEN", font(F_BC, 9), (40, 26, 8))
    cx, cy = W / 2, 0.15 * ppm
    d.rectangle([cx - 60, cy - 10, cx + 60, cy + 10], fill=(232, 228, 214))
    text_c(d, (cx, cy), "TOKENS ONLY", font(F_BC, 13), (170, 20, 20))
    text_c(d, (cx, cy + 22), "2 TOKENS PER GAME", font(F_BC, 10), (210, 206, 196))
    lx, ly = 0.165 * ppm, 0.20 * ppm
    d.ellipse([lx - 9, ly - 9, lx + 9, ly + 9], fill=(180, 176, 160), outline=(50, 50, 50), width=2)
    d.rectangle([lx - 2, ly - 6, lx + 2, ly + 6], fill=(30, 30, 30))
    rx, ry = 0.085 * ppm, 0.215 * ppm
    d.rounded_rectangle([rx - 38, ry - 16, rx + 38, ry + 16], 6, fill=(30, 30, 34), outline=(14, 14, 14), width=2)
    d.rounded_rectangle([rx - 31, ry - 9, rx + 31, ry + 12], 5, fill=(4, 4, 5))
    im = smudges(im, 902, 40, (0, 0, W, H * 0.6), (150, 146, 136), 30, 9)
    im = scuffs(im, 903, 100, None, (170, 170, 170), 70, 16)
    save(im, "door")


if __name__ == "__main__":
    paint_field(); paint_side(); paint_end(); paint_leg(); paint_rail(); paint_acrylic()
    paint_unit(); paint_led(); paint_lamp(); paint_door()
    tot = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT) if f.startswith("airhockey_") and f.endswith(".png"))
    print("total", tot)
