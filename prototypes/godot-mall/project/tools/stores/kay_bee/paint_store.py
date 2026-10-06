"""Textures for Kay-Bee Toys (store.gd), written to tex/kb/*.png.

Front: Steven's photo of the Southland store (white wall tile with scattered red and
blue accent tiles over a royal-blue fascia with red letters). Inside: a 1993 home video
of a Kay-Bee in Columbus, Georgia (design/storefronts/kay-bee-toys.md): tan carpet,
white gondola shelving packed with boxed toys, teal department signs with lime
lettering, orange price cards, yellow sale signs.

Every package design here is original: generic toy shapes and scribbled "titles",
no real brand, logo, character or box art.
  python3 tools/stores/kay_bee/paint_store.py   (from the project folder)
"""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "..", "tex", "kb")
os.makedirs(OUT, exist_ok=True)
BOLD = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"   # a Helvetica-type grotesque, right for the early 1990s
SS = 2   # supersampling for the drawn sheets


def save(im, name, colors=0):
    im = im.convert("RGBA" if im.mode == "RGBA" else "RGB")
    if colors:
        im = im.quantize(colors, method=Image.Quantize.FASTOCTREE if im.mode == "RGBA" else Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(os.path.join(OUT, name + ".png"), optimize=True)


def noise(w, h, amp, seed, blur=0):
    r = np.random.default_rng(seed)
    a = r.normal(0, amp, (h, w)).astype(np.float32)
    if blur:
        im = Image.fromarray(np.clip(a * 4 + 128, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(blur))
        a = (np.asarray(im).astype(np.float32) - 128) / 4
    return a


def grain(im, amp, seed, blur=0):
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    a += noise(a.shape[1], a.shape[0], amp, seed, blur)[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


# ------------------------------------------------------------------ the front
def tile_wall():
    """6 m x 1.2 m of the mall-side wall over the fascia: white 15 cm glazed tile, light
    grout, with small red and blue accent tiles scattered as in the photo."""
    W, H = 1280, 256
    cols, rows = 40, 8
    rng = random.Random(18)
    img = np.zeros((H, W, 3), np.float32)
    accents = {}
    # the photo: single accents a few tiles apart, alternating red and blue, in loose rows
    for k, (cx, cy) in enumerate([(2, 2), (5, 5), (9, 2), (13, 1), (16, 5), (19, 2), (23, 5), (26, 1), (29, 2), (33, 5), (36, 2), (38, 6), (7, 6), (21, 6)]):
        accents[(cx, cy)] = [(196, 34, 44), (36, 58, 150)][k % 2]
    for j in range(rows):
        for i in range(cols):
            x0, x1 = round(i * W / cols), round((i + 1) * W / cols)
            y0, y1 = round(j * H / rows), round((j + 1) * H / rows)
            c = np.array(accents.get((i, j), (236, 236, 232)), np.float32)
            img[y0:y1, x0:x1] = c + rng.uniform(-4, 4)
    img += noise(W, H, 1.5, 4)[..., None]
    for i in range(cols + 1):
        x = min(W - 1, round(i * W / cols))
        img[:, max(0, x - 1):x + 1] = [200, 200, 196]
    for j in range(rows + 1):
        y = min(H - 1, round(j * H / rows))
        img[max(0, y - 1):y + 1, :] = [200, 200, 196]
    save(Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)), "tile_wall", 64)


def louver():
    """The lit ceiling strip just inside the entrance (the bright slatted band under the fascia
    in the photo): white fluorescent light behind blades, 0.6 m x 0.6 m."""
    N = 128
    img = np.full((N, N, 3), 250, np.float32)
    for k in range(8):
        y = int(k * N / 8)
        img[y:y + 4, :] = [150, 150, 146]
        img[y + 4:y + 7, :] = [215, 215, 210]
    save(Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)), "louver", 16)


# ------------------------------------------------------------------ the room
def carpet():
    """1 m x 1 m, seamless: the video's tan level-loop carpet, a little mottled."""
    N = 512
    a = np.zeros((N, N, 3), np.float32) + np.array([160, 142, 106], np.float32)
    a *= (1 + noise(N, N, 0.09, 11))[..., None]
    a += noise(N, N, 3, 12, blur=10)[..., None]
    # loop rows
    yy = np.arange(N)[:, None]
    a *= (1 + 0.035 * np.sin(yy * math.tau / 4.0))[..., None]
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "carpet", 64)


def ceiling():
    """One 2 x 4 ft lay-in panel (0.61 x 1.22 m): fissured white tile in a white T-grid."""
    W, H = 128, 256
    a = np.full((H, W, 3), 232, np.float32)
    r = np.random.default_rng(5)
    for _ in range(900):
        x, y = r.integers(2, W - 2), r.integers(2, H - 2)
        a[y:y + r.integers(1, 3), x:x + r.integers(1, 4)] -= r.uniform(10, 40)
    a += noise(W, H, 2, 6)[..., None]
    a[:2, :] = 206; a[-2:, :] = 206; a[:, :2] = 206; a[:, -2:] = 206
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "ceiling", 32)


