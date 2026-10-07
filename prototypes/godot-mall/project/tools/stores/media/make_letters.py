"""Outlines of the media shops' raised sign letters, for kit.gd's letters() to extrude.

Babbage's (video 19:50-20:26): "Babbage's" in fat rounded lower-case neon channel letters
with a capital B. Sound Shop (Hammond 1993, 4.3-4.9 s): "SOUND SHOP" in fat rounded italic
capitals. Nunito Black and Nunito Black Italic (SIL OFL, FONTS-OFL.txt; static instances
of the variable font at weight 900) stand in for both faces. Uses the outline code of
tools/stores/pocket_change/make_letters.py. Writes bb_letters.json and ss_letters.json.
  python3 tools/stores/media/make_letters.py   (from the project folder)
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "pocket_change"))
import make_letters as ml

ml.HERE = HERE
for text, font, cap, track, out in [("Babbage’s", "Nunito-Black.ttf", 0.42, 0.02, "bb_letters.json"),
                                     ("SOUND SHOP", "Nunito-BlackItalic.ttf", 0.36, 0.03, "ss_letters.json")]:
    ml.FONT = os.path.join(HERE, font)
    ml.TEXT = text
    ml.CAP_H = cap
    ml.TRACK = track
    ml.SPACE = 0.9
    ml.main()
    os.replace(os.path.join(HERE, "letters.json"), os.path.join(HERE, out))
