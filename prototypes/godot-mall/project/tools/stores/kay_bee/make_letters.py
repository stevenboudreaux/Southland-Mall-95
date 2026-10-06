"""Outlines of Kay-Bee Toys' raised sign letters, for store.gd to extrude.

Steven's photo of the Southland front shows "KAY·BEE TOYS" in red channel letters on
the royal-blue fascia: heavy sans capitals with a round dot between KAY and BEE.
FreeSans Bold stands in for the face. Uses the outline code of
tools/stores/pocket_change/make_letters.py. Writes tools/stores/kay_bee/letters.json.
  python3 tools/stores/kay_bee/make_letters.py   (from the project folder)
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "pocket_change"))
import make_letters as ml

ml.HERE = HERE
ml.TEXT = "KAY•BEE TOYS"
ml.CAP_H = 0.40        # the caps fill half of the 0.8 m fascia (photo)
ml.TRACK = 0.04
ml.SPACE = 0.9
if __name__ == "__main__":
    ml.main()
