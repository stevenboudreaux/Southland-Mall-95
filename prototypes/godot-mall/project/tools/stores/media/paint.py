"""Textures for the media kit (tools/stores/media/kit.gd): Babbage's and Sound Shop,
written to tex/md/*.png.

Babbage's: the 1997 Killeen Mall video Steven chose (design/storefronts/babbages.md):
dark grey carpet, white wall bays with lit header boxes, white slatwall, a yellow
new-release board, red price posters on chrome stands.
Sound Shop: the 1993 Hammond Square commercial (design/storefronts/sound-shop.md):
white wall racks of CDs and cassettes, white islands, a light vinyl floor, posters hung
high, and (Steven) a box-office ticket board behind the registers.

Every package, cover, poster and act name here is invented: scribbled titles and
generic shapes, no real logo, platform mark, game, album, band or venue.
  python3 tools/stores/media/paint.py   (from the project folder)
"""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "kay_bee"))
import paint_store as kb   # noqa: E402  (motif, scribble, burst, noise, grain, fit_text)

OUT = os.path.join(HERE, "..", "..", "..", "tex", "md")
os.makedirs(OUT, exist_ok=True)
BOLD = kb.BOLD
SS = 2
GAP = (34, 32, 34)


def save(im, name, colors=0):
    im = im.convert("RGBA" if im.mode == "RGBA" else "RGB")
    if colors:
        im = im.quantize(colors, method=Image.Quantize.FASTOCTREE if im.mode == "RGBA" else Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(os.path.join(OUT, name + ".png"), optimize=True)


# ------------------------------------------------------------------ floors and walls
def carpet_grey():
    """1 m x 1 m, seamless: Babbage's dark grey commercial carpet with a faint fleck."""
    N = 512
    a = np.zeros((N, N, 3), np.float32) + np.array([74, 74, 78], np.float32)
    a *= (1 + kb.noise(N, N, 0.10, 61))[..., None]
    a += kb.noise(N, N, 3, 62, blur=12)[..., None]
    r = np.random.default_rng(63)
    fl = r.random((N, N)) < 0.012
    a[fl] += np.array([40, 40, 46], np.float32)
    yy = np.arange(N)[:, None]
    a *= (1 + 0.03 * np.sin(yy * math.tau / 4.0))[..., None]
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "carpet_grey", 64)


