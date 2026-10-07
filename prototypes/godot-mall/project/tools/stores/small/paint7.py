"""Textures for the Wave 7 shops (tools/stores/small/wave7.gd), written to tex/w7/*.png:
Merry-Go-Round's sunset stripes, Regis' travertine, Gordon's back-lit sign panels, Sports
Avenue's bulb marquee, Orange Julius' red-and-black diamond course, Great American Cookie
Co.'s sign box and cookie case, Afterthoughts' mauve mosaic. All from the Southland facade
records (Steven's photos); names are the stores' own, everything else invented.
  python3 tools/stores/small/paint7.py   (from the project folder)
"""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "kay_bee"))
import paint_store as kb   # noqa: E402

OUT = os.path.join(HERE, "..", "..", "..", "tex", "w7")
os.makedirs(OUT, exist_ok=True)
BOLD = kb.BOLD
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SCRIPT = os.path.join(HERE, "..", "gumballs", "MrDafoe-Regular.ttf")
SS = 2


def save(im, name, colors=0):
    im = im.convert("RGB")
    if colors:
        im = im.quantize(colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(os.path.join(OUT, name + ".png"), optimize=True)


def sunset():
    """Merry-Go-Round's sunset stripes on the back wall: 1024 x 256 = 6 m x 1.5 m."""
    W, H = 1024, 256
    im = Image.new("RGB", (W, H), (250, 240, 220))
    d = ImageDraw.Draw(im)
    cols = [(250, 200, 60), (246, 150, 50), (236, 90, 60), (210, 50, 90), (140, 40, 120)]
    for k, c in enumerate(cols):
        d.rectangle([0, 40 + k * 40, W, 40 + k * 40 + 28], fill=c)
    save(kb.grain(im, 1.5, 101), "sunset", 32)


def travertine():
    """Regis' honed travertine, 0.6 m square: cream with pits and bedding lines."""
    N = 256
    a = np.zeros((N, N, 3), np.float32) + np.array([222, 208, 184], np.float32)
    a += kb.noise(N, N, 5, 103, blur=4)[..., None]
    r = np.random.default_rng(104)
    for _ in range(140):
        x, y = r.integers(0, N - 6), r.integers(0, N - 3)
        a[y:y + 2, x:x + r.integers(2, 6)] -= 40
    for y in range(0, N, 21):
        a[y:y + 1] -= 12
    a[:, :2] -= 30; a[:2, :] -= 30
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "travertine", 48)


def gordons():
    """Gordon's Jewelers' header: a row of back-lit frosted panels in dark bronze crossed by one
    long arch, the name on the centre panel in a narrow high-contrast serif. 2048 x 256 =
    8 m x 1 m."""
    W, H = 2048, 256
    im = Image.new("RGB", (W, H), (60, 46, 34))
    d = ImageDraw.Draw(im)
    n = 7
    pw = (W - 40) / n
    for k in range(n):
        x0 = 20 + k * pw
        d.rectangle([x0 + 6, 24, x0 + pw - 6, H - 24], fill=(244, 238, 222))
    d.arc([60, 30, W - 60, H * 3], 190, 350, fill=(60, 46, 34), width=10)
    c = 3
    x0 = 20 + c * pw
    f = ImageFont.truetype(SERIF, 64)
    l, t, r, b = d.textbbox((0, 0), "Gordon's", font=f)
    d.text((x0 + pw / 2 - (l + r) / 2, H * 0.36 - (t + b) / 2), "Gordon's", font=f, fill=(40, 30, 24))
    f2 = ImageFont.truetype(SERIF, 26)
    l, t, r, b = d.textbbox((0, 0), "JEWELERS", font=f2)
    d.text((x0 + pw / 2 - (l + r) / 2, H * 0.62 - (t + b) / 2), "JEWELERS", font=f2, fill=(40, 30, 24))
    save(kb.grain(im, 1.2, 105), "gordons", 48)


