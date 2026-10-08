"""K&B's logo as the oval it was (Steven, Oct 8 2026: "more oval than you have it"), replacing the
round disc make_logos.py kb() made. The proportions are the 1990s Houma newspaper ad's logo
(1.40 : 1, the letters about 70 % of the width), which agrees with Steven's photo of a lit K&B
sign (refs/kb-logo.jpg, about 1.6 : 1 seen from below). Purple face, gold rim, a red line inside
it, white K&B traced from the logo photo (src/kb_letters.png). DRUGS / TOBACCO are no longer used.

  python3 tools/stores/signs/make_kb_oval.py   (from the project folder)
"""
import os
import cv2
import numpy as np
import make_logos as ML

HERE = os.path.dirname(os.path.abspath(__file__))
H = 1.25                 # the oval's height (m): it sits on the 1.6 m fascia
W = H * 1.40             # and its width
LETTERS_W = 0.70 * W


def main():
    rx, ry = W / 2, H / 2
    w = 0.07 * ry                         # the gold rim's width
    m = cv2.imread(os.path.join(HERE, "src", "kb_letters.png"), 0) > 127
    ys, xs = np.where(m)
    s_px = LETTERS_W / (xs.max() - xs.min())
    lh = (ys.max() - ys.min()) * s_px
    x0 = xs.min() - (W - LETTERS_W) / 2 / s_px     # frame: the oval's left edge
    base = ys.max() + (H - lh) / 2 / s_px           # frame: the oval's bottom (letters centred)
    ML.write("kb_letters", "K&B", ML.trace_mask(m, "K&B", W, base, frame=(x0, s_px), smooth=6.0), W, (0, 0, 0), 0.1,
             "K&B traced from Steven's logo photo, centred in the oval", top=H, tex=False)
    E = ML.ellipse
    ML.write("kb_disc", "disc", [ML.letter("O", [E(rx, ry, rx - w, ry - w, 120)])], W, (0, 0, 0), 0.1, "the purple face", top=H, tex=False)
    ML.write("kb_rim", "rim", [ML.letter("O", [E(rx, ry, rx, ry, 120), E(rx, ry, rx - w, ry - w, 120, cw=True)])], W, (0, 0, 0), 0.1, "the gold rim", top=H, tex=False)
    ML.write("kb_line", "line", [ML.letter("O", [E(rx, ry, rx - w * 1.07, ry - w * 1.07, 120), E(rx, ry, rx - w * 1.36, ry - w * 1.36, 120, cw=True)])],
             W, (0, 0, 0), 0.1, "the red line", top=H, tex=False)


if __name__ == "__main__":
    main()
