"""Paints the crane (claw machine) textures for Pocket Change into tex/pc/crane_*.png.

Module: tools/stores/pocket_change/crane.gd. Three cabinet styles (0, 1, 2), each with
its own header marquee and cabinet atlas; the control panel, glass, plush fabric and
plush faces are shared. All artwork is original: invented titles (PRIZE CATCHER,
LUCKY GRAB, SKILL CRANE), generic stars, bears and claws.
Run from the project folder: python3 tools/stores/pocket_change/paint_crane.py
Deterministic: every random source is seeded.

Atlas layouts (pixels) must match crane.gd:
  crane_header_<s>.png 1024x640: front marquee (0,0)-(1024,400), side marquee (0,416)-(512,640)
  crane_cab_<s>.png    1024x512: cabinet front (0,0)-(440,435), cabinet side (448,0)-(916,479)
  crane_panel.png       512x256: panel top (0,0)-(512,110), fascia (0,112)-(512,164),
                                 prize flap (0,168)-(80,256), token lamp (96,168)-(144,232)
"""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(PROJ, "tex", "pc")
os.makedirs(OUT, exist_ok=True)

F_BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
F_BLACKI = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"
F_ADV = "/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyreadventor-bold.otf"
F_ADVI = "/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyreadventor-bolditalic.otf"
F_CN = "/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyreheroscn-bold.otf"
F_HB = "/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyreheros-bold.otf"
F_POPI = "/usr/share/fonts/truetype/google-fonts/Poppins-BoldItalic.ttf"


