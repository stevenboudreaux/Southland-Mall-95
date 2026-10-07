"""The Cucos sign (Steven, Oct 7 2026): an open-face neon channel sign, traced from his photos.

Sources: his close-up of the street sign from below-left (1100 px) and his square-on photo of the
same sign. The close-up was registered to the square-on photo (a homography found by aligning the
two red masks), then levelled on the blue bar: src/cucos_front.jpg. From that view:
  src/cucos_cans.png   the letter openings (red interior, shadowed inner walls and tubes included),
                       cut where u, c and o touch each other and the S: they are cans of their own
This script writes cu_sign.json for cucos_sign.gd: per can its outline loops and back-pan
triangles; the tube runs (a run 30 mm inside the walls, a centre run where the stroke is wide or
too narrow for two); MEXICAN CAFE (Old Standard Bold, OFL) as plates with a single tube each.
Units: metres, x right, y up, origin at the middle of the bar's bottom edge.

  python3 tools/stores/signs/make_cucos.py   (opencv, scipy, scikit-image, mapbox_earcut, pillow)
"""
import json, os, sys
import cv2
import numpy as np
from scipy import interpolate
from skimage.morphology import skeletonize
import mapbox_earcut as earcut
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
LOGO_W = 1.80            # metres: the script's width in the mall (the parapet is 1.62 m clear)
BAR_W_K = 1.29           # the bar's width over the script's (photo)
BAR_H_K = 0.138          # the bar face's height over the script's width
GAP_K = 0.042            # gap between the script's lowest point and the bar
D1 = 19.0                # px: the outline tube run's inset from the can wall (30 mm)
DC = 40.0                # px: strokes wider than twice this get a centre run too


def spline_closed(c, step, smooth):
    c = np.asarray(c, dtype=np.float64)
    if len(c) < 12:
        return c
    sub = c[::3]
    try:
        tck, _ = interpolate.splprep([sub[:, 0], sub[:, 1]], s=len(sub) * smooth, per=True)
    except Exception:
        return c
    per = np.sum(np.linalg.norm(np.diff(np.vstack([c, c[:1]]), axis=0), axis=1))
    n = max(12, int(per / step))
    u = np.linspace(0, 1, n, endpoint=False)
    x, y = interpolate.splev(u, tck)
    return np.stack([x, y], 1)


def spline_open(c, step, smooth):
    c = np.asarray(c, dtype=np.float64)
    if len(c) < 8:
        return c
    sub = c[::2]
    try:
        tck, _ = interpolate.splprep([sub[:, 0], sub[:, 1]], s=len(sub) * smooth)
    except Exception:
        return c
    ln = np.sum(np.linalg.norm(np.diff(c, axis=0), axis=1))
    n = max(4, int(ln / step))
    x, y = interpolate.splev(np.linspace(0, 1, n), tck)
    return np.stack([x, y], 1)


def area(c):
    x, y = c[:, 0], c[:, 1]
    return 0.5 * float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


def simp(c, eps, closed):
    a = np.asarray(c, dtype=np.float32).reshape(-1, 1, 2)
    return cv2.approxPolyDP(a, eps, closed).reshape(-1, 2).astype(np.float64)


def trace_paths(sk):
    """Simple pixel paths of a skeleton: junction pixels removed, each piece walked end to end."""
    sk = sk.astype(np.uint8)
    nb = cv2.filter2D(sk, -1, np.ones((3, 3), np.float32)) - sk
    sk2 = ((sk > 0) & (nb <= 2)).astype(np.uint8)
    n, lab = cv2.connectedComponents(sk2, connectivity=8)
    out = []
    for i in range(1, n):
        ys, xs = np.nonzero(lab == i)
        if len(xs) < 6:
            continue
        pts = set(zip(xs.tolist(), ys.tolist()))
        deg = {p: sum(((p[0] + dx, p[1] + dy) in pts) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy) for p in pts}
        ends = [p for p in pts if deg[p] <= 1]
        cur = ends[0] if ends else next(iter(pts))
        path = [cur]; seen = {cur}
        while True:
            nxt = None
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                q = (cur[0] + dx, cur[1] + dy)
                if q in pts and q not in seen:
                    nxt = q; break
            if nxt is None:
                break
            path.append(nxt); seen.add(nxt); cur = nxt
        out.append(np.array(path, dtype=np.float64))
    return out


def polys(mask, step, smooth, min_hole=150):
    """[(outer, [holes])] of a mask, splined; outer counter-clockwise, holes clockwise (y up later)."""
    cs, hier = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    res = []
    if hier is None:
        return res
    hier = hier[0]
    for i, c in enumerate(cs):
        if hier[i][3] != -1 or cv2.contourArea(c) < 400:
            continue
        outer = spline_closed(c.reshape(-1, 2), step, smooth)
        holes = []
        j = hier[i][2]
        while j != -1:
            if cv2.contourArea(cs[j]) >= min_hole:
                holes.append(spline_closed(cs[j].reshape(-1, 2), step, smooth))
            j = hier[j][0]
        res.append((outer, holes))
    return res


