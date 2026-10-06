"""Word-free copies of the basketball and claw-machine marquees, for the owner-editable
names (scripts/signs.gd draws the words live over them; design/godot-owner-signs.md).
Runs each painter's own marquee function with its text drawing switched off.
Writes tex/pc/hoops_marquee_blank.png and crane_header_<0..2>_blank.png.
  python3 tools/stores/pocket_change/paint_blanks.py   (from the project folder)
"""
import os, sys
from PIL import ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paint_hoops as ph
import paint_crane as pc

_text = ImageDraw.ImageDraw.text
ImageDraw.ImageDraw.text = lambda self, *a, **k: None
try:
    keep = ph.save
    ph.save = lambda im, name: keep(im, name + "_blank")
    ph.paint_marquee()
    ph.save = keep
    keep_c = pc.save
    keep_f = pc.fancy_text
    pc.save = lambda im, name, colors=0: keep_c(im, name.replace(".png", "_blank.png"), colors)
    pc.fancy_text = lambda *a, **k: None
    for s in range(3):
        pc.header(s)
    pc.save = keep_c
    pc.fancy_text = keep_f
finally:
    ImageDraw.ImageDraw.text = _text
