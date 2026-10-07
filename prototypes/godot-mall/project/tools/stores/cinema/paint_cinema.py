"""Textures for the Southland Cinema front (tools/stores/cinema/front.gd), after Steven's photos
(Oct 7, 2026): white-painted brick, the lit poster cases, the "Welcome to Southland Cinema 4"
case (without the United Artists badge), the box office's price cards and help-wanted card.
Every film here is invented: titles, art and credits (no real films, studios or actors).
  tex/cin/brick.png    512 x 512, 1 m square, tiling: white-painted running-bond brick
  tex/cin/posters.png  1024 x 768: 4 posters, each 256 x 384 (27 x 40 in one-sheets)
  tex/cin/welcome.png  256 x 384: the welcome case
  tex/cin/cards.png    512 x 128: price cards and the help-wanted card
Run: python3 tools/stores/cinema/paint_cinema.py   (from the project folder)
"""
import os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "..", "tex", "cin")
SRC = os.path.join(HERE, "..", "signs", "src")
F = lambda name, size: ImageFont.truetype(os.path.join(SRC, name), size)


def brick():
    N = 512
    rng = np.random.default_rng(4)
    img = np.zeros((N, N, 3), np.float32)
    rows = 15
    rh = N / rows
    for r in range(rows):
        off = 0 if r % 2 == 0 else N / 8
        for c in range(-1, 5):
            x0 = int(c * N / 4 + off)
            y0 = int(r * rh)
            sh = rng.uniform(0.93, 1.03)
            img[y0 + 3:int(y0 + rh) - 2, max(0, x0 + 3):min(N, x0 + N // 4 - 2)] = np.array([236, 234, 228]) * sh
    joint = np.all(img == 0, axis=2)
    img[joint] = (205, 203, 198)
    noise = np.asarray(Image.fromarray((rng.normal(0, 1, (N, N)) * 40 + 128).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32) / 128 - 1
    img = np.clip(img * (1 + noise[..., None] * 0.05), 0, 255).astype(np.uint8)
    Image.fromarray(img).save(os.path.join(OUT, "brick.png"))


POSTERS = [
    # title, tagline, colours (top, bottom, title), art
    ("BAYOU RUN", "ONE NIGHT. ONE RIVER. NO WAY BACK.", ("#0d1a2e", "#1e4a5a", "#f2c94c"), "moon"),
    ("COMET KIDS", "THIS SUMMER, THE SKY IS FALLING... UP!", ("#2a1a5e", "#e86a3a", "#ffffff"), "comet"),
    ("GULF BREEZE", "SHE HAD ONE SUMMER TO FIND HIM.", ("#f2a65a", "#4ab0c8", "#ffffff"), "sun"),
    ("RED MESA", "THE LAST RIDE WEST.", ("#3a0e0a", "#c8501e", "#f4e2b8"), "mesa"),
]


def poster(d, x, y, w, h, title, tag, cols, art, rng):
    top, bot, tc = cols
    t, b = Image.new("RGB", (1, 2)), None
    for k in range(h):
        f = k / (h - 1)
        c0 = tuple(int(top[i:i + 2], 16) for i in (1, 3, 5))
        c1 = tuple(int(bot[i:i + 2], 16) for i in (1, 3, 5))
        d.line([(x, y + k), (x + w, y + k)], fill=tuple(int(c0[i] * (1 - f) + c1[i] * f) for i in range(3)))
    cx, cy = x + w // 2, y + int(h * 0.42)
    if art == "moon":
        d.ellipse([cx - 50, cy - 90, cx + 50, cy + 10], fill="#e8e2c0")
        for i in range(9):
            px = x + 10 + i * (w - 20) // 8
            d.polygon([(px - 18, y + h * 0.66), (px, y + h * 0.66 - rng.randint(40, 90)), (px + 18, y + h * 0.66)], fill="#06100c")
        d.rectangle([x, y + int(h * 0.66), x + w, y + int(h * 0.72)], fill="#0a1c24")
    elif art == "comet":
        for i in range(40):
            d.point((x + rng.randint(0, w), y + rng.randint(0, int(h * 0.6))), fill="#ffffff")
        d.polygon([(cx + 60, cy - 100), (cx - 70, cy + 20), (cx - 50, cy + 40)], fill="#ffd27a")
        d.ellipse([cx + 40, cy - 120, cx + 80, cy - 80], fill="#ffffff")
        for i, px in enumerate((cx - 60, cx - 15, cx + 30)):
            d.ellipse([px - 12, cy + 50, px + 12, cy + 74], fill="#1a1030")
            d.rectangle([px - 14, cy + 74, px + 14, cy + 130], fill="#1a1030")
    elif art == "sun":
        d.ellipse([cx - 60, cy - 70, cx + 60, cy + 50], fill="#ffe08a")
        d.rectangle([x, cy + 20, x + w, y + int(h * 0.72)], fill="#2a8aa8")
        d.polygon([(cx - 30, cy + 60), (cx - 20, cy - 10), (cx - 8, cy + 60)], fill="#3a2a2a")
        d.polygon([(cx + 6, cy + 60), (cx + 18, cy - 4), (cx + 30, cy + 60)], fill="#3a2a2a")
    else:
        d.polygon([(x, cy + 70), (x + 40, cy - 30), (x + 150, cy - 30), (x + 170, cy + 70)], fill="#5a1a0e")
        d.polygon([(x + 160, cy + 70), (x + 200, cy + 10), (x + w, cy + 10), (x + w, cy + 70)], fill="#4a160c")
        d.ellipse([cx - 14, cy + 20, cx + 14, cy + 48], fill="#140806")
        d.polygon([(cx - 26, cy + 100), (cx, cy + 40), (cx + 26, cy + 100)], fill="#140806")
    ft = F("FrancoisOne-Regular.ttf", 44 if len(title) < 10 else 36)
    tw = d.textlength(title, font=ft)
    d.text((cx - tw / 2, y + int(h * 0.74)), title, font=ft, fill=tc, stroke_width=2, stroke_fill="#000000")
    fs = F("SourceSans3-Bold.ttf", 11)
    tw = d.textlength(tag, font=fs)
    d.text((cx - tw / 2, y + 14), tag, font=fs, fill="#ffffff")
    # the billing block: tiny condensed lines, unreadable as on a real one-sheet
    for k in range(4):
        lw = rng.randint(int(w * 0.5), int(w * 0.85))
        d.rectangle([cx - lw // 2, y + int(h * 0.88) + k * 7, cx + lw // 2, y + int(h * 0.88) + k * 7 + 3], fill="#d8d0c0")
    d.rectangle([x + w - 40, y + h - 22, x + w - 8, y + h - 8], outline="#ffffff")
    d.text((x + w - 37, y + h - 22), "PG-13" if rng.random() < 0.6 else "  PG", font=F("SourceSans3-Bold.ttf", 10), fill="#ffffff")


def posters():
    rng = random.Random(1995)
    im = Image.new("RGB", (1024, 768), "#000000")
    d = ImageDraw.Draw(im)
    for k, p in enumerate(POSTERS):
        poster(d, (k % 4) * 256, 0, 256, 384, *p, rng)
    # row 2: the same films' teaser one-sheets (title over a plain field)
    for k, p in enumerate(POSTERS):
        x = (k % 4) * 256
        top = p[2][1]
        d.rectangle([x, 384, x + 255, 767], fill=top)
        ft = F("FrancoisOne-Regular.ttf", 40)
        tw = d.textlength(p[0], font=ft)
        d.text((x + 128 - tw / 2, 384 + 170), p[0], font=ft, fill=p[2][2], stroke_width=2, stroke_fill="#000000")
        fs = F("SourceSans3-Bold.ttf", 16)
        msg = "COMING SOON"
        tw = d.textlength(msg, font=fs)
        d.text((x + 128 - tw / 2, 384 + 230), msg, font=fs, fill="#ffffff")
    im.save(os.path.join(OUT, "posters.png"))


def welcome():
    W, H = 256, 384
    im = Image.new("RGB", (W, H), "#f4f2ec")
    d = ImageDraw.Draw(im)
    # a film-strip border
    for side in (0, W - 22):
        d.rectangle([side, 0, side + 21, H], fill="#1a1a1a")
        for y in range(6, H, 18):
            d.rectangle([side + 6, y, side + 15, y + 9], fill="#f4f2ec")
    ft = F("FrancoisOne-Regular.ttf", 46)
    d.text((34, 10), "WELCOME", font=ft, fill="#c8501e", stroke_width=1, stroke_fill="#5a1a0e")
    d.text((34, 66), "TO", font=ft, fill="#c8501e", stroke_width=1, stroke_fill="#5a1a0e")
    d.rectangle([34, 150, W - 34, 240], fill="#141414")
    d.text((50, 156), "Welcome", font=F("SourceSans3-Bold.ttf", 34), fill="#f2c94c")
    d.text((50, 198), "Enjoy the show", font=F("SourceSans3-Bold.ttf", 24), fill="#f2c94c")
    fb = F("FrancoisOne-Regular.ttf", 40)
    for k, line in enumerate(("SOUTHLAND", "CINEMA - 4")):
        tw = d.textlength(line, font=fb)
        d.text(((W - tw) / 2, 262 + k * 50), line, font=fb, fill="#141414")
    im.save(os.path.join(OUT, "welcome.png"))


def cards():
    im = Image.new("RGB", (512, 128), "#2a1a12")
    d = ImageDraw.Draw(im)
    fb = F("SourceSans3-Bold.ttf", 15)
    cols = ["#d8501e", "#e8a02a", "#c83a2a", "#f2c94c"]
    labels = [("ADULTS", "$5.50"), ("CHILDREN", "$3.50"), ("SENIORS", "$3.50"), ("MATINEES", "$3.75")]
    for k, (a, b) in enumerate(labels):
        x = k * 96
        d.rectangle([x + 4, 8, x + 92, 120], fill=cols[k])
        d.text((x + 12, 20), a, font=fb, fill="#ffffff")
        d.text((x + 12, 56), b, font=F("FrancoisOne-Regular.ttf", 34), fill="#ffffff")
    d.rectangle([392, 30, 508, 98], fill="#f4f2ec", outline="#c8202c", width=4)
    d.text((404, 40), "HELP", font=F("FrancoisOne-Regular.ttf", 22), fill="#c8202c")
    d.text((404, 66), "WANTED", font=F("FrancoisOne-Regular.ttf", 22), fill="#c8202c")
    im.save(os.path.join(OUT, "cards.png"))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    brick(); posters(); welcome(); cards()
    print("wrote", OUT)
