"""Textures for the Wave 9 shops (tools/stores/small/wave9.gd), written to tex/w9/*.png:
Solarium's beach print, Rave's poster wall, Concepts' uniform and backpack walls and sign box,
Country Fair's quilt, gingham and shelf of country gifts, Lion's Share's brick and carved
plaque, American Bank's wrought-iron gate. From the Southland facade records; the names are
the stores' own, the lettering is stand-in type, everything else invented (no real bands,
brands or schools).
  python3 tools/stores/small/paint9.py   (from the project folder)
"""
import math, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "kay_bee"))
import paint_store as kb   # noqa: E402

OUT = os.path.join(HERE, "..", "..", "..", "tex", "w9")
os.makedirs(OUT, exist_ok=True)
BOLD = kb.BOLD
DJ = "/usr/share/fonts/truetype/dejavu/"
SERIF_B = DJ + "DejaVuSerif-Bold.ttf"
SERIF = DJ + "DejaVuSerif.ttf"
SS = 2


def save(im, name, colors=0):
    if im.mode != "RGBA":
        im = im.convert("RGB")
        if colors:
            im = im.quantize(colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    im.save(os.path.join(OUT, name + ".png"), optimize=True)


def beach():
    """Solarium's lit print: sea, sand and a palm at sunset. 512 x 384 = 1.2 m x 0.9 m."""
    W, H = 512, 384
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        f = y / H
        if f < 0.55:
            c = (int(250 - 60 * f), int(170 + 40 * f), int(120 + 120 * f))
        elif f < 0.72:
            c = (40, int(150 + 40 * (f - 0.55) * 4), 170)
        else:
            c = (236, 214, 170)
        d.line([0, y, W, y], fill=c)
    d.ellipse([300, 150, 380, 230], fill=(255, 220, 120))
    d.line([(110, 330), (130, 250), (150, 170), (160, 110)], fill=(70, 50, 30), width=10)
    for a in range(0, 360, 45):
        r = math.radians(a)
        d.line([(160, 110), (160 + 80 * math.cos(r), 110 + 40 * math.sin(r) + 20)], fill=(30, 90, 50), width=8)
    d.rectangle([0, 0, W - 1, H - 1], outline=(250, 250, 248), width=10)
    save(kb.grain(im, 1.5, 901), "beach", 64)


def posters():
    """Rave's back wall: invented posters, abstract shapes and nonsense-free plain words.
    1024 x 256 = 4 m x 1 m."""
    W, H = 1024, 256
    rng = random.Random(902)
    im = Image.new("RGB", (W, H), (20, 18, 22))
    d = ImageDraw.Draw(im)
    words = ["SUMMER", "NIGHT", "LOUD", "DREAM", "WILD", "ECHO", "NEON", "WAVE"]
    for k in range(8):
        x0 = 8 + k * 127
        bg = rng.choice([(30, 30, 34), (200, 30, 70), (240, 220, 60), (60, 60, 180), (230, 230, 226), (120, 30, 140)])
        d.rectangle([x0, 14, x0 + 116, 240], fill=bg)
        fg = (250, 250, 248) if sum(bg) < 400 else (20, 18, 22)
        for _ in range(3):
            cx, cy, r = rng.uniform(x0 + 20, x0 + 96), rng.uniform(40, 170), rng.uniform(10, 34)
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=fg, width=3)
        kb.fit_text(d, words[k], (x0 + 8, 190, x0 + 108, 230), BOLD, fg)
    save(kb.grain(im, 2, 903), "posters", 64)


