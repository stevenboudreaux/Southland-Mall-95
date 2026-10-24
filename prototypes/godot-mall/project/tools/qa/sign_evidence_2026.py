"""Side-by-side evidence for the 2026 signs: each sign's squared-up reference from Steven's
footage (y26/src/<id>_ref.png) next to the baked in-game view of it (a wingshots.gd shot named
<id>.png), several signs per sheet.

  python3 tools/qa/sign_evidence_2026.py <shots dir> <out prefix>
  e.g. python3 tools/qa/sign_evidence_2026.py /tmp/baked ../../../production/qa/evidence/d43-signs
"""
import glob, json, os, sys
import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
Y26 = os.path.join(HERE, "..", "stores", "signs", "y26")
W, H = 560, 315


def fit(im, w, h):
    k = min(w / im.shape[1], h / im.shape[0])
    im = cv2.resize(im, (max(1, int(im.shape[1] * k)), max(1, int(im.shape[0] * k))), interpolation=cv2.INTER_AREA)
    out = np.full((h, w, 3), 24, np.uint8)
    y, x = (h - im.shape[0]) // 2, (w - im.shape[1]) // 2
    out[y:y + im.shape[0], x:x + im.shape[1]] = im
    return out


def main(shots, prefix):
    rows = []
    for f in sorted(glob.glob(os.path.join(Y26, "parts", "*.json"))):
        s = json.load(open(f))
        sid = s["id"]
        shot = os.path.join(shots, sid + ".png")
        if not os.path.exists(shot):
            continue
        ref = cv2.imread(os.path.join(Y26, "src", s.get("ref_img", ""))) if s.get("ref_img") else None
        left = fit(ref, W, H) if ref is not None else np.full((H, W, 3), 24, np.uint8)
        right = fit(cv2.imread(shot), W, H)
        row = np.hstack([left, np.full((H, 8, 3), 255, np.uint8), right])
        label = "%s  (%s)" % (s["store"], s.get("ref", "")[:60])
        cv2.rectangle(row, (0, 0), (row.shape[1], 26), (0, 0, 0), -1)
        cv2.putText(row, label, (8, 19), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1, cv2.LINE_AA)
        rows.append(row)
    per = 6
    for k in range(0, len(rows), per):
        sheet = np.vstack([np.vstack([r, np.full((6, r.shape[1], 3), 255, np.uint8)]) for r in rows[k:k + per]])
        cv2.imwrite("%s-%02d.jpg" % (prefix, k // per + 1), sheet, [cv2.IMWRITE_JPEG_QUALITY, 84])
    print("%d signs, %d sheets" % (len(rows), (len(rows) + per - 1) // per))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
