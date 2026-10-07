"""Textures for the Wave 4 clothing stores (tools/stores/apparel/more.gd): Lerner Shop,
The Limited, Gadzooks, Lane Bryant and Miller's Outpost, written to tex/a2/*.png.

Sources (design/storefronts/lerner.md, limited.md, gadzooks.md, lane-bryant.md,
millers-outpost.md): the 1993 Hammond Square commercial, the 1992 Pecanland Mall opening-day
video and the Gadzooks photo slideshow Steven pointed to. Every card is generic; the only
names are the stores' own.
  python3 tools/stores/apparel/paint_more.py   (from the project folder)
"""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "kay_bee"))
import paint_store as kb   # noqa: E402

OUT = os.path.join(HERE, "..", "..", "..", "tex", "a2")
os.makedirs(OUT, exist_ok=True)
BOLD = kb.BOLD
SERIF_BI = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-BoldItalic.ttf"
SS = 2


def save(im, name, colors=0):
    im = im.convert("RGB")
    if colors:
        im = im.quantize(colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(os.path.join(OUT, name + ".png"), optimize=True)


def cards():
    """1024 x 1024, 4 x 4 cells of 256 px (sale cards for hanging and for stands):
    row 0 Lerner (purple/pink: '$15', 'SALE', 'NEW ARRIVALS', '2 for $25'),
    row 1 The Limited ('1/2 PRICE', 'NEW', '$19', 'SALE'),
    row 2 Gadzooks ('SALE', '$9.99', 'TEES $10', 'NEW STUFF'),
    row 3 Lane Bryant and Miller's Outpost ('NEW ARRIVALS', 'SALE', 'JEANS $19.99', '25% OFF')."""
    N = 1024 * SS
    c = N // 4
    im = Image.new("RGB", (N, N), (0, 0, 0))
    d = ImageDraw.Draw(im)
    spec = [
        [((120, 40, 120), (255, 255, 255), "$15", ""), ((230, 70, 140), (255, 255, 255), "SALE", ""), ((250, 250, 246), (120, 40, 120), "NEW", "ARRIVALS"), ((120, 40, 120), (255, 220, 240), "2 for", "$25")],
        [((250, 250, 246), (20, 20, 24), "1/2", "PRICE"), ((20, 20, 24), (255, 255, 255), "NEW", ""), ((250, 250, 246), (180, 30, 40), "$19", ""), ((180, 30, 40), (255, 255, 255), "SALE", "")],
        [((20, 20, 24), (255, 40, 60), "SALE", ""), ((255, 220, 40), (20, 20, 24), "$9.99", ""), ((40, 90, 200), (255, 255, 255), "TEES", "$10"), ((255, 40, 60), (255, 255, 255), "NEW", "STUFF")],
        [((250, 250, 246), (70, 40, 110), "NEW", "ARRIVALS"), ((150, 30, 40), (255, 255, 255), "SALE", ""), ((110, 70, 40), (255, 240, 200), "JEANS", "$19.99"), ((240, 200, 60), (110, 50, 20), "25%", "OFF")],
    ]
    for j, row in enumerate(spec):
        for i, (bg, fg, a, b2) in enumerate(row):
            x0, y0 = i * c, j * c
            d.rectangle([x0, y0, x0 + c, y0 + c], fill=bg)
            d.rectangle([x0 + 6 * SS, y0 + 6 * SS, x0 + c - 6 * SS, y0 + c - 6 * SS], outline=fg, width=3 * SS)
            if b2:
                kb.fit_text(d, a, (x0 + 22 * SS, y0 + 24 * SS, x0 + c - 22 * SS, y0 + c * 0.5), BOLD, fg)
                kb.fit_text(d, b2, (x0 + 22 * SS, y0 + c * 0.54, x0 + c - 22 * SS, y0 + c - 24 * SS), BOLD, fg)
            else:
                kb.fit_text(d, a, (x0 + 24 * SS, y0 + 40 * SS, x0 + c - 24 * SS, y0 + c - 40 * SS), BOLD, fg)
    im = im.resize((1024, 1024), Image.LANCZOS)
    save(kb.grain(im, 1.5, 61), "cards", 96)


def gz_tile():
    """Gadzooks' black square tile with light grout (slideshow 0:02, 0:16): 0.6 m square,
    four 15 cm tiles a side."""
    N = 256
    a = np.zeros((N, N, 3), np.float32) + 22
    a += kb.noise(N, N, 2, 62, blur=3)[..., None]
    for k in range(4):
        p = k * N // 4
        a[p:p + 4, :] = 196
        a[:, p:p + 4] = 196
    # a glaze highlight in each tile
    for j in range(4):
        for i in range(4):
            a[j * 64 + 10:j * 64 + 14, i * 64 + 10:i * 64 + 40] += 30
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "gz_tile", 32)


def checker():
    """Red-and-white checker vinyl (slideshow 0:36, 0:42): 0.61 m square, four 12 in tiles."""
    N = 256
    a = np.zeros((N, N, 3), np.float32)
    h = N // 2
    a[:h, :h] = [236, 234, 228]; a[h:, h:] = [236, 234, 228]
    a[:h, h:] = [196, 26, 36]; a[h:, :h] = [196, 26, 36]
    a += kb.noise(N, N, 3, 63, blur=1)[..., None]
    a[:, :1] -= 30; a[:1, :] -= 30; a[:, h - 1:h] -= 30; a[h - 1:h, :] -= 30
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "checker", 16)


def gz_ceiling():
    """Gadzooks' ceiling: dark panels in a red grid (slideshow 0:36), one 2 x 4 ft panel."""
    W, H = 128, 256
    a = np.zeros((H, W, 3), np.float32) + 34
    a += kb.noise(W, H, 2, 64)[..., None]
    a[:5, :] = [200, 24, 36]; a[-5:, :] = [200, 24, 36]; a[:, :5] = [200, 24, 36]; a[:, -5:] = [200, 24, 36]
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "gz_ceiling", 16)


def carpet(name, rgb, seed):
    N = 512
    a = np.zeros((N, N, 3), np.float32) + np.array(rgb, np.float32)
    a *= (1 + kb.noise(N, N, 0.08, seed))[..., None]
    a += kb.noise(N, N, 3, seed + 1, blur=12)[..., None]
    yy = np.arange(N)[:, None]
    a *= (1 + 0.03 * np.sin(yy * math.tau / 4.0))[..., None]
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), name, 64)


def capsule():
    """The Limited's sign face: a black capsule with the name in thin white script-like
    neon tubes drawn on it is done in 3D; this is the black face with a faint sheen band."""
    W, H = 512, 128
    a = np.zeros((H, W, 3), np.float32) + 16
    a[10:18] += 26
    a += kb.noise(W, H, 1.5, 65)[..., None]
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "capsule", 16)


if __name__ == "__main__":
    cards(); gz_tile(); checker(); gz_ceiling(); capsule()
    carpet("carpet_mauve", (150, 118, 128), 66)
    carpet("carpet_grey", (110, 110, 114), 68)
    carpet("carpet_teal", (60, 96, 100), 70)
    print("wrote tex/a2/*.png")
