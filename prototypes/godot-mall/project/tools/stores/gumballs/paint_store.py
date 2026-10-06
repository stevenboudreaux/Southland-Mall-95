"""Textures for Gumballs (design/storefronts/gumballs.md) -> tex/gb/*.png.

Everything is painted from scratch after the 1995 video's look: the bulk-candy bins, the
plush, the satin jackets, the black slatwall of bagged T-shirts, posters, cards, the
showcase candy and the sign plaque. All graphics, words and packaging are original; no
brand, band, film, cartoon or sports mark appears.
  python3 tools/stores/gumballs/paint_store.py   (from the project folder)
"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "..", "tex", "gb"))
SS = 2
SCRIPT = os.path.join(HERE, "MrDafoe-Regular.ttf")
SANS_B = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
COND_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"
BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
LORA = "/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf"
SOFT = os.path.join(HERE, "Fraunces-ExtraBold.ttf")   # OFL; a soft, flared serif like the plaque's


def F(path, size, var=None):
    f = ImageFont.truetype(path, int(size))
    if var:
        try:
            f.set_variation_by_name(var)
        except Exception:
            pass
    return f


def save(im, name, colors=0):
    im = im.convert("RGBA" if im.mode == "RGBA" else "RGB")
    if colors:
        im = im.quantize(colors, method=Image.Quantize.FASTOCTREE if im.mode == "RGBA" else Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(os.path.join(OUT, name + ".png"), optimize=True)


def grain(im, amp, seed):
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    a += np.random.default_rng(seed).normal(0, amp, a.shape[:2])[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def text_c(d, xy, s, f, fill, stroke=0, sfill=None, anchor="mm"):
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=sfill)


def fit(path, s, maxw, size, var=None):
    d = ImageDraw.Draw(Image.new("L", (8, 8)))
    while size > 6 and d.textlength(s, font=F(path, size, var)) > maxw:
        size -= 2
    return F(path, size, var)


R = np.random.default_rng(1995)
CANDY = [(220, 30, 40), (250, 200, 30), (40, 170, 60), (40, 90, 220), (250, 130, 30), (150, 60, 190), (250, 120, 170), (245, 245, 240)]


# ------------------------------------------------------------------ the sign plaque
def plaque():
    """'Sweet Ideas' on the blue plaque under the script (video 1:08): cream serif with a
    dark red outline and a black drop shadow, on a glossy blue plate."""
    W, H = 512, 160
    im = Image.new("RGB", (W * SS, H * SS), (36, 52, 190))
    d = ImageDraw.Draw(im)
    for y in range(H * SS):
        t = y / (H * SS)
        c = (int(30 + 40 * (1 - t) ** 3), int(44 + 50 * (1 - t) ** 3), int(170 + 60 * (1 - t) ** 2))
        d.line([(0, y), (W * SS, y)], fill=c)
    d.rectangle([0, 0, W * SS - 1, H * SS - 1], outline=(14, 20, 90), width=8 * SS)
    d.line([(10 * SS, 10 * SS), (W * SS - 10 * SS, 10 * SS)], fill=(120, 140, 255), width=3 * SS)
    f = fit(SOFT, "Sweet Ideas", (W - 70) * SS, 104 * SS)
    text_c(d, (W * SS / 2 + 5 * SS, H * SS / 2 + 7 * SS), "Sweet Ideas", f, (0, 0, 0), 10 * SS, (0, 0, 0))
    text_c(d, (W * SS / 2, H * SS / 2), "Sweet Ideas", f, (248, 236, 206), 7 * SS, (122, 26, 30))
    save(im.resize((W, H), Image.LANCZOS), "plaque")


# ------------------------------------------------------------------ bulk candy bins
def candy_fill(d, box, kind, r):
    x0, y0, x1, y1 = box
    if kind in ("gumballs", "jawbreakers", "lemon", "cinnamon", "choc", "mints"):
        rad = {"gumballs": 7, "jawbreakers": 9, "lemon": 5, "cinnamon": 4, "choc": 5, "mints": 8}[kind]
        cols = {"gumballs": CANDY, "jawbreakers": CANDY[:6], "lemon": [(250, 220, 50), (240, 200, 30)],
                "cinnamon": [(200, 20, 30), (170, 10, 20)], "choc": [(90, 50, 30), (70, 40, 24), (110, 66, 40)],
                "mints": [(250, 250, 250)]}[kind]
        y = y1 - rad
        row = 0
        while y > y0 + rad * 0.5:
            x = x0 + rad + (rad if row % 2 else 0)
            while x < x1 - rad * 0.6:
                c = cols[r.integers(len(cols))]
                d.ellipse([x - rad, y - rad, x + rad, y + rad], fill=c, outline=tuple(int(v * 0.7) for v in c))
                if kind == "mints":
                    d.arc([x - rad + 2, y - rad + 2, x + rad - 2, y + rad - 2], 0, 90, fill=(210, 30, 40), width=3)
                    d.arc([x - rad + 2, y - rad + 2, x + rad - 2, y + rad - 2], 180, 270, fill=(210, 30, 40), width=3)
                d.ellipse([x - rad * 0.45, y - rad * 0.6, x - rad * 0.1, y - rad * 0.25], fill=tuple(min(255, int(v * 0.5 + 128)) for v in c))
                x += rad * 2
            y -= rad * 1.75
            row += 1
    elif kind in ("beans", "bears"):
        n = int((x1 - x0) * (y1 - y0) / (40 if kind == "beans" else 70))
        for _ in range(n):
            x = r.uniform(x0 + 3, x1 - 3)
            y = r.uniform(y0 + 3, y1 - 3)
            c = CANDY[r.integers(len(CANDY))] if kind == "beans" else [(230, 40, 40), (250, 160, 30), (60, 190, 60), (250, 230, 60), (240, 240, 230)][r.integers(5)]
            if kind == "beans":
                a = r.uniform(0, math.pi)
                dx, dy = 6 * math.cos(a), 4 * math.sin(a)
                d.ellipse([x - 6, y - 4, x + 6, y + 4], fill=c)
            else:
                d.ellipse([x - 5, y - 6, x + 5, y + 7], fill=c)
                d.ellipse([x - 5, y - 10, x - 1, y - 6], fill=c)
                d.ellipse([x + 1, y - 10, x + 5, y - 6], fill=c)
    elif kind in ("worms", "licorice", "taffy"):
        n = int((x1 - x0) * (y1 - y0) / 110)
        for _ in range(n):
            x = r.uniform(x0, x1)
            y = r.uniform(y0 + 4, y1 - 4)
            if kind == "worms":
                c1, c2 = [((230, 40, 60), (250, 220, 60)), ((60, 190, 70), (250, 140, 40)), ((80, 120, 230), (240, 90, 160))][r.integers(3)]
                pts = [(x + i * 5, y + 4 * math.sin(i * 1.3 + x)) for i in range(5)]
                d.line(pts, fill=c1, width=5)
                d.line([(p[0], p[1] + 2) for p in pts], fill=c2, width=2)
            elif kind == "licorice":
                c = [(180, 20, 30), (30, 24, 24)][r.integers(2)]
                a = r.uniform(-0.6, 0.6)
                d.line([(x - 12 * math.cos(a), y - 12 * math.sin(a)), (x + 12 * math.cos(a), y + 12 * math.sin(a))], fill=c, width=5)
            else:
                c = [(250, 200, 210), (200, 230, 250), (250, 240, 180), (210, 250, 210), (250, 250, 250)][r.integers(5)]
                d.rounded_rectangle([x - 8, y - 5, x + 8, y + 5], radius=4, fill=c, outline=(200, 200, 200))
                d.line([(x - 12, y), (x - 8, y)], fill=(240, 240, 240), width=3)
                d.line([(x + 8, y), (x + 12, y)], fill=(240, 240, 240), width=3)
    elif kind == "rock":
        for _ in range(int((x1 - x0) * (y1 - y0) / 90)):
            x = r.uniform(x0, x1)
            y = r.uniform(y0, y1)
            c = [(140, 90, 200), (90, 180, 230), (240, 140, 200), (250, 220, 120)][r.integers(4)]
            pts = [(x + r.uniform(-7, 7), y + r.uniform(-7, 7)) for _ in range(4)]
            d.polygon(pts, fill=c, outline=(255, 255, 255))


KINDS = ["gumballs", "beans", "worms", "mints", "bears", "lemon", "licorice", "choc", "jawbreakers", "taffy", "cinnamon", "rock"]


def bins():
    """Two bays (1.22 m each) of four tiers of acrylic scoop bins, filled with candy.
    1024 x 512: a bay is 512 px wide; a tier 128 px (0.325 m) tall, four bins to a tier."""
    W, H = 1024, 512
    im = Image.new("RGB", (W, H), (236, 236, 232))
    d = ImageDraw.Draw(im)
    r = np.random.default_rng(58)
    for bay in range(2):
        for tier in range(4):
            for k in range(4):
                x0 = bay * 512 + k * 128
                y0 = tier * 128
                # the bin's dark interior, then candy up to its fill line
                d.rectangle([x0 + 3, y0 + 4, x0 + 125, y0 + 112], fill=(196, 200, 204))
                fill_top = y0 + int(r.uniform(22, 50))
                candy_fill(d, (x0 + 6, fill_top, x0 + 122, y0 + 110), KINDS[r.integers(len(KINDS))], r)
                # clear acrylic: a glare stripe and the hinged lid's front edge
                for gy in range(y0 + 6, y0 + 110):
                    gx = x0 + 18 + int((gy - y0) * 0.35)
                    d.line([(gx, gy), (gx + 6, gy)], fill=(255, 255, 255))
                d.rectangle([x0 + 3, y0 + 4, x0 + 125, y0 + 13], fill=(226, 232, 236))
                d.line([(x0 + 3, y0 + 13), (x0 + 125, y0 + 13)], fill=(150, 160, 170), width=2)
                d.rectangle([x0 + 50, y0 + 5, x0 + 78, y0 + 11], fill=(170, 176, 182))
                # the lip: white with a yellow price label
                d.rectangle([x0, y0 + 112, x0 + 128, y0 + 127], fill=(246, 246, 244))
                d.rectangle([x0 + 40, y0 + 114, x0 + 88, y0 + 125], fill=(250, 214, 40))
                d.text((x0 + 64, y0 + 120), "$%d.%02d LB" % (r.integers(2, 5), [49, 69, 79, 99][r.integers(4)]), font=F(SANS_B, 8), fill=(30, 30, 30), anchor="mm")
                # acrylic edges
                d.line([(x0 + 1, y0 + 2), (x0 + 1, y0 + 112)], fill=(150, 156, 160), width=2)
                d.line([(x0 + 126, y0 + 2), (x0 + 126, y0 + 112)], fill=(170, 176, 180), width=2)
    save(grain(im, 2.0, 7), "bins", 128)


# ------------------------------------------------------------------ plush (generic animals)
def plush():
    """A shelf row of soft toys, 2.44 m x 0.5 m (1024 x 210 in a 1024 x 256 sheet): bears,
    spotted dogs, cats, rabbits, frogs, moose. No characters."""
    W, H = 1024, 256
    im = Image.new("RGB", (W, H), (242, 242, 240))
    d = ImageDraw.Draw(im)
    r = np.random.default_rng(31)
    x = 6
    while x < W - 30:
        kind = ["bear", "bear", "dog", "cat", "rabbit", "frog", "moose", "bear"][r.integers(8)]
        s = r.uniform(0.75, 1.15)
        w = int(70 * s)
        cx = x + w // 2
        base = H - 4
        col = {"bear": [(214, 160, 70), (150, 100, 60), (240, 200, 120), (250, 230, 190)][r.integers(4)], "dog": (246, 246, 240),
               "cat": [(140, 140, 150), (240, 150, 60), (60, 60, 64)][r.integers(3)], "rabbit": (250, 230, 236),
               "frog": (90, 180, 70), "moose": (120, 80, 50)}[kind]
        dk = tuple(int(v * 0.7) for v in col)
        bh = int(110 * s)
        d.ellipse([cx - w * 0.5, base - bh, cx + w * 0.5, base], fill=col, outline=dk)                    # body
        hr = int(30 * s)
        hy = base - bh - hr + 10
        if kind == "rabbit":
            d.ellipse([cx - 14 * s, hy - 70 * s, cx - 2 * s, hy - 10 * s], fill=col, outline=dk)
            d.ellipse([cx + 2 * s, hy - 70 * s, cx + 14 * s, hy - 10 * s], fill=col, outline=dk)
        if kind in ("bear", "dog", "moose"):
            for sx in (-1, 1):
                d.ellipse([cx + sx * hr * 0.8 - 11 * s, hy - hr - 4 * s, cx + sx * hr * 0.8 + 11 * s, hy - hr + 18 * s], fill=col if kind != "dog" else (40, 40, 40), outline=dk)
        if kind == "cat":
            for sx in (-1, 1):
                d.polygon([(cx + sx * hr * 0.9, hy - hr * 0.2), (cx + sx * hr * 0.75, hy - hr * 1.25), (cx + sx * hr * 0.25, hy - hr * 0.8)], fill=col, outline=dk)
        if kind == "moose":
            for sx in (-1, 1):
                d.polygon([(cx + sx * hr * 0.6, hy - hr * 0.9), (cx + sx * hr * 2.0, hy - hr * 1.7), (cx + sx * hr * 1.6, hy - hr * 1.0), (cx + sx * hr * 1.0, hy - hr * 0.6)], fill=(200, 170, 120))
        d.ellipse([cx - hr, hy - hr, cx + hr, hy + hr], fill=col, outline=dk)                             # head
        if kind == "dog":
            for _ in range(5):
                px, py = cx + r.uniform(-w * 0.35, w * 0.35), base - r.uniform(15, bh - 15)
                d.ellipse([px - 6, py - 5, px + 6, py + 5], fill=(30, 30, 30))
        d.ellipse([cx - hr * 0.5, hy - 2, cx + hr * 0.5, hy + hr * 0.75], fill=tuple(min(255, v + 30) for v in col))   # muzzle
        for sx in (-1, 1):
            d.ellipse([cx + sx * hr * 0.4 - 4, hy - hr * 0.35 - 4, cx + sx * hr * 0.4 + 4, hy - hr * 0.35 + 4], fill=(20, 20, 20))
        d.ellipse([cx - 5, hy + 2, cx + 5, hy + 9], fill=(30, 20, 20))
        if r.random() < 0.4:
            bc = [(220, 30, 40), (40, 90, 220), (250, 200, 30)][r.integers(3)]
            d.polygon([(cx - 14, hy + hr - 2), (cx, hy + hr + 6), (cx - 14, hy + hr + 14)], fill=bc)
            d.polygon([(cx + 14, hy + hr - 2), (cx, hy + hr + 6), (cx + 14, hy + hr + 14)], fill=bc)
        x += int(w * r.uniform(0.7, 0.9))
    save(grain(im, 2.5, 9), "plush", 96)


# ------------------------------------------------------------------ satin jackets on a rail
def jackets():
    """Satin and wool team-style jackets hung on a rail (video 3:22): 2.44 m x 1.0 m, no marks."""
    W, H = 1024, 420
    im = Image.new("RGB", (W, H), (240, 240, 238))
    d = ImageDraw.Draw(im)
    r = np.random.default_rng(3)
    d.rectangle([0, 8, W, 14], fill=(170, 172, 176))
    x = -20
    cols = [(24, 40, 92), (22, 70, 44), (20, 20, 22), (110, 24, 34), (20, 110, 120), (60, 60, 64), (200, 200, 205)]
    while x < W:
        w = int(r.uniform(150, 175))
        body = cols[r.integers(len(cols))]
        sleeve = body if r.random() < 0.6 else (236, 234, 228)
        dk = tuple(int(v * 0.7) for v in body)
        cx = x + w // 2
        d.line([(cx, 12), (cx, 30)], fill=(120, 120, 120), width=3)
        d.polygon([(cx - w * 0.35, 40), (cx + w * 0.35, 40), (cx + w * 0.5, 120), (cx + w * 0.48, H - 30), (cx - w * 0.48, H - 30), (cx - w * 0.5, 120)], fill=body, outline=dk)
        d.polygon([(cx - w * 0.5, 120), (cx - w * 0.35, 40), (cx - w * 0.62, 80), (cx - w * 0.62, H - 60), (cx - w * 0.5, H - 60)], fill=sleeve, outline=dk)
        d.polygon([(cx + w * 0.5, 120), (cx + w * 0.35, 40), (cx + w * 0.62, 80), (cx + w * 0.62, H - 60), (cx + w * 0.5, H - 60)], fill=sleeve, outline=dk)
        rib = (230, 230, 226) if body != (200, 200, 205) else (30, 40, 90)
        for yy in (H - 44, H - 38):
            d.line([(cx - w * 0.48, yy), (cx + w * 0.48, yy)], fill=rib, width=4)
        d.rectangle([cx - w * 0.5 - 12, H - 70, cx - w * 0.5 + 2, H - 58], fill=rib)
        d.arc([cx - 26, 26, cx + 26, 66], 0, 180, fill=rib, width=7)
        d.line([(cx, 56), (cx, H - 30)], fill=tuple(min(255, v + 50) for v in body), width=2)
        # satin sheen
        for k in range(18):
            d.line([(cx - w * 0.3 + k, 60), (cx - w * 0.3 + k, H - 60)], fill=tuple(min(255, int(v + 30 - abs(k - 9) * 3)) for v in body))
        if r.random() < 0.5:   # an abstract chest patch
            d.ellipse([cx + w * 0.12, 90, cx + w * 0.32, 130], fill=rib)
        x += int(w * 0.72)
    save(grain(im, 2.0, 11), "jackets", 96)


# ------------------------------------------------------------------ the T-shirt wall
TEE = ["SWAMP DOGS", "HOUMA", "BAYOU", "LOUISIANA", "CRAWDADDY", "SKATE OR SURF", "COOL CAT", "PEACE", "GATOR",
       "MOON DOG", "HOT STUFF", "MARDI GRAS", "DO THE TWIST", "CAJUN", "NIGHT OWL", "SPACE CADET"]


def tee_art(d, box, i, r):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w = x1 - x0
    kind = i % 10
    if kind == 0:   # tie-dye: a spiral of colour wedges
        R = w * 0.46
        for k in range(36):
            a0 = k * 10
            for j in range(10):
                rr = R * (1 - j / 10)
                col = CANDY[(k // 3 + j) % 6]
                d.pieslice([cx - rr, cy - rr, cx + rr, cy + rr], a0 + j * 9, a0 + j * 9 + 11, fill=col)
    elif kind == 1:  # alien head
        d.ellipse([cx - w * 0.22, cy - w * 0.3, cx + w * 0.22, cy + w * 0.2], fill=(140, 220, 120))
        for sx in (-1, 1):
            d.ellipse([cx + sx * w * 0.1 - w * 0.08, cy - w * 0.12, cx + sx * w * 0.1 + w * 0.08, cy - w * 0.02], fill=(10, 10, 10))
    elif kind == 2:  # yin-yang
        d.ellipse([cx - w * 0.25, cy - w * 0.25, cx + w * 0.25, cy + w * 0.25], fill=(245, 245, 240))
        d.pieslice([cx - w * 0.25, cy - w * 0.25, cx + w * 0.25, cy + w * 0.25], 90, 270, fill=(10, 10, 10))
        d.ellipse([cx - w * 0.125, cy - w * 0.25, cx + w * 0.125, cy], fill=(10, 10, 10))
        d.ellipse([cx - w * 0.125, cy, cx + w * 0.125, cy + w * 0.25], fill=(245, 245, 240))
    elif kind == 3:  # flames
        for k in range(7):
            fx = x0 + w * (0.12 + k * 0.12)
            d.polygon([(fx - w * 0.07, y1 - w * 0.1), (fx, cy - w * r.uniform(0.05, 0.3)), (fx + w * 0.07, y1 - w * 0.1)], fill=[(250, 200, 30), (250, 120, 20), (220, 40, 20)][k % 3])
    elif kind == 4:  # skull and crossbones
        for sx in (-1, 1):
            d.line([(cx - w * 0.26, cy + sx * w * 0.16), (cx + w * 0.26, cy - sx * w * 0.02)], fill=(235, 235, 225), width=max(3, int(w * 0.05)))
        d.ellipse([cx - w * 0.17, cy - w * 0.25, cx + w * 0.17, cy + w * 0.05], fill=(235, 235, 225))
        d.rectangle([cx - w * 0.1, cy, cx + w * 0.1, cy + w * 0.1], fill=(235, 235, 225))
        for sx in (-1, 1):
            d.ellipse([cx + sx * w * 0.07 - w * 0.05, cy - w * 0.14, cx + sx * w * 0.07 + w * 0.05, cy - w * 0.04], fill=(10, 10, 10))
    elif kind == 5:  # sunset palms
        d.ellipse([cx - w * 0.25, cy - w * 0.25, cx + w * 0.25, cy + w * 0.25], fill=(250, 140, 40))
        d.rectangle([x0 + 4, cy + w * 0.05, x1 - 4, cy + w * 0.25], fill=(40, 90, 200))
        d.line([(cx + w * 0.15, cy + w * 0.2), (cx + w * 0.2, cy - w * 0.2)], fill=(20, 20, 20), width=4)
    elif kind == 6:  # wolf moon
        d.ellipse([cx - w * 0.2, cy - w * 0.3, cx + w * 0.2, cy + w * 0.1], fill=(240, 240, 200))
        d.polygon([(cx - w * 0.3, cy + w * 0.3), (cx - w * 0.05, cy - w * 0.05), (cx + w * 0.05, cy + w * 0.05), (cx + w * 0.3, cy + w * 0.3)], fill=(40, 40, 50))
    elif kind == 7:  # checker + bolt
        s = w / 10
        for a in range(6):
            for b in range(3):
                if (a + b) % 2 == 0:
                    d.rectangle([x0 + w * 0.2 + a * s, cy + w * 0.05 + b * s, x0 + w * 0.2 + (a + 1) * s, cy + w * 0.05 + (b + 1) * s], fill=(240, 240, 240))
        d.polygon([(cx, cy - w * 0.3), (cx - w * 0.1, cy), (cx, cy), (cx - w * 0.06, cy + w * 0.12), (cx + w * 0.12, cy - w * 0.1), (cx + w * 0.02, cy - w * 0.1)], fill=(250, 220, 40))
    elif kind == 8:  # dolphins over waves
        for k in range(3):
            d.arc([x0 + k * w * 0.3, cy, x0 + (k + 1) * w * 0.3 + 8, cy + w * 0.2], 180, 360, fill=(60, 160, 230), width=4)
        d.chord([cx - w * 0.2, cy - w * 0.25, cx + w * 0.2, cy + w * 0.05], 200, 340, fill=(130, 150, 170))
    else:            # gator
        d.polygon([(x0 + w * 0.1, cy), (cx, cy - w * 0.1), (x1 - w * 0.1, cy - w * 0.02), (cx, cy + w * 0.08)], fill=(70, 150, 60))
        for k in range(5):
            d.polygon([(x0 + w * (0.3 + k * 0.08), cy - w * 0.05), (x0 + w * (0.34 + k * 0.08), cy - w * 0.12), (x0 + w * (0.38 + k * 0.08), cy - w * 0.05)], fill=(50, 120, 40))
    word = TEE[i % len(TEE)]
    f = fit(COND_B, word, w * 0.86, w * 0.16)
    light_shirt = sum(d.im.getpixel((int(x0 + 3), int(y1 - 3)))[:3]) > 450
    fills = [(20, 20, 30), (200, 20, 40), (30, 70, 170)] if light_shirt else [(250, 250, 240), (250, 210, 40), (90, 220, 250)]
    d.text((cx, y1 - w * 0.14), word, font=f, fill=fills[i % 3], anchor="mm")


def tees():
    """Black slatwall with bagged T-shirts face out (video 3:07-3:12): 7 x 5 shirts on a
    2.44 x 2.44 m sheet, each with a round price tag."""
    W, H = 1024, 1024
    im = Image.new("RGB", (W, H), (22, 22, 24))
    d = ImageDraw.Draw(im)
    for y in range(0, H, 32):
        d.rectangle([0, y, W, y + 5], fill=(8, 8, 9))
        d.line([(0, y + 6), (W, y + 6)], fill=(46, 46, 50))
    r = np.random.default_rng(87)
    cw, ch = W / 7, H / 5
    i = int(r.integers(100))
    for row in range(5):
        for col in range(7):
            x0 = col * cw + 8
            y0 = row * ch + 14
            x1 = x0 + cw - 16
            y1 = y0 + ch - 24
            base = [(250, 250, 248), (24, 24, 26), (230, 220, 190), (50, 60, 120), (130, 30, 40), (60, 100, 70), (250, 250, 248)][r.integers(7)]
            d.rectangle([x0, y0, x1, y1], fill=base)
            tee_art(d, (x0 + 6, y0 + 10, x1 - 6, y1 - 6), i, r)
            i += 1
            # the poly bag: a soft sheen and creased edges
            for k in range(10):
                d.line([(x0 + 10 + k * 2, y0 + 4), (x0 + 30 + k * 2, y1 - 4)], fill=tuple(min(255, v + 30) for v in base))
            d.rectangle([x0, y0, x1, y1], outline=(200, 200, 205), width=2)
            d.ellipse([x0 + 4, y0 - 6, x0 + 30, y0 + 20], fill=(250, 250, 250), outline=(120, 120, 120))
            d.text((x0 + 17, y0 + 7), "$%d" % [9, 12, 14, 15][r.integers(4)], font=F(SANS_B, 11), fill=(200, 20, 30), anchor="mm")
            d.line([(x0 + (x1 - x0) / 2, y0 - 10), (x0 + (x1 - x0) / 2, y0)], fill=(170, 170, 170), width=3)
    save(grain(im, 2.0, 13), "tees", 192)


# ------------------------------------------------------------------ posters, cards, boxes
def posters():
    """Four original posters on the white slatwall by the window (2 x 2 of 256 x 256)."""
    W = 512
    im = Image.new("RGB", (W, W), (240, 240, 238))
    d = ImageDraw.Draw(im)
    r = np.random.default_rng(5)
    def frame(x0, y0):
        d.rectangle([x0 + 8, y0 + 8, x0 + 248, y0 + 248], fill=(20, 20, 22))
        return x0 + 14, y0 + 14, x0 + 242, y0 + 242
    # 1 black-light galaxy
    a, b, c, e = frame(0, 0)
    d.rectangle([a, b, c, e], fill=(20, 0, 50))
    for _ in range(120):
        x, y = r.uniform(a, c), r.uniform(b, e)
        d.ellipse([x, y, x + 2, y + 2], fill=(255, 255, 255))
    d.ellipse([a + 50, b + 50, a + 170, b + 170], fill=(250, 60, 200))
    d.arc([a + 20, b + 95, a + 200, b + 125], 0, 360, fill=(80, 255, 120), width=5)
    # 2 sports car at sunset
    a, b, c, e = frame(256, 0)
    for y in range(int(b), int(e)):
        t = (y - b) / (e - b)
        d.line([(a, y), (c, y)], fill=(int(250 - 120 * t), int(120 - 80 * t), int(60 + 120 * t)))
    d.polygon([(a + 20, e - 50), (a + 60, e - 90), (a + 150, e - 95), (a + 200, e - 60), (a + 215, e - 40), (a + 20, e - 40)], fill=(220, 20, 30))
    for wx in (a + 60, a + 175):
        d.ellipse([wx - 18, e - 58, wx + 18, e - 22], fill=(15, 15, 15))
    # 3 kitten on a branch
    a, b, c, e = frame(0, 256)
    d.rectangle([a, b, c, e], fill=(140, 200, 240))
    d.line([(a, b + 70), (c, b + 90)], fill=(110, 70, 40), width=10)
    d.ellipse([a + 80, b + 80, a + 150, b + 150], fill=(230, 160, 80))
    d.ellipse([a + 95, b + 50, a + 140, b + 95], fill=(230, 160, 80))
    d.text(((a + c) / 2, e - 25), "HOLD ON", font=F(SANS_B, 22), fill=(255, 255, 255), anchor="mm")
    # 4 surf wave
    a, b, c, e = frame(256, 256)
    d.rectangle([a, b, c, e], fill=(250, 230, 160))
    d.pieslice([a - 40, b + 40, c + 20, e + 160], 180, 290, fill=(30, 110, 200))
    d.pieslice([a + 30, b + 90, c - 30, e + 100], 190, 280, fill=(250, 250, 250))
    d.text(((a + c) / 2, b + 30), "SURF'S UP", font=F(BLACK, 26), fill=(220, 40, 30), anchor="mm")
    save(grain(im, 2.0, 15), "posters", 128)


def cards():
    """Postcards and greeting cards for the spinners and the card rack: 4 x 4 cells."""
    W = 512
    im = Image.new("RGB", (W, W), (230, 230, 228))
    d = ImageDraw.Draw(im)
    r = np.random.default_rng(23)
    words = ["HOUMA", "LOUISIANA", "HAPPY B-DAY", "MISS YOU", "SWAMP TOUR", "CAJUN", "GET WELL", "BAYOU", "FRIENDS", "OVER THE HILL", "THANK YOU", "MARDI GRAS", "LOVE", "OOPS!", "SORRY", "PARTY"]
    for k in range(16):
        x0, y0 = (k % 4) * 128 + 6, (k // 4) * 128 + 6
        bg = [(250, 220, 60), (60, 170, 220), (240, 90, 140), (90, 190, 90), (250, 250, 248), (240, 130, 40)][r.integers(6)]
        d.rectangle([x0, y0, x0 + 116, y0 + 116], fill=bg, outline=(120, 120, 120))
        d.ellipse([x0 + 30, y0 + 20, x0 + 86, y0 + 76], fill=CANDY[r.integers(8)])
        f = fit(COND_B, words[k], 104, 22)
        d.text((x0 + 58, y0 + 96), words[k], font=f, fill=(20, 20, 20), anchor="mm")
    save(grain(im, 2.0, 25), "cards", 96)


BOX_WORDS = ["GLOW STARS", "MOOD RING", "STORM GLOBE", "SLIME", "X-RAY SPECS", "HAND BUZZER", "BOUNCY BALLS",
             "KALEIDOSCOPE", "MAGIC TRICKS", "WIND-UP TEETH", "FORTUNE FISH", "SEA CRITTERS", "PUZZLE CUBE", "GLITTER PENS", "MOTION LAMP", "SPRING TOY"]


def boxes():
    """Boxed novelties and gag gifts (video 3:08): 4 x 4 box fronts of 128 x 128."""
    W = 512
    im = Image.new("RGB", (W, W), (200, 200, 200))
    d = ImageDraw.Draw(im)
    r = np.random.default_rng(41)
    for k in range(16):
        x0, y0 = (k % 4) * 128, (k // 4) * 128
        bg = [(250, 210, 40), (30, 60, 170), (220, 30, 40), (30, 150, 70), (130, 40, 160), (20, 20, 22), (250, 120, 30)][r.integers(7)]
        d.rectangle([x0 + 2, y0 + 2, x0 + 125, y0 + 125], fill=bg)
        d.rectangle([x0 + 10, y0 + 30, x0 + 117, y0 + 92], fill=(245, 245, 240))
        d.ellipse([x0 + 40, y0 + 36, x0 + 88, y0 + 86], fill=CANDY[r.integers(8)])
        d.ellipse([x0 + 52, y0 + 44, x0 + 64, y0 + 56], fill=(255, 255, 255))
        f = fit(COND_B, BOX_WORDS[k], 112, 20)
        tc = (255, 255, 255) if sum(bg) < 400 else (20, 20, 20)
        d.text((x0 + 64, y0 + 16), BOX_WORDS[k], font=f, fill=tc, anchor="mm")
        d.text((x0 + 64, y0 + 108), ["NEW!", "GAG GIFT", "WOW!", "FUN!"][r.integers(4)], font=F(BLACK, 16), fill=tc, anchor="mm")
    save(grain(im, 2.0, 43), "boxes", 128)


def knick():
    """Knickknack shelves: mugs, snow globes, little figurines, wild-haired troll-style dolls,
    spring toys, a toy plasma globe. Two rows on a 512 x 256 sheet (1.0 x 0.5 m)."""
    W, H = 512, 256
    im = Image.new("RGB", (W, H), (236, 236, 234))
    d = ImageDraw.Draw(im)
    r = np.random.default_rng(66)
    for row in range(2):
        base = (row + 1) * 128 - 8
        d.rectangle([0, base, W, base + 8], fill=(250, 250, 250))
        x = 8
        while x < W - 30:
            k = r.integers(6)
            if k == 0:     # mug
                c = CANDY[r.integers(8)]
                d.rectangle([x, base - 44, x + 34, base], fill=c, outline=(80, 80, 80))
                d.arc([x + 26, base - 36, x + 46, base - 12], 270, 90, fill=c, width=5)
                x += 52
            elif k == 1:   # snow globe
                d.rectangle([x, base - 18, x + 40, base], fill=(120, 70, 40))
                d.ellipse([x - 2, base - 62, x + 42, base - 14], fill=(200, 230, 250), outline=(250, 250, 250))
                d.polygon([(x + 12, base - 20), (x + 20, base - 44), (x + 28, base - 20)], fill=(40, 120, 60))
                x += 52
            elif k == 2:   # troll-style doll: tall bright hair
                hc = [(250, 60, 160), (60, 200, 250), (250, 230, 40), (100, 230, 90), (250, 120, 30)][r.integers(5)]
                d.polygon([(x + 4, base - 50), (x + 15, base - 100), (x + 26, base - 50)], fill=hc)
                d.ellipse([x + 3, base - 56, x + 27, base - 30], fill=(240, 190, 150))
                d.rectangle([x + 5, base - 32, x + 25, base], fill=CANDY[r.integers(6)])
                x += 36
            elif k == 3:   # spring toy
                c = CANDY[r.integers(8)]
                for j in range(9):
                    d.ellipse([x, base - 8 - j * 4, x + 36, base - j * 4], outline=c, width=2)
                x += 46
            elif k == 4:   # figurine
                c = [(250, 250, 250), (200, 170, 120), (130, 160, 200)][r.integers(3)]
                d.polygon([(x + 6, base), (x + 14, base - 40), (x + 22, base)], fill=c, outline=(150, 150, 150))
                d.ellipse([x + 8, base - 52, x + 20, base - 38], fill=c)
                x += 30
            else:          # toy plasma globe
                d.rectangle([x + 8, base - 16, x + 38, base], fill=(20, 20, 20))
                d.ellipse([x, base - 56, x + 46, base - 12], fill=(40, 0, 70))
                for j in range(6):
                    a = r.uniform(0, math.tau)
                    d.line([(x + 23, base - 34), (x + 23 + 20 * math.cos(a), base - 34 + 20 * math.sin(a))], fill=(240, 120, 255), width=2)
                x += 56
    save(grain(im, 2.0, 67), "knick", 128)


# ------------------------------------------------------------------ the candy case, the oval sign
def showcase():
    """What sits on the glass shelves of the candy case: boxed chocolates, fudge, swirl
    lollipops, truffles in paper cups. 512 x 256 for 1.6 x 0.8 m (three shelves)."""
    W, H = 512, 256
    im = Image.new("RGB", (W, H), (236, 232, 226))
    d = ImageDraw.Draw(im)
    r = np.random.default_rng(71)
    for row in range(3):
        base = (row + 1) * 85 - 6
        d.rectangle([0, base, W, base + 6], fill=(200, 220, 225))
        x = 4
        while x < W - 20:
            k = r.integers(4)
            if k == 0:
                c = [(214, 170, 60), (160, 30, 50), (250, 250, 250)][r.integers(3)]
                d.rectangle([x, base - 30, x + 54, base], fill=c, outline=(110, 80, 30))
                d.line([(x + 27, base - 30), (x + 27, base)], fill=(200, 30, 40), width=4)
                x += 60
            elif k == 1:
                for j in range(4):
                    d.rectangle([x + j * 14, base - 22, x + j * 14 + 12, base], fill=(100, 60, 34))
                x += 60
            elif k == 2:
                for j in range(3):
                    cx = x + 14 + j * 26
                    d.line([(cx, base), (cx, base - 30)], fill=(250, 250, 250), width=3)
                    d.ellipse([cx - 12, base - 56, cx + 12, base - 32], fill=CANDY[r.integers(8)])
                    d.arc([cx - 8, base - 52, cx + 8, base - 36], 0, 270, fill=(255, 255, 255), width=2)
                x += 84
            else:
                for j in range(5):
                    d.ellipse([x + j * 14, base - 14, x + j * 14 + 12, base - 2], fill=(70, 40, 24))
                    d.rectangle([x + j * 14, base - 6, x + j * 14 + 12, base], fill=(140, 90, 50))
                x += 76
    save(grain(im, 2.0, 73), "showcase", 96)


def oval():
    """The red oval sign over the candy case (after the video's, new words)."""
    W, H = 512, 256
    im = Image.new("RGB", (W * SS, H * SS), (246, 242, 230))
    d = ImageDraw.Draw(im)
    d.ellipse([4 * SS, 4 * SS, (W - 4) * SS, (H - 4) * SS], fill=(170, 18, 40), outline=(246, 242, 230), width=10 * SS)
    d.ellipse([22 * SS, 22 * SS, (W - 22) * SS, (H - 22) * SS], outline=(230, 190, 120), width=3 * SS)
    f = fit(SCRIPT, "Fudge & Chocolates", (W - 110) * SS, 110 * SS)
    text_c(d, (W * SS / 2, H * SS * 0.44), "Fudge & Chocolates", f, (250, 236, 210), 2 * SS, (90, 0, 10))
    text_c(d, (W * SS / 2, H * SS * 0.72), "MADE FRESH DAILY", F(SERIF_B, 22 * SS), (240, 210, 150))
    save(im.resize((W, H), Image.LANCZOS), "oval", 64)


def gumball_fill():
    """Packed gumballs as seen through the globe (tiles)."""
    W = 256
    im = Image.new("RGB", (W, W), (40, 30, 40))
    d = ImageDraw.Draw(im)
    r = np.random.default_rng(99)
    rad = 9
    for row in range(-1, W // 15 + 2):
        for col in range(-1, W // 18 + 2):
            x = col * 18 + (9 if row % 2 else 0)
            y = row * 15
            c = CANDY[r.integers(8)]
            for ox in (-W, 0, W):
                for oy in (-W, 0, W):
                    d.ellipse([x + ox - rad, y + oy - rad, x + ox + rad, y + oy + rad], fill=c, outline=tuple(int(v * 0.6) for v in c))
                    d.ellipse([x + ox - 5, y + oy - 6, x + ox - 1, y + oy - 2], fill=tuple(min(255, int(v * 0.4 + 150)) for v in c))
    save(im, "gumballs", 64)


# ------------------------------------------------------------------ surfaces and small signs
def floor():
    """White vinyl tile, 12-inch, with faint mottling: 2 x 2 tiles (0.61 m)."""
    W = 256
    a = np.full((W, W, 3), 238.0)
    r = np.random.default_rng(17)
    spots = r.random((W, W))
    a[spots > 0.985] -= 30
    a[spots > 0.996] -= 40
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7))
    d = ImageDraw.Draw(im)
    for k in (0, 128):
        d.line([(k, 0), (k, W)], fill=(196, 196, 194), width=2)
        d.line([(0, k), (W, k)], fill=(196, 196, 194), width=2)
    save(grain(im, 1.5, 19), "floor", 48)


def slat(name, base, groove):
    """Slatwall: 3-inch slats; 128 px = 0.305 m (four slats)."""
    W = 128
    im = Image.new("RGB", (W, W), base)
    d = ImageDraw.Draw(im)
    for y in range(0, W, 32):
        d.rectangle([0, y, W, y + 4], fill=groove)
        d.line([(0, y + 5), (W, y + 5)], fill=tuple(min(255, v + 18) for v in base))
    save(grain(im, 1.5, 21), name, 32)


def snacks():
    """The blue candy tower by the T-shirts (video 3:10), unbranded: a white strip reading
    SNACKS down its edge, shelves of rolled candy tubes and candy sticks in cups."""
    W, H = 256, 512
    im = Image.new("RGB", (W * SS, H * SS), (30, 70, 190))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 52 * SS, H * SS], fill=(246, 246, 244))
    for i, ch in enumerate("SNACKS"):
        text_c(d, (26 * SS, (50 + i * 76) * SS), ch, F(BLACK, 58 * SS), (20, 20, 22))
    r = np.random.default_rng(29)
    for row in range(6):
        y = (40 + row * 78) * SS
        d.rectangle([58 * SS, y + 62 * SS, W * SS, y + 70 * SS], fill=(20, 40, 120))
        if row % 2 == 0:
            # rolled candy tubes, lying in a tray
            for k in range(5):
                x = (64 + k * 37) * SS
                c = CANDY[r.integers(8)]
                d.rounded_rectangle([x, y + 34 * SS, x + 32 * SS, y + 62 * SS], radius=10 * SS, fill=c)
                d.rectangle([x + 10 * SS, y + 34 * SS, x + 22 * SS, y + 62 * SS], fill=(250, 250, 248))
        else:
            # candy sticks standing in cups
            for k in range(4):
                x = (66 + k * 46) * SS
                d.rectangle([x, y + 40 * SS, x + 36 * SS, y + 62 * SS], fill=(246, 246, 244))
                for j in range(6):
                    sx = x + (4 + j * 5) * SS
                    c = CANDY[r.integers(8)]
                    d.line([(sx, y + 6 * SS), (sx, y + 42 * SS)], fill=c, width=4 * SS)
                    d.line([(sx - 2 * SS, y + 12 * SS), (sx + 2 * SS, y + 16 * SS)], fill=(255, 255, 255), width=SS)
    save(im.resize((W, H), Image.LANCZOS), "snacks", 64)


