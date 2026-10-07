"""Textures for the Wave 8 shops (tools/stores/small/wave8.gd), written to tex/w8/*.png:
Cucos Border Cafe's plank front, sign board, clay-tile awning, papel picado, back bar and
saltillo floor; Claire's marble, lit sign box and walls of carded jewellery; Optical Outlet's
ribbed fascia, frame walls and portraits; Tee Tai's fretwork, menu boards, steam table and
counter front; Saadi's sub-sign and tie rack; Mitchell's Formal Wear's sign panel; Golden
Chain Gang's sign and chain wall. From the Southland facade records (Steven's photos and
ads); the names are the stores' own, the lettering is stand-in type, everything else is
invented. Food names and prices on the menu boards are generic guesses for 1995.
  python3 tools/stores/small/paint8.py   (from the project folder)
"""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "kay_bee"))
import paint_store as kb   # noqa: E402

OUT = os.path.join(HERE, "..", "..", "..", "tex", "w8")
os.makedirs(OUT, exist_ok=True)
BOLD = kb.BOLD
DJ = "/usr/share/fonts/truetype/dejavu/"
SERIF_B = DJ + "DejaVuSerif-Bold.ttf"
SERIF_BI = DJ + "DejaVuSerif-BoldItalic.ttf"
COND_B = DJ + "DejaVuSansCondensed-Bold.ttf"
SANS_B = DJ + "DejaVuSans-Bold.ttf"
FRAUNCES = os.path.join(HERE, "..", "gumballs", "Fraunces-ExtraBold.ttf")
SCRIPT = os.path.join(HERE, "..", "gumballs", "MrDafoe-Regular.ttf")
LORA_I = "/usr/share/fonts/truetype/google-fonts/Lora-Italic-Variable.ttf"
SS = 2


def save(im, name, colors=0):
    if im.mode != "RGBA":
        im = im.convert("RGB")
        if colors:
            im = im.quantize(colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(os.path.join(OUT, name + ".png"), optimize=True)


def spaced(d, text, cx, cy, font, fill, track):
    """Capitals with extra letter spacing, centred on (cx, cy)."""
    ws = [d.textlength(ch, font=font) for ch in text]
    total = sum(ws) + track * (len(text) - 1)
    x = cx - total / 2
    l, t, r, b = d.textbbox((0, 0), "H", font=font)
    for ch, w in zip(text, ws):
        d.text((x, cy - (t + b) / 2), ch, font=font, fill=fill)
        x += w + track


# ------------------------------------------------------------------ Cucos Border Cafe
def planks():
    """Warm vertical wood planks, 1.2 m wide x 2.4 m (256 x 512): 8 boards with dark seams."""
    W, H = 256, 512
    r = np.random.default_rng(801)
    a = np.zeros((H, W, 3), np.float32)
    bw = W // 8
    for k in range(8):
        base = np.array([176, 112, 58], np.float32) * r.uniform(0.86, 1.08)
        a[:, k * bw:(k + 1) * bw] = base
        # grain: long streaks down the board
        streak = kb.noise(bw, H, 9, 802 + k, blur=0)
        streak = np.cumsum(streak, axis=0) * 0.04
        a[:, k * bw:(k + 1) * bw] += (streak - streak.mean())[..., None]
        a[:, k * bw:k * bw + 2] -= 70
    a += kb.noise(W, H, 4, 803)[..., None]
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "planks", 64)


def cucos_sign():
    """The sign board: cream with pale peach stripes, the name in a big red swash with a dark
    drop shadow and a swash under it, MEXICAN CAFE beneath. 1024 x 384 = 4.8 m x 1.8 m."""
    W, H = 1024 * SS, 384 * SS
    im = Image.new("RGB", (W, H), (250, 238, 222))
    d = ImageDraw.Draw(im)
    for k in range(9):
        y = 20 * SS + k * 34 * SS
        d.rectangle([0, y, W, y + 16 * SS], fill=(246, 206, 176))
    d.rectangle([0, 0, W - 1, H - 1], outline=(40, 120, 110), width=10 * SS)
    # the name: a chunky soft serif, slanted, red over a dark shadow
    txt = Image.new("L", (W, H), 0)
    td = ImageDraw.Draw(txt)
    kb.fit_text(td, "Cucos", (W * 0.14, H * 0.06, W * 0.86, H * 0.72), FRAUNCES, 255)
    txt = txt.transform(txt.size, Image.AFFINE, (1, 0.22, -H * 0.08, 0, 1, 0), Image.BICUBIC)
    sh = Image.new("RGB", (W, H), (60, 20, 16))
    im.paste(sh, (10 * SS, 10 * SS), txt)
    im.paste(Image.new("RGB", (W, H), (206, 36, 30)), (0, 0), txt)
    # a swash under the name
    d.arc([W * 0.16, H * 0.42, W * 0.84, H * 0.76], 20, 160, fill=(206, 36, 30), width=9 * SS)
    f = ImageFont.truetype(SANS_B, 46 * SS)
    spaced(d, "MEXICAN CAFE", W / 2, H * 0.865, f, (40, 30, 26), 9 * SS)
    im = im.resize((1024, 384), Image.LANCZOS)
    save(kb.grain(im, 1.2, 804), "cucos_sign", 64)


