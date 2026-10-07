"""Square up a photo of a sign and trace its coloured parts into a mask, ready for a sign maker
(make_cucos.py). These are the steps the Cucos neon sign was traced with, as one tool: see
design/godot-neon-signs.md for when to use which, and for the numbers that worked.

  front  two photos of the same sign: registers the sharp oblique one to the square-on one
  quad   one photo: squares up four corners of a rectangle on the sign's plane
  level  turns a squared-up picture so a part known to be level is level
  mask   the parts of one colour (an open can's inside, a lit face), cleaned and smoothed
  cut    cuts a mask where separate parts touch, and lists the parts
  zoom   a magnified crop with a pixel grid and mask outlines, for reading off coordinates

Every command takes --help. Rectangles are x0,y0,x1,y1 in pixels; hues are OpenCV's (0 to 180).
Needs opencv-python-headless and numpy. Run from the project folder, e.g.:

  python3 tools/stores/signs/photo_trace.py front --oblique close.png --orect 370,300,790,640 \\
      --frontal front.png --frect 280,75,455,190 --hue red --canvas 250,60,490,230 --out f0.png
  python3 tools/stores/signs/photo_trace.py level --front f0.png --hue blue --out f1.png
  python3 tools/stores/signs/photo_trace.py mask --front f1.png --hue red --box 0,0,1920,980 \\
      --out m.png --overlay m_check.png
  python3 tools/stores/signs/photo_trace.py zoom --front f1.png --mask m.png --rect 730,280,1190,650 --out z.png
  python3 tools/stores/signs/photo_trace.py cut --mask m.png --lines "765,506,765,542;936,408,947,454" --out cans.png
"""
import argparse
import sys

import cv2
import numpy as np

HUES = {"red": (168, 12), "orange": (5, 22), "yellow": (20, 35), "green": (35, 85), "aqua": (80, 100),
        "blue": (105, 135), "purple": (130, 150), "pink": (145, 172), "any": (0, 180)}


def rect(s):
    """'x0,y0,x1,y1' -> four ints."""
    v = [int(round(float(t))) for t in s.split(",")]
    if len(v) != 4:
        raise argparse.ArgumentTypeError("a rectangle is x0,y0,x1,y1")
    return v


def hue_range(s):
    """A colour name from HUES, or 'lo,hi' (lo > hi wraps through red)."""
    if s in HUES:
        return HUES[s]
    lo, hi = [int(t) for t in s.split(",")]
    return lo, hi


def colour_mask(im, hue, smin, vmin, smax=255, vmax=255):
    """255 where a BGR image's pixels are in the hue range and the saturation and value limits."""
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[..., 0].astype(int), hsv[..., 1].astype(int), hsv[..., 2].astype(int)
    lo, hi = hue
    inh = ((h >= lo) | (h <= hi)) if lo > hi else ((h >= lo) & (h <= hi))
    return (inh & (s >= smin) & (s <= smax) & (v >= vmin) & (v <= vmax)).astype(np.uint8) * 255


def odd(x):
    """The nearest odd integer of at least 3 (a structuring element's size)."""
    k = max(3, int(round(x)))
    return k if k % 2 else k + 1


def ell(k):
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))


def keep_big(m, min_area):
    """The mask's connected parts of at least min_area pixels."""
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    out = np.zeros_like(m)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] >= min_area:
            out[lab == i] = 255
    return out


def parts(m, min_area=500):
    """[(x, y, w, h, area)] of a mask's connected parts, largest first."""
    n, _, st, _ = cv2.connectedComponentsWithStats(m, 8)
    r = [tuple(int(v) for v in st[i]) for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= min_area]
    return sorted(r, key=lambda t: -t[4])