def marquee():
    """Sports Avenue's gold marquee: a field of white bulbs with SPORTS picked out in red, a star
    at each corner. 1024 x 384 = 3.2 m x 1.2 m."""
    W, H = 1024, 384
    im = Image.new("RGB", (W, H), (200, 160, 50))
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    kb.fit_text(md, "SPORTS", (90, 60, W - 90, H - 60), BOLD, 255)
    m = np.asarray(mask)
    d = ImageDraw.Draw(im)
    for y in range(24, H - 12, 24):
        for x in range(24, W - 12, 24):
            on = m[y, x] > 128
            d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=(240, 40, 40) if on else (255, 250, 230))
    for cx, cy in [(40, 40), (W - 40, 40), (40, H - 40), (W - 40, H - 40)]:
        pts = []
        for k in range(10):
            rr = 30 if k % 2 == 0 else 12
            a = -math.pi / 2 + k * math.pi / 5
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        d.polygon(pts, fill=(240, 40, 40))
    save(im, "marquee", 32)


def diamonds():
    """Orange Julius' course of red tiles set with black diamonds, 0.6 m x 0.15 m (256 x 64)."""
    W, H = 256, 64
    im = Image.new("RGB", (W, H), (190, 40, 36))
    d = ImageDraw.Draw(im)
    for k in range(4):
        cx = 32 + k * 64
        d.polygon([(cx, 8), (cx + 22, 32), (cx, 56), (cx - 22, 32)], fill=(24, 20, 20))
        d.line([k * 64, 0, k * 64, H], fill=(120, 30, 26), width=2)
    save(kb.grain(im, 2, 106), "diamonds", 16)


def cookie_sign():
    """Great American Cookie Co.'s sign box: cream with maroon checkerboard corners, a maroon lobe
    with 'Great American' in yellow script over a black pill of white capitals. 1024 x 320 =
    4.6 m x 1.4 m."""
    W, H = 1024 * SS, 320 * SS
    im = Image.new("RGB", (W, H), (244, 236, 214))
    d = ImageDraw.Draw(im)
    cs = 22 * SS
    for (x0, y0) in [(0, 0), (W - 4 * cs, 0), (0, H - 4 * cs), (W - 4 * cs, H - 4 * cs)]:
        for j in range(4):
            for i in range(4):
                if (i + j) % 2 == 0:
                    d.rectangle([x0 + i * cs, y0 + j * cs, x0 + (i + 1) * cs, y0 + (j + 1) * cs], fill=(120, 24, 40))
    d.ellipse([W * 0.2, 16 * SS, W * 0.8, H * 0.62], fill=(120, 24, 40))
    kb.fit_text(d, "Great American", (W * 0.25, 40 * SS, W * 0.75, H * 0.5), SCRIPT, (255, 220, 60))
    d.rounded_rectangle([W * 0.18, H * 0.6, W * 0.82, H * 0.92], radius=H * 0.16, fill=(20, 20, 22))
    kb.fit_text(d, "COOKIE COMPANY", (W * 0.24, H * 0.64, W * 0.76, H * 0.88), BOLD, (255, 255, 255))
    im = im.resize((1024, 320), Image.LANCZOS)
    save(kb.grain(im, 1.2, 107), "cookie_sign", 48)


def cookies():
    """The glass case of cookies and the lit panels of cookie cakes: 512 x 256 = 1.2 m x 0.6 m."""
    W, H = 512, 256
    rng = random.Random(108)
    im = Image.new("RGB", (W, H), (240, 236, 226))
    d = ImageDraw.Draw(im)
    for j in range(3):
        for i in range(8):
            cx, cy = 32 + i * 64, 44 + j * 84
            r = 26
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rng.choice([(200, 150, 90), (180, 120, 70), (120, 80, 50), (220, 180, 120)]))
            for _ in range(5):
                x, y = cx + rng.uniform(-16, 16), cy + rng.uniform(-16, 16)
                d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(60, 36, 24))
    save(kb.grain(im, 2, 109), "cookies", 64)


def mosaic():
    """Afterthoughts' mauve mosaic tile with a raised pink speed-line, 0.6 m square."""
    N = 256
    a = np.zeros((N, N, 3), np.float32)
    r = np.random.default_rng(110)
    for j in range(0, N, 16):
        for i in range(0, N, 16):
            a[j:j + 16, i:i + 16] = np.array([150, 100, 140], np.float32) + r.uniform(-14, 14)
    for k in range(0, N, 16):
        a[k:k + 1] = 220; a[:, k:k + 1] = 220
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "mosaic", 32)


if __name__ == "__main__":
    sunset(); travertine(); gordons(); marquee(); diamonds(); cookie_sign(); cookies(); mosaic()
    print("wrote tex/w7/*.png")
