"""Textures for the Radio Shack interior (tools/stores/small/radio_shack.gd), from the 1999 mall
store video Steven sent on Oct 20, 2026 ("Christmas shopping at RadioShack in 1999"):

- tex/md/stock_rsphones.png: shelves of out-of-box electronics, mostly black (corded and cordless
  phones, answering machines, clock radios, scanners), each with a small white price tag.
- tex/md/stock_rsboxes.png: boxed goods: R/C trucks in purple-and-blue boxes with yellow flames,
  black-and-red electronics boxes.
- tex/md/stock_rsparts.png: blister cards on white pegboard (cables, adapters, plugs, parts).
- tex/md/stock_rsbatt.png: battery cards, red and black.
- tex/sm/rs_valance.png: the black-and-white striped valance over the wall sections.
- tex/sm/rs_signs.png: header words (PowerZone, Telephones, Cellular, Computers) in the store's
  red-and-black, and promo cards.
- tex/sm/rs_screen.png: the POS screen (a blue window, a white panel).

Every product, package and name is invented; no real brand mark other than the store's own words.
Stock sheets follow the media kit's layout (tools/stores/media/paint.py): 512 x 1024 = 1.22 m x
8 rows of 0.305 m, items bottom-aligned on each row.
  python3 tools/stores/small/paint_rs.py   (from the project folder)
"""
import os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "kay_bee"))
import paint_store as kb   # noqa: E402

ROOT = os.path.join(HERE, "..", "..", "..", "tex")
SS = 2
PXM = 512 / 1.22