def vinyl():
    """0.61 m x 0.61 m: four 12 in vinyl composition tiles, near-white with grey chips,
    laid in the usual alternating grain (Sound Shop, Hammond 1993: a light floor)."""
    N = 256
    a = np.zeros((N, N, 3), np.float32)
    r = np.random.default_rng(71)
    for j in range(2):
        for i in range(2):
            base = np.array([226, 226, 222], np.float32) + r.uniform(-5, 5)
            tile = np.zeros((N // 2, N // 2, 3), np.float32) + base
            chips = kb.noise(N // 2, N // 2, 7, 72 + i + j * 2, blur=1.2)
            if (i + j) % 2:
                chips = chips.T
            tile += chips[..., None]
            spots = r.random((N // 2, N // 2)) < 0.02
            tile[spots] -= 40
            a[j * N // 2:(j + 1) * N // 2, i * N // 2:(i + 1) * N // 2] = tile
    a[:, :1] -= 30; a[:1, :] -= 30
    a[:, N // 2 - 1:N // 2] -= 30; a[N // 2 - 1:N // 2, :] -= 30
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "vinyl", 64)


def slatwall():
    """White slatwall, 0.6 m square: 3 in grooves with the dark slot in each (Babbage's cash
    wrap and accessory walls)."""
    N = 256
    a = np.full((N, N, 3), 238, np.float32)
    a += kb.noise(N, N, 1.2, 81)[..., None]
    step = N / 8
    for k in range(8):
        y = int(k * step)
        a[y:y + 3] = [120, 120, 118]
        a[y + 3:y + 5] = [196, 196, 192]
        a[y + 5:y + 7] = [250, 250, 248]
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "slatwall", 16)


def counter_front(name, band, band2=None):
    """A cash wrap's front, 2.4 m x 0.95 m: white laminate, a coloured band, a dark kick."""
    W, H = 1024, 400
    a = np.zeros((H, W, 3), np.float32) + 238
    a[54:78] = band
    if band2:
        a[86:96] = band2
    a[H - 40:] = [30, 30, 32]
    a += kb.noise(W, H, 2, 91)[..., None]
    sc = kb.noise(W, H, 5, 92, blur=8)
    a[H - 140:H - 40] -= np.clip(sc[H - 140:H - 40], 0, 30)[..., None] * np.linspace(0, 1, 100)[:, None, None] * 1.4
    for x in (341, 682):
        a[:H - 40, x - 1:x + 1] = 180
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), name, 64)


# ------------------------------------------------------------------ stock
# Each stock sheet is 512 x 1024 px for a 1.22 m wide shelf face (420 px per metre),
# split into rows: ROWS[k] = (rows, row height in m). kit.gd uses the same numbers.
PXM = 512 / 1.22
ROWS = {"games": (8, 0.305), "pc": (8, 0.305), "books": (8, 0.305), "acc": (8, 0.305),
        "cd": (16, 0.1525), "tape": (16, 0.1525)}

PAL = [(220, 40, 40), (240, 200, 40), (40, 90, 200), (60, 170, 90), (240, 120, 30), (150, 60, 170), (250, 250, 250), (20, 20, 24), (90, 200, 230)]


def cover_art(d, x0, y0, w, h, rng, dark=None):
    """An invented cover: a gradient sky, a horizon, a shape, and a scribbled title."""
    c0 = rng.choice(PAL) if dark is None else dark
    c1 = rng.choice(PAL)
    for k in range(int(h)):
        f = k / max(1, h)
        d.line([x0, y0 + k, x0 + w, y0 + k], fill=tuple(int(c0[i] * (1 - f) + c1[i] * f * 0.6) for i in range(3)))
    kind = rng.choice(["planet", "ship", "sword", "car", "figure", "robot", "screen", "ball", "plane", "mountain"])
    mx, my, mw, mh = x0 + w * 0.08, y0 + h * 0.3, w * 0.84, h * 0.62
    if kind == "planet":
        r = min(mw, mh) * 0.36
        cx, cy = mx + mw * rng.uniform(0.3, 0.7), my + mh * 0.5
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rng.choice(PAL))
        d.arc([cx - r * 1.6, cy - r * 0.4, cx + r * 1.6, cy + r * 0.4], 0, 360, fill=rng.choice(PAL), width=max(1, int(r * 0.12)))
    elif kind == "ship":
        cx, cy = mx + mw * 0.5, my + mh * 0.5
        s = min(mw, mh) * 0.5
        d.polygon([(cx, cy - s), (cx + s * 0.5, cy + s * 0.6), (cx, cy + s * 0.3), (cx - s * 0.5, cy + s * 0.6)], fill=rng.choice(PAL))
        d.polygon([(cx - s * 0.12, cy + s * 0.5), (cx + s * 0.12, cy + s * 0.5), (cx, cy + s * 0.95)], fill=(250, 200, 60))
    elif kind == "sword":
        cx = mx + mw * 0.5
        d.polygon([(cx - mw * 0.05, my + mh * 0.95), (cx + mw * 0.05, my + mh * 0.95), (cx + mw * 0.03, my), (cx - mw * 0.03, my)], fill=(220, 224, 232))
        d.rectangle([cx - mw * 0.25, my + mh * 0.7, cx + mw * 0.25, my + mh * 0.76], fill=(200, 160, 50))
    elif kind == "mountain":
        d.polygon([(mx, my + mh), (mx + mw * 0.35, my + mh * 0.15), (mx + mw * 0.6, my + mh * 0.6), (mx + mw * 0.8, my + mh * 0.3), (mx + mw, my + mh)], fill=rng.choice(PAL))
    else:
        kb.motif(d, kind, mx, my, mw, mh, rng, PAL)
    kb.scribble(d, x0 + w * 0.08, y0 + h * 0.06, w * 0.84, h * 0.16, rng.choice([(250, 250, 250), (250, 220, 60), (240, 60, 50)]), rng)


def item(d, kind, x0, y0, w, h, rng):
    """One face-out item, x0, y0 = top-left, in supersampled pixels."""
    if kind == "game16":
        # a cardboard cartridge box: a coloured band across the top, art below
        band = rng.choice([(20, 20, 24), (200, 200, 204), (230, 230, 226), (180, 30, 36)])
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=band)
        cover_art(d, x0 + w * 0.05, y0 + h * 0.13, w * 0.9, h * 0.82, rng)
        d.rectangle([x0 + w * 0.06, y0 + h * 0.03, x0 + w * 0.45, y0 + h * 0.09], fill=rng.choice([(250, 250, 250), (220, 40, 40)]))
    elif kind == "game32":
        # a jewel case or long case: dark rim, art inside, a spine shadow on the left
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=(18, 18, 20))
        cover_art(d, x0 + w * 0.08, y0 + h * 0.04, w * 0.88, h * 0.92, rng)
        d.rectangle([x0, y0, x0 + w * 0.07, y0 + h], fill=(10, 10, 12))
        d.line([x0 + w * 0.2, y0 + h * 0.9, x0 + w * 0.6, y0 + h * 0.1], fill=(255, 255, 255), width=max(1, int(w * 0.02)))
    elif kind == "pc":
        cover_art(d, x0, y0, w, h, rng)
        d.rectangle([x0, y0 + h * 0.86, x0 + w, y0 + h], fill=rng.choice([(250, 250, 250), (20, 20, 24), (220, 40, 40)]))
        if rng.random() < 0.4:
            kb.burst(d, x0 + w * 0.8, y0 + h * 0.25, min(w, h) * 0.12, (250, 220, 60), rng, (200, 30, 30))
    elif kind == "book":
        base = rng.choice([(250, 250, 248), (240, 200, 40), (20, 20, 24), (40, 90, 200), (220, 40, 40)])
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=base)
        cover_art(d, x0 + w * 0.08, y0 + h * 0.3, w * 0.84, h * 0.6, rng)
        kb.scribble(d, x0 + w * 0.08, y0 + h * 0.06, w * 0.84, h * 0.18, (20, 20, 24) if sum(base) > 400 else (250, 250, 250), rng, lines=2)
    elif kind == "acc":
        # a blister card on a peg: hang hole, header, the controller or cable in its bubble
        base = rng.choice([(20, 40, 120), (200, 30, 36), (20, 20, 24), (240, 200, 40), (250, 250, 250)])
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=base)
        d.ellipse([x0 + w / 2 - 4 * SS, y0 + 3 * SS, x0 + w / 2 + 4 * SS, y0 + 8 * SS], fill=GAP)
        kb.scribble(d, x0 + w * 0.1, y0 + h * 0.12, w * 0.8, h * 0.12, (250, 250, 250) if sum(base) < 500 else (20, 20, 24), rng)
        bx0, by0, bx1, by1 = x0 + w * 0.12, y0 + h * 0.32, x0 + w * 0.88, y0 + h * 0.94
        d.rounded_rectangle([bx0, by0, bx1, by1], radius=w * 0.08, fill=(200, 204, 210))
        pad = rng.choice(["pad", "cable", "card"])
        cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
        if pad == "pad":
            pw, ph = (bx1 - bx0) * 0.8, (by1 - by0) * 0.4
            col = rng.choice([(40, 40, 44), (120, 120, 126), (210, 210, 206)])
            d.rounded_rectangle([cx - pw / 2, cy - ph / 2, cx + pw / 2, cy + ph / 2], radius=ph * 0.45, fill=col)
            d.rectangle([cx - pw * 0.34, cy - ph * 0.08, cx - pw * 0.18, cy + ph * 0.08], fill=(20, 20, 20))
            d.rectangle([cx - pw * 0.30, cy - ph * 0.22, cx - pw * 0.22, cy + ph * 0.22], fill=(20, 20, 20))
            for k in range(2):
                d.ellipse([cx + pw * (0.14 + k * 0.13), cy - ph * 0.1, cx + pw * (0.23 + k * 0.13), cy + ph * 0.16], fill=rng.choice([(200, 30, 30), (20, 20, 20), (90, 90, 96)]))
            d.line([cx, cy - ph / 2, cx, by0 + 2], fill=(30, 30, 30), width=max(1, SS))
        elif pad == "cable":
            for k in range(4):
                d.arc([bx0 + 4 + k * 2, by0 + 4 + k * 3, bx1 - 4 - k * 2, by1 - 4 - k * 3], 0, 360, fill=(30, 30, 34), width=max(2, SS * 2))
        else:
            d.rectangle([cx - (bx1 - bx0) * 0.3, cy - (by1 - by0) * 0.2, cx + (bx1 - bx0) * 0.3, cy + (by1 - by0) * 0.2], fill=rng.choice(PAL))
        d.line([bx0 + 4, by1 - 6, bx0 + (bx1 - bx0) * 0.3, by0 + 6], fill=(255, 255, 255), width=SS)
    elif kind == "cd":
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=(16, 16, 18))
        cover_art(d, x0 + w * 0.1, y0 + h * 0.03, w * 0.88, h * 0.94, rng)
        d.rectangle([x0, y0, x0 + w * 0.08, y0 + h], fill=(28, 28, 30))
        if rng.random() < 0.3:
            # a price sticker in the corner
            d.rectangle([x0 + w * 0.68, y0 + h * 0.06, x0 + w * 0.94, y0 + h * 0.2], fill=(250, 250, 250))
            d.line([x0 + w * 0.71, y0 + h * 0.13, x0 + w * 0.9, y0 + h * 0.13], fill=(200, 30, 30), width=SS)
        d.line([x0 + w * 0.3, y0 + h * 0.95, x0 + w * 0.75, y0 + h * 0.05], fill=(255, 255, 255), width=SS)
    elif kind == "tape":
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=(18, 18, 20))
        cover_art(d, x0 + w * 0.06, y0 + h * 0.04, w * 0.88, h * 0.92, rng)
        d.line([x0 + w * 0.2, y0 + h * 0.95, x0 + w * 0.8, y0 + h * 0.05], fill=(255, 255, 255), width=SS)


