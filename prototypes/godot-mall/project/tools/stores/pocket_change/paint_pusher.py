"""Paints the textures of the Pocket Change coin pusher (module `pusher`).

A mid-1990s three-player "penny falls" coin pusher in the British seaside style (Steven's
reference photos: a Crompton's-type cabinet): blue lower doors with black payout cups, grey
side wings, a blue coin-entry band with three chrome coin mechanisms, a big sloped glass
window over a two-tier playfield heaped with coppers, back-lit space-art translites, and a
back-lit top marquee. The invented title is COIN COMET (red chrome 3D letters on a blue
sparkle ground, a starred ribbon and a heap of gold coins, after the style of the period's
pusher marquees). No real game's name, logo, characters or artwork is used.

Every texture is drawn for a known physical size (pusher.gd holds the matching UVs).
Run from the project folder:  python3 tools/stores/pocket_change/paint_pusher.py
Writes tex/pc/pusher_*.png (including pusher_marquee_blank.png, the word-free marquee for
the owner-editable name). Seeded, so re-running reproduces the same files.
"""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(PROJ, "tex", "pc")
os.makedirs(OUT, exist_ok=True)

F_BLACK_I = os.path.join(PROJ, "fonts", "sans_italic.otf")   # Inter Display Black Italic (the live sign font)
F_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_BC = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"
F_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_BI = "/usr/share/fonts/truetype/google-fonts/Poppins-BoldItalic.ttf"

# copper pennies (new to tarnished) and some silver
COPPER = [(214, 128, 74), (196, 112, 62), (178, 98, 56), (160, 88, 52), (138, 78, 48),
          (120, 70, 44), (188, 120, 78), (150, 96, 64)]
SILVER = [(190, 192, 196), (168, 170, 176), (146, 150, 156)]


def font(p, s):
    return ImageFont.truetype(p, s)


def save(im, name, colors=0):
    p = os.path.join(OUT, "pusher_%s.png" % name)
    if colors:
        im = im.convert("RGB").quantize(colors, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG)
    im.save(p, optimize=True)
    print("pusher_%s.png" % name, im.size, os.path.getsize(p))


def to_img(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


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


def tile_noise(w, h, seed, terms=10, kmax=5):
    """Tileable low-frequency noise in about [-1, 1] (a sum of whole-period waves)."""
    rs = np.random.RandomState(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = np.zeros((h, w), np.float32)
    for _ in range(terms):
        kx, ky = rs.randint(-kmax, kmax + 1), rs.randint(-kmax, kmax + 1)
        if kx == 0 and ky == 0:
            continue
        ph = rs.uniform(0, math.tau)
        a += np.cos(math.tau * (kx * xx / w + ky * yy / h) + ph) / math.hypot(kx, ky)
    return a / (np.abs(a).max() + 1e-6)


def grain(w, h, seed, k):
    rs = np.random.RandomState(seed)
    return (rs.rand(h, w).astype(np.float32) - 0.5) * k


def paint_flat(w, h, col, seed, k=6, cell=40, flake=0):
    """Painted or laminated panel: base colour with soft mottling (and metal flake)."""
    n = noise(w, h, cell, seed, 3)
    a = np.zeros((h, w, 3), np.float32)
    for i in range(3):
        a[..., i] = col[i] + (n - 0.5) * k
    if flake:
        a += grain(w, h, seed + 3, flake)[..., None]
    return a


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
    """Soft greasy hand marks."""
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


def star(d, cx, cy, r, col, pts=5, inner=0.45, rot=-90, outline=None, width=1):
    p = []
    for i in range(pts * 2):
        a = math.radians(rot + i * 180 / pts)
        rr = r if i % 2 == 0 else r * inner
        p.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(p, fill=col, outline=outline, width=width)


def sparkle(d, cx, cy, r, col):
    star(d, cx, cy, r, col, pts=4, inner=0.16, rot=-90)


def glow(im, cx, cy, r, col, strength=1.0):
    """Additive soft radial glow."""
    a = np.asarray(im).astype(np.float32)
    h, w, _ = a.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    g = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (r * r))) * strength
    for i in range(3):
        a[..., i] += g * col[i]
    return to_img(a)


def backlit(im, tubes=(0.3, 0.7), seed=0, ends=0.2):
    """Flat art as a fluorescent-backlit translucent panel: tube hot bands, darker ends,
    faint diffuser grain."""
    a = np.asarray(im).astype(np.float32)
    h, w, _ = a.shape
    y = np.linspace(0, 1, h)[:, None]
    x = np.linspace(0, 1, w)[None, :]
    f = 0.84
    for t in tubes:
        f = f + 0.12 * np.exp(-((y - t) / 0.18) ** 2)
    f = f * (1.0 - ends * (np.abs(x - 0.5) * 2) ** 3)
    a = a * f[:, :, None]
    return to_img(a)


def text_mask(text, fpath, size, skew=0.0, track=0):
    """White-on-black L mask of text, cropped, optional italic skew and letter tracking."""
    f = font(fpath, size)
    widths = [f.getlength(ch) for ch in text]
    tw = int(sum(widths) + track * (len(text) - 1) + size * 2)
    im = Image.new("L", (int(tw + size * abs(skew)), int(size * 2.0)), 0)
    d = ImageDraw.Draw(im)
    x = size * 0.5
    for ch, wd in zip(text, widths):
        d.text((x, size * 0.2), ch, font=f, fill=255)
        x += wd + track
    if skew:
        im = im.transform(im.size, Image.AFFINE, (1, skew, -skew * im.size[1] * 0.5, 0, 1, 0), Image.BICUBIC)
    bb = im.getbbox()
    return im.crop(bb)


def grow(mask, r):
    """Round dilation of an L mask by about r pixels (pads the result by p, returned)."""
    pad = int(r * 2 + 4)
    m = Image.new("L", (mask.size[0] + pad * 2, mask.size[1] + pad * 2), 0)
    m.paste(mask, (pad, pad))
    if r <= 0:
        return m, pad
    b = m.filter(ImageFilter.GaussianBlur(r * 0.5))
    a = np.asarray(b).astype(np.float32)
    a = np.clip((a - 6) * 10, 0, 255)
    return to_img(a), pad


