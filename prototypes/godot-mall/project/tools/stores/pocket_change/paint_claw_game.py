"""Textures for the playable CLAW page (play/claw.html, Steven Oct 11 2026).

1. Re-encodes the mall crane's own textures (paint_crane.py -> tex/pc/crane_*.png) as WebP.
2. Paints the prizes' own art, all this mall's invented characters:
   - faces.webp: 4 x 2 cells of 256 px, a face decal for each plush/figure (RGBA);
   - pogs.webp: 4 x 2 cells of 256 px, the POG designs, the hologram-eye slammer and a cardboard
     back (RGB);
   - capsule.webp: 3 strips, the printed ticket rolls (75 / 100 / 200) wound in a capsule.
Run from the project folder:
    python3 tools/stores/pocket_change/paint_claw_game.py
"""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.abspath(os.path.join(PROJ, "..", "play", "claw"))
os.makedirs(OUT, exist_ok=True)
F_BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
F_BLACKI = "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf"
F_CN = "/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyreheroscn-bold.otf"


def font(p, s):
    return ImageFont.truetype(p, s)


def save(im, name, lossless=False, q=88):
    p = os.path.join(OUT, name + ".webp")
    im.save(p, "WEBP", quality=q, method=6, lossless=lossless)
    print(name, im.size, os.path.getsize(p))


# ---------------------------------------------------------------- 1. the cabinet's textures
for n in ["crane_cab_0", "crane_cab_1", "crane_cab_2", "crane_header_0", "crane_header_1", "crane_header_2",
          "crane_panel", "crane_glass", "crane_fur", "crane_face", "store_carpet", "store_wall"]:
    im = Image.open(os.path.join(PROJ, "tex", "pc", n + ".png"))
    if n == "store_carpet":
        im = im.resize((512, 512), Image.LANCZOS)
    if im.mode not in ("RGB", "RGBA"):
        im = im.convert("RGB")
    save(im, n.replace("crane_", ""), lossless=n in ("crane_glass", "crane_face"))


# ---------------------------------------------------------------- 2. faces (RGBA decals)
S = 2            # paint at 2x, downscale
C = 256 * S


def cell(im, i):
    """Draw context for cell i (0..7) of a 4 x 2 atlas."""
    x0, y0 = (i % 4) * C, (i // 4) * C
    return x0, y0


def ctext(d, cx, cy, t, f, fill, stroke=None, sw=0):
    bb = d.textbbox((0, 0), t, font=f, stroke_width=sw)
    d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], cy - (bb[3] - bb[1]) / 2 - bb[1]), t, font=f, fill=fill,
           stroke_width=sw, stroke_fill=stroke)


def eye(d, x, y, r, iris=(20, 14, 10), white=True, lid=None):
    if white:
        d.ellipse([x - r, y - r, x + r, y + r], fill=(252, 250, 246, 255), outline=(30, 20, 14, 255), width=3 * S)
    ir = r * (0.62 if white else 1.0)
    d.ellipse([x - ir, y - ir, x + ir, y + ir], fill=iris + (255,))
    pr = ir * 0.42
    d.ellipse([x - ir * 0.35 - pr, y - ir * 0.35 - pr, x - ir * 0.35 + pr, y - ir * 0.35 + pr], fill=(255, 255, 255, 255))
    if lid is not None:   # a heavy upper lid, lid = fraction covered
        d.chord([x - r - 2, y - r - 2, x + r + 2, y - r - 2 + 2 * (r + 2) * lid * 2], 180, 360, fill=lid[1] if isinstance(lid, tuple) else (0, 0, 0, 0))