SIZES = {  # kind -> (width m range, height m range)
    "game16": ((0.13, 0.14), (0.18, 0.19)), "game32": ((0.14, 0.145), (0.125, 0.21)),
    "pc": ((0.19, 0.24), (0.235, 0.29)), "book": ((0.20, 0.215), (0.25, 0.28)),
    "acc": ((0.15, 0.20), (0.22, 0.28)), "cd": ((0.142, 0.142), (0.125, 0.125)),
    "tape": ((0.071, 0.071), (0.11, 0.11)),
}
MIX = {"games": ["game16", "game16", "game32"], "pc": ["pc"], "books": ["book"], "acc": ["acc"], "cd": ["cd"], "tape": ["tape"]}


def stock(sheet, seed):
    """One stock sheet: rows of face-out items, bottom-aligned, with runs of the same item
    as a stocked wall has them, a shadow from the shelf above."""
    rows, rh_m = ROWS[sheet]
    W, H = 512 * SS, 1024 * SS
    rh = H // rows
    rng = random.Random(seed)
    im = Image.new("RGB", (W, H), GAP)
    d = ImageDraw.Draw(im)
    for r in range(rows):
        ytop = r * rh
        x = 2 * SS
        while x < W - 20 * SS:
            kind = rng.choice(MIX[sheet])
            wr, hr = SIZES[kind]
            w = int(rng.uniform(*wr) * PXM * SS)
            h = int(min(rng.uniform(*hr) * PXM * SS, rh - 4 * SS))
            faces = rng.choice([1, 1, 2, 2, 3])
            s = rng.randint(0, 10 ** 9)
            gap = int(rng.uniform(0.004, 0.012) * PXM * SS)
            for _ in range(faces):
                if x + w > W - 2 * SS:
                    break
                item(d, kind, x, ytop + rh - h - 2 * SS, w, h, random.Random(s))
                x += w + gap
            if rng.random() < 0.06:
                x += int(0.1 * PXM * SS)   # a sold-out gap
    im = im.resize((512, 1024), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32)
    rhp = 1024 // rows
    for r in range(rows):
        y0 = r * rhp
        n = max(6, rhp // 5)
        a[y0:y0 + n] *= np.linspace(0.6, 1.0, n)[:, None, None]
    a += kb.noise(512, 1024, 2.5, seed)[..., None]
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "stock_" + sheet, 192)