def gold_coin(d, cx, cy, rx, ry, base=(236, 178, 40), seed=0):
    """A gold coin seen at an angle (cartoon-realistic, for marquees and translites)."""
    rnd = random.Random(seed)
    dark = tuple(int(c * 0.55) for c in base)
    mid = tuple(int(c * 0.82) for c in base)
    hi = tuple(min(255, int(c * 1.18) + 30) for c in base)
    th = max(2, ry * 0.28)
    d.ellipse([cx - rx, cy - ry + th, cx + rx, cy + ry + th], fill=dark)
    d.rectangle([cx - rx, cy, cx + rx, cy + th], fill=dark)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=mid)
    d.ellipse([cx - rx * 0.86, cy - ry * 0.86, cx + rx * 0.86, cy + ry * 0.86], fill=base)
    d.ellipse([cx - rx * 0.62, cy - ry * 0.62, cx + rx * 0.62, cy + ry * 0.62], outline=mid, width=max(1, int(rx * 0.08)))
    d.arc([cx - rx * 0.8, cy - ry * 0.8, cx + rx * 0.8, cy + ry * 0.8], 200, 290, fill=hi, width=max(1, int(rx * 0.14)))
    if rx > 9:
        star(d, cx, cy, rx * 0.34, mid, inner=0.45)


# ---------------------------------------------------------------- marquee
def paint_marquee(text=True):
    """Top marquee, 1024 x 256 for the 1.544 x 0.29 m back-lit face."""
    W, H = 1024, 256
    S = 2
    w, h = W * S, H * S
    # blue patterned ground: deep blue, lighter in the middle, with a fine dot screen
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((xx - w / 2) / (w * 0.55)) ** 2 + ((yy - h * 0.45) / (h * 0.9)) ** 2)
    base = np.clip(1.0 - r * 0.6, 0.35, 1.0)
    a = np.zeros((h, w, 3), np.float32)
    a[..., 0] = 14 + 30 * base
    a[..., 1] = 40 + 70 * base
    a[..., 2] = 150 + 95 * base
    # dot screen (diagonal grid) as on the period's printed marquees
    p = 14.0
    u = (xx + yy) / p
    v = (xx - yy) / p
    dots = np.exp(-(((u - np.round(u)) ** 2 + (v - np.round(v)) ** 2) / 0.05))
    a += dots[..., None] * np.array([30, 50, 60], np.float32) * (0.5 + base[..., None])
    im = to_img(a)
    d = ImageDraw.Draw(im)
    rnd = random.Random(31)
    # little stars and sparkles in the blue
    for _ in range(90):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h * 0.8)
        sparkle(d, x, y, rnd.uniform(4, 11), (200, 230, 255))
    for _ in range(14):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h * 0.75)
        sparkle(d, x, y, rnd.uniform(14, 22), (255, 255, 255))
    # the comet: a hot head just past the last letter, its tail streaking left along the top
    im = comet(im, 1985, 60, 183, 920, 30, col=(255, 110, 30), wave=8)
    d = ImageDraw.Draw(im)
    # gold coins: a heap along the bottom, either side of the ribbon, and a few flying
    coins = []
    for _ in range(170):
        side = rnd.choice([-1, 1])
        x = w / 2 + side * rnd.uniform(270, 1060)
        hgt = 70 + 40 * math.sin(x / 140.0) + 30 * (1 - abs(x - w / 2) / (w / 2))
        y = h - rnd.uniform(0, hgt) + 6
        coins.append((y, x, rnd.uniform(26, 36)))
    for _ in range(40):
        x = rnd.uniform(130, w - 60)
        y = rnd.uniform(h * 0.72, h + 10)
        if abs(x - w / 2) > 300:
            coins.append((y, x, rnd.uniform(24, 32)))
    for (x, y) in [(70, 210), (300, 60), (1820, 150), (1980, 240), (260, 300), (1700, 330), (40, 380)]:
        coins.append((y, x, 30))
    coins.sort()
    for i, (y, x, rr) in enumerate(coins):
        gold_coin(d, x, y, rr, rr * rnd.uniform(0.45, 0.8), base=rnd.choice([(240, 184, 46), (230, 170, 36), (250, 198, 70)]), seed=i)
    # ribbon banner with stars below the letters
    cx, cy = w / 2, h - 66
    bw, bh = 560, 64
    dk = (120, 10, 14)
    for s in (-1, 1):
        tx = cx + s * (bw / 2 + 40)
        d.polygon([(cx + s * (bw / 2 - 30), cy - bh / 2 + 18), (tx + s * 70, cy - bh / 2 + 18), (tx + s * 30, cy + 8 + 18),
                   (tx + s * 70, cy + bh / 2 + 18), (cx + s * (bw / 2 - 30), cy + bh / 2 + 18)], fill=dk, outline=(60, 0, 0))
    for s in (-1, 1):
        d.polygon([(cx + s * (bw / 2 - 30), cy + bh / 2 + 18), (cx + s * (bw / 2), cy + bh / 2), (cx + s * (bw / 2 - 30), cy + bh / 2)], fill=(70, 0, 0))
    d.rounded_rectangle([cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2], radius=10, fill=(214, 28, 30), outline=(110, 8, 10), width=4)
    d.line([cx - bw / 2 + 8, cy - bh / 2 + 9, cx + bw / 2 - 8, cy - bh / 2 + 9], fill=(250, 110, 100), width=4)
    for k in (-3, -2, -1, 1, 2, 3):
        star(d, cx + k * 68, cy + 2, 19, (255, 226, 60), outline=(150, 70, 0), width=2)
    # the centre medallion: a gold disc with a small comet
    d.ellipse([cx - 52, cy - 52, cx + 52, cy + 52], fill=(170, 100, 10))
    d.ellipse([cx - 46, cy - 46, cx + 46, cy + 46], fill=(250, 196, 50))
    d.ellipse([cx - 34, cy - 34, cx + 34, cy + 34], fill=(232, 120, 20))
    for k in range(10):
        t = k / 9
        rr = 3 + t * 10
        d.ellipse([cx + 12 - t * 40 - rr, cy - 10 + t * 18 - rr * 0.7, cx + 12 - t * 40 + rr, cy - 10 + t * 18 + rr * 0.7], fill=(255, int(240 - 90 * t), int(170 - 150 * t)))
    d.ellipse([cx + 4, cy - 18, cx + 22, cy], fill=(255, 255, 235))
    if text:
        im = coin_comet_letters(im, (w / 2, h * 0.42), 1830)
    im = im.resize((W, H), Image.LANCZOS)
    im = backlit(im, tubes=(0.35, 0.75), seed=40, ends=0.18)
    d = ImageDraw.Draw(im)
    # a dark border where the aluminium frame clamps the translite
    d.rectangle([0, 0, W - 1, H - 1], outline=(10, 14, 40), width=3)
    return im


