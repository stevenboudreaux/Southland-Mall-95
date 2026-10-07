"""Textures for the sports stores' stock (Champs Sports, Sports Avenue; tools/stores/small/sports.gd).
Every team here is invented: colours, stripes and numbers only, no names or logos.
  tex/sp/jerseys.png  1024 x 512: 8 x 2 jerseys faced out, alpha cut-out (row 0 football, row 1
                      basketball and baseball)
  tex/sp/racks.png    512 x 256: jerseys hanging on a rail seen side-on, 4 bands (rows)
  tex/sp/pennant.png  256 x 128: felt pennants, 4 x 2
Run: python3 tools/stores/small/paint_sports.py   (from the project folder)
"""
import os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "..", "tex", "sp")
FONT = os.path.join(HERE, "..", "signs", "src", "FrancoisOne-Regular.ttf")
# invented team colours: body, trim, number
TEAMS = [("#1f3f8f", "#f2c94c", "#ffffff"), ("#b3141a", "#ffffff", "#ffffff"), ("#145a32", "#f2c94c", "#ffffff"),
         ("#4b2a7a", "#f2c94c", "#f2c94c"), ("#f2f0ea", "#1f3f8f", "#1f3f8f"), ("#111114", "#c8202c", "#ffffff"),
         ("#0d7c8c", "#f08a24", "#ffffff"), ("#d85a12", "#1c1c20", "#1c1c20"), ("#5a0f1e", "#d8c08a", "#d8c08a"),
         ("#2a6ec8", "#ffffff", "#ffffff"), ("#c8b88a", "#1c1c20", "#1c1c20"), ("#e8e8e8", "#c8202c", "#c8202c")]


def jersey(d, x, y, w, h, body, trim, num, kind, number, font):
    if kind == "football":
        pts = [(x + w * .28, y + h * .06), (x + w * .40, y + h * .10), (x + w * .60, y + h * .10), (x + w * .72, y + h * .06),
               (x + w * .98, y + h * .20), (x + w * .90, y + h * .38), (x + w * .80, y + h * .34), (x + w * .80, y + h * .96),
               (x + w * .20, y + h * .96), (x + w * .20, y + h * .34), (x + w * .10, y + h * .38), (x + w * .02, y + h * .20)]
        d.polygon(pts, fill=body)
        for k in (0.28, 0.32):   # sleeve stripes
            d.line([(x + w * (0.02 + k * 0.25), y + h * (0.20 + k * 0.4)), (x + w * (0.12 + k * 0.2), y + h * (0.14 + k * 0.2))], fill=trim, width=5)
            d.line([(x + w * (0.98 - k * 0.25), y + h * (0.20 + k * 0.4)), (x + w * (0.88 - k * 0.2), y + h * (0.14 + k * 0.2))], fill=trim, width=5)
        d.polygon([(x + w * .40, y + h * .10), (x + w * .50, y + h * .18), (x + w * .60, y + h * .10)], fill=trim)
    elif kind == "basketball":
        pts = [(x + w * .30, y + h * .04), (x + w * .40, y + h * .04), (x + w * .50, y + h * .16), (x + w * .60, y + h * .04),
               (x + w * .70, y + h * .04), (x + w * .72, y + h * .22), (x + w * .84, y + h * .30), (x + w * .84, y + h * .96),
               (x + w * .16, y + h * .96), (x + w * .16, y + h * .30), (x + w * .28, y + h * .22)]
        d.polygon(pts, fill=body)
        d.line(pts[:5] + [pts[5]], fill=trim, width=4)
    else:  # baseball: buttoned, short sleeves, piping
        pts = [(x + w * .32, y + h * .06), (x + w * .50, y + h * .14), (x + w * .68, y + h * .06), (x + w * .94, y + h * .18),
               (x + w * .88, y + h * .34), (x + w * .80, y + h * .32), (x + w * .80, y + h * .96), (x + w * .20, y + h * .96),
               (x + w * .20, y + h * .32), (x + w * .12, y + h * .34), (x + w * .06, y + h * .18)]
        d.polygon(pts, fill=body)
        d.line([(x + w * .5, y + h * .14), (x + w * .5, y + h * .96)], fill=trim, width=3)
        for k in range(5):
            d.ellipse([x + w * .5 - 3 + 7, y + h * (0.22 + k * 0.14) - 3, x + w * .5 + 3 + 7, y + h * (0.22 + k * 0.14) + 3], fill=trim)
    tw = d.textlength(number, font=font)
    d.text((x + w * 0.5 - tw * 0.5 + (w * 0.12 if kind == "baseball" else 0), y + h * 0.36), number, font=font, fill=num, stroke_width=2, stroke_fill=trim)


def main():
    os.makedirs(OUT, exist_ok=True)
    rng = random.Random(1995)
    font = ImageFont.truetype(FONT, 92)
    im = Image.new("RGBA", (1024, 512), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for row in range(2):
        for col in range(8):
            body, trim, num = TEAMS[(col * 5 + row * 3) % len(TEAMS)]
            kind = "football" if row == 0 else ("basketball" if col % 2 == 0 else "baseball")
            jersey(d, col * 128 + 4, row * 256 + 8, 120, 240, body, trim, num, kind, str(rng.choice([1, 3, 7, 8, 12, 14, 21, 23, 32, 33, 44, 55, 80, 88, 99])), font)
    im.save(os.path.join(OUT, "jerseys.png"))
    # racks: jerseys side-on on a rail, each a narrow strip in its team colour with a sleeve stripe
    rk = Image.new("RGB", (512, 256), (40, 40, 44))
    d = ImageDraw.Draw(rk)
    for row in range(4):
        x = 0
        while x < 512:
            body, trim, _ = TEAMS[rng.randrange(len(TEAMS))]
            w = rng.randint(6, 10)
            y0, y1 = row * 64 + 2, row * 64 + 62
            d.rectangle([x, y0 + rng.randint(0, 6), x + w - 1, y1], fill=body)
            d.rectangle([x, y0 + 14, x + w - 1, y0 + 17], fill=trim)
            d.line([(x + w - 1, y0), (x + w - 1, y1)], fill=(20, 20, 22))
            x += w
    rk.save(os.path.join(OUT, "racks.png"))
    # pennants: felt triangles with a band and a star
    pn = Image.new("RGBA", (256, 128), (0, 0, 0, 0))
    d = ImageDraw.Draw(pn)
    for k in range(8):
        body, trim, _ = TEAMS[(k * 7 + 2) % len(TEAMS)]
        x, y = (k % 4) * 64, (k // 4) * 64
        d.polygon([(x + 2, y + 6), (x + 62, y + 32), (x + 2, y + 58)], fill=body)
        d.rectangle([x + 2, y + 6, x + 9, y + 58], fill=trim)
        d.ellipse([x + 20, y + 26, x + 32, y + 38], fill=trim)
    pn.save(os.path.join(OUT, "pennant.png"))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