def clay():
    """Barrel clay roof tiles, 0.6 m square (256): courses of half-round terracotta."""
    N = 256
    a = np.zeros((N, N, 3), np.float32)
    r = np.random.default_rng(805)
    rows = 4
    rh = N // rows
    for j in range(rows):
        for i in range(8):
            x0 = i * 32 + (16 if j % 2 else 0)
            tone = np.array([186, 92, 52], np.float32) * r.uniform(0.85, 1.1)
            for x in range(32):
                xx = (x0 + x) % N
                s = math.sin(math.pi * x / 32)
                a[j * rh:(j + 1) * rh, xx] = tone * (0.55 + 0.5 * s)
        a[(j + 1) * rh - 5:(j + 1) * rh] *= 0.55
    a += kb.noise(N, N, 5, 806, blur=1)[..., None]
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "clay", 48)


def papel():
    """Papel picado: a string of cut-paper flags in bright colours, alpha. 1024 x 128 = 4 m x 0.5 m."""
    W, H = 1024, 128
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cols = [(232, 52, 92), (250, 200, 40), (40, 170, 120), (60, 120, 220), (240, 120, 40), (170, 60, 190)]
    d.line([0, 6, W, 6], fill=(240, 240, 240, 255), width=3)
    for k in range(10):
        x0 = 8 + k * 102
        c = cols[k % len(cols)] + (255,)
        d.rectangle([x0, 6, x0 + 86, 96], fill=c)
        # a scalloped hem and cut-outs
        for s in range(6):
            d.pieslice([x0 + s * 14.3, 88, x0 + s * 14.3 + 14.3, 106], 0, 180, fill=c)
        for s in range(3):
            for t in range(3):
                cx, cy = x0 + 18 + s * 25, 26 + t * 24
                d.polygon([(cx, cy - 7), (cx + 6, cy), (cx, cy + 7), (cx - 6, cy)], fill=(0, 0, 0, 0))
    save(im, "papel")


def bar():
    """The back bar: dark wood shelves of bottles and a mirror strip. 512 x 256 = 2.4 m x 1.2 m."""
    W, H = 512, 256
    rng = random.Random(807)
    im = Image.new("RGB", (W, H), (70, 44, 28))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 40], fill=(150, 160, 160))
    for row, y in enumerate([118, 236]):
        d.rectangle([0, y, W, y + 10], fill=(50, 30, 18))
        x = 6
        while x < W - 20:
            bw = rng.choice([14, 16, 18, 22])
            bh = rng.randint(54, 74)
            c = rng.choice([(150, 90, 30), (60, 110, 60), (200, 190, 150), (120, 40, 30), (220, 220, 210), (90, 60, 30), (40, 80, 120)])
            d.rectangle([x, y - bh + 18, x + bw, y], fill=c)
            d.rectangle([x + bw * 0.35, y - bh, x + bw * 0.65, y - bh + 18], fill=c)
            d.rectangle([x + 2, y - bh * 0.55, x + bw - 2, y - bh * 0.3], fill=(236, 226, 200))
            x += bw + rng.randint(3, 8)
    save(kb.grain(im, 2, 808), "bar", 64)


def saltillo():
    """Saltillo tile, 0.6 m square in four 0.3 m tiles (256): warm terracotta, grey grout."""
    N = 256
    r = np.random.default_rng(809)
    a = np.zeros((N, N, 3), np.float32) + np.array([120, 110, 100], np.float32)
    for j in range(2):
        for i in range(2):
            tone = np.array([196, 110, 66], np.float32) * r.uniform(0.85, 1.08)
            a[j * 128 + 3:(j + 1) * 128 - 3, i * 128 + 3:(i + 1) * 128 - 3] = tone
    a += kb.noise(N, N, 7, 810, blur=3)[..., None]
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "saltillo", 48)


# ------------------------------------------------------------------ Claire's
def marble():
    """Cream marble with pink veins, 0.8 m square (512)."""
    N = 512
    a = np.zeros((N, N, 3), np.float32) + np.array([240, 226, 214], np.float32)
    a += kb.noise(N, N, 4, 811, blur=6)[..., None]
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    rng = random.Random(812)
    for _ in range(26):
        x, y = rng.uniform(0, N), rng.uniform(0, N)
        pts = [(x, y)]
        ang = rng.uniform(0, math.pi)
        for _ in range(40):
            ang += rng.uniform(-0.4, 0.4)
            x += math.cos(ang) * 14; y += math.sin(ang) * 14
            pts.append((x, y))
        d.line(pts, fill=rng.choice([(214, 150, 150), (226, 170, 168), (200, 130, 136)]), width=rng.choice([1, 2, 2, 3]))
    im = im.filter(ImageFilter.GaussianBlur(0.8))
    save(im, "marble", 64)