def sale():
    """The window card (video 3:29): BUY 1 T-SHIRT, GET 1 1/2 PRICE."""
    W, H = 256, 384
    im = Image.new("RGB", (W * SS, H * SS), (250, 250, 248))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W * SS - 1, H * SS - 1], outline=(200, 20, 30), width=10 * SS)
    for i, (s, sz) in enumerate([("BUY 1", 70), ("T-SHIRT", 50), ("GET 1", 70), ("1/2", 110), ("PRICE", 66)]):
        text_c(d, (W * SS / 2, (52 + i * 72) * SS), s, fit(BLACK, s, (W - 40) * SS, sz * SS), (200, 20, 30))
    save(im.resize((W, H), Image.LANCZOS), "sale", 32)


def lava():
    """Wax blobs in a lava lamp, greyscale (the material tints it): 64 x 128, v up the bottle."""
    W, H = 64, 128
    a = np.full((H, W), 150.0)
    r = np.random.default_rng(5)
    yy, xx = np.mgrid[0:H, 0:W]
    for _ in range(7):
        cx, cy, rad = r.uniform(0, W), r.uniform(10, H - 10), r.uniform(6, 14)
        for ox in (-W, 0, W):
            dd = ((xx - cx - ox) / 1.0) ** 2 + ((yy - cy) / 1.4) ** 2
            a = np.maximum(a, 255 * np.exp(-dd / (rad * rad)) ** 0.5)
    a[H - 14:, :] = np.maximum(a[H - 14:, :], 240)
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGB"), "lava", 32)


