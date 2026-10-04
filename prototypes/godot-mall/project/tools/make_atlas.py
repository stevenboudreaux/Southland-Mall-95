"""Store interior atlas: one back-wall picture per store, drawn by store type.

Types are guessed from the store name (apparel racks, shoe walls, food counters
with menu boards, jewelry cases, shelving for books/music/toys, service
counters). Colours come from each store's merch colours in mall-data.
Run after convert_map.py: python3 tools/make_atlas.py
"""
import json, os, random
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "..", "tex")
CW, CH, COLS, ROWS = 256, 128, 8, 12

TYPES = [
    ("food", ["COOKIE", "PIZZA", "JULIUS", "FRANKS", "CORN DOG", "CHICK", "KARMELKORN", "LION'S SHARE", "TEE TAI", "CUCOS", "GUMBALLS", "PRETZEL", "CAFE"]),
    ("jewelry", ["JEWEL", "ZALES", "GOLD", "CHAIN", "GORDON", "SILVERMAN", "CLAIRE", "AFTERTHOUGHTS"]),
    ("shoes", ["SHOE", "FOOT", "PAYLESS", "NATURALIZER", "BAKERS", "FELGER", "ATHLETE"]),
    ("shelves", ["BOOK", "DALTON", "MUSIC", "BABBAGE", "KAY-BEE", "TOYS", "SOUND SHOP", "RADIO SHACK", "NUTRITION", "WICKS", "GIFTS", "POCKET CHANGE", "K&B", "WOOLWORTH", "COUNTRY FAIR", "BLOCKBUSTER", "SPORTS"]),
    ("service", ["HAIR", "CUTS", "OPTICAL", "VISION", "PHOTO", "COPIES", "BANK", "OUTREAC", "PETS", "CINEMA", "MEN", "WOMEN"]),
]


def kind_of(name, anchor):
    if anchor:
        return "apparel"
    for k, words in TYPES:
        if any(w in name for w in words):
            return k
    return "apparel"


def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def jitter(c, rnd, k=0.2):
    f = 1 - k / 2 + rnd.random() * k
    return tuple(max(0, min(255, int(v * f))) for v in c)