def claire_sign():
    """The white sign box: the name in tall narrow dark red capitals and lower case, lit red
    from behind, ACCESSORIES in spaced capitals. 1024 x 320 = 3.2 m x 1.0 m."""
    W, H = 1024 * SS, 320 * SS
    im = Image.new("RGB", (W, H), (252, 250, 246))
    # tall narrow letters: draw wide, squeeze to 62 %
    wide = Image.new("L", (int(W * 2.3), H), 0)
    wd = ImageDraw.Draw(wide)
    kb.fit_text(wd, "Claire's", (wide.width * 0.1, H * 0.0, wide.width * 0.9, H * 0.7), COND_B, 255)
    m = wide.resize((W, H), Image.LANCZOS)
    m = m.transform(m.size, Image.AFFINE, (1, 0, 0, 0, 0.98, 0), Image.BICUBIC)
    halo = m.filter(ImageFilter.GaussianBlur(14 * SS))
    im.paste(Image.new("RGB", (W, H), (255, 120, 120)), (0, 0), halo.point(lambda v: min(255, v * 2)))
    im.paste(Image.new("RGB", (W, H), (128, 10, 24)), (0, 0), m)
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(SANS_B, 40 * SS)
    spaced(d, "ACCESSORIES", W / 2, H * 0.85, f, (128, 10, 24), 12 * SS)
    im = im.resize((1024, 320), Image.LANCZOS)
    save(im, "claire_sign", 64)


def jewel_cards():
    """Walls of carded earrings and hair things on purple slatwall, 1.2 m x 1.2 m (512):
    a grid of small white cards on pegs, a few pink SALE tags."""
    N = 512
    rng = random.Random(813)
    im = Image.new("RGB", (N, N), (78, 50, 120))
    d = ImageDraw.Draw(im)
    for y in range(0, N, 16):
        d.line([0, y, N, y], fill=(58, 36, 92), width=3)
    cols = [(232, 80, 140), (250, 210, 60), (90, 200, 220), (240, 240, 240), (180, 120, 230), (120, 220, 140)]
    for j in range(8):
        for i in range(10):
            x, y = 6 + i * 50.5, 8 + j * 63
            d.rectangle([x, y, x + 40, y + 52], fill=(246, 244, 240))
            d.rectangle([x, y, x + 40, y + 9], fill=rng.choice([(150, 18, 30), (60, 40, 110), (230, 90, 150)]))
            c = rng.choice(cols)
            kind = rng.randrange(3)
            if kind == 0:
                for s in (-1, 1):
                    d.ellipse([x + 20 + s * 9 - 5, y + 22, x + 20 + s * 9 + 5, y + 32], fill=c)
            elif kind == 1:
                d.rectangle([x + 8, y + 18, x + 32, y + 44], outline=c, width=3)
            else:
                d.arc([x + 6, y + 16, x + 34, y + 46], 0, 360, fill=c, width=4)
    for _ in range(4):
        x, y = rng.uniform(20, N - 80), rng.uniform(20, N - 50)
        d.rectangle([x, y, x + 58, y + 26], fill=(232, 40, 90))
        kb.fit_text(d, "SALE", (x + 4, y + 3, x + 54, y + 23), BOLD, (255, 255, 255))
    save(kb.grain(im, 1.5, 814), "jewel_cards", 64)


# ------------------------------------------------------------------ Optical Outlet
def ribbed():
    """The lilac-grey ribbed fascia, 0.6 m square (256): vertical ribs every 5 cm."""
    N = 256
    a = np.zeros((N, N, 3), np.float32)
    for x in range(N):
        s = 0.5 + 0.5 * math.cos(2 * math.pi * x / 21.3)
        a[:, x] = np.array([168, 156, 182], np.float32) * (0.78 + 0.28 * s)
    a += kb.noise(N, N, 2, 815)[..., None]
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "ribbed", 32)


def frames():
    """A wall of eyeglass frames on white glass shelves, 1.2 m x 1.2 m (512): seven rows."""
    N = 512
    rng = random.Random(816)
    im = Image.new("RGB", (N, N), (244, 240, 230))
    d = ImageDraw.Draw(im)
    for j in range(7):
        y = 30 + j * 70
        d.rectangle([0, y + 38, N, y + 42], fill=(200, 210, 210))
        x = 10
        while x < N - 60:
            c = rng.choice([(30, 26, 24), (120, 70, 40), (170, 140, 90), (60, 60, 70), (150, 30, 40), (40, 60, 120), (200, 170, 110)])
            w = rng.choice([22, 24, 26])
            h = rng.choice([14, 16, 18])
            for s in (0, 1):
                bx = x + s * (w + 6)
                if rng.random() < 0.5:
                    d.ellipse([bx, y + 14, bx + w, y + 14 + h], outline=c, width=3)
                else:
                    d.rounded_rectangle([bx, y + 14, bx + w, y + 14 + h], radius=4, outline=c, width=3)
            d.line([x + w, y + 18, x + w + 6, y + 18], fill=c, width=2)
            x += 2 * w + 22
    save(kb.grain(im, 1.0, 817), "frames", 64)


