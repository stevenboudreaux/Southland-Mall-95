"""The Karmelkorn sign (Steven, Oct 7 2026): an open-face neon channel sign, from his photos.

Sources: his square-on night photo of a Karmelkorn sign (a mall unit, 582 px) and a close-up of
another (377 px), both lit. The square-on photo, cropped and enlarged 4x, is src/kk_front.jpg.
Too small and too soft to trace each letter, so:
  - the swash K (stem, the arm up to its top bar, the leg) and the swash under the A are traced
    from the photo; the K's stem is Coustard Black's I fitted to it;
  - A R M E L K O R N are Coustard Black (OFL), thinned a little (3 px of the 4x photo), each fitted by correlation into
    its own box read off the photo (the gaps between letters), so size and spacing are the photo's.
  src/kk_cans.png    the letter cans (11): K, the swash, and the nine capitals; 3x kk_front.jpg
The neon is an outline: one run 30 mm inside the can walls (photo: two lines in every heavy
stroke), a single centre run where the stroke is too narrow for two (the hairlines).
This script writes kk_sign.json for kk_sign.gd. Units: metres, x right, y up, origin at the
middle of the sign's bottom edge.

  python3 tools/stores/signs/make_kk.py [check.png]   (opencv, scipy, scikit-image, mapbox_earcut)
"""
import json, os, sys
import cv2
import numpy as np
from scipy import interpolate
from skimage.morphology import skeletonize
import mapbox_earcut as earcut

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
LOGO_W = 6.00            # metres: K's stem to N's right serif (the bulkhead is 1.9 m tall: caps 0.42 m)
D1 = 24.0                # px (1.08 mm each): the outline run's inset from the can wall (26 mm)
MIN_CENTRE = 70          # px: shorter centre runs are serif stubs, which carry no tube


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
    full = cv2.imread(os.path.join(SRC, "kk_cans.png"), 0)
    ys, xs = np.nonzero(full)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    S = LOGO_W / float(x1 - x0)                       # metres per pixel
    cx = (x0 + x1) * 0.5
    M = lambda p: [round((float(p[0]) - cx) * S, 4), round((y1 - float(p[1])) * S, 4)]
    n, lab, st, _ = cv2.connectedComponentsWithStats(full, 8)
    regs = [(lab == i).astype(np.uint8) * 255 for i in range(1, n) if st[i, cv2.CC_STAT_AREA] > 3000]
    cans, tubes = [], []
    for R in regs:
        for outer, holes in polys(R, 5.0, 5.0):
            o = np.array([M(p) for p in outer]); hs = [np.array([M(p) for p in h]) for h in holes]
            o = simp(o, 0.0009, True); hs = [simp(h, 0.0009, True) for h in hs]
            if area(o) < 0:
                o = o[::-1]
            hs = [h[::-1] if area(h) > 0 else h for h in hs]
            cans.append({"loops": [o.round(4).tolist()] + [h.round(4).tolist() for h in hs], "tris": [[round(a, 4), round(b, 4)] for a, b in tri(o, hs)]})
        dt = cv2.distanceTransform(R, cv2.DIST_L2, 5)
        ring = (dt >= D1).astype(np.uint8) * 255
        cs, _ = cv2.findContours(ring, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        for c in cs:
            c = c.reshape(-1, 2)
            if len(c) < 70:
                continue
            p = spline_closed(c, 6.0, 1.5)
            p = simp(np.array([M(q) for q in p]), 0.0007, True)
            tubes.append({"closed": True, "pts": p.round(4).tolist()})
        sk = skeletonize(R > 0)
        for path in trace_paths(sk & (dt < D1 + 1.0) & (dt > 6.0)):
            if len(path) < MIN_CENTRE:
                continue
            p = spline_open(path, 6.0, 2.0)
            p = simp(np.array([M(q) for q in p]), 0.0007, False)
            if len(p) >= 2:
                tubes.append({"closed": False, "pts": p.round(4).tolist()})
    hi = max(max(q[1] for q in c["loops"][0]) for c in cans)
    J = {"logo_w": LOGO_W, "h": round(hi, 4), "cap_h": round(128 * 3 * S, 4), "cans": cans, "tubes": tubes}
    out = os.path.join(HERE, "kk_sign.json")
    json.dump(J, open(out, "w"), separators=(",", ":"))
    print("cans", len(cans), "loops", sum(len(c["loops"]) for c in cans), "tris", sum(len(c["tris"]) // 3 for c in cans),
          "tubes", len(tubes), "tube pts", sum(len(t["pts"]) for t in tubes), "h", round(hi, 3), "kB", os.path.getsize(out) // 1024)
    if len(sys.argv) > 1:          # a flat check drawing
        sc = 300.0
        W = int(LOGO_W * sc) + 60; Hh = int(hi * sc) + 60
        cv = np.full((Hh, W, 3), (40, 170, 230), np.uint8)
        P = lambda q: (int(W / 2 + q[0] * sc), int(Hh - 30 - q[1] * sc))
        for c in cans:
            t = c["tris"]
            for i in range(0, len(t), 3):
                cv2.fillPoly(cv, [np.array([P(t[i]), P(t[i + 1]), P(t[i + 2])], np.int32)], (40, 40, 160))
            for l in c["loops"]:
                cv2.polylines(cv, [np.array([P(q) for q in l], np.int32)], True, (20, 10, 60), 2)
        for t in tubes:
            cv2.polylines(cv, [np.array([P(q) for q in t["pts"]], np.int32)], t["closed"], (210, 220, 255), 2)
        cv2.imwrite(sys.argv[1], cv)


if __name__ == "__main__":
    main()