def coin_comet_letters(im, centre, max_w):
    """COIN COMET in red chrome 3D letters: a deep extrusion, a dark outline, a gradient face
    with a chrome horizon line and a bright top bevel."""
    m = text_mask("COIN COMET", F_BLACK_I, 260, skew=0.0, track=10)
    k = max_w / m.size[0]
    if True:
        m = m.resize((int(m.size[0] * k), int(m.size[1] * k)), Image.LANCZOS)
    # stretch a little taller, like the chunky display letters of the era
    m = m.resize((m.size[0], int(m.size[1] * 1.12)), Image.LANCZOS)
    cx, cy = centre
    mw, mh = m.size
    x0, y0 = int(cx - mw / 2), int(cy - mh / 2)
    # drop shadow
    g, pad = grow(m, 16)
    sh = g.filter(ImageFilter.GaussianBlur(8))
    im.paste(Image.new("RGB", sh.size, (6, 10, 40)), (x0 - pad + 10, y0 - pad + 16), sh)
    # extrusion: the letters stepped down and right, dark red to near black
    ext = 22
    g, pad = grow(m, 7)
    for i in range(ext, 0, -1):
        t = i / ext
        col = (int(110 - 70 * t), int(10 - 6 * t), int(12 - 8 * t))
        im.paste(Image.new("RGB", g.size, col), (x0 - pad + int(i * 0.45), y0 - pad + i), g)
    # dark outline round the face
    im.paste(Image.new("RGB", g.size, (44, 6, 8)), (x0 - pad, y0 - pad), g)
    g2, pad2 = grow(m, 3)
    im.paste(Image.new("RGB", g2.size, (255, 214, 190)), (x0 - pad2, y0 - pad2), g2)
    # chrome red face
    t = np.linspace(0, 1, mh)[:, None]
    top = np.array([255, 150, 120], np.float32)
    up = np.array([236, 40, 26], np.float32)
    hor = np.array([110, 6, 8], np.float32)
    lo = np.array([250, 70, 44], np.float32)
    bot = np.array([200, 22, 18], np.float32)
    grad = np.zeros((mh, mw, 3), np.float32)
    for i in range(3):
        c = np.where(t < 0.18, top[i] + (up[i] - top[i]) * (t / 0.18),
             np.where(t < 0.5, up[i] + (hor[i] - up[i]) * ((t - 0.18) / 0.32),
             np.where(t < 0.56, hor[i] + (lo[i] - hor[i]) * ((t - 0.5) / 0.06),
                      lo[i] + (bot[i] - lo[i]) * ((t - 0.56) / 0.44))))
        grad[:, :, i] = c
    # a diagonal glint across each letter
    xx = np.arange(mw)[None, :].astype(np.float32)
    gl = np.exp(-((((xx * 0.18 + t * mh * 1.0) % 120) - 30) / 7.0) ** 2) * 70
    grad += gl[..., None] * (t < 0.45)[..., None]
    im.paste(to_img(grad), (x0, y0), m)
    # bright bevel along the top edges of each stroke
    ma = np.asarray(m).astype(np.float32)
    sh2 = np.zeros_like(ma)
    sh2[5:, :] = ma[:-5, :]
    bev = np.clip(ma - sh2, 0, 255) / 255.0
    arr = np.asarray(im).astype(np.float32)
    sub = arr[y0:y0 + mh, x0:x0 + mw]
    sub += bev[..., None] * np.array([120, 120, 110], np.float32)
    arr[y0:y0 + mh, x0:x0 + mw] = sub
    im = to_img(arr)
    d = ImageDraw.Draw(im)
    rnd = random.Random(77)
    for _ in range(5):
        sparkle(d, x0 + rnd.uniform(0.05, 0.95) * mw, y0 + rnd.uniform(0.05, 0.4) * mh, rnd.uniform(14, 22), (255, 255, 255))
    return im


# ---------------------------------------------------------------- translites
def planet(im, cx, cy, r, c0, c1, ring=None, bands=0, seed=0, craters=0):
    """A shaded planet (lit from the upper left), optional ring and bands."""
    a = np.asarray(im).astype(np.float32)
    h, w, _ = a.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dx, dy = (xx - cx) / r, (yy - cy) / r
    rr = dx * dx + dy * dy
    inside = rr <= 1.0
    z = np.sqrt(np.clip(1 - rr, 0, 1))
    lam = np.clip(-0.55 * dx - 0.6 * dy + 0.58 * z, 0, 1)
    shade = 0.25 + 0.85 * lam
    col = np.zeros((h, w, 3), np.float32)
    band = np.zeros((h, w), np.float32)
    if bands:
        band = 0.5 + 0.5 * np.sin(dy * bands * math.pi + np.sin(dx * 3 + seed) * 0.8)
    for i in range(3):
        col[..., i] = (c0[i] * (1 - band) + c1[i] * band) * shade
    rim = np.clip((rr - 0.82) / 0.18, 0, 1) * inside
    col += rim[..., None] * np.array([60, 80, 120], np.float32)
    a[inside] = col[inside]
    im = to_img(a)
    d = ImageDraw.Draw(im)
    rnd = random.Random(seed)
    for _ in range(craters):
        ang = rnd.uniform(0, math.tau)
        dist = rnd.uniform(0, 0.75) * r
        x, y = cx + math.cos(ang) * dist, cy + math.sin(ang) * dist
        cr = rnd.uniform(0.05, 0.14) * r
        d.ellipse([x - cr, y - cr, x + cr, y + cr], outline=tuple(int(c * 0.6) for c in c0), width=max(1, int(cr * 0.25)))
    if ring:
        # ring in front: an ellipse band, the back half hidden by the planet
        ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        for k in range(6):
            rx, ry = r * (1.55 + k * 0.07), r * (0.38 + k * 0.02)
            od.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=ring + (230 - k * 22,), width=max(2, int(r * 0.05)))
        rot = ov.rotate(-14, center=(cx, cy), resample=Image.BICUBIC)
        mask = np.asarray(rot)[..., 3].astype(np.float32)
        ya = np.mgrid[0:h, 0:w][0].astype(np.float32)
        xa = np.mgrid[0:h, 0:w][1].astype(np.float32)
        # behind the planet on the upper side of the ring line
        line_y = cy + (xa - cx) * math.tan(math.radians(-14)) * -1
        hide = inside & (ya < line_y)
        mask[hide] = 0
        rot.putalpha(to_img(mask))
        im = Image.alpha_composite(im.convert("RGBA"), rot).convert("RGB")
    return im


