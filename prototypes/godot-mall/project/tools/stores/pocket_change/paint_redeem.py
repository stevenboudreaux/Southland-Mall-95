#!/usr/bin/env python3
"""Paints every texture used by tools/stores/pocket_change/redeem.gd into tex/pc/redeem_*.png.

Pocket Change (Southland Mall, Houma LA, 1995): the ticket-redemption area. Showcase
counter prizes, the big-prize wall, the token changer. All art is original: invented
generic product names, no brands. Seeded, so re-running reproduces the same files.

Atlas layouts (pixel rects) are mirrored as UV constants in redeem.gd; keep them in step.
"""
import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(ROOT, "tex", "pc")
FD = "/usr/share/fonts/truetype/"
F_BOLD = FD + "dejavu/DejaVuSans-Bold.ttf"
F_COND = FD + "dejavu/DejaVuSansCondensed-Bold.ttf"
F_REG = FD + "dejavu/DejaVuSans.ttf"
F_POP = FD + "google-fonts/Poppins-Bold.ttf"
F_SERIF = FD + "dejavu/DejaVuSerif-Bold.ttf"
F_MONO = FD + "dejavu/DejaVuSansMono-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def rng_for(name):
    return np.random.default_rng(abs(hash_str(name)) % (2 ** 32))


def hash_str(s):
    h = 1995
    for c in s:
        h = (h * 131 + ord(c)) % 2147483647
    return h


def fnoise(h, w, fx, fy, rng):
    """Tileable band-limited noise in [0, 1]; fx/fy = cutoff frequency (cycles per image)."""
    n = rng.standard_normal((h, w))
    F = np.fft.fft2(n)
    ky = np.fft.fftfreq(h)[:, None] * h
    kx = np.fft.fftfreq(w)[None, :] * w
    F *= np.exp(-((kx / fx) ** 2 + (ky / fy) ** 2))
    r = np.real(np.fft.ifft2(F))
    r -= r.min()
    r /= max(r.max(), 1e-9)
    return r


def fbm(h, w, base, rng, octaves=4, aniso=(1.0, 1.0)):
    acc = np.zeros((h, w))
    amp = 1.0
    tot = 0.0
    f = base
    for _ in range(octaves):
        acc += amp * fnoise(h, w, f * aniso[0], f * aniso[1], rng)
        tot += amp
        amp *= 0.5
        f *= 2.0
    return acc / tot


def to_img(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def save(im, name, quant=None):
    p = os.path.join(OUT, "redeem_%s.png" % name)
    if quant and im.mode == "RGB":
        im = im.quantize(colors=quant, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
    im.save(p, optimize=True)
    return p


def text_c(d, xy, s, f, fill, anchor="mm", stroke=0, sfill=None):
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=sfill)


def fit_font(path, s, maxw, maxh, start=200):
    sz = start
    while sz > 6:
        f = font(path, sz)
        b = f.getbbox(s)
        if b[2] - b[0] <= maxw and b[3] - b[1] <= maxh:
            return f
        sz -= 2
    return font(path, 6)


def grime(im, rng, amount=0.15, scale=6):
    """Multiply an RGB image by a soft dirt mask."""
    a = np.asarray(im).astype(float)
    h, w = a.shape[:2]
    n = fbm(h, w, scale, rng, 4)
    m = 1.0 - amount * np.clip((n - 0.45) * 2.5, 0, 1)
    a[..., :3] *= m[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), im.mode)


def scratches(d, rng, w, h, n, col, lw=1, maxlen=60, box=None):
    x0, y0, x1, y1 = box if box else (0, 0, w, h)
    for _ in range(n):
        x = rng.uniform(x0, x1)
        y = rng.uniform(y0, y1)
        a = rng.uniform(0, math.pi)
        L = rng.uniform(4, maxlen)
        d.line([(x, y), (x + math.cos(a) * L, y + math.sin(a) * L)], fill=col, width=lw)


def shade_ball(d, cx, cy, r, col, hl=True):
    """A shaded sphere drawn top-down: dark rim, bright highlight."""
    col = np.array(col, float)
    steps = max(3, int(r))
    for i in range(steps, 0, -1):
        t = i / steps
        k = 0.45 + 0.55 * (1 - t ** 2) ** 0.5
        c = tuple(int(v) for v in np.clip(col * k, 0, 255))
        rr = r * t
        ox = -r * 0.25 * (1 - t)
        oy = -r * 0.25 * (1 - t)
        d.ellipse([cx - rr + ox, cy - rr + oy, cx + rr + ox, cy + rr + oy], fill=c)
    if hl:
        hr = max(1, r * 0.22)
        d.ellipse([cx - r * 0.45 - hr, cy - r * 0.45 - hr, cx - r * 0.45 + hr, cy - r * 0.45 + hr], fill=(255, 255, 255))


BRIGHT = [(230, 40, 60), (40, 120, 230), (250, 200, 30), (50, 190, 80), (240, 110, 30), (170, 60, 200),
          (30, 200, 210), (250, 90, 170), (255, 255, 255), (120, 230, 40)]


# ------------------------------------------------------------------ wood laminate
def paint_wood():
    W, H = 512, 1024
    rng = rng_for("wood")
    yy, xx = np.mgrid[0:H, 0:W]
    warp = fbm(H, W, 3, rng, 3) * 40
    streak = fnoise(H, W, 40, 2.5, rng)
    rings = np.sin((xx + warp) * 2 * math.pi / 37.0 + streak * 6) * 0.5 + 0.5
    rings = rings ** 3
    fine = fnoise(H, W, 160, 6, rng)
    pores = (rng.random((H, W)) < 0.012) * rng.random((H, W))
    pores = np.asarray(Image.fromarray((pores * 255).astype(np.uint8)).resize((W, H)).filter(ImageFilter.GaussianBlur(0.6))) / 255.0
    pores = np.repeat(pores, 1, 0)
    base = np.array([46, 28, 19], float)
    dark = np.array([26, 16, 11], float)
    lite = np.array([74, 47, 31], float)
    t = 0.55 * streak + 0.25 * fine + 0.2 * rings
    col = dark[None, None] * (1 - t[..., None]) + lite[None, None] * t[..., None]
    col = col * 0.7 + base * 0.3
    col *= (1 - 0.35 * pores[..., None])
    # edge wear: laminate chipped through to tan particleboard near the edges, worst low down
    d = np.minimum(np.minimum(xx, W - 1 - xx), np.minimum(yy, H - 1 - yy)).astype(float)
    wearn = fbm(H, W, 18, rng, 3)
    low = np.clip((yy - H * 0.82) / (H * 0.18), 0, 1)
    corner = np.clip(1 - np.minimum(xx, W - 1 - xx) / 60.0, 0, 1) * np.clip((yy - H * 0.7) / (H * 0.3), 0, 1)
    thr = 2 + 7 * low + 10 * corner
    worn = (d < thr * (0.3 + wearn)) & (wearn > 0.55)
    board = np.array([118, 90, 62], float) * (0.75 + 0.5 * fnoise(H, W, 200, 200, rng))[..., None]
    col = np.where(worn[..., None], board, col)
    # rubbed lighter (lost sheen) along the vertical edges, grime at the kick
    rub = np.exp(-d / 8.0) * 0.12
    col = col * (1 + rub[..., None])
    col *= (1 - 0.35 * low[..., None] * fbm(H, W, 8, rng, 3)[..., None])
    im = to_img(col)
    dr = ImageDraw.Draw(im)
    scratches(dr, rng, W, H, 30, (64, 46, 34), 1, 40)
    scratches(dr, rng, W, H, 18, (84, 64, 48), 1, 20, (0, int(H * 0.75), W, H))
    # shoe scuffs at the bottom
    for _ in range(14):
        x = rng.uniform(0, W)
        y = rng.uniform(H * 0.9, H - 4)
        dr.line([(x, y), (x + rng.uniform(15, 60), y + rng.uniform(-4, 4))], fill=(24, 20, 18), width=int(rng.integers(2, 5)))
    save(im, "wood", 160)


