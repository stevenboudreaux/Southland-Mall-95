"""Duncan Sports, Inc. (s28): the script from the store's 1990s Courier ad ("IT PAYS TO PLAY ...
VISIT OUR NEW STORE LOCATION ACROSS FROM SEARS (NEXT DOOR TO CUCOS)", src/duncan_ad.png),
traced as it is printed and built in blue over the facade (Steven, Oct 8 2026: "recreate that
exact script in blue"). The ribbon above it is left out. Writes du_name_logo.json and
tex/sg/du_name_face.png, du_name_glow.png.

  python3 tools/stores/signs/make_duncan.py   (from the project folder)
"""
import os
import cv2
import numpy as np
import make_logos as ML

HERE = os.path.dirname(os.path.abspath(__file__))
WIDTH = 4.9          # metres: the script across the 6 m front's bulkhead
S = 6                # trace at 6x


def main():
    im = cv2.imread(os.path.join(HERE, "src", "duncan_ad.png"), 0)
    x0, y0, x1, y1 = 70, 105, 640, 190
    g = cv2.resize(im[y0:y1, x0:x1], None, fx=S, fy=S, interpolation=cv2.INTER_CUBIC)
    g = cv2.GaussianBlur(g, (0, 0), 2.0)
    m = (g < 120).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    keep = np.zeros(m.shape, bool)
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if y <= 2 and h < 40 * S:
            continue          # the ribbon's tails, cut by the crop's top edge
        if a < 600:
            continue
        keep |= lab == i
    cv2.imwrite(os.path.join(HERE, "src", "duncan_mask.png"), keep.astype(np.uint8) * 255)
    ys, xs = np.where(keep)
    # the baseline: the bottom of the lowercase (u, n, c, a), not the p's descender
    base = 172 - y0
    L = ML.trace_mask(keep, "DuncanSports,Inc.", WIDTH, base * S, smooth=1.5)
    ML.write("du_name", "Duncan Sports, Inc.", L, WIDTH, (60, 110, 255), 0.18, "traced from the Courier ad's script")


if __name__ == "__main__":
    main()