def portraits():
    """Four lit portrait panels of invented people in glasses, 1024 x 256 (each 0.9 m square):
    a young woman in large ovals, an older man with grey hair and a moustache in wire rims, a
    boy in round frames, a woman with grey curls in tortoiseshell. Soft-shaded; nobody in
    particular."""
    W, H = 1024, 256
    im = Image.new("RGB", (W, H), (230, 226, 220))
    d = ImageDraw.Draw(im)
    people = [
        dict(skin=(232, 196, 166), hair=(70, 44, 30), bg=(150, 190, 214), long=True, grey=False, frame="oval", col=(40, 30, 30), shirt=(200, 60, 80), stache=False, child=False),
        dict(skin=(214, 170, 136), hair=(176, 176, 172), bg=(214, 206, 180), long=False, grey=True, frame="wire", col=(170, 150, 90), shirt=(60, 70, 110), stache=True, child=False),
        dict(skin=(150, 104, 74), hair=(30, 24, 20), bg=(196, 214, 180), long=False, grey=False, frame="round", col=(40, 60, 140), shirt=(230, 180, 40), stache=False, child=True),
        dict(skin=(240, 210, 186), hair=(196, 190, 186), bg=(232, 200, 210), long=True, grey=True, frame="tort", col=(110, 60, 30), shirt=(120, 60, 120), stache=False, child=False),
    ]
    for k, q in enumerate(people):
        x0 = k * 256
        tile = Image.new("RGB", (256, 256), q["bg"])
        td = ImageDraw.Draw(tile)
        for y in range(256):
            td.line([0, y, 256, y], fill=tuple(int(c * (1.08 - y / 900)) for c in q["bg"]))
        cx = 128
        sc = 0.82 if q["child"] else 1.0
        fw, fh = 60 * sc, 76 * sc
        top = 70 if not q["child"] else 92
        if q["long"]:
            td.ellipse([cx - fw - 24, top - 26, cx + fw + 24, top + 2 * fh + 30], fill=q["hair"])
        td.rectangle([cx - 110, 214, cx + 110, 256], fill=q["shirt"])
        td.ellipse([cx - 120, 200, cx + 120, 300], fill=q["shirt"])
        td.rectangle([cx - 22 * sc, top + 2 * fh - 20, cx + 22 * sc, 222], fill=q["skin"])
        td.ellipse([cx - fw, top, cx + fw, top + 2 * fh], fill=q["skin"])
        # shading on one side of the face
        sh = Image.new("L", (256, 256), 0)
        ImageDraw.Draw(sh).ellipse([cx + fw * 0.35, top, cx + fw * 1.6, top + 2 * fh], fill=28)
        sh = sh.filter(ImageFilter.GaussianBlur(24))
        face = Image.new("L", (256, 256), 0)
        ImageDraw.Draw(face).ellipse([cx - fw, top, cx + fw, top + 2 * fh], fill=255)
        tile.paste((0, 0, 0), (0, 0), Image.fromarray((np.asarray(sh).astype(np.float32) * np.asarray(face) / 255).astype(np.uint8)))
        td = ImageDraw.Draw(tile)
        td.chord([cx - fw - 6, top - 14, cx + fw + 6, top + fh * 0.9], 180, 360, fill=q["hair"])
        if q["grey"] and not q["long"]:
            td.chord([cx - fw - 2, top - 6, cx + fw + 2, top + fh * 0.6], 180, 360, fill=q["hair"])
        ey = top + fh * 0.95
        for s_ in (-1, 1):
            ex = cx + s_ * fw * 0.42
            td.ellipse([ex - 6, ey - 4, ex + 6, ey + 5], fill=(60, 44, 34))
            r = fw * 0.32
            box = [ex - r, ey - r * 0.75, ex + r, ey + r * 0.75]
            if q["frame"] == "round":
                box = [ex - r * 0.8, ey - r * 0.8, ex + r * 0.8, ey + r * 0.8]
                td.ellipse(box, outline=q["col"], width=4)
            elif q["frame"] == "wire":
                td.ellipse([ex - r * 0.85, ey - r * 0.6, ex + r * 0.85, ey + r * 0.6], outline=q["col"], width=2)
            elif q["frame"] == "tort":
                td.rounded_rectangle(box, radius=10, outline=q["col"], width=6)
            else:
                td.ellipse([ex - r * 1.05, ey - r * 0.85, ex + r * 1.05, ey + r * 0.85], outline=q["col"], width=4)
        td.line([cx - 8, ey - 2, cx + 8, ey - 2], fill=q["col"], width=3)
        td.line([cx, ey + 8, cx - 5, ey + fh * 0.4], fill=tuple(int(c * 0.82) for c in q["skin"]), width=3)
        my = top + fh * 1.55
        if q["stache"]:
            td.chord([cx - 22, my - 14, cx + 22, my + 6], 180, 360, fill=q["hair"])
        td.arc([cx - 18, my - 8, cx + 18, my + 10], 20, 160, fill=(150, 70, 70), width=3)
        tile = tile.filter(ImageFilter.GaussianBlur(0.7))
        im.paste(tile.crop((8, 8, 248, 248)), (x0 + 8, 8))
    save(kb.grain(im, 1.5, 818), "portraits", 96)


