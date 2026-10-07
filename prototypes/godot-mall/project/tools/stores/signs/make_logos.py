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


SIMPLIFY = 0.0012     # metres: outline points closer than this to the line are dropped (download size)


def simplify(c):
    if len(c) < 8:
        return c
    a = np.array(c, dtype=np.float32).reshape(-1, 1, 2)
    out = cv2.approxPolyDP(a, SIMPLIFY, True).reshape(-1, 2)
    return [(float(p[0]), float(p[1])) for p in out] if len(out) >= 3 else c


def letter(ch, cons):
    """Contours (metres, y up) -> {ch, tris, loops}: outers counter-clockwise, holes clockwise."""
    cons = [simplify(c) for c in cons]
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


def set_text(font, text, cap_m, track=0.0):
    """text set in the font with its own spacing, capitals cap_m high, baseline y = 0, from x = 0."""
    f = TTFont(font)
    gs = f.getGlyphSet()
    cmap = f.getBestCmap()
    hmtx = f["hmtx"]
    bp = FlatPen(gs)
    gs[cmap[ord("H")]].draw(bp)
    capu = max(p[1] for c in bp.contours for p in c)
    k = cap_m / capu
    out = []
    x = 0.0
    for ch in text:
        g = cmap[ord(ch)]
        if ch != " ":
            pen = FlatPen(gs)
            gs[g].draw(pen)
            out.append(letter(ch, [[((p[0] + x) * k, p[1] * k) for p in c] for c in pen.contours]))
        x += hmtx[g][0] + track / k
    return out, (x - track / k) * k


def circle(r, cx=0.0, cy=0.0, n=96, cw=False):
    pts = [(cx + r * np.cos(2 * np.pi * i / n), cy + r * np.sin(2 * np.pi * i / n)) for i in range(n)]
    return pts[::-1] if cw else pts


