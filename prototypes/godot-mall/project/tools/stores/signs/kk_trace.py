"""Traces the Karmelkorn letter cans (src/kk_cans.png) from Steven's square-on photo (Oct 7 2026).

The photo (src/kk_front.jpg: his 582 px night photo cropped to the sign and enlarged 4x) is too
small and too soft to trace each letter: the glow joins them. So this fits a typeface instead:
  1. each capital's box is read off the photo: the dark gaps between letters (CUTS), the caps
     band (Y0..Y1);
  2. each glyph of the typeface is fitted into its box by correlation with the photo's brightness,
     after blurring the glyph as much as the photo is blurred (--fonts scores several faces:
     Oct 7, Coustard Black 0.67 with Ultra, Holtwood One SC, Bevan and Alfa Slab One close behind;
     Coustard read closest by eye, its bracketed wedge serifs);
  3. the swash K is built: Coustard's I fitted to its stem, and the arm, top bar, leg and the
     swash under the A as straight strokes measured off a trace of the photo (centre lines and
     widths, less the glow);
  4. the cans keep 1.5 photo px of air between them; slivers are dropped.
Then make_kk.py turns src/kk_cans.png into the sign.

  python3 tools/stores/signs/kk_trace.py [--fonts a.ttf b.ttf ...] [--overlay check.png]
"""
import argparse, os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
FONT = os.path.join(SRC, "Coustard-Black.ttf")
CUTS = [366, 554, 753, 973, 1137, 1278, 1448, 1624, 1785, 1962]   # photo px: the gaps between capitals
CAPS = "ARMELKORN"
Y0, Y1 = 120, 258                                                    # the caps band
STEM = (115, 202, 61, 295)                                           # the K's stem, fitted (Oct 7)
S = 3                                                                # the mask is 3x the photo
ERODE = 3                                                            # photo px: the sign's strokes are lighter

im = cv2.imread(os.path.join(SRC, "kk_front.jpg"))
V = cv2.GaussianBlur(cv2.cvtColor(im, cv2.COLOR_BGR2HSV)[..., 2].astype(np.float32), (0, 0), 1.0)


def glyph(font, ch, size=400):
    f = ImageFont.truetype(font, size)
    g = Image.new("L", (size * 2, size * 2), 0)
    ImageDraw.Draw(g).text((size // 2, size * 3 // 2), ch, font=f, fill=255, anchor="ls")
    a = np.array(g); ys, xs = np.nonzero(a > 127)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def score(g, x0, x1, y0, y1, sig=4.0, pad=14):
    w, h = x1 - x0, y1 - y0
    gm = cv2.resize(g, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    c = np.zeros((h + 2 * pad, w + 2 * pad), np.float32); c[pad:pad + h, pad:pad + w] = gm
    gb = cv2.GaussianBlur(c, (0, 0), sig)
    T = V[y0 - pad:y1 + pad, x0 - pad:x1 + pad]
    a = gb - gb.mean(); b = T - T.mean()
    return float((a * b).sum() / (np.sqrt((a * a).sum() * (b * b).sum()) + 1e-6))


def fit(g, x0, x1, y0=Y0, y1=Y1):
    best = (-1.0, None)
    for dx0 in range(-9, 10, 3):
        for dx1 in range(-9, 10, 3):
            for dy0 in (-6, -3, 0, 3, 6):
                for dy1 in (-6, -3, 0, 3, 6):
                    s = score(g, x0 + dx0, x1 + dx1, y0 + dy0, y1 + dy1)
                    if s > best[0]:
                        best = (s, (x0 + dx0, x1 + dx1, y0 + dy0, y1 + dy1))
    return best


def boxes(font):
    out = []
    for i, ch in enumerate(CAPS):
        s, b = fit(glyph(font, ch), CUTS[i] + 4, CUTS[i + 1] - 4)
        out.append((ch, s, b))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonts", nargs="*")
    ap.add_argument("--overlay")
    A = ap.parse_args()
    if A.fonts:
        for f in A.fonts:
            r = boxes(f); print(f"{np.mean([s for _, s, _ in r]):.3f}", os.path.basename(f), [round(s, 2) for _, s, _ in r])
        return
    H, W = im.shape[:2]
    blank = np.zeros((H * S, W * S), np.uint8)

    def put(ch, x0, x1, y0, y1):
        g = cv2.resize(glyph(FONT, ch, 600), ((x1 - x0) * S, (y1 - y0) * S), interpolation=cv2.INTER_AREA)
        g = cv2.erode(g, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * ERODE * S + 1,) * 2))
        m = blank.copy(); m[y0 * S:y1 * S, x0 * S:x1 * S] = (g > 127) * 255
        return m

    def poly(pts):
        m = blank.copy()
        cv2.fillPoly(m, [np.round(np.array(pts, np.float64) * S * 8).astype(np.int32)], 255, cv2.LINE_AA, 3)
        return m

    def stroke(p0, p1, w0, w1):
        p0 = np.array(p0, float); p1 = np.array(p1, float); d = (p1 - p0) / np.linalg.norm(p1 - p0); nv = np.array([-d[1], d[0]])
        return poly([p0 + nv * w0 / 2, p1 + nv * w1 / 2, p1 - nv * w1 / 2, p0 - nv * w0 / 2])

    sm = lambda m: (cv2.GaussianBlur(m, (0, 0), 2.0) > 127).astype(np.uint8) * 255
    parts = [put(ch, *b) for ch, _, b in boxes(FONT)]
    # the K: stem, the arm up to the top bar, the bar, the leg with its foot; then the swash
    k = np.maximum.reduce([put("I", *STEM), stroke((180, 182), (384, 92), 21, 23),
                           poly([(318, 79), (350, 74), (497, 72), (507, 78), (503, 97), (372, 99), (348, 93)]),
                           stroke((185, 186), (346, 238), 25, 23), poly([(330, 226), (352, 228), (366, 244), (338, 247)])])
    parts.insert(0, sm(k))
    parts.append(sm(poly([(386, 286), (398, 274), (440, 271), (588, 272), (618, 281), (590, 292), (440, 296), (398, 296)])))
    cans = blank.copy()
    for p in parts:
        gap = cv2.dilate(cans, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3 * S + 1,) * 2))
        cans = np.maximum(cans, np.where(gap > 0, 0, p).astype(np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(cans, 8)
    keep = np.zeros_like(cans)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] > 20000:
            keep[lab == i] = 255
    cv2.imwrite(os.path.join(SRC, "kk_cans.png"), keep)
    print("cans", cv2.connectedComponents(keep)[0] - 1)
    if A.overlay:
        ov = cv2.resize(im, (W * S, H * S), interpolation=cv2.INTER_CUBIC)
        cs, _ = cv2.findContours(keep, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(ov, cs, -1, (255, 255, 0), 3)
        cv2.imwrite(A.overlay, ov)


if __name__ == "__main__":
    main()
