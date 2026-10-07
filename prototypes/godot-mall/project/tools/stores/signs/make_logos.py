"""Sign logos traced from Steven's photos, for channel.gd to build as 3D channel letters.

Writes, per logo, tools/stores/signs/<id>_logo.json (the letters.json format of
apparel/kit.gd letters(): per letter, face triangles and outline loops in metres, baseline
y = 0, x from 0) and two textures in tex/sg/: <id>_face.png (the lit face: brighter along
the middle of each stroke, a faint grain) and <id>_glow.png (the halo the letters throw on
the fascia).

- Radio Shack ("rs"): traced with potrace from Steven's close-up of the red channel letters
  (design/storefronts/refs/radio-shack-letters-1.png), first warped onto his frontal photo
  of the storefront (radio-shack-front.png) so the shapes are seen square-on. The cleaned
  mask is src/rs_mask.png: touching faces are split where the photo shows the seams.
- Woolworth ("wl"): the capitals WOOLWORTH from Steven's photo of the lit sign
  (refs/woolworth-front.png). The photo is too soft to trace cleanly, so each letter is the
  Coustard Black glyph (OFL, src/Coustard-Black.ttf: the closest match of 17 slab-serif
  faces), fitted to that letter's box in the levelled photo, so widths and spacing are the
  photo's.

  python3 tools/stores/signs/make_logos.py   (from the project folder; needs opencv-python-headless,
  potracer, mapbox_earcut, fonttools, pillow)
"""
import json, os
import cv2
import numpy as np
import potrace
import mapbox_earcut as earcut
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "..", "..", "..", "tex", "sg")
STEPS = 10


def area(c):
    return 0.5 * sum(c[i][0] * c[(i + 1) % len(c)][1] - c[(i + 1) % len(c)][0] * c[i][1] for i in range(len(c)))


def inside(pt, c):
    x, y = pt
    n = False
    for i in range(len(c)):
        (xa, ya), (xb, yb) = c[i], c[(i + 1) % len(c)]
        if (ya > y) != (yb > y) and x < (xb - xa) * (y - ya) / (yb - ya) + xa:
            n = not n
    return n


def letter(ch, cons):
    """Contours (metres, y up) -> {ch, tris, loops}: outers counter-clockwise, holes clockwise."""
    outers, holes = [], []
    for c in cons:
        d = sum(1 for o in cons if o is not c and inside(c[0], o))
        (outers if d % 2 == 0 else holes).append(c)
    tris, loops = [], []
    for o in outers:
        if area(o) < 0:
            o = o[::-1]
        hs = [h if area(h) < 0 else h[::-1] for h in holes if inside(h[0], o)]
        verts = list(o)
        rings = [len(verts)]
        for h in hs:
            verts += h
            rings.append(len(verts))
        idx = earcut.triangulate_float32(np.array(verts, dtype=np.float32).reshape(-1, 2), np.array(rings, dtype=np.uint32))
        tris += [[round(verts[i][0], 5), round(verts[i][1], 5)] for i in idx]
        loops.append([[round(p[0], 5), round(p[1], 5)] for p in o])
        loops += [[[round(p[0], 5), round(p[1], 5)] for p in h] for h in hs]
    return {"ch": ch, "tris": tris, "loops": loops}


def dedupe(pts):
    out = []
    for p in pts:
        if not out or abs(p[0] - out[-1][0]) + abs(p[1] - out[-1][1]) > 1e-4:
            out.append(p)
    if len(out) > 2 and abs(out[0][0] - out[-1][0]) + abs(out[0][1] - out[-1][1]) <= 1e-4:
        out.pop()
    return out


