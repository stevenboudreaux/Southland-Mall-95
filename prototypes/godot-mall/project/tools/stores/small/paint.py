"""Textures for the Wave 5 small shops (tools/stores/small/store.gd): Coach House Gifts, GNC,
MasterCuts, Wicks 'N' Sticks and Chick-fil-A, written to tex/sm/*.png, plus two stock sheets
(gifts, candles) for the media kit's stock rows in tex/md/.

Fronts follow the Southland facade records (from Steven's photos) and the 1993 Hammond
Square commercial; insides are period types. Every package, poster and menu line is
invented; the only names are the stores' own.
  python3 tools/stores/small/paint.py   (from the project folder)
"""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "kay_bee"))
sys.path.insert(0, os.path.join(HERE, "..", "media"))
import paint_store as kb   # noqa: E402
import paint as md         # noqa: E402

OUT = os.path.join(HERE, "..", "..", "..", "tex", "sm")
MD_OUT = os.path.join(HERE, "..", "..", "..", "tex", "md")
os.makedirs(OUT, exist_ok=True)
BOLD = kb.BOLD
SS = 2


def save(im, name, colors=0, out=OUT):
    im = im.convert("RGB")
    if colors:
        im = im.quantize(colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(os.path.join(out, name + ".png"), optimize=True)


def stone():
    """GNC's honed stone tile portal: 0.6 m square, four 30 cm tiles, warm beige."""
    N = 256
    a = np.zeros((N, N, 3), np.float32)
    r = np.random.default_rng(81)
    for j in range(2):
        for i in range(2):
            base = np.array([206, 192, 168], np.float32) + r.uniform(-8, 8)
            t = np.zeros((N // 2, N // 2, 3), np.float32) + base
            t += kb.noise(N // 2, N // 2, 6, 82 + i + 2 * j, blur=3)[..., None]
            a[j * N // 2:(j + 1) * N // 2, i * N // 2:(i + 1) * N // 2] = t
    a[:, :2] -= 40; a[:2, :] -= 40; a[:, N // 2 - 1:N // 2 + 1] -= 40; a[N // 2 - 1:N // 2 + 1, :] -= 40
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "stone", 48)


def terrazzo():
    """MasterCuts' band of sea-green terrazzo with two brass lines: 1024 x 128 = 4 m x 0.5 m."""
    W, H = 1024, 128
    a = np.zeros((H, W, 3), np.float32) + np.array([70, 140, 128], np.float32)
    r = np.random.default_rng(83)
    chips = r.random((H, W))
    a[chips < 0.08] += np.array([60, 60, 60], np.float32)
    a[chips > 0.95] -= np.array([40, 50, 40], np.float32)
    a += kb.noise(W, H, 4, 84, blur=1)[..., None]
    for y in (14, 110):
        a[y:y + 5] = [200, 160, 70]
        a[y + 1:y + 2] = [240, 210, 120]
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "terrazzo", 64)


def slat_green():
    """Coach House's sea-green slatwall, 0.6 m square."""
    N = 256
    a = np.zeros((N, N, 3), np.float32) + np.array([96, 170, 156], np.float32)
    a += kb.noise(N, N, 2, 85)[..., None]
    for k in range(8):
        y = k * N // 8
        a[y:y + 3] = [40, 80, 74]
        a[y + 3:y + 5] = [130, 200, 186]
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "slat_green", 32)


def cedar():
    """Wicks 'N' Sticks' dark-stained vertical-groove cedar boards, 0.6 m square."""
    N = 256
    a = np.zeros((N, N, 3), np.float32) + np.array([96, 62, 38], np.float32)
    grain = kb.noise(N, N, 10, 86)
    grain = np.repeat(grain[:1], N, axis=0) * 0.6 + kb.noise(N, N, 4, 87) * 0.4
    a += grain[..., None] * np.array([1, 0.7, 0.45])
    for k in range(0, N, 32):
        a[:, k:k + 3] = [40, 26, 16]
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "cedar", 48)


def tan_diag():
    """Chick-fil-A's tan tile set on the diagonal, 0.6 m square."""
    N = 256
    im = Image.new("RGB", (N, N), (204, 176, 132))
    d = ImageDraw.Draw(im)
    for k in range(-N, 2 * N, 64):
        d.line([k, 0, k + N, N], fill=(150, 124, 90), width=3)
        d.line([k, N, k + N, 0], fill=(150, 124, 90), width=3)
    save(kb.grain(im, 4, 88), "tan_diag", 32)


def stripes():
    """Chick-fil-A's dining-room wallpaper (Hammond 19.2 s): cream with fine stripes, 0.6 m."""
    N = 256
    im = Image.new("RGB", (N, N), (236, 228, 206))
    d = ImageDraw.Draw(im)
    for k in range(0, N, 16):
        d.line([k, 0, k, N], fill=(206, 196, 170), width=4)
        d.line([k + 8, 0, k + 8, N], fill=(222, 212, 188), width=1)
    save(kb.grain(im, 1.5, 89), "stripes", 32)


def cards():
    """1024 x 1024, 4 x 4 cells: row 0 GNC (GOLD CARD, SALE, VITAMINS, PROTEIN), row 1
    MasterCuts (HAIRCUT $8, PERMS, WALK-INS WELCOME, a style poster), row 2 Coach House
    (GIFTS, CARDS, COLLECTIBLES, SALE), row 3 Chick-fil-A menu panels (scribbled lines)."""
    N = 1024 * SS
    c = N // 4
    im = Image.new("RGB", (N, N), (0, 0, 0))
    d = ImageDraw.Draw(im)
    rng = random.Random(90)
    spec = [
        [((200, 20, 30), (255, 255, 255), "GOLD", "CARD"), ((250, 250, 246), (200, 20, 30), "SALE", ""), ((20, 90, 60), (255, 255, 255), "VITA", "MINS"), ((240, 200, 40), (20, 20, 24), "PRO", "TEIN")],
        [((20, 20, 24), (255, 255, 255), "CUTS", "$8"), ((70, 140, 128), (255, 255, 255), "PERMS", ""), ((250, 250, 246), (20, 20, 24), "WALK-INS", "WELCOME"), None],
        [((110, 30, 60), (255, 240, 220), "GIFTS", ""), ((70, 140, 128), (255, 255, 255), "CARDS", ""), ((250, 250, 246), (60, 40, 30), "COLLECT", "IBLES"), ((200, 30, 40), (255, 255, 255), "SALE", "")],
    ]
    for j, row in enumerate(spec):
        for i, cell in enumerate(row):
            x0, y0 = i * c, j * c
            if cell is None:
                # a style poster: a profile with a big shape of hair (invented)
                d.rectangle([x0, y0, x0 + c, y0 + c], fill=(220, 210, 200))
                d.ellipse([x0 + c * 0.25, y0 + c * 0.15, x0 + c * 0.75, y0 + c * 0.65], fill=(90, 50, 30))
                d.ellipse([x0 + c * 0.35, y0 + c * 0.3, x0 + c * 0.65, y0 + c * 0.7], fill=(230, 190, 160))
                d.rectangle([x0 + c * 0.42, y0 + c * 0.68, x0 + c * 0.58, y0 + c * 0.85], fill=(230, 190, 160))
                d.rectangle([x0 + c * 0.2, y0 + c * 0.82, x0 + c * 0.8, y0 + c], fill=(40, 40, 44))
                continue
            bg, fg, a, b2 = cell
            d.rectangle([x0, y0, x0 + c, y0 + c], fill=bg)
            if b2:
                kb.fit_text(d, a, (x0 + 22 * SS, y0 + 24 * SS, x0 + c - 22 * SS, y0 + c * 0.5), BOLD, fg)
                kb.fit_text(d, b2, (x0 + 22 * SS, y0 + c * 0.54, x0 + c - 22 * SS, y0 + c - 24 * SS), BOLD, fg)
            else:
                kb.fit_text(d, a, (x0 + 24 * SS, y0 + 40 * SS, x0 + c - 24 * SS, y0 + c - 40 * SS), BOLD, fg)
    f = ImageFont.truetype(BOLD, 18 * SS)
    for i in range(4):
        x0, y0 = i * c, 3 * c
        d.rectangle([x0, y0, x0 + c, y0 + c], fill=(150, 20, 34))
        d.rectangle([x0 + 8 * SS, y0 + 8 * SS, x0 + c - 8 * SS, y0 + c * 0.42], fill=(250, 244, 230))
        md.cover_art(d, x0 + 12 * SS, y0 + 12 * SS, c - 24 * SS, c * 0.42 - 16 * SS, rng, dark=(120, 70, 40))
        for k in range(5):
            y = y0 + c * 0.47 + k * 26 * SS
            kb.scribble(d, x0 + 14 * SS, y + 4 * SS, rng.uniform(100, 150) * SS, 12 * SS, (255, 240, 220), rng)
            d.text((x0 + c - 70 * SS, y), "%d.%02d" % (rng.randint(1, 3), rng.choice([9, 19, 39, 59, 89, 99])), font=f, fill=(255, 230, 120))
    im = im.resize((1024, 1024), Image.LANCZOS)
    save(kb.grain(im, 1.5, 91), "cards", 96)


def sm_item(d, kind, x0, y0, w, h, rng):
    if kind == "gift":
        k = rng.choice(["mug", "frame", "figure", "box", "jar"])
        cx = x0 + w / 2
        if k == "mug":
            col = rng.choice([(250, 250, 246), (200, 40, 60), (60, 110, 180), (240, 200, 60)])
            d.rounded_rectangle([x0 + w * 0.15, y0 + h * 0.3, x0 + w * 0.75, y0 + h], radius=w * 0.08, fill=col)
            d.arc([x0 + w * 0.62, y0 + h * 0.45, x0 + w * 0.95, y0 + h * 0.85], 270, 90, fill=col, width=max(2, int(w * 0.08)))
            d.ellipse([cx - w * 0.12, y0 + h * 0.5, cx + w * 0.08, y0 + h * 0.75], fill=rng.choice(md.PAL))
        elif k == "frame":
            d.rectangle([x0 + w * 0.1, y0 + h * 0.1, x0 + w * 0.9, y0 + h], fill=rng.choice([(200, 170, 80), (40, 30, 24), (240, 240, 236)]))
            md.cover_art(d, x0 + w * 0.2, y0 + h * 0.2, w * 0.6, h * 0.7, rng)
        elif k == "figure":
            col = rng.choice([(240, 236, 226), (200, 190, 170), (180, 200, 220)])
            d.ellipse([cx - w * 0.12, y0 + h * 0.05, cx + w * 0.12, y0 + h * 0.3], fill=col)
            d.polygon([(cx - w * 0.2, y0 + h * 0.3), (cx + w * 0.2, y0 + h * 0.3), (cx + w * 0.3, y0 + h), (cx - w * 0.3, y0 + h)], fill=col)
        elif k == "box":
            d.rectangle([x0 + w * 0.05, y0 + h * 0.4, x0 + w * 0.95, y0 + h], fill=rng.choice(md.PAL))
            d.rectangle([x0 + w * 0.45, y0 + h * 0.4, x0 + w * 0.55, y0 + h], fill=(250, 220, 80))
        else:
            d.rounded_rectangle([x0 + w * 0.2, y0 + h * 0.2, x0 + w * 0.8, y0 + h], radius=w * 0.1, fill=(200, 220, 230))
            d.rectangle([x0 + w * 0.25, y0 + h * 0.1, x0 + w * 0.75, y0 + h * 0.22], fill=(180, 140, 80))
    elif kind == "candle":
        k = rng.choice(["pillar", "jar", "taper", "carved"])
        cx = x0 + w / 2
        col = rng.choice([(250, 246, 236), (200, 40, 50), (240, 200, 90), (130, 180, 120), (180, 140, 200), (240, 150, 60), (120, 160, 220)])
        if k == "pillar":
            d.rectangle([x0 + w * 0.15, y0 + h * 0.25, x0 + w * 0.85, y0 + h], fill=col)
            d.line([cx, y0 + h * 0.25, cx, y0 + h * 0.15], fill=(30, 30, 30), width=2)
        elif k == "jar":
            d.rounded_rectangle([x0 + w * 0.12, y0 + h * 0.35, x0 + w * 0.88, y0 + h], radius=w * 0.15, fill=tuple(int(v * 0.85) for v in col))
            d.rectangle([x0 + w * 0.2, y0 + h * 0.28, x0 + w * 0.8, y0 + h * 0.38], fill=(200, 180, 120))
            d.rectangle([x0 + w * 0.25, y0 + h * 0.55, x0 + w * 0.75, y0 + h * 0.8], fill=(250, 246, 236))
        elif k == "taper":
            for j in range(3):
                xx = x0 + w * (0.25 + j * 0.25)
                d.rectangle([xx - w * 0.04, y0 + h * 0.1, xx + w * 0.04, y0 + h], fill=col)
        else:
            d.polygon([(x0 + w * 0.2, y0 + h), (x0 + w * 0.8, y0 + h), (x0 + w * 0.65, y0 + h * 0.15), (x0 + w * 0.35, y0 + h * 0.15)], fill=col)
            for j in range(4):
                yy = y0 + h * (0.3 + j * 0.17)
                d.arc([x0 + w * 0.25, yy - h * 0.06, x0 + w * 0.75, yy + h * 0.06], 0, 180, fill=rng.choice(md.PAL), width=max(2, int(w * 0.06)))


def sm_stock(sheet, kind, seed, size_w, size_h):
    rows, rh_m = 8, 0.305
    W, H = 512 * SS, 1024 * SS
    rh = H // rows
    rng = random.Random(seed)
    im = Image.new("RGB", (W, H), md.GAP)
    d = ImageDraw.Draw(im)
    for r in range(rows):
        ytop = r * rh
        x = 2 * SS
        while x < W - 30 * SS:
            w = int(rng.uniform(*size_w) * md.PXM * SS)
            h = int(min(rng.uniform(*size_h) * md.PXM * SS, rh - 4 * SS))
            if x + w > W - 2 * SS:
                break
            sm_item(d, kind, x, ytop + rh - h - 2 * SS, w, h, random.Random(rng.randint(0, 10 ** 9)))
            x += w + rng.randint(2, 8) * SS
    im = im.resize((512, 1024), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32)
    rhp = 1024 // rows
    for r in range(rows):
        a[r * rhp:r * rhp + 25] *= np.linspace(0.6, 1.0, 25)[:, None, None]
    a += kb.noise(512, 1024, 2.5, seed)[..., None]
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "stock_" + sheet, 192, out=MD_OUT)


if __name__ == "__main__":
    stone(); terrazzo(); slat_green(); cedar(); tan_diag(); stripes(); cards()
    sm_stock("gifts", "gift", 700, (0.08, 0.16), (0.10, 0.22))
    sm_stock("candles", "candle", 701, (0.07, 0.13), (0.10, 0.25))
    print("wrote tex/sm/*.png and tex/md/stock_{gifts,candles}.png")
