"""Textures shared by the clothing stores built from the 1995 North East Mall video
(JW / Jeans West, 5-7-9, County Seat) -> tex/ap/*.png. All original; no brand marks.
  python3 tools/stores/apparel/paint.py   (from the project folder)
"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "..", "tex", "ap"))
SS = 2
BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
BOLD = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

# palettes: JW tops, JW bottoms, 5-7-9 juniors, County Seat denim
PAL = [
    [(196, 170, 120), (110, 90, 60), (40, 40, 44), (230, 226, 214), (60, 80, 120), (120, 40, 40), (80, 96, 70), (150, 130, 100)],
    [(190, 166, 120), (120, 96, 66), (36, 36, 40), (70, 60, 52), (210, 196, 160), (90, 100, 120), (160, 140, 110)],
    [(150, 26, 40), (24, 24, 28), (60, 90, 150), (236, 230, 214), (90, 40, 70), (40, 80, 50), (200, 170, 140), (110, 130, 170)],
    [(54, 78, 128), (78, 104, 150), (40, 54, 92), (120, 140, 170), (236, 234, 228), (30, 30, 34), (140, 40, 40), (98, 120, 160)],
]
PLAID = {0: True, 2: True, 3: True}


def F(path, size):
    return ImageFont.truetype(path, int(size))


def save(im, name, colors=0):
    im = im.convert("RGBA" if im.mode == "RGBA" else "RGB")
    if colors:
        im = im.quantize(colors, method=Image.Quantize.FASTOCTREE if im.mode == "RGBA" else Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(os.path.join(OUT, name + ".png"), optimize=True)


def grain(im, amp, seed):
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    a += np.random.default_rng(seed).normal(0, amp, a.shape[:2])[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def dk(c, f=0.7):
    return tuple(int(v * f) for v in c)


def plaid(d, box, c, r):
    x0, y0, x1, y1 = box
    c2 = dk(c, 0.55)
    c3 = tuple(min(255, int(v * 0.5 + 120)) for v in c)
    for x in range(int(x0), int(x1), 10):
        d.line([(x, y0), (x, y1)], fill=c2, width=3)
    for y in range(int(y0), int(y1), 10):
        d.line([(x0, y), (x1, y)], fill=c2, width=3)
    for x in range(int(x0) + 5, int(x1), 20):
        d.line([(x, y0), (x, y1)], fill=c3, width=1)


def racks():
    """Garments hung side by side on a rail, seen from the side: 4 rows (JW tops, JW
    bottoms, juniors, denim), each 1024 x 256 for 2.0 m x 0.8 m."""
    W, H = 1024, 1024
    im = Image.new("RGB", (W, H), (30, 30, 32))
    d = ImageDraw.Draw(im)
    r = np.random.default_rng(12)
    for row in range(4):
        y0 = row * 256
        d.rectangle([0, y0, W, y0 + 256], fill=(26, 26, 28))
        x = 0
        while x < W:
            w = int(r.uniform(14, 30))
            c = PAL[row][r.integers(len(PAL[row]))]
            top = y0 + 6 + int(r.uniform(0, 8))
            bot = y0 + (256 if row in (1, 3) and r.random() < 0.6 else int(r.uniform(170, 240)))
            d.rounded_rectangle([x, top, x + w, bot], radius=5, fill=c)
            if PLAID.get(row) and r.random() < 0.25:
                plaid(d, (x + 1, top + 6, x + w - 1, bot), c, r)
            d.line([(x, top), (x, bot)], fill=dk(c, 0.55), width=2)
            d.line([(x + w - 3, top + 4), (x + w - 3, bot)], fill=tuple(min(255, v + 26) for v in c), width=2)
            d.line([(x + w // 2, y0), (x + w // 2, top + 2)], fill=(170, 170, 174), width=2)    # hanger
            x += w - int(r.uniform(2, 6))
    save(grain(im, 2.0, 3), "racks", 128)


def shirt(d, box, c, r, kind):
    x0, y0, x1, y1 = box
    w = x1 - x0
    cx = (x0 + x1) / 2
    if kind == "pants":
        d.polygon([(x0 + w * 0.18, y0 + 10), (x1 - w * 0.18, y0 + 10), (x1 - w * 0.08, y1), (cx + w * 0.04, y1), (cx, y0 + (y1 - y0) * 0.3), (cx - w * 0.04, y1), (x0 + w * 0.08, y1)], fill=c, outline=dk(c))
        d.line([(cx, y0 + 12), (cx, y0 + (y1 - y0) * 0.3)], fill=dk(c, 0.6), width=2)
        d.rectangle([x0 + w * 0.18, y0 + 10, x1 - w * 0.18, y0 + 20], fill=dk(c, 0.8))
        if c[2] > c[0]:   # denim: orange stitching
            d.line([(x0 + w * 0.25, y0 + 30), (x0 + w * 0.2, y0 + 70)], fill=(200, 140, 60), width=1)
            d.line([(x1 - w * 0.25, y0 + 30), (x1 - w * 0.2, y0 + 70)], fill=(200, 140, 60), width=1)
    else:
        sh = y0 + 20
        d.polygon([(cx - w * 0.15, y0 + 8), (cx + w * 0.15, y0 + 8), (x1 - w * 0.02, sh + 10), (x1 - w * 0.06, sh + 60), (x1 - w * 0.16, sh + 52), (x1 - w * 0.16, y1),
                   (x0 + w * 0.16, y1), (x0 + w * 0.16, sh + 52), (x0 + w * 0.06, sh + 60), (x0 + w * 0.02, sh + 10)], fill=c, outline=dk(c))
        if kind == "flannel":
            plaid(d, (x0 + w * 0.18, sh, x1 - w * 0.18, y1 - 2), c, r)
        if kind == "jacket":
            d.line([(cx, y0 + 14), (cx, y1)], fill=dk(c, 0.5), width=2)
            d.polygon([(cx - w * 0.15, y0 + 8), (cx, y0 + 50), (cx - w * 0.05, y0 + 60), (cx - w * 0.2, y0 + 14)], fill=dk(c, 0.8))
            d.polygon([(cx + w * 0.15, y0 + 8), (cx, y0 + 50), (cx + w * 0.05, y0 + 60), (cx + w * 0.2, y0 + 14)], fill=dk(c, 0.8))
        if kind == "vest":
            d.rectangle([x0 + w * 0.16, sh + 52, x1 - w * 0.16, y1], fill=c)
            for k in range(4):
                d.ellipse([cx - 2, y0 + 40 + k * 22, cx + 2, y0 + 44 + k * 22], fill=(220, 200, 150))
        d.arc([cx - w * 0.15, y0 + 2, cx + w * 0.15, y0 + 22], 0, 180, fill=dk(c, 0.5), width=2)


def faceouts():
    """Single garments faced out on the wall (front views): 2 rows of 8 cells of 128 x 256
    (0.5 x 1.0 m): row 0 men's casual, row 1 juniors and denim."""
    W, H = 1024, 512
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = np.random.default_rng(21)
    kinds = [["shirt", "pants", "jacket", "flannel", "pants", "shirt", "jacket", "pants"],
             ["vest", "pants", "flannel", "shirt", "jacket", "pants", "vest", "flannel"]]
    pals = [PAL[0] + PAL[1], PAL[2] + PAL[3]]
    for row in range(2):
        for k in range(8):
            c = pals[row][r.integers(len(pals[row]))]
            kd = kinds[row][k]
            if kd == "vest":
                c = (70, 100, 150)
            shirt(d, (k * 128 + 10, row * 256 + 6, k * 128 + 118, row * 256 + (250 if kd == "pants" else 200)), c, r, kd)
    save(im, "faceouts", 0)


