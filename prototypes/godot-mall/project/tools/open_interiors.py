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
    # Pocket Change (s52b, tiles x 93-96, y 130-149, faces north): the whole arcade
    "s52b": [(93, 96, 130, 149)],
    # Kay-Bee Toys (s18, tiles x 131-142, y 71-73, faces east): the whole store
    "s18": [(131, 142, 71, 73)],
    # Gumballs (s8, tiles x 138-142, y 118-123, a corner open to the east hall and the
    # Dillard's court): the whole store
    "s8": [(138, 142, 118, 123)],
    # JW (n33, tiles x 108-110, y 110-123) and 5-7-9 (n33b, x 111-113), side by side on the
    # Concourse's north side, facing south; County Seat (n46, x 101-104, y 130-149) facing north
    "n33": [(108, 110, 110, 123)],
    "n33b": [(111, 113, 110, 123)],
    "n46": [(101, 104, 130, 149)],
    # Babbage's (n39b, tiles x 83-85, y 130-133, faces north, by Corn Dog 7; the 2 m jog on
    # its right is x 82, y 131-133) and Sound Shop (s19, x 131-142, y 68-70, faces east,
    # beside Kay-Bee): the whole stores (design/storefronts/babbages.md, sound-shop.md)
    "n39b": [(83, 85, 130, 133), (82, 82, 131, 133)],
    "s19": [(131, 142, 68, 70)],
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