# ------------------------------------------------------------------ Tee Tai's
def fret():
    """The black fretwork rail: a Chinese key pattern band, alpha. 512 x 64 = 2 m x 0.25 m."""
    W, H = 512, 64
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    K = (14, 12, 12, 255)
    d.rectangle([0, 0, W, 6], fill=K)
    d.rectangle([0, H - 6, W, H], fill=K)
    for k in range(8):
        x = k * 64
        d.rectangle([x + 4, 12, x + 60, 52], outline=K, width=5)
        d.rectangle([x + 16, 24, x + 48, 40], outline=K, width=5)
        d.rectangle([x + 28, 24, x + 33, 40], fill=K)
        d.line([x + 60, 32, x + 68, 32], fill=K, width=5)
    save(im, "fret")


def tt_menu():
    """Three back-lit black menu boards with food pictures and plain names and prices (a
    generic mall Chinese counter of the mid-1990s; dishes and prices are guesses).
    1024 x 256 = 4.8 m x 1.2 m."""
    W, H = 1024 * SS, 256 * SS
    im = Image.new("RGB", (W, H), (16, 14, 14))
    d = ImageDraw.Draw(im)
    rng = random.Random(819)
    boards = [["Bourbon Chicken", "Sweet & Sour Pork", "Pepper Steak"],
              ["Lo Mein", "Fried Rice", "Broccoli Beef"],
              ["Egg Roll  .99", "2 Item Plate  3.99", "3 Item Plate  4.69"]]
    fb = ImageFont.truetype(SANS_B, 15 * SS)
    for k, names in enumerate(boards):
        x0 = k * W / 3
        d.rectangle([x0 + 6 * SS, 6 * SS, x0 + W / 3 - 6 * SS, H - 6 * SS], outline=(200, 160, 60), width=3 * SS)
        for j, nm in enumerate(names):
            px = x0 + 14 * SS + j * (W / 9 - 6 * SS)
            pw = W / 9 - 16 * SS
            d.rectangle([px, 18 * SS, px + pw, 150 * SS], fill=(240, 236, 226))
            cx, cy = px + pw / 2, 84 * SS
            d.ellipse([cx - 44 * SS, cy - 40 * SS, cx + 44 * SS, cy + 40 * SS], fill=(250, 250, 248), outline=(200, 40, 40), width=3 * SS)
            food = [(170, 90, 30), (200, 140, 60), (230, 210, 150), (80, 140, 60), (150, 60, 30)]
            for _ in range(26):
                fx, fy = cx + rng.uniform(-28, 28) * SS, cy + rng.uniform(-24, 24) * SS
                r = rng.uniform(4, 9) * SS
                d.ellipse([fx - r, fy - r, fx + r, fy + r], fill=rng.choice(food))
            fn = ImageFont.truetype(SANS_B, 13 * SS)
            words = nm.split("  ") if "  " in nm else (nm.rsplit(" ", 1) if d.textlength(nm, font=fn) > pw else [nm])
            for li, ln in enumerate(words):
                yy = 168 * SS + li * 17 * SS - (len(words) - 1) * 8 * SS
                d.text((px + pw / 2 - d.textlength(ln, font=fn) / 2, yy), ln, font=fn, fill=(250, 220, 120))
        if k == 2:
            kb.fit_text(d, "COMBINATIONS", (x0 + 20 * SS, 206 * SS, x0 + W / 3 - 20 * SS, 240 * SS), SANS_B, (230, 60, 50))
        else:
            kb.fit_text(d, "ENTREES", (x0 + 20 * SS, 206 * SS, x0 + W / 3 - 20 * SS, 240 * SS), SANS_B, (230, 60, 50))
    im = im.resize((1024, 256), Image.LANCZOS)
    save(im, "tt_menu", 64)


def trays():
    """The steam table seen from the counter: a row of steel pans of food. 512 x 128 = 2.4 m x 0.5 m."""
    W, H = 512, 128
    rng = random.Random(820)
    im = Image.new("RGB", (W, H), (176, 180, 182))
    d = ImageDraw.Draw(im)
    food = [[(170, 80, 20), (200, 120, 40)], [(220, 190, 120), (200, 160, 90)], [(240, 236, 220), (220, 200, 160)],
            [(90, 140, 60), (140, 90, 50)], [(210, 70, 40), (240, 160, 60)], [(130, 70, 40), (90, 140, 70)]]
    for k in range(6):
        x0 = 6 + k * 84
        d.rectangle([x0, 10, x0 + 78, H - 10], fill=(120, 124, 128))
        pal = food[k]
        for _ in range(90):
            fx, fy = rng.uniform(x0 + 6, x0 + 72), rng.uniform(16, H - 16)
            r = rng.uniform(3, 7)
            d.ellipse([fx - r, fy - r, fx + r, fy + r], fill=rng.choice(pal))
    save(kb.grain(im, 2, 821), "trays", 64)