def troffer():
    """A 2 x 4 ft fluorescent troffer with a prismatic lens: two tube glows under the lens."""
    W, H = 128, 256
    xx = np.arange(W)[None, :] / W
    glow = 0.80 + 0.20 * np.exp(-((xx - 0.3) / 0.11) ** 2) + 0.20 * np.exp(-((xx - 0.7) / 0.11) ** 2)
    a = np.repeat(np.clip(glow, 0, 1), H, axis=0)[..., None] * np.array([255, 253, 244], np.float32)
    yy, x2 = np.mgrid[0:H, 0:W]
    a *= (0.95 + 0.05 * (((x2 // 3) + (yy // 3)) % 2))[..., None]
    a[:5, :] = 196; a[-5:, :] = 196; a[:, :5] = 196; a[:, -5:] = 196
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "troffer", 32)


def pegboard():
    """White pegboard back panel, 0.305 m square tile (1-inch hole pitch)."""
    N = 192
    a = np.full((N, N, 3), 226, np.float32)
    a += noise(N, N, 1.5, 8)[..., None]
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    for j in range(12):
        for i in range(12):
            cx, cy = i * 16 + 8, j * 16 + 8
            d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(92, 90, 86))
    save(im, "pegboard", 16)


def shelf_edge():
    """A shelf's front lip, 1.22 m x 4 cm: white enamel with a ticket strip of price labels."""
    W, H = 512, 16
    im = Image.new("RGB", (W, H), (238, 238, 234))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 3, W, 13], fill=(250, 250, 246))
    rng = random.Random(3)
    x = 10
    while x < W - 40:
        w = rng.choice([26, 30, 34])
        c = rng.choice([(250, 250, 250), (250, 236, 120), (250, 250, 250), (246, 150, 60)])
        d.rectangle([x, 3, x + w, 13], fill=c, outline=(170, 170, 166))
        d.line([x + 3, 6, x + w - 9, 6], fill=(60, 60, 60))
        d.rectangle([x + w - 8, 8, x + w - 3, 11], fill=(40, 40, 40))
        x += w + rng.randint(30, 90)
    d.line([0, 0, W, 0], fill=(206, 206, 202)); d.line([0, H - 1, W, H - 1], fill=(170, 170, 166))
    save(im, "shelf_edge", 32)


# ------------------------------------------------------------------ merchandise
ROW_H = 146          # 7 rows of 512 x 146 px per sheet: each row is one 1.22 m shelf face, 0.35 m tall
GAP = (30, 28, 28)   # the shadowed space between and above packages


def scribble(d, x0, y0, w, h, col, rng, lines=1):
    """A stand-in for a printed title: fat wavy strokes, no letters."""
    for k in range(lines):
        yy = y0 + h * (k + 0.5) / lines
        pts = []
        n = max(4, int(w / (h / lines * 0.7)))
        for i in range(n + 1):
            pts.append((x0 + w * i / n, yy + (rng.uniform(-1, 1)) * h / lines * 0.32))
        d.line(pts, fill=col, width=max(2, int(h / lines * 0.34)), joint="curve")


def burst(d, cx, cy, r, col, rng, text_col=None):
    pts = []
    n = 12
    for i in range(n * 2):
        rr = r if i % 2 == 0 else r * 0.68
        a = math.pi * i / n + 0.2
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=col)
    if text_col:
        d.line([cx - r * 0.35, cy, cx + r * 0.35, cy], fill=text_col, width=max(2, int(r * 0.22)))


