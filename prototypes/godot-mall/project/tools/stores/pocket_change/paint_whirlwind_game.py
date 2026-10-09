"""Textures for the playable WHIRLWIND page (play/whirlwind.html, Steven Oct 9).

Re-runs the cabinet's own painters (paint_cyclone.py) without their final downscale, so the
game page shows the same playfield, console and BONUS box as the mall's cabinet at 2x the
resolution (the rest at their shipped size). Writes play/whirlwind/*.webp. Run from the project folder:
    python3 tools/stores/pocket_change/paint_whirlwind_game.py
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paint_cyclone as pc

OUT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "play", "whirlwind"))
os.makedirs(OUT, exist_ok=True)
_down = pc.down


def save(im, name, colors=0):
    p = os.path.join(OUT, name + ".webp")
    if im.mode not in ("RGB", "RGBA"):
        im = im.convert("RGBA")
    im.save(p, "WEBP", quality=88, method=6)
    print(name, im.size, os.path.getsize(p))


pc.save = save
pc.down = lambda im, k=2: im          # the playfield at its full working resolution (2048)
pc.paint_field()
pc.down = _down                       # the rest post-process at their shipped size
pc.paint_console()
pc.paint_bonus()
pc.paint_button()
pc.paint_deck()
pc.paint_tower()
pc.paint_front()
