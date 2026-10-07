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
def trace_mask(mask, text, width_m, base_px, frame=None, smooth=0.0):
    """frame: (x0_px, metres per px) to share one frame between several masks; else the
    mask's own left edge and width_m. smooth: Gaussian sigma (px) applied to each shape alone."""
    ys, xs = np.where(mask)
    if frame:
        x0, s = frame
    else:
        x0, x1 = xs.min(), xs.max()
        s = width_m / (x1 - x0)
    n, lab = cv2.connectedComponents(mask.astype(np.uint8), connectivity=4)
    comps = []
    for i in range(1, n):
        cm = lab == i
        if cm.sum() < 400:
            continue
        if smooth > 0:
            cm = cv2.GaussianBlur(cm.astype(np.float32), (0, 0), smooth) > 0.5
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
    return [letter(chars[k] if k < len(chars) else "?", cons) for k, (_, cons) in enumerate(comps)]


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


def fit_words(font, words, frame_x0, base_px, s_px):
    """words: [(text, (x, y, w, h) px)]: each word set in the font (its own spacing), its outline
    stretched to the box; frame: metres = (px - frame_x0) * s_px across, (base_px - py) * s_px up."""
    f = TTFont(font)
    gs = f.getGlyphSet()
    cmap = f.getBestCmap()
    hmtx = f["hmtx"]
    out = []
    for text, (bx, by, bw, bh) in words:
        glyphs = []
        x = 0.0
        for ch in text:
            gname = cmap.get(ord(ch)) or cmap.get(ord("'"))
            pen = FlatPen(gs)
            gs[gname].draw(pen)
            glyphs.append((ch, [[(p[0] + x, p[1]) for p in c] for c in pen.contours]))
            x += hmtx[gname][0]
        pts = [p for _, cs in glyphs for c in cs for p in c]
        gx0, gx1 = min(p[0] for p in pts), max(p[0] for p in pts)
        gy0, gy1 = min(p[1] for p in pts), max(p[1] for p in pts)
        L, R = (bx - frame_x0) * s_px, (bx + bw - frame_x0) * s_px
        B, T = (base_px - (by + bh)) * s_px, (base_px - by) * s_px
        for ch, cs in glyphs:
            if not cs:
                continue
            out.append(letter(ch, [[(L + (p[0] - gx0) / (gx1 - gx0) * (R - L), B + (p[1] - gy0) / (gy1 - gy0) * (T - B)) for p in c] for c in cs]))
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