def folded():
    """Stacks of folded jeans and khakis seen from the front: 512 x 256, two halves
    (denim, mixed), each 0.6 m wide x 0.6 m tall."""
    W, H = 512, 256
    im = Image.new("RGB", (W, H), (240, 240, 236))
    d = ImageDraw.Draw(im)
    r = np.random.default_rng(31)
    for half in range(2):
        for col in range(3):
            x0 = half * 256 + col * 85 + 4
            y = H - 2
            while y > 12:
                th = int(r.uniform(9, 13))
                c = (PAL[3] if half == 0 else PAL[1] + PAL[0])[r.integers(7)]
                jx = int(r.uniform(-3, 3))
                d.rounded_rectangle([x0 + jx, y - th, x0 + 78 + jx, y], radius=3, fill=c, outline=dk(c, 0.6))
                d.line([(x0 + jx + 4, y - th + 3), (x0 + 74 + jx, y - th + 3)], fill=tuple(min(255, v + 30) for v in c))
                y -= th
    save(grain(im, 2.0, 33), "folded", 96)


def signs():
    """Hanging and standing signs: 2 x 2 cells of 256 x 512 (0.5 x 1.0 m):
    0 '2 for $20' (JW's blue banners, video 3:46), 1 'SPECIAL PRICE 25% OFF' (County Seat,
    video 11:12), 2 'NEW ARRIVALS' (5-7-9), 3 'JEANS' wall header."""
    W, H = 512, 1024
    im = Image.new("RGB", (W * SS, H * SS), (250, 250, 250))
    d = ImageDraw.Draw(im)
    def cell(k):
        return (k % 2) * 256 * SS, (k // 2) * 512 * SS
    # 0
    x, y = cell(0)
    d.rectangle([x, y, x + 256 * SS, y + 512 * SS], fill=(28, 52, 150))
    d.rectangle([x + 10 * SS, y + 10 * SS, x + 246 * SS, y + 502 * SS], outline=(250, 250, 250), width=4 * SS)
    d.text((x + 128 * SS, y + 90 * SS), "TOPS", font=F(BLACK, 46 * SS), fill=(250, 210, 40), anchor="mm")
    d.text((x + 128 * SS, y + 200 * SS), "2", font=F(BLACK, 150 * SS), fill=(250, 250, 250), anchor="mm")
    d.text((x + 128 * SS, y + 290 * SS), "for", font=F(SERIF, 44 * SS), fill=(250, 250, 250), anchor="mm")
    d.text((x + 128 * SS, y + 380 * SS), "$20", font=F(BLACK, 96 * SS), fill=(250, 210, 40), anchor="mm")
    d.text((x + 128 * SS, y + 460 * SS), "PANTS", font=F(BLACK, 40 * SS), fill=(250, 250, 250), anchor="mm")
    # 1
    x, y = cell(1)
    d.rectangle([x, y, x + 256 * SS, y + 512 * SS], fill=(92, 52, 150))
    d.text((x + 128 * SS, y + 100 * SS), "SPECIAL", font=F(SERIF, 40 * SS), fill=(250, 250, 250), anchor="mm")
    d.text((x + 128 * SS, y + 150 * SS), "PRICE", font=F(SERIF, 40 * SS), fill=(250, 250, 250), anchor="mm")
    d.text((x + 128 * SS, y + 280 * SS), "25%", font=F(BLACK, 100 * SS), fill=(250, 250, 250), anchor="mm")
    d.text((x + 128 * SS, y + 380 * SS), "OFF", font=F(BLACK, 80 * SS), fill=(250, 250, 250), anchor="mm")
    # 2
    x, y = cell(2)
    d.rectangle([x, y, x + 256 * SS, y + 512 * SS], fill=(250, 248, 240))
    d.rectangle([x + 8 * SS, y + 8 * SS, x + 248 * SS, y + 504 * SS], outline=(20, 20, 20), width=3 * SS)
    d.text((x + 128 * SS, y + 200 * SS), "NEW", font=F(BLACK, 80 * SS), fill=(20, 20, 20), anchor="mm")
    d.text((x + 128 * SS, y + 300 * SS), "ARRIVALS", font=F(BLACK, 42 * SS), fill=(200, 30, 60), anchor="mm")
    # 3
    x, y = cell(3)
    d.rectangle([x, y, x + 256 * SS, y + 512 * SS], fill=(24, 24, 26))
    for i, ch in enumerate("JEANS"):
        d.text((x + 128 * SS, y + (70 + i * 92) * SS), ch, font=F(BLACK, 84 * SS), fill=(240, 240, 236), anchor="mm")
    save(im.resize((W, H), Image.LANCZOS), "signs", 64)


def wood():
    """Light wood plank floor (5-7-9, video 8:11): 4-inch boards, 1.0 m square."""
    W = 256
    im = Image.new("RGB", (W, W), (214, 190, 150))
    d = ImageDraw.Draw(im)
    r = np.random.default_rng(41)
    bw = 26
    for k in range(W // bw + 1):
        x = k * bw
        k_ = r.uniform(0.9, 1.05)
        c = tuple(int(v * k_) for v in (214, 190, 150))
        d.rectangle([x, 0, x + bw - 2, W], fill=c)
        for _ in range(6):
            yy = r.uniform(0, W)
            d.line([(x + 3, yy), (x + bw - 5, yy + r.uniform(-3, 3))], fill=dk(c, 0.9))
        cut = int(r.uniform(20, W - 20))
        d.line([(x, cut), (x + bw - 2, cut)], fill=(150, 126, 90), width=2)
        d.line([(x + bw - 2, 0), (x + bw - 2, W)], fill=(160, 136, 100), width=2)
    save(grain(im, 2.0, 43), "wood", 64)


def tile_cs():
    """County Seat's floor (video 10:54): white 12-inch tile with grey squares set in a
    pattern; 2.44 m square (8 x 8 tiles)."""
    W = 512
    im = Image.new("RGB", (W, W), (236, 236, 232))
    d = ImageDraw.Draw(im)
    t = W // 8
    for i in range(8):
        for j in range(8):
            c = (236, 236, 232)
            if (i % 4 == 1 and j % 4 == 1) or (i % 4 == 2 and j % 4 == 2):
                c = (150, 150, 152)
            d.rectangle([i * t, j * t, i * t + t - 2, j * t + t - 2], fill=c)
    save(grain(im, 1.5, 45), "tile_cs", 32)


def posters():
    """Denim posters, original: 2 cells of 256 x 512. One is a close-up of a jeans back
    pocket with its stitching, the other a single pair of jeans laid flat, with a word."""
    W, H = 512, 512
    im = Image.new("RGB", (W, H), (240, 240, 240))
    d = ImageDraw.Draw(im)
    r = np.random.default_rng(49)
    for k in range(2):
        x0 = k * 256
        d.rectangle([x0 + 6, 6, x0 + 250, 506], fill=(30, 30, 34))
        d.rectangle([x0 + 16, 16, x0 + 240, 440], fill=(62, 86, 132) if k == 0 else (226, 222, 212))
        if k == 0:
            # denim twill and a back pocket, stitched in gold thread
            for y in range(16, 440, 4):
                d.line([(x0 + 16, y), (x0 + 240, y + 12)], fill=(54, 76, 120))
            pts = [(x0 + 52, 120), (x0 + 204, 120), (x0 + 196, 330), (x0 + 128, 372), (x0 + 60, 330)]
            d.polygon(pts, fill=(70, 96, 146), outline=(214, 160, 70))
            d.line(pts + [pts[0]], fill=(214, 160, 70), width=3)
            d.line([(x0 + 52, 140), (x0 + 204, 140)], fill=(214, 160, 70), width=2)
            d.arc([x0 + 76, 200, x0 + 180, 290], 200, 340, fill=(214, 160, 70), width=3)
        else:
            # one pair of jeans laid flat
            c = (58, 82, 128)
            d.polygon([(x0 + 70, 60), (x0 + 186, 60), (x0 + 200, 420), (x0 + 140, 420), (x0 + 128, 170), (x0 + 116, 420), (x0 + 56, 420)], fill=c, outline=(36, 52, 86))
            d.rectangle([x0 + 70, 60, x0 + 186, 80], fill=(48, 68, 108))
            d.line([(x0 + 128, 82), (x0 + 128, 170)], fill=(36, 52, 86), width=2)
            d.arc([x0 + 78, 84, x0 + 120, 130], 0, 90, fill=(214, 160, 70), width=2)
            d.arc([x0 + 136, 84, x0 + 178, 130], 90, 180, fill=(214, 160, 70), width=2)
        d.text((x0 + 128, 470), "DENIM" if k == 0 else "THE FIT", font=F(BLACK, 34), fill=(240, 240, 236), anchor="mm")
    save(grain(im, 2.0, 47), "posters", 64)


def main():
    os.makedirs(OUT, exist_ok=True)
    racks(); faceouts(); folded(); signs(); wood(); tile_cs(); posters()
    tot = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT) if f.endswith(".png"))
    print("wrote tex/ap/*.png, %d KB" % (tot // 1024))


if __name__ == "__main__":
    main()