def tt_counter():
    """The counter front: lacquer red with gold medallions on a black kick. 512 x 128 = 2 m x 0.5 m."""
    W, H = 512, 128
    im = Image.new("RGB", (W, H), (180, 24, 22))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 8], fill=(214, 170, 70))
    for k in range(4):
        cx = 64 + k * 128
        d.ellipse([cx - 30, 34, cx + 30, 94], outline=(220, 176, 70), width=6)
        d.ellipse([cx - 12, 52, cx + 12, 76], fill=(220, 176, 70))
    save(kb.grain(im, 1.5, 822), "tt_counter", 32)


# ------------------------------------------------------------------ Saadi's
def saadi_sub():
    """Under the name, on the black fascia: a fine grey rule in from the left to the middle of
    a grey box with 'haberdashery' in black bold serif, and a small tick off its right side.
    1024 x 128 = 3.2 m x 0.4 m."""
    W, H = 1024 * SS, 192 * SS
    im = Image.new("RGB", (W, H), (12, 12, 12))
    d = ImageDraw.Draw(im)
    bx0, bx1 = W * 0.47, W * 0.95
    d.line([W * 0.02, H * 0.5, (bx0 + bx1) / 2, H * 0.5], fill=(190, 190, 186), width=3 * SS)
    d.rectangle([bx0, H * 0.12, bx1, H * 0.88], fill=(190, 190, 186))
    kb.fit_text(d, "haberdashery", (bx0 + 16 * SS, H * 0.16, bx1 - 16 * SS, H * 0.84), SERIF_B, (12, 12, 12))
    d.line([bx1, H * 0.5, bx1 + 14 * SS, H * 0.5], fill=(190, 190, 186), width=3 * SS)
    im = im.resize((1024, 192), Image.LANCZOS)
    save(im, "saadi_sub", 32)


def ties():
    """A tie rack: rows of hanging ties in stripes and foulards, 1.2 m x 0.6 m (512 x 256)."""
    W, H = 512, 256
    rng = random.Random(823)
    im = Image.new("RGB", (W, H), (110, 76, 46))
    d = ImageDraw.Draw(im)
    cols = [(120, 20, 30), (20, 40, 90), (40, 70, 50), (170, 140, 60), (90, 30, 70), (30, 30, 34), (160, 60, 40)]
    for row in range(2):
        y0 = 8 + row * 124
        d.rectangle([0, y0, W, y0 + 5], fill=(190, 160, 110))
        x = 6
        while x < W - 20:
            c = rng.choice(cols)
            w = 18
            d.polygon([(x, y0 + 6), (x + w, y0 + 6), (x + w - 2, y0 + 96), (x + w / 2, y0 + 112), (x + 2, y0 + 96)], fill=c)
            if rng.random() < 0.5:
                c2 = rng.choice([(220, 210, 180), (200, 170, 80), (150, 150, 160)])
                for k in range(5):
                    yy = y0 + 18 + k * 18
                    d.line([x + 2, yy, x + w - 2, yy + 8], fill=c2, width=3)
            x += w + 4
    save(kb.grain(im, 1.5, 824), "ties", 64)


# ------------------------------------------------------------------ Mitchell's Formal Wear
def mitchell_sign():
    """The logo panel, black on white: the name in a heavy italic, a rule broken by a bow tie,
    FORMAL WEAR in widely spaced capitals with the registered mark. 512 x 256 = 2.4 m x 1.2 m
    with a dark border."""
    W, H = 512 * SS, 256 * SS
    im = Image.new("RGB", (W, H), (250, 250, 248))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W - 1, H - 1], outline=(24, 24, 26), width=10 * SS)
    fi = ImageFont.truetype(LORA_I, 100 * SS)
    fi.set_variation_by_axes([700])
    l, t, r, b = d.textbbox((0, 0), "Mitchell's", font=fi)
    k = min((W * 0.8) / (r - l), (H * 0.44) / (b - t))
    fi = ImageFont.truetype(LORA_I, int(100 * SS * k))
    fi.set_variation_by_axes([700])
    l, t, r, b = d.textbbox((0, 0), "Mitchell's", font=fi)
    d.text((W / 2 - (l + r) / 2, H * 0.3 - (t + b) / 2), "Mitchell's", font=fi, fill=(16, 16, 18))
    y = H * 0.6
    d.line([W * 0.1, y, W * 0.44, y], fill=(16, 16, 18), width=3 * SS)
    d.line([W * 0.56, y, W * 0.9, y], fill=(16, 16, 18), width=3 * SS)
    cx = W / 2
    d.polygon([(cx - 36 * SS, y - 16 * SS), (cx - 6 * SS, y - 4 * SS), (cx - 6 * SS, y + 4 * SS), (cx - 36 * SS, y + 16 * SS)], fill=(16, 16, 18))
    d.polygon([(cx + 36 * SS, y - 16 * SS), (cx + 6 * SS, y - 4 * SS), (cx + 6 * SS, y + 4 * SS), (cx + 36 * SS, y + 16 * SS)], fill=(16, 16, 18))
    d.rectangle([cx - 8 * SS, y - 8 * SS, cx + 8 * SS, y + 8 * SS], fill=(16, 16, 18))
    f = ImageFont.truetype(DJ + "DejaVuSerif.ttf", 32 * SS)
    spaced(d, "FORMAL WEAR", W / 2, H * 0.8, f, (16, 16, 18), 8 * SS)
    ws = sum(d.textlength(ch, font=f) for ch in "FORMAL WEAR") + 8 * SS * 10
    f2 = ImageFont.truetype(DJ + "DejaVuSans.ttf", 14 * SS)
    d.text((W / 2 + ws / 2 + 3 * SS, H * 0.8 - 22 * SS), "®", font=f2, fill=(16, 16, 18))
    im = im.resize((512, 256), Image.LANCZOS)
    save(im, "mitchell_sign", 32)