def bin_tops():
    """512 x 256 = 1.0 m x 0.5 m: CDs filed upright in a browser bin seen from above and in
    front: the tops of jewel cases (thin dark lines with a lighter spine), every so often a
    white divider card standing taller, the front case tipped forward showing its cover."""
    W, H = 512 * SS, 256 * SS
    rng = random.Random(5)
    im = Image.new("RGB", (W, H), (30, 30, 32))
    d = ImageDraw.Draw(im)
    for col in range(4):
        x0, x1 = col * W // 4 + 4 * SS, (col + 1) * W // 4 - 4 * SS
        y = 6 * SS
        while y < H - 70 * SS:
            c = rng.choice(PAL)
            d.rectangle([x0, y, x1, y + 3 * SS], fill=(14, 14, 16))
            d.rectangle([x0, y + 3 * SS, x1, y + 5 * SS], fill=tuple(int(v * 0.7) for v in c))
            y += 5 * SS
            if rng.random() < 0.05:
                d.rectangle([x0, y, x1, y + 6 * SS], fill=(246, 246, 240))
                kb.scribble(d, x0 + 10 * SS, y + SS, (x1 - x0) * 0.5, 4 * SS, (30, 30, 30), rng)
                y += 7 * SS
        cover_art(d, x0, H - 68 * SS, x1 - x0, 66 * SS, rng)
    im = im.resize((512, 256), Image.LANCZOS)
    save(kb.grain(im, 2, 6), "bin_tops", 128)