# ------------------------------------------------------------------ the black-light wall (Steven, Oct 6)
def bl_posters():
    """Four black-light posters, original psychedelic art (no band, film or brand art):
    flocked-look swirls in fluorescent colours on black. 4 x 256 x 384 in a 1024 x 384 sheet."""
    W, H = 256, 384
    sheet = Image.new("RGB", (W * 4, H), (0, 0, 0))
    FL = [(255, 40, 200), (60, 255, 80), (255, 240, 40), (40, 220, 255), (255, 120, 20), (180, 60, 255)]
    r = np.random.default_rng(1969)
    for k in range(4):
        im = Image.new("RGB", (W * SS, H * SS), (6, 4, 10))
        d = ImageDraw.Draw(im)
        cx, cy = W * SS / 2, H * SS * 0.45
        if k == 0:     # a radiating sun with a face-free spiral centre
            for i in range(36):
                a0 = i * 10
                d.pieslice([cx - 400, cy - 400, cx + 400, cy + 400], a0, a0 + 5, fill=FL[i % 6])
            for rr, c in ((150, (6, 4, 10)), (130, FL[2]), (100, FL[4]), (70, FL[0]), (40, FL[3])):
                d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=c)
        elif k == 1:   # mushrooms
            for (mx, my, ms, c) in ((cx - 120, cy + 120, 1.0, FL[0]), (cx + 110, cy + 170, 0.8, FL[3]), (cx, cy - 40, 1.3, FL[2])):
                d.rectangle([mx - 30 * ms, my, mx + 30 * ms, my + 180 * ms], fill=FL[1])
                d.chord([mx - 140 * ms, my - 110 * ms, mx + 140 * ms, my + 90 * ms], 180, 360, fill=c)
                for j in range(6):
                    sx = mx + r.uniform(-100, 100) * ms
                    sy = my - r.uniform(10, 80) * ms
                    d.ellipse([sx - 14 * ms, sy - 10 * ms, sx + 14 * ms, sy + 10 * ms], fill=(250, 250, 240))
        elif k == 2:   # peace sign in a wavy rainbow
            for i, c in enumerate(FL):
                rr = 240 - i * 26
                d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=c, width=22)
            d.ellipse([cx - 110, cy - 110, cx + 110, cy + 110], outline=(250, 250, 250), width=26)
            d.line([(cx, cy - 110), (cx, cy + 110)], fill=(250, 250, 250), width=26)
            d.line([(cx, cy), (cx - 78, cy + 78)], fill=(250, 250, 250), width=26)
            d.line([(cx, cy), (cx + 78, cy + 78)], fill=(250, 250, 250), width=26)
        else:          # an eye in a starburst of waves
            for i in range(14):
                y = 60 + i * 50
                pts = [(x, y + 26 * math.sin(x / 40 + i)) for x in range(0, W * SS, 8)]
                d.line(pts, fill=FL[i % 6], width=14)
            d.ellipse([cx - 170, cy - 90, cx + 170, cy + 90], fill=(250, 250, 240), outline=FL[5], width=12)
            d.ellipse([cx - 70, cy - 70, cx + 70, cy + 70], fill=FL[3])
            d.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=(6, 4, 10))
        word = ["FAR OUT", "GROOVY", "PEACE", "TRIPPY"][k]
        f = fit(BLACK, word, W * SS * 0.8, 70 * SS)
        d.text((W * SS / 2, H * SS - 46 * SS), word, font=f, fill=FL[(k + 2) % 6], anchor="mm", stroke_width=3 * SS, stroke_fill=(6, 4, 10))
        d.rectangle([0, 0, W * SS - 1, H * SS - 1], outline=(30, 30, 34), width=6 * SS)
        sheet.paste(im.resize((W, H), Image.LANCZOS), (k * W, 0))
    save(sheet, "bl_posters", 128)


