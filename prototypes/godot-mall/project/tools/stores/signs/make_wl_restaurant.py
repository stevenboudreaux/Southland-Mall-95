"""Woolworth's "Restaurant" as red lit channel letters straight on the dark fascia over the
restaurant's door (Steven, Oct 8 2026: no white plate behind them), in Roboto Slab ExtraBold (the
face the plate was painted in, tools/stores/woolworth/paint.py). Writes wlr_logo.json and
tex/sg/wlr_face.png, wlr_glow.png.

  python3 tools/stores/signs/make_wl_restaurant.py   (from the project folder)
"""
import os
import make_logos as ML

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "..", "woolworth", "RobotoSlab-ExtraBold.ttf")


def main():
    cap = 0.40
    L, w = ML.set_text(FONT, "Restaurant", cap, 0.01)
    if w > 3.5:
        k = 3.5 / w
        L, w = ML.set_text(FONT, "Restaurant", cap * k, 0.01 * k)
    ML.write("wlr", "Restaurant", L, w, (255, 50, 30), 0.22, "Roboto Slab ExtraBold, as the plate was painted")


if __name__ == "__main__":
    main()
