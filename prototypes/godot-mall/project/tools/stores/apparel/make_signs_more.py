"""Outlines of the Wave 4 clothing stores' signs, for more.gd to extrude or trace in neon.
Hammond 1993: "Lerner" in white script (22.4 s), "the limited" in white neon script on a
black capsule (3.8 s), "Lane Bryant" in white lit serif letters (5.2 s). Pecanland 1992:
"Miller's Outpost" in outlined serif letters with a star (9:13). Gadzooks slideshow: red
neon "GADZOOKS" (0:02, 0:16). Stand-in faces: Mr Dafoe (OFL, tools/stores/gumballs),
Inter Bold Italic, DejaVu Serif, DejaVu Serif Bold and Nunito Black (OFL, tools/stores/media).
Uses tools/stores/apparel/make_signs.py's font fix and pocket_change/make_letters.py.
Writes tools/stores/apparel/{lerner,lerner_ny,limited,lb,mo,gz}_letters.json.
  python3 tools/stores/apparel/make_signs_more.py   (from the project folder)
"""
import os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "pocket_change"))
import make_letters as ml
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen

_TT = ml.TTFont


def _tt(path):
    f = _TT(path)
    os2 = f["OS/2"]
    if not getattr(os2, "sCapHeight", 0):
        g = f.getGlyphSet()["H"]
        bp = BoundsPen(f.getGlyphSet())
        g.draw(bp)
        os2.sCapHeight = int(bp.bounds[3])
    return f


ml.TTFont = _tt
GB = os.path.join(HERE, "..", "gumballs")
MD = os.path.join(HERE, "..", "media")
SIGNS = [
    ("lerner_letters.json", os.path.join(GB, "MrDafoe-Regular.ttf"), "Lerner", 0.62, 0.0, 0.5),
    ("lerner_ny_letters.json", "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf", "NEW YORK", 0.09, 0.25, 0.9),
    ("limited_letters.json", "/usr/share/fonts/opentype/inter/Inter-BoldItalic.otf", "the limited", 0.42, 0.0, 0.6),
    ("lb_letters.json", "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", "Lane Bryant", 0.40, 0.0, 0.7),
    ("mo_letters.json", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", "Miller's    Outpost", 0.34, 0.02, 0.9),
    ("gz_letters.json", os.path.join(MD, "Nunito-Black.ttf"), "GADZOOKS", 0.42, 0.04, 0.5),
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
    print("  ->", out)
