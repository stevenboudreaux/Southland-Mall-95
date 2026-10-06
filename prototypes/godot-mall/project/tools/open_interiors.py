"""Opens the customer areas of fully built stores in layout_mall.json's walk grid.

convert_map.py marks every store tile as blocked; stores built in full 3D
(design/storefronts/*.md) let the player walk in. Each entry lists the map
tiles (x, y ranges, inclusive) that become floor; the furniture and counters
are obstacles placed by the store's builder. Run after convert_map.py:
  python3 tools/open_interiors.py   (from the project folder)
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.join(HERE, "..")
OPEN = {
    # Corn Dog 7 (s54, tiles x 79-84, y 134-139, faces west): the queue in front
    # of the counter, and the dining room along the north wall (it runs behind the mall wall)
    "s54": [(79, 80, 134, 139), (81, 84, 134, 136)],
}


def main():
    p = os.path.join(PROJ, "layout_mall.json")
    L = json.load(open(p))
    rows = [list(r) for r in L["walk"]]
    n = 0
    for sid, rects in OPEN.items():
        for (x0, x1, y0, y1) in rects:
            for y in range(y0, y1 + 1):
                for x in range(x0, x1 + 1):
                    if rows[y][x] != "1":
                        rows[y][x] = "1"
                        n += 1
    L["walk"] = ["".join(r) for r in rows]
    L["interiors_open"] = sorted(OPEN.keys())
    json.dump(L, open(p, "w"), indent=1)
    print("opened", n, "tiles for", list(OPEN))


if __name__ == "__main__":
    main()