def incense():
    """The bottom shelf of the black-light wall: incense boxes and cones, stick bundles in a
    cup, brass and soapstone burners, little trinkets. 1024 x 192 for 2.4 x 0.45 m."""
    W, H = 1024, 192
    im = Image.new("RGB", (W, H), (14, 12, 18))
    d = ImageDraw.Draw(im)
    r = np.random.default_rng(77)
    x = 6
    base = H - 6
    names = ["SANDALWOOD", "PATCHOULI", "JASMINE", "MUSK", "ROSE", "AMBER", "VANILLA", "PINE"]
    while x < W - 40:
        k = r.integers(5)
        if k == 0:     # an incense box
            c = [(120, 30, 120), (30, 90, 60), (160, 60, 20), (40, 50, 140), (150, 20, 30)][r.integers(5)]
            d.rectangle([x, base - 110, x + 46, base], fill=c, outline=(230, 190, 80), width=2)
            d.ellipse([x + 8, base - 92, x + 38, base - 62], fill=(230, 190, 80))
            nm = names[r.integers(len(names))]
            f = fit(COND_B, nm, 42, 11)
            d.text((x + 23, base - 30), nm, font=f, fill=(250, 240, 200), anchor="mm")
            x += 52
        elif k == 1:   # sticks standing in a cup
            d.rectangle([x, base - 40, x + 34, base], fill=(200, 170, 110))
            for j in range(9):
                sx = x + 4 + j * 3.4
                d.line([(sx, base - 40), (sx + r.uniform(-6, 6), base - 140)], fill=(110, 60, 40), width=2)
            x += 42
        elif k == 2:   # a soapstone burner (a little elephant shape)
            d.ellipse([x, base - 46, x + 60, base - 6], fill=(220, 210, 190))
            d.rectangle([x + 8, base - 14, x + 18, base], fill=(220, 210, 190))
            d.rectangle([x + 42, base - 14, x + 52, base], fill=(220, 210, 190))
            d.polygon([(x + 54, base - 36), (x + 72, base - 20), (x + 66, base - 10), (x + 52, base - 22)], fill=(220, 210, 190))
            d.ellipse([x + 22, base - 40, x + 30, base - 32], fill=(60, 50, 40))
            x += 80
        elif k == 3:   # cones in a dish
            d.ellipse([x, base - 16, x + 70, base], fill=(170, 130, 60))
            for j in range(4):
                cx = x + 12 + j * 15
                d.polygon([(cx - 6, base - 10), (cx + 6, base - 10), (cx, base - 30)], fill=[(150, 40, 30), (90, 60, 40), (40, 90, 50)][j % 3])
            x += 78
        else:          # a crystal and a little mirror-ball trinket
            d.polygon([(x + 10, base), (x, base - 40), (x + 14, base - 70), (x + 28, base - 40), (x + 20, base)], fill=(180, 140, 230), outline=(240, 220, 255))
            d.ellipse([x + 32, base - 30, x + 60, base - 2], fill=(200, 200, 210))
            for j in range(5):
                d.line([(x + 32, base - 26 + j * 6), (x + 60, base - 26 + j * 6)], fill=(120, 120, 130))
            x += 70
    save(grain(im, 2.0, 79), "incense", 96)


