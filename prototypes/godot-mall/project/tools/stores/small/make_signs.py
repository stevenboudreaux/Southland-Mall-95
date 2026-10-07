"""Outlines of the Wave 5 small shops' signs, for store.gd to extrude or trace in neon:
GNC's three red letters, MasterCuts' white condensed lettering, Coach House's white serif
capitals, Wicks 'N' Sticks' white rounded letters, Chick-fil-A's script name (traced in
neon). Stand-in faces: FreeSans Bold, DejaVu Sans Condensed Bold, DejaVu Serif, Nunito
Black (OFL, tools/stores/media) and Mr Dafoe (OFL, tools/stores/gumballs). Uses
tools/stores/apparel/make_signs.py's approach. Writes tools/stores/small/*_letters.json.
  python3 tools/stores/small/make_signs.py   (from the project folder)
"""
import os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "pocket_change"))
import make_letters as ml
from fontTools.pens.boundsPen import BoundsPen

_TT = ml.TTFont


def _tt(path):
    f = _TT(path)
    os2 = f["OS/2"]
    if not getattr(os2, "sCapHeight", 0):
        bp = BoundsPen(f.getGlyphSet())
        f.getGlyphSet()["H"].draw(bp)
        os2.sCapHeight = int(bp.bounds[3])
    return f


ml.TTFont = _tt
DJ = "/usr/share/fonts/truetype/dejavu/"
SIGNS = [
    ("gnc_letters.json", "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf", "GNC", 0.5, 0.04, 0.5),
    ("mc_letters.json", DJ + "DejaVuSansCondensed-Bold.ttf", "MasterCuts", 0.28, 0.01, 0.5),
    ("ch_letters.json", DJ + "DejaVuSerif.ttf", "COACH HOUSE", 0.32, 0.08, 1.2),
    ("ws_letters.json", os.path.join(HERE, "..", "media", "Nunito-Black.ttf"), "Wicks 'N' Sticks", 0.26, 0.01, 0.8),
    ("cfa_letters.json", os.path.join(HERE, "..", "gumballs", "MrDafoe-Regular.ttf"), "Chick-fil-A", 0.42, 0.0, 0.5),
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

# Wave 6 (store2.gd): Radio Shack's red wordmark, B. Dalton's white script, Karmelkorn's red
# slab-serif capitals with a big K, Zales' silver capitals
MORE = [
    ("rs_letters.json", DJ + "DejaVuSerif-BoldItalic.ttf", "Radio Shack", 0.30, 0.0, 0.6),
    ("bd_letters.json", os.path.join(HERE, "..", "gumballs", "MrDafoe-Regular.ttf"), "B. Dalton", 0.5, 0.0, 0.5),
    ("bd_sub_letters.json", DJ + "DejaVuSerif.ttf", "BOOKSELLER", 0.09, 0.2, 0.9),
    ("kk_letters.json", os.path.join(HERE, "..", "woolworth", "RobotoSlab-ExtraBold.ttf"), "Karmelkorn", 0.62, 0.0, 0.5),
    ("zl_letters.json", "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf", "ZALES", 0.34, 0.06, 0.5),
    ("zl_sub_letters.json", "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf", "JEWELERS", 0.11, 0.2, 0.5),
]
if __name__ == "__main__":
    for out, font, text, cap, track, space in MORE:
        ml.HERE = HERE
        ml.FONT = font
        ml.TEXT = text
        ml.CAP_H = cap
        ml.TRACK = track
        ml.SPACE = space
        ml.main()
        shutil.move(os.path.join(HERE, "letters.json"), os.path.join(HERE, out))