# ------------------------------------------------------------------ signs
BB_HEADERS = ["16-BIT", "32-BIT", "CD-ROM", "PC GAMES", "FAMILY", "EDUCATION", "VALUE ZONE", "ACCESSORIES", "HANDHELD", "BOOKS", "NEW RELEASES", "8-BIT"]
SS_HEADERS = ["ROCK", "POP", "R & B", "COUNTRY", "RAP", "JAZZ", "CLASSICAL", "SOUNDTRACKS", "CAJUN & ZYDECO", "GOSPEL", "NEW RELEASES", "CASSETTES"]


def headers(name, words, bg, fg, rule=None):
    """The lit header boxes over the wall bays: 12 faces of 512 x 128 px (1.22 m x 0.30 m)."""
    W, H = 512, 1536
    im = Image.new("RGB", (W * SS, H * SS), bg)
    d = ImageDraw.Draw(im)
    size = 120 * SS
    for word in words:
        while size > 10:
            l, t_, r_, b_ = d.textbbox((0, 0), word, font=ImageFont.truetype(BOLD, size))
            if r_ - l <= (W - 72) * SS and b_ - t_ <= 74 * SS:
                break
            size -= 2
    for k, word in enumerate(words):
        y0 = k * 128 * SS
        d.rectangle([0, y0, W * SS, y0 + 128 * SS], fill=bg)
        if rule:
            d.rectangle([0, y0 + 112 * SS, W * SS, y0 + 120 * SS], fill=rule)
        # one letter height for every word (the video: one big word per header box)
        kb.fit_text(d, word, (36 * SS, y0 + 26 * SS, (W - 36) * SS, y0 + 100 * SS), BOLD, fg, max_size=size)
    im = im.resize((W, H), Image.LANCZOS)
    save(kb.grain(im, 1.2, 33), name, 32)