def plasma():
    """A lightning ball's glow: purple-pink tendrils from the centre (sphere wrap)."""
    W = 256
    im = Image.new("RGB", (W, W), (40, 6, 70))
    d = ImageDraw.Draw(im)
    r = np.random.default_rng(91)
    for i in range(14):
        x = r.uniform(0, W)
        pts = [(x, W)]
        for j in range(10):
            x += r.uniform(-16, 16)
            pts.append((x, W - (j + 1) * W / 10))
        d.line(pts, fill=(250, 140, 255), width=4)
        d.line(pts, fill=(255, 230, 255), width=1)
    save(im.filter(ImageFilter.GaussianBlur(1.2)), "plasma", 48)


def main():
    os.makedirs(OUT, exist_ok=True)
    bl_posters(); incense(); plasma()
    lava()
    plaque(); bins(); plush(); jackets(); tees(); posters(); cards(); boxes(); knick()
    showcase(); oval(); gumball_fill(); floor(); snacks(); sale()
    slat("slat_black", (24, 24, 26), (6, 6, 7))
    slat("slat_white", (238, 238, 236), (190, 190, 190))
    tot = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT) if f.endswith(".png"))
    print("wrote tex/gb/*.png, %d KB" % (tot // 1024))


if __name__ == "__main__":
    main()