def rocket(d, cx, cy, s, ang, body=(236, 236, 240), fin=(220, 30, 30), win=(80, 180, 255)):
    """A classic finned rocket with a flame, pointing at angle ang (degrees, 0 = up)."""
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    def P(x, y):   # x across, y along (up is negative)
        return (cx + x * ca - y * sa, cy + x * sa + y * ca)
    # flame
    for k, col in enumerate([(255, 120, 20), (255, 200, 40), (255, 250, 200)]):
        f = 1.0 - k * 0.28
        d.polygon([P(-0.22 * s * f, 0.9 * s), P(0, (1.7 + 0.3 * (2 - k)) * s * f + 0.9 * s * (1 - f)), P(0.22 * s * f, 0.9 * s)], fill=col)
    d.polygon([P(-0.3 * s, 0.35 * s), P(-0.62 * s, 0.95 * s), P(-0.3 * s, 0.8 * s)], fill=fin, outline=(60, 0, 0))
    d.polygon([P(0.3 * s, 0.35 * s), P(0.62 * s, 0.95 * s), P(0.3 * s, 0.8 * s)], fill=fin, outline=(60, 0, 0))
    pts = [P(0, -1.2 * s)]
    for i in range(1, 10):
        t = i / 9
        pts.append(P(0.3 * s * math.sin(t * math.pi * 0.62) / math.sin(math.pi * 0.62), -1.2 * s + t * 1.2 * s))
    pts += [P(0.3 * s, 0.85 * s), P(-0.3 * s, 0.85 * s)]
    for i in range(9, 0, -1):
        t = i / 9
        pts.append(P(-0.3 * s * math.sin(t * math.pi * 0.62) / math.sin(math.pi * 0.62), -1.2 * s + t * 1.2 * s))
    d.polygon(pts, fill=body, outline=(40, 40, 60))
    d.polygon([P(0, -1.2 * s), P(0.16 * s, -0.75 * s), P(-0.16 * s, -0.75 * s)], fill=fin)
    wx, wy = P(0, -0.25 * s)
    d.ellipse([wx - 0.17 * s, wy - 0.17 * s, wx + 0.17 * s, wy + 0.17 * s], fill=(40, 40, 60))
    d.ellipse([wx - 0.12 * s, wy - 0.12 * s, wx + 0.12 * s, wy + 0.12 * s], fill=win)
    d.line([P(0, 0.85 * s), P(0, 0.3 * s)], fill=fin, width=max(1, int(s * 0.08)))


def comet(im, hx, hy, ang, length, width, col=(255, 140, 40), seed=0, wave=0.0):
    """A comet with a glowing head and a fanned tail pointing away along `ang` (degrees):
    white-hot at the head, through yellow to `col`, fading out."""
    w, h = im.size
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    cl = Image.new("RGB", (w, h), (0, 0, 0))
    al = Image.new("L", (w, h), 0)
    cd, ad = ImageDraw.Draw(cl), ImageDraw.Draw(al)
    n = 70
    for k in range(n):
        t = 1.0 - k / (n - 1)          # far end first
        rr = width * (0.18 + 0.85 * t)
        x = hx + ca * t * length - sa * math.sin(t * 3.0) * wave
        y = hy + sa * t * length + ca * math.sin(t * 3.0) * wave
        stops = [(0.0, (255, 255, 235)), (0.1, (255, 244, 150)), (0.35, (255, 196, 60)), (0.7, col), (1.0, tuple(int(v * 0.8) for v in col))]
        for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
            if t <= t1:
                q = (t - t0) / (t1 - t0)
                c = tuple(int(a2 + (b2 - a2) * q) for a2, b2 in zip(c0, c1))
                break
        cd.ellipse([x - rr, y - rr, x + rr, y + rr], fill=c)
        ad.ellipse([x - rr, y - rr, x + rr, y + rr], fill=int(255 * (1 - t) ** 0.55))
    rb = width * 0.35
    clb = np.asarray(cl.filter(ImageFilter.GaussianBlur(rb))).astype(np.float32)
    alm = np.asarray(al).astype(np.float32) / 255.0
    alb = np.asarray(al.filter(ImageFilter.GaussianBlur(rb))).astype(np.float32) / 255.0
    # colour is not premultiplied in cl, so weight by a blurred coverage of the drawn area
    cov = np.asarray(Image.fromarray(((np.asarray(cl).sum(axis=2) > 0) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(rb))).astype(np.float32) / 255.0
    colr = clb / np.maximum(cov, 1e-3)[..., None]
    a = np.asarray(im).astype(np.float32)
    k = np.clip(alb * 1.05, 0, 0.97)[..., None]
    a = a * (1 - k) + np.clip(colr, 0, 255) * k
    im = glow(to_img(a), hx, hy, width * 1.5, (255, 250, 230), 0.9)
    d = ImageDraw.Draw(im)
    d.ellipse([hx - width * 0.42, hy - width * 0.42, hx + width * 0.42, hy + width * 0.42], fill=(255, 255, 240))
    star(d, hx, hy, width * 1.05, (255, 255, 235), pts=6, inner=0.25)
    return im


def led_window(d, x, y, w, h, label, digits, fnt):
    """A small black window with red 7-segment-style digits (painted on the translite)."""
    d.rounded_rectangle([x, y, x + w, y + h], radius=6, fill=(14, 10, 12), outline=(220, 220, 230), width=3)
    d.text((x + 8, y + h / 2), label, font=fnt, fill=(255, 230, 60), anchor="lm")
    dw = (w * 0.55) / len(digits)
    for i, ch in enumerate(digits):
        seg_digit(d, x + w * 0.42 + i * dw, y + h * 0.2, dw * 0.78, h * 0.6, ch, (255, 40, 30), (52, 12, 12))


SEG = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd",
       "6": "afgedc", "7": "abc", "8": "abcdefg", "9": "abcdfg"}


def seg_digit(d, x, y, w, h, ch, on, off, slant=0.12):
    t = max(2, w * 0.18)
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