# ------------------------------------------------------------------ Golden Chain Gang
def gcg_sign():
    """The shop's mark in gold on black: three big outlined G's down the left, GOLDEN / CHAIN /
    GANG beside them, a chain running down to a ball. Stand-in type after the 1994 ad (the ad
    is black and white; the gold is a guess). 512 x 512 = 2.0 m x 2.0 m."""
    W, H = 1536 * SS, 512 * SS
    im = Image.new("RGB", (W, H), (10, 10, 14))
    d = ImageDraw.Draw(im)
    GOLD = (226, 184, 70)
    fg = ImageFont.truetype(FRAUNCES, 176 * SS)
    fw = ImageFont.truetype(SERIF_B, 132 * SS)
    for k, word in enumerate(["OLDEN", "HAIN", "ANG"]):
        y = 14 * SS + k * 138 * SS
        d.text((70 * SS, y - 34 * SS), "G" if k != 1 else "C", font=fg, fill=(10, 10, 14), stroke_width=6 * SS, stroke_fill=GOLD)
        d.text((212 * SS, y + 10 * SS), word, font=fw, fill=GOLD)
    # the chain: links running down to a ball
    x, y = 160 * SS, 404 * SS
    for k in range(5):
        cy = y + k * 16 * SS
        if k % 2:
            d.ellipse([x - 5 * SS, cy - 9 * SS, x + 5 * SS, cy + 9 * SS], outline=GOLD, width=3 * SS)
        else:
            d.ellipse([x - 9 * SS, cy - 5 * SS, x + 9 * SS, cy + 5 * SS], outline=GOLD, width=3 * SS)
    by = y + 90 * SS
    d.ellipse([x - 26 * SS, by - 26 * SS, x + 26 * SS, by + 26 * SS], fill=GOLD)
    d.ellipse([x - 14 * SS, by - 18 * SS, x - 2 * SS, by - 6 * SS], fill=(250, 236, 170))
    im = im.resize((1536, 512), Image.LANCZOS)
    save(im, "gcg_sign", 32)


def chains():
    """The back wall: black velvet panels hung with gold chains in V's and pendants, lit.
    1024 x 256 = 4 m x 1 m."""
    W, H = 1024, 256
    rng = random.Random(825)
    im = Image.new("RGB", (W, H), (22, 16, 28))
    d = ImageDraw.Draw(im)
    for k in range(10):
        x0 = 8 + k * 101
        d.rectangle([x0, 8, x0 + 92, H - 8], fill=(36, 26, 48))
        for j in range(2):
            y0 = 22 + j * 116
            for s in range(rng.choice([2, 3])):
                drop = 50 + s * 16
                g = rng.choice([(236, 196, 90), (214, 170, 64), (246, 220, 140), (210, 210, 214)])
                d.line([(x0 + 14 + s * 4, y0), (x0 + 46, y0 + drop), (x0 + 78 - s * 4, y0)], fill=g, width=2 + (s == 0))
                if rng.random() < 0.6:
                    d.ellipse([x0 + 42, y0 + drop - 2, x0 + 50, y0 + drop + 8], fill=g)
    save(kb.grain(im, 1.2, 826), "chains", 64)


def hats():
    """Claire's top shelf: straw hats, berets and little bags in a row, on clear backing (alpha).
    1024 x 128 = 4 m x 0.5 m."""
    W, H = 1024, 128
    rng = random.Random(827)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = 6
    while x < W - 70:
        kind = rng.randrange(3)
        c = rng.choice([(232, 200, 140), (230, 90, 150), (40, 40, 44), (120, 200, 220), (250, 250, 246), (170, 110, 220)])
        if kind == 0:
            d.ellipse([x, 92, x + 70, 116], fill=c + (255,))
            d.chord([x + 14, 58, x + 56, 112], 180, 360, fill=c + (255,))
            d.rectangle([x + 15, 92, x + 55, 98], fill=(150, 18, 30, 255))
            x += 76
        elif kind == 1:
            d.ellipse([x, 70, x + 54, 104], fill=c + (255,))
            d.ellipse([x + 22, 62, x + 32, 72], fill=c + (255,))
            x += 60
        else:
            d.rounded_rectangle([x, 70, x + 44, 116], radius=6, fill=c + (255,))
            d.arc([x + 8, 46, x + 36, 86], 180, 360, fill=c + (255,), width=4)
            x += 52
    save(im, "hats")