# ---------------------------------------------------------------------------- front
def register(I, T):
    """The homography taking T's pixels to I's, for two masks (float, 0..1) of the same flat shape
    seen from two places. Start: both shapes whitened by their second moments, then the rotation
    between them searched in 3 degree steps; then ECC, blurred wide and narrowed (8, 4, 2 px)."""
    def stats(M):
        ys, xs = np.nonzero(M > 0.5)
        P = np.stack([xs, ys], 1).astype(np.float64)
        mu = P.mean(0)
        return mu, np.cov((P - mu).T)

    def sqrtm(C):
        w, v = np.linalg.eigh(C)
        return v @ np.diag(np.sqrt(w)) @ v.T

    muI, CI = stats(I)
    muT, CT = stats(T)
    SI, ST = sqrtm(CI), sqrtm(CT)
    best = None
    Tb = cv2.GaussianBlur(T, (0, 0), 6)
    for ang in np.arange(0, 360, 3):
        a = np.deg2rad(ang)
        R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
        A = SI @ R @ np.linalg.inv(ST)
        t = muI - A @ muT
        W = np.hstack([A, t[:, None]]).astype(np.float32)
        Iw = cv2.warpAffine(I, W, (T.shape[1], T.shape[0]), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)
        Iwb = cv2.GaussianBlur(Iw, (0, 0), 6)
        sc = float((Iwb * Tb).sum() / np.sqrt((Iwb ** 2).sum() * (Tb ** 2).sum()))
        if best is None or sc > best[0]:
            best = (sc, ang, W)
    print("start: correlation %.3f at %d degrees" % (best[0], best[1]))
    W = np.vstack([best[2], [0, 0, 1]]).astype(np.float32)
    for sig in (8, 4, 2):
        Tb = cv2.GaussianBlur(T, (0, 0), sig)
        Ib = cv2.GaussianBlur(I, (0, 0), sig)
        try:
            cc, W = cv2.findTransformECC(Tb, Ib, W, cv2.MOTION_HOMOGRAPHY,
                                         (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 400, 1e-7), None, 1)
            print("ecc at blur %d: %.3f" % (sig, cc))
        except cv2.error as e:
            print("ecc failed at blur %d: %s" % (sig, str(e).strip().splitlines()[-1]))
    return W