def faces():
    im = Image.new("RGBA", (4 * C, 2 * C), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    m = C / 2
    # 0 gator: wide-set goggle eyes, a long toothy grin
    x0, y0 = cell(im, 0)
    for ex in (-0.26, 0.26):
        eye(d, x0 + m + ex * C, y0 + m - 0.18 * C, 0.12 * C, iris=(230, 180, 20))
        d.ellipse([x0 + m + ex * C - 0.025 * C, y0 + m - 0.26 * C, x0 + m + ex * C + 0.025 * C, y0 + m - 0.10 * C], fill=(10, 8, 6, 255))  # slit pupil
    d.arc([x0 + m - 0.42 * C, y0 + m - 0.1 * C, x0 + m + 0.42 * C, y0 + m + 0.34 * C], 15, 165, fill=(20, 40, 20, 255), width=6 * S)
    for k in range(9):
        tx = x0 + m - 0.34 * C + k * 0.085 * C
        ty = y0 + m + 0.14 * C + 0.08 * C * math.sin((k - 4) / 4 * 1.2)
        d.polygon([(tx - 0.03 * C, ty), (tx + 0.03 * C, ty), (tx, ty + 0.09 * C)], fill=(250, 248, 236, 255), outline=(40, 40, 30, 255))
    # 1 crawfish: stalk eyes (black beads), a small mouth
    x0, y0 = cell(im, 1)
    for ex in (-0.2, 0.2):
        d.ellipse([x0 + m + ex * C - 0.09 * C, y0 + m - 0.3 * C, x0 + m + ex * C + 0.09 * C, y0 + m - 0.12 * C], fill=(16, 10, 8, 255))
        d.ellipse([x0 + m + ex * C - 0.05 * C, y0 + m - 0.27 * C, x0 + m + ex * C - 0.0 * C, y0 + m - 0.22 * C], fill=(255, 255, 255, 255))
    d.arc([x0 + m - 0.12 * C, y0 + m + 0.0 * C, x0 + m + 0.12 * C, y0 + m + 0.16 * C], 10, 170, fill=(40, 10, 10, 255), width=5 * S)
    # 2 pelican: one big round eye each side (painted twice, left/right of centre), a yellow bill root
    x0, y0 = cell(im, 2)
    for ex in (-0.3, 0.3):
        eye(d, x0 + m + ex * C, y0 + m - 0.2 * C, 0.1 * C, iris=(30, 24, 20))
    d.polygon([(x0 + m - 0.1 * C, y0 + m - 0.02 * C), (x0 + m + 0.1 * C, y0 + m - 0.02 * C), (x0 + m + 0.06 * C, y0 + m + 0.4 * C), (x0 + m - 0.06 * C, y0 + m + 0.4 * C)],
              fill=(240, 160, 40, 255), outline=(120, 70, 10, 255), width=3 * S)
    d.line([x0 + m - 0.08 * C, y0 + m + 0.2 * C, x0 + m + 0.08 * C, y0 + m + 0.2 * C], fill=(120, 70, 10, 255), width=3 * S)
    # 3 nutria: beady eyes, a pink nose, whiskers, big orange front teeth
    x0, y0 = cell(im, 3)
    for ex in (-0.22, 0.22):
        d.ellipse([x0 + m + ex * C - 0.07 * C, y0 + m - 0.3 * C, x0 + m + ex * C + 0.07 * C, y0 + m - 0.16 * C], fill=(16, 10, 8, 255))
        d.ellipse([x0 + m + ex * C - 0.04 * C, y0 + m - 0.28 * C, x0 + m + ex * C + 0.0 * C, y0 + m - 0.24 * C], fill=(255, 255, 255, 255))
    d.ellipse([x0 + m - 0.1 * C, y0 + m - 0.08 * C, x0 + m + 0.1 * C, y0 + m + 0.06 * C], fill=(230, 110, 130, 255))
    for sx in (-1, 1):
        for k in range(3):
            d.line([x0 + m + sx * 0.12 * C, y0 + m + 0.0 * C + k * 0.05 * C, x0 + m + sx * 0.46 * C, y0 + m - 0.08 * C + k * 0.09 * C], fill=(60, 40, 30, 255), width=2 * S)
    d.rectangle([x0 + m - 0.09 * C, y0 + m + 0.08 * C, x0 + m - 0.01 * C, y0 + m + 0.3 * C], fill=(250, 150, 40, 255), outline=(120, 60, 10, 255), width=2 * S)
    d.rectangle([x0 + m + 0.01 * C, y0 + m + 0.08 * C, x0 + m + 0.09 * C, y0 + m + 0.3 * C], fill=(250, 150, 40, 255), outline=(120, 60, 10, 255), width=2 * S)
    # 4 rougarou: yellow eyes under heavy brows, a muzzle with a fanged snarl
    x0, y0 = cell(im, 4)
    for ex in (-0.22, 0.22):
        eye(d, x0 + m + ex * C, y0 + m - 0.2 * C, 0.1 * C, iris=(240, 200, 30))
        d.line([x0 + m + ex * C - 0.14 * C, y0 + m - 0.36 * C + (0.06 * C if ex < 0 else 0), x0 + m + ex * C + 0.14 * C, y0 + m - 0.36 * C + (0 if ex < 0 else 0.06 * C)],
               fill=(40, 30, 30, 255), width=6 * S)
    d.ellipse([x0 + m - 0.1 * C, y0 + m - 0.02 * C, x0 + m + 0.1 * C, y0 + m + 0.1 * C], fill=(20, 14, 14, 255))
    d.arc([x0 + m - 0.3 * C, y0 + m + 0.02 * C, x0 + m + 0.3 * C, y0 + m + 0.34 * C], 200, 340, fill=(40, 20, 20, 255), width=6 * S)
    for sx in (-1, 1):
        d.polygon([(x0 + m + sx * 0.18 * C - 0.03 * C, y0 + m + 0.1 * C), (x0 + m + sx * 0.18 * C + 0.03 * C, y0 + m + 0.1 * C), (x0 + m + sx * 0.18 * C, y0 + m + 0.24 * C)],
                  fill=(250, 248, 236, 255))
    # 5 bruiser: a square-jawed face, squint, a grin, a flat-top hairline
    x0, y0 = cell(im, 5)
    d.rectangle([x0 + m - 0.4 * C, y0 + m - 0.46 * C, x0 + m + 0.4 * C, y0 + m - 0.3 * C], fill=(70, 40, 20, 255))
    for ex in (-0.2, 0.2):
        d.line([x0 + m + ex * C - 0.1 * C, y0 + m - 0.14 * C, x0 + m + ex * C + 0.1 * C, y0 + m - 0.14 * C], fill=(30, 20, 20, 255), width=5 * S)
        d.line([x0 + m + ex * C - 0.12 * C, y0 + m - 0.24 * C, x0 + m + ex * C + 0.12 * C, y0 + m - 0.2 * C], fill=(60, 40, 30, 255), width=5 * S)
    d.arc([x0 + m - 0.22 * C, y0 + m - 0.0 * C, x0 + m + 0.22 * C, y0 + m + 0.28 * C], 10, 170, fill=(60, 30, 30, 255), width=5 * S)
    d.rectangle([x0 + m - 0.16 * C, y0 + m + 0.13 * C, x0 + m + 0.16 * C, y0 + m + 0.2 * C], fill=(250, 248, 236, 255))
    # 6 comet (the astronaut): a visor glint over a smiling face
    x0, y0 = cell(im, 6)
    for ex in (-0.18, 0.18):
        eye(d, x0 + m + ex * C, y0 + m - 0.1 * C, 0.09 * C, iris=(40, 80, 160))
    d.arc([x0 + m - 0.18 * C, y0 + m + 0.02 * C, x0 + m + 0.18 * C, y0 + m + 0.26 * C], 15, 165, fill=(120, 60, 50, 255), width=5 * S)
    d.ellipse([x0 + m - 0.44 * C, y0 + m - 0.46 * C, x0 + m + 0.44 * C, y0 + m + 0.44 * C], outline=(200, 230, 255, 140), width=10 * S)
    d.arc([x0 + m - 0.36 * C, y0 + m - 0.4 * C, x0 + m + 0.36 * C, y0 + m + 0.36 * C], 200, 250, fill=(255, 255, 255, 200), width=12 * S)
    # 7 a tag: "HOUMA MALL REWIND" care label used on every plush's backside
    x0, y0 = cell(im, 7)
    d.rounded_rectangle([x0 + 0.2 * C, y0 + 0.3 * C, x0 + 0.8 * C, y0 + 0.7 * C], radius=12 * S, fill=(245, 242, 232, 255), outline=(90, 90, 90, 255), width=3 * S)
    ctext(d, x0 + m, y0 + m - 0.08 * C, "POCKET CHANGE", font(F_CN, 30 * S), (40, 40, 60, 255))
    ctext(d, x0 + m, y0 + m + 0.08 * C, "PLUSH PRIZE  1995", font(F_CN, 22 * S), (120, 40, 40, 255))
    im = im.resize((4 * 256, 2 * 256), Image.LANCZOS)
    save(im, "faces", lossless=True)


# ---------------------------------------------------------------- 3. POGs
def pog_disc(d, cx, cy, r, fill, rim=(250, 246, 230)):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rim)
    d.ellipse([cx - r * 0.93, cy - r * 0.93, cx + r * 0.93, cy + r * 0.93], fill=fill)