def tux():
    """Mitchell's wall: dinner jackets on hangers (black, white, grey), vest-and-cummerbund sets
    in colours, a rail of bow ties, black shoes along the bottom. 1024 x 512 = 2.4 m x 1.2 m."""
    W, H = 1024, 512
    rng = random.Random(828)
    im = Image.new("RGB", (W, H), (36, 34, 36))
    d = ImageDraw.Draw(im)
    for y in range(0, H, 24):
        d.line([0, y, W, y], fill=(28, 26, 28), width=3)
    d.rectangle([0, 18, W, 24], fill=(200, 200, 204))
    x = 8
    while x < W - 70:
        c = rng.choice([(14, 14, 16), (14, 14, 16), (236, 232, 222), (90, 90, 96), (14, 14, 16)])
        d.line([x + 34, 22, x + 34, 34], fill=(200, 200, 204), width=2)
        d.polygon([(x + 2, 42), (x + 66, 42), (x + 70, 300), (x - 2, 300)], fill=c)
        d.polygon([(x + 22, 42), (x + 34, 120), (x + 46, 42)], fill=(250, 250, 248))
        lap = (40, 40, 44) if c[0] < 50 else (20, 20, 22)
        d.line([(x + 22, 42), (x + 34, 170)], fill=lap, width=5)
        d.line([(x + 46, 42), (x + 34, 170)], fill=lap, width=5)
        x += 74
    # vests and cummerbunds in colours
    cols = [(150, 20, 40), (30, 50, 120), (20, 90, 70), (120, 20, 90), (200, 160, 40), (14, 14, 16), (120, 120, 126)]
    for k in range(14):
        x0 = 8 + k * 72
        c = cols[k % len(cols)]
        d.polygon([(x0 + 6, 320), (x0 + 60, 320), (x0 + 56, 392), (x0 + 33, 404), (x0 + 10, 392)], fill=c)
        d.rectangle([x0 + 6, 408, x0 + 60, 424], fill=c)
        for j in range(3):
            d.line([x0 + 6, 410 + j * 5, x0 + 60, 410 + j * 5], fill=tuple(max(0, v - 30) for v in c))
    # bow ties on a rail
    d.rectangle([0, 432, W, 436], fill=(200, 200, 204))
    for k in range(32):
        cx = 18 + k * 31.5
        c = cols[k % len(cols)]
        d.polygon([(cx - 12, 440), (cx, 448), (cx - 12, 456)], fill=c)
        d.polygon([(cx + 12, 440), (cx, 448), (cx + 12, 456)], fill=c)
    # black patent shoes along the bottom
    for k in range(16):
        cx = 30 + k * 63
        d.ellipse([cx - 24, 476, cx + 24, 500], fill=(10, 10, 12))
        d.ellipse([cx - 10, 478, cx + 2, 484], fill=(120, 120, 130))
    save(kb.grain(im, 1.2, 829), "tux", 64)


def tux_shirts():
    """White and ivory dress shirts folded in white cubbies, a few boxes of studs: 1.2 m square (512)."""
    N = 512
    rng = random.Random(830)
    im = Image.new("RGB", (N, N), (244, 242, 236))
    d = ImageDraw.Draw(im)
    for j in range(5):
        for i in range(4):
            x0, y0 = i * 128, j * 102
            d.rectangle([x0 + 6, y0 + 6, x0 + 122, y0 + 96], fill=(214, 212, 206))
            for k in range(rng.choice([3, 4])):
                c = rng.choice([(250, 250, 248), (240, 234, 216), (250, 250, 248), (226, 230, 240)])
                yy = y0 + 90 - k * 18
                d.rectangle([x0 + 14, yy - 16, x0 + 114, yy], fill=c, outline=(200, 198, 190))
                d.polygon([(x0 + 54, yy - 16), (x0 + 64, yy - 8), (x0 + 74, yy - 16)], fill=(236, 236, 232))
    save(kb.grain(im, 1.0, 831), "tux_shirts", 32)


def sale():
    """A hanging SALE card, pink with white capitals: 256 x 128 = 0.6 m x 0.3 m."""
    im = Image.new("RGB", (256, 128), (232, 40, 90))
    d = ImageDraw.Draw(im)
    d.rectangle([6, 6, 249, 121], outline=(255, 255, 255), width=4)
    kb.fit_text(d, "SALE", (24, 14, 232, 112), BOLD, (255, 255, 255))
    save(im, "sale", 16)


if __name__ == "__main__":
    planks(); cucos_sign(); clay(); papel(); bar(); saltillo()
    marble(); claire_sign(); jewel_cards(); hats()
    ribbed(); frames(); portraits()
    fret(); tt_menu(); trays(); tt_counter()
    saadi_sub(); ties(); mitchell_sign(); gcg_sign(); chains(); tux(); tux_shirts(); sale()
    print("wrote tex/w8/*.png")