# ------------------------------------------------------------------ token changer face atlas
def paint_tok():
    W, H = 512, 1024
    rng = rng_for("tok")
    im = Image.new("RGB", (W, H), (20, 20, 20))
    d = ImageDraw.Draw(im)
    # HEADER (0,0)-(512,140): backlit translucent panel, two tubes behind it
    hy = np.linspace(0, 1, 140)[:, None]
    glow = 0.82 + 0.18 * (np.exp(-((hy - 0.3) / 0.18) ** 2) + np.exp(-((hy - 0.72) / 0.18) ** 2))
    hx = np.linspace(0, 1, W)[None, :]
    glow = glow * (0.9 + 0.1 * np.sin(hx * math.pi))
    hdr = np.stack([glow * 250, glow * 246, glow * 232], -1)
    im.paste(to_img(hdr), (0, 0))
    d.rectangle([6, 6, W - 7, 133], outline=(170, 24, 30), width=5)
    d.rectangle([14, 14, W - 15, 125], outline=(30, 30, 60), width=2)
    text_c(d, (W // 2, 72), "TOKENS", fit_font(F_BOLD, "TOKENS", 400, 92), (22, 22, 40))
    for sx in (40, W - 40):
        star(d, sx, 70, 18, (200, 30, 36))
    # FACE (0,140)-(512,620): almond powder-coated steel plate
    fy0 = 140
    n = fbm(480, W, 30, rng, 3)
    face = np.stack([182 + 18 * n, 172 + 16 * n, 150 + 14 * n], -1)
    im.paste(to_img(face), (0, fy0))
    d.rectangle([0, fy0, W - 1, fy0 + 479], outline=(110, 104, 92), width=3)
    # instruction card behind a scratched clear window
    cx0, cy0, cx1, cy1 = 40, fy0 + 18, 472, fy0 + 206
    d.rectangle([cx0 - 6, cy0 - 6, cx1 + 6, cy1 + 6], fill=(70, 70, 72))
    d.rectangle([cx0, cy0, cx1, cy1], fill=(244, 240, 226))
    d.rectangle([cx0, cy0, cx1, cy0 + 34], fill=(26, 52, 120))
    text_c(d, ((cx0 + cx1) // 2, cy0 + 18), "TOKEN CHANGER", font(F_BOLD, 24), (250, 250, 250))
    lines = [("INSERT BILL FACE UP", 22), ("$1 BILL  =  4 TOKENS", 24), ("$5 BILL  =  20 TOKENS", 24),
             ("TOKENS HAVE NO CASH VALUE", 15), ("SEE ATTENDANT FOR CHANGE", 15)]
    y = cy0 + 56
    for s, sz in lines:
        text_c(d, ((cx0 + cx1) // 2, y), s, font(F_BOLD if sz > 16 else F_REG, sz), (24, 24, 30))
        y += 30 if sz > 16 else 22
    # sun-fade on the card and dust in the window corners
    # bill acceptor recess (the 3D bezel covers most of it)
    d.rectangle([168, fy0 + 232, 344, fy0 + 404], fill=(30, 30, 30))
    # bill icons sticker, left
    sx0, sy0 = 40, fy0 + 250
    d.rounded_rectangle([sx0, sy0, sx0 + 110, sy0 + 120], 8, fill=(236, 234, 220), outline=(60, 60, 60), width=2)
    text_c(d, (sx0 + 55, sy0 + 16), "BILLS", font(F_BOLD, 16), (30, 30, 30))
    for k, v in enumerate(("$1", "$5")):
        by = sy0 + 34 + k * 42
        d.rectangle([sx0 + 12, by, sx0 + 98, by + 34], fill=(150, 175, 140), outline=(60, 90, 60), width=2)
        d.ellipse([sx0 + 40, by + 5, sx0 + 70, by + 29], outline=(60, 90, 60), width=2)
        text_c(d, (sx0 + 24, by + 17), v, font(F_BOLD, 13), (40, 70, 40))
    # key lock, right
    lx, ly = 420, fy0 + 300
    d.ellipse([lx - 22, ly - 22, lx + 22, ly + 22], fill=(150, 150, 150), outline=(70, 70, 70), width=2)
    d.ellipse([lx - 14, ly - 14, lx + 14, ly + 14], fill=(190, 190, 186))
    d.rectangle([lx - 2, ly - 10, lx + 2, ly + 10], fill=(40, 40, 40))
    # cup opening area
    d.rectangle([150, fy0 + 412, 362, fy0 + 472], fill=(26, 26, 26))
    # serial plate
    px, py = 380, fy0 + 420
    d.rectangle([px, py, px + 110, py + 44], fill=(168, 168, 162), outline=(90, 90, 90))
    for k, s in enumerate(("MODEL TC-500", "SER 004417", "120V 60Hz 1.5A")):
        d.text((px + 6, py + 4 + k * 13), s, font=font(F_MONO, 9), fill=(40, 40, 40))
    for q in ((px + 3, py + 3), (px + 105, py + 3), (px + 3, py + 39), (px + 105, py + 39)):
        d.ellipse([q[0] - 2, q[1] - 2, q[0] + 2, q[1] + 2], fill=(90, 90, 90))
    # screws in the plate corners
    for q in ((14, fy0 + 14), (W - 14, fy0 + 14), (14, fy0 + 466), (W - 14, fy0 + 466)):
        d.ellipse([q[0] - 5, q[1] - 5, q[0] + 5, q[1] + 5], fill=(120, 116, 106), outline=(70, 66, 60))
        d.line([q[0] - 3, q[1], q[0] + 3, q[1]], fill=(60, 56, 50))
    scratches(d, rng, W, H, 120, (206, 198, 180), 1, 30, (0, fy0 + 210, W, fy0 + 480))
    scratches(d, rng, W, H, 40, (120, 112, 98), 1, 18, (140, fy0 + 220, 372, fy0 + 480))
    # BEZEL (0,640)-(180,880): bill acceptor bezel, black plastic, lit arrows
    bx0, by0, bx1, by1 = 0, 640, 180, 880
    d.rectangle([bx0, by0, bx1, by1], fill=(28, 28, 30))
    d.rounded_rectangle([bx0 + 8, by0 + 8, bx1 - 8, by1 - 8], 10, fill=(18, 18, 20), outline=(48, 48, 52), width=2)
    text_c(d, (90, by0 + 30), "INSERT BILL", font(F_BOLD, 15), (200, 200, 200))
    d.rectangle([bx0 + 22, by0 + 108, bx1 - 22, by0 + 132], fill=(4, 4, 4))
    d.line([bx0 + 26, by0 + 120, bx1 - 26, by0 + 120], fill=(0, 0, 0), width=4)
    for k in range(3):
        ay = by0 + 92 - k * 16
        for ax in (40, 140):
            d.polygon([(ax - 10, ay), (ax + 10, ay), (ax, ay - 10)], fill=(60, 255, 90))
    text_c(d, (90, by0 + 168), "FACE UP", font(F_BOLD, 14), (170, 170, 170))
    d.rectangle([60, by0 + 192, 120, by0 + 204], fill=(255, 60, 40))   # red status LED bar
    # SIDE / TOP of head: plain almond (200,640)-(512,880)
    d.rectangle([200, 640, 512, 880], fill=(176, 166, 146))
    # CUP interior (0,890)-(256,1024): brushed steel, worn bright where hands go
    cy = np.linspace(0, 1, 134)[:, None]
    br = 120 + 40 * fnoise(134, 256, 60, 2, rng) + 30 * np.exp(-((cy - 0.6) / 0.25) ** 2)
    im.paste(to_img(np.stack([br, br, br * 0.98], -1)), (0, 890))
    # brushed stainless (256,890)-(512,1024)
    br = 150 + 50 * fnoise(134, 256, 120, 2, rng)
    im.paste(to_img(np.stack([br, br, br * 0.98], -1)), (256, 890))
    im = grime(im, rng, 0.12, 5)
    save(im, "tok", 200)


def star(d, cx, cy, r, col, pts=5, inner=0.45):
    p = []
    for i in range(pts * 2):
        a = -math.pi / 2 + i * math.pi / pts
        rr = r if i % 2 == 0 else r * inner
        p.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    d.polygon(p, fill=col)


# ------------------------------------------------------------------ counter desk atlas
def seg7(d, x, y, h, s, on, off):
    """Draws 7-segment digits; h = digit height."""
    w = h * 0.55
    t = max(2, h * 0.12)
    SEG = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc",
           "7": "abc", "8": "abcdefg", "9": "abcdfg", " ": "", "-": "g"}
    for ch in s:
        segs = SEG.get(ch, "")
        for sname in "abcdefg":
            c = on if sname in segs else off
            if sname == "a": r = [x + t, y, x + w - t, y + t]
            elif sname == "g": r = [x + t, y + h / 2 - t / 2, x + w - t, y + h / 2 + t / 2]
            elif sname == "d": r = [x + t, y + h - t, x + w - t, y + h]
            elif sname == "b": r = [x + w - t, y + t, x + w, y + h / 2 - t / 2]
            elif sname == "c": r = [x + w - t, y + h / 2 + t / 2, x + w, y + h - t]
            elif sname == "f": r = [x, y + t, x + t, y + h / 2 - t / 2]
            else: r = [x, y + h / 2 + t / 2, x + t, y + h - t]
            d.rectangle(r, fill=c)
        x += w + t * 1.6


def paint_desk():
    W, H = 512, 512
    rng = rng_for("desk")
    beige = (196, 188, 168)
    im = Image.new("RGB", (W, H), beige)
    d = ImageDraw.Draw(im)
    # KEYPAD (0,0)-(256,256): register keyboard seen from the clerk's side
    d.rectangle([0, 0, 255, 255], fill=(170, 164, 150))
    d.rectangle([6, 6, 249, 249], fill=(60, 60, 62))
    kf = font(F_BOLD, 9)
    labels = [["7", "8", "9"], ["4", "5", "6"], ["1", "2", "3"], ["0", "00", "."]]
    for r in range(4):
        for c in range(3):
            x = 120 + c * 40
            y = 74 + r * 38
            d.rounded_rectangle([x, y, x + 34, y + 34], 4, fill=(214, 210, 200), outline=(120, 118, 110))
            text_c(d, (x + 17, y + 17), labels[r][c], font(F_BOLD, 14), (30, 30, 30))
    fnk = [("CLR", (230, 200, 60)), ("X", (214, 210, 200)), ("VOID", (210, 80, 60)), ("NS", (214, 210, 200)),
           ("DEPT1", (90, 140, 210)), ("DEPT2", (90, 140, 210)), ("DEPT3", (90, 140, 210)), ("DEPT4", (90, 140, 210))]
    for i, (s, col) in enumerate(fnk):
        x = 14 + (i % 2) * 50
        y = 80 + (i // 2) * 40
        d.rounded_rectangle([x, y, x + 44, y + 34], 4, fill=col, outline=(90, 90, 90))
        text_c(d, (x + 22, y + 17), s, kf, (20, 20, 20))
    d.rounded_rectangle([14, 14, 236, 66], 4, fill=(26, 26, 26))
    d.rectangle([22, 22, 140, 58], fill=(10, 30, 22))
    text_c(d, (81, 40), "  12.00", font(F_MONO, 20), (90, 255, 190))
    d.rounded_rectangle([150, 22, 230, 58], 4, fill=(150, 150, 150))
    text_c(d, (190, 40), "PAPER", font(F_BOLD, 10), (30, 30, 30))
    d.rounded_rectangle([120, 228, 234, 250], 4, fill=(60, 170, 70), outline=(30, 80, 30))
    text_c(d, (177, 239), "TOTAL", font(F_BOLD, 12), (10, 30, 10))
    # REGFRONT (256,0)-(512,128): cash drawer front
    d.rectangle([256, 0, 511, 127], fill=beige)
    d.rectangle([262, 8, 505, 120], outline=(150, 142, 124), width=2)
    d.rectangle([370, 52, 400, 66], fill=(150, 150, 150))
    d.ellipse([440, 50, 458, 68], fill=(170, 170, 170), outline=(90, 90, 90))
    d.line([449, 53, 449, 65], fill=(40, 40, 40), width=2)
    d.text((272, 100), "ELECTRONIC CASH REGISTER", font=font(F_BOLD, 10), fill=(110, 104, 90))
    # VFD (256,128)-(384,160): customer pole display
    d.rectangle([256, 128, 383, 159], fill=(6, 14, 12))
    text_c(d, (320, 144), "  12.00", font(F_MONO, 22), (90, 255, 200))
    # LED (384,128)-(512,160): ticket counter red 7-seg
    d.rectangle([384, 128, 511, 159], fill=(40, 6, 6))
    seg7(d, 392, 133, 22, "0450", (255, 40, 30), (70, 14, 12))
    # COUNTERFRONT (256,160)-(512,288): ticket counting machine front
    d.rectangle([256, 160, 511, 287], fill=(150, 150, 146))
    d.rectangle([262, 166, 505, 281], outline=(100, 100, 96), width=2)
    d.rectangle([300, 176, 468, 222], fill=(20, 20, 20))   # LED window (LED quad sits here)
    text_c(d, (384, 240), "TICKET COUNTER", font(F_BOLD, 15), (36, 36, 40))
    text_c(d, (384, 262), "FEED TICKETS FACE UP", font(F_REG, 10), (50, 50, 54))
    d.ellipse([276, 252, 290, 266], fill=(200, 30, 30))
    d.ellipse([478, 252, 492, 266], fill=(40, 40, 40))
    # TICKET_FACE (0,256)-(128,320): one arcade ticket, top face
    d.rectangle([0, 256, 127, 319], fill=(246, 132, 40))
    d.rectangle([4, 260, 123, 315], outline=(190, 70, 20), width=1)
    text_c(d, (64, 280), "TICKET", font(F_BOLD, 16), (150, 30, 20))
    text_c(d, (64, 302), "NO CASH VALUE", font(F_REG, 8), (150, 40, 20))
    for x in range(2, 128, 6):
        d.point((x, 257), fill=(120, 50, 20)); d.point((x, 318), fill=(120, 50, 20))
    # TICKET_SIDE (128,256)-(256,320): stack edge, folds
    for y in range(256, 320):
        k = 0.82 + 0.18 * ((y % 3) == 0) - 0.2 * ((y % 3) == 1)
        d.line([128, y, 255, y], fill=(int(240 * k), int(128 * k), int(40 * k)))
    # REGSIDE (256,288)-(512,416): plain beige plastic, a little grime
    # PAPER (0,320)-(128,384): receipt roll paper
    d.rectangle([0, 320, 127, 383], fill=(236, 232, 220))
    # DARK (0,384)-(128,448): throat / slot dark
    d.rectangle([0, 384, 127, 447], fill=(14, 14, 14))
    d.rectangle([20, 410, 108, 420], fill=(0, 0, 0))
    im = grime(im, rng, 0.10, 6)
    save(im, "desk")


# ------------------------------------------------------------------ small prize piles (top-down)
def pile_cell(kind, rng):
    S = 256
    im = Image.new("RGB", (S, S), (40, 40, 44))
    d = ImageDraw.Draw(im)
    # tray bottom shading so the pile reads heaped
    yy, xx = np.mgrid[0:S, 0:S]
    if kind == "balls":
        for _ in range(140):
            r = rng.uniform(9, 16)
            x, y = rng.uniform(r, S - r), rng.uniform(r, S - r)
            c = BRIGHT[int(rng.integers(len(BRIGHT)))]
            shade_ball(d, x, y, r, c)
            if rng.random() < 0.5:   # swirl
                d.arc([x - r * 0.7, y - r * 0.7, x + r * 0.7, y + r * 0.7], rng.uniform(0, 360), rng.uniform(0, 360) + 140,
                      fill=BRIGHT[int(rng.integers(len(BRIGHT)))], width=3)
    elif kind == "gum":
        for _ in range(400):
            r = rng.uniform(6, 8)
            x, y = rng.uniform(r, S - r), rng.uniform(r, S - r)
            shade_ball(d, x, y, r, BRIGHT[int(rng.integers(len(BRIGHT)))])
    elif kind == "rings":
        for _ in range(110):
            x, y = rng.uniform(10, S - 10), rng.uniform(10, S - 10)
            r = rng.uniform(9, 12)
            c = [(230, 200, 60), (210, 210, 220), (240, 120, 200), (90, 200, 240)][int(rng.integers(4))]
            d.ellipse([x - r, y - r * 0.8, x + r, y + r * 0.8], outline=c, width=3)
            g = BRIGHT[int(rng.integers(len(BRIGHT)))]
            shade_ball(d, x + rng.uniform(-r, r) * 0.7, y - r * 0.8, 5, g)
    elif kind == "candy":
        for _ in range(130):
            x, y = rng.uniform(14, S - 14), rng.uniform(14, S - 14)
            a = rng.uniform(0, math.pi)
            c = BRIGHT[int(rng.integers(len(BRIGHT)))]
            wrap_candy(d, x, y, a, c, rng)
    elif kind == "taffy":
        for _ in range(110):
            x, y = rng.uniform(10, S - 10), rng.uniform(10, S - 10)
            a = rng.uniform(0, math.pi)
            c = [(250, 120, 140), (120, 200, 250), (250, 220, 90), (150, 230, 120), (240, 240, 230)][int(rng.integers(5))]
            stick(d, x, y, a, 26, 9, c, (255, 255, 255))
    elif kind == "pencils":
        for _ in range(60):
            x, y = rng.uniform(0, S), rng.uniform(0, S)
            a = rng.uniform(-0.4, 0.4) + (math.pi / 2 if rng.random() < 0.15 else 0)
            c = BRIGHT[int(rng.integers(len(BRIGHT)))]
            stick(d, x, y, a, 110, 7, c, (240, 210, 150))
            ex, ey = x + math.cos(a) * 55, y + math.sin(a) * 55
            shade_ball(d, ex, ey, 7, BRIGHT[int(rng.integers(len(BRIGHT)))])
    elif kind == "traps":
        for _ in range(55):
            x, y = rng.uniform(0, S), rng.uniform(0, S)
            a = rng.uniform(0, math.pi)
            c1 = BRIGHT[int(rng.integers(len(BRIGHT)))]
            weave(d, x, y, a, 70, 10, c1)
    elif kind == "slap":
        for _ in range(26):
            x, y = rng.uniform(10, S - 10), rng.uniform(10, S - 10)
            r = rng.uniform(20, 28)
            c = BRIGHT[int(rng.integers(len(BRIGHT)))]
            c2 = BRIGHT[int(rng.integers(len(BRIGHT)))]
            d.ellipse([x - r, y - r, x + r, y + r], outline=(30, 30, 30), width=9)
            d.ellipse([x - r + 1, y - r + 1, x + r - 1, y + r - 1], outline=c, width=7)
            for k in range(10):
                aa = k * math.pi / 5
                d.ellipse([x + math.cos(aa) * (r - 4) - 2, y + math.sin(aa) * (r - 4) - 2,
                           x + math.cos(aa) * (r - 4) + 2, y + math.sin(aa) * (r - 4) + 2], fill=c2)
    elif kind == "sticky":
        for _ in range(40):
            x, y = rng.uniform(10, S - 10), rng.uniform(10, S - 10)
            a = rng.uniform(0, 2 * math.pi)
            c = [(60, 230, 60), (240, 60, 200), (250, 220, 40), (60, 160, 255)][int(rng.integers(4))]
            hand(d, x, y, a, c)
    elif kind == "bugs":
        for _ in range(70):
            x, y = rng.uniform(10, S - 10), rng.uniform(10, S - 10)
            c = [(20, 20, 20), (120, 40, 160), (40, 160, 40), (200, 60, 30)][int(rng.integers(4))]
            r = rng.uniform(5, 8)
            for k in range(8):
                aa = (k + 0.5) * math.pi / 4 + rng.uniform(-0.2, 0.2)
                d.line([x, y, x + math.cos(aa) * r * 2.6, y + math.sin(aa) * r * 2.6], fill=c, width=2)
            shade_ball(d, x, y, r, c)
    elif kind == "erasers":
        for _ in range(90):
            x, y = rng.uniform(10, S - 10), rng.uniform(10, S - 10)
            c = [(250, 160, 190), (160, 220, 250), (250, 240, 140), (180, 250, 170), (250, 200, 130)][int(rng.integers(5))]
            k = int(rng.integers(3))
            r = rng.uniform(9, 13)
            if k == 0:
                star(d, x, y, r, c)
            elif k == 1:
                heart(d, x, y, r, c)
            else:
                d.rounded_rectangle([x - r, y - r * 0.6, x + r, y + r * 0.6], 4, fill=c)
            d.line([x - r * 0.3, y + r * 0.5, x + r * 0.3, y + r * 0.5], fill=tuple(int(v * 0.8) for v in c))
    elif kind == "cars":
        for _ in range(36):
            x, y = rng.uniform(16, S - 16), rng.uniform(16, S - 16)
            a = rng.uniform(0, math.pi)
            mini_car(d, x, y, a, BRIGHT[int(rng.integers(len(BRIGHT)))])
    elif kind == "tattoo":
        for _ in range(14):
            x, y = rng.uniform(20, S - 20), rng.uniform(20, S - 20)
            sheet = Image.new("RGBA", (54, 70), (245, 245, 240, 255))
            sd = ImageDraw.Draw(sheet)
            for k in range(4):
                star(sd, 14 + (k % 2) * 26, 18 + (k // 2) * 30, 10, BRIGHT[int(rng.integers(len(BRIGHT)))])
            sheet = sheet.rotate(rng.uniform(-40, 40), expand=True)
            im.paste(sheet, (int(x - 30), int(y - 35)), sheet)
    elif kind == "whistles":
        for _ in range(55):
            x, y = rng.uniform(10, S - 10), rng.uniform(10, S - 10)
            a = rng.uniform(0, 2 * math.pi)
            c = BRIGHT[int(rng.integers(len(BRIGHT)))]
            stick(d, x, y, a, 22, 10, c, c)
            shade_ball(d, x + math.cos(a) * 10, y + math.sin(a) * 10, 8, c, False)
    elif kind == "snakes":
        for _ in range(26):
            x, y = rng.uniform(0, S), rng.uniform(0, S)
            c = [(240, 80, 30), (60, 200, 60), (230, 220, 40), (150, 60, 200)][int(rng.integers(4))]
            ph = rng.uniform(0, 6)
            a = rng.uniform(0, math.pi)
            pts = []
            for k in range(30):
                t = k * 3.5
                pts.append((x + math.cos(a) * t - math.sin(a) * math.sin(t * 0.08 + ph) * 10,
                            y + math.sin(a) * t + math.cos(a) * math.sin(t * 0.08 + ph) * 10))
            d.line(pts, fill=(20, 20, 20), width=9)
            d.line(pts, fill=c, width=7)
    elif kind == "dinos":
        for _ in range(28):
            x, y = rng.uniform(14, S - 14), rng.uniform(14, S - 14)
            c = [(60, 140, 50), (130, 90, 50), (200, 120, 40), (90, 90, 160)][int(rng.integers(4))]
            d.ellipse([x - 13, y - 7, x + 13, y + 7], fill=c)
            d.ellipse([x + 9, y - 10, x + 20, y - 2], fill=c)
            d.line([x - 12, y, x - 26, y + 6], fill=c, width=4)
            for lx in (-7, 6):
                d.line([x + lx, y + 5, x + lx, y + 12], fill=c, width=3)
    arr = np.asarray(im).astype(float)
    # heap shading: brighter in the middle, shadowed at the tray walls
    r = np.sqrt(((xx - S / 2) / (S / 2)) ** 2 + ((yy - S / 2) / (S / 2)) ** 2)
    arr *= np.clip(1.08 - 0.35 * r ** 3, 0.55, 1.1)[..., None]
    return to_img(arr)


def wrap_candy(d, x, y, a, c, rng):
    ca, sa = math.cos(a), math.sin(a)
    def P(u, v):
        return (x + ca * u - sa * v, y + sa * u + ca * v)
    d.polygon([P(-8, -6), P(8, -6), P(8, 6), P(-8, 6)], fill=c)
    d.polygon([P(-8, -2), P(-15, -7), P(-15, 7), P(-8, 2)], fill=tuple(min(255, v + 40) for v in c))
    d.polygon([P(8, -2), P(15, -7), P(15, 7), P(8, 2)], fill=tuple(min(255, v + 40) for v in c))
    d.line([P(-6, -3), P(6, -3)], fill=(255, 255, 255), width=2)


def stick(d, x, y, a, L, wdt, c, tip):
    ca, sa = math.cos(a), math.sin(a)
    x0, y0 = x - ca * L / 2, y - sa * L / 2
    x1, y1 = x + ca * L / 2, y + sa * L / 2
    d.line([(x0, y0), (x1, y1)], fill=(20, 20, 20), width=wdt + 2)
    d.line([(x0, y0), (x1, y1)], fill=c, width=wdt)
    d.line([(x0 - sa * wdt * 0.25, y0 + ca * wdt * 0.25), (x1 - sa * wdt * 0.25, y1 + ca * wdt * 0.25)],
           fill=tuple(min(255, v + 60) for v in c), width=max(1, wdt // 4))
    d.line([(x1, y1), (x1 + ca * 6, y1 + sa * 6)], fill=tip, width=wdt)


def weave(d, x, y, a, L, wdt, c):
    ca, sa = math.cos(a), math.sin(a)
    n = 10
    for k in range(n):
        t0 = -L / 2 + k * L / n
        t1 = t0 + L / n
        cc = c if k % 2 == 0 else (240, 240, 230)
        d.line([(x + ca * t0, y + sa * t0), (x + ca * t1, y + sa * t1)], fill=cc, width=wdt)


def hand(d, x, y, a, c):
    ca, sa = math.cos(a), math.sin(a)
    d.line([(x, y), (x - ca * 30, y - sa * 30)], fill=c, width=3)
    d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=c)
    for k in range(5):
        aa = a + (k - 2) * 0.4
        d.line([(x, y), (x + math.cos(aa) * 15, y + math.sin(aa) * 15)], fill=c, width=4)
    d.ellipse([x - 3, y - 5, x + 1, y - 1], fill=tuple(min(255, v + 90) for v in c))


def heart(d, x, y, r, c):
    d.ellipse([x - r, y - r * 0.8, x, y + r * 0.1], fill=c)
    d.ellipse([x, y - r * 0.8, x + r, y + r * 0.1], fill=c)
    d.polygon([(x - r * 0.95, y - r * 0.2), (x + r * 0.95, y - r * 0.2), (x, y + r)], fill=c)


def mini_car(d, x, y, a, c):
    ca, sa = math.cos(a), math.sin(a)
    def P(u, v):
        return (x + ca * u - sa * v, y + sa * u + ca * v)
    for u in (-9, 9):
        for v in (-9, 9):
            q = P(u, v)
            d.ellipse([q[0] - 4, q[1] - 4, q[0] + 4, q[1] + 4], fill=(20, 20, 20))
    d.polygon([P(-16, -8), P(16, -8), P(16, 8), P(-16, 8)], fill=c)
    d.polygon([P(-6, -6), P(6, -6), P(6, 6), P(-6, 6)], fill=(60, 80, 110))
    d.line([P(-14, 0), P(14, 0)], fill=(255, 255, 255), width=2)


PILES = ["balls", "rings", "candy", "taffy", "pencils", "traps", "slap", "sticky",
         "bugs", "erasers", "cars", "tattoo", "whistles", "gum", "snakes", "dinos"]


def paint_small():
    im = Image.new("RGB", (1024, 1024))
    for i, k in enumerate(PILES):
        im.paste(pile_cell(k, rng_for("pile" + k)), ((i % 4) * 256, (i // 4) * 256))
    save(im, "small", 256)


# ------------------------------------------------------------------ standing prize cards + price tags
def card_bg(d, w, h, c1, c2, title, f):
    d.rounded_rectangle([2, 2, w - 3, h - 3], 6, fill=c1, outline=(30, 30, 30), width=2)
    d.ellipse([w / 2 - 9, 10, w / 2 + 9, 22], fill=(0, 0, 0, 0))   # hang hole
    d.rectangle([6, 28, w - 7, 62], fill=c2)
    text_c(d, (w / 2, 45), title, fit_font(F_COND, title, w - 20, 26, 26), (255, 255, 255), stroke=2, sfill=(20, 20, 20))


def blister(d, x0, y0, x1, y1):
    d.rounded_rectangle([x0, y0, x1, y1], 10, outline=(255, 255, 255), width=3)
    d.line([x0 + 8, y0 + 6, x0 + 20, y1 - 10], fill=(255, 255, 255), width=2)


def paint_cards():
    W, H = 1024, 1024
    rng = rng_for("cards")
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cw, ch = 170, 256
    items = ["snapbands", "speedcar", "sticky", "traps", "yoyo", "rings",
             "chews", "sour", "lolli", "water", "harmonica", "shades",
             "kazoo", "spiders", "glow", "bubbles", "gumtube", "pencils"]
    for i, k in enumerate(items):
        c = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        d = ImageDraw.Draw(c)
        prize_card(d, k, cw, ch, rng, c)
        im.paste(c, ((i % 6) * cw, (i // 6) * ch))
    d = ImageDraw.Draw(im)
    # price tent cards, 128x64, two rows of 8 at y 768
    vals = ["10", "25", "50", "75", "100", "150", "250", "500",
            "800", "1000", "1500", "2000", "2500", "5000", "3500", "1200"]
    for i, v in enumerate(vals):
        x = (i % 8) * 128
        y = 768 + (i // 8) * 64
        big = i >= 8
        d.rectangle([x + 1, y + 1, x + 126, y + 62], fill=(250, 248, 238, 255), outline=(40, 40, 40, 255), width=2)
        d.rectangle([x + 5, y + 5, x + 122, y + 12], fill=(210, 30, 40, 255) if not big else (30, 70, 190, 255))
        text_c(d, (x + 64, y + 32), v, fit_font(F_BOLD, v, 110, 26, 30), (20, 20, 20, 255))
        text_c(d, (x + 64, y + 52), "TICKETS", font(F_BOLD, 12), (190, 20, 30, 255))
    # price channel strip (0,896)-(1024,928): clear channel over a white strip
    d.rectangle([0, 896, 1023, 927], fill=(232, 232, 228, 255))
    d.line([0, 897, 1023, 897], fill=(255, 255, 255, 255), width=2)
    d.line([0, 926, 1023, 926], fill=(150, 150, 150, 255), width=2)
    # a hang tag (string + tag) (0,928)-(64,1024)
    d.line([32, 928, 32, 960], fill=(250, 250, 250, 255), width=2)
    d.rectangle([4, 958, 60, 1020], fill=(250, 248, 238, 255), outline=(40, 40, 40, 255), width=2)
    text_c(d, (32, 980), "2500", font(F_BOLD, 15), (20, 20, 20, 255))
    text_c(d, (32, 1000), "TICKETS", font(F_BOLD, 9), (190, 20, 30, 255))
    save(im, "cards")


def prize_card(d, k, w, h, rng, img):
    fT = font(F_COND, 20)
    if k in ("chews", "sour", "gumtube", "glow"):
        # candy boxes / tubes: full-colour fronts, no hang hole
        c1, c2, title = {"chews": ((230, 50, 60), (250, 210, 40), "FRUIT CHEWS"),
                         "sour": ((60, 200, 70), (250, 240, 60), "SOUR BITES"),
                         "gumtube": ((50, 120, 230), (250, 90, 170), "GUMBALL TUBE"),
                         "glow": ((30, 30, 40), (120, 250, 60), "GLOW STIX")}[k]
        d.rectangle([4, 14, w - 5, h - 3], fill=c1, outline=(20, 20, 20), width=2)
        d.rectangle([4, 14, w - 5, 30], fill=tuple(int(v * 0.7) for v in c1))
        text_c(d, (w / 2, 70), title, fit_font(F_COND, title, w - 22, 40, 30), c2, stroke=2, sfill=(20, 20, 20))
        if k == "gumtube":
            d.rounded_rectangle([40, 100, w - 40, h - 20], 14, fill=(220, 230, 240), outline=(255, 255, 255), width=2)
            for _ in range(30):
                x, y = rng.uniform(52, w - 52), rng.uniform(112, h - 32)
                shade_ball(d, x, y, 8, BRIGHT[int(rng.integers(len(BRIGHT)))])
        elif k == "glow":
            for j in range(5):
                x = 34 + j * 25
                d.rounded_rectangle([x, 100, x + 12, h - 24], 6, fill=BRIGHT[(j * 3) % len(BRIGHT)])
        else:
            for _ in range(10):
                x, y = rng.uniform(30, w - 30), rng.uniform(110, h - 40)
                wrap_candy(d, x, y, rng.uniform(0, 3), BRIGHT[int(rng.integers(len(BRIGHT)))], rng)
            text_c(d, (w / 2, h - 22), "NET WT 2 OZ", font(F_REG, 10), (255, 255, 255))
        return
    if k == "lolli":
        cx, cy, r = w / 2, 95, 70
        for j in range(40, 0, -1):
            d.pieslice([cx - r * j / 40, cy - r * j / 40, cx + r * j / 40, cy + r * j / 40], j * 40, j * 40 + 200,
                       fill=BRIGHT[j % 5])
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(240, 240, 250), width=3)
        d.rectangle([cx - 4, cy + r, cx + 4, h - 4], fill=(245, 245, 240))
        d.polygon([(cx - 8, cy + r - 4), (cx + 8, cy + r - 4), (cx, cy + r + 18)], fill=(240, 50, 120))
        return
    if k == "bubbles":
        d.rounded_rectangle([50, 70, w - 50, h - 6], 12, fill=(120, 200, 250), outline=(30, 30, 30), width=2)
        d.rectangle([66, 30, w - 66, 72], fill=(240, 60, 150), outline=(30, 30, 30), width=2)
        text_c(d, (w / 2, 150), "BUBBLES", fit_font(F_COND, "BUBBLES", w - 110, 30, 24), (255, 255, 255), stroke=2, sfill=(30, 60, 140))
        for _ in range(6):
            x, y, r = rng.uniform(60, w - 60), rng.uniform(170, h - 20), rng.uniform(5, 12)
            d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 255, 255), width=2)
        return
    cfg = {"snapbands": ((250, 230, 60), (220, 40, 140), "SNAP BANDS"),
           "speedcar": ((40, 90, 210), (230, 40, 40), "SPEED RACER"),
           "sticky": ((250, 120, 30), (40, 170, 60), "STICKY HAND"),
           "traps": ((150, 60, 200), (250, 200, 30), "FINGER TRAP"),
           "yoyo": ((230, 40, 50), (30, 30, 30), "SUPER YO-YO"),
           "rings": ((250, 150, 200), (150, 60, 200), "FASHION RINGS"),
           "water": ((40, 170, 220), (250, 240, 60), "WATER RING GAME"),
           "harmonica": ((30, 30, 120), (230, 180, 40), "HARMONICA"),
           "shades": ((20, 20, 20), (250, 60, 170), "COOL SHADES"),
           "kazoo": ((250, 210, 40), (220, 40, 40), "KAZOO"),
           "spiders": ((90, 200, 60), (20, 20, 20), "CREEPY SPIDERS"),
           "pencils": ((60, 190, 220), (240, 70, 40), "FUN PENCILS")}
    c1, c2, title = cfg[k]
    card_bg(d, w, h, c1, c2, title, fT)
    d.ellipse([w / 2 - 9, 9, w / 2 + 9, 21], fill=(0, 0, 0, 0))
    by0, by1 = 72, h - 14
    if k == "snapbands":
        for j in range(2):
            x0 = 24 + j * 64
            d.rounded_rectangle([x0, by0 + 10, x0 + 52, by1 - 6], 10, fill=BRIGHT[j * 5 % 10])
            for yy in range(by0 + 18, by1 - 10, 14):
                star(d, x0 + 26, yy, 6, (255, 255, 255))
    elif k == "speedcar":
        d.polygon([(26, 170), (144, 170), (150, 140), (110, 128), (70, 126), (40, 140)], fill=(230, 40, 40))
        d.polygon([(70, 128), (106, 128), (118, 142), (62, 142)], fill=(60, 80, 120))
        for x in (50, 122):
            d.ellipse([x - 13, 158, x + 13, 184], fill=(20, 20, 20))
            d.ellipse([x - 5, 166, x + 5, 176], fill=(190, 190, 190))
        text_c(d, (w / 2, 212), "DIE-CAST", font(F_BOLD, 14), (255, 255, 255))
    elif k == "sticky":
        hand(d, 85, 150, -math.pi / 2, (80, 240, 70))
        d.line([85, 150, 85, 230], fill=(80, 240, 70), width=4)
    elif k == "traps":
        for j in range(3):
            weave(d, 85 + (j - 1) * 30, 160, math.pi / 2, 140, 16, BRIGHT[j * 3])
    elif k == "yoyo":
        d.ellipse([35, 95, 135, 195], fill=(230, 40, 50), outline=(20, 20, 20), width=3)
        d.ellipse([70, 130, 100, 160], fill=(250, 250, 250))
        d.line([85, 145, 85, 240], fill=(255, 255, 255), width=2)
    elif k == "rings":
        for j in range(6):
            x = 45 + (j % 3) * 40
            y = 110 + (j // 3) * 60
            d.ellipse([x - 13, y - 9, x + 13, y + 9], outline=(240, 210, 60), width=4)
            shade_ball(d, x, y - 12, 7, BRIGHT[j])
    elif k == "water":
        d.rounded_rectangle([22, by0 + 4, w - 22, by1 - 4], 10, fill=(70, 160, 240), outline=(20, 20, 20), width=3)
        for j in range(6):
            x, y = rng.uniform(40, w - 40), rng.uniform(110, 210)
            d.ellipse([x - 9, y - 9, x + 9, y + 9], outline=BRIGHT[j], width=4)
        for x in (60, 110):
            d.line([x, 120, x, 160], fill=(250, 250, 250), width=4)
        d.ellipse([40, 214, 60, 234], fill=(240, 40, 40)); d.ellipse([110, 214, 130, 234], fill=(240, 40, 40))
    elif k == "harmonica":
        d.rectangle([22, 135, 148, 175], fill=(200, 200, 205), outline=(60, 60, 60), width=2)
        for x in range(30, 145, 12):
            d.rectangle([x, 150, x + 6, 160], fill=(30, 30, 30))
    elif k == "shades":
        for x in (52, 118):
            d.ellipse([x - 28, 130, x + 28, 172], fill=(20, 20, 20), outline=(250, 60, 170), width=5)
        d.line([80, 145, 90, 145], fill=(250, 60, 170), width=5)
    elif k == "kazoo":
        d.polygon([(30, 160), (140, 140), (140, 180)], fill=(220, 40, 40))
        d.ellipse([84, 146, 104, 166], fill=(250, 210, 40))
    elif k == "spiders":
        for j in range(3):
            x, y = 50 + j * 35, 130 + (j % 2) * 50
            for a in range(8):
                aa = (a + 0.5) * math.pi / 4
                d.line([x, y, x + math.cos(aa) * 26, y + math.sin(aa) * 26], fill=(20, 20, 20), width=3)
            d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=(20, 20, 20))
    elif k == "pencils":
        for j in range(4):
            x = 40 + j * 30
            d.rectangle([x - 6, 90, x + 6, 236], fill=BRIGHT[j * 2])
            shade_ball(d, x, 92, 10, BRIGHT[(j * 2 + 5) % 10])
    if k not in ("water",):
        blister(d, 14, by0, w - 14, by1)


# ------------------------------------------------------------------ big-prize toys atlas
def paint_toys():
    W, H = 512, 512
    rng = rng_for("toys")
    im = Image.new("RGB", (W, H), (30, 30, 32))
    d = ImageDraw.Draw(im)
    # BOOM1 (0,0)-(256,128), BOOM2 (256,0)-(512,128): portable stereo fronts
    for bi, (bx, body, acc) in enumerate(((0, (34, 34, 38), (200, 200, 205)), (256, (170, 172, 176), (40, 40, 44)))):
        d.rectangle([bx, 0, bx + 255, 127], fill=body)
        d.rectangle([bx + 2, 2, bx + 253, 125], outline=acc, width=2)
        for sx in (bx + 48, bx + 208):
            d.ellipse([sx - 40, 24, sx + 40, 104], fill=(20, 20, 22), outline=acc, width=3)
            for r in range(36, 4, -6):
                d.ellipse([sx - r, 64 - r, sx + r, 64 + r], outline=(46, 46, 50) if r % 12 else (28, 28, 30))
            d.ellipse([sx - 10, 54, sx + 10, 74], fill=(70, 70, 76))
        d.rectangle([bx + 96, 30, bx + 160, 74], fill=(14, 14, 16), outline=acc, width=2)    # cassette door
        d.rectangle([bx + 104, 40, bx + 152, 64], fill=(60, 50, 40))
        d.ellipse([bx + 110, 46, bx + 122, 58], fill=(230, 230, 230)); d.ellipse([bx + 134, 46, bx + 146, 58], fill=(230, 230, 230))
        d.rectangle([bx + 96, 8, bx + 160, 22], fill=(200, 180, 120) if bi == 0 else (230, 220, 180))   # tuning dial
        for x in range(bx + 100, bx + 158, 6):
            d.line([x, 10, x, 20], fill=(60, 60, 60))
        d.line([bx + 128, 8, bx + 128, 22], fill=(220, 30, 30), width=2)
        for k in range(6):
            d.rectangle([bx + 98 + k * 10, 80, bx + 105 + k * 10, 90], fill=acc)
        text_c(d, (bx + 128, 104), "STEREO", font(F_BOLD, 11), acc)
        text_c(d, (bx + 128, 116), "AM/FM CASSETTE", font(F_REG, 7), acc)
    # PLASTIC (0,128)-(128,256) dark plastic side, (128,128)-(256,256) silver plastic side
    d.rectangle([0, 128, 127, 255], fill=(36, 36, 40))
    d.rectangle([128, 128, 255, 255], fill=(165, 167, 172))
    # BOXES row (0,256)-(512,384): four 128x128 boxed prize fronts
    boxes = [("R/C RACER", (230, 40, 40), (250, 220, 40)), ("WALKIE TALKIES", (30, 60, 160), (250, 250, 250)),
             ("35mm CAMERA", (30, 30, 30), (250, 200, 30)), ("STEREO HEADPHONES", (120, 40, 170), (90, 240, 230))]
    for i, (t, c1, c2) in enumerate(boxes):
        x0, y0 = i * 128, 256
        d.rectangle([x0, y0, x0 + 127, y0 + 127], fill=c1)
        d.rectangle([x0 + 4, y0 + 4, x0 + 123, y0 + 30], fill=tuple(int(v * 0.6) for v in c1))
        text_c(d, (x0 + 64, y0 + 17), t, fit_font(F_COND, t, 116, 20, 18), c2)
        if i == 0:
            d.polygon([(x0 + 16, y0 + 96), (x0 + 112, y0 + 96), (x0 + 104, y0 + 70), (x0 + 30, y0 + 66)], fill=(250, 250, 250))
            for wx in (x0 + 34, x0 + 96):
                d.ellipse([wx - 12, y0 + 86, wx + 12, y0 + 110], fill=(15, 15, 15))
            d.line([x0 + 100, y0 + 66, x0 + 110, y0 + 40], fill=(20, 20, 20), width=2)
        elif i == 1:
            for wx in (x0 + 40, x0 + 86):
                d.rounded_rectangle([wx - 14, y0 + 50, wx + 14, y0 + 112], 5, fill=(20, 20, 20))
                d.line([wx + 8, y0 + 50, wx + 8, y0 + 36], fill=(20, 20, 20), width=3)
                d.rectangle([wx - 9, y0 + 60, wx + 9, y0 + 80], fill=(80, 80, 80))
        elif i == 2:
            d.rounded_rectangle([x0 + 20, y0 + 54, x0 + 108, y0 + 106], 6, fill=(60, 60, 64))
            d.ellipse([x0 + 46, y0 + 60, x0 + 82, y0 + 96], fill=(20, 20, 22), outline=(160, 160, 160), width=3)
            d.rectangle([x0 + 86, y0 + 58, x0 + 102, y0 + 68], fill=(200, 220, 230))
        else:
            d.arc([x0 + 26, y0 + 40, x0 + 102, y0 + 116], 180, 360, fill=(30, 30, 30), width=7)
            for wx in (x0 + 28, x0 + 100):
                d.ellipse([wx - 12, y0 + 70, wx + 12, y0 + 104], fill=(30, 30, 30))
        d.rectangle([x0 + 4, y0 + 112, x0 + 123, y0 + 123], fill=(250, 250, 250))
        text_c(d, (x0 + 64, y0 + 118), "AGES 8 AND UP", font(F_REG, 8), (30, 30, 30))
    # BOXSIDE (0,384)-(128,512): cardboard printed side
    d.rectangle([0, 384, 127, 511], fill=(220, 214, 196))
    d.rectangle([0, 384, 127, 404], fill=(200, 40, 40))
    # CHROME (128,384)-(256,512)
    br = 150 + 70 * fnoise(128, 128, 40, 4, rng)
    im.paste(to_img(np.stack([br, br, br], -1)), (128, 384))
    im = grime(im, rng, 0.08, 6)
    save(im, "toys")


# ------------------------------------------------------------------ PRIZES header
def paint_header():
    W, H = 1024, 256
    rng = rng_for("header")
    yy, xx = np.mgrid[0:H, 0:W] / np.array([H, W])[:, None, None]
    g = np.stack([30 + 40 * (1 - yy), 10 + 20 * (1 - yy), 90 + 80 * (1 - yy)], -1)
    # backlight hot spots from the tubes
    g *= (0.9 + 0.2 * np.exp(-((yy - 0.5) / 0.4) ** 2))[..., None]
    im = to_img(g)
    d = ImageDraw.Draw(im)
    # confetti / stars
    for _ in range(60):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        star(d, x, y, rng.uniform(3, 8), (250, 240, 200) if rng.random() < 0.6 else BRIGHT[int(rng.integers(10))])
    # neon-ish band lines
    d.line([0, 18, W, 18], fill=(250, 60, 180), width=6)
    d.line([0, H - 18, W, H - 18], fill=(60, 220, 250), width=6)
    # PRIZES lettering: yellow-to-orange fill, dark outline, drop shadow
    f = fit_font(F_POP, "PRIZES", 600, 170, 200)
    txt = Image.new("L", (W, H), 0)
    ImageDraw.Draw(txt).text((W // 2, H // 2 + 6), "PRIZES", font=f, fill=255, anchor="mm")
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).text((W // 2 + 8, H // 2 + 14), "PRIZES", font=f, fill=255, anchor="mm", stroke_width=8)
    outl = Image.new("L", (W, H), 0)
    ImageDraw.Draw(outl).text((W // 2, H // 2 + 6), "PRIZES", font=f, fill=255, anchor="mm", stroke_width=8)
    im.paste((10, 6, 30), (0, 0), sh)
    im.paste((250, 250, 250), (0, 0), outl)
    grad = np.zeros((H, W, 3))
    t = np.clip((yy - 0.2) / 0.6, 0, 1)
    grad[..., 0] = 255
    grad[..., 1] = 236 - 120 * t
    grad[..., 2] = 60 - 40 * t
    inner = Image.new("L", (W, H), 0)
    ImageDraw.Draw(inner).text((W // 2, H // 2 + 6), "PRIZES", font=f, fill=255, anchor="mm", stroke_width=3)
    im.paste((200, 30, 60), (0, 0), inner)
    im.paste(to_img(grad), (0, 0), txt)
    # ticket icons and the sub-line either side
    for cx in (110, W - 110):
        for k in range(3):
            tx = cx - 30 + k * 12
            ty = 96 + k * 14
            d.rectangle([tx, ty, tx + 64, ty + 30], fill=(250, 140, 40), outline=(120, 40, 10), width=2)
            d.text((tx + 8, ty + 8), "TICKET", font=font(F_BOLD, 11), fill=(140, 30, 10))
    text_c(d, (110, 196), "REDEEM", font(F_BOLD, 22), (250, 250, 250))
    text_c(d, (W - 110, 196), "TICKETS", font(F_BOLD, 22), (250, 250, 250))
    im = grime(im, rng, 0.06, 6)
    save(im, "header")


def paint_band():
    """Horizontally tileable header band either side of the PRIZES panel (1.12 m x 0.28 m per tile)."""
    W, H = 512, 128
    rng = rng_for("band")
    yy = np.linspace(0, 1, H)[:, None] * np.ones((1, W))
    g = np.stack([30 + 40 * (1 - yy), 10 + 20 * (1 - yy), 90 + 80 * (1 - yy)], -1)
    g *= (0.9 + 0.2 * np.exp(-((yy - 0.5) / 0.4) ** 2))[..., None]
    im = to_img(g)
    d = ImageDraw.Draw(im)
    d.line([0, 9, W, 9], fill=(250, 60, 180), width=3)
    d.line([0, H - 9, W, H - 9], fill=(60, 220, 250), width=3)
    for k in range(2):
        cx = 128 + k * 256
        for j in range(3):
            tx, ty = cx - 52 + j * 30, 40 + (j % 2) * 18
            d.rectangle([tx, ty, tx + 40, ty + 20], fill=(250, 140, 40), outline=(120, 40, 10), width=2)
            d.text((tx + 4, ty + 5), "TICKET", font=font(F_BOLD, 7), fill=(140, 30, 10))
        star(d, cx + 70, 64, 14, (255, 220, 60))
        star(d, cx - 80, 64, 10, (250, 250, 250))
    for _ in range(14):
        x, y = rng.uniform(8, W - 8), rng.uniform(18, H - 18)
        star(d, x, y, rng.uniform(2, 4), (250, 240, 200))
    save(im, "band")


# ------------------------------------------------------------------ tiles
def paint_slat():
    S = 256
    rng = rng_for("slat")
    n = fbm(S, S, 16, rng, 3)
    base = 52 + 8 * n
    arr = np.stack([base, base, base * 1.04], -1)
    yy = np.arange(S)
    period = S / 13.0
    for g in range(13):
        y0 = g * period
        for dy in range(int(period)):
            y = int(y0 + dy) % S
            t = dy / period
            if t < 0.13:                       # the groove, an aluminium insert lip
                arr[y] = arr[y] * 0.25 + (np.array([120, 120, 124]) if t < 0.04 else np.array([10, 10, 10]))
            elif t > 0.92:                      # top bevel of the next slat, catches light
                arr[y] *= 1.25
    im = to_img(arr)
    d = ImageDraw.Draw(im)
    scratches(d, rng, S, S, 20, (80, 80, 84), 1, 20)
    save(im, "slat")


def paint_fur():
    S = 256
    rng = rng_for("fur")
    a = fnoise(S, S, 90, 90, rng) * 0.5 + fnoise(S, S, 20, 60, rng) * 0.3 + fnoise(S, S, 6, 6, rng) * 0.2
    a = 140 + 115 * a ** 1.3
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "L").convert("RGB")
    save(im, "fur")


def paint_glass():
    S = 512
    rng = rng_for("glass")
    a = np.full((S, S), 10.0)
    smear = fbm(S, S, 6, rng, 4)
    a += 18 * np.clip((smear - 0.5) * 3, 0, 1)
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "L")
    d = ImageDraw.Draw(im)
    # fingerprints and palm smudges (whorls), mostly in the lower half where hands rest
    for _ in range(26):
        x, y = rng.uniform(0, S), rng.uniform(S * 0.3, S)
        r = rng.uniform(7, 13)
        for k in range(int(r / 2)):
            rr = r - k * 2
            d.ellipse([x - rr * 0.75, y - rr, x + rr * 0.75, y + rr], outline=int(30 + rng.uniform(0, 14)))
    for _ in range(4):
        x, y = rng.uniform(0, S), rng.uniform(S * 0.5, S)
        sm = Image.new("L", (S, S), 0)
        ImageDraw.Draw(sm).ellipse([x - 40, y - 22, x + 40, y + 22], fill=10)
        sm = sm.filter(ImageFilter.GaussianBlur(10))
        im = Image.fromarray(np.clip(np.asarray(im).astype(int) + np.asarray(sm), 0, 255).astype(np.uint8), "L")
        d = ImageDraw.Draw(im)
    for _ in range(10):   # wipe streaks
        y = rng.uniform(0, S)
        d.line([(0, y), (S, y + rng.uniform(-30, 30))], fill=20, width=int(rng.integers(3, 8)))
    im = im.filter(ImageFilter.GaussianBlur(1.6))
    alpha = np.asarray(im).astype(float)
    rgb = np.full((S, S, 3), 235.0)
    out = np.dstack([rgb, alpha])
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA").save(os.path.join(OUT, "redeem_glass.png"), optimize=True)


def paint_scuff():
    S = 256
    rng = rng_for("scuff")
    a = 200 + 30 * fbm(S, S, 8, rng, 4)
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "L")
    d = ImageDraw.Draw(im)
    scratches(d, rng, S, S, 60, 255, 1, 30)
    scratches(d, rng, S, S, 20, 150, 2, 20)
    im.convert("RGB").save(os.path.join(OUT, "redeem_scuff.png"), optimize=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    paint_wood()
    paint_tok()
    paint_desk()
    paint_small()
    paint_cards()
    paint_toys()
    paint_header()
    paint_band()
    paint_slat()
    paint_fur()
    paint_glass()
    paint_scuff()
    tot = 0
    for f in sorted(os.listdir(OUT)):
        if f.startswith("redeem_"):
            s = os.path.getsize(os.path.join(OUT, f))
            tot += s
            print("%-24s %7d" % (f, s))
    print("total", tot)


if __name__ == "__main__":
    main()
