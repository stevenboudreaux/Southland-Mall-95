"""Textures for the Chick-fil-A rebuild (tools/stores/cfa/store.gd), from Steven's video of the
Southland unit (Oct 8, 2026; design/storefronts/chick-fil-a.md), written to tex/cfa/*.png.

  python3 tools/stores/cfa/paint.py   (from the project folder)

The menu board's layout follows the video (dark panels, a food picture at each end, white
lines); its lines and prices are not readable in the video and are period guesses. The food
pictures and framed prints are painted here, not copied from anything.
"""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "..", "tex", "cfa")
os.makedirs(OUT, exist_ok=True)
BOLD = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
SANS = "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
R = random.Random(64)


def save(im, name):
    im.convert("RGB").save(os.path.join(OUT, name + ".png"), optimize=True)


def font(p, s):
    return ImageFont.truetype(p, s)


def wallpaper():
    """Cream paper with sage stripes: a pair of hairlines framing a chain of small lozenges,
    repeating about every 13 cm (the booth close-ups, 30-38 s). One tile = 0.52 m square."""
    N = 512
    im = Image.new("RGB", (N, N), (238, 232, 212))
    d = ImageDraw.Draw(im)
    sage = (150, 166, 132)
    light = (196, 204, 176)
    for k in range(4):
        x = k * 128 + 64
        for dx in (-17, 17):
            d.line([(x + dx, 0), (x + dx, N)], fill=sage, width=3)
        for dx in (-11, 11):
            d.line([(x + dx, 0), (x + dx, N)], fill=light, width=1)
        y = 0
        while y < N:
            d.polygon([(x, y), (x + 7, y + 16), (x, y + 32), (x - 7, y + 16)], fill=sage)
            d.ellipse([x - 2, y + 37, x + 2, y + 41], fill=sage)
            y += 46 if (N % 46) == 0 else 64
        # a faint second stripe between the main ones
        d.line([(x + 64, 0), (x + 64, N)], fill=(226, 222, 200), width=2)
    a = np.asarray(im).astype(np.float32)
    a += np.random.default_rng(1).normal(0, 2.0, a.shape)
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "wallpaper")


def quarry():
    """Red quarry pavers, 10 x 20 cm in running bond, dark grout (23 s). One tile = 0.8 m."""
    N = 512
    px = N / 0.8
    im = Image.new("RGB", (N, N), (58, 36, 30))
    d = ImageDraw.Draw(im)
    rows = 8
    h = N / rows
    for r in range(rows):
        off = (r % 2) * (px * 0.1)
        x = -off
        while x < N:
            c = R.randint(-14, 14)
            col = (138 + c, 58 + c // 2, 44 + c // 3)
            d.rectangle([x + 2, r * h + 2, x + px * 0.2 - 3, (r + 1) * h - 3], fill=col)
            x += px * 0.2
    a = np.asarray(im).astype(np.float32)
    a += np.random.default_rng(2).normal(0, 4.0, a.shape)
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))
    save(im, "quarry")


def vinyl():
    """Booth vinyl, sage-cream, button-tufted in diamonds (10 s, 36 s). One tile = 0.4 m."""
    N = 256
    a = np.zeros((N, N, 3), np.float32)
    base = np.array([196, 196, 160], np.float32)
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    s = N / 2.0
    # distance to the nearest tuft in a diamond lattice
    best = np.full((N, N), 1e9, np.float32)
    for cy in (0, s, 2 * s):
        for cx in (0, s, 2 * s):
            best = np.minimum(best, np.hypot(xx - cx, yy - cy))
    for cy in (s / 2, 1.5 * s):
        for cx in (s / 2, 1.5 * s):
            best = np.minimum(best, np.hypot(xx - cx, yy - cy))
    shade = 0.72 + 0.28 * np.clip(best / (s * 0.5), 0, 1) ** 0.6
    a = base[None, None, :] * shade[:, :, None]
    a[best < 4] = [96, 94, 70]
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "vinyl")