def release_board():
    """Babbage's yellow new-release board on the cash-wrap wall (video 0:22-6:32): a red head,
    then rows of titles with their street dates. 512 x 640 px = 0.8 m x 1.0 m."""
    W, H = 512 * SS, 640 * SS
    im = Image.new("RGB", (W, H), (250, 222, 60))
    d = ImageDraw.Draw(im)
    rng = random.Random(14)
    d.rectangle([0, 0, W, 92 * SS], fill=(214, 34, 40))
    kb.fit_text(d, "NEW RELEASES", (20 * SS, 10 * SS, W - 20 * SS, 82 * SS), BOLD, (255, 255, 255))
    f = ImageFont.truetype(BOLD, 30 * SS)
    for j in range(12):
        y = 108 * SS + j * 43 * SS
        kb.scribble(d, 24 * SS, y + 6 * SS, rng.uniform(220, 330) * SS, 24 * SS, (30, 30, 34), rng)
        # weekly Tuesday street dates, spring 1995 (period-art-director, Oct 6)
        d.text((W - 150 * SS, y), ["3-07", "3-14", "3-21", "3-28", "4-04", "4-11", "4-18", "4-25", "5-02", "5-09", "5-16", "5-23"][j], font=f, fill=(200, 30, 36))
        d.line([18 * SS, y + 40 * SS, W - 18 * SS, y + 40 * SS], fill=(214, 180, 40), width=SS)
    d.rectangle([0, 0, W - 1, H - 1], outline=(150, 20, 24), width=6 * SS)
    im = im.resize((512, 640), Image.LANCZOS)
    save(kb.grain(im, 1.5, 15), "release", 64)


def bb_posters():
    """512 x 512, 2 x 2: the red price poster on the chrome stand (video 7:00, 20:06; a
    generic system, no brand; $299.99 is the fall 1995 price of a 32-bit system), a yellow
    'SALE' hanging card, an orange '$19.99' card and a 'GIFT CERTIFICATES' card (the video's
    trade-in card is 1997: left out of the 1995 store)."""
    N = 512 * SS
    h = N // 2
    im = Image.new("RGB", (N, N), (0, 0, 0))
    d = ImageDraw.Draw(im)
    # (0,0) the red poster
    d.rectangle([0, 0, h, h], fill=(214, 60, 30))
    kb.fit_text(d, "new low price", (16 * SS, 8 * SS, h - 16 * SS, 46 * SS), BOLD, (255, 236, 120))
    kb.fit_text(d, "32-BIT SYSTEM", (16 * SS, 54 * SS, h - 16 * SS, 92 * SS), BOLD, (255, 255, 255))
    kb.fit_text(d, "$299", (16 * SS, 98 * SS, h - 70 * SS, 230 * SS), BOLD, (255, 222, 40))
    kb.fit_text(d, "99", (h - 68 * SS, 104 * SS, h - 14 * SS, 150 * SS), BOLD, (255, 222, 40))
    # (1,0) yellow SALE
    d.rectangle([h, 0, N, h], fill=(250, 214, 40))
    d.rectangle([h, 0, N, h * 0.28], fill=(214, 34, 40))
    kb.fit_text(d, "HOT", (h + 20 * SS, 8 * SS, N - 20 * SS, h * 0.26), BOLD, (255, 255, 255))
    kb.fit_text(d, "SALE", (h + 14 * SS, h * 0.32, N - 14 * SS, h - 10 * SS), BOLD, (214, 34, 40))
    # (0,1) orange price card
    d.rectangle([0, h, h, N], fill=(240, 120, 30))
    kb.fit_text(d, "ONLY", (20 * SS, h + 8 * SS, h - 20 * SS, h + h * 0.24), BOLD, (255, 255, 255))
    kb.fit_text(d, "$19.99", (14 * SS, h + h * 0.28, h - 14 * SS, N - 14 * SS), BOLD, (255, 255, 255))
    # (1,1) trade-in card
    d.rectangle([h, h, N, N], fill=(250, 250, 246))
    d.rectangle([h, h, N, h + h * 0.3], fill=(150, 30, 40))
    kb.fit_text(d, "GIFT", (h + 20 * SS, h + 10 * SS, N - 20 * SS, h + h * 0.26), BOLD, (255, 255, 255))
    kb.fit_text(d, "CERTIFICATES", (h + 14 * SS, h + h * 0.36, N - 14 * SS, N - 20 * SS), BOLD, (150, 30, 40))
    im = im.resize((512, 512), Image.LANCZOS)
    save(kb.grain(im, 1.5, 16), "bb_cards", 64)


