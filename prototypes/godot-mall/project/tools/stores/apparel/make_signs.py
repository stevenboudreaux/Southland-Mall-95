"""Outlines of the signs of JW (neon), 5-7-9 and County Seat, for their store.gd files to
extrude or trace (1995 North East Mall video: JW 0:25, 5-7-9 0:33, County Seat 0:35).
Uses tools/stores/pocket_change/make_letters.py's outline code. Writes
tools/stores/apparel/{jw,s579,cs}_letters.json.
  python3 tools/stores/apparel/make_signs.py   (from the project folder)
"""
import json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "pocket_change"))
import make_letters as ml

_TT = ml.TTFont


def _tt(path):
    """Old fonts (DejaVu) carry no cap height in OS/2: measure it from the H."""
    f = _TT(path)
    os2 = f["OS/2"]
    if not getattr(os2, "sCapHeight", 0):
        g = f.getGlyphSet()["H"]
        from fontTools.pens.boundsPen import BoundsPen
        bp = BoundsPen(f.getGlyphSet())
        g.draw(bp)
        os2.sCapHeight = int(bp.bounds[3])
    return f


ml.TTFont = _tt

SIGNS = [
    # JW: a tall serif J and W traced in double white neon (video 0:25)
    ("jw_letters.json", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", "JW", 0.78, -0.02, 0.5),
    # 5-7-9: heavy italic numerals with round dots between (video 0:33)
    ("s579_letters.json", "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf", "5•7•9", 0.46, 0.02, 0.5),
    # COUNTY-SEAT: wide, heavy wedge-serif capitals with a centred dot (video 0:35)
    ("cs_letters.json", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", "COUNTY•SEAT", 0.40, 0.03, 0.5),
]

for out, font, text, cap, track, space in SIGNS:
    ml.HERE = HERE
    ml.FONT = font
    ml.TEXT = text
    ml.CAP_H = cap
    ml.TRACK = track
    ml.SPACE = space
    ml.main()
    shutil.move(os.path.join(HERE, "letters.json"), os.path.join(HERE, out))
    if out.startswith("cs_"):
        # County Seat's capitals are wider and heavier than the stand-in face: stretch them
        J = json.load(open(os.path.join(HERE, out)))
        SX = 1.22
        for Lt in J["letters"]:
            Lt["tris"] = [[round(p[0] * SX, 5), p[1]] for p in Lt["tris"]]
            Lt["loops"] = [[[round(p[0] * SX, 5), p[1]] for p in lp] for lp in Lt["loops"]]
        J["width"] = round(J["width"] * SX, 4)
        json.dump(J, open(os.path.join(HERE, out), "w"))
        print("  stretched to %.2f m" % J["width"])
    print("  ->", out)