def prints():
    """Four framed prints in a 4 x 1 strip, dark frames with a cream mat: soft country scenes
    (the video's pictures are too small to read; these are invented)."""
    W, H = 256, 320
    im = Image.new("RGB", (W * 4, H), (40, 28, 20))
    for k in range(4):
        x0 = k * W
        d = ImageDraw.Draw(im)
        d.rectangle([x0 + 18, 18, x0 + W - 19, H - 19], fill=(224, 214, 188))
        ix0, iy0, ix1, iy1 = x0 + 46, 50, x0 + W - 47, H - 51
        sky = [(176, 192, 196), (196, 186, 160), (170, 186, 200), (204, 196, 170)][k]
        d.rectangle([ix0, iy0, ix1, iy1], fill=sky)
        hz = iy0 + (iy1 - iy0) * (0.55 + 0.05 * k)
        d.polygon([(ix0, hz), (ix0 + 60, hz - 30), (ix0 + 120, hz - 8), (ix1, hz - 26), (ix1, iy1), (ix0, iy1)], fill=(108, 124, 82))
        d.rectangle([ix0, hz + 30, ix1, iy1], fill=(132, 140, 90))
        if k == 0:   # a barn
            d.rectangle([ix0 + 40, hz - 40, ix0 + 100, hz + 10], fill=(140, 48, 40))
            d.polygon([(ix0 + 34, hz - 40), (ix0 + 70, hz - 70), (ix0 + 106, hz - 40)], fill=(90, 40, 34))
        elif k == 1:  # a hen and chicks in a yard
            d.ellipse([ix0 + 60, hz + 20, ix0 + 110, hz + 55], fill=(168, 96, 52))
            d.ellipse([ix0 + 98, hz + 8, ix0 + 118, hz + 30], fill=(168, 96, 52))
            for c in range(3):
                d.ellipse([ix0 + 30 + c * 22, hz + 58, ix0 + 42 + c * 22, hz + 68], fill=(230, 200, 90))
        elif k == 2:  # a white farmhouse
            d.rectangle([ix0 + 50, hz - 34, ix0 + 120, hz + 12], fill=(236, 232, 220))
            d.polygon([(ix0 + 44, hz - 34), (ix0 + 85, hz - 62), (ix0 + 126, hz - 34)], fill=(70, 66, 64))
            d.rectangle([ix0 + 78, hz - 10, ix0 + 92, hz + 12], fill=(80, 56, 40))
        else:  # a tree by a fence
            d.ellipse([ix0 + 70, hz - 90, ix0 + 140, hz - 20], fill=(70, 96, 58))
            d.rectangle([ix0 + 100, hz - 30, ix0 + 110, hz + 10], fill=(80, 60, 40))
            for f in range(6):
                d.line([(ix0 + 10 + f * 26, hz + 10), (ix0 + 10 + f * 26, hz + 34)], fill=(230, 226, 214), width=3)
            d.line([(ix0, hz + 18), (ix1, hz + 18)], fill=(230, 226, 214), width=3)
        im.paste(im.crop((ix0, iy0, ix1, iy1)).filter(ImageFilter.GaussianBlur(1.2)), (ix0, iy0))
        d.rectangle([x0 + 4, 4, x0 + W - 5, H - 5], outline=(70, 50, 30), width=6)
    save(im, "prints")


# ------------------------------------------------------------------ the menu board
def _sandwich(d, cx, cy, s):
    d.ellipse([cx - 1.0 * s, cy + 0.05 * s, cx + 1.0 * s, cy + 0.55 * s], fill=(200, 140, 70))      # heel
    d.ellipse([cx - 1.1 * s, cy - 0.25 * s, cx + 1.1 * s, cy + 0.3 * s], fill=(214, 160, 82))       # fillet
    for k in range(3):
        d.ellipse([cx - 0.6 * s + k * 0.45 * s, cy - 0.32 * s, cx - 0.25 * s + k * 0.45 * s, cy - 0.16 * s], fill=(110, 140, 60))
    d.chord([cx - 1.0 * s, cy - 1.0 * s, cx + 1.0 * s, cy - 0.05 * s], 180, 360, fill=(222, 158, 74))  # crown
    d.chord([cx - 0.8 * s, cy - 0.9 * s, cx + 0.5 * s, cy - 0.4 * s], 200, 320, fill=(240, 196, 120))


def _lemonade(d, cx, cy, s):
    d.polygon([(cx - 0.55 * s, cy - 0.9 * s), (cx + 0.55 * s, cy - 0.9 * s), (cx + 0.42 * s, cy + 0.8 * s), (cx - 0.42 * s, cy + 0.8 * s)], fill=(246, 232, 120))
    d.polygon([(cx - 0.55 * s, cy - 0.9 * s), (cx - 0.3 * s, cy - 0.9 * s), (cx - 0.22 * s, cy + 0.8 * s), (cx - 0.42 * s, cy + 0.8 * s)], fill=(255, 250, 200))
    d.ellipse([cx + 0.25 * s, cy - 1.15 * s, cx + 0.95 * s, cy - 0.55 * s], fill=(248, 220, 40))
    d.ellipse([cx + 0.38 * s, cy - 1.02 * s, cx + 0.82 * s, cy - 0.68 * s], fill=(255, 244, 150))
    d.ellipse([cx - 1.1 * s, cy + 0.2 * s, cx - 0.35 * s, cy + 0.85 * s], fill=(236, 200, 30))     # a lemon
    d.polygon([(cx - 0.4 * s, cy + 0.2 * s), (cx - 0.05 * s, cy - 0.1 * s), (cx - 0.25 * s, cy + 0.35 * s)], fill=(70, 120, 50))