def motif(d, kind, x0, y0, w, h, rng, pal):
    """A generic toy drawn in the package's window or on its face."""
    cx, cy = x0 + w / 2, y0 + h / 2
    s = min(w, h)
    if kind == "doll":
        skin = rng.choice([(238, 196, 160), (232, 184, 150), (150, 100, 70)])
        hair = rng.choice([(240, 214, 110), (90, 50, 30), (30, 24, 22), (200, 90, 40)])
        dress = rng.choice(pal)
        hr = s * 0.16
        d.ellipse([cx - hr * 1.5, y0 + h * 0.06, cx + hr * 1.5, y0 + h * 0.06 + hr * 3.4], fill=hair)
        d.ellipse([cx - hr, y0 + h * 0.10, cx + hr, y0 + h * 0.10 + hr * 2], fill=skin)
        top = y0 + h * 0.10 + hr * 2
        d.polygon([(cx - hr * 0.8, top), (cx + hr * 0.8, top), (cx + s * 0.34, y0 + h * 0.96), (cx - s * 0.34, y0 + h * 0.96)], fill=dress)
        d.line([cx - hr * 0.8, top + 2, cx - s * 0.3, top + h * 0.3], fill=skin, width=max(2, int(s * 0.05)))
        d.line([cx + hr * 0.8, top + 2, cx + s * 0.3, top + h * 0.3], fill=skin, width=max(2, int(s * 0.05)))
    elif kind == "figure":
        body = rng.choice(pal)
        skin = rng.choice([(226, 180, 140), (120, 160, 90), (150, 150, 160), (200, 60, 50)])
        hr = s * 0.11
        d.ellipse([cx - hr, y0 + h * 0.05, cx + hr, y0 + h * 0.05 + hr * 2], fill=skin)
        top = y0 + h * 0.05 + hr * 2
        d.polygon([(cx - s * 0.26, top), (cx + s * 0.26, top), (cx + s * 0.13, y0 + h * 0.58), (cx - s * 0.13, y0 + h * 0.58)], fill=body)
        lw = max(3, int(s * 0.10))
        d.line([cx - s * 0.26, top + lw / 2, cx - s * 0.36, y0 + h * 0.5], fill=skin, width=lw)
        d.line([cx + s * 0.26, top + lw / 2, cx + s * 0.36, y0 + h * 0.5], fill=skin, width=lw)
        d.line([cx - s * 0.08, y0 + h * 0.56, cx - s * 0.16, y0 + h * 0.96], fill=body, width=lw)
        d.line([cx + s * 0.08, y0 + h * 0.56, cx + s * 0.16, y0 + h * 0.96], fill=body, width=lw)
    elif kind == "car":
        body = rng.choice(pal)
        bw, bh = w * 0.84, h * 0.30
        by = cy + h * 0.06
        d.rounded_rectangle([cx - bw / 2, by - bh / 2, cx + bw / 2, by + bh / 2], radius=bh * 0.3, fill=body)
        d.polygon([(cx - bw * 0.28, by - bh / 2), (cx - bw * 0.14, by - bh * 1.15), (cx + bw * 0.2, by - bh * 1.15), (cx + bw * 0.34, by - bh / 2)], fill=body)
        d.polygon([(cx - bw * 0.2, by - bh * 0.55), (cx - bw * 0.11, by - bh * 1.0), (cx + bw * 0.17, by - bh * 1.0), (cx + bw * 0.26, by - bh * 0.55)], fill=(170, 210, 230))
        wr = bh * 0.42
        for wx in (cx - bw * 0.28, cx + bw * 0.28):
            d.ellipse([wx - wr, by + bh / 2 - wr * 0.9, wx + wr, by + bh / 2 + wr * 1.1], fill=(20, 20, 22))
            d.ellipse([wx - wr * 0.45, by + bh / 2 - wr * 0.35, wx + wr * 0.45, by + bh / 2 + wr * 0.55], fill=(190, 190, 196))
    elif kind == "truck":
        body = rng.choice(pal)
        bw, bh = w * 0.86, h * 0.36
        by = cy
        d.rectangle([cx - bw / 2, by - bh / 2, cx + bw * 0.16, by + bh / 2], fill=body)
        d.rectangle([cx + bw * 0.18, by - bh * 0.2, cx + bw / 2, by + bh / 2], fill=rng.choice(pal))
        d.rectangle([cx + bw * 0.24, by - bh * 0.1, cx + bw * 0.42, by + bh * 0.12], fill=(170, 210, 230))
        wr = bh * 0.34
        for wx in (cx - bw * 0.32, cx - bw * 0.06, cx + bw * 0.34):
            d.ellipse([wx - wr, by + bh / 2 - wr * 0.7, wx + wr, by + bh / 2 + wr * 1.3], fill=(20, 20, 22))
    elif kind == "ball":
        col = rng.choice([(232, 120, 40), (240, 240, 236), (200, 50, 50), (70, 150, 70), (240, 200, 50)])
        r = s * 0.40
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
        dark = tuple(int(c * 0.35) for c in col)
        d.arc([cx - r, cy - r * 2.2, cx + r, cy], 20, 160, fill=dark, width=max(2, int(r * 0.08)))
        d.line([cx, cy - r, cx, cy + r], fill=dark, width=max(2, int(r * 0.08)))
        d.arc([cx - r, cy, cx + r, cy + r * 2.2], 200, 340, fill=dark, width=max(2, int(r * 0.08)))
    elif kind == "bear":
        fur = rng.choice([(150, 100, 56), (232, 224, 204), (236, 196, 70), (240, 160, 180), (120, 120, 126), (200, 150, 96)])
        dk = tuple(int(c * 0.75) for c in fur)
        r = s * 0.24
        for ex in (-1, 1):
            d.ellipse([cx + ex * r * 0.85 - r * 0.42, cy - s * 0.42, cx + ex * r * 0.85 + r * 0.42, cy - s * 0.42 + r * 0.84], fill=dk)
        d.ellipse([cx - r * 1.3, cy - s * 0.02, cx + r * 1.3, cy + s * 0.5], fill=dk)
        d.ellipse([cx - r, cy - s * 0.36, cx + r, cy - s * 0.36 + r * 2], fill=fur)
        d.ellipse([cx - r * 0.42, cy - s * 0.14, cx + r * 0.42, cy + s * 0.03], fill=tuple(min(255, c + 30) for c in fur))
        for ex in (-1, 1):
            d.ellipse([cx + ex * r * 0.4 - 2, cy - s * 0.22, cx + ex * r * 0.4 + 2, cy - s * 0.22 + 4], fill=(20, 16, 14))
        d.ellipse([cx - 3, cy - s * 0.11, cx + 3, cy - s * 0.07], fill=(20, 16, 14))
    elif kind == "blocks":
        n = 3
        bs = s * 0.28
        for k in range(n):
            bx = cx - bs * 1.5 + k * bs
            by = cy + bs * 0.4 - (bs if k == 1 else 0) * 0.0
            d.rectangle([bx, by, bx + bs * 0.94, by + bs * 0.94], fill=rng.choice(pal))
        d.rectangle([cx - bs * 0.5, cy - bs * 0.58, cx + bs * 0.44, cy + bs * 0.36], fill=rng.choice(pal))
        d.polygon([(cx - bs * 0.5, cy - bs * 0.62), (cx, cy - bs * 1.2), (cx + bs * 0.46, cy - bs * 0.62)], fill=rng.choice(pal))
    elif kind == "rings":
        cols = [(220, 50, 50), (240, 150, 40), (240, 210, 50), (70, 170, 80), (50, 110, 200)]
        for k in range(5):
            rw = s * (0.46 - k * 0.06)
            yy = y0 + h * 0.86 - k * h * 0.15
            d.ellipse([cx - rw, yy - h * 0.09, cx + rw, yy + h * 0.09], fill=cols[k])
    elif kind == "robot":
        body = rng.choice(pal)
        d.rectangle([cx - s * 0.22, y0 + h * 0.3, cx + s * 0.22, y0 + h * 0.72], fill=body)
        d.rectangle([cx - s * 0.14, y0 + h * 0.08, cx + s * 0.14, y0 + h * 0.28], fill=(180, 184, 190))
        d.rectangle([cx - s * 0.10, y0 + h * 0.14, cx + s * 0.10, y0 + h * 0.19], fill=(240, 60, 40))
        for ex in (-1, 1):
            d.rectangle([cx + ex * s * 0.3 - s * 0.05, y0 + h * 0.32, cx + ex * s * 0.3 + s * 0.05, y0 + h * 0.66], fill=(150, 154, 160))
            d.rectangle([cx + ex * s * 0.12 - s * 0.07, y0 + h * 0.72, cx + ex * s * 0.12 + s * 0.07, y0 + h * 0.96], fill=(120, 124, 130))
    elif kind == "dino":
        col = rng.choice([(70, 140, 70), (150, 90, 50), (120, 80, 150)])
        d.ellipse([cx - s * 0.3, cy - s * 0.1, cx + s * 0.22, cy + s * 0.3], fill=col)
        d.polygon([(cx - s * 0.22, cy + s * 0.1), (cx - s * 0.48, cy + s * 0.34), (cx - s * 0.2, cy + s * 0.26)], fill=col)
        d.polygon([(cx + s * 0.08, cy), (cx + s * 0.2, cy - s * 0.36), (cx + s * 0.3, cy - s * 0.3), (cx + s * 0.22, cy + s * 0.08)], fill=col)
        d.ellipse([cx + s * 0.14, cy - s * 0.46, cx + s * 0.46, cy - s * 0.26], fill=col)
        for lx in (-0.12, 0.1):
            d.rectangle([cx + s * lx, cy + s * 0.22, cx + s * (lx + 0.09), cy + s * 0.46], fill=col)
    elif kind == "plane":
        col = rng.choice(pal)
        d.ellipse([cx - s * 0.44, cy - s * 0.08, cx + s * 0.44, cy + s * 0.08], fill=col)
        d.polygon([(cx - s * 0.08, cy), (cx + s * 0.1, cy), (cx - s * 0.12, cy + s * 0.42), (cx - s * 0.22, cy + s * 0.42)], fill=col)
        d.polygon([(cx - s * 0.08, cy), (cx + s * 0.1, cy), (cx - s * 0.06, cy - s * 0.36), (cx - s * 0.16, cy - s * 0.36)], fill=col)
        d.polygon([(cx - s * 0.44, cy), (cx - s * 0.34, cy), (cx - s * 0.46, cy - s * 0.26)], fill=col)
    elif kind == "dots":
        for _ in range(9):
            r = s * rng.uniform(0.06, 0.13)
            px, py = rng.uniform(x0 + r, x0 + w - r), rng.uniform(y0 + r, y0 + h - r)
            d.ellipse([px - r, py - r, px + r, py + r], fill=rng.choice(pal))
    elif kind == "screen":
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=(16, 20, 40))
        for _ in range(7):
            bw_, bh_ = w * rng.uniform(0.08, 0.3), h * rng.uniform(0.08, 0.2)
            px, py = rng.uniform(x0, x0 + w - bw_), rng.uniform(y0 + h * 0.2, y0 + h - bh_)
            d.rectangle([px, py, px + bw_, py + bh_], fill=rng.choice(pal))