def paint_back():
    """The three back-lit translites behind the playfield: 1024 x 448 for 1.58 x 0.579 m
    (the partitions hide the seams at u = 1/3 and 2/3). Original space art."""
    W, H = 1024, 448
    S = 2
    w, h = W * S, H * S
    pw = w / 3
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    t = yy / h
    a = np.zeros((h, w, 3), np.float32)
    # bright 90s space: cobalt at the top, violet then magenta toward the bottom
    a[..., 0] = 20 + 150 * t ** 1.6
    a[..., 1] = 40 + 30 * t
    a[..., 2] = 170 + 60 * (1 - t)
    neb = noise(w, h, 160, 9, 4)
    a[..., 0] += (neb - 0.5) * 90
    a[..., 2] += (neb - 0.5) * 50
    a[..., 1] += np.clip(neb - 0.62, 0, 1) * 200
    im = to_img(a)
    d = ImageDraw.Draw(im)
    rnd = random.Random(5)
    for _ in range(700):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        r = rnd.choice([1.5, 2, 2.5, 3])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, rnd.randint(200, 255)))
    for _ in range(40):
        sparkle(d, rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(8, 18), (255, 255, 255))
    # panel 1: a ringed orange planet and a rocket
    im = planet(im, pw * 0.36, h * 0.36, 150, (250, 150, 40), (220, 80, 30), ring=(255, 230, 150), bands=5, seed=1)
    d = ImageDraw.Draw(im)
    rocket(d, pw * 0.78, h * 0.62, 70, 35)
    # panel 2: the big comet with coins in its tail
    im = planet(im, pw * 1.8, h * 0.78, 90, (90, 210, 160), (40, 140, 200), bands=3, seed=4)
    im = comet(im, pw * 1.72, h * 0.26, 145, 760, 62, col=(255, 170, 60), seed=2)
    # panel 3: a red cratered planet, a little moon and another rocket
    im = planet(im, pw * 2.62, h * 0.34, 135, (236, 70, 60), (200, 40, 80), bands=0, seed=6, craters=9)
    im = planet(im, pw * 2.2, h * 0.16, 36, (210, 210, 220), (170, 170, 190), seed=7, craters=4)
    d = ImageDraw.Draw(im)
    rocket(d, pw * 2.24, h * 0.66, 64, -30, fin=(30, 120, 240))
    im = comet(im, pw * 0.15, h * 0.12, 200, 220, 20, seed=3)
    im = comet(im, pw * 2.9, h * 0.75, -25, 240, 22, col=(160, 230, 255), seed=8)
    d = ImageDraw.Draw(im)
    # gold coins flying everywhere
    for i in range(70):
        x = rnd.uniform(0, w)
        y = rnd.uniform(h * 0.08, h * 0.95)
        if math.hypot(x - pw * 1.72, y - h * 0.26) < 120 or math.hypot(x - pw * 2.9, y - h * 0.75) < 60:
            continue
        rr = rnd.uniform(18, 34)
        gold_coin(d, x, y, rr, rr * rnd.uniform(0.35, 0.95), base=rnd.choice([(244, 190, 52), (232, 172, 40)]), seed=i + 100)
    # generic word plates and the little LED win counters (top corners)
    f1 = font(F_BLACK_I, 64)
    fl = font(F_BC, 28)
    for k, (word, col) in enumerate([("BONUS", (255, 236, 60)), ("JACKPOT", (255, 236, 60)), ("WIN", (255, 236, 60))]):
        x0 = pw * k
        cx = x0 + pw * 0.5
        y = h * 0.86
        bb = d.textbbox((cx, y), word, font=f1, anchor="mm")
        for o in range(7, 0, -1):
            d.text((cx + o * 0.5, y + o), word, font=f1, fill=(100, 10, 30), anchor="mm")
        d.text((cx, y), word, font=f1, fill=col, anchor="mm", stroke_width=5, stroke_fill=(150, 20, 40))
        led_window(d, x0 + pw * 0.06 if k != 1 else x0 + pw * 0.56, h * 0.05, 250, 64, "WIN", "%03d" % [20, 50, 10][k], fl)
    im = im.resize((W, H), Image.LANCZOS)
    im = backlit(im, tubes=(0.25, 0.65), seed=6, ends=0.1)
    # dark seams where the partitions stand
    d = ImageDraw.Draw(im)
    for u in (W / 3, 2 * W / 3):
        d.rectangle([u - 4, 0, u + 4, H], fill=(20, 20, 30))
    return im


# ---------------------------------------------------------------- cabinet
BLUE = (34, 68, 196)
GREY = (138, 152, 164)