def _nuggets(d, cx, cy, s):
    d.polygon([(cx - 0.9 * s, cy - 0.3 * s), (cx + 0.9 * s, cy - 0.3 * s), (cx + 0.7 * s, cy + 0.7 * s), (cx - 0.7 * s, cy + 0.7 * s)], fill=(236, 232, 224))
    rr = random.Random(7)
    for k in range(9):
        x = cx + rr.uniform(-0.6, 0.6) * s
        y = cy + rr.uniform(-0.8, -0.2) * s
        d.ellipse([x - 0.22 * s, y - 0.16 * s, x + 0.22 * s, y + 0.16 * s], fill=(206 + rr.randint(-10, 10), 144, 66), outline=(160, 100, 40))


def _fries(d, cx, cy, s):
    d.polygon([(cx - 0.7 * s, cy - 0.2 * s), (cx + 0.7 * s, cy - 0.2 * s), (cx + 0.55 * s, cy + 0.8 * s), (cx - 0.55 * s, cy + 0.8 * s)], fill=(196, 40, 46))
    rr = random.Random(9)
    for k in range(7):
        x = cx + rr.uniform(-0.55, 0.55) * s
        y = cy + rr.uniform(-0.75, -0.3) * s
        d.ellipse([x - 0.24 * s, y - 0.2 * s, x + 0.24 * s, y + 0.2 * s], fill=(232, 190, 92))
        for g in range(3):
            d.line([(x - 0.18 * s, y - 0.12 * s + g * 0.12 * s), (x + 0.18 * s, y - 0.12 * s + g * 0.12 * s)], fill=(200, 150, 60), width=2)


MENU = [
    # (title, picture, [(line, price)]): lines and prices guessed for the 1995 map
    ("SANDWICHES", _sandwich, [("Chick-fil-A Sandwich", "1.99"), ("Chick-fil-A Deluxe", "2.49"),
                              ("Chargrilled Chicken", "2.59"), ("Chicken Salad Sandwich", "2.29")]),
    ("NUGGETS", _nuggets, [("8 Pack", "1.99"), ("12 Pack", "2.89"), ("Chick-n-Strips 4 ct", "2.69"),
                           ("Hearty Chicken Soup", "1.39")]),
    ("SIDES", _fries, [("Waffle Potato Fries", ".89 / 1.09"), ("Cole Slaw", ".89"),
                       ("Carrot & Raisin Salad", ".89"), ("Tossed Salad", "1.29")]),
    ("LEMONADE", _lemonade, [("Fresh Lemonade", ".89 / 1.09 / 1.29"), ("Iced Tea", ".89 / 1.09"),
                             ("Soft Drinks", ".89 / 1.09"), ("Lemon Pie  ·  Icedream", "1.19 / .79")]),
]


def menu():
    """Four backlit panels, 1.2 x 0.6 m each, in one 2048 x 256 strip (512 px a panel):
    dark brown, a food picture on the left half, white lines and prices (15.5 s)."""
    PW, H = 512, 256
    im = Image.new("RGB", (PW * 4, H), (34, 22, 16))
    d = ImageDraw.Draw(im)
    ft = font(BOLD, 30)
    fl = font(SANS, 19)
    for k, (title, pic, lines) in enumerate(MENU):
        x0 = k * PW
        d.rectangle([x0 + 4, 4, x0 + PW - 5, H - 5], fill=(46, 30, 22))
        # the picture: a soft-lit "photo" on a warm ground
        ph = Image.new("RGB", (200, 200), (94, 60, 36))
        pd = ImageDraw.Draw(ph)
        pd.ellipse([10, 120, 190, 196], fill=(70, 44, 28))
        pic(pd, 100, 110, 60)
        ph = ph.filter(ImageFilter.GaussianBlur(1.0))
        im.paste(ph, (x0 + 20, 28))
        d.text((x0 + 236, 26), title, font=ft, fill=(255, 248, 232))
        d.line([(x0 + 236, 64), (x0 + PW - 20, 64)], fill=(200, 60, 60), width=3)
        for j, (ln, pr) in enumerate(lines):
            y = 80 + j * 40
            d.text((x0 + 236, y), ln, font=fl, fill=(250, 244, 230))
            w = d.textlength(pr, font=fl)
            d.text((x0 + PW - 22 - w, y + 20), pr, font=fl, fill=(255, 220, 120))
    save(im, "menu")


def tray_liner():
    """The paper on the counter's register shelf and the condiment island's label panels:
    cream plates with dark brown lettering."""
    im = Image.new("RGB", (512, 128), (232, 224, 204))
    d = ImageDraw.Draw(im)
    f = font(BOLD, 34)
    for k, s in enumerate(["NAPKINS", "STRAWS", "SAUCES", "THANK YOU"]):
        x0 = k * 128
        d.rectangle([x0 + 4, 4, x0 + 123, 123], outline=(70, 46, 30), width=4)
        ff = f if len(s) < 7 else font(BOLD, 22)
        w = d.textlength(s, font=ff)
        d.text((x0 + 64 - w / 2, 46), s, font=ff, fill=(70, 46, 30))
    save(im, "labels")


if __name__ == "__main__":
    wallpaper(); quarry(); vinyl(); prints(); menu(); tray_liner()
    print("wrote", sorted(os.listdir(OUT)))