def bricks(path, base=(92, 52, 38)):
    """Running-bond brick, 1024 px = 1 m (bricks 20 x 6.7 cm with 1 cm joints), tiling."""
    N = 1024
    img = np.zeros((N, N, 3), np.float32)
    rng = np.random.default_rng(11)
    rows = 15
    rh = N / rows
    for r in range(rows):
        off = 0 if r % 2 == 0 else N / 10
        for c in range(-1, 6):
            x0 = int(c * N / 5 + off)
            y0 = int(r * rh)
            sh = rng.uniform(0.75, 1.15)
            col = np.array([base[2], base[1], base[0]]) * sh
            img[y0 + 5:int(y0 + rh) - 5, max(0, x0 + 5):min(N, x0 + N // 5 - 5)] = col
    joint = np.all(img == 0, axis=2)
    img[joint] = (120, 125, 128)
    noise = cv2.GaussianBlur(rng.normal(0, 1, (N, N)).astype(np.float32), (0, 0), 1.5)
    img = np.clip(img * (1 + noise[..., None] * 0.06), 0, 255).astype(np.uint8)
    cv2.imwrite(path, cv2.resize(img, (512, 512), interpolation=cv2.INTER_AREA))


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


def kb():
    """K&B (Prien Lake Mall photo, refs/kb-prien-lake-mall.png; the logo from refs/kb-logo.jpg):
    the round logo 1.3 m across (purple face, gold rim, a red line inside it, K&B traced from the
    logo photo), and DRUGS / TOBACCO in Francois One (OFL), 0.6 m capitals."""
    D = 1.3
    R = D / 2
    m = cv2.imread(os.path.join(HERE, "src", "kb_letters.png"), 0) > 127
    ys, xs = np.where(m)
    lw = 0.8 * D                                # the letters span 80 % of the disc
    s_px = lw / (xs.max() - xs.min())
    lh = (ys.max() - ys.min()) * s_px
    x0 = xs.min() - (D - lw) / 2 / s_px         # frame: the disc's left edge
    base = ys.max() + (D - lh) / 2 / s_px       # frame: the disc's bottom
    write("kb_letters", "K&B", trace_mask(m, "K&B", D, base, frame=(x0, s_px), smooth=6.0), D, (0, 0, 0), 0.1,
          "K&B traced from Steven's logo photo", top=D, tex=False)
    write("kb_disc", "disc", [letter("O", [circle(R * 0.93, R, R)])], D, (0, 0, 0), 0.1, "the purple face", top=D, tex=False)
    write("kb_rim", "rim", [letter("O", [circle(R, R, R), circle(R * 0.93, R, R, cw=True)])], D, (0, 0, 0), 0.1, "the gold rim", top=D, tex=False)
    write("kb_line", "line", [letter("O", [circle(R * 0.925, R, R), circle(R * 0.905, R, R, cw=True)])], D, (0, 0, 0), 0.1, "the red line", top=D, tex=False)
    for word in ("DRUGS", "TOBACCO"):
        L, w = set_text(os.path.join(HERE, "src", "FrancoisOne-Regular.ttf"), word, 0.6, 0.06)
        write("kb_" + word.lower(), word, L, w, (225, 200, 255), 0.25, "Francois One, read off the Prien Lake photo")
    bricks(os.path.join(TEX, "kb_brick.png"))


def level(m, deg):
    h, w = m.shape
    R = cv2.getRotationMatrix2D((w / 2, h / 2), deg, 1.0)
    return cv2.warpAffine(m.astype(np.uint8) * 255, R, (w, h), flags=cv2.INTER_LINEAR) > 127


def stone_blocks(path, base=(184, 166, 138)):
    """Tan ashlar tile, 1024 px = 1 m: blocks 50 x 25 cm, running bond, thin light joints, tiling."""
    N = 1024
    rng = np.random.default_rng(5)
    img = np.zeros((N, N, 3), np.float32)
    for r in range(4):
        off = 0 if r % 2 == 0 else N // 4
        for c in range(-1, 3):
            sh = rng.uniform(0.88, 1.08)
            x0 = c * N // 2 + off
            img[r * N // 4 + 4:(r + 1) * N // 4 - 4, max(0, x0 + 4):min(N, x0 + N // 2 - 4)] = np.array(base[::-1]) * sh
    joint = np.all(img == 0, axis=2)
    img[joint] = np.array(base[::-1]) * 1.12
    spots = cv2.GaussianBlur(rng.normal(0, 1, (N, N)).astype(np.float32), (0, 0), 6) * 0.05 + cv2.GaussianBlur(rng.normal(0, 1, (N, N)).astype(np.float32), (0, 0), 1) * 0.03
    img = np.clip(img * (1 + spots[..., None]), 0, 255).astype(np.uint8)
    cv2.imwrite(path, cv2.resize(img, (512, 512), interpolation=cv2.INTER_AREA))


def marble(path, base=(92, 78, 70)):
    """Dark brown-grey marble with pale veins, 1024 px = 1 m, tiling (whole-period sines)."""
    N = 1024
    y, x = np.mgrid[0:N, 0:N].astype(np.float32) / N
    rng = np.random.default_rng(9)
    t = np.zeros_like(x)
    for fx, fy, a in ((1, 2, 1.0), (3, 1, 0.6), (2, 5, 0.4), (7, 3, 0.25), (11, 13, 0.12)):
        ph = rng.uniform(0, 6.28)
        t += a * np.sin(2 * np.pi * (fx * x + fy * y) + ph)
    veins = np.exp(-np.abs(np.sin(3 * np.pi * (x + 0.35 * y) + 1.6 * t)) * 16.0)
    cloud = 0.8 + 0.12 * np.sin(2 * np.pi * (2 * x + y) + t) + 0.08 * np.sin(2 * np.pi * (5 * x - 3 * y) + 2 * t)
    v = cloud[..., None] * np.array(base[::-1], np.float32) + veins[..., None] * np.array([150, 160, 170], np.float32) * 0.35
    # tile joints every 50 cm
    j = ((x * 2) % 1 < 0.004) | ((y * 2) % 1 < 0.004)
    v[j] *= 0.6
    cv2.imwrite(path, cv2.resize(np.clip(v, 0, 255).astype(np.uint8), (512, 512), interpolation=cv2.INTER_AREA))


def reveal_panels(path, base=(26, 56, 160)):
    """Blue metal panels with a horizontal reveal every 25 cm (Blockbuster Music's fascia), 1 m tile."""
    N = 512
    img = np.zeros((N, N, 3), np.float32) + np.array(base[::-1], np.float32)
    y = np.arange(N)
    img[(y % (N // 4)) < 5] *= 0.45
    img[(y % (N // 4)) == 5] *= 1.25
    rng = np.random.default_rng(2)
    img *= (1 + cv2.GaussianBlur(rng.normal(0, 1, (N, N)).astype(np.float32), (0, 0), 8)[..., None] * 0.04)
    cv2.imwrite(path, np.clip(img, 0, 255).astype(np.uint8))


def ticket_poly(inset=0.0):
    """Blockbuster's ticket in view units (levelled logo, 0.6 x the 3x crop; y down): a box with a
    round notch on the left and a torn right edge. inset shrinks it all round."""
    i = inset
    x0, y0, y1 = 52 + i, 42 + i, 340 - i
    nc, nr = 190, 45 + i
    torn = [(598, 42), (612, 60), (622, 100), (616, 140), (624, 180), (614, 220), (620, 260), (606, 300), (612, 340)]
    pts = [(x0, y0)]
    pts += [(x - i, y + (i if k == 0 else (-i if k == len(torn) - 1 else 0))) for k, (x, y) in enumerate(torn)]
    pts += [(x0, y1), (x0, nc + nr)]
    for k in range(1, 16):
        a = np.pi / 2 - np.pi * k / 16
        pts.append((52 + nr * np.cos(a), nc + nr * np.sin(a)))
    pts.append((x0, nc - nr))
    return pts


def more():
    """Blockbuster Music, Zales and The Shoe Dept (Steven's photos, Oct 7)."""
    # --- Blockbuster Music (refs/blockbuster-music-logo.jpg): the ticket 2.0 m across, drawn from the
    # levelled logo; BLOCKBUSTER traced; "music" traced, 3.0 m across
    tw = 2.0
    sv = tw / (625 - 52)
    to_m = lambda pts: [((x - 52) * sv, (340 - y) * sv) for (x, y) in pts]
    th = (340 - 42) * sv
    write("bb_ticket_rim", "rim", [letter("T", [to_m(ticket_poly(0))])], tw, (0, 0, 0), 0.1, "the ticket's yellow edge", top=th, tex=False)
    write("bb_ticket_face", "face", [letter("T", [to_m(ticket_poly(10))])], tw, (0, 0, 0), 0.1, "the ticket's blue face", top=th, tex=False)
    fr = [(112, 77), (592, 77), (592, 310), (112, 310)]
    fi = [(117, 82), (117, 305), (587, 305), (587, 82)]
    write("bb_ticket_frame", "frame", [letter("#", [to_m(fr), to_m(fi)])], tw, (0, 0, 0), 0.1, "the thin inner frame", top=th, tex=False)
    m = cv2.imread(os.path.join(HERE, "src", "bb_ticket_text.png"), 0) > 127
    # the mask is in levelled big pixels (view / 0.6): frame x0 = 52 / 0.6, metres per px = sv * 0.6
    write("bb_ticket_text", "BLOCKBUSTER", trace_mask(m, "BLOCKBUSTER", tw, 340 / 0.6, frame=(52 / 0.6, sv * 0.6), smooth=2.5), tw, (0, 0, 0), 0.1,
          "traced from the logo", top=th, tex=False)
    mu = cv2.imread(os.path.join(HERE, "src", "bb_music.png"), 0) > 127
    # the logo's stripes notch the letters' left edges: close each letter vertically
    n, lab = cv2.connectedComponents(mu.astype(np.uint8))
    cl = np.zeros_like(mu)
    for k in range(1, n):
        cl |= cv2.morphologyEx((lab == k).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((41, 9), np.uint8)) > 0
    mu = cl
    ys, xs = np.where(mu)
    write("bb_music", "music", trace_mask(mu, "music", 3.0, ys.max(), smooth=3.0), 3.0, (255, 60, 200), 0.3, "traced from the logo")
    reveal_panels(os.path.join(TEX, "bb_panels.png"))

    # --- Zales (refs/zales-1.jpg): ZALES and JEWELERS traced (levelled 2.9 degrees), ZALES 2.6 m across
    z = level(cv2.imread(os.path.join(HERE, "src", "zl_letters.png"), 0) > 127, -2.9)
    n, lab, st, _ = cv2.connectedComponentsWithStats(z.astype(np.uint8))
    big = np.zeros_like(z); small = np.zeros_like(z)
    for k in range(1, n):
        if st[k][4] < 400 or st[k][3] < 20:
            continue
        (big if st[k][3] > 120 else small).__ior__(lab == k)
    ys, xs = np.where(big)
    s_px = 2.6 / (xs.max() - xs.min())
    x0 = xs.min()
    base = ys.max()
    ys2, xs2 = np.where(small)
    zw = 2.6
    write("zl_name", "ZALES", trace_mask(big, "ZALES", zw, base, frame=(x0, s_px), smooth=2.0), zw, (255, 250, 240), 0.2, "traced from Steven's photo")
    jw = (xs2.max() - xs2.min()) * s_px
    write("zl_sub", "JEWELERS", trace_mask(small, "JEWELERS", jw, ys2.max(), frame=(xs2.min(), s_px), smooth=1.5), jw, (255, 250, 240), 0.15, "traced from Steven's photo")
    stone_blocks(os.path.join(TEX, "zl_stone.png"))

    # --- The Shoe Dept (refs/shoe-dept-*.jpg): SHOE DEPT traced (levelled 2.6 degrees;
    # src/sd_letters.png, cleaned of the marble's veins), 0.62 m capitals; "the" in Kaushan Script (OFL); a square full stop
    sd = level(cv2.imread(os.path.join(HERE, "src", "sd_letters.png"), 0) > 127, 2.6)
    ys, xs = np.where(sd)
    cap = 0.62
    s_px = cap / (np.percentile(ys, 99) - np.percentile(ys, 1))
    base = np.percentile(ys, 99)
    L = trace_mask(sd, "SHOEDEPT", 0, base, frame=(xs.min(), s_px), smooth=2.5)
    sw = (xs.max() - xs.min()) * s_px
    L.append(letter(".", [[(sw + 0.05, 0.0), (sw + 0.15, 0.0), (sw + 0.15, 0.1), (sw + 0.05, 0.1)]]))
    the, tw2 = set_text(os.path.join(HERE, "src", "KaushanScript-Regular.ttf"), "the", 0.42)
    off = tw2 + 0.12
    shifted = [{"ch": Lt["ch"], "tris": [[p[0] + off, p[1]] for p in Lt["tris"]], "loops": [[[p[0] + off, p[1]] for p in lp] for lp in Lt["loops"]]} for Lt in L]
    the = [{"ch": Lt["ch"], "tris": [[p[0], p[1] + 0.22] for p in Lt["tris"]], "loops": [[[p[0], p[1] + 0.22] for p in lp] for lp in Lt["loops"]]} for Lt in the]
    write("sd_name", "the SHOE DEPT.", the + shifted, off + sw + 0.15, (255, 250, 240), 0.25, "SHOE DEPT traced from Steven's photo, 'the' in Kaushan Script")
    marble(os.path.join(TEX, "sd_marble.png"))


def shift(L, dx, dy=0.0, shear=0.0):
    """Move letters by (dx, dy) metres, slanting by shear (x += shear * y)."""
    f = lambda p: [round(p[0] + dx + shear * p[1], 5), round(p[1] + dy, 5)]
    return [{"ch": l["ch"], "tris": [f(p) for p in l["tris"]], "loops": [[f(p) for p in lp] for lp in l["loops"]]} for l in L]


def bbox(L):
    pts = [p for l in L for lp in l["loops"] for p in lp]
    return min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)


def batch3():
    """Payless ShoeSource, Claire's, Gordon's, Rave, 5-7-9, Lady Foot Locker (Steven's photos, Oct 7)."""
    SRC = os.path.join(HERE, "src")
    # --- Payless (photos/payless/01): yellow letters and the two orange O's traced from the photo
    # straightened to the fascia; 6.8 m across
    yl = cv2.imread(os.path.join(SRC, "pay_yellow.png"), 0) > 127
    og = cv2.imread(os.path.join(SRC, "pay_orange.png"), 0) > 127
    ys, xs = np.where(yl | og)
    pw = 9.0
    s_px = pw / (xs.max() - xs.min())
    fr = (xs.min(), s_px)
    base = ys.max()
    write("pay_name", "Payless ShoeSource", trace_mask(yl, "PaylessShoeSurce", pw, base, frame=fr, smooth=3.0), pw, (255, 210, 40), 0.3, "traced from Steven's photo")
    write("pay_dots", "oo", trace_mask(og, "oo", pw, base, frame=fr, smooth=3.0), pw, (255, 120, 30), 0.2, "the orange O's, traced", top=(base - ys.min()) * s_px)

    # --- Claire's (photos/claires/01): "Claire's" in a compressed Bodoni (Bodoni Moda Bold, OFL)
    # stretched to the photo's word box; ACCESSORIES in Josefin Sans (OFL), spaced
    nm = cv2.imread(os.path.join(SRC, "cla_name.png"), 0) > 127
    ys, xs = np.where(nm)
    cw = 1.5
    s_px = cw / (xs.max() - xs.min())
    name = fit_words(os.path.join(SRC, "BodoniModa-Bold.ttf"), [("Claire\u2019s", (xs.min(), ys.min(), xs.max() - xs.min(), ys.max() - ys.min()))], xs.min(), ys.max(), s_px)
    write("cla_name", "Claire's", name, cw, (255, 40, 50), 0.25, "Bodoni Moda fitted to Steven's photo")
    acc, aw = set_text(os.path.join(SRC, "JosefinSans-Regular.ttf"), "ACCESSORIES", 0.15, 0.07)
    write("cla_acc", "ACCESSORIES", acc, aw, (255, 40, 50), 0.15, "Josefin Sans, spaced")

    # --- Gordon's (photos/gordons/02, 04): "Gordon's" in Old Standard Bold (OFL), JEWELERS spaced
    gd, gw = set_text(os.path.join(SRC, "OldStandard-Bold.ttf"), "Gordon\u2019s", 0.42)
    write("gor_name", "Gordon's", gd, gw, (0, 0, 0), 0.1, "Old Standard Bold (the photos' serif)", tex=False)
    gj, jw = set_text(os.path.join(SRC, "OldStandard-Bold.ttf"), "JEWELERS", 0.1, 0.1)
    write("gor_sub", "JEWELERS", gj, jw, (0, 0, 0), 0.1, "Old Standard Bold, spaced", tex=False)

    # --- Rave (photos/rave/01, 02): RAVE in Poppins Black (OFL), slanted 14 degrees, 2.5 m across
    rv, rw = set_text(os.path.join(SRC, "Poppins-Black.ttf"), "RAVE", 0.62, -0.02)
    rv = shift(rv, 0.0, 0.0, np.tan(np.radians(14)))
    x0, y0, x1, y1 = bbox(rv)
    k = 2.5 / (x1 - x0)
    rv = [{"ch": l["ch"], "tris": [[(p[0] - x0) * k, p[1] * k] for p in l["tris"]], "loops": [[[(p[0] - x0) * k, p[1] * k] for p in lp] for lp in l["loops"]]} for l in rv]
    write("rave_name", "RAVE", rv, 2.5, (255, 110, 190), 0.25, "Poppins Black slanted, after Steven's photos")

    # --- 5-7-9 (photos/579/02): the burgundy oval ring on a silver plate, "5.7.9" in Kaushan Script
    # (OFL; the photo's brushy italic digits) with round dots
    ow, oh = 2.2, 0.92
    ring = [letter("O", [[(ow / 2 + ow / 2 * np.cos(a), oh / 2 + oh / 2 * np.sin(a)) for a in np.linspace(0, 2 * np.pi, 96, endpoint=False)],
                         [(ow / 2 + (ow / 2 - 0.09) * np.cos(a), oh / 2 + (oh / 2 - 0.09) * np.sin(a)) for a in np.linspace(2 * np.pi, 0, 96, endpoint=False)]])]
    write("s579_ring", "ring", ring, ow, (0, 0, 0), 0.1, "the oval ring", top=oh, tex=False)
    plate = [letter("O", [[(ow / 2 + (ow / 2 - 0.08) * np.cos(a), oh / 2 + (oh / 2 - 0.08) * np.sin(a)) for a in np.linspace(0, 2 * np.pi, 96, endpoint=False)]])]
    write("s579_plate", "plate", plate, ow, (0, 0, 0), 0.1, "the silver plate", top=oh, tex=False)
    dg = []
    x = 0.0
    for ch in "579":
        L, w = set_text(os.path.join(SRC, "KaushanScript-Regular.ttf"), ch, 0.62)
        bx = bbox(L)
        dg += shift(L, x - bx[0], 0.0)
        x += (bx[2] - bx[0]) + 0.26
        if ch != "9":
            dg.append(letter(".", [circle(0.055, x - 0.13, 0.07)]))
    bx = bbox(dg)
    dg = shift(dg, (ow - (bx[2] - bx[0])) / 2 - bx[0], (oh - (bx[3] - bx[1])) / 2 - bx[1])
    write("s579_digits", "5.7.9", dg, ow, (0, 0, 0), 0.1, "Kaushan Script digits", top=oh, tex=False)

    # --- Lady Foot Locker (photos/lady-foot-locker/01): rounded green letters, Fredoka Bold (OFL)
    lf, lw = set_text(os.path.join(SRC, "Fredoka-Bold.ttf"), "Lady Foot Locker", 0.42, 0.01)
    write("lfl_name", "Lady Foot Locker", lf, lw, (60, 220, 80), 0.2, "Fredoka Bold (the photo's rounded letters)")


def star(cx, cy, ro, ri, rot=90.0):
    return [(cx + (ro if k % 2 == 0 else ri) * np.cos(np.radians(rot + 36 * k)), cy + (ro if k % 2 == 0 else ri) * np.sin(np.radians(rot + 36 * k))) for k in range(10)]


def ellipse(cx, cy, rx, ry, n=72, cw=False):
    pts = [(cx + rx * np.cos(2 * np.pi * i / n), cy + ry * np.sin(2 * np.pi * i / n)) for i in range(n)]
    return pts[::-1] if cw else pts


def bulbs(path, w_m, h_m, pitch=0.075):
    """A marquee's field of bulbs: warm white dots on near-black, w_m x h_m metres, 400 px per metre."""
    k = 400
    W, H = int(w_m * k), int(h_m * k)
    img = np.zeros((H, W, 3), np.float32) + 6
    r = pitch * k * 0.26
    for y in np.arange(pitch * k / 2, H, pitch * k):
        for x in np.arange(pitch * k / 2, W, pitch * k):
            cv2.circle(img, (int(x), int(y)), int(r) + 2, (60, 90, 110), -1, cv2.LINE_AA)
            cv2.circle(img, (int(x), int(y)), int(r), (170, 215, 245), -1, cv2.LINE_AA)
    img = img + cv2.GaussianBlur(img, (0, 0), r * 0.8) * 0.25
    cv2.imwrite(path, np.clip(img, 0, 255).astype(np.uint8))


def dot_matrix(path_json, text, font, cols=52, rows=15, top=2, height=11, side=1):
    """A scoreboard field: cols x rows round lamps; the lamps under the letters are red, the rest
    white. The text is rendered large, fitted to `height` rows from row `top` with `side` columns
    of margin, and sampled per cell (a lamp is red when over half its cell is letter)."""
    from PIL import Image, ImageDraw, ImageFont
    ft = ImageFont.truetype(font, 400)
    im = Image.new("L", (4000, 700), 0)
    ImageDraw.Draw(im).text((20, 20), text, font=ft, fill=255)
    a = np.array(im) > 127
    ys, xs = np.where(a)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.float32)
    W = cols - 2 * side
    cell = cv2.resize(a, (W * 8, height * 8), interpolation=cv2.INTER_AREA)
    cell = cell.reshape(height, 8, W, 8).mean(axis=(1, 3))
    red = np.zeros((rows, cols), bool)
    red[top:top + height, side:side + W] = cell > 0.45
    json.dump({"cols": cols, "rows": rows, "red": ["".join("1" if red[r, c] else "0" for c in range(cols)) for r in range(rows)]}, open(path_json, "w"))
    return red


def batch4():
    """Coach House Gifts, Footaction USA, Champs Sports, Sports Avenue (Steven's photos, Oct 7)."""
    SRC = os.path.join(HERE, "src")
    # --- Coach House: COACH HOUSE GIFTS on one line (photos/coach-house/02, the exact lettering),
    # Source Sans 3 Bold (OFL), 0.25 m capitals; the hood over the door: 4.2 x 1.0 m, the top
    # bowed up 0.24 m (photos/coach-house/01)
    L, w = set_text(os.path.join(SRC, "SourceSans3-Bold.ttf"), "COACH HOUSE GIFTS", 0.25, 0.02)
    write("ch_name", "COACH HOUSE GIFTS", L, w, (255, 250, 235), 0.2, "Source Sans 3 Bold, after Steven's photo")
    hw, hh, bow = 4.2, 1.0, 0.24
    top = [(hw * i / 24, hh + bow * np.sin(np.pi * i / 24)) for i in range(24, -1, -1)]
    write("ch_hood", "hood", [letter("H", [[(0, 0), (hw, 0)] + top])], hw, (0, 0, 0), 0.1, "the arched hood", top=hh + bow, tex=False)
    cap = [(-0.06 + (hw + 0.12) * i / 24, hh + 0.02 + (bow + 0.02) * np.sin(np.pi * i / 24)) for i in range(25)]
    cap2 = [(x, y + 0.09) for (x, y) in cap][::-1]
    write("ch_cornice", "cornice", [letter("H", [cap + cap2])], hw, (0, 0, 0), 0.1, "the cornice along the arch", top=hh + bow, tex=False)

    # --- Footaction USA (photos/footaction): FOOTACTION in Krona One (OFL) stretched wide and heavy
    # as on the sign, 0.42 m capitals; the bar under it, USA small; the star (blue outline,
    # white inner line)
    L, w = set_text(os.path.join(SRC, "KronaOne-Regular.ttf"), "FOOTACTION", 0.42, 0.0)
    x0, y0, x1, y1 = bbox(L)
    k = 4.2 / (x1 - x0)
    L = [{"ch": l["ch"], "tris": [[(p[0] - x0) * k, p[1]] for p in l["tris"]], "loops": [[[(p[0] - x0) * k, p[1]] for p in lp] for lp in l["loops"]]} for l in L]
    bar = letter("-", [[(0.35, -0.14), (3.3, -0.14), (3.3, -0.09), (0.35, -0.09)]])
    U, uw = set_text(os.path.join(SRC, "KronaOne-Regular.ttf"), "USA", 0.11, 0.03)
    U = shift(U, 3.35, -0.2)
    L = shift(L + [bar] + U, 0.0, 0.2)
    write("fa_name", "FOOTACTION USA", L, 4.2, (240, 250, 255), 0.25, "Krona One stretched, after Steven's photos")
    so, si = 0.62, 0.25
    write("fa_star", "star", [letter("*", [star(so, so, so, si), star(so, so, so - 0.07, si - 0.03)[::-1]])], 2 * so, (40, 140, 255), 0.25, "the star's blue outline", top=2 * so)
    write("fa_star_in", "star", [letter("*", [star(so, so, so - 0.11, si - 0.045), star(so, so, so - 0.135, si - 0.055)[::-1]])], 2 * so, (0, 0, 0), 0.1, "the star's white inner line", top=2 * so, tex=False)

    # --- Champs Sports (photos/champs-sports/03, 04: the blue badge): the badge 3.6 x 1.3 m, the top
    # bowed, a lobe below for SPORTS; CHAMPS in Old Standard Bold (OFL) widened, the end letters
    # taller as on the sign; SPORTS spaced in a red-lined oval
    bw, bh = 3.6, 1.05
    tp = [(bw * i / 24, bh + 0.12 * np.sin(np.pi * i / 24)) for i in range(24, -1, -1)]
    lobe = [(1.8 + 1.0 * np.cos(np.pi + np.pi * i / 20), 0.22 - 0.22 * np.sin(np.pi * i / 20)) for i in range(21)]
    badge = [(0.0, 0.22)] + lobe + [(bw, 0.22)] + tp
    def grow(poly, d):
        c = np.mean(poly, axis=0)
        return [(c[0] + (x - c[0]) * (1 + d / (bw / 2)), c[1] + (y - c[1]) * (1 + d / (bh / 2))) for (x, y) in poly]
    write("cs_badge", "badge", [letter("B", [badge])], bw, (0, 0, 0), 0.1, "the blue badge", top=bh + 0.12, tex=False)
    rim = grow(badge, 0.06)
    x0 = min(p[0] for p in rim)
    y0 = min(p[1] for p in rim)
    write("cs_rim", "rim", [letter("B", [[(x - x0 - 0.06 * 0 + 0.0, y - y0 + 0.0) for (x, y) in rim]])], bw, (0, 0, 0), 0.1, "the red edge", top=bh + 0.12, tex=False)
    L, w = set_text(os.path.join(SRC, "OldStandard-Bold.ttf"), "CHAMPS", 0.5, 0.02)
    x0, y0, x1, y1 = bbox(L)
    sx = 3.1 / (x1 - x0)
    out = []
    for l in L:
        lx = np.mean([p[0] for lp in l["loops"] for p in lp])
        tt = ((lx - x0) / (x1 - x0)) * 2 - 1
        sy = 1.0 + 0.22 * tt * tt
        f = lambda p: [round((p[0] - x0) * sx + 0.25, 5), round(0.62 + (p[1] - 0.25) * sy, 5)]
        out.append({"ch": l["ch"], "tris": [f(p) for p in l["tris"]], "loops": [[f(p) for p in lp] for lp in l["loops"]]})
    write("cs_name", "CHAMPS", out, bw, (255, 245, 230), 0.15, "Old Standard Bold, widened, ends taller", top=bh + 0.12)
    S2, sw = set_text(os.path.join(SRC, "OldStandard-Bold.ttf"), "SPORTS", 0.1, 0.12)
    S2 = shift(S2, 1.8 - sw / 2, 0.12)
    ring = letter("O", [ellipse(1.8, 0.2, 0.92, 0.17), ellipse(1.8, 0.2, 0.89, 0.145, cw=True)])
    write("cs_sub", "SPORTS", S2 + [ring], bw, (0, 0, 0), 0.1, "SPORTS in the red-lined oval", top=bh + 0.12, tex=False)

    # --- Sports Avenue (photos/sports-avenue): the marquee field of bulbs 3.0 x 0.95 m, SPORTS in
    # red (Francois One, OFL) over it, gold stars at the corners
    red = dot_matrix(os.path.join(HERE, "sa_dots.json"), "SPORTS", os.path.join(SRC, "FrancoisOne-Regular.ttf"))
    print("\n".join("".join("#" if v else "." for v in r) for r in red))
    # the gold frame: a trapezoid (wider at the top, as in the photos) round the 3.1 x 0.95 m field
    fw_b, fw_t, fh = 3.45, 3.75, 1.3
    outer = [((fw_t - fw_b) / 2, 0.0), ((fw_t + fw_b) / 2, 0.0), (fw_t, fh), (0.0, fh)]
    hole = [((fw_t - 3.1) / 2, (fh - 0.95) / 2), ((fw_t - 3.1) / 2, (fh + 0.95) / 2), ((fw_t + 3.1) / 2, (fh + 0.95) / 2), ((fw_t + 3.1) / 2, (fh - 0.95) / 2)]
    write("sa_frame", "frame", [letter("F", [outer, hole])], fw_t, (0, 0, 0), 0.1, "the marquee's gold frame", top=fh, tex=False)
    L, w = set_text(os.path.join(SRC, "FrancoisOne-Regular.ttf"), "SPORTS", 0.66, 0.04)
    x0, y0, x1, y1 = bbox(L)
    k = 2.6 / (x1 - x0)
    L = [{"ch": l["ch"], "tris": [[(p[0] - x0) * k, p[1] * 1.0] for p in l["tris"]], "loops": [[[(p[0] - x0) * k, p[1] * 1.0] for p in lp] for lp in l["loops"]]} for l in L]
    write("sa_name", "SPORTS", L, 2.6, (255, 60, 40), 0.15, "Francois One, after Steven's photos")
    write("sa_star", "star", [letter("*", [star(0.11, 0.11, 0.11, 0.045)])], 0.22, (0, 0, 0), 0.1, "a corner star", top=0.22, tex=False)


def batch5():
    """Demo 16 (Steven, Oct 7): Cucos, Great American Cookie Co., Foot Locker's backlight."""
    SRC = os.path.join(HERE, "src")
    # --- Cucos (Steven's two photos: the lit flat sign at night, the neon script on the street
    # front): the script traced from the night photo (src/cucos_mask.png, 8 px per photo pixel;
    # the small c and o redrawn where the photo is too soft), neon tubes run along
    # its outline (apparel/kit.gd neon); 2.7 m across on the 1.7 m parapet. MEXICAN CAFE in Source Sans 3 Bold (OFL) on the blue band.
    m = cv2.imread(os.path.join(SRC, "cucos_mask.png"), 0) > 127
    ys, xs = np.where(m)
    write("cu_name", "Cucos", trace_mask(m, "Cucos", 2.7, ys.max(), smooth=2.0), 2.7, (255, 90, 50), 0.3,
          "traced from Steven's night photo of the Cucos sign")
    L, w = set_text(os.path.join(SRC, "SourceSans3-Bold.ttf"), "MEXICAN CAFE", 0.17, 0.04)
    write("cu_sub", "MEXICAN CAFE", L, w, (240, 245, 255), 0.15, "Source Sans 3 Bold, spaced, after Steven's photo")
    # --- Great American Cookie Co. (Steven's photo of a mall store): "Great American" in red neon
    # script, Kaushan Script (OFL, the photo's brush script), over COOKIE CO. in white lit
    # capitals, Poppins Black (OFL, the photo's heavy geometric sans)
    L, w = set_text(os.path.join(SRC, "KaushanScript-Regular.ttf"), "Great American", 0.36, 0.0)
    x0, y0, x1, y1 = bbox(L)
    k = 3.4 / (x1 - x0)
    L = [{"ch": l["ch"], "tris": [[(p[0] - x0) * k, (p[1] - y0) * k] for p in l["tris"]], "loops": [[[(p[0] - x0) * k, (p[1] - y0) * k] for p in lp] for lp in l["loops"]]} for l in L]
    write("gac_script", "Great American", L, 3.4, (255, 50, 40), 0.25, "Kaushan Script, after Steven's photo")
    L, w = set_text(os.path.join(SRC, "Poppins-Black.ttf"), "COOKIE CO.", 0.42, 0.03)
    write("gac_name", "COOKIE CO.", L, w, (255, 250, 240), 0.2, "Poppins Black, after Steven's photo")
    # --- Foot Locker: a soft halo behind the red letters (the letters themselves are main()'s)
    J = json.load(open(os.path.join(HERE, "fl_logo.json")))
    textures("fl", J["letters"], J["width"], J["cap_h"], (255, 70, 50), 0.22)
    print("fl: halo")


if __name__ == "__main__":
    main()
    kb()
    more()
    batch3()
    batch4()
    batch5()