def paint_front():
    """Lower front: three blue doors with locks, dividers and the payout-cup openings.
    1024 x 512 for x -0.79..0.79, y 0.70 (top) .. 0.07 m."""
    W, H = 1024, 512
    a = paint_flat(W, H, BLUE, 21, k=6, cell=90, flake=0)
    # a soft sheen band (gloss paint catching the arcade lights)
    y = np.linspace(0, 1, H)[:, None]
    a *= (0.92 + 0.12 * np.exp(-((y - 0.25) / 0.2) ** 2))[..., None]
    # scuffed lower edge (feet)
    a *= (1.0 - 0.18 * np.clip((y - 0.86) / 0.14, 0, 1))[..., None]
    im = to_img(a)
    d = ImageDraw.Draw(im)
    px = lambda x: (x + 0.79) / 1.58 * W
    py = lambda yy: (0.70 - yy) / 0.63 * H
    # door gaps and aluminium dividers
    for x in (-0.263, 0.263):
        u = px(x)
        d.rectangle([u - 9, 0, u + 9, H], fill=(168, 174, 184))
        d.line([u - 9, 0, u - 9, H], fill=(70, 74, 84), width=2)
        d.line([u + 9, 0, u + 9, H], fill=(70, 74, 84), width=2)
        d.line([u - 3, 0, u - 3, H], fill=(225, 230, 236), width=2)
    # the middle door's split, and top / bottom door edges
    d.rectangle([px(-0.263) + 9, py(0.37) - 6, px(0.263) - 9, py(0.37) + 6], fill=(160, 166, 176))
    d.line([px(-0.263) + 9, py(0.37) - 6, px(0.263) - 9, py(0.37) - 6], fill=(225, 230, 236), width=2)
    d.line([0, 6, W, 6], fill=(14, 22, 70), width=3)
    d.line([0, H - 6, W, H - 6], fill=(14, 22, 70), width=3)
    for cx in (-0.527, 0.0, 0.527):
        u = px(cx)
        # payout opening behind the black cup
        v = py(0.24)
        d.rounded_rectangle([u - 62, v - 36, u + 62, v + 36], radius=8, fill=(18, 18, 20))
        d.rounded_rectangle([u - 54, v - 28, u + 54, v + 28], radius=5, fill=(4, 4, 5))
        # key lock and screws
        lv = py(0.60) if cx != 0.0 else py(0.63)
        d.ellipse([u - 13, lv - 13, u + 13, lv + 13], fill=(70, 72, 78))
        d.ellipse([u - 10, lv - 10, u + 10, lv + 10], fill=(206, 210, 216))
        d.rectangle([u - 2, lv - 7, u + 2, lv + 7], fill=(40, 40, 46))
        for sx in (-1, 1):
            for vv in (py(0.665), py(0.12)):
                d.ellipse([u + sx * 140 - 4, vv - 4, u + sx * 140 + 4, vv + 4], fill=(170, 176, 186), outline=(60, 64, 72))
    # stickers: FOR AMUSEMENT ONLY on the middle door, a serial plate on the right
    f = font(F_BC, 14)
    sx, sy = px(0.0), py(0.50)
    d.rectangle([sx - 84, sy - 14, sx + 84, sy + 14], fill=(232, 226, 206), outline=(150, 140, 120))
    d.text((sx, sy), "FOR AMUSEMENT ONLY", font=f, fill=(170, 26, 26), anchor="mm")
    rx, ry = px(0.70), py(0.50)
    d.rectangle([rx - 40, ry - 14, rx + 40, ry + 14], fill=(176, 178, 182), outline=(90, 90, 96))
    f2 = font(F_R, 10)
    d.text((rx, ry - 5), "MODEL 3P-95", font=f2, fill=(30, 30, 34), anchor="mm")
    d.text((rx, ry + 6), "SER. 04127", font=f2, fill=(30, 30, 34), anchor="mm")
    im = scuffs(im, 22, 200, area=(0, H * 0.72, W, H), col=(140, 160, 225), alpha=45, lmax=26)
    im = scuffs(im, 23, 80, col=(170, 190, 240), alpha=40, lmax=18)
    im = smudges(im, 24, 60, area=(0, 0, W, H * 0.4), col=(255, 255, 255), alpha=12)
    return im


def paint_side():
    """Outer side panel, 512 x 1024 for z 0..1.1 m (u, 0 = front) and y 2.2..0 m (v): blue
    below, the grey wing above a line falling from the front toward the back."""
    W, H = 512, 1024
    blue = paint_flat(W, H, BLUE, 31, k=6, cell=90, flake=0)
    grey = paint_flat(W, H, GREY, 32, k=6, cell=90, flake=0)
    zz = np.linspace(0, 1.1, W)[None, :]
    yy = (1.0 - np.linspace(0, 1, H)[:, None]) * 2.2
    edge_y = 0.74 - (0.74 - 0.42) * zz / 1.1
    m = np.clip((yy - edge_y) / 0.006, 0, 1)
    a = blue * (1 - m[..., None]) + grey * m[..., None]
    # a little darker where the wing meets the blue (a painted shadow line)
    a *= (1.0 - 0.25 * np.exp(-((yy - edge_y) / 0.008) ** 2))[..., None]
    a *= (1.0 - 0.2 * np.clip((0.25 - yy) / 0.2, 0, 1))[..., None]
    im = to_img(a)
    im = scuffs(im, 33, 140, area=(0, H * 0.8, W, H), col=(150, 165, 220), alpha=34, lmax=22)
    im = scuffs(im, 34, 120, area=(0, H * 0.1, W, H * 0.62), col=(200, 205, 210), alpha=45, lmax=22)
    im = smudges(im, 35, 40, area=(0, H * 0.35, W * 0.5, H * 0.62), col=(80, 70, 60), alpha=16)
    return im


def paint_band():
    """Coin-entry band, 1024 x 256 for x -0.79..0.79 and y 1.79 (top) .. 1.48 m: royal blue
    with pale pinstripes, an INSERT COIN sticker under each coin mechanism."""
    W, H = 1024, 256
    a = paint_flat(W, H, (30, 66, 200), 41, k=6, cell=90, flake=0)
    y = np.arange(H)[:, None].astype(np.float32)
    stripes = np.zeros((H, 1), np.float32)
    # pinstripes in bands, thicker toward the bottom (as on the reference)
    for k, yc in enumerate(range(18, H - 10, 13)):
        th = 1.2 + 2.6 * (yc / H)
        stripes += np.exp(-((y - yc) / th) ** 2) * (0.35 + 0.4 * (yc / H))
    a = a * (1 - stripes[..., None] * 0.35) + stripes[..., None] * np.array([110, 170, 255], np.float32) * 0.6
    im = to_img(a)
    d = ImageDraw.Draw(im)
    px = lambda x: (x + 0.79) / 1.58 * W
    py = lambda yy: (1.79 - yy) / 0.31 * H
    f = font(F_BC, 10)
    for cx in (-0.527, 0.0, 0.527):
        u = px(cx)
        # shadow round the coin mech
        d.rounded_rectangle([u - 37, py(1.70), u + 37, py(1.590)], radius=4, fill=(16, 32, 100))
        sv = py(1.555)
        d.rectangle([u - 36, sv - 9, u + 36, sv + 9], fill=(238, 234, 220), outline=(120, 110, 100))
        d.text((u, sv), "INSERT COIN", font=f, fill=(190, 20, 20), anchor="mm")
    im = scuffs(im, 42, 60, col=(170, 190, 250), alpha=40, lmax=14)
    return im


def paint_mech():
    """A chrome coin-entry mechanism face, 128 x 128 for 0.10 x 0.11 m."""
    W = H = 128
    a = np.zeros((H, W, 3), np.float32)
    x = np.linspace(0, 1, W)[None, :]
    yv = np.linspace(0, 1, H)[:, None]
    base = 175 + 50 * np.exp(-((yv - 0.3) / 0.2) ** 2) - 30 * yv + grain(W, H, 50, 10)
    base = base + 6 * np.sin(x * 140)
    for i in range(3):
        a[..., i] = base * [0.97, 0.99, 1.03][i]
    im = to_img(a)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, H - 1], outline=(90, 94, 100), width=3)
    d.rectangle([4, 4, W - 5, H - 5], outline=(235, 238, 242), width=1)
    # the coin slot (vertical) in a raised boss, the reject button below
    d.rounded_rectangle([46, 14, 82, 74], radius=6, fill=(120, 124, 130), outline=(240, 242, 246), width=2)
    d.rectangle([61, 20, 67, 68], fill=(8, 8, 10))
    d.ellipse([52, 84, 76, 108], fill=(60, 60, 66))
    d.ellipse([55, 87, 73, 105], fill=(200, 202, 206))
    for (sx, sy) in [(12, 12), (W - 13, 12), (12, H - 13), (W - 13, H - 13)]:
        d.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=(110, 112, 118), outline=(230, 232, 236))
        d.line([sx - 3, sy, sx + 3, sy], fill=(60, 60, 66), width=1)
    return im