def skull(d, cx, cy, s, col=(250, 246, 236), dark=(20, 16, 24)):
    d.ellipse([cx - s, cy - s * 1.05, cx + s, cy + s * 0.65], fill=col)
    d.rounded_rectangle([cx - s * 0.55, cy + s * 0.3, cx + s * 0.55, cy + s * 1.0], radius=s * 0.15, fill=col)
    for ex in (-0.42, 0.42):
        d.ellipse([cx + ex * s - s * 0.3, cy - s * 0.45, cx + ex * s + s * 0.3, cy + s * 0.15], fill=dark)
    d.polygon([(cx, cy + s * 0.05), (cx - s * 0.14, cy + s * 0.4), (cx + s * 0.14, cy + s * 0.4)], fill=dark)
    for k in range(-2, 3):
        d.line([cx + k * s * 0.2, cy + s * 0.62, cx + k * s * 0.2, cy + s * 0.98], fill=dark, width=max(2, int(s * 0.06)))


def pogs():
    im = Image.new("RGB", (4 * C, 2 * C), (0, 0, 0))
    d = ImageDraw.Draw(im)
    m = C / 2
    R = 0.47 * C
    # 0 Swamp Skull: a bone-white skull on murky green with a snake curling round it
    x0, y0 = cell(im, 0)
    pog_disc(d, x0 + m, y0 + m, R, (26, 64, 36))
    skull(d, x0 + m, y0 + m - 0.02 * C, 0.26 * C)
    for k in range(24):
        a = k / 24 * math.pi * 1.5 + 0.6
        d.ellipse([x0 + m + math.cos(a) * 0.36 * C - 0.04 * C, y0 + m + math.sin(a) * 0.36 * C - 0.04 * C,
                   x0 + m + math.cos(a) * 0.36 * C + 0.04 * C, y0 + m + math.sin(a) * 0.36 * C + 0.04 * C], fill=(120, 200, 70))
    ctext(d, x0 + m, y0 + m + 0.36 * C, "SWAMP SKULL", font(F_BLACKI, 20 * S), (240, 240, 200), (10, 30, 10), 3 * S)
    # 1 Gator Bite: open jaws across an orange burst
    x0, y0 = cell(im, 1)
    pog_disc(d, x0 + m, y0 + m, R, (240, 120, 20))
    for k in range(16):
        a = k / 16 * math.pi * 2
        d.line([x0 + m, y0 + m, x0 + m + math.cos(a) * R, y0 + m + math.sin(a) * R], fill=(255, 190, 40), width=6 * S)
    d.chord([x0 + m - 0.36 * C, y0 + m - 0.36 * C, x0 + m + 0.36 * C, y0 + m + 0.36 * C], 200, 340, fill=(30, 90, 40))
    d.chord([x0 + m - 0.36 * C, y0 + m - 0.36 * C, x0 + m + 0.36 * C, y0 + m + 0.36 * C], 20, 160, fill=(30, 90, 40))
    for k in range(7):
        tx = x0 + m - 0.27 * C + k * 0.09 * C
        d.polygon([(tx - 0.03 * C, y0 + m - 0.13 * C), (tx + 0.03 * C, y0 + m - 0.13 * C), (tx, y0 + m + 0.0 * C)], fill=(250, 250, 240))
        d.polygon([(tx - 0.03 * C, y0 + m + 0.13 * C), (tx + 0.03 * C, y0 + m + 0.13 * C), (tx, y0 + m + 0.0 * C)], fill=(250, 250, 240))
    ctext(d, x0 + m, y0 + m + 0.36 * C, "GATOR BITE", font(F_BLACKI, 20 * S), (255, 250, 200), (90, 30, 0), 3 * S)
    # 2 Lightning: a jagged bolt on purple
    x0, y0 = cell(im, 2)
    pog_disc(d, x0 + m, y0 + m, R, (70, 20, 120))
    bolt = [(0.08, -0.4), (-0.14, 0.02), (0.02, 0.02), (-0.1, 0.4), (0.2, -0.08), (0.04, -0.08)]
    d.polygon([(x0 + m + bx * C, y0 + m + by * C) for bx, by in bolt], fill=(255, 230, 40), outline=(255, 255, 255))
    ctext(d, x0 + m, y0 + m + 0.36 * C, "LIGHTNING", font(F_BLACKI, 20 * S), (255, 250, 200), (40, 0, 60), 3 * S)
    # 3 Eye Spy: a bloodshot eyeball on black
    x0, y0 = cell(im, 3)
    pog_disc(d, x0 + m, y0 + m, R, (12, 12, 16))
    d.ellipse([x0 + m - 0.32 * C, y0 + m - 0.32 * C, x0 + m + 0.32 * C, y0 + m + 0.32 * C], fill=(250, 246, 240))
    r = random.Random(4)
    for k in range(14):
        a = r.uniform(0, math.pi * 2)
        d.line([x0 + m + math.cos(a) * 0.17 * C, y0 + m + math.sin(a) * 0.17 * C, x0 + m + math.cos(a + 0.2) * 0.31 * C, y0 + m + math.sin(a + 0.2) * 0.31 * C], fill=(200, 40, 40), width=2 * S)
    d.ellipse([x0 + m - 0.16 * C, y0 + m - 0.16 * C, x0 + m + 0.16 * C, y0 + m + 0.16 * C], fill=(40, 150, 90))
    d.ellipse([x0 + m - 0.07 * C, y0 + m - 0.07 * C, x0 + m + 0.07 * C, y0 + m + 0.07 * C], fill=(0, 0, 0))
    d.ellipse([x0 + m - 0.12 * C, y0 + m - 0.13 * C, x0 + m - 0.05 * C, y0 + m - 0.06 * C], fill=(255, 255, 255))
    ctext(d, x0 + m, y0 + m + 0.38 * C, "EYE SPY", font(F_BLACKI, 20 * S), (255, 255, 255), (120, 0, 0), 3 * S)
    # 4 8-Ball
    x0, y0 = cell(im, 4)
    pog_disc(d, x0 + m, y0 + m, R, (14, 14, 14))
    d.ellipse([x0 + m - 0.2 * C, y0 + m - 0.2 * C, x0 + m + 0.2 * C, y0 + m + 0.2 * C], fill=(250, 250, 250))
    ctext(d, x0 + m, y0 + m, "8", font(F_BLACK, 60 * S), (10, 10, 10))
    d.ellipse([x0 + m - 0.3 * C, y0 + m - 0.34 * C, x0 + m - 0.18 * C, y0 + m - 0.26 * C], fill=(90, 90, 90))
    # 5 Hologram Eye slammer: a rainbow-foil disc with a staring eye (the rarest pull)
    x0, y0 = cell(im, 5)
    a = np.zeros((C, C, 3), np.float32)
    yy, xx = np.mgrid[0:C, 0:C]
    ang = np.arctan2(yy - m, xx - m)
    rad = np.hypot(yy - m, xx - m) / R
    hue = (ang / (2 * math.pi) * 3 + rad * 2) % 1.0
    for ch, off in enumerate((0, 1 / 3, 2 / 3)):
        a[..., ch] = 150 + 105 * np.cos((hue + off) * 2 * math.pi)
    a *= np.clip(1.15 - rad * 0.3, 0.6, 1.2)[..., None]
    foil = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    mask = Image.new("L", (C, C), 0)
    ImageDraw.Draw(mask).ellipse([m - R * 0.95, m - R * 0.95, m + R * 0.95, m + R * 0.95], fill=255)
    d.ellipse([x0 + m - R, y0 + m - R, x0 + m + R, y0 + m + R], fill=(200, 200, 210))
    im.paste(foil, (x0, y0), mask)
    d = ImageDraw.Draw(im)
    d.ellipse([x0 + m - 0.3 * C, y0 + m - 0.2 * C, x0 + m + 0.3 * C, y0 + m + 0.2 * C], fill=(250, 250, 250), outline=(30, 30, 40), width=4 * S)
    d.ellipse([x0 + m - 0.15 * C, y0 + m - 0.15 * C, x0 + m + 0.15 * C, y0 + m + 0.15 * C], fill=(120, 40, 160))
    d.ellipse([x0 + m - 0.07 * C, y0 + m - 0.07 * C, x0 + m + 0.07 * C, y0 + m + 0.07 * C], fill=(0, 0, 0))
    d.ellipse([x0 + m - 0.11 * C, y0 + m - 0.12 * C, x0 + m - 0.04 * C, y0 + m - 0.05 * C], fill=(255, 255, 255))
    ctext(d, x0 + m, y0 + m + 0.34 * C, "SLAMMER", font(F_BLACK, 18 * S), (255, 255, 255), (20, 20, 60), 3 * S)
    # 6 the cardboard back, common to every pog
    x0, y0 = cell(im, 6)
    pog_disc(d, x0 + m, y0 + m, R, (214, 196, 160), rim=(230, 220, 200))
    ctext(d, x0 + m, y0 + m - 0.05 * C, "POCKET", font(F_CN, 30 * S), (120, 100, 70))
    ctext(d, x0 + m, y0 + m + 0.08 * C, "CHANGE", font(F_CN, 30 * S), (120, 100, 70))
    # 7 the slammer's metal back
    x0, y0 = cell(im, 7)
    pog_disc(d, x0 + m, y0 + m, R, (150, 152, 160), rim=(200, 202, 210))
    im = im.filter(ImageFilter.GaussianBlur(0.6)).resize((4 * 256, 2 * 256), Image.LANCZOS)
    save(im, "pogs")


# ---------------------------------------------------------------- 4. ticket rolls in capsules: a printed strip per value
def capsule():
    W, H = 512, 3 * 64
    im = Image.new("RGB", (W, H), (240, 230, 200))
    d = ImageDraw.Draw(im)
    cols = [(220, 60, 50), (40, 90, 200), (40, 150, 80)]
    for row, (val, col) in enumerate(zip((75, 100, 200), cols)):
        y = row * 64
        d.rectangle([0, y, W, y + 64], fill=col)
        for k in range(0, W, 64):
            d.rectangle([k + 4, y + 6, k + 60, y + 58], outline=(255, 240, 200), width=2)
            ctext(d, k + 32, y + 24, str(val), font(F_BLACK, 20), (255, 245, 210))
            ctext(d, k + 32, y + 44, "TICKETS", font(F_CN, 10), (255, 245, 210))
        for k in range(0, W, 8):
            d.ellipse([k + 2, y + 1, k + 5, y + 4], fill=(255, 255, 255))
            d.ellipse([k + 2, y + 59, k + 5, y + 62], fill=(255, 255, 255))
    save(im, "capsule")


faces()
pogs()
capsule()