def save(im, sub, name, colors=0):
    im = im.convert("RGB")
    if colors:
        im = im.quantize(colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    os.makedirs(os.path.join(ROOT, sub), exist_ok=True)
    im.save(os.path.join(ROOT, sub, name + ".png"), optimize=True)


def tag(d, x0, y1, w, rng):
    """A small white shelf tag at the item's foot."""
    tw = max(10 * SS, min(w * 0.45, 22 * SS))
    th = 9 * SS
    tx = x0 + rng.uniform(0.05, 0.4) * w
    d.rectangle([tx, y1 - th, tx + tw, y1], fill=(246, 246, 240))
    d.line([tx + 2 * SS, y1 - th * 0.55, tx + tw - 3 * SS, y1 - th * 0.55], fill=(200, 30, 30), width=SS)


def item(d, kind, x0, y0, w, h, rng):
    x1, y1 = x0 + w, y0 + h
    blk = rng.choice([(22, 22, 24), (30, 30, 34), (40, 40, 44), (22, 22, 24)])
    if kind == "phone":
        body = rng.choice([blk, blk, (210, 206, 194), (120, 122, 128)])
        # base: a trapezoid, handset lying on top, a keypad
        d.polygon([(x0 + w * 0.05, y1), (x1 - w * 0.05, y1), (x1 - w * 0.15, y0 + h * 0.35), (x0 + w * 0.15, y0 + h * 0.35)], fill=body)
        d.rounded_rectangle([x0 + w * 0.08, y0 + h * 0.1, x1 - w * 0.08, y0 + h * 0.42], radius=h * 0.14, fill=tuple(max(0, c - 10) for c in body))
        kc = (180, 180, 176) if sum(body) < 300 else (60, 60, 62)
        for r in range(3):
            for c in range(3):
                kx = x0 + w * (0.36 + c * 0.1)
                ky = y0 + h * (0.5 + r * 0.14)
                d.rectangle([kx, ky, kx + w * 0.06, ky + h * 0.08], fill=kc)
        if rng.random() < 0.4:
            d.rectangle([x0 + w * 0.2, y0 + h * 0.5, x0 + w * 0.32, y0 + h * 0.62], fill=(90, 150, 110))
    elif kind == "cordless":
        # an upright handset in its base, antenna up
        d.rectangle([x0 + w * 0.1, y0 + h * 0.75, x1 - w * 0.1, y1], fill=blk)
        d.rounded_rectangle([x0 + w * 0.3, y0 + h * 0.12, x1 - w * 0.3, y0 + h * 0.85], radius=w * 0.08, fill=(40, 40, 44))
        d.line([x1 - w * 0.36, y0, x1 - w * 0.36, y0 + h * 0.15], fill=(20, 20, 20), width=2 * SS)
        for r in range(4):
            d.line([x0 + w * 0.38, y0 + h * (0.45 + r * 0.08), x1 - w * 0.38, y0 + h * (0.45 + r * 0.08)], fill=(150, 150, 150), width=SS)
    elif kind == "machine":
        # answering machine / clock radio: a black slab, a speaker grille, a window, buttons
        d.rounded_rectangle([x0, y0 + h * 0.15, x1, y1], radius=h * 0.12, fill=blk)
        gx = x0 + w * 0.08
        for r in range(4):
            d.line([gx, y0 + h * (0.35 + r * 0.14), gx + w * 0.3, y0 + h * (0.35 + r * 0.14)], fill=(70, 70, 74), width=SS)
        win = rng.choice([(40, 120, 70), (160, 40, 30), (70, 80, 90)])
        d.rectangle([x0 + w * 0.5, y0 + h * 0.32, x0 + w * 0.88, y0 + h * 0.58], fill=win)
        for k in range(4):
            d.rectangle([x0 + w * (0.5 + k * 0.1), y0 + h * 0.68, x0 + w * (0.56 + k * 0.1), y0 + h * 0.8], fill=(150, 150, 150))
    elif kind == "scanner":
        d.rounded_rectangle([x0 + w * 0.1, y0 + h * 0.25, x1 - w * 0.1, y1], radius=w * 0.15, fill=blk)
        d.line([x0 + w * 0.3, y0, x0 + w * 0.3, y0 + h * 0.3], fill=(16, 16, 16), width=3 * SS)
        d.rectangle([x0 + w * 0.22, y0 + h * 0.35, x1 - w * 0.22, y0 + h * 0.48], fill=(120, 150, 90))
        for r in range(4):
            for c in range(3):
                d.rectangle([x0 + w * (0.22 + c * 0.2), y0 + h * (0.56 + r * 0.09), x0 + w * (0.34 + c * 0.2), y0 + h * (0.61 + r * 0.09)], fill=(110, 110, 110))
    elif kind == "boxed_rc":
        # an R/C truck box: purple to blue, yellow flames, a truck, a yellow title
        top = rng.choice([(110, 40, 150), (40, 60, 170), (130, 30, 120)])
        bot = (30, 50, 150)
        for k in range(int(h)):
            f = k / max(1, h)
            d.line([x0, y0 + k, x1, y0 + k], fill=tuple(int(top[i] * (1 - f) + bot[i] * f) for i in range(3)))
        for k in range(5):
            fx = x0 + w * (0.1 + k * 0.17)
            d.polygon([(fx, y1 - h * 0.08), (fx + w * 0.08, y0 + h * 0.45), (fx + w * 0.16, y1 - h * 0.08)], fill=(250, 150, 20))
            d.polygon([(fx + w * 0.03, y1 - h * 0.08), (fx + w * 0.08, y0 + h * 0.6), (fx + w * 0.13, y1 - h * 0.08)], fill=(250, 220, 40))
        tc = rng.choice([(230, 190, 30), (40, 40, 44), (220, 40, 30)])
        d.rounded_rectangle([x0 + w * 0.22, y0 + h * 0.48, x0 + w * 0.78, y0 + h * 0.75], radius=h * 0.05, fill=tc)
        d.rectangle([x0 + w * 0.32, y0 + h * 0.36, x0 + w * 0.6, y0 + h * 0.5], fill=tc)
        for cx in (0.32, 0.68):
            d.ellipse([x0 + w * (cx - 0.1), y0 + h * 0.62, x0 + w * (cx + 0.1), y0 + h * 0.92], fill=(14, 14, 14))
        kb.scribble(d, x0 + w * 0.08, y0 + h * 0.07, w * 0.6, h * 0.2, (250, 210, 40), rng)
        d.rectangle([x0 + w * 0.04, y0 + h * 0.04, x0 + w * 0.2, y0 + h * 0.12], fill=(250, 250, 250))
    elif kind == "boxed":
        base = rng.choice([(20, 20, 24), (20, 20, 24), (200, 30, 36), (240, 240, 236), (30, 60, 140)])
        d.rectangle([x0, y0, x1, y1], fill=base)
        d.rectangle([x0, y0 + h * 0.78, x1, y0 + h * 0.86], fill=(200, 30, 36) if base != (200, 30, 36) else (20, 20, 24))
        dev = rng.choice([(150, 150, 154), (40, 40, 44), (210, 206, 194)])
        d.rounded_rectangle([x0 + w * 0.15, y0 + h * 0.3, x0 + w * 0.7, y0 + h * 0.7], radius=h * 0.06, fill=dev)
        d.rectangle([x0 + w * 0.2, y0 + h * 0.36, x0 + w * 0.4, y0 + h * 0.5], fill=(90, 160, 200))
        kb.scribble(d, x0 + w * 0.08, y0 + h * 0.07, w * 0.84, h * 0.16, (250, 250, 250) if sum(base) < 400 else (20, 20, 24), rng)
    elif kind == "blister":
        base = rng.choice([(236, 236, 232), (236, 236, 232), (190, 194, 200), (20, 20, 24), (200, 30, 36)])
        d.rectangle([x0, y0, x1, y1], fill=base)
        d.rectangle([x0, y0, x1, y0 + h * 0.2], fill=rng.choice([(200, 30, 36), (20, 20, 24), (30, 60, 140)]))
        d.ellipse([x0 + w / 2 - 3 * SS, y0 + 3 * SS, x0 + w / 2 + 3 * SS, y0 + 7 * SS], fill=(230, 230, 226))
        bx0, by0, bx1, by1 = x0 + w * 0.14, y0 + h * 0.3, x1 - w * 0.14, y1 - h * 0.08
        d.rounded_rectangle([bx0, by0, bx1, by1], radius=w * 0.08, fill=(214, 218, 222))
        cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
        what = rng.choice(["coil", "plug", "chip", "adapter"])
        if what == "coil":
            col = rng.choice([(30, 30, 34), (220, 220, 216), (40, 60, 160)])
            for k in range(3):
                d.arc([bx0 + 3 + k * 3, by0 + 3 + k * 4, bx1 - 3 - k * 3, by1 - 3 - k * 4], 0, 360, fill=col, width=2 * SS)
        elif what == "plug":
            d.rectangle([cx - w * 0.08, cy - h * 0.12, cx + w * 0.08, cy + h * 0.1], fill=rng.choice([(200, 170, 60), (30, 30, 34), (180, 180, 184)]))
            d.line([cx, cy + h * 0.1, cx, by1 - 3], fill=(30, 30, 34), width=2 * SS)
        elif what == "chip":
            d.rectangle([cx - w * 0.15, cy - h * 0.06, cx + w * 0.15, cy + h * 0.06], fill=(24, 24, 26))
            for k in range(5):
                d.line([cx - w * 0.12 + k * w * 0.06, cy - h * 0.1, cx - w * 0.12 + k * w * 0.06, cy + h * 0.1], fill=(190, 190, 190), width=SS)
        else:
            d.rounded_rectangle([cx - w * 0.18, cy - h * 0.15, cx + w * 0.18, cy + h * 0.15], radius=4, fill=(32, 32, 36))
            d.line([cx + w * 0.18, cy, bx1 - 3, cy], fill=(32, 32, 36), width=2 * SS)
        d.line([bx0 + 3, by1 - 5, bx0 + (bx1 - bx0) * 0.3, by0 + 5], fill=(255, 255, 255), width=SS)
    elif kind == "battery":
        base = rng.choice([(200, 30, 36), (20, 20, 24), (200, 30, 36), (230, 180, 30)])
        d.rectangle([x0, y0, x1, y1], fill=base)
        d.ellipse([x0 + w / 2 - 3 * SS, y0 + 3 * SS, x0 + w / 2 + 3 * SS, y0 + 7 * SS], fill=(230, 230, 226))
        kb.scribble(d, x0 + w * 0.1, y0 + h * 0.1, w * 0.8, h * 0.12, (250, 250, 250) if base != (230, 180, 30) else (20, 20, 24), rng)
        n = rng.choice([2, 4, 4])
        cw = w * 0.7 / n
        for k in range(n):
            bx = x0 + w * 0.15 + k * cw
            d.rectangle([bx + 1, y0 + h * 0.38, bx + cw - 2, y1 - h * 0.1], fill=(30, 30, 30))
            d.rectangle([bx + 1, y0 + h * 0.38, bx + cw - 2, y0 + h * 0.52], fill=(200, 160, 50))
            d.rectangle([bx + cw * 0.35, y0 + h * 0.34, bx + cw * 0.6, y0 + h * 0.38], fill=(180, 180, 180))


SIZES = {
    "phone": ((0.19, 0.25), (0.10, 0.15)), "cordless": ((0.12, 0.16), (0.2, 0.27)),
    "machine": ((0.2, 0.3), (0.07, 0.12)), "scanner": ((0.07, 0.08), (0.2, 0.26)),
    "boxed_rc": ((0.42, 0.55), (0.24, 0.29)), "boxed": ((0.2, 0.36), (0.14, 0.27)),
    "blister": ((0.09, 0.13), (0.15, 0.22)), "battery": ((0.09, 0.12), (0.14, 0.18)),
}
SHEETS = {
    "rsphones": (["phone", "phone", "cordless", "machine", "machine", "scanner"], (206, 206, 202), True),
    "rsboxes": (["boxed_rc", "boxed", "boxed", "boxed"], (200, 200, 196), False),
    "rsparts": (["blister"], (232, 232, 228), False),
    "rsbatt": (["battery", "battery", "blister"], (232, 232, 228), False),
}


def stock(sheet, seed):
    kinds, bg, tags = SHEETS[sheet]
    rows = 8
    W, H = 512 * SS, 1024 * SS
    rh = H // rows
    rng = random.Random(seed)
    im = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(im)
    peg = sheet in ("rsparts", "rsbatt")
    if peg:
        # pegboard holes every inch
        step = int(0.0254 * PXM * SS)
        for y in range(step // 2, H, step):
            for x in range(step // 2, W, step):
                d.ellipse([x - SS, y - SS, x + SS, y + SS], fill=(170, 170, 166))
    for r in range(rows):
        ytop = r * rh
        x = 2 * SS
        while x < W - 20 * SS:
            kind = rng.choice(kinds)
            wr, hr = SIZES[kind]
            w = int(rng.uniform(*wr) * PXM * SS)
            h = int(min(rng.uniform(*hr) * PXM * SS, rh - 6 * SS))
            faces = rng.choice([1, 2, 2, 3]) if peg else rng.choice([1, 1, 2])
            s = rng.randint(0, 10 ** 9)
            gap = int(rng.uniform(0.01, 0.03) * PXM * SS)
            if x + w > W - 2 * SS:
                break
            for _ in range(faces):
                if x + w > W - 2 * SS:
                    break
                yb = ytop + rh - 4 * SS
                if peg:
                    yb = ytop + rh * rng.uniform(0.8, 0.95)
                item(d, kind, x, yb - h, w, h, random.Random(s))
                if tags:
                    tag(d, x, ytop + rh - 1 * SS, w, rng)
                x += w + gap
    im = im.resize((512, 1024), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32)
    rhp = 1024 // rows
    if not peg:
        for r in range(rows):
            y0 = r * rhp
            n = max(6, rhp // 6)
            a[y0:y0 + n] *= np.linspace(0.7, 1.0, n)[:, None, None]
    a += kb.noise(512, 1024, 2.0, seed)[..., None]
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "md", "stock_" + sheet, 192)


def valance():
    """256 x 64 = 1.0 m x 0.25 m, tiling along x: black and white diagonal stripes, a black edge."""
    W, H = 256 * SS, 64 * SS
    im = Image.new("RGB", (W, H), (240, 240, 236))
    d = ImageDraw.Draw(im)
    step = W // 8
    for k in range(-4, 12):
        x = k * step
        d.polygon([(x, H), (x + step * 0.5, H), (x + step * 0.5 + H * 0.6, 0), (x + H * 0.6, 0)], fill=(22, 22, 24))
    d.rectangle([0, 0, W, H * 0.08], fill=(20, 20, 22))
    d.rectangle([0, H * 0.92, W, H], fill=(20, 20, 22))
    save(im.resize((256, 64), Image.LANCZOS), "sm", "rs_valance", 32)


def font(size, italic=False):
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf" if italic else "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              os.path.join(HERE, "..", "media", "Nunito-BlackItalic.ttf" if italic else "Nunito-Black.ttf")]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def signs():
    """1024 x 512, four rows of 1024 x 128 (each a 2.4 m x 0.3 m header): PowerZone in white
    italic on red with a black end block; Telephones, Cellular, Computers in red on black.
    The right quarter of rows 2-3 holds two promo cards (white, red headline, grey lines)."""
    W, H = 1024 * SS, 512 * SS
    im = Image.new("RGB", (W, H), (20, 20, 22))
    d = ImageDraw.Draw(im)
    rh = H // 4
    # row 0: PowerZone
    d.rectangle([0, 0, W, rh], fill=(196, 28, 34))
    d.rectangle([0, 0, W * 0.12, rh], fill=(20, 20, 22))
    d.ellipse([W * 0.03, rh * 0.25, W * 0.09, rh * 0.75], fill=(196, 28, 34))
    f = font(int(rh * 0.62), True)
    d.text((W * 0.56, rh * 0.5), "PowerZone", font=f, fill=(250, 250, 250), anchor="mm")
    for i, word in enumerate(["Telephones", "Cellular", "Computers"]):
        y0 = rh * (i + 1)
        d.rectangle([0, y0, W, y0 + rh], fill=(20, 20, 22))
        d.rectangle([0, y0 + rh * 0.86, W, y0 + rh], fill=(196, 28, 34))
        d.text((W * 0.5, y0 + rh * 0.45), word, font=font(int(rh * 0.55), True), fill=(230, 40, 44), anchor="mm")
    save(im.resize((1024, 512), Image.LANCZOS), "sm", "rs_signs", 64)


def cards():
    """512 x 256: two promo cards side by side (white, a red headline, grey lines, a red sale burst)."""
    W, H = 512 * SS, 256 * SS
    im = Image.new("RGB", (W, H), (246, 246, 242))
    d = ImageDraw.Draw(im)
    rng = random.Random(1999)
    for k in range(2):
        x0 = k * W // 2
        d.rectangle([x0 + 4, 4, x0 + W // 2 - 4, H - 4], outline=(200, 200, 196), width=2)
        d.text((x0 + W * 0.25, H * 0.16), "FREE", font=font(int(H * 0.13), True), fill=(200, 30, 36), anchor="mm")
        for r in range(4):
            kb.scribble(d, x0 + W * 0.06, H * (0.3 + r * 0.12), W * 0.38, H * 0.06, (60, 60, 64), rng, lines=1)
        d.rectangle([x0 + W * 0.06, H * 0.82, x0 + W * 0.44, H * 0.92], fill=(200, 30, 36))
    save(im.resize((512, 256), Image.LANCZOS), "sm", "rs_cards", 32)


def screen():
    """256 x 192: the POS screen: a blue field, a white panel at the right, a green line."""
    W, H = 256, 192
    im = Image.new("RGB", (W, H), (40, 70, 170))
    d = ImageDraw.Draw(im)
    d.rectangle([150, 20, 240, 170], fill=(240, 240, 236))
    d.rectangle([14, 20, 140, 40], fill=(120, 200, 110))
    d.rectangle([14, 50, 140, 130], fill=(200, 210, 240))
    d.rectangle([60, 140, 140, 160], fill=(240, 240, 236))
    for r in range(5):
        d.line([160, 50 + r * 18, 230, 50 + r * 18], fill=(120, 120, 130), width=2)
    save(im, "sm", "rs_screen", 32)


if __name__ == "__main__":
    for i, s in enumerate(SHEETS):
        stock(s, 1999 + i)
    valance()
    signs()
    cards()
    screen()
    print("ok")