def uniforms():
    """Concepts' wall: navy blazers, white polos, plaid jumpers, khakis on hangers. 1024 x 512
    = 2.4 m x 1.2 m."""
    W, H = 1024, 512
    rng = random.Random(904)
    im = Image.new("RGB", (W, H), (236, 234, 228))
    d = ImageDraw.Draw(im)
    for row in range(2):
        y0 = 10 + row * 250
        d.rectangle([0, y0, W, y0 + 6], fill=(170, 170, 176))
        x = 6
        while x < W - 60:
            kind = rng.choice(["blazer", "polo", "jumper", "khaki", "polo"])
            if kind == "blazer":
                d.polygon([(x, y0 + 26), (x + 54, y0 + 26), (x + 58, y0 + 200), (x - 4, y0 + 200)], fill=(26, 34, 70))
                d.polygon([(x + 18, y0 + 26), (x + 27, y0 + 90), (x + 36, y0 + 26)], fill=(250, 250, 248))
            elif kind == "polo":
                c = rng.choice([(250, 250, 248), (250, 250, 248), (190, 210, 236), (26, 34, 70)])
                d.polygon([(x - 6, y0 + 30), (x + 60, y0 + 30), (x + 54, y0 + 130), (x, y0 + 130)], fill=c, outline=(200, 200, 200))
            elif kind == "jumper":
                for yy in range(y0 + 30, y0 + 190, 10):
                    for xx in range(x, x + 54, 10):
                        c = (30, 60, 120) if ((xx - x) // 10 + (yy - y0) // 10) % 2 else (40, 100, 70)
                        d.rectangle([xx, yy, xx + 10, yy + 10], fill=c)
                for yy in range(y0 + 30, y0 + 190, 20):
                    d.line([x, yy, x + 54, yy], fill=(200, 40, 40), width=2)
            else:
                d.polygon([(x, y0 + 30), (x + 54, y0 + 30), (x + 56, y0 + 230), (x + 30, y0 + 230), (x + 27, y0 + 100), (x + 24, y0 + 230), (x - 2, y0 + 230)], fill=(196, 172, 120))
            d.line([x + 27, y0 + 6, x + 27, y0 + 28], fill=(150, 150, 156), width=2)
            x += 64
    save(kb.grain(im, 1.2, 905), "uniforms", 64)


def backpacks():
    """A wall of backpacks on pegs, plain colours, no logos. 1024 x 256 = 4 m x 1 m."""
    W, H = 1024, 256
    rng = random.Random(906)
    im = Image.new("RGB", (W, H), (236, 234, 228))
    d = ImageDraw.Draw(im)
    for row in range(2):
        y0 = 8 + row * 124
        x = 8
        while x < W - 70:
            c = rng.choice([(26, 34, 70), (170, 30, 40), (30, 90, 60), (40, 40, 44), (60, 110, 190), (230, 190, 40), (120, 40, 110)])
            d.rounded_rectangle([x, y0 + 14, x + 62, y0 + 112], radius=16, fill=c)
            d.rounded_rectangle([x + 10, y0 + 60, x + 52, y0 + 104], radius=8, fill=tuple(max(0, v - 30) for v in c))
            d.arc([x + 18, y0, x + 44, y0 + 30], 180, 360, fill=(60, 60, 60), width=4)
            x += 74
    save(kb.grain(im, 1.2, 907), "backpacks", 64)


def concepts_sign():
    """The lit sign box: cream capitals on dark plum with a fine cream border. 1024 x 192 =
    3.6 m x 0.68 m."""
    W, H = 1024 * SS, 192 * SS
    im = Image.new("RGB", (W, H), (58, 24, 40))
    d = ImageDraw.Draw(im)
    d.rectangle([10 * SS, 10 * SS, W - 10 * SS, H - 10 * SS], outline=(244, 232, 200), width=3 * SS)
    f = ImageFont.truetype(BOLD, 120 * SS)
    txt = "CONCEPTS"
    tr = 26 * SS
    ws = [d.textlength(ch, font=f) for ch in txt]
    x = W / 2 - (sum(ws) + tr * (len(txt) - 1)) / 2
    l, t, r, b = d.textbbox((0, 0), "C", font=f)
    for ch, w in zip(txt, ws):
        d.text((x, H / 2 - (t + b) / 2), ch, font=f, fill=(250, 238, 206))
        x += w + tr
    im = im.resize((1024, 192), Image.LANCZOS)
    save(im, "concepts_sign", 32)


def quilt():
    """A patchwork quilt hung on the wall, 1.2 m square (512)."""
    N = 512
    rng = random.Random(908)
    im = Image.new("RGB", (N, N), (240, 232, 214))
    d = ImageDraw.Draw(im)
    cols = [(150, 40, 56), (104, 128, 160), (164, 112, 140), (50, 84, 60), (236, 226, 200), (196, 170, 120)]
    s = N // 8
    for j in range(8):
        for i in range(8):
            c1, c2 = rng.sample(cols, 2)
            x0, y0 = i * s, j * s
            d.rectangle([x0, y0, x0 + s, y0 + s], fill=c1)
            d.polygon([(x0, y0), (x0 + s, y0), (x0, y0 + s)], fill=c2)
            d.rectangle([x0, y0, x0 + s, y0 + s], outline=(250, 246, 236), width=2)
    save(kb.grain(im, 2, 909), "quilt", 64)


def gingham():
    """Red-and-white gingham for the valance, 0.3 m square (128)."""
    N = 128
    a = np.zeros((N, N, 3), np.float32) + 250
    stripe = (np.arange(N) // 16) % 2 == 0
    for y in range(N):
        for x in range(N):
            k = int(stripe[x]) + int(stripe[y])
            a[y, x] = [(250, 250, 248), (226, 140, 140), (190, 30, 40)][k]
    save(Image.fromarray(a.astype(np.uint8)), "gingham", 16)


def country():
    """Country Fair's shelves: baskets, jar candles, wooden hearts, dried flowers, little
    signs. 1024 x 256 = 2.4 m x 0.6 m, two shelves."""
    W, H = 1024, 256
    rng = random.Random(910)
    im = Image.new("RGB", (W, H), (226, 210, 180))
    d = ImageDraw.Draw(im)
    for row in range(2):
        y = 122 + row * 128
        d.rectangle([0, y - 6, W, y], fill=(150, 104, 60))
        x = 8
        while x < W - 70:
            kind = rng.randrange(5)
            if kind == 0:
                d.chord([x, y - 70, x + 70, y + 30], 180, 360, fill=(176, 130, 70))
                for k in range(5):
                    d.line([x + 6 + k * 14, y - 40, x + 6 + k * 14, y - 4], fill=(130, 90, 46), width=2)
                d.arc([x + 10, y - 104, x + 60, y - 30], 180, 360, fill=(150, 104, 56), width=5)
                x += 78
            elif kind == 1:
                c = rng.choice([(200, 60, 60), (240, 220, 180), (120, 150, 90), (230, 180, 120)])
                d.rectangle([x, y - 54, x + 34, y], fill=c)
                d.rectangle([x - 2, y - 60, x + 36, y - 52], fill=(160, 140, 110))
                x += 42
            elif kind == 2:
                c = rng.choice([(176, 60, 50), (180, 140, 90), (90, 110, 80)])
                d.ellipse([x, y - 52, x + 30, y - 22], fill=c)
                d.ellipse([x + 24, y - 52, x + 54, y - 22], fill=c)
                d.polygon([(x + 2, y - 34), (x + 52, y - 34), (x + 27, y - 4)], fill=c)
                x += 62
            elif kind == 3:
                d.rectangle([x + 10, y - 40, x + 30, y], fill=(170, 150, 120))
                for k in range(9):
                    fx = x + 20 + rng.uniform(-24, 24)
                    fy = y - 40 - rng.uniform(10, 60)
                    d.line([x + 20, y - 40, fx, fy], fill=(110, 120, 70), width=2)
                    d.ellipse([fx - 5, fy - 5, fx + 5, fy + 5], fill=rng.choice([(200, 110, 140), (230, 200, 120), (170, 140, 200), (240, 240, 230)]))
                x += 54
            else:
                d.rectangle([x, y - 66, x + 60, y - 24], fill=(240, 232, 214), outline=(120, 80, 40), width=3)
                d.line([x + 10, y - 50, x + 50, y - 50], fill=(150, 40, 40), width=3)
                d.line([x + 10, y - 38, x + 44, y - 38], fill=(90, 90, 90), width=2)
                x += 68
    save(kb.grain(im, 1.5, 911), "country", 64)


def brick():
    """Lion's Share's dark brown brick, 1.2 m x 0.6 m (512 x 256), running bond."""
    W, H = 512, 256
    r = np.random.default_rng(912)
    a = np.zeros((H, W, 3), np.float32) + np.array([58, 44, 36], np.float32)
    bh, bw = 32, 85
    for j in range(H // bh):
        off = 0 if j % 2 == 0 else bw // 2
        for i in range(-1, W // bw + 2):
            x0 = i * bw + off
            tone = np.array([104, 62, 44], np.float32) * r.uniform(0.75, 1.1)
            xs, xe = max(0, x0 + 3), min(W, x0 + bw - 3)
            if xe > xs:
                a[j * bh + 3:(j + 1) * bh - 3, xs:xe] = tone
    a += kb.noise(W, H, 6, 913, blur=1)[..., None]
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), "brick", 48)


def plaque():
    """The carved shield plaque: dark stained wood, a gold rim, the name in gold serif.
    512 x 640 = 0.8 m x 1.0 m, alpha outside the shield."""
    W, H = 512 * SS, 640 * SS
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    def shield(inset):
        pts = [(inset, inset)]
        pts.append((W - inset, inset))
        for k in range(21):
            a = k / 20
            x = (W - inset) - a * (W / 2 - inset)
            y = H * 0.45 + (H - inset - H * 0.45) * math.sin(a * math.pi / 2)
            pts.append((x, y))
        for k in range(21):
            a = 1 - k / 20
            x = inset + a * (W / 2 - inset)
            y = H * 0.45 + (H - inset - H * 0.45) * math.sin(a * math.pi / 2)
            pts.append((x, y))
        return pts
    d.polygon(shield(4 * SS), fill=(200, 160, 70, 255))
    d.polygon(shield(22 * SS), fill=(66, 40, 26, 255))
    d.polygon(shield(34 * SS), outline=(200, 160, 70, 255), width=3 * SS)
    gold = (226, 186, 90, 255)
    BASK = "/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf"
    f1 = ImageFont.truetype(BASK, 72 * SS)
    f2 = ImageFont.truetype(BASK, 118 * SS)
    d.polygon(shield(14 * SS), outline=(120, 90, 36, 255), width=4 * SS)
    for txt, f, y in [("The", f1, H * 0.2), ("Lion\u2019s", f2, H * 0.4), ("Share", f2, H * 0.6)]:
        l, t, r, b = d.textbbox((0, 0), txt, font=f)
        d.text((W / 2 - (l + r) / 2 + 3 * SS, y - (t + b) / 2 + 3 * SS), txt, font=f, fill=(30, 18, 10, 255))
        l, t, r, b = d.textbbox((0, 0), txt, font=f)
        d.text((W / 2 - (l + r) / 2, y - (t + b) / 2), txt, font=f, fill=gold)
    im = im.resize((512, 640), Image.LANCZOS)
    save(im, "plaque")


def gate():
    """American Bank's wrought-iron gate: vertical bars with spear tops, two rails with rings,
    alpha. 512 x 512 (stretched over the arch)."""
    N = 512
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    K = (18, 18, 20, 255)
    for x in range(8, N, 32):
        d.rectangle([x, 0, x + 6, N], fill=K)
    for y in (90, 300, 500):
        d.rectangle([0, y, N, y + 10], fill=K)
    for x in range(24, N, 32):
        for y in (60, 270):
            d.ellipse([x - 12, y - 12, x + 12, y + 12], outline=K, width=4)
    save(im, "gate")


def black_clothes():
    """Rave's walls: black and charcoal tops and jeans on hangers against black slat, a few
    white and red accents. 1024 x 512 = 2.4 m x 1.2 m."""
    W, H = 1024, 512
    rng = random.Random(914)
    im = Image.new("RGB", (W, H), (22, 22, 24))
    d = ImageDraw.Draw(im)
    for y in range(0, H, 24):
        d.line([0, y, W, y], fill=(14, 14, 16), width=3)
    for row in range(2):
        y0 = 10 + row * 250
        d.rectangle([0, y0, W, y0 + 5], fill=(150, 150, 156))
        x = 6
        while x < W - 60:
            c = rng.choice([(28, 28, 30), (40, 40, 44), (52, 52, 56), (28, 28, 30), (236, 234, 228), (170, 30, 50), (34, 36, 54)])
            if rng.random() < 0.6:
                d.polygon([(x - 6, y0 + 28), (x + 60, y0 + 28), (x + 54, y0 + 160), (x, y0 + 160)], fill=c)
                d.chord([x + 16, y0 + 18, x + 38, y0 + 40], 0, 180, fill=(22, 22, 24))
            else:
                d.polygon([(x, y0 + 28), (x + 54, y0 + 28), (x + 56, y0 + 228), (x + 30, y0 + 228), (x + 27, y0 + 100), (x + 24, y0 + 228), (x - 2, y0 + 228)], fill=c)
            d.line([x + 27, y0 + 6, x + 27, y0 + 26], fill=(150, 150, 156), width=2)
            x += 64
    save(kb.grain(im, 1.0, 915), "black_clothes", 32)


if __name__ == "__main__":
    beach(); posters(); uniforms(); backpacks(); concepts_sign()
    quilt(); gingham(); country(); brick(); plaque(); gate(); black_clothes()
    print("wrote tex/w9/*.png")
