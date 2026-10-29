"""Textures for games, inc. (2026, store s52: the old Blockbuster Music box), tools/stores/games_inc/store.gd.
Painted from Steven's Oct 23 2026 footage (IMG_4443 f003-f058, IMG_4444, photo IMG_4445):
wood-look vinyl plank floor, white slatwall, the red-orange upper band with its mustard stripe,
the mustard 6x12 tile portal, the navy "CLAW MANIA" party wall. Writes tex/gi/*.png. Seeded.

  python3 tools/stores/games_inc/paint.py     (from the project folder)
"""
import os, random
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "tex", "gi")
os.makedirs(OUT, exist_ok=True)
random.seed(2026)


def save(im, name):
    im.save(os.path.join(OUT, name + ".png"), optimize=True)
    print(name, im.size)


def plank():
    """Honey-brown LVT planks, 1.2 x 0.18 m, staggered; the texture covers 2.4 x 2.4 m."""
    S = 768
    m_px = S / 2.4
    im = Image.new("RGB", (S, S), "#b98b5c")
    d = ImageDraw.Draw(im)
    pw, ph = 1.2 * m_px, 0.18 * m_px
    row = 0
    y = 0.0
    while y < S:
        x = -(row % 3) * pw / 3.0
        while x < S:
            base = random.choice(["#b98b5c", "#c3966a", "#ad7f52", "#bb8f61", "#a97a4e", "#c79b70"])
            d.rectangle([x, y, x + pw - 1, y + ph - 1], fill=base)
            # grain: faint long streaks
            for _ in range(14):
                gy = y + random.uniform(1, ph - 1)
                gx0 = x + random.uniform(0, pw * 0.5)
                gx1 = gx0 + random.uniform(pw * 0.2, pw * 0.6)
                c = random.choice(["#a3764a", "#8f6540", "#caa078"])
                d.line([gx0, gy, gx1, gy + random.uniform(-1, 1)], fill=c, width=1)
            # a darker seam
            d.line([x, y, x, y + ph], fill="#8a6239", width=1)
            d.line([x, y + ph - 1, x + pw, y + ph - 1], fill="#8a6239", width=1)
            x += pw
        y += ph
        row += 1
    im = im.filter(ImageFilter.GaussianBlur(0.4))
    save(im, "plank")


def slatwall():
    """White slatwall: a groove every 7.6 cm; the texture covers 0.608 x 0.608 m (8 grooves)."""
    S = 512
    im = Image.new("RGB", (S, S), "#f1efea")
    d = ImageDraw.Draw(im)
    g = S / 8
    for k in range(8):
        y = int(k * g + g * 0.5)
        d.rectangle([0, y - 4, S, y + 4], fill="#d8d5cd")
        d.line([0, y - 4, S, y - 4], fill="#bdb9b0")
        d.line([0, y + 4, S, y + 4], fill="#fbfaf7")
    save(im, "slat")


def band():
    """The upper wall band: red-orange with a mustard stripe near its foot; covers 1 x 1 m (y 0..1 = band bottom..top)."""
    S = 256
    im = Image.new("RGB", (S, S), "#d6552b")
    d = ImageDraw.Draw(im)
    # mustard stripe 12 cm tall, 8 cm up from the band's bottom (texture y grows downward: bottom is y = S)
    d.rectangle([0, S - int(0.20 * S), S, S - int(0.08 * S)], fill="#e2a62a")
    save(im, "band")


def tile():
    """Mustard 6x12 inch glazed tile in a running bond; covers 0.6 x 0.6 m."""
    S = 512
    im = Image.new("RGB", (S, S), "#cfa33a")
    d = ImageDraw.Draw(im)
    tw, th = S * 0.3048 / 0.6, S * 0.1524 / 0.6
    y = 0.0
    r = 0
    while y < S:
        x = -(r % 2) * tw / 2
        while x < S:
            c = random.choice(["#cfa33a", "#d4a93f", "#c99c34", "#d7ad46"])
            d.rectangle([x + 1, y + 1, x + tw - 2, y + th - 2], fill=c)
            d.rectangle([x + 3, y + 3, x + tw - 6, y + 6], fill="#e0bb5a")
            x += tw
        y += th
        r += 1
    save(im.filter(ImageFilter.GaussianBlur(0.3)), "tile")


def mural():
    """The party wall: navy with a thin grid and the 'games, inc. CLAW MANIA' lettering block; 4 x 2.6 m."""
    W, H = 1024, 666
    im = Image.new("RGB", (W, H), "#141c3a")
    d = ImageDraw.Draw(im)
    for x in range(0, W, 64):
        d.line([x, 0, x, H], fill="#1c2750")
    for y in range(0, H, 64):
        d.line([0, y, W, y], fill="#1c2750")
    # a lighter "neon" horizon line and the lettering as blocks (no real type: keep it a texture detail)
    d.line([0, H * 0.72, W, H * 0.72], fill="#2fd6c8", width=3)
    d.rounded_rectangle([W * 0.18, H * 0.2, W * 0.82, H * 0.34], radius=14, fill="#f2f2f2")
    d.rounded_rectangle([W * 0.3, H * 0.4, W * 0.7, H * 0.5], radius=10, fill="#49c53c")
    # claw silhouettes
    for cx in (W * 0.12, W * 0.88):
        d.line([cx, H * 0.1, cx, H * 0.55], fill="#5a6ba8", width=5)
        d.arc([cx - 40, H * 0.5, cx + 40, H * 0.68], 0, 180, fill="#5a6ba8", width=5)
    save(im, "mural")


def panel():
    """The white sign panel behind the 'games, inc.' letters, with a faint bevel; 1 x 1 m."""
    S = 256
    im = Image.new("RGB", (S, S), "#f4f3ee")
    save(im, "panel")


if __name__ == "__main__":
    plank(); slatwall(); band(); tile(); mural(); panel()