def package(d, x0, y0, w, h, style, rng):
    """One package front, drawn bottom-aligned in its slot (x0, y0 = top-left)."""
    pal = style["pal"]
    base = rng.choice(style["base"])
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=base)
    kind = style["kind"]
    lay = style.get("lay", "window")
    accent = rng.choice(pal)
    white = (250, 248, 240)
    if lay == "window":
        # title band on top, a die-cut window with the toy in its tray
        th = h * rng.uniform(0.2, 0.28)
        scribble(d, x0 + w * 0.1, y0 + th * 0.2, w * 0.8, th * 0.6, rng.choice([white, accent, (250, 220, 60)]), rng)
        wx0, wy0, wx1, wy1 = x0 + w * 0.1, y0 + th + h * 0.02, x0 + w * 0.9, y0 + h * 0.92
        inner = tuple(min(255, int(c * 0.55 + 110)) for c in base)
        d.rounded_rectangle([wx0, wy0, wx1, wy1], radius=w * 0.06, fill=inner)
        motif(d, kind, wx0 + 3, wy0 + 3, wx1 - wx0 - 6, wy1 - wy0 - 6, rng, pal)
        # cellophane glare
        d.line([wx0 + w * 0.08, wy1 - 4, wx0 + w * 0.3, wy0 + 4], fill=tuple(min(255, c + 60) for c in inner), width=max(2, int(w * 0.035)))
    elif lay == "card":
        # a blister card: hang hole, art panel on top, the bubble below
        d.ellipse([x0 + w / 2 - 5, y0 + 5, x0 + w / 2 + 5, y0 + 11], fill=GAP)
        scribble(d, x0 + w * 0.12, y0 + h * 0.12, w * 0.76, h * 0.14, rng.choice([white, (250, 220, 60), accent]), rng)
        bx0, by0, bx1, by1 = x0 + w * 0.16, y0 + h * 0.34, x0 + w * 0.84, y0 + h * 0.95
        d.rounded_rectangle([bx0, by0, bx1, by1], radius=w * 0.1, fill=tuple(min(255, int(c * 0.6 + 96)) for c in base))
        motif(d, kind, bx0 + 2, by0 + 2, bx1 - bx0 - 4, by1 - by0 - 4, rng, pal)
        d.line([bx0 + 4, by1 - 6, bx0 + (bx1 - bx0) * 0.3, by0 + 6], fill=(255, 255, 255), width=2)
    elif lay == "photo":
        # a closed box with printed art: big picture, a title band, a side flash
        d.rectangle([x0, y0 + h * 0.62, x0 + w, y0 + h], fill=accent)
        motif(d, kind, x0 + w * 0.08, y0 + h * 0.2, w * 0.84, h * 0.6, rng, pal)
        scribble(d, x0 + w * 0.08, y0 + h * 0.04, w * 0.7, h * 0.16, rng.choice([white, (250, 220, 60)]), rng)
        if rng.random() < 0.6:
            burst(d, x0 + w * 0.82, y0 + h * 0.82, min(w, h) * 0.13, (250, 220, 60), rng, (200, 30, 30))
    elif lay == "stack":
        # flat boxes stacked on their backs: the shopper sees the long edges, a title on each
        n = max(2, int(round(h / (ROW_H * SS * 0.2))))
        for k in range(n):
            ya, yb = y0 + h * k / n, y0 + h * (k + 1) / n
            c = base if k % 2 == 0 else tuple(int(v * 0.9) for v in base)
            d.rectangle([x0, ya, x0 + w, yb - 1], fill=c)
            d.rectangle([x0, ya, x0 + w * 0.22, yb - 1], fill=accent)
            scribble(d, x0 + w * 0.28, ya + (yb - ya) * 0.22, w * 0.5, (yb - ya) * 0.56, white, rng)
            d.ellipse([x0 + w * 0.84, ya + (yb - ya) * 0.2, x0 + w * 0.84 + (yb - ya) * 0.6, yb - (yb - ya) * 0.2], fill=rng.choice(pal))
            d.line([x0, yb - 1, x0 + w, yb - 1], fill=GAP, width=2)
    elif lay == "cart":
        # small video game boxes, two rows high
        n = 2
        for k in range(n):
            ya, yb = y0 + h * k / n + 2, y0 + h * (k + 1) / n - 2
            d.rectangle([x0, ya, x0 + w, yb], fill=base)
            d.rectangle([x0 + w * 0.08, ya + (yb - ya) * 0.3, x0 + w * 0.92, yb - (yb - ya) * 0.08], fill=(16, 20, 40))
            motif(d, "screen", x0 + w * 0.08, ya + (yb - ya) * 0.3, w * 0.84, (yb - ya) * 0.62, rng, pal)
            scribble(d, x0 + w * 0.1, ya + (yb - ya) * 0.06, w * 0.8, (yb - ya) * 0.2, rng.choice([white, (250, 220, 60), (240, 60, 50)]), rng)
    # printed edge and the gap to the next package
    d.rectangle([x0, y0, x0 + w, y0 + h], outline=tuple(int(c * 0.6) for c in base), width=2)