def draw(kind, cols, rnd, vacant=False):
    W, H = 1024, 512
    im = Image.new("RGB", (W, H), "#ece6da")
    d = ImageDraw.Draw(im)
    if vacant:
        im = Image.new("RGB", (W, H), "#4a4744")
        d = ImageDraw.Draw(im)
        for i in range(6):
            d.rectangle([60 + i * 160, 300, 140 + i * 160, 512], fill="#3c3a37")
        return im
    if kind == "apparel":
        # wall: folded stacks on cubbies; floor: two rails of hanging garments
        for y in (60, 150):
            d.rectangle([0, y + 70, W, y + 76], fill=(170, 160, 145))
            x = 10
            while x < W - 30:
                c = jitter(cols[rnd.randrange(len(cols))], rnd)
                for k in range(4):
                    d.rectangle([x, y + 66 - k * 12, x + 46, y + 56 - k * 12 + 10], fill=jitter(c, rnd, 0.1))
                x += 62
        for ry in (300, 330):
            d.rectangle([0, ry, W, ry + 5], fill=(120, 115, 110))
            x = 4
            while x < W:
                c = jitter(cols[rnd.randrange(len(cols))], rnd)
                w = rnd.randint(10, 18)
                d.rectangle([x, ry + 5, x + w, ry + 150 + rnd.randint(-20, 30)], fill=c)
                x += w + rnd.randint(1, 4)
    elif kind == "shoes":
        for row in range(6):
            y = 40 + row * 62
            d.rectangle([0, y + 40, W, y + 46], fill=(200, 192, 178))
            x = 12
            while x < W - 40:
                c = jitter(cols[rnd.randrange(len(cols))], rnd)
                d.polygon([(x, y + 40), (x + 34, y + 40), (x + 34, y + 30), (x + 14, y + 22), (x, y + 22)], fill=c)
                x += 52
        d.rectangle([0, 440, W, 512], fill=(150, 120, 90))
    elif kind == "food":
        im = Image.new("RGB", (W, H), "#f2e7d2")
        d = ImageDraw.Draw(im)
        acc = cols[0] if cols else (200, 40, 40)
        d.rectangle([0, 0, W, 40], fill=acc)
        for b in range(3):
            x0 = 80 + b * 300
            d.rectangle([x0, 70, x0 + 240, 220], fill=(40, 36, 34))
            for li in range(6):
                d.rectangle([x0 + 16, 88 + li * 21, x0 + 150 + rnd.randint(0, 60), 96 + li * 21], fill=(235, 225, 200))
        d.rectangle([0, 330, W, 512], fill=jitter(cols[min(1, len(cols) - 1)], rnd, 0.0))
        d.rectangle([0, 320, W, 340], fill=(220, 220, 220))
        for i in range(8):
            c = jitter(cols[i % len(cols)], rnd)
            d.ellipse([60 + i * 115, 280, 110 + i * 115, 320], fill=c)
    elif kind == "jewelry":
        im = Image.new("RGB", (W, H), "#3b2633")
        d = ImageDraw.Draw(im)
        for i in range(5):
            x0 = 40 + i * 200
            d.rectangle([x0, 80, x0 + 150, 260], fill=(70, 40, 58))
            for k in range(20):
                x = x0 + 10 + rnd.random() * 130
                y = 95 + rnd.random() * 150
                d.ellipse([x, y, x + 5, y + 5], fill=(240, 215, 140))
        d.rectangle([0, 360, W, 512], fill=(30, 26, 28))
        d.rectangle([0, 340, W, 362], fill=(210, 220, 225))
    elif kind == "service":
        im = Image.new("RGB", (W, H), "#e9e6e0")
        d = ImageDraw.Draw(im)
        for i in range(3):
            c = jitter(cols[i % len(cols)], rnd)
            d.rectangle([100 + i * 300, 80, 260 + i * 300, 260], fill=c)
            d.rectangle([110 + i * 300, 90, 250 + i * 300, 250], outline=(255, 255, 255), width=3)
        d.rectangle([0, 360, W, 512], fill=jitter(cols[0], rnd, 0.0))
        d.rectangle([0, 350, W, 366], fill=(240, 240, 240))
    else:  # shelves
        for sy in (150, 270, 390):
            d.rectangle([0, sy, W, sy + 8], fill=(150, 140, 125))
            x = 8
            while x < W - 20:
                bw = rnd.randint(14, 30)
                bh = rnd.randint(40, 90)
                c = jitter(cols[rnd.randrange(len(cols))], rnd)
                d.rectangle([x, sy - bh, x + bw, sy], fill=c)
                x += bw + rnd.randint(2, 8)
    return im.filter(ImageFilter.GaussianBlur(1.0))


def main():
    L = json.load(open(os.path.join(HERE, "..", "layout_mall.json")))
    ids = sorted(L["stores"].keys())
    assert len(ids) <= COLS * ROWS
    atlas = Image.new("RGB", (COLS * CW, ROWS * CH), "#ece6da")
    kinds = {}
    for i, sid in enumerate(ids):
        sd = L["stores"][sid]
        rnd = random.Random(sid)
        cols = [hexc(c) for c in (sd["merch"] or ["#cccccc"])]
        k = kind_of(sd["name"], sd["anchor"])
        kinds[sd["name"]] = k
        im = draw(k, cols, rnd, sd["vacant"]).resize((CW, CH), Image.LANCZOS)
        atlas.paste(im, ((i % COLS) * CW, (i // COLS) * CH))
    atlas.save(os.path.join(OUT, "int_atlas.png"))
    json.dump(kinds, open(os.path.join(HERE, "..", "store_kinds.json"), "w"), indent=1)
    print("atlas", atlas.size, {k: list(kinds.values()).count(k) for k in set(kinds.values())})


if __name__ == "__main__":
    main()