def paint_inner():
    """Inner side walls of the playfield, a 256 x 256 tile for 0.4 m: deep blue with stars."""
    W = H = 256
    a = paint_flat(W, H, (22, 40, 140), 61, k=14, cell=80, flake=4)
    im = to_img(a)
    d = ImageDraw.Draw(im)
    rnd = random.Random(62)
    for _ in range(40):
        x, y = rnd.uniform(8, W - 8), rnd.uniform(8, H - 8)
        sparkle(d, x, y, rnd.uniform(3, 8), (200, 220, 255))
    for _ in range(5):
        x, y = rnd.uniform(16, W - 16), rnd.uniform(16, H - 16)
        star(d, x, y, rnd.uniform(6, 10), (255, 220, 60))
    return im


def paint_ramp():
    """The blue art covering of the deflector ramps, 128 x 512 (u across the slope, base to
    ridge; v along it, back to front): chrome edges, chevrons and stars."""
    W, H = 128, 512
    a = paint_flat(W, H, (26, 80, 220), 71, k=12, cell=40, flake=4)
    im = to_img(a)
    d = ImageDraw.Draw(im)
    for k in range(0, H + 64, 64):
        d.polygon([(14, k), (W / 2, k + 30), (W - 14, k), (W - 14, k + 16), (W / 2, k + 46), (14, k + 16)], fill=(255, 220, 40))
        d.polygon([(14, k + 16), (W / 2, k + 46), (W - 14, k + 16), (W - 14, k + 22), (W / 2, k + 52), (14, k + 22)], fill=(230, 40, 40))
    rnd = random.Random(72)
    for _ in range(18):
        sparkle(d, rnd.uniform(20, W - 20), rnd.uniform(0, H), rnd.uniform(4, 8), (255, 255, 255))
    for x0, x1 in ((0, 12), (W - 12, W)):
        for x in range(x0, x1):
            t = (x - x0) / 11.0
            c = int(150 + 90 * math.sin(t * math.pi))
            d.line([x, 0, x, H], fill=(c, c, c + 6))
    im = scuffs(im, 73, 60, col=(200, 210, 255), alpha=50, lmax=20)
    return im