def ticket_board():
    """Sound Shop's box-office board behind the registers (Steven: the counter sold concert
    tickets; a generic board, no ticket company's name or logo). 1024 x 512 px = 2.0 m x
    1.0 m: a black board, a red TICKETS head, white show lines with dates, a seating-chart
    panel and an 'ON SALE NOW' flash."""
    W, H = 1024 * SS, 512 * SS
    im = Image.new("RGB", (W, H), (20, 20, 24))
    d = ImageDraw.Draw(im)
    rng = random.Random(19)
    d.rectangle([0, 0, W, 96 * SS], fill=(200, 26, 34))
    kb.fit_text(d, "TICKETS", (30 * SS, 8 * SS, 560 * SS, 88 * SS), BOLD, (255, 255, 255))
    kb.fit_text(d, "CONCERT BOX OFFICE", (580 * SS, 24 * SS, W - 30 * SS, 76 * SS), BOLD, (255, 230, 120))
    f = ImageFont.truetype(BOLD, 26 * SS)
    # real 1995 weekdays, in date order (period-art-director, Oct 6)
    shows = ["FRI 3/3", "SAT 3/11", "SUN 3/19", "FRI 4/7", "SAT 4/8", "SUN 4/9", "FRI 5/19", "SAT 5/27"]
    for j in range(8):
        y = 116 * SS + j * 46 * SS
        kb.scribble(d, 30 * SS, y + 6 * SS, rng.uniform(260, 380) * SS, 26 * SS, (250, 250, 246), rng)
        d.text((470 * SS, y + 4 * SS), shows[j], font=f, fill=(255, 210, 60))
        if j % 3 == 0:
            d.rectangle([610 * SS, y + 6 * SS, 700 * SS, y + 34 * SS], fill=(200, 26, 34))
            d.text((616 * SS, y + 6 * SS), "NEW", font=f, fill=(255, 255, 255))
    # seating chart
    cx, cy = 860 * SS, 330 * SS
    d.rectangle([730 * SS, 120 * SS, 1000 * SS, 480 * SS], fill=(240, 240, 236))
    d.rectangle([800 * SS, 140 * SS, 920 * SS, 170 * SS], fill=(40, 40, 44))
    for k, c in enumerate([(220, 40, 40), (40, 90, 200), (60, 170, 90), (240, 200, 40)]):
        r = (70 + k * 40) * SS
        d.arc([cx - r, cy - r - 120 * SS, cx + r, cy + r - 120 * SS], 30, 150, fill=c, width=22 * SS)
    d.rectangle([30 * SS, 486 * SS, 700 * SS, 506 * SS], fill=(20, 20, 24))
    kb.fit_text(d, "ON SALE NOW AT THIS COUNTER", (30 * SS, 482 * SS, 700 * SS, 508 * SS), BOLD, (255, 210, 60))
    im = im.resize((1024, 512), Image.LANCZOS)
    save(kb.grain(im, 1.5, 20), "tickets", 96)


def ss_posters():
    """1024 x 512, four album posters (0.6 m x 0.9 m each, 256 x 384 px) in a row with a
    long banner strip under them: the big posters hung high round Sound Shop (Hammond 1993)."""
    W, H = 1024 * SS, 512 * SS
    im = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(im)
    rng = random.Random(22)
    for k in range(4):
        x0 = k * 256 * SS
        cover_art(d, x0, 0, 256 * SS, 384 * SS, rng)
        d.rectangle([x0, 330 * SS, x0 + 256 * SS, 384 * SS], fill=rng.choice([(20, 20, 24), (250, 250, 246), (200, 26, 34)]))
        kb.scribble(d, x0 + 20 * SS, 342 * SS, 200 * SS, 30 * SS, rng.choice([(250, 220, 60), (250, 250, 250), (220, 40, 40)]), rng)
        d.rectangle([x0, 0, x0 + 256 * SS - 1, 384 * SS - 1], outline=(250, 250, 246), width=4 * SS)
    # the banner strip: 'NEW MUSIC' generic
    d.rectangle([0, 384 * SS, W, H], fill=(200, 26, 34))
    kb.fit_text(d, "NEW MUSIC  ·  CDs  ·  CASSETTES  ·  TICKETS", (30 * SS, 400 * SS, W - 30 * SS, 496 * SS), BOLD, (255, 255, 255))
    im = im.resize((1024, 512), Image.LANCZOS)
    save(kb.grain(im, 1.5, 23), "ss_posters", 128)