STYLES = {
    # category -> list of product styles; all colours as 1990s packaging ran
    "dolls": [
        {"kind": "doll", "base": [(236, 80, 150), (244, 120, 176), (226, 60, 132)], "pal": [(250, 250, 250), (250, 200, 60), (150, 90, 200), (80, 200, 220)], "w": (56, 70), "h": (0.9, 1.0)},
        {"kind": "doll", "base": [(250, 170, 200), (176, 120, 210)], "pal": [(250, 250, 250), (236, 80, 150), (250, 220, 90)], "w": (70, 92), "h": (0.82, 0.96)},
        {"kind": "bear", "base": [(250, 210, 224), (190, 220, 244)], "pal": [(236, 80, 150), (250, 250, 250)], "w": (84, 100), "h": (0.75, 0.9)},
        {"kind": "dots", "lay": "photo", "base": [(236, 80, 150), (150, 90, 200)], "pal": [(250, 250, 250), (250, 220, 90), (250, 170, 200)], "w": (90, 120), "h": (0.6, 0.8)},
    ],
    "action": [
        {"kind": "figure", "lay": "card", "base": [(20, 30, 90), (150, 24, 30), (16, 16, 20), (30, 90, 50)], "pal": [(220, 40, 40), (240, 200, 40), (60, 90, 200), (40, 40, 44)], "w": (44, 52), "h": (0.84, 0.94)},
        {"kind": "figure", "base": [(16, 16, 20), (24, 40, 110), (90, 30, 110)], "pal": [(220, 40, 40), (240, 200, 40), (120, 130, 140)], "w": (64, 84), "h": (0.9, 1.0)},
        {"kind": "robot", "lay": "photo", "base": [(24, 28, 60), (60, 60, 70)], "pal": [(220, 40, 40), (240, 200, 40), (60, 120, 220)], "w": (90, 124), "h": (0.8, 1.0)},
        {"kind": "dino", "base": [(40, 70, 40), (120, 60, 30)], "pal": [(240, 200, 40), (220, 90, 30)], "w": (84, 110), "h": (0.75, 0.92)},
    ],
    "vehicles": [
        {"kind": "car", "lay": "card", "base": [(240, 200, 40), (220, 50, 40), (40, 80, 190)], "pal": [(220, 40, 40), (40, 80, 190), (240, 240, 240), (30, 30, 30)], "w": (44, 54), "h": (0.6, 0.72)},
        {"kind": "truck", "base": [(240, 200, 40), (250, 130, 30)], "pal": [(220, 40, 40), (40, 80, 190), (250, 250, 250), (60, 150, 70)], "w": (100, 130), "h": (0.7, 0.9)},
        {"kind": "car", "base": [(220, 50, 40), (30, 30, 34), (40, 80, 190)], "pal": [(240, 200, 40), (240, 240, 240), (220, 40, 40)], "w": (86, 110), "h": (0.62, 0.8)},
        {"kind": "plane", "lay": "photo", "base": [(60, 130, 200), (230, 230, 226)], "pal": [(220, 40, 40), (120, 130, 140), (240, 200, 40)], "w": (96, 124), "h": (0.7, 0.9)},
    ],
    "games": [
        {"kind": "dots", "lay": "stack", "base": [(220, 50, 40), (40, 80, 190), (30, 130, 80), (240, 200, 40), (90, 40, 120), (240, 240, 232)], "pal": [(240, 200, 40), (250, 250, 250), (220, 40, 40), (40, 80, 190)], "w": (150, 200), "h": (0.7, 1.0)},
        {"kind": "dots", "lay": "photo", "base": [(40, 80, 190), (220, 50, 40), (30, 130, 80)], "pal": [(240, 200, 40), (250, 250, 250), (240, 120, 40)], "w": (100, 130), "h": (0.8, 1.0)},
    ],
    "video": [
        {"kind": "screen", "lay": "cart", "base": [(30, 30, 34), (120, 124, 130), (70, 30, 100), (20, 40, 110)], "pal": [(220, 40, 40), (240, 200, 40), (60, 200, 90), (60, 120, 240), (250, 250, 250)], "w": (48, 58), "h": (0.94, 1.0)},
        {"kind": "screen", "lay": "photo", "base": [(120, 124, 130), (30, 30, 34)], "pal": [(220, 40, 40), (60, 120, 240), (240, 200, 40)], "w": (110, 150), "h": (0.8, 1.0)},
    ],
    "preschool": [
        {"kind": "rings", "base": [(250, 250, 244), (240, 200, 40), (50, 110, 200)], "pal": [(220, 50, 50), (70, 170, 80), (50, 110, 200), (240, 200, 40)], "w": (70, 90), "h": (0.8, 1.0)},
        {"kind": "blocks", "lay": "photo", "base": [(220, 50, 40), (50, 110, 200), (70, 170, 80)], "pal": [(240, 200, 40), (250, 250, 250), (220, 50, 50), (50, 110, 200)], "w": (100, 130), "h": (0.75, 1.0)},
        {"kind": "truck", "base": [(250, 250, 244), (240, 200, 40)], "pal": [(220, 50, 50), (50, 110, 200), (70, 170, 80)], "w": (100, 124), "h": (0.7, 0.9)},
    ],
    "sports": [
        {"kind": "ball", "base": [(24, 28, 60), (30, 110, 60), (230, 230, 226)], "pal": [(240, 200, 40), (220, 50, 40)], "w": (86, 100), "h": (0.86, 1.0)},
        {"kind": "ball", "lay": "photo", "base": [(220, 50, 40), (40, 80, 190)], "pal": [(240, 200, 40), (250, 250, 250)], "w": (90, 120), "h": (0.7, 0.95)},
        {"kind": "plane", "base": [(240, 200, 40), (60, 170, 200)], "pal": [(220, 50, 40), (250, 250, 250), (60, 60, 200)], "w": (100, 130), "h": (0.6, 0.8)},
    ],
}