def paint_perf():
    """Perforated aluminium (side deflectors), a 128 x 128 tile for 0.064 m: 4 mm holes."""
    W = H = 128
    yv = np.linspace(0, 1, H)[:, None]
    a = np.zeros((H, W, 3), np.float32) + 188 + grain(W, H, 80, 12)[..., None]
    a += (8 * np.sin(np.linspace(0, 1, W)[None, :] * 300))[..., None]
    im = to_img(a)
    d = ImageDraw.Draw(im)
    step = 16
    for j in range(0, H // step + 1):
        for i in range(0, W // step + 1):
            x = i * step + (step / 2 if j % 2 else 0)
            y = j * step + step / 2
            for ox in (-W, 0, W):
                d.ellipse([x + ox - 4.5, y - 4.5, x + ox + 4.5, y + 4.5], fill=(18, 20, 40))
                d.arc([x + ox - 5, y - 5, x + ox + 5, y + 5], 200, 340, fill=(240, 242, 246), width=1)
    return im


def paint_glass():
    """Fingerprints, dust and wipe arcs on the window (RGBA, mostly clear). The image bottom
    is the glass's bottom edge, where hands lean."""
    W = H = 256
    r = random.Random(90)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    al = np.zeros((H, W), np.float32) + 16.0
    al += np.exp(-((H - yy) / 10.0)) * 50
    s = xx * 0.7 + yy
    al += np.exp(-((s - 150) / 16) ** 2) * 16 + np.exp(-((s - 210) / 6) ** 2) * 14
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    for _ in range(8):
        cx, cy, rad = r.uniform(0, W), r.uniform(0, H), r.uniform(30, 90)
        st = r.uniform(0, 360)
        d.arc([cx - rad, cy - rad, cx + rad, cy + rad], st, st + r.uniform(40, 120), fill=r.randint(8, 16), width=r.randint(4, 10))
    for _ in range(50):
        x = r.gauss(W * 0.5, W * 0.28)
        y = H - abs(r.gauss(0, H * 0.25)) - 6
        rx, ry = r.uniform(4, 7), r.uniform(5, 9)
        for k in range(int(rx / 1.6)):
            q = k * 1.6
            d.ellipse([x - rx + q, y - ry + q, x + rx - q, y + ry - q], outline=r.randint(14, 30), width=1)
    m = m.filter(ImageFilter.GaussianBlur(0.8))
    al += np.asarray(m).astype(np.float32)
    rgb = np.zeros((H, W, 4), np.float32)
    rgb[..., 0] = 222; rgb[..., 1] = 230; rgb[..., 2] = 238
    rgb[..., 3] = np.clip(al, 0, 255)
    return to_img(rgb)


# ---------------------------------------------------------------- coins
def coin_patch(col, R, seed, silver=False):
    """One coin face (RGBA), radius R px, lit from the upper left, with rim and relief."""
    rnd = random.Random(seed)
    n = int(R * 2 + 2)
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    dx, dy = (xx - n / 2 + 0.5) / R, (yy - n / 2 + 0.5) / R
    rr = np.sqrt(dx * dx + dy * dy)
    al = np.clip((1.0 - rr) * R, 0, 1)
    c = np.array(col, np.float32)
    # face: a soft gradient, the raised rim brighter on the lit side, darker on the other
    lit = 1.0 + 0.22 * (-dx * 0.6 - dy * 0.8)
    rim = (rr > 0.84) & (rr <= 1.0)
    rimshade = np.where(rim, 1.0 + 0.3 * (-dx * 0.6 - dy * 0.8), 1.0)
    groove = np.exp(-((rr - 0.84) / 0.03) ** 2)
    a = np.zeros((n, n, 4), np.float32)
    for i in range(3):
        a[..., i] = c[i] * lit * rimshade * (1 - 0.18 * groove)
    # relief: a few blobs and arcs (a generic head / building / lettering ring)
    relief = Image.new("L", (n, n), 0)
    rd = ImageDraw.Draw(relief)
    cx = n / 2
    for _ in range(4):
        bx, by = cx + rnd.uniform(-0.3, 0.3) * R, cx + rnd.uniform(-0.35, 0.3) * R
        br = rnd.uniform(0.12, 0.3) * R
        rd.ellipse([bx - br, by - br * 1.2, bx + br, by + br * 1.2], fill=rnd.randint(60, 120))
    for k in range(14):
        ang = math.radians(200 + k * 10)
        rd.point((cx + math.cos(ang) * 0.68 * R, cx + math.sin(ang) * 0.68 * R), fill=160)
    relief = relief.filter(ImageFilter.GaussianBlur(max(0.6, R * 0.05)))
    rl = np.asarray(relief).astype(np.float32) / 255.0
    emb = np.zeros_like(rl)
    emb[1:, 1:] = rl[1:, 1:] - rl[:-1, :-1]
    a[..., :3] *= (1 + emb[..., None] * 2.2)
    # tarnish blotches on copper
    if not silver:
        tn = noise(n, n, max(2, int(R * 0.5)), seed, 2)
        a[..., :3] *= (0.8 + 0.3 * tn)[..., None]
    a[..., :3] += np.exp(-(((dx + 0.35) ** 2 + (dy + 0.4) ** 2) / 0.06))[..., None] * (34 if not silver else 30)
    a[..., 3] = al * 255
    return to_img(a)


def coin_field(W, H, R, count, seed, wrap=True, aspect=(0.55, 1.0), ss=2, ydist=None, base=(40, 24, 14)):
    """Overlapping coins scattered over a W x H image (drawn ss x larger, then reduced)."""
    rnd = random.Random(seed)
    w, h = W * ss, H * ss
    Rs = R * ss
    bg = np.zeros((h, w, 3), np.float32) + np.array(base, np.float32)
    im = to_img(bg).convert("RGBA")
    patches = []
    for k in range(28):
        sil = k % 9 == 4
        col = rnd.choice(SILVER) if sil else rnd.choice(COPPER)
        patches.append((coin_patch(col, Rs * rnd.uniform(0.96, 1.04), seed * 100 + k, sil), sil))
    shadow_cache = {}
    for i in range(count):
        p, sil = rnd.choice(patches)
        asp = rnd.uniform(*aspect)
        if rnd.random() < 0.6:
            asp = max(asp, rnd.uniform(0.8, 1.0))
        rot = rnd.uniform(0, 360)
        q = p.resize((p.size[0], max(2, int(p.size[1] * asp))), Image.BICUBIC).rotate(rot, expand=True, resample=Image.BICUBIC)
        # brightness: deeper coins darker
        depth = i / count
        k = 0.72 + 0.34 * depth + rnd.uniform(-0.08, 0.08)
        qa = np.asarray(q).astype(np.float32)
        qa[..., :3] *= k
        q = to_img(qa)
        sh = q.split()[3].filter(ImageFilter.GaussianBlur(Rs * 0.18))
        x = rnd.uniform(0, w)
        y = ydist(rnd) * h if ydist else rnd.uniform(0, h)
        offs = [(0, 0)]
        if wrap:
            offs = [(ox, oy) for ox in (-w, 0, w) for oy in (-h, 0, h)]
        for ox, oy in offs:
            px = int(x + ox - q.size[0] / 2)
            py = int(y + oy - q.size[1] / 2)
            if px > w or py > h or px + q.size[0] < 0 or py + q.size[1] < 0:
                continue
            im.paste((0, 0, 0, 255), (px + int(Rs * 0.12), py + int(Rs * 0.2)), sh.point(lambda v: int(v * 0.4)))
            im.alpha_composite(q, (max(0, px), max(0, py)), (max(0, -px), max(0, -py)))
    return im.convert("RGB").resize((W, H), Image.LANCZOS)


def paint_coins():
    """The coin heaps: a seamless 512 x 512 tile for 0.35 m (coins ~23 mm across)."""
    W = H = 512
    R = 0.0125 / 0.35 * W
    im = coin_field(W, H, R, 1300, 101)
    a = np.asarray(im).astype(np.float32)
    a *= (0.92 + 0.1 * tile_noise(W, H, 102))[..., None]
    return to_img(a)


def paint_edge():
    """The front faces of the heaps (coins edge-on and tumbled), a 512 x 64 strip, seamless
    left-right, for 0.35 x 0.044 m; v = 0 is the heap's top."""
    W, H = 512, 64
    R = 0.0125 / 0.35 * W
    im = coin_field(W, H, R, 460, 111, wrap=True, aspect=(0.12, 0.45), ydist=lambda r: r.uniform(0.0, 1.0) ** 0.8)
    a = np.asarray(im).astype(np.float32)
    y = np.linspace(0, 1, H)[:, None]
    a *= (1.08 - 0.45 * y)[..., None]
    return to_img(a)


def paint_coin():
    """Single loose coins: 128 x 64, a copper face (left) and a silver face (right); the
    corners outside the faces are the edge colours."""
    im = Image.new("RGB", (128, 64))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 63, 63], fill=(150, 84, 48))
    d.rectangle([64, 0, 127, 63], fill=(150, 152, 158))
    for k, (col, sil) in enumerate([((200, 116, 66), False), ((196, 198, 204), True)]):
        p = coin_patch(col, 31.5, 900 + k, sil)
        im.paste(p, (k * 64 + (64 - p.size[0]) // 2, (64 - p.size[1]) // 2), p)
    return im


def main():
    save(paint_marquee(True), "marquee", colors=256)
    save(paint_marquee(False), "marquee_blank", colors=256)
    save(paint_back(), "back")
    save(paint_front(), "front", colors=0)
    save(paint_side(), "side")
    save(paint_band(), "band")
    save(paint_mech(), "mech")
    save(paint_inner(), "inner")
    save(paint_ramp(), "ramp")
    save(paint_perf(), "perf")
    save(paint_glass(), "glass")
    save(paint_coins(), "coins", colors=256)
    save(paint_edge(), "edge")
    save(paint_coin(), "coin")
    tot = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT) if f.startswith("pusher_") and f.endswith(".png"))
    print("total", tot)


if __name__ == "__main__":
    main()
