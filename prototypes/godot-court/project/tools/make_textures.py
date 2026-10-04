"""Procedural textures for the Godot court proof.

Every texture is generated here so the look can be tuned by editing numbers,
and nothing is copied from photos. Colors are sampled by eye from the 2018
walkthrough frames (0:16 court floor, 0:22 hall floor, 0:36 court vault).
Run: python3 tools/make_textures.py   (writes into tex/)
"""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(__file__), "..", "tex")
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(7)
PX = 128  # pixels per metre for floors


def hexc(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


def speckle(img, amt=10.0, scale=1.0):
    """Terrazzo-like grain: fine noise plus sparse chips."""
    h, w, _ = img.shape
    n = rng.normal(0, amt, (h, w, 1)).astype(np.float32)
    img = img + n
    chips = rng.random((h, w)) < 0.004 * scale
    img[chips] *= rng.uniform(0.75, 1.15, (chips.sum(), 1)).astype(np.float32)
    return img


def soft_mottle(h, w, amt, blur):
    m = Image.fromarray((rng.random((h // 8, w // 8)) * 255).astype(np.uint8))
    m = m.resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(blur))
    return (np.asarray(m, dtype=np.float32)[..., None] / 255.0 - 0.5) * amt


def save(arr, name):
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(os.path.join(OUT, name))
    print("wrote", name)


def diag_checker(xm, zm, period, c1, c2):
    """Diagonal (45 deg) checkerboard; period = diagonal repeat along an axis."""
    u = (xm + zm) / period
    v = (xm - zm) / period
    m = ((np.floor(u) + np.floor(v)) % 2 == 0)
    return np.where(m[..., None], c1, c2), u, v


def grout_lines(u, v, width_frac):
    fu = np.abs(u - np.round(u))
    fv = np.abs(v - np.round(v))
    return (np.minimum(fu, fv) < width_frac)


# ------------------------------------------------------------------ hall floor
# 12 m wide (x) by 6 m long (z), tiles along z. Plank lanes 3 m each side,
# charcoal border strips, taupe/cream diagonal checker in the 6 m centre band.
def hall_floor():
    W, L = 12.0, 6.0
    w, h = int(W * PX), int(L * PX)
    xs = (np.arange(w) + 0.5) / PX
    zs = (np.arange(h) + 0.5) / PX
    X, Z = np.meshgrid(xs, zs)
    img = np.zeros((h, w, 3), np.float32)
    # plank lanes: 0.30 x 0.60 m beige tiles laid lengthwise, running bond
    plank = hexc("#d9c7a8")
    grout = hexc("#a8977c")
    col = np.floor(X / 0.30)
    row = np.floor((Z + (col % 2) * 0.30) / 0.60)
    tone = (np.sin(col * 12.9898 + row * 78.233) * 43758.5453) % 1.0
    img[:] = plank * (0.94 + 0.08 * tone[..., None])
    gx = np.abs(X / 0.30 - np.round(X / 0.30)) * 0.30 < 0.004
    gz = np.abs((Z + (col % 2) * 0.30) / 0.60 - np.round((Z + (col % 2) * 0.30) / 0.60)) * 0.60 < 0.004
    img[gx | gz] = grout
    # centre band 3..9 m
    band = (X > 3.0) & (X < 9.0)
    period = 0.75
    chk, u, v = diag_checker(X - 3.0, Z, period, hexc("#efe6d2"), hexc("#8f7c66"))
    img[band] = chk[band]
    gl = grout_lines(u, v, 0.006 / period * 2)
    img[band & gl] = hexc("#b9ab94")
    # charcoal border strips 0.18 m
    bord = ((X > 2.82) & (X <= 3.0)) | ((X >= 9.0) & (X < 9.18))
    img[bord] = hexc("#3a3734")
    img = speckle(img, 5.0)
    img += soft_mottle(h, w, 10, 6)
    save(img, "floor_hall.png")


# ----------------------------------------------------------------- court floor
# 14 m (x) by 16 m (z). 1.2 m plank perimeter, then a charcoal border band with
# cream inserts, then blue-grey / cream diagonal checker (0:16 frame).
def court_floor():
    W, L = 16.0, 16.0
    w, h = int(W * PX), int(L * PX)
    xs = (np.arange(w) + 0.5) / PX
    zs = (np.arange(h) + 0.5) / PX
    X, Z = np.meshgrid(xs, zs)
    img = np.zeros((h, w, 3), np.float32)
    plank = hexc("#d9c7a8")
    col = np.floor(X / 0.30)
    row = np.floor((Z + (col % 2) * 0.30) / 0.60)
    tone = (np.sin(col * 12.9898 + row * 78.233) * 43758.5453) % 1.0
    img[:] = plank * (0.94 + 0.08 * tone[..., None])
    gx = np.abs(X / 0.30 - np.round(X / 0.30)) * 0.30 < 0.004
    gz = np.abs((Z + (col % 2) * 0.30) / 0.60 - np.round((Z + (col % 2) * 0.30) / 0.60)) * 0.60 < 0.004
    img[gx | gz] = hexc("#a8977c")
    m0, bw = 1.6, 0.9  # perimeter margin, border band width
    d = np.minimum.reduce([X - m0, W - m0 - X, Z - m0, L - m0 - Z])
    inner = d > bw
    border = (d > 0) & ~inner
    period = 0.80
    chk, u, v = diag_checker(X - W / 2, Z - L / 2, period, hexc("#e9e3d3"), hexc("#7d8ea3"))
    img[inner] = chk[inner]
    img[inner & grout_lines(u, v, 0.012)] = hexc("#b6b2a6")
    img[border] = hexc("#3b3a3d")
    # cream square inserts set diagonally in the border, every 1.5 m
    along = np.where(np.minimum(X - m0, W - m0 - X) < np.minimum(Z - m0, L - m0 - Z), Z, X)
    t = (along % 1.5) - 0.75
    across = d - bw / 2
    ins = border & (np.abs(t) + np.abs(across) < 0.26)
    img[ins] = hexc("#ece4d0")
    # thin cream pinstripes either side of the band
    pin = ((np.abs(d - 0.05) < 0.02) | (np.abs(d - (bw - 0.05)) < 0.02))
    img[pin] = hexc("#d8d0bd")
    img = speckle(img, 4.5)
    img += soft_mottle(h, w, 8, 6)
    save(img, "floor_court.png")


# ------------------------------------------------------------- corridor floor
# Entrance corridor (12 m wide x 6 m tile), same as hall but with a salmon
# border row and a diamond medallion (2:28 frame) every tile.
def corridor_floor():
    hall_floor()
    img = np.asarray(Image.open(os.path.join(OUT, "floor_hall.png")), np.float32)
    h, w, _ = img.shape
    xs = (np.arange(w) + 0.5) / PX
    zs = (np.arange(h) + 0.5) / PX
    X, Z = np.meshgrid(xs, zs)
    for cx in (1.5, 10.5):
        dmd = (np.abs(X - cx) + np.abs(Z - 3.0)) < 0.45
        img[dmd] = hexc("#c98a73")
        img[(np.abs(X - cx) + np.abs(Z - 3.0) < 0.47) & ~dmd] = hexc("#3a3734")
        img[(np.abs(X - cx) + np.abs(Z - 3.0)) < 0.18] = hexc("#3a3734")
    save(img, "floor_corridor.png")


# ------------------------------------------------------------------- plaster
def plaster():
    s = 512
    base = hexc("#c9b48f")
    img = np.zeros((s, s, 3), np.float32) + base
    img += soft_mottle(s, s, 18, 10)
    img += rng.normal(0, 3, (s, s, 1))
    # make tileable by blending with a half-shifted copy
    sh = np.roll(np.roll(img, s // 2, 0), s // 2, 1)
    yy, xx = np.mgrid[0:s, 0:s] / s
    wgt = (np.minimum(np.minimum(xx, 1 - xx), np.minimum(yy, 1 - yy)) * 4).clip(0, 1)[..., None]
    img = img * wgt + sh * (1 - wgt)
    save(img, "plaster.png")


def stone():
    s = 512
    img = np.zeros((s, s, 3), np.float32) + hexc("#8e8a85")
    img = speckle(img, 14, 6)
    img += soft_mottle(s, s, 22, 4)
    save(img, "stone.png")


def wood():
    s = 512
    yy, xx = np.mgrid[0:s, 0:s].astype(np.float32)
    g = np.sin(xx / s * 60 + np.sin(yy / s * 9) * 3 + soft_mottle(s, s, 6, 8)[..., 0]) * 0.5 + 0.5
    base = hexc("#4a2e1d")
    img = base * (0.75 + 0.35 * g[..., None])
    img += rng.normal(0, 3, (s, s, 1))
    save(img, "wood_dark.png")


# --------------------------------------------------------------- foliage
def palm_frond():
    """One frond: a midrib with drooping leaflets, on transparent background."""
    w, h = 256, 1024
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = w // 2
    for i in range(46):
        t = i / 45.0
        y = int(40 + t * (h - 80))
        ln = int((1 - abs(t - 0.35) * 1.2) * 118)
        ln = max(ln, 16)
        g = int(95 + 60 * rng.random())
        colr = (int(40 + 30 * rng.random()), g, int(35 + 20 * rng.random()), 255)
        for side in (-1, 1):
            tipx = cx + side * ln
            tipy = y + int(ln * 0.55)
            d.polygon([(cx, y - 4), (tipx, tipy), (tipx - side * 3, tipy + 2), (cx, y + 7)], fill=colr)
    d.line([(cx, 0), (cx, h)], fill=(110, 120, 60, 255), width=5)
    im = im.filter(ImageFilter.SMOOTH)
    im.save(os.path.join(OUT, "palm_frond.png"))
    print("wrote palm_frond.png")


def leaf_cluster(name, leaf, center, n=34):
    s = 512
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i in range(n):
        a = rng.random() * math.tau
        r = 60 + rng.random() * 170
        L = 70 + rng.random() * 70
        x0, y0 = s / 2 + math.cos(a) * r * 0.3, s / 2 + math.sin(a) * r * 0.3
        x1, y1 = x0 + math.cos(a) * L, y0 + math.sin(a) * L
        nx, ny = -math.sin(a) * L * 0.22, math.cos(a) * L * 0.22
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        k = 0.8 + 0.35 * rng.random()
        c = tuple(int(min(255, v * k)) for v in leaf) + (255,)
        d.polygon([(x0, y0), (mx + nx, my + ny), (x1, y1), (mx - nx, my - ny)], fill=c)
    if center:
        for i in range(14):
            x, y = s / 2 + rng.normal(0, 14), s / 2 + rng.normal(0, 14)
            d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=center + (255,))
    im = im.filter(ImageFilter.SMOOTH)
    im.save(os.path.join(OUT, name))
    print("wrote", name)


# ------------------------------------------------------------ store interiors
def interior(name, colors, wall="#f3eee4"):
    """Back wall of a lit store: shelving with product blocks in the store's colors."""
    w, h = 1024, 512
    im = Image.new("RGB", (w, h), wall)
    d = ImageDraw.Draw(im)
    cols = [tuple(int(c) for c in hexc(x)) for x in colors] or [(200, 60, 60)]
    # shelves
    for sy in (150, 270, 390):
        d.rectangle([0, sy, w, sy + 8], fill=(150, 140, 125))
        x = 8
        while x < w - 20:
            bw = int(18 + rng.random() * 34)
            bh = int(40 + rng.random() * 60)
            c = cols[int(rng.random() * len(cols))]
            k = 0.8 + 0.3 * rng.random()
            c = tuple(min(255, int(v * k)) for v in c)
            d.rectangle([x, sy - bh, x + bw, sy], fill=c)
            x += bw + int(4 + rng.random() * 10)
    # display racks at floor
    for i in range(6):
        x = 60 + i * 160
        c = cols[i % len(cols)]
        d.rectangle([x, 430, x + 90, 512], fill=tuple(int(v * 0.9) for v in c))
    im = im.filter(ImageFilter.GaussianBlur(1.2))  # seen through glass, slightly soft
    im.save(os.path.join(OUT, name))
    print("wrote", name)


if __name__ == "__main__":
    court_floor()
    corridor_floor()
    hall_floor()
    plaster()
    stone()
    wood()
    palm_frond()
    leaf_cluster("poinsettia.png", (190, 22, 30), (230, 200, 60))
    leaf_cluster("leafy.png", (52, 120, 48), None, 44)
    import json
    for name, cols in json.load(open(os.path.join(os.path.dirname(__file__), "stores.json"))).items():
        interior("int_" + name + ".png", cols)