def save(im, name, colors=0):
    p = os.path.join(OUT, name)
    if colors:
        im = im.convert("RGB").quantize(colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
    im.save(p, optimize=True)
    print(name, im.size, os.path.getsize(p))


def font(path, size):
    return ImageFont.truetype(path, size)


def rng(seed):
    return np.random.default_rng(seed)


def periodic_noise(h, w, sx, sy, seed):
    """Gaussian noise blurred by an elongated kernel in the frequency domain: tiles seamlessly."""
    r = rng(seed)
    n = r.normal(size=(h, w))
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    k = np.exp(-2 * (math.pi ** 2) * ((fx * sx) ** 2 + (fy * sy) ** 2))
    o = np.real(np.fft.ifft2(np.fft.fft2(n) * k))
    o -= o.mean()
    return o / (o.std() + 1e-9)


def noise(h, w, s, seed):
    return periodic_noise(h, w, s, s, seed)


def to_img(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def text_mask(text, fpath, size, skew=0.0, track=0):
    """White-on-black L mask of text, cropped, optional italic skew and letter tracking."""
    f = font(fpath, size)
    if track:
        widths = [f.getbbox(ch)[2] - f.getbbox(ch)[0] if ch != " " else size * 0.3 for ch in text]
        tw = int(sum(widths) + track * (len(text) - 1) + size)
    else:
        bb = f.getbbox(text)
        tw = bb[2] + size
    im = Image.new("L", (int(tw + size * abs(skew) + size), int(size * 2.0)), 0)
    d = ImageDraw.Draw(im)
    if track:
        x = size * 0.5
        for ch, wd in zip(text, widths):
            d.text((x, size * 0.15), ch, font=f, fill=255)
            x += (f.getlength(ch)) + track
    else:
        d.text((size * 0.5, size * 0.15), text, font=f, fill=255)
    if skew:
        w, h = im.size
        im = im.transform((w, h), Image.AFFINE, (1, skew, -skew * h * 0.5, 0, 1, 0), resample=Image.BICUBIC)
    bb = im.getbbox()
    return im.crop(bb) if bb else im


def grow(mask, r):
    """Round dilation of an L mask by about r pixels (soft edge)."""
    if r <= 0:
        return mask
    pad = int(r * 2 + 4)
    m = Image.new("L", (mask.size[0] + pad * 2, mask.size[1] + pad * 2), 0)
    m.paste(mask, (pad, pad))
    b = m.filter(ImageFilter.GaussianBlur(r * 0.5))
    a = np.asarray(b).astype(np.float32)
    a = np.clip((a - 6) * 10, 0, 255)
    return to_img(a), pad


def fancy_text(base, text, fpath, size, centre, fill_top, fill_bot, outlines=(), shadow=None, skew=0.0,
               max_w=None, track=0, shine=True):
    """Draw display lettering: gradient fill, stacked outlines (outermost first), drop shadow."""
    m = text_mask(text, fpath, size, skew, track)
    if max_w and m.size[0] > max_w:
        k = max_w / m.size[0]
        m = m.resize((int(m.size[0] * k), int(m.size[1] * k)), Image.LANCZOS)
    cx, cy = centre
    layers = []
    total = sum(w for w, _ in outlines)
    acc = total
    for w, col in outlines:
        g, pad = grow(m, acc)
        layers.append((g, pad, col))
        acc -= w
    x0 = int(cx - m.size[0] / 2)
    y0 = int(cy - m.size[1] / 2)
    if shadow:
        (dx, dy), col = shadow
        g, pad = grow(m, total)
        g = g.filter(ImageFilter.GaussianBlur(2))
        base.paste(Image.new("RGB", g.size, col), (x0 - pad + dx, y0 - pad + dy), g)
    for g, pad, col in layers:
        base.paste(Image.new("RGB", g.size, col), (x0 - pad, y0 - pad), g)
    # gradient fill
    w, h = m.size
    grad = np.zeros((h, w, 3), np.float32)
    t = np.linspace(0, 1, h)[:, None]
    for i in range(3):
        grad[:, :, i] = fill_top[i] * (1 - t) + fill_bot[i] * t
    if shine:
        # a light band across the upper third, as screen-printed chrome letters have
        band = np.exp(-((t - 0.3) / 0.08) ** 2) * 60
        grad += band[:, :, None]
    base.paste(to_img(grad), (x0, y0), m)
    return (x0, y0, x0 + w, y0 + h)


def star(d, cx, cy, r, col, pts=5, inner=0.45, rot=-90, outline=None, width=1):
    p = []
    for i in range(pts * 2):
        a = math.radians(rot + i * 180 / pts)
        rr = r if i % 2 == 0 else r * inner
        p.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(p, fill=col, outline=outline, width=width)


def sparkle(d, cx, cy, r, col):
    star(d, cx, cy, r, col, pts=4, inner=0.18, rot=-90)


def backlit(im, tubes=(0.28, 0.72), seed=0):
    """Make flat art read as a fluorescent-backlit translucent panel: tube hot bands,
    darker ends, a faint diffuser grain and a little yellowing of the whites."""
    a = np.asarray(im).astype(np.float32)
    h, w, _ = a.shape
    y = np.linspace(0, 1, h)[:, None]
    x = np.linspace(0, 1, w)[None, :]
    f = 0.80
    for t in tubes:
        f = f + 0.16 * np.exp(-((y - t) / 0.16) ** 2)
    ends = 1.0 - 0.22 * (np.abs(x - 0.5) * 2) ** 3
    f = f * ends
    g = noise(h, w, 1.2, seed) * 3.0
    a = a * f[:, :, None] + g[:, :, None]
    a[:, :, 2] *= 0.96
    return to_img(a)


def bear_face(d, cx, cy, s, col, muz, eye=(20, 14, 12), outline=(40, 20, 10)):
    """A generic cartoon teddy-bear head (circles), for marquee art."""
    for ex in (-0.78, 0.78):
        d.ellipse([cx + ex * s - 0.32 * s, cy - 0.98 * s, cx + ex * s + 0.32 * s, cy - 0.34 * s], fill=col, outline=outline, width=max(2, int(s * 0.06)))
        d.ellipse([cx + ex * s - 0.17 * s, cy - 0.82 * s, cx + ex * s + 0.17 * s, cy - 0.5 * s], fill=muz)
    d.ellipse([cx - s, cy - 0.85 * s, cx + s, cy + 0.85 * s], fill=col, outline=outline, width=max(2, int(s * 0.06)))
    d.ellipse([cx - 0.45 * s, cy + 0.0 * s, cx + 0.45 * s, cy + 0.62 * s], fill=muz)
    for ex in (-0.38, 0.38):
        d.ellipse([cx + ex * s - 0.11 * s, cy - 0.32 * s, cx + ex * s + 0.11 * s, cy - 0.08 * s], fill=eye)
        d.ellipse([cx + ex * s - 0.03 * s, cy - 0.27 * s, cx + ex * s + 0.03 * s, cy - 0.2 * s], fill=(255, 255, 255))
    d.ellipse([cx - 0.16 * s, cy + 0.08 * s, cx + 0.16 * s, cy + 0.28 * s], fill=eye)
    d.arc([cx - 0.2 * s, cy + 0.12 * s, cx, cy + 0.46 * s], 20, 160, fill=eye, width=max(2, int(s * 0.05)))
    d.arc([cx, cy + 0.12 * s, cx + 0.2 * s, cy + 0.46 * s], 20, 160, fill=eye, width=max(2, int(s * 0.05)))


def claw_icon(d, cx, cy, s, metal=(200, 206, 214), dark=(40, 44, 60)):
    """A generic three-prong claw graphic hanging from a cable."""
    w = max(3, int(s * 0.07))
    d.line([cx, cy - 1.6 * s, cx, cy - 0.5 * s], fill=dark, width=max(2, w // 2))
    d.rounded_rectangle([cx - 0.28 * s, cy - 0.55 * s, cx + 0.28 * s, cy - 0.05 * s], radius=int(s * 0.08), fill=metal, outline=dark, width=w // 2 + 1)
    for side in (-1, 1):
        pts = [(cx + side * 0.15 * s, cy - 0.05 * s), (cx + side * 0.75 * s, cy + 0.35 * s), (cx + side * 0.62 * s, cy + 1.0 * s), (cx + side * 0.35 * s, cy + 1.2 * s)]
        d.line(pts, fill=dark, width=w + 6, joint="curve")
        d.line(pts, fill=metal, width=w, joint="curve")
    pts = [(cx, cy - 0.05 * s), (cx, cy + 0.5 * s), (cx + 0.05 * s, cy + 1.05 * s)]
    d.line(pts, fill=dark, width=w + 6, joint="curve")
    d.line(pts, fill=metal, width=w, joint="curve")


# ------------------------------------------------------------------ header marquees
def header(style):
    W, H = 1024, 640
    im = Image.new("RGB", (W, H), (0, 0, 0))
    FH = 400
    front = Image.new("RGB", (W, FH))
    d = ImageDraw.Draw(front)
    rr = random.Random(100 + style)
    if style == 0:
        # PRIZE CATCHER: red sunburst, yellow chrome letters, two teddy bears
        a = np.zeros((FH, W, 3), np.float32)
        yy, xx = np.mgrid[0:FH, 0:W]
        ang = np.arctan2(yy - 430, xx - 512)
        ray = (np.floor((ang + math.pi) / (math.pi / 16)) % 2)
        rad = np.hypot(xx - 512, yy - 430) / 600
        c1 = np.array([214, 34, 26]); c2 = np.array([238, 72, 24])
        a = c1[None, None, :] * (1 - ray[:, :, None]) + c2[None, None, :] * ray[:, :, None]
        a = a * (1.15 - 0.45 * rad[:, :, None])
        front = to_img(a)
        d = ImageDraw.Draw(front)
        d.rectangle([0, 318, W, FH], fill=(16, 10, 14))
        d.rectangle([0, 318, W, 326], fill=(255, 196, 30))
        for i in range(26):
            x = rr.uniform(20, W - 20); y = rr.uniform(18, 300)
            if 230 < x < 800 and y > 60:
                continue
            star(d, x, y, rr.uniform(7, 16), (255, 226, 60))
        bear_face(d, 128, 150, 78, (196, 132, 70), (238, 210, 160))
        bear_face(d, 896, 150, 78, (236, 228, 214), (250, 200, 210))
        fancy_text(front, "PRIZE", F_BLACKI, 170, (512, 112), (255, 246, 120), (255, 170, 0),
                   outlines=[(10, (20, 6, 6)), (6, (255, 255, 255)), (8, (150, 10, 10))], shadow=((8, 9), (40, 0, 0)), max_w=560)
        fancy_text(front, "CATCHER", F_BLACKI, 130, (512, 250), (255, 246, 120), (255, 170, 0),
                   outlines=[(9, (20, 6, 6)), (5, (255, 255, 255)), (7, (150, 10, 10))], shadow=((7, 8), (40, 0, 0)), max_w=650)
        fancy_text(front, "WIN A PLUSH PRIZE!", F_HB, 48, (512, 362), (255, 230, 80), (255, 190, 30), shine=False, track=4)
        for x in (210, 814):
            star(d, x, 362, 18, (255, 226, 60))
    elif style == 1:
        # LUCKY GRAB: midnight-to-blue gradient, sparkles, pink and yellow lettering
        t = np.linspace(0, 1, FH)[:, None, None]
        a = np.array([40, 10, 110])[None, None, :] * (1 - t) + np.array([10, 60, 150])[None, None, :] * t
        a = np.repeat(a, W, axis=1).astype(np.float32)
        yy, xx = np.mgrid[0:FH, 0:W]
        glow = np.exp(-(((xx - 600) / 300) ** 2 + ((yy - 190) / 140) ** 2))
        a += glow[:, :, None] * np.array([90, 40, 120])[None, None, :]
        front = to_img(a)
        d = ImageDraw.Draw(front)
        # a burst behind GRAB
        cx, cy = 640, 215
        pts = []
        for i in range(40):
            r = 190 if i % 2 == 0 else 120
            an = math.radians(i * 9)
            pts.append((cx + r * 1.5 * math.cos(an), cy + r * math.sin(an)))
        d.polygon(pts, fill=(255, 70, 170))
        pts2 = [(cx + (p[0] - cx) * 0.86, cy + (p[1] - cy) * 0.86) for p in pts]
        d.polygon(pts2, fill=(255, 120, 200))
        for i in range(40):
            sparkle(d, rr.uniform(10, W - 10), rr.uniform(10, 330), rr.uniform(5, 15), (255, 255, 230))
        for i in range(12):
            star(d, rr.uniform(20, 300), rr.uniform(220, 320), rr.uniform(8, 14), (90, 240, 255))
        fancy_text(front, "Lucky", F_POPI, 140, (270, 120), (255, 150, 220), (255, 40, 150),
                   outlines=[(8, (10, 10, 40)), (6, (80, 240, 255))], shadow=((6, 7), (10, 0, 30)), max_w=420)
        fancy_text(front, "GRAB", F_BLACKI, 190, (640, 220), (255, 250, 140), (255, 190, 0),
                   outlines=[(10, (10, 10, 40)), (6, (255, 255, 255)), (8, (40, 20, 120))], shadow=((8, 10), (10, 0, 30)), max_w=560)
        d.rectangle([0, 330, W, FH], fill=(230, 30, 140))
        d.rectangle([0, 330, W, 336], fill=(90, 240, 255))
        fancy_text(front, "PLUSH  TOYS  *  PRIZES", F_HB, 44, (512, 368), (255, 255, 255), (240, 240, 255), shine=False, track=3)
        for x in (150, 874):
            star(d, x, 368, 18, (255, 240, 90))
    else:
        # SKILL CRANE: yellow, halftone dots, blue stripes, red letters, a claw graphic
        front = Image.new("RGB", (W, FH), (255, 208, 0))
        d = ImageDraw.Draw(front)
        for j in range(0, FH, 16):
            for i in range(0, W, 16):
                r = 2.5 + 2.5 * (j / FH)
                ox = 8 if (j // 16) % 2 else 0
                d.ellipse([i + ox - r, j - r, i + ox + r, j + r], fill=(255, 188, 0))
        for k in range(-2, 8):
            x = k * 46
            d.polygon([(x, 0), (x + 24, 0), (x + 24 - 120, FH), (x - 120, FH)], fill=(20, 60, 170))
            x2 = W - k * 46
            d.polygon([(x2, 0), (x2 - 24, 0), (x2 - 24 + 120, FH), (x2 + 120, FH)], fill=(20, 60, 170))
        d.rectangle([0, 0, W, 14], fill=(200, 20, 30)); d.rectangle([0, 316, W, 324], fill=(200, 20, 30))
        claw_icon(d, 190, 150, 70)
        d.ellipse([140, 228, 240, 318], fill=(230, 40, 50), outline=(40, 20, 30), width=4)
        d.arc([150, 236, 230, 310], 200, 300, fill=(255, 160, 160), width=6)
        fancy_text(front, "SKILL", F_ADV, 150, (600, 108), (255, 80, 70), (200, 10, 20),
                   outlines=[(9, (20, 30, 90)), (6, (255, 255, 255))], shadow=((9, 9), (20, 30, 90)), max_w=520)
        fancy_text(front, "CRANE", F_ADV, 150, (600, 248), (255, 80, 70), (200, 10, 20),
                   outlines=[(9, (20, 30, 90)), (6, (255, 255, 255))], shadow=((9, 9), (20, 30, 90)), max_w=560)
        d.rectangle([0, 324, W, FH], fill=(20, 50, 150))
        fancy_text(front, "TEST YOUR SKILL!", F_HB, 46, (512, 362), (255, 255, 255), (230, 236, 255), shine=False, track=4)
        for x in (220, 804):
            star(d, x, 362, 17, (255, 214, 0))
    im.paste(backlit(front, seed=10 + style), (0, 0))

    # side marquee, 512x224 (u runs front -> back on the right-hand side)
    SW, SH = 512, 224
    side = Image.new("RGB", (SW, SH))
    sd = ImageDraw.Draw(side)
    if style == 0:
        side.paste(front.crop((300, 40, 300 + SW, 40 + SH)).resize((SW, SH)))
        side = Image.new("RGB", (SW, SH), (200, 30, 24))
        sd = ImageDraw.Draw(side)
        for i in range(-4, 30):
            sd.polygon([(i * 32, 0), (i * 32 + 16, 0), (i * 32 + 16 - 90, SH), (i * 32 - 90, SH)], fill=(230, 64, 26))
        bear_face(sd, 90, 112, 62, (196, 132, 70), (238, 210, 160))
        fancy_text(side, "WIN!", F_BLACKI, 140, (330, 112), (255, 246, 120), (255, 170, 0),
                   outlines=[(8, (20, 6, 6)), (5, (255, 255, 255)), (6, (150, 10, 10))], shadow=((6, 7), (40, 0, 0)), max_w=300)
    elif style == 1:
        t = np.linspace(0, 1, SH)[:, None, None]
        a = np.array([40, 10, 110])[None, None, :] * (1 - t) + np.array([10, 60, 150])[None, None, :] * t
        side = to_img(np.repeat(a, SW, axis=1))
        sd = ImageDraw.Draw(side)
        for i in range(24):
            sparkle(sd, rr.uniform(5, SW - 5), rr.uniform(5, SH - 5), rr.uniform(5, 12), (255, 255, 230))
        star(sd, 256, 112, 100, (255, 70, 170), inner=0.5)
        fancy_text(side, "WIN!", F_BLACKI, 120, (256, 112), (255, 250, 140), (255, 190, 0),
                   outlines=[(8, (10, 10, 40)), (5, (80, 240, 255))], shadow=((6, 7), (10, 0, 30)), max_w=280)
    else:
        side = Image.new("RGB", (SW, SH), (255, 208, 0))
        sd = ImageDraw.Draw(side)
        for k in range(-2, 16):
            x = k * 46
            sd.polygon([(x, 0), (x + 20, 0), (x + 20 - 80, SH), (x - 80, SH)], fill=(255, 188, 0))
        claw_icon(sd, 110, 90, 48)
        sd.ellipse([75, 150, 145, 214], fill=(30, 70, 200), outline=(20, 20, 50), width=3)
        fancy_text(side, "WIN!", F_ADV, 120, (330, 112), (255, 80, 70), (200, 10, 20),
                   outlines=[(8, (20, 30, 90)), (5, (255, 255, 255))], shadow=((7, 7), (20, 30, 90)), max_w=300)
    im.paste(backlit(side, tubes=(0.5,), seed=20 + style), (0, 416))
    save(im, "crane_header_%d.png" % style, colors=256)


# ------------------------------------------------------------------ cabinet atlas
CAB = [  # laminate, T-molding, decal accent colours
    {"lam": (22, 22, 25), "tm": (190, 192, 198), "tm_chrome": True, "a1": (230, 40, 30), "a2": (255, 200, 30), "title": "PRIZE CATCHER"},
    {"lam": (28, 54, 142), "tm": (18, 18, 20), "tm_chrome": False, "a1": (255, 70, 170), "a2": (90, 230, 255), "title": "LUCKY GRAB"},
    {"lam": (150, 20, 24), "tm": (18, 18, 20), "tm_chrome": False, "a1": (255, 208, 0), "a2": (30, 70, 190), "title": "SKILL CRANE"},
]
PXM = 550.0  # cabinet atlas pixels per metre


def laminate(w, h, col, seed, grain=5.0):
    n1 = noise(h, w, 1.0, seed) * grain * 0.5
    n2 = noise(h, w, 18.0, seed + 1) * grain * 0.35
    a = np.ones((h, w, 3), np.float32) * np.array(col, np.float32)[None, None, :]
    a += (n1 + n2)[:, :, None]
    return a


def wear(a, seed, edges=True, scuffs=40, kick=True, light=(150, 150, 150)):
    """Paint scuffs, edge wear and shoe kicks into a float image array."""
    h, w, _ = a.shape
    r = random.Random(seed)
    im = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(im)
    for i in range(scuffs):
        x = r.uniform(0, w); y = r.uniform(0, h)
        if kick and r.random() < 0.6:
            y = r.uniform(h * 0.78, h)          # shoe scuffs low down
        L = r.uniform(4, 30); an = r.uniform(-0.5, 0.5)
        d.line([x, y, x + L * math.cos(an), y + L * math.sin(an)], fill=r.randint(25, 70), width=1)
    if edges:
        e = np.zeros((h, w), np.float32)
        nn = (noise(h, w, 2.0, seed + 5) > 0.7).astype(np.float32)
        band = np.zeros((h, w), np.float32)
        band[:, :5] = 1; band[:, -5:] = 1; band[-6:, :] = 1
        e = band * nn * 60
        m = np.asarray(im).astype(np.float32) + e
    else:
        m = np.asarray(im).astype(np.float32)
    m = m / 255.0
    a = a * (1 - m[:, :, None]) + np.array(light, np.float32)[None, None, :] * m[:, :, None]
    return a


def tmold(d, x0, y0, x1, y1, col, chrome):
    """A vertical T-molding strip with a highlight down its rounded face."""
    d.rectangle([x0, y0, x1, y1], fill=col)
    if chrome:
        w = x1 - x0
        d.rectangle([x0 + w * 0.3, y0, x0 + w * 0.5, y1], fill=(250, 250, 252))
        d.rectangle([x0, y0, x0 + 1, y1], fill=(90, 90, 96))
        d.rectangle([x1 - 1, y0, x1, y1], fill=(110, 110, 116))
    else:
        d.rectangle([x0 + (x1 - x0) * 0.35, y0, x0 + (x1 - x0) * 0.5, y1], fill=(70, 70, 74))


def sticker(base, box, bg, lines, fg=(10, 10, 10), fpath=F_CN, fade=0.0, border=None, rot=0.0):
    x0, y0, x1, y1 = [int(v) for v in box]
    w, h = x1 - x0, y1 - y0
    s = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(s)
    if border:
        d.rectangle([1, 1, w - 2, h - 2], outline=border, width=2)
    n = len(lines)
    for i, ln in enumerate(lines):
        sz = int(h / (n + 0.6) * 0.9)
        f = font(fpath, sz)
        while f.getlength(ln) > w * 0.9 and sz > 6:
            sz -= 1; f = font(fpath, sz)
        tw = f.getlength(ln)
        bb = f.getbbox(ln)
        d.text(((w - tw) / 2, h * (i + 0.5) / n - (bb[1] + bb[3]) / 2), ln, font=f, fill=fg)
    if fade:
        s = Image.blend(s, Image.new("RGB", (w, h), (230, 226, 210)), fade)
    mask = Image.new("L", (w, h), 255)
    if rot:
        s = s.rotate(rot, expand=True, resample=Image.BICUBIC)
        mask = mask.rotate(rot, expand=True, resample=Image.BICUBIC)
    base.paste(s, (x0, y0), mask)


def cab(style):
    S = CAB[style]
    W, H = 1024, 512
    im = Image.new("RGB", (W, H), (0, 0, 0))
    # ---- front, 0.80 x 0.79 m (y 0.05..0.84): px = (x + 0.40) * PXM, py = (0.84 - y) * PXM
    FW, FH = 440, 435
    a = laminate(FW, FH, S["lam"], 300 + style)
    a = wear(a, 310 + style, light=(120, 120, 124) if style == 0 else tuple(min(255, c + 70) for c in S["lam"]))
    f = to_img(a)
    d = ImageDraw.Draw(f)
    P = lambda x, y: ((x + 0.40) * PXM, (0.84 - y) * PXM)
    # decal: a band of stripes across the lower front
    yb0 = P(0, 0.20)[1]; yb1 = P(0, 0.12)[1]
    d.rectangle([0, yb0, FW, yb0 + 10], fill=S["a1"])
    d.rectangle([0, yb0 + 16, FW, yb0 + 22], fill=S["a2"])
    d.rectangle([0, yb0 + 28, FW, yb0 + 31], fill=S["a1"])
    # prize door frame: x -0.33..-0.13, y 0.30..0.52 (the flap itself is geometry)
    px0, py0 = P(-0.345, 0.535); px1, py1 = P(-0.115, 0.285)
    d.rounded_rectangle([px0, py0, px1, py1], radius=6, fill=(170, 172, 178))
    d.rounded_rectangle([px0 + 4, py0 + 4, px1 - 4, py1 - 4], radius=4, fill=(120, 122, 128))
    d.rectangle(list(P(-0.33, 0.52)) + list(P(-0.13, 0.30)), fill=(6, 6, 6))
    for sx, sy in [(-0.338, 0.527), (-0.122, 0.527), (-0.338, 0.293), (-0.122, 0.293)]:
        x, y = P(sx, sy); d.ellipse([x - 2.5, y - 2.5, x + 2.5, y + 2.5], fill=(220, 220, 225), outline=(60, 60, 60))
    sticker(f, list(P(-0.33, 0.60)) + list(P(-0.13, 0.555)), (255, 214, 30), ["PRIZE"], fg=(20, 10, 10), fpath=F_HB, fade=0.12)
    # coin door: x 0.05..0.31, y 0.40..0.74 (a proud plate in crane.gd maps this region)
    cx0, cy0 = P(0.05, 0.74); cx1, cy1 = P(0.31, 0.40)
    cw, chh = int(cx1 - cx0), int(cy1 - cy0)
    door = laminate(cw, chh, (66, 68, 74), 330, grain=3.0)
    door += (noise(chh, cw, 1, 331)[:, :, None] * 0) + np.linspace(-6, 6, cw)[None, :, None]
    dimg = to_img(door)
    dd = ImageDraw.Draw(dimg)
    dd.rectangle([0, 0, cw - 1, chh - 1], outline=(30, 30, 34), width=2)
    dd.rectangle([3, 3, cw - 4, chh - 4], outline=(110, 112, 118), width=1)
    # two coin-entry bezels (their lit inserts are geometry), price card, two return buttons, lock
    for k in range(2):
        bx = cw * (0.27 + 0.46 * k)
        dd.rounded_rectangle([bx - 19, 14, bx + 19, 72], radius=4, fill=(196, 198, 204), outline=(60, 60, 66))
        dd.rectangle([bx - 13, 20, bx + 13, 54], fill=(40, 6, 6))
        dd.rectangle([bx - 2, 58, bx + 2, 68], fill=(10, 10, 10))
    sticker(dimg, (16, 80, cw - 16, 108), (250, 246, 230), ["1 TOKEN  PER PLAY"], fg=(160, 10, 10), border=(160, 10, 10), fade=0.08)
    for k in range(2):
        bx = cw * (0.27 + 0.46 * k)
        dd.rounded_rectangle([bx - 14, 118, bx + 14, 142], radius=3, fill=(180, 182, 188), outline=(50, 50, 56))
        dd.rectangle([bx - 8, 126, bx + 8, 132], fill=(12, 12, 12))
    f9 = font(F_CN, 10)
    dd.text((cw / 2 - f9.getlength("COIN RETURN") / 2, 146), "COIN RETURN", font=f9, fill=(200, 200, 204))
    dd.ellipse([cw / 2 - 9, chh - 26, cw / 2 + 9, chh - 8], fill=(200, 196, 170), outline=(70, 66, 50), width=2)
    dd.rectangle([cw / 2 - 1.5, chh - 22, cw / 2 + 1.5, chh - 12], fill=(40, 36, 20))
    # fingerprints and grime around the coin slots
    g = to_img(np.zeros((chh, cw, 3)))
    f.paste(dimg, (int(cx0), int(cy0)))
    # operator stickers
    sticker(f, list(P(0.07, 0.36)) + list(P(0.29, 0.32)), (230, 30, 30), ["TOKENS ONLY"], fg=(255, 255, 255), fpath=F_HB, fade=0.1)
    sticker(f, list(P(0.07, 0.30)) + list(P(0.29, 0.255)), (250, 248, 240), ["PLAY AT YOUR OWN RISK", "SKILL REQUIRED"], fg=(20, 20, 20), fade=0.15, border=(20, 20, 20))
    # serial plate low on the left
    sp = P(-0.36, 0.25)
    d.rectangle([sp[0], sp[1], sp[0] + 46, sp[1] + 18], fill=(176, 170, 150), outline=(90, 86, 70))
    d.text((sp[0] + 4, sp[1] + 3), "SER 4471", font=font(F_CN, 10), fill=(60, 56, 44))
    # T-molding on both front edges, chrome kick at the bottom
    tmold(d, 0, 0, 7, FH, S["tm"], S["tm_chrome"])
    tmold(d, FW - 8, 0, FW - 1, FH, S["tm"], S["tm_chrome"])
    # finger grime under the panel lip, toe scuffs at the bottom
    fa = np.asarray(f).astype(np.float32)
    yy = np.arange(FH)[:, None]
    grime = np.exp(-(yy / 25.0)) * 18
    fa = fa - grime[:, :, None] * 0.6
    f = to_img(fa)
    im.paste(f, (0, 0))

    # ---- side, 0.85 x 0.87 m (z 0.05..0.90, y 0.05..0.92); u = 0 at the front edge
    SW, SH = 468, 479
    a = laminate(SW, SH, S["lam"], 340 + style)
    a = wear(a, 350 + style, scuffs=60, light=(120, 120, 124) if style == 0 else tuple(min(255, c + 70) for c in S["lam"]))
    s = to_img(a)
    sd = ImageDraw.Draw(s)
    # a big swoosh decal with stars and the title
    sw = Image.new("L", (SW, SH), 0)
    swd = ImageDraw.Draw(sw)
    swd.polygon([(0, SH * 0.62), (SW, SH * 0.38), (SW, SH * 0.52), (0, SH * 0.80)], fill=255)
    s.paste(Image.new("RGB", (SW, SH), S["a1"]), (0, 0), sw)
    sw2 = Image.new("L", (SW, SH), 0)
    ImageDraw.Draw(sw2).polygon([(0, SH * 0.83), (SW, SH * 0.56), (SW, SH * 0.60), (0, SH * 0.88)], fill=255)
    s.paste(Image.new("RGB", (SW, SH), S["a2"]), (0, 0), sw2)
    rs = random.Random(360 + style)
    for i in range(9):
        star(sd, rs.uniform(30, SW - 30), rs.uniform(SH * 0.12, SH * 0.36), rs.uniform(8, 20), S["a2"])
    fancy_text(s, S["title"], F_BLACKI, 60, (SW * 0.5, SH * 0.25), (255, 255, 255), (220, 220, 230),
               outlines=[(4, (10, 10, 12)), (3, S["a1"])], max_w=SW * 0.85)
    # decal edge wear: knock back the decal where the laminate is scuffed
    sa = np.asarray(s).astype(np.float32)
    sa = wear(sa, 370 + style, edges=False, scuffs=50, light=tuple(min(255, c + 60) for c in S["lam"]))
    s = to_img(sa)
    sd = ImageDraw.Draw(s)
    tmold(sd, 0, 0, 7, SH, S["tm"], S["tm_chrome"])
    tmold(sd, SW - 8, 0, SW - 1, SH, S["tm"], S["tm_chrome"])
    sd.ellipse([SW - 60, 40, SW - 44, 56], fill=(180, 176, 150), outline=(60, 56, 40))   # back-door lock
    im.paste(s, (448, 0))
    save(im, "crane_cab_%d.png" % style, colors=256)


# ------------------------------------------------------------------ control panel, flap, lamp
def panel():
    W, H = 512, 256
    im = Image.new("RGB", (W, H), (0, 0, 0))
    # top: 0.80 m x 0.17 m, v = 0 at the back edge; joystick at x -0.12, button at x 0.13, both z 0.085
    top = to_img(laminate(512, 110, (24, 24, 28), 400, grain=4))
    d = ImageDraw.Draw(top)
    jx, bx, cy = (0.28 / 0.8) * 512, (0.53 / 0.8) * 512, 55
    d.ellipse([jx - 36, cy - 36, jx + 36, cy + 36], outline=(250, 210, 30), width=3)
    for an in range(4):
        a = math.radians(an * 90)
        ux, uy = math.cos(a), math.sin(a)
        tip = (jx + ux * 50, cy + uy * 50)
        b1 = (jx + ux * 41 - uy * 7, cy + uy * 41 + ux * 7)
        b2 = (jx + ux * 41 + uy * 7, cy + uy * 41 - ux * 7)
        d.polygon([tip, b1, b2], fill=(250, 210, 30))
    d.ellipse([bx - 34, cy - 34, bx + 34, cy + 34], outline=(240, 40, 40), width=3)
    fs = font(F_HB, 13)
    d.text((bx + 42, cy - 8), "DROP", font=fs, fill=(240, 240, 240))
    d.text((jx + 42, cy - 30), "MOVE", font=fs, fill=(240, 240, 240))
    f2 = font(F_CN, 11)
    for i, ln in enumerate(["1. INSERT TOKEN", "2. MOVE CLAW", "3. PRESS TO DROP"]):
        d.text((6, 22 + i * 16), ln, font=f2, fill=(220, 220, 200))
    d.text((420, 20), "SKILL", font=font(F_HB, 16), fill=(250, 210, 30))
    d.text((420, 40), "GAME", font=font(F_HB, 16), fill=(250, 210, 30))
    ta = np.asarray(top).astype(np.float32)
    # wrist-worn gloss and grime band at the front edge (bottom of the image)
    yy = np.arange(110)[:, None]
    ta += (np.exp(-((110 - yy) / 14.0)) * 14)[:, :, None]
    ta = wear(ta, 410, edges=False, scuffs=50, kick=False, light=(90, 90, 92))
    im.paste(to_img(ta), (0, 0))
    # fascia 512x52
    fa = Image.new("RGB", (512, 52), (14, 14, 16))
    fd = ImageDraw.Draw(fa)
    fd.rectangle([0, 0, 512, 4], fill=(200, 202, 208))
    ft = font(F_HB, 20)
    t = "EVERY PRIZE CAN BE WON"
    fd.text((256 - ft.getlength(t) / 2, 16), t, font=ft, fill=(236, 236, 236))
    im.paste(fa, (0, 112))
    # prize flap 80x88: smoked black acrylic with PUSH
    fl = Image.new("RGB", (80, 88), (20, 20, 22))
    fld = ImageDraw.Draw(fl)
    fp = font(F_HB, 18)
    fld.text((40 - fp.getlength("PUSH") / 2, 50), "PUSH", font=fp, fill=(230, 230, 230))
    fld.polygon([(40, 44), (30, 30), (50, 30)], fill=(230, 230, 230))
    fla = wear(np.asarray(fl).astype(np.float32), 420, edges=False, scuffs=30, kick=False, light=(110, 110, 110))
    im.paste(to_img(fla), (0, 168))
    # token lamp 48x64: lit red-orange insert with TOKEN
    lp = np.zeros((64, 48, 3), np.float32)
    yy, xx = np.mgrid[0:64, 0:48]
    gl = np.exp(-(((xx - 24) / 22) ** 2 + ((yy - 32) / 30) ** 2))
    lp[:] = np.array([200, 30, 10])[None, None, :] * 0.6
    lp += gl[:, :, None] * np.array([255, 150, 60])[None, None, :] * 0.8
    li = to_img(lp)
    ld = ImageDraw.Draw(li)
    fl2 = font(F_CN, 11)
    for i, ch in enumerate(["T", "O", "K", "E", "N"]):
        ld.text((24 - fl2.getlength(ch) / 2, 4 + i * 11), ch, font=fl2, fill=(255, 240, 210))
    im.paste(li, (96, 168))
    save(im, "crane_panel.png")


# ------------------------------------------------------------------ glass, fur, faces
def glass():
    W = H = 512
    r = random.Random(500)
    a = np.zeros((H, W), np.float32) + 12.0
    # a dust line along the bottom edge and in the corners
    yy, xx = np.mgrid[0:H, 0:W]
    a += np.exp(-((H - yy) / 14.0)) * 40
    a += (np.exp(-(xx / 10.0)) + np.exp(-((W - xx) / 10.0))) * 14
    # sheen bands
    s = (xx * 0.8 + yy)
    a += np.exp(-((s - 300) / 22) ** 2) * 22 + np.exp(-((s - 380) / 9) ** 2) * 18
    # wiped arcs (cleaning swirls)
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    for i in range(10):
        cx, cy, rad = r.uniform(0, W), r.uniform(0, H), r.uniform(40, 160)
        st = r.uniform(0, 360)
        d.arc([cx - rad, cy - rad, cx + rad, cy + rad], st, st + r.uniform(40, 120), fill=r.randint(10, 22), width=r.randint(6, 18))
    # fingerprints: mostly low (the glass bottom is the image bottom), where hands lean and point
    fp = Image.new("L", (W, H), 0)
    fd = ImageDraw.Draw(fp)
    for i in range(70):
        x = r.gauss(W * 0.5, W * 0.25); y = H - abs(r.gauss(0, H * 0.28)) - 10
        if r.random() < 0.25:
            y = r.uniform(H * 0.2, H * 0.7)
        rx, ry = r.uniform(6, 10), r.uniform(8, 13)
        for k in range(int(rx / 1.9)):
            q = k * 1.9
            fd.ellipse([x - rx + q, y - ry + q, x + rx - q, y + ry - q], outline=r.randint(14, 30), width=1)
    fp = fp.filter(ImageFilter.GaussianBlur(1.0))
    # palm smudges
    for i in range(6):
        x = r.uniform(60, W - 60); y = r.uniform(H * 0.55, H * 0.9)
        e = Image.new("L", (W, H), 0)
        ImageDraw.Draw(e).ellipse([x - 40, y - 26, x + 40, y + 26], fill=26)
        fp = ImageChops.add(fp, e.filter(ImageFilter.GaussianBlur(14)))
    a += np.asarray(m.filter(ImageFilter.GaussianBlur(3))).astype(np.float32)
    a += np.asarray(fp).astype(np.float32)
    a = np.clip(a, 0, 150)
    rgb = np.zeros((H, W, 4), np.float32)
    rgb[:, :, 0] = 222; rgb[:, :, 1] = 232; rgb[:, :, 2] = 236
    rgb[:, :, 3] = a
    Image.fromarray(rgb.astype(np.uint8), "RGBA").save(os.path.join(OUT, "crane_glass.png"), optimize=True)
    print("crane_glass.png", os.path.getsize(os.path.join(OUT, "crane_glass.png")))


def fur():
    """Tileable plush fabric: short pile fibres (streaky noise in two directions) on a soft base."""
    N = 256
    a = 200 + noise(N, N, 1.0, 600) * 10 + periodic_noise(N, N, 0.6, 5.0, 601) * 14 + periodic_noise(N, N, 5.0, 0.7, 602) * 8
    a += noise(N, N, 10.0, 603) * 12
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGB")
    save(img, "crane_fur.png")


def faces():
    W, H = 256, 128
    im = Image.new("RGBA", (W * 2, H * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    S = 2
    # eyes: quad 0.06 m wide, eyes at +-0.02 m, radius 0.0075 m (128 px = 0.06 m)
    for ex in (64 - 43, 64 + 43):
        d.ellipse([(ex - 16) * S, (64 - 16) * S, (ex + 16) * S, (64 + 16) * S], fill=(12, 8, 6, 255))
        d.ellipse([(ex - 7) * S, (64 - 11) * S, (ex - 1) * S, (64 - 5) * S], fill=(250, 250, 250, 255))
    # nose + stitched mouth (right square, quad 0.03 m)
    o = 128
    d.ellipse([(o + 34) * S, 22 * S, (o + 94) * S, 62 * S], fill=(20, 12, 10, 255))
    d.ellipse([(o + 48) * S, 28 * S, (o + 62) * S, 36 * S], fill=(120, 110, 108, 255))
    d.line([(o + 64) * S, 60 * S, (o + 64) * S, 76 * S], fill=(30, 18, 14, 255), width=5 * S)
    d.arc([(o + 34) * S, 50 * S, (o + 64) * S, 90 * S], 20, 160, fill=(30, 18, 14, 255), width=5 * S)
    d.arc([(o + 64) * S, 50 * S, (o + 94) * S, 90 * S], 20, 160, fill=(30, 18, 14, 255), width=5 * S)
    im = im.resize((W, H), Image.LANCZOS)
    im.save(os.path.join(OUT, "crane_face.png"), optimize=True)
    print("crane_face.png", os.path.getsize(os.path.join(OUT, "crane_face.png")))


if __name__ == "__main__":
    for s in range(3):
        header(s)
        cab(s)
    panel()
    glass()
    fur()
    faces()
    tot = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT) if f.startswith("crane_") and f.endswith(".png"))
    print("total bytes", tot)