def merch(cat, seed):
    """512 x 1024: seven shelf faces. Each row is two 256 px halves (a package edge always
    falls on the middle, where store.gd may step the stock back), facings repeated in
    runs as a stocked shelf has them."""
    W, H = 512 * SS, 1024 * SS
    rh = ROW_H * SS
    rng = random.Random(seed)
    im = Image.new("RGB", (W, H), GAP)
    d = ImageDraw.Draw(im)
    for r in range(7):
        ytop = r * rh
        for half in range(2):
            x = half * 256 * SS + 2 * SS
            xend = (half + 1) * 256 * SS - 2 * SS
            while x < xend - 20 * SS:
                st = rng.choice(STYLES[cat])
                w = rng.randint(*st["w"]) * SS
                hh = int(rh * rng.uniform(*st["h"])) - 3 * SS
                faces = rng.choice([1, 2, 2, 3, 4]) if w < 90 * SS else rng.choice([1, 1, 2])
                srng_seed = rng.randint(0, 10 ** 9)
                for _ in range(faces):
                    if x + w > xend:
                        w2 = xend - x
                        if w2 < 26 * SS:
                            x = xend
                            break
                        w = w2   # the last facing is squeezed in, as on a full shelf
                    package(d, x, ytop + rh - hh - 2 * SS, w - 2 * SS, hh, st, random.Random(srng_seed))
                    x += w
    im = im.resize((512, 1024), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32)
    # the shelf above shades the top of each row; print grain
    for r in range(7):
        y0 = r * ROW_H
        sh = np.linspace(0.62, 1.0, 34)[:, None, None]
        a[y0:y0 + 34] *= sh
    a += noise(512, 1024, 2.5, seed)[..., None]
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "merch_" + cat, 192)