def write(lid, text, letters, width, glow_rgb, pad, note, top=None, tex=True):
    """width/top: the frame the shapes sit in (channel.gd centres on width; face UVs span it)."""
    if top is None:
        top = max(p[1] for L in letters for lp in L["loops"] for p in lp)
    json.dump({"text": text, "cap_h": round(top, 4), "width": round(width, 4), "glow_pad": pad, "letters": letters, "note": note},
              open(os.path.join(HERE, lid + "_logo.json"), "w"))
    if tex:
        textures(lid, letters, width, top, glow_rgb, pad)
    print("%s: %d letters, %.2f x %.2f m, %d triangles" % (lid, len(letters), width, top, sum(len(L["tris"]) for L in letters) // 3))


def wood_planks(path, base=(122, 74, 42)):
    """Diagonal wood planks at 45 degrees, 1024 px = 1 m, tiling: grooves every 1/8 m along x + y
    (planks 8.8 cm wide), each plank its own shade, grain along the plank (sums of whole-period
    sines, so it tiles too)."""
    N = 1024
    y, x = np.mgrid[0:N, 0:N].astype(np.float32) / N
    a = (x + y) * 8.0                       # across the planks: plank index = floor(a)
    b = (x - y)                             # along the planks
    k = np.floor(a) % 8
    rng = np.random.default_rng(3)
    shade = rng.uniform(0.82, 1.12, 8)[k.astype(int)]
    grain = np.zeros_like(x)
    for m, amp in ((53, 0.05), (97, 0.035), (181, 0.025)):
        ph = rng.uniform(0, 6.28, 8)[k.astype(int)]
        wob = 0.6 * np.sin(2 * np.pi * (2 * b) + ph) + 0.3 * np.sin(2 * np.pi * (5 * b) + 2 * ph)
        grain += amp * np.sin(2 * np.pi * m * (x + y) + wob * 3.0 + ph)
    fine = cv2.GaussianBlur(rng.normal(0, 1, (N, N)).astype(np.float32), (0, 0), 1.0)
    groove = np.clip(np.abs((a % 1.0) - 0.5) * 2.0, 0, 1)      # 1 at the plank edges
    groove = np.where(groove > 0.94, 0.6, 1.0)
    v = shade * (1.0 + grain + fine * 0.03) * groove
    img = np.dstack([np.clip(base[2] * v, 0, 255), np.clip(base[1] * v, 0, 255), np.clip(base[0] * v, 0, 255)]).astype(np.uint8)
    cv2.imwrite(path, cv2.resize(img, (512, 512), interpolation=cv2.INTER_AREA))


def rect_ring(x0, y0, x1, y1, w):
    """A rectangular band of width w inside (x0, y0)-(x1, y1): one outline with one hole."""
    return letter("#", [[(x0, y0), (x1, y0), (x1, y1), (x0, y1)], [(x0 + w, y0 + w), (x0 + w, y1 - w), (x1 - w, y1 - w), (x1 - w, y0 + w)]])


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

    # Foot Locker (refs/foot-locker-front.jpg, levelled 1.79 degrees, 6 px per photo pixel): the
    # photo's red-and-gold letters are too soft to trace, so each is Fredoka Bold (OFL, the best
    # of 50 rounded and geometric faces) fitted to the letter's box; baseline row 260; the
    # ascenders ('f', 'L', 'k') 0.56 m. The oval: 0.86 x 0.58 m (the photo's 460 x 308 px),
    # with the runner traced from the photo (src/fl_figure.png, 10 px per photo pixel).
    fl_boxes = [(86, 65, 105, 197), (219, 147, 134, 115), (379, 133, 133, 128), (530, 110, 92, 152), (758, 60, 106, 192),
                (892, 137, 131, 115), (1040, 134, 110, 126), (1179, 70, 134, 191), (1333, 131, 106, 128), (1471, 138, 78, 117)]
    fl_boxes = [(x, y, w, 260 - y) for (x, y, w, h) in fl_boxes]     # every letter sits on the baseline
    asc = 260 - min(b[1] for b in fl_boxes)
    fl = fit_glyphs(os.path.join(HERE, "src", "Fredoka-Bold.ttf"), "footLocker", fl_boxes, 260, 0.56 * (260 - 135) / asc)
    width = max(p[0] for L in fl for lp in L["loops"] for p in lp)
    write("fl", "foot Locker", fl, width, (255, 60, 40), 0.25, "Fredoka Bold glyphs fitted to Steven's photo (make_logos.py)", tex=False)
    ow, oh = 0.86, 0.58
    oval = [[ow * 0.5 + ow * 0.5 * np.cos(2 * np.pi * k / 72), oh * 0.5 + oh * 0.5 * np.sin(2 * np.pi * k / 72)] for k in range(72)]
    write("fl_oval", "oval", [letter("O", [oval])], ow, (0, 0, 0), 0.1, "the logo plaque", top=oh, tex=False)
    fig = cv2.imread(os.path.join(HERE, "src", "fl_figure.png"), 0) > 127
    s_px = ow / 460.0
    cx, cy = 267, 141
    write("fl_fig", "runner", trace_mask(fig, "runner", ow, cy + 154, frame=(cx - 230, s_px), smooth=2.0), ow, (0, 0, 0), 0.1,
          "the runner, traced from the photo", top=oh, tex=False)

    # Foot Locker's white portal, a U round the opening with bevelled top corners (photos): 5.6 m
    # wide, 3.3 m high, the opening 4.8 x 2.95 m; and the diagonal wood
    W5, H5, c5, iw, ih, ic = 5.6, 3.3, 0.55, 0.4, 2.95, 0.45
    U = [(0, 0), (iw, 0), (iw, ih - ic), (iw + ic, ih), (W5 - iw - ic, ih), (W5 - iw, ih - ic), (W5 - iw, 0), (W5, 0),
         (W5, H5 - c5), (W5 - c5, H5), (c5, H5), (0, H5 - c5)]
    write("fl_portal", "portal", [letter("U", [U])], W5, (0, 0, 0), 0.1, "Foot Locker's white portal (photos)", top=H5, tex=False)
    wood_planks(os.path.join(TEX, "fl_wood.png"))

    # The Athlete's Foot (refs/athletes-foot-front.jpg, levelled -2.84 degrees, 6 px per photo
    # pixel): letters, foot and wing traced, in the frame of the sign's yellow border (src/
    # af_frame.txt: left, top, right, bottom px), 2.9 m across.
    L, T, R, B = [int(v) for v in open(os.path.join(HERE, "src", "af_frame.txt")).read().split()]
    fw = 2.9
    s_px = fw / (R - L)
    fh = (B - T) * s_px
    # the words: Fredoka Bold set to each word's box in the photo (the trace was too lumpy)
    words = [("The", (226, 115, 262, 152)), ("Athlete\u2019s", (740, 125, 755, 176)), ("Foot", (1005, 326, 361, 178))]
    write("af_text", "The Athlete's Foot", fit_words(os.path.join(HERE, "src", "Fredoka-Bold.ttf"), words, L, B, s_px), fw, (0, 0, 0), 0.1,
          "Fredoka Bold words fitted to Steven's photo", top=fh, tex=False)
    for part, sm in (("foot", 6.0), ("wing", 5.0)):
        m = cv2.imread(os.path.join(HERE, "src", "af_%s.png" % part), 0) > 127
        shapes = trace_mask(m, "TheAthlete'sFoot" if part == "text" else part, fw, B, frame=(L, s_px), smooth=sm)
        write("af_" + part, part, shapes, fw, (0, 0, 0), 0.1, "traced from Steven's photo", top=fh, tex=False)
    write("af_border", "border", [rect_ring(-0.01, -0.01, fw + 0.01, fh + 0.01, 0.022)], fw, (0, 0, 0), 0.1, "the yellow pinstripe", top=fh, tex=False)


if __name__ == "__main__":
    main()