# ------------------------------------------------------------------ traced from a mask
def trace_mask(mask, text, width_m, base_px):
    ys, xs = np.where(mask)
    x0, x1 = xs.min(), xs.max()
    s = width_m / (x1 - x0)
    n, lab = cv2.connectedComponents(mask.astype(np.uint8), connectivity=4)
    comps = []
    for i in range(1, n):
        cm = lab == i
        if cm.sum() < 400:
            continue
        path = potrace.Bitmap(~cm).trace(   # potracer fills False pixels
                                       turdsize=40, turnpolicy=potrace.POTRACE_TURNPOLICY_MINORITY,
                                       alphamax=1.15, opticurve=True, opttolerance=0.5)
        cons = []
        for curve in path:
            X = lambda q: (q.x, q.y)
            pts = [X(curve.start_point)]
            for seg in curve.segments:
                if seg.is_corner:
                    pts += [X(seg.c), X(seg.end_point)]
                else:
                    p0, c1, c2, p3 = pts[-1], X(seg.c1), X(seg.c2), X(seg.end_point)
                    for k in range(1, STEPS + 1):
                        t = k / STEPS
                        mt = 1 - t
                        pts.append((mt ** 3 * p0[0] + 3 * mt * mt * t * c1[0] + 3 * mt * t * t * c2[0] + t ** 3 * p3[0],
                                    mt ** 3 * p0[1] + 3 * mt * mt * t * c1[1] + 3 * mt * t * t * c2[1] + t ** 3 * p3[1]))
            cons.append(dedupe([((p[0] - x0) * s, (base_px - p[1]) * s) for p in pts]))
        comps.append((np.where(cm)[1].min(), cons))
    comps.sort(key=lambda t: t[0])
    chars = text.replace(" ", "")
    return [letter(chars[k], cons) for k, (_, cons) in enumerate(comps)]


# ------------------------------------------------------------------ font glyphs fitted to boxes
class FlatPen(BasePen):
    def __init__(self, gs):
        super().__init__(gs)
        self.contours, self.cur = [], []

    def _moveTo(self, p):
        self.cur = [p]

    def _lineTo(self, p):
        self.cur.append(p)

    def _curveToOne(self, p1, p2, p3):
        p0 = self.cur[-1]
        for i in range(1, STEPS + 1):
            t = i / STEPS
            mt = 1 - t
            self.cur.append((mt ** 3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t ** 3 * p3[0],
                             mt ** 3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t ** 3 * p3[1]))

    def _qCurveToOne(self, p1, p2):
        p0 = self.cur[-1]
        for i in range(1, STEPS + 1):
            t = i / STEPS
            mt = 1 - t
            self.cur.append((mt * mt * p0[0] + 2 * mt * t * p1[0] + t * t * p2[0], mt * mt * p0[1] + 2 * mt * t * p1[1] + t * t * p2[1]))

    def _closePath(self):
        if len(self.cur) > 2:
            self.contours.append(dedupe(self.cur))
        self.cur = []

    _endPath = _closePath