def ss_cards():
    """512 x 512, 2 x 2: island header cards: 'NEW RELEASES', 'TOP 30', 'SALE $9.99',
    'CASSETTES $7.99'."""
    N = 512 * SS
    h = N // 2
    im = Image.new("RGB", (N, N), (0, 0, 0))
    d = ImageDraw.Draw(im)
    spec = [((200, 26, 34), (255, 255, 255), "NEW", "RELEASES"), ((20, 20, 24), (255, 210, 60), "TOP", "30"),
            ((250, 214, 40), (200, 26, 34), "SALE", "$9.99"), ((40, 80, 180), (255, 255, 255), "CASSETTES", "$7.99")]
    for k, (bg, fg, a, b2) in enumerate(spec):
        x0, y0 = (k % 2) * h, (k // 2) * h
        d.rectangle([x0, y0, x0 + h, y0 + h], fill=bg)
        kb.fit_text(d, a, (x0 + 16 * SS, y0 + 14 * SS, x0 + h - 16 * SS, y0 + h * 0.42), BOLD, fg)
        kb.fit_text(d, b2, (x0 + 16 * SS, y0 + h * 0.48, x0 + h - 16 * SS, y0 + h - 16 * SS), BOLD, fg)
    im = im.resize((512, 512), Image.LANCZOS)
    save(kb.grain(im, 1.5, 24), "ss_cards", 64)


def screens():
    """256 x 128: left, an invented racing game on Babbage's demo kiosk; right, a register display."""
    im = Image.new("RGB", (256, 128), (0, 0, 0))
    d = ImageDraw.Draw(im)
    rng = random.Random(31)
    d.rectangle([0, 0, 127, 60], fill=(90, 150, 230))
    d.rectangle([0, 60, 127, 127], fill=(60, 140, 70))
    d.polygon([(54, 60), (74, 60), (127, 127), (0, 127)], fill=(80, 80, 86))
    for k in range(6):
        y = 64 + k * k * 2
        d.rectangle([62, y, 66, y + 2 + k], fill=(250, 250, 250))
    d.polygon([(0, 60), (20, 40), (44, 60)], fill=(120, 110, 140)); d.polygon([(80, 60), (110, 34), (127, 50), (127, 60)], fill=(110, 100, 130))
    d.rectangle([50, 100, 78, 118], fill=(220, 40, 40)); d.rectangle([54, 94, 74, 102], fill=(150, 200, 240))
    d.rectangle([4, 4, 34, 9], fill=(250, 250, 250)); d.rectangle([94, 4, 124, 9], fill=(250, 220, 60))
    d.rectangle([128, 0, 255, 127], fill=(6, 14, 8))
    for j in range(7):
        y = 12 + j * 15
        x = 140
        for _ in range(rng.randint(2, 4)):
            w = rng.randint(8, 30)
            d.rectangle([x, y, x + w, y + 6], fill=(70, 230, 110))
            x += w + 8
    a = np.asarray(im).astype(np.float32)
    a[::2] *= 0.82
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "screens", 48)


if __name__ == "__main__":
    carpet_grey(); vinyl(); slatwall()
    counter_front("bb_counter", [120, 24, 36])
    counter_front("ss_counter", [200, 26, 34], [30, 30, 34])
    for i, s in enumerate(ROWS):
        stock(s, 300 + i)
    bin_tops()
    headers("bb_headers", BB_HEADERS, (246, 246, 242), (70, 70, 74))
    headers("ss_headers", SS_HEADERS, (246, 246, 242), (190, 24, 34), rule=(30, 30, 34))
    release_board(); bb_posters(); ticket_board(); ss_posters(); ss_cards(); screens()
    print("wrote tex/md/*.png")
