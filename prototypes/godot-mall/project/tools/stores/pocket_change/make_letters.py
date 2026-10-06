"""Outlines of Pocket Change's raised sign letters, for store.gd to extrude.

The 2009 photo of the Southland front (unchanged since the 1990s) shows
"POCKET CHANGE" in raised channel letters: a heavy grotesque in capitals,
like Helvetica Bold. FreeSans Bold is a Helvetica clone, so the outlines come
from it. Curves are flattened, and each letter's face is triangulated with its
holes (earcut). Units are metres, with the baseline at y = 0 and the text
starting at x = 0.
Writes tools/stores/pocket_change/letters.json.
  python3 tools/stores/pocket_change/make_letters.py   (from the project folder)
"""
import json, os
import mapbox_earcut as earcut
import numpy as np
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
TEXT = "POCKET CHANGE"
CAP_H = 0.35          # metres: the caps are ~0.35 m (photo: the letters against the 20 cm glass blocks at both ends)
TRACK = 0.02          # extra letter spacing, in cap heights (the photo's letters sit a little apart)
STEPS = 8             # segments per curve


class FlatPen(BasePen):
    def __init__(self, gs):
        super().__init__(gs)
        self.contours = []
        self.cur = []

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
            self.cur.append((mt * mt * p0[0] + 2 * mt * t * p1[0] + t * t * p2[0],
                             mt * mt * p0[1] + 2 * mt * t * p1[1] + t * t * p2[1]))

    def _closePath(self):
        if len(self.cur) > 2:
            if self.cur[0] == self.cur[-1]:
                self.cur.pop()
            self.contours.append(self.cur)
        self.cur = []

    _endPath = _closePath


def area(c):
    a = 0.0
    for i in range(len(c)):
        x0, y0 = c[i]
        x1, y1 = c[(i + 1) % len(c)]
        a += x0 * y1 - x1 * y0
    return a * 0.5


def inside(pt, c):
    x, y = pt
    n = False
    for i in range(len(c)):
        x0, y0 = c[i]
        x1, y1 = c[(i + 1) % len(c)]
        if (y0 > y) != (y1 > y) and x < (x1 - x0) * (y - y0) / (y1 - y0) + x0:
            n = not n
    return n


def main():
    f = TTFont(FONT)
    gs = f.getGlyphSet()
    cmap = f.getBestCmap()
    cap = f["OS/2"].sCapHeight or 729
    s = CAP_H / cap
    hmtx = f["hmtx"]
    x = 0.0
    letters = []
    for ch in TEXT:
        gname = cmap[ord(ch)]
        adv = hmtx[gname][0] * s
        if ch == " ":
            x += adv
            continue
        pen = FlatPen(gs)
        gs[gname].draw(pen)
        cons = [[(px * s + x, py * s) for (px, py) in c] for c in pen.contours]
        # outer contours contain no other contour's first point... group holes with their outer
        outers = []
        holes = []
        for c in cons:
            depth = sum(1 for o in cons if o is not c and inside(c[0], o))
            (outers if depth % 2 == 0 else holes).append(c)
        tris = []
        loops = []
        for o in outers:
            if area(o) < 0:
                o = o[::-1]          # outer counter-clockwise (face +y up in the letter's plane)
            hs = []
            for h in holes:
                if inside(h[0], o):
                    hs.append(h if area(h) < 0 else h[::-1])   # holes clockwise
            verts = list(o)
            rings = [len(verts)]
            for h in hs:
                verts += h
                rings.append(len(verts))
            idx = earcut.triangulate_float32(np.array(verts, dtype=np.float32).reshape(-1, 2), np.array(rings, dtype=np.uint32))
            for i in idx:
                tris.append([round(verts[i][0], 5), round(verts[i][1], 5)])
            loops.append([[round(p[0], 5), round(p[1], 5)] for p in o])
            for h in hs:
                loops.append([[round(p[0], 5), round(p[1], 5)] for p in h])
        letters.append({"ch": ch, "tris": tris, "loops": loops})
        x += adv + TRACK * CAP_H
    width = x - TRACK * CAP_H
    out = {"text": TEXT, "cap_h": CAP_H, "width": round(width, 4), "letters": letters,
           "note": "loops: outer counter-clockwise, holes clockwise (seen from the front, y up); tris: face triangles"}
    json.dump(out, open(os.path.join(HERE, "letters.json"), "w"))
    print("width %.3f m at cap %.2f m, %d letters, %d triangles" % (width, CAP_H, len(letters), sum(len(l["tris"]) for l in letters) // 3))


if __name__ == "__main__":
    main()
