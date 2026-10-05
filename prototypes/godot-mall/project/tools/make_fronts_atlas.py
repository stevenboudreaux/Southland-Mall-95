"""Pack the captured storefronts (tex/fronts/*.png, from capture_fronts.py) into
one atlas for the Godot mall: tex/fronts_atlas.png, and the UV rect of each
front written back into fronts.json ("uv": [u0, v0, u1, v1]).

The captures are 4x (128 px per 2 m tile, 600 px tall); the atlas holds them
at 2x (64 px per tile, 300 px tall), enough for signs to read in the hall and
small enough for phones. Anchors keep their own 3D fronts and are left out.
Run: python3 tools/make_fronts_atlas.py   (from the project folder)
"""
import json, os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.join(HERE, "..")
ATLAS_W = 4096
SCALE_DOWN = 2   # 4x captures -> 2x atlas
PAD = 2


def main():
    data = json.load(open(os.path.join(PROJ, "fronts.json")))
    fronts = data["fronts"]
    items = []
    for key, f in fronts.items():
        if f["anchor"]:
            f.pop("uv", None)
            continue
        im = Image.open(os.path.join(PROJ, "tex", "fronts", key + ".png")).convert("RGBA")
        im = im.resize((im.width // SCALE_DOWN, im.height // SCALE_DOWN), Image.BOX)
        items.append((key, im))
    items.sort(key=lambda kv: -kv[1].width)
    row_h = items[0][1].height
    # shelf packing: rows of equal height, widest first
    shelves = []   # [x_used]
    places = {}
    for key, im in items:
        for si, used in enumerate(shelves):
            if used + im.width + PAD <= ATLAS_W:
                places[key] = (used, si)
                shelves[si] = used + im.width + PAD
                break
        else:
            places[key] = (0, len(shelves))
            shelves.append(im.width + PAD)
    H = len(shelves) * (row_h + PAD)
    atlas_h = 1
    while atlas_h < H:
        atlas_h *= 2
    atlas = Image.new("RGBA", (ATLAS_W, atlas_h), (0, 0, 0, 0))
    for key, im in items:
        x, si = places[key]
        y = si * (row_h + PAD)
        atlas.paste(im, (x, y))
        fronts[key]["uv"] = [x / ATLAS_W, y / atlas_h, (x + im.width) / ATLAS_W, (y + im.height) / atlas_h]
    atlas.save(os.path.join(PROJ, "tex", "fronts_atlas.png"), optimize=True)
    data["atlas"] = {"file": "tex/fronts_atlas.png", "px": [ATLAS_W, atlas_h], "px_per_tile": 32 * (4 // SCALE_DOWN)}
    json.dump(data, open(os.path.join(PROJ, "fronts.json"), "w"), indent=1)
    print("atlas", ATLAS_W, "x", atlas_h, "rows", len(shelves), "fronts", len(items))


if __name__ == "__main__":
    main()