def plush():
    """512 x 512, tiles sideways: a heap of stuffed animals (dump bins, shelf tops)."""
    N = 512 * SS
    rng = random.Random(77)
    im = Image.new("RGB", (N, N), (60, 44, 36))
    d = ImageDraw.Draw(im)
    pal = [(250, 250, 250)]
    pts = [(rng.uniform(0, N), rng.uniform(0, N)) for _ in range(60)]
    pts.sort(key=lambda p: p[1])
    for (x, y) in pts:
        s = rng.uniform(120, 170) * SS / 1.4
        for ox in (-N, 0, N):
            motif(d, "bear", x - s / 2 + ox, y - s / 2, s, s, random.Random(int(x * 7 + y)), pal)
    im = im.resize((512, 512), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32)
    a *= (1 + noise(512, 512, 0.10, 9))[..., None]
    a = np.asarray(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)))
    save(Image.fromarray(a), "plush", 128)


def carton():
    """Plain shipping cartons for the overstock above the shelves: kraft board with a
    tape line and a stencilled label block. 512 x 256 = 1.22 m x 0.6 m, three cartons."""
    W, H = 512, 256
    a = np.zeros((H, W, 3), np.float32) + np.array([176, 140, 96], np.float32)
    a += noise(W, H, 4, 21, blur=3)[..., None]
    a += noise(W, H, 2.5, 22)[..., None]
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    rng = random.Random(4)
    for k, (x0, x1) in enumerate([(0, 170), (170, 342), (342, 512)]):
        d.rectangle([x0, 0, x1 - 1, H - 1], outline=(96, 72, 46), width=2)
        d.rectangle([x0 + 2, H // 2 - 9, x1 - 3, H // 2 + 9], fill=(200, 176, 132))
        lx = x0 + rng.randint(14, 40)
        d.rectangle([lx, 30, lx + 70, 74], fill=(240, 238, 228))
        for j in range(4):
            d.line([lx + 6, 38 + j * 9, lx + rng.randint(36, 62), 38 + j * 9], fill=(40, 40, 40), width=2)
        d.line([x1 - 60, 190, x1 - 20, 190], fill=(60, 44, 30), width=5)
        d.line([x1 - 60, 204, x1 - 34, 204], fill=(60, 44, 30), width=5)
    save(im, "carton", 48)


# ------------------------------------------------------------------ signs
def fit_text(d, text, box, font_path, fill, stroke=None, max_size=400):
    x0, y0, x1, y1 = box
    size = max_size
    while size > 8:
        f = ImageFont.truetype(font_path, size)
        l, t, r, b = d.textbbox((0, 0), text, font=f)
        if r - l <= x1 - x0 and b - t <= y1 - y0:
            break
        size -= 2
    d.text(((x0 + x1) / 2 - (l + r) / 2, (y0 + y1) / 2 - (t + b) / 2), text, font=f, fill=fill, stroke_width=3 if stroke else 0, stroke_fill=stroke)


DEPTS = ["DOLLS", "VIDEO", "GAMES", "VEHICLES", "STUFFED TOYS", "ACTION TOYS", "PRESCHOOL", "SPORTS"]


def dept_signs():
    """The hanging department boards (video): teal with bright lime capitals. Eight boards
    of 512 x 128 px (1.5 m x 0.375 m) in one sheet."""
    W, H = 512, 1024
    im = Image.new("RGB", (W * SS, H * SS), (0, 0, 0))
    d = ImageDraw.Draw(im)
    for k, name in enumerate(DEPTS):
        y0 = k * 128 * SS
        d.rectangle([0, y0, W * SS, y0 + 128 * SS], fill=(22, 104, 110))
        d.rectangle([0, y0, W * SS, y0 + 10 * SS], fill=(30, 128, 134))
        d.rectangle([0, y0 + 118 * SS, W * SS, y0 + 128 * SS], fill=(14, 80, 86))
        fit_text(d, name, (26 * SS, y0 + 20 * SS, (W - 26) * SS, y0 + 108 * SS), BOLD, (176, 240, 60))
    im = im.resize((W, H), Image.LANCZOS)
    save(grain(im, 1.5, 31), "dept_signs", 48)


def dept_blank():
    """One department board with no words: the owner-editable text is drawn over it live
    (scripts/signs.gd)."""
    W, H = 512, 128
    im = Image.new("RGB", (W * SS, H * SS), (22, 104, 110))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W * SS, 10 * SS], fill=(30, 128, 134))
    d.rectangle([0, 118 * SS, W * SS, H * SS], fill=(14, 80, 86))
    im = im.resize((W, H), Image.LANCZOS)
    save(grain(im, 1.5, 31), "dept_blank", 48)


