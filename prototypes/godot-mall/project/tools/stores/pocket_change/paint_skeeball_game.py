"""Textures for the playable SKEE-BALL page (play/skeeball.html, Steven Oct 11 2026).

The page draws the mall's own four alleys, so it uses the same painted textures as the mall
(paint_skee.py -> tex/pc/skee_*.png, and the store's carpet and wall), re-encoded as WebP
into play/skeeball/. Run from the project folder after paint_skee.py:
    python3 tools/stores/pocket_change/paint_skeeball_game.py
"""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.abspath(os.path.join(PROJ, "..", "play", "skeeball"))
os.makedirs(OUT, exist_ok=True)

NAMES = ["skee_ball", "skee_board", "skee_front", "skee_lane", "skee_led", "skee_marquee", "skee_mesh",
         "skee_metal", "skee_num", "skee_rail", "skee_side", "skee_sidetext", "skee_ticket",
         "store_carpet", "store_wall"]

for n in NAMES:
    im = Image.open(os.path.join(PROJ, "tex", "pc", n + ".png"))
    if n == "store_carpet":
        im = im.resize((512, 512), Image.LANCZOS)   # seen only at a distance, under the alleys
    if im.mode not in ("RGB", "RGBA"):
        im = im.convert("RGBA")
    p = os.path.join(OUT, n.replace("skee_", "") + ".webp")
    lossless = n in ("skee_mesh",)
    im.save(p, "WEBP", quality=88, method=6, lossless=lossless)
    print(os.path.basename(p), im.size, os.path.getsize(p))
