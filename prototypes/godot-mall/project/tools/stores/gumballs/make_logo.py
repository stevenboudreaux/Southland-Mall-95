"""Outline of Gumballs' sign script, for store.gd to extrude (design/storefronts/gumballs.md).

The sign (video 1:07-1:09): "Gumballs" in a tall, slanted brush script rising to the right,
with a long swash sweeping under the word from the G's tail out past the s. Mr Dafoe
(OFL-1.1, MrDafoe-Regular.ttf here) is the nearest free brush script; it is thickened to
the sign's heavier stroke and the swash is drawn. The word is rasterised, traced (OpenCV)
and triangulated with its holes (earcut). Units are metres: x from the left, y up from the
lowest point. Writes tools/stores/gumballs/logo.json, and logo_preview.png to check.
  python3 tools/stores/gumballs/make_logo.py   (from the project folder)
"""
import json, math, os
import cv2
import mapbox_earcut as earcut
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "MrDafoe-Regular.ttf")
WIDTH_M = 3.85          # the word across the fascia (the video's sign is ~3.5 x 1 m)
PX = 2600
TILT = 6.0             # degrees: the word rises to the right


def swash(d, pts, w0, w1, w2):
    """A tapered brush stroke along a quadratic-ish polyline: thin, thick, thin."""
    n = 220
    (x0, y0), (x1, y1), (x2, y2) = pts
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * x1 + t * t * x2
        y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * y1 + t * t * y2
        w = (w0 + (w1 - w0) * (t / 0.45)) if t < 0.45 else (w1 + (w2 - w1) * ((t - 0.45) / 0.55))
        d.ellipse([x - w, y - w * 0.8, x + w, y + w * 0.8], fill=255)


def mask():
    W, H = PX, 1100
    im = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 600)
    d.text((170, 120), "Gumballs", font=f, fill=255, stroke_width=13, stroke_fill=255)
    # the swash: from under the G's tail, low under "umb", rising out past the s
    swash(d, [(330, 860), (1150, 830), (2330, 560)], 12, 50, 7)
    im = im.rotate(TILT, resample=Image.BICUBIC, center=(W / 2, H / 2), fillcolor=0)
    a = (np.asarray(im) > 110).astype(np.uint8) * 255
    a = cv2.morphologyEx(a, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return a


def main():
    a = mask()
    ys, xs = np.nonzero(a)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    s = WIDTH_M / float(x1 - x0)
    cons, hier = cv2.findContours(a, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    hier = hier[0]
    to_m = lambda p: [round((float(p[0]) - x0) * s, 4), round((y1 - float(p[1])) * s, 4)]
    letters = []
    ntri = 0
    for i, c in enumerate(cons):
        if hier[i][3] != -1:
            continue    # a hole: handled with its outer
        if cv2.contourArea(c) < 60:
            continue
        outer = cv2.approxPolyDP(c, 1.4, True)[:, 0, :]
        holes = []
        k = hier[i][2]
        while k != -1:
            if cv2.contourArea(cons[k]) > 40:
                holes.append(cv2.approxPolyDP(cons[k], 1.4, True)[:, 0, :])
            k = hier[k][0]
        O = [to_m(p) for p in outer]
        # outer counter-clockwise, holes clockwise, as seen from the front with y up
        ar = sum(O[j][0] * O[(j + 1) % len(O)][1] - O[(j + 1) % len(O)][0] * O[j][1] for j in range(len(O)))
        if ar < 0:
            O = O[::-1]
        Hs = []
        for h in holes:
            Hm = [to_m(p) for p in h]
            ah = sum(Hm[j][0] * Hm[(j + 1) % len(Hm)][1] - Hm[(j + 1) % len(Hm)][0] * Hm[j][1] for j in range(len(Hm)))
            Hs.append(Hm if ah < 0 else Hm[::-1])
        verts = list(O)
        rings = [len(verts)]
        for h in Hs:
            verts += h
            rings.append(len(verts))
        idx = earcut.triangulate_float32(np.array(verts, dtype=np.float32).reshape(-1, 2), np.array(rings, dtype=np.uint32))
        tris = [verts[j] for j in idx]
        ntri += len(tris) // 3
        letters.append({"tris": tris, "loops": [O] + Hs})
    out = {"text": "Gumballs", "width": WIDTH_M, "height": round((y1 - y0) * s, 4), "letters": letters,
           "note": "loops: outer counter-clockwise, holes clockwise (seen from the front, y up); tris: face triangles"}
    json.dump(out, open(os.path.join(HERE, "logo.json"), "w"))
    prev = Image.fromarray(a[y0:y1 + 1, x0:x1 + 1]).resize((900, int(900 * (y1 - y0) / (x1 - x0))))
    prev.save(os.path.join(HERE, "logo_preview.png"))
    print("logo %.2f x %.2f m, %d parts, %d triangles" % (WIDTH_M, out["height"], len(letters), ntri))


if __name__ == "__main__":
    main()