def cards():
    """Price and sale cards, 512 x 512 in a 2 x 2 grid:
    orange price cards with white figures (video), and the yellow SALE signs of the photo."""
    N = 512 * SS
    im = Image.new("RGB", (N, N), (0, 0, 0))
    d = ImageDraw.Draw(im)
    h = N // 2
    # (0,0) and (1,0): orange price cards
    for k, (big, small) in enumerate([("9", "99"), ("6", "99")]):
        x0 = k * h
        d.rectangle([x0, 0, x0 + h, h], fill=(238, 96, 34))
        d.rectangle([x0, 0, x0 + h, h * 0.24], fill=(26, 110, 60))
        fit_text(d, "SALE PRICE" if k == 0 else "SPECIAL", (x0 + 16 * SS, 6 * SS, x0 + h - 16 * SS, h * 0.22), BOLD, (250, 240, 120))
        fit_text(d, big, (x0 + 20 * SS, h * 0.26, x0 + h * 0.62, h * 0.98), BOLD, (255, 255, 255))
        fit_text(d, small, (x0 + h * 0.60, h * 0.34, x0 + h - 14 * SS, h * 0.62), BOLD, (255, 255, 255))
    # (0,1): yellow SALE sign with red letters; (1,1): "20% OFF"
    d.rectangle([0, h, h, N], fill=(250, 214, 40))
    d.rectangle([0, h, h, h + h * 0.3], fill=(214, 34, 40))
    fit_text(d, "BIGGEST", (20 * SS, h + 8 * SS, h - 20 * SS, h + h * 0.28), BOLD, (255, 255, 255))
    fit_text(d, "SALE", (14 * SS, h + h * 0.32, h - 14 * SS, N - 10 * SS), BOLD, (214, 34, 40))
    d.rectangle([h, h, N, N], fill=(250, 214, 40))
    d.rectangle([h, N - h * 0.34, N, N], fill=(26, 130, 70))
    fit_text(d, "20%", (h + 14 * SS, h + 6 * SS, N - 14 * SS, N - h * 0.36), BOLD, (214, 34, 40))
    fit_text(d, "OFF", (h + 60 * SS, N - h * 0.32, N - 60 * SS, N - 8 * SS), BOLD, (255, 255, 255))
    im = im.resize((512, 512), Image.LANCZOS)
    save(grain(im, 1.5, 41), "cards", 64)


def counter():
    """The cash wrap's front, 2.4 m x 0.95 m: white laminate, a red and a blue band, a
    black kick, scuffs low down."""
    W, H = 1024, 400
    a = np.zeros((H, W, 3), np.float32) + 236
    a[60:84] = [196, 34, 44]
    a[96:120] = [30, 48, 150]
    a[H - 44:] = [26, 26, 28]
    a += noise(W, H, 2, 51)[..., None]
    sc = noise(W, H, 5, 52, blur=8)
    a[H - 150:H - 44] -= np.clip(sc[H - 150:H - 44], 0, 30)[..., None] * np.linspace(0, 1, 106)[:, None, None] * 1.6
    for x in (341, 682):
        a[:H - 44, x - 1:x + 1] = 176
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "counter", 64)


def screens():
    """256 x 128: left, the demo TV in the video game case (an invented side-scroller frame);
    right, the register's green-on-black display."""
    im = Image.new("RGB", (256, 128), (0, 0, 0))
    d = ImageDraw.Draw(im)
    rng = random.Random(8)
    # an invented top-down space shooter: stars, a small ship, rows of blocky invaders
    d.rectangle([0, 0, 127, 127], fill=(8, 8, 28))
    for _ in range(40):
        x, y = rng.randint(0, 126), rng.randint(0, 126)
        d.point((x, y), fill=rng.choice([(250, 250, 250), (160, 180, 250), (250, 230, 160)]))
    for j in range(3):
        for i in range(6):
            x, y = 14 + i * 18, 22 + j * 16
            d.rectangle([x, y, x + 10, y + 7], fill=[(90, 220, 120), (240, 200, 60), (230, 90, 200)][j])
            d.rectangle([x + 2, y + 2, x + 3, y + 3], fill=(8, 8, 28)); d.rectangle([x + 7, y + 2, x + 8, y + 3], fill=(8, 8, 28))
    d.polygon([(64, 100), (56, 114), (72, 114)], fill=(120, 200, 250))
    d.line([64, 96, 64, 84], fill=(250, 250, 250), width=1)
    d.rectangle([4, 4, 40, 9], fill=(250, 250, 250)); d.rectangle([90, 4, 124, 9], fill=(250, 220, 60))
    d.rectangle([128, 0, 255, 127], fill=(6, 14, 8))
    for j in range(7):
        y = 12 + j * 15
        x = 140
        for _ in range(rng.randint(2, 4)):
            w = rng.randint(8, 30)
            d.rectangle([x, y, x + w, y + 6], fill=(70, 230, 110))
            x += w + 8
    a = np.asarray(im).astype(np.float32)
    a[::2] *= 0.82   # scanlines
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "screens", 48)


def wire():
    """Wire mesh of the rolling dump bins: white rods on clear, 0.3 m tile, 64 px."""
    N = 64
    im = Image.new("RGBA", (N, N), (255, 255, 255, 0))
    d = ImageDraw.Draw(im)
    for k in range(0, N, 16):
        d.line([k, 0, k, N], fill=(244, 244, 240, 255), width=3)
        d.line([0, k, N, k], fill=(244, 244, 240, 255), width=3)
    save(im, "wire")


if __name__ == "__main__":
    tile_wall(); louver(); carpet(); ceiling(); troffer(); pegboard(); shelf_edge()
    for i, c in enumerate(STYLES):
        merch(c, 100 + i)
    plush(); carton(); dept_signs(); dept_blank(); cards(); counter(); screens(); wire()
    print("wrote tex/kb/*.png")