def tri(outer, holes):
    rings = [outer] + holes
    v = np.vstack(rings).astype(np.float32)
    ends = np.cumsum([len(r) for r in rings]).astype(np.uint32)
    idx = earcut.triangulate_float32(v, ends)
    return v[idx].tolist()


def main():
    full = cv2.imread(os.path.join(SRC, "cucos_cans.png"), 0)
    ys, xs = np.nonzero(full)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    S = LOGO_W / float(x1 - x0)                       # metres per pixel
    bar_h = BAR_H_K * LOGO_W
    cx = (x0 + x1) * 0.5 - 27.0                       # photo: the script sits 27 px right of the bar's middle
    ybase = y1 + GAP_K * (x1 - x0) + bar_h / S        # pixel row of the bar's bottom edge
    M = lambda p: [round((float(p[0]) - cx) * S, 4), round((ybase - float(p[1])) * S, 4)]

    # the cans: the big C-swash-S, and u, c, o on their own (cut apart in the mask where they touch)
    n, lab, st, _ = cv2.connectedComponentsWithStats(full, 8)
    regs = [(lab == i).astype(np.uint8) * 255 for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 3000]
    cans, tubes = [], []
    for R in regs:
        R = (cv2.GaussianBlur(R, (0, 0), 2.5) > 127).astype(np.uint8) * 255
        nn, ll, ss, _ = cv2.connectedComponentsWithStats(R, 8)
        keep = np.zeros_like(R)
        for i in range(1, nn):
            if ss[i, cv2.CC_STAT_AREA] > 3000:
                keep[ll == i] = 255
        R = keep
        for outer, holes in polys(R, 5.0, 5.0):
            o = np.array([M(p) for p in outer]); hs = [np.array([M(p) for p in h]) for h in holes]
            o = simp(o, 0.0009, True); hs = [simp(h, 0.0009, True) for h in hs]
            if area(o) < 0:
                o = o[::-1]
            hs = [h[::-1] if area(h) > 0 else h for h in hs]
            cans.append({"loops": [o.round(4).tolist()] + [h.round(4).tolist() for h in hs], "tris": [[round(a, 4), round(b, 4)] for a, b in tri(o, hs)]})
        dt = cv2.distanceTransform(R, cv2.DIST_L2, 5)
        # the run inside the walls
        ring = (dt >= D1).astype(np.uint8) * 255
        cs, _ = cv2.findContours(ring, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        for c in cs:
            c = c.reshape(-1, 2)
            if len(c) < 70:
                continue
            p = spline_closed(c, 6.0, 1.5)
            p = simp(np.array([M(q) for q in p]), 0.0007, True)
            tubes.append({"closed": True, "pts": p.round(4).tolist()})
        # centre runs: where the stroke is too narrow for two, and a third where it is wide
        sk = skeletonize(R > 0)
        for sel in (sk & (dt < D1 + 1.0) & (dt > 6.0), sk & (dt > DC)):
            for path in trace_paths(sel):
                if len(path) < 45:
                    continue
                p = spline_open(path, 6.0, 2.0)
                p = simp(np.array([M(q) for q in p]), 0.0007, False)
                if len(p) >= 2:
                    tubes.append({"closed": False, "pts": p.round(4).tolist()})

    # MEXICAN CAFE: plates and a single tube per stroke
    bar_w = BAR_W_K * LOGO_W
    cap_px = 240
    font = ImageFont.truetype(os.path.join(SRC, "OldStandard-Bold.ttf"), int(cap_px / 0.70))
    track = int(cap_px * 0.10)
    x = 40; im = Image.new("L", (cap_px * 14, int(cap_px * 2.2)), 0); d = ImageDraw.Draw(im)
    base = int(cap_px * 1.7)
    for ch in "MEXICAN CAFE":
        if ch == " ":
            x += int(cap_px * 0.42); continue
        d.text((x, base), ch, font=font, fill=255, anchor="ls")
        x += int(d.textlength(ch, font=font)) + track
    tm = (np.array(im) > 127).astype(np.uint8) * 255
    tm = cv2.dilate(tm, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13)))   # the sign's letters are heavier
    tm = (cv2.GaussianBlur(tm, (0, 0), 2.0) > 127).astype(np.uint8) * 255
    tys, txs = np.nonzero(tm)
    tx0, tx1, ty0, ty1 = txs.min(), txs.max(), tys.min(), tys.max()
    text_w = 0.705 * bar_w                               # photo: the words span 18% to 89% of the bar
    ts = text_w / float(tx1 - tx0)
    text_cx = (0.181 + 0.892) * 0.5 * bar_w - bar_w * 0.5
    cap_h = (ty1 - ty0) * ts
    ty_mid = bar_h * 0.5
    T = lambda p: [round((float(p[0]) - (tx0 + tx1) * 0.5) * ts + text_cx, 4), round(((ty0 + ty1) * 0.5 - float(p[1])) * ts + ty_mid, 4)]
    plates, wtubes = [], []
    cs, hier = cv2.findContours(tm, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    hier = hier[0]
    for i, c in enumerate(cs):
        if hier[i][3] != -1:
            continue
        o = simp(np.array([T(p) for p in c.reshape(-1, 2)]), 0.0005, True)
        hs = []
        j = hier[i][2]
        while j != -1:
            hs.append(simp(np.array([T(p) for p in cs[j].reshape(-1, 2)]), 0.0005, True)); j = hier[j][0]
        if area(o) < 0:
            o = o[::-1]
        hs = [h[::-1] if area(h) > 0 else h for h in hs]
        plates.append({"loops": [o.round(4).tolist()] + [h.round(4).tolist() for h in hs], "tris": [[round(a, 4), round(b, 4)] for a, b in tri(o, hs)]})
    tdt = cv2.distanceTransform(tm, cv2.DIST_L2, 5)
    tsk = skeletonize(tm > 0) & (tdt > 9.0)
    for path in trace_paths(tsk):
        if len(path) < 62:      # the main strokes only: serif stubs carry no tube
            continue
        p = spline_open(path, 8.0, 1.0)
        p = simp(np.array([T(q) for q in p]), 0.0006, False)
        if len(p) >= 2:
            wtubes.append({"closed": False, "pts": p.round(4).tolist()})

    lo = min(min(q[1] for q in c["loops"][0]) for c in cans)
    hi = max(max(q[1] for q in c["loops"][0]) for c in cans)
    J = {"logo_w": LOGO_W, "bar_w": round(bar_w, 4), "bar_h": round(bar_h, 4), "logo_y0": round(lo, 4), "logo_y1": round(hi, 4),
         "cap_h": round(cap_h, 4), "cans": cans, "tubes": tubes, "plates": plates, "wtubes": wtubes}
    json.dump(J, open(os.path.join(HERE, "cu_sign.json"), "w"), separators=(",", ":"))
    seg = sum(len(t["pts"]) for t in tubes); wseg = sum(len(t["pts"]) for t in wtubes)
    print("cans", len(cans), "loops", sum(len(c["loops"]) for c in cans), "pts", sum(len(l) for c in cans for l in c["loops"]),
          "tris", sum(len(c["tris"]) // 3 for c in cans), "tubes", len(tubes), "tube pts", seg, "plates", len(plates), "wtubes", len(wtubes), wseg,
          "total h", round(hi, 3), "cap", round(cap_h, 3), "size kB", os.path.getsize(os.path.join(HERE, "cu_sign.json")) // 1024)

    # a check drawing
    sc = 700.0
    W = int(bar_w * sc) + 80; Hh = int(hi * sc) + 80
    cv = np.full((Hh, W, 3), 40, np.uint8)
    P = lambda q: (int(W / 2 + q[0] * sc), int(Hh - 40 - q[1] * sc))
    for c in cans:
        t = c["tris"]
        for i in range(0, len(t), 3):
            cv2.fillPoly(cv, [np.array([P(t[i]), P(t[i + 1]), P(t[i + 2])], np.int32)], (40, 40, 150))
        for l in c["loops"]:
            cv2.polylines(cv, [np.array([P(q) for q in l], np.int32)], True, (0, 0, 0), 2)
    for t in tubes:
        cv2.polylines(cv, [np.array([P(q) for q in t["pts"]], np.int32)], t["closed"], (190, 210, 255), 2)
    cv2.rectangle(cv, P((-bar_w / 2, bar_h)), P((bar_w / 2, 0)), (170, 90, 80), -1)
    for c in plates:
        t = c["tris"]
        for i in range(0, len(t), 3):
            cv2.fillPoly(cv, [np.array([P(t[i]), P(t[i + 1]), P(t[i + 2])], np.int32)], (235, 235, 235))
    for t in wtubes:
        cv2.polylines(cv, [np.array([P(q) for q in t["pts"]], np.int32)], False, (255, 160, 60), 2)
    if len(sys.argv) > 1:          # a flat check drawing: make_cucos.py <out.png>
        cv2.imwrite(sys.argv[1], cv)


if __name__ == "__main__":
    main()
