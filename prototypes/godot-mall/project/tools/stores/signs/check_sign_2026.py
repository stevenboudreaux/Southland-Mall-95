"""Checks a 2026 sign's letters against its squared-up reference picture, by eye.

For each part with a "ref_box" ([x0, y0, x1, y1], pixels in the sign's "ref_img", a picture in
y26/src/ squared up with photo_trace.py), draws the part's generated outlines (y26/<id>_<part>_logo.json)
fitted into that box: the reference on the left, the reference with the outlines over it (yellow)
in the middle, the outlines alone filled in the spec's face colours on the right.
Writes y26/check/<id>.png.

  python3 tools/stores/signs/check_sign_2026.py <id> [...]   (from the project folder; after make_signs_2026.py)
"""
import json, os, sys
import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
Y26 = os.path.join(HERE, "y26")


def hexbgr(h):
    h = h.lstrip("#")
    return (int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16))


def check(sid):
    s = json.load(open(os.path.join(Y26, "parts", sid + ".json")))
    ref = cv2.imread(os.path.join(Y26, "src", s["ref_img"]))
    if ref is None:
        raise SystemExit("%s: no ref_img" % sid)
    over = ref.copy()
    flat = np.full_like(ref, 0)
    flat[:] = hexbgr(s.get("backer", {}).get("color", s.get("fascia_color", "#808080")))
    for p in s["parts"]:
        if "ref_box" not in p:
            continue
        J = json.load(open(os.path.join(Y26, "%s_%s_logo.json" % (sid, p["name"]))))
        x0, y0, x1, y1 = p["ref_box"]
        kx = (x1 - x0) / float(J["width"])
        ky = (y1 - y0) / float(J["cap_h"])
        col = hexbgr(p.get("face", "#ffffff"))
        for L in J["letters"]:
            for lp in L["loops"]:
                pts = np.array([[x0 + q[0] * kx, y1 - q[1] * ky] for q in lp], np.int32)
                cv2.polylines(over, [pts], True, (0, 255, 255), 1, cv2.LINE_AA)
        m = np.zeros(ref.shape[:2], np.uint8)
        for L in J["letters"]:
            # outer loops counter-clockwise (positive area), holes clockwise: fill in order
            for lp in L["loops"]:
                pts = np.array([[x0 + q[0] * kx, y1 - q[1] * ky] for q in lp], np.int32)
                a = 0.5 * sum(lp[i][0] * lp[(i + 1) % len(lp)][1] - lp[(i + 1) % len(lp)][0] * lp[i][1] for i in range(len(lp)))
                cv2.fillPoly(m, [pts], 255 if a > 0 else 0)
        flat[m > 0] = col
    out = np.hstack([ref, over, flat])
    os.makedirs(os.path.join(Y26, "check"), exist_ok=True)
    cv2.imwrite(os.path.join(Y26, "check", sid + ".png"), out)
    print("y26/check/%s.png" % sid)


if __name__ == "__main__":
    for sid in sys.argv[1:]:
        check(sid)