def cmd_front(a):
    obl = cv2.imread(a.oblique)
    fro = cv2.imread(a.frontal)
    ox0, oy0, ox1, oy1 = a.orect
    fx0, fy0, fx1, fy1 = a.frect
    hue = hue_range(a.hue)
    # both masks made at twice the working size, then halved: about 840 px (oblique) and 700 px (frontal)
    so = 840.0 / (ox1 - ox0)
    sf = 700.0 / (fx1 - fx0)
    cu = cv2.resize(obl[oy0:oy1, ox0:ox1], None, fx=2 * so, fy=2 * so, interpolation=cv2.INTER_CUBIC)
    mo = colour_mask(cu, hue, a.osv[0], a.osv[1])
    mo = cv2.morphologyEx(mo, cv2.MORPH_CLOSE, ell(odd(13 * mo.shape[1] / 1680.0)))
    mo = cv2.morphologyEx(mo, cv2.MORPH_OPEN, ell(odd(5 * mo.shape[1] / 1680.0)))
    mo = keep_big(mo, 3000)
    fu = cv2.resize(fro[fy0:fy1, fx0:fx1], None, fx=2 * sf, fy=2 * sf, interpolation=cv2.INTER_CUBIC)
    mf = colour_mask(fu, hue, a.fsv[0], a.fsv[1])
    mf = cv2.morphologyEx(mf, cv2.MORPH_CLOSE, ell(odd(9 * mf.shape[1] / 1400.0)))
    mf = keep_big(mf, 3000)
    I = cv2.resize(mo, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    T = cv2.resize(mf, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    W = register(I, T).astype(np.float64)
    Iw = cv2.warpPerspective(I, W.astype(np.float32), (T.shape[1], T.shape[0]), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)
    iou = ((Iw > 0.5) & (T > 0.5)).sum() / float(((Iw > 0.5) | (T > 0.5)).sum())
    print("overlap of the two masks (IoU): %.3f" % iou)
    if a.overlay:
        ov = np.zeros(T.shape + (3,), np.uint8)
        ov[..., 2] = (T * 255).astype(np.uint8)       # red: the frontal photo's mask
        ov[..., 1] = (Iw * 255).astype(np.uint8)      # green: the oblique one, warped; yellow where they agree
        cv2.imwrite(a.overlay, ov)
    # frontal-photo pixels -> oblique-photo pixels
    C = np.array([[sf, 0, -sf * fx0], [0, sf, -sf * fy0], [0, 0, 1.0]])
    B = np.array([[1 / so, 0, ox0], [0, 1 / so, oy0], [0, 0, 1.0]])
    H = B @ W @ C
    if a.canvas:
        cx0, cy0, cx1, cy1 = a.canvas
    else:
        mx, my = 0.2 * (fx1 - fx0), 0.2 * (fy1 - fy0)
        cx0, cy0, cx1, cy1 = fx0 - mx, fy0 - my, fx1 + mx, fy1 + my
    s = float(a.scale)
    D = np.array([[1 / s, 0, cx0], [0, 1 / s, cy0], [0, 0, 1.0]])
    size = (int((cx1 - cx0) * s), int((cy1 - cy0) * s))
    out = cv2.warpPerspective(obl, H @ D, size, flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP, borderValue=(128, 128, 128))
    cv2.imwrite(a.out, out)
    np.save(a.out + ".H.npy", H)
    print("wrote %s (%d x %d), and the frontal-to-oblique homography beside it" % (a.out, size[0], size[1]))


# ---------------------------------------------------------------------------- quad
def cmd_quad(a):
    im = cv2.imread(a.photo)
    pts = np.array([[float(v) for v in p.split(",")] for p in a.pts.split(";")], np.float32)
    if pts.shape != (4, 2):
        sys.exit("--pts takes four corners: top-left;top-right;bottom-right;bottom-left")
    aw, ah = [float(v) for v in a.aspect.split(":")]
    w = float(a.width)
    h = w * ah / aw
    mx, my = a.margin * w, a.margin * w
    dst = np.array([[mx, my], [mx + w, my], [mx + w, my + h], [mx, my + h]], np.float32)
    H = cv2.getPerspectiveTransform(pts, dst)
    size = (int(w + 2 * mx), int(h + 2 * my))
    out = cv2.warpPerspective(im, H, size, flags=cv2.INTER_CUBIC, borderValue=(128, 128, 128))
    cv2.imwrite(a.out, out)
    print("wrote %s (%d x %d): the rectangle is at x %d..%d, y %d..%d" % (a.out, size[0], size[1], mx, mx + w, my, my + h))


# ---------------------------------------------------------------------------- level
def level_angle(im, hue, smin, vmin, edge):
    """The slope (degrees, image coordinates) of the top or bottom edge of the largest part of a colour."""
    m = colour_mask(im, hue, smin, vmin)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    if n < 2:
        sys.exit("nothing of that colour to level on")
    i = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    bm = (lab == i)
    ys, xs = np.nonzero(bm)
    span = xs.max() - xs.min()
    pts = []
    for c in np.arange(xs.min() + int(0.15 * span), xs.max() - int(0.1 * span), 4):
        yy = np.nonzero(bm[:, c])[0]
        if len(yy) > 10:
            pts.append((c, yy.max() if edge == "bottom" else yy.min()))
    pts = np.array(pts, float)
    return float(np.degrees(np.arctan(np.polyfit(pts[:, 0], pts[:, 1], 1)[0])))


def cmd_level(a):
    im = cv2.imread(a.front)
    ang = a.deg if a.deg is not None else level_angle(im, hue_range(a.hue), a.sv[0], a.sv[1], a.edge)
    h, w = im.shape[:2]
    R = cv2.getRotationMatrix2D((w / 2, h / 2), ang, 1.0)
    out = cv2.warpAffine(im, R, (w, h), flags=cv2.INTER_CUBIC, borderValue=(128, 128, 128))
    cv2.imwrite(a.out, out)
    print("turned by %.2f degrees; wrote %s" % (ang, a.out))


# ---------------------------------------------------------------------------- mask
def cmd_mask(a):
    im = cv2.imread(a.front)
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    V = hsv[..., 2].astype(int)
    col = colour_mask(im, hue_range(a.hue), a.sv[0], a.sv[1], a.smax, a.vmax)
    box = np.zeros_like(col)
    if a.box:
        x0, y0, x1, y1 = a.box
        box[y0:y1, x0:x1] = 255
    else:
        box[:] = 255
    col &= box
    ins = col.copy()
    if a.tube > 0:
        # pale glass over the colour: unlit tubes read white, and belong to the opening they cross
        near = cv2.dilate(col, ell(a.near))
        ins |= (((V > a.tube) & (near > 0)).astype(np.uint8) * 255) & box
    ins = cv2.morphologyEx(ins, cv2.MORPH_CLOSE, ell(a.close))
    if a.dark > 0:
        # black is never inside: the returns seen from the side, the gaps between cans
        dark = (V < a.dark).astype(np.uint8) * 255
        dark = cv2.morphologyEx(dark, cv2.MORPH_OPEN, ell(7))
        ins[cv2.dilate(dark, np.ones((3, 3), np.uint8)) > 0] = 0
    ins = cv2.morphologyEx(ins, cv2.MORPH_OPEN, ell(a.open))
    out = keep_big(ins, a.min_area)
    inv = 255 - out
    n, lab, st, _ = cv2.connectedComponentsWithStats(inv, 4)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] < a.fill:
            out[lab == i] = 255
    out = (cv2.GaussianBlur(out, (0, 0), a.blur) > 127).astype(np.uint8) * 255
    cv2.imwrite(a.out, out)
    ps = parts(out)
    print("wrote %s: %d part(s) (x, y, w, h, area): %s" % (a.out, len(ps), ps))
    if a.overlay:
        ov = im.copy()
        cs, _ = cv2.findContours(out, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(ov, cs, -1, (0, 255, 0), 2)
        cv2.imwrite(a.overlay, ov)


# ---------------------------------------------------------------------------- cut
def cmd_cut(a):
    m = cv2.imread(a.mask, 0)
    for ln in a.lines.split(";"):
        x0, y0, x1, y1 = rect(ln)
        cv2.line(m, (x0, y0), (x1, y1), 0, a.width)
    cv2.imwrite(a.out, m)
    ps = parts(m)
    print("wrote %s: %d part(s) (x, y, w, h, area): %s" % (a.out, len(ps), ps))


# ---------------------------------------------------------------------------- zoom
def cmd_zoom(a):
    im = cv2.imread(a.front)
    x0, y0, x1, y1 = a.rect
    f = a.factor
    c = cv2.resize(im[y0:y1, x0:x1], None, fx=f, fy=f, interpolation=cv2.INTER_CUBIC)
    for path, col in ((a.mask, (0, 255, 0)), (a.mask2, (0, 255, 255))):
        if path:
            mm = cv2.resize(cv2.imread(path, 0)[y0:y1, x0:x1], None, fx=f, fy=f, interpolation=cv2.INTER_NEAREST)
            cs, _ = cv2.findContours(mm, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
            cv2.drawContours(c, cs, -1, col, 1)
    g = a.grid
    for gx in range(x0 - x0 % g + g, x1, g):
        cv2.line(c, ((gx - x0) * f, 0), ((gx - x0) * f, 12), (255, 255, 255), 1)
        cv2.putText(c, str(gx), ((gx - x0) * f + 2, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
    for gy in range(y0 - y0 % g + g, y1, g):
        cv2.line(c, (0, (gy - y0) * f), (12, (gy - y0) * f), (255, 255, 255), 1)
        cv2.putText(c, str(gy), (14, (gy - y0) * f + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
    cv2.imwrite(a.out, c)
    print("wrote %s (%d x %d): labels are the picture's own pixel coordinates" % (a.out, c.shape[1], c.shape[0]))


def pair(s):
    v = [int(t) for t in s.split(",")]
    if len(v) != 2:
        raise argparse.ArgumentTypeError("two numbers: saturation,value")
    return v


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("front", help="register a sharp oblique photo to a square-on photo of the same sign")
    p.add_argument("--oblique", required=True, help="the sharp photo, taken from an angle")
    p.add_argument("--orect", type=rect, required=True, help="the coloured part's box in it, with a little margin")
    p.add_argument("--frontal", required=True, help="the square-on photo (may be small and soft)")
    p.add_argument("--frect", type=rect, required=True, help="the same part's box in the square-on photo")
    p.add_argument("--hue", default="red", help="the part's colour: %s, or lo,hi" % ", ".join(HUES))
    p.add_argument("--osv", type=pair, default=[70, 70], help="least saturation,value in the oblique photo")
    p.add_argument("--fsv", type=pair, default=[110, 110], help="least saturation,value in the square-on photo")
    p.add_argument("--canvas", type=rect, help="what to show, in the square-on photo's pixels (default: frect plus a fifth)")
    p.add_argument("--scale", type=float, default=8.0, help="output pixels per square-on-photo pixel")
    p.add_argument("--overlay", help="write the two masks overlaid here (yellow where they agree)")
    p.add_argument("--out", required=True)
    p.set_defaults(fn=cmd_front)

    p = sub.add_parser("quad", help="square up one photo from four corners of a rectangle on the sign's plane")
    p.add_argument("--photo", required=True)
    p.add_argument("--pts", required=True, help="top-left;top-right;bottom-right;bottom-left, each x,y")
    p.add_argument("--aspect", required=True, help="the rectangle's true width:height, e.g. 8.4:1")
    p.add_argument("--width", type=float, default=1200, help="the rectangle's width in the output, pixels")
    p.add_argument("--margin", type=float, default=0.25, help="space kept round it, as a fraction of its width")
    p.add_argument("--out", required=True)
    p.set_defaults(fn=cmd_quad)

    p = sub.add_parser("level", help="turn a squared-up picture so a part known to be level is level")
    p.add_argument("--front", required=True)
    p.add_argument("--hue", default="blue", help="the level part's colour")
    p.add_argument("--sv", type=pair, default=[60, 60])
    p.add_argument("--edge", choices=["bottom", "top"], default="bottom", help="which edge of it to fit")
    p.add_argument("--deg", type=float, help="turn by this many degrees instead (positive: counter-clockwise)")
    p.add_argument("--out", required=True)
    p.set_defaults(fn=cmd_level)

    p = sub.add_parser("mask", help="trace the parts of one colour into a clean mask")
    p.add_argument("--front", required=True)
    p.add_argument("--hue", default="red")
    p.add_argument("--sv", type=pair, default=[38, 57], help="least saturation,value (low enough to keep shadowed inner walls)")
    p.add_argument("--smax", type=int, default=255)
    p.add_argument("--vmax", type=int, default=255)
    p.add_argument("--tube", type=int, default=168, help="pale pixels brighter than this, near the colour, count as inside (0: off)")
    p.add_argument("--near", type=int, default=13, help="how near, pixels")
    p.add_argument("--dark", type=int, default=50, help="pixels darker than this are never inside (0: off)")
    p.add_argument("--close", type=int, default=7)
    p.add_argument("--open", type=int, default=7)
    p.add_argument("--min-area", type=int, default=5000, help="drop parts smaller than this")
    p.add_argument("--fill", type=int, default=1500, help="fill holes smaller than this (rust, electrodes); counters are bigger")
    p.add_argument("--blur", type=float, default=3.5, help="smoothing before the final threshold, pixels")
    p.add_argument("--box", type=rect, help="only look inside this box")
    p.add_argument("--overlay", help="write the photo with the mask's outline here, to check it by eye")
    p.add_argument("--out", required=True)
    p.set_defaults(fn=cmd_mask)

    p = sub.add_parser("cut", help="cut a mask along lines, where separate parts touch")
    p.add_argument("--mask", required=True)
    p.add_argument("--lines", required=True, help="x0,y0,x1,y1;x0,y0,x1,y1;...")
    p.add_argument("--width", type=int, default=6, help="the cut's width, pixels")
    p.add_argument("--out", required=True)
    p.set_defaults(fn=cmd_cut)

    p = sub.add_parser("zoom", help="a magnified crop with a coordinate grid and mask outlines")
    p.add_argument("--front", required=True)
    p.add_argument("--rect", type=rect, required=True)
    p.add_argument("--mask", help="outlined in green")
    p.add_argument("--mask2", help="outlined in yellow")
    p.add_argument("--factor", type=int, default=3)
    p.add_argument("--grid", type=int, default=50, help="a tick every this many pixels")
    p.add_argument("--out", required=True)
    p.set_defaults(fn=cmd_zoom)

    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