def fit_glyphs(font, text, boxes, base_px, cap_m):
    """boxes: (x, y, w, h) of each letter in photo pixels (y down); base_px: the baseline row."""
    f = TTFont(font)
    gs = f.getGlyphSet()
    cmap = f.getBestCmap()
    tops = sorted(b[1] for b in boxes)
    cap_px = base_px - tops[len(tops) // 2]
    s = cap_m / cap_px
    x0 = boxes[0][0]
    out = []
    for ch, (bx, by, bw, bh) in zip(text, boxes):
        pen = FlatPen(gs)
        gs[cmap[ord(ch)]].draw(pen)
        pts = [p for c in pen.contours for p in c]
        gx0, gx1 = min(p[0] for p in pts), max(p[0] for p in pts)
        gy0, gy1 = min(p[1] for p in pts), max(p[1] for p in pts)
        # the letter's box in metres (y up from the baseline)
        L, R = (bx - x0) * s, (bx + bw - x0) * s
        B, T = (base_px - (by + bh)) * s, (base_px - by) * s
        cons = [[(L + (p[0] - gx0) / (gx1 - gx0) * (R - L), B + (p[1] - gy0) / (gy1 - gy0) * (T - B)) for p in c] for c in pen.contours]
        out.append(letter(ch, cons))
    return out


# ------------------------------------------------------------------ textures
def textures(lid, letters, width, top, glow_rgb, pad, face_lo=0.72):
    """face: UV (x / width, 1 - y / top); glow: covers the letters plus pad metres all round."""
    W = 2048
    k = W / width
    H = max(64, int(round(top * k)))
    m = np.zeros((H, W), np.uint8)
    for L in letters:
        for lp in L["loops"]:
            pts = np.array([[p[0] * k, H - p[1] * k] for p in lp], np.int32)
            cv2.fillPoly(m, [pts], 255 if area(lp) > 0 else 0)
    # face: strokes brighter along the middle (lamps inside the letter), darker at the trim
    dist = cv2.distanceTransform((m > 0).astype(np.uint8), cv2.DIST_L2, 5)
    stroke = max(1.0, np.percentile(dist[m > 0], 95))
    v = face_lo + (1.0 - face_lo) * np.clip(dist / stroke, 0, 1) ** 0.6
    rng = np.random.default_rng(7)
    grain = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 1.2)
    v = np.clip(v + grain * 0.015, 0, 1)
    v = cv2.dilate((v * 255).astype(np.uint8), np.ones((5, 5), np.uint8))   # no dark rim at the face's own edge
    face = np.dstack([v, v, v])
    cv2.imwrite(os.path.join(TEX, lid + "_face.png"), cv2.resize(face, (1024, max(32, H // 2)), interpolation=cv2.INTER_AREA))
    # glow: the letters blurred, as alpha over a flat colour
    P = int(round(pad * k))
    g = cv2.copyMakeBorder(m, P, P, P, P, cv2.BORDER_CONSTANT, value=0).astype(np.float32) / 255
    g = cv2.GaussianBlur(g, (0, 0), P * 0.35) * 0.8 + cv2.GaussianBlur(g, (0, 0), P * 0.12) * 0.5
    a = np.clip(g / max(g.max(), 1e-6), 0, 1)
    # premultiplied: the colour fades to black with the alpha, so an additive blend needs no alpha
    rgba = np.dstack([a * glow_rgb[2], a * glow_rgb[1], a * glow_rgb[0], a * 255]).astype(np.uint8)
    cv2.imwrite(os.path.join(TEX, lid + "_glow.png"), cv2.resize(rgba, (512, max(16, int(512 * rgba.shape[0] / rgba.shape[1]))), interpolation=cv2.INTER_AREA))


def write(lid, text, letters, width, glow_rgb, pad, note):
    top = max(p[1] for L in letters for lp in L["loops"] for p in lp)
    json.dump({"text": text, "cap_h": round(top, 4), "width": round(width, 4), "glow_pad": pad, "letters": letters, "note": note},
              open(os.path.join(HERE, lid + "_logo.json"), "w"))
    textures(lid, letters, width, top, glow_rgb, pad)
    print("%s: %d letters, %.2f x %.2f m, %d triangles" % (lid, len(letters), width, top, sum(len(L["tris"]) for L in letters) // 3))


def main():
    os.makedirs(TEX, exist_ok=True)
    # Radio Shack: 4.2 m across the 8 m front, about half the fascia's width as in the photo
    rs = cv2.imread(os.path.join(HERE, "src", "rs_mask.png"), 0) > 127
    write("rs", "Radio Shack", trace_mask(rs, "Radio Shack", 4.2, 698), 4.2, (255, 40, 40), 0.3,
          "traced from Steven's photos (make_logos.py)")
    # Woolworth: letter boxes in the levelled photo (1.6 px per photo pixel), baseline row 130.5;
    # capitals 0.78 m, about 55 % of the 1.4 m fascia as in the photo
    boxes = [(9, 46, 127, 86), (138, 44, 84, 88), (233, 42, 83, 89), (324, 43, 80, 86), (395, 44, 129, 86),
             (526, 43, 85, 87), (619, 45, 90, 86), (710, 45, 83, 84), (800, 44, 103, 87)]
    wl = fit_glyphs(os.path.join(HERE, "src", "Coustard-Black.ttf"), "WOOLWORTH", boxes, 130.5, 0.78)
    width = max(p[0] for L in wl for lp in L["loops"] for p in lp)
    write("wl", "WOOLWORTH", wl, width, (255, 60, 30), 0.35, "Coustard Black glyphs fitted to Steven's photo (make_logos.py)")


if __name__ == "__main__":
    main()
