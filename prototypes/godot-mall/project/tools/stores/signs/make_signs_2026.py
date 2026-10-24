"""The 2026 store signs, generated from tools/stores/signs/y26/signs_2026.json (Demo 43, Oct 24 2026).

Each sign in the spec is what Steven's Oct 23 2026 footage shows on that unit's fascia: one or
more parts (a word set in a font, with the letter spacing, size and colours read off the frame,
or a shape traced from a mask in y26/src/), the letter type (closed-face channel letters, flat
cut letters, halo-lit, open neon, a lit cabinet), the cans' depth and the backer panel or raceway
behind them. For every part this writes y26/<id>_<part>_logo.json (channel.gd's letters.json
format, metres, baseline y = 0, x from 0) and tex/sg/y26/<id>_<part>_face.png + _glow.png; the
spec itself is read at build time by tools/stores/signs/sign_2026.gd (geometry and materials).

  python3 tools/stores/signs/make_signs_2026.py [id ...]   (from the project folder)

Fonts: a name from FONTS (the OFL files in tools/stores/signs/src/ and the system fonts the
cloud workspace has), or a path. Shapes: "trace": "<mask png in y26/src>" traces the white
pixels of a mask, "width" metres across (make the mask with photo_trace.py mask).
"""
import json, os, sys, glob
import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_logos as ML   # noqa: E402

Y26 = os.path.join(HERE, "y26")
SRC = os.path.join(HERE, "src")
TEX = os.path.join(HERE, "..", "..", "..", "tex", "sg", "y26")
os.makedirs(TEX, exist_ok=True)
ML.TEX = os.path.join(HERE, "..", "..", "..", "tex", "sg")

SYS = "/usr/share/fonts"


def _find(name):
    for root in (os.path.join(HERE, "y26", "src", "fonts"), SRC, SYS, "/usr/share/texmf/fonts"):
        hits = glob.glob(os.path.join(root, "**", name), recursive=True)
        if hits:
            return hits[0]
    return None


FONTS = {
    # in src/ (OFL)
    "bodoni": "BodoniModa-Bold.ttf", "coustard": "Coustard-Black.ttf", "francois": "FrancoisOne-Regular.ttf",
    "fredoka": "Fredoka-Bold.ttf", "josefin": "JosefinSans-Regular.ttf", "kaushan": "KaushanScript-Regular.ttf",
    "krona": "KronaOne-Regular.ttf", "oldstandard": "OldStandard-Bold.ttf", "poppins_black": "Poppins-Black.ttf",
    "sourcesans": "SourceSans3-Bold.ttf",
    # system
    "inter_black": "Inter-Black.otf", "inter_bold": "Inter-Bold.otf", "inter_semibold": "Inter-SemiBold.otf",
    "inter_medium": "Inter-Medium.otf", "inter": "Inter-Regular.otf", "inter_light": "Inter-Light.otf",
    "heros": "texgyreheros-regular.otf", "heros_bold": "texgyreheros-bold.otf", "heros_cn": "texgyreheroscn-bold.otf",
    "adventor": "texgyreadventor-bold.otf", "adventor_reg": "texgyreadventor-regular.otf",
    "bonum": "texgyrebonum-bold.otf", "chorus": "texgyrechorus-mediumitalic.otf",
    "pagella": "texgyrepagella-bold.otf", "schola": "texgyreschola-bold.otf", "termes": "texgyretermes-bold.otf",
    "caladea": "Caladea-Bold.ttf",
    "carlito": "Carlito-Bold.ttf", "dejavu_bold": "DejaVuSans-Bold.ttf", "dejavu_cn": "DejaVuSansCondensed-Bold.ttf",
    "liberation_serif_bold": "LiberationSerif-Bold.ttf", "liberation_serif": "LiberationSerif-Regular.ttf",
    "liberation_bold": "LiberationSans-Bold.ttf", "poppins": "Poppins-Medium.ttf", "poppins_reg": "Poppins-Regular.ttf",
    "poppins_bold": "Poppins-Bold.ttf",
}
# Any other font: put the file (an OFL font, with its licence) in y26/src/fonts/ and give its file name,
# e.g. "GreatVibes-Regular.ttf" from https://raw.githubusercontent.com/google/fonts/main/ofl/greatvibes/


def font_path(name):
    if os.path.exists(name):
        return name
    f = FONTS.get(name, name)
    p = _find(f)
    if p is None:
        raise SystemExit("font not found: " + name)
    return p


def _scale(L, k):
    f = lambda p: [round(p[0] * k, 5), round(p[1] * k, 5)]
    return [{"ch": l["ch"], "tris": [f(p) for p in l["tris"]], "loops": [[f(p) for p in lp] for lp in l["loops"]]} for l in L]


def _stretch(L, kx):
    f = lambda p: [round(p[0] * kx, 5), round(p[1], 5)]
    return [{"ch": l["ch"], "tris": [f(p) for p in l["tris"]], "loops": [[f(p) for p in lp] for lp in l["loops"]]} for l in L]


def part_letters(part):
    """The part's letters in metres, moved so x and y start at 0; returns (letters, w, h)."""
    if "trace" in part:
        m = cv2.imread(os.path.join(Y26, "src", part["trace"]), 0) > 127
        ys, xs = np.where(m)
        L = ML.trace_mask(m, part.get("text", "?" * 40), float(part["width"]), ys.max() + 1, smooth=float(part.get("smooth", 0.0)))
    else:
        L, _ = ML.set_text(font_path(part["font"]), part["text"], float(part["cap_h"]), float(part.get("track", 0.0)))
        if part.get("lower_scale"):
            # x-height letters scaled on their own (some fonts' lowercase runs tall or short)
            pass
    if part.get("stretch", 1.0) != 1.0:
        L = _stretch(L, float(part["stretch"]))
    if part.get("shear", 0.0):
        L = ML.shift(L, 0.0, 0.0, float(part["shear"]))
    x0, y0, x1, y1 = ML.bbox(L)
    L = ML.shift(L, -x0, -y0)
    return L, round(x1 - x0, 4), round(y1 - y0, 4)


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def build(sign):
    sid = sign["id"]
    out = []
    for part in sign["parts"]:
        pid = part["name"]
        L, w, h = part_letters(part)
        lid = "y26/%s_%s" % (sid, pid)
        glow = part.get("glow")
        lit = float(part.get("lit", 1.0))
        # no glow: a tiny pad (that texture is thrown away; a big pad on a small part takes minutes)
        pad = float(part.get("glow_pad", 0.25)) if glow else 0.01
        if glow:
            pad = min(pad, max(0.03, 0.6 * min(w, h)))
        ML.write(lid, part.get("text", pid), L, w, hexrgb(glow) if glow else (0, 0, 0), pad,
                 "2026: %s (%s)" % (sign["store"], sign.get("ref", "")), top=h, tex=True)
        if not glow:
            try:
                os.remove(os.path.join(ML.TEX, lid + "_glow.png"))
            except OSError:
                pass
        if lit <= 0.0 and not part.get("face_tex"):
            try:
                os.remove(os.path.join(ML.TEX, lid + "_face.png"))
            except OSError:
                pass
        out.append((pid, w, h))
    return out


def load_parts():
    """y26/parts/<id>.json, one sign each (written per sign so they can be worked on separately),
    merged into y26/signs_2026.json, which the game reads."""
    signs = []
    for f in sorted(glob.glob(os.path.join(Y26, "parts", "*.json"))):
        s = json.load(open(f))
        s.setdefault("id", os.path.splitext(os.path.basename(f))[0])
        signs.append(s)
    return {"note": "2026 store signs from Steven's Oct 23 2026 footage; built by tools/stores/signs/sign_2026.gd. "
                    "Edit y26/parts/<id>.json and run make_signs_2026.py.", "signs": signs}


def main(only=()):
    spec = load_parts()
    json.dump(spec, open(os.path.join(Y26, "signs_2026.json"), "w"), indent=1, ensure_ascii=False)
    n = 0
    for sign in spec["signs"]:
        if only and sign["id"] not in only:
            continue
        try:
            for pid, w, h in build(sign):
                print("  %s/%s: %.2f x %.2f m" % (sign["id"], pid, w, h))
            n += 1
        except (SystemExit, Exception) as ex:
            print("FAILED %s: %s" % (sign["id"], ex))
            sign["failed"] = str(ex)
    print("%d signs" % n)


if __name__ == "__main__":
    main(tuple(sys.argv[1:]))
