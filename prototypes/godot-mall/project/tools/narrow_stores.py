"""Narrows store frontages that the 1995 map draws too wide (Steven's marked-up screenshots,
Oct 7, 2026: a yellow line on each front showing how much to keep), keeping every hall's length:
the room freed goes to a closed "Coming Soon" stall when it is about 3 m or more, else to plain
wall between the neighbours. Edits layout_mall.json in place (edges, stores, walk grid); safe to
run again. Run after convert_map.py and open_interiors.py:
  python3 tools/narrow_stores.py   (from the project folder)

- Lion's Share (n36, 12 m): keeps the doorway and the crest, 9.3 m (the lines kept 2.0..11.3 m).
- Wicks 'N' Sticks (s44, 6 m): loses about 1 m on its west side, 5 m.
- The 3.7 m between them becomes the Coming Soon stall (cs1).
- Radio Shack (s21b, 8 m): loses 1.6 m at its south end, 6.4 m; the 1.6 m is plain wall next to GNC.
- Champs Sports and Sports Avenue are closed to walking (their tiles shut).
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "layout_mall.json")

# store id -> new frontage (a, b) in metres
FRONTS = {"n36": ([-50.0, 48.0], [-40.7, 48.0]), "s44": ([-37.0, 48.0], [-32.0, 48.0]), "s21b": ([2.0, 26.0], [2.0, 32.4])}
NEW_STALLS = [{"id": "cs1", "a": [-40.7, 48.0], "b": [-37.0, 48.0], "n": [0, 1], "depth": 4.0}]
NEW_WALLS = [{"a": [2.0, 32.4], "b": [2.0, 34.0], "n": [-1, 0]}]
# map tiles (x0, x1, y0, y1 inclusive) no longer walkable: the parts of Lion's Share and Wicks
# that are now the stall (or the stores' cut-down edges), Radio Shack's south end
CLOSE = [(127, 129, 118, 123), (149, 156, 116, 116),
         # Champs Sports (s49) and Sports Avenue (s8b) are shut for now (Steven, Oct 7: "I don't
         # want to walk in yet"): seen through the glass, not walked into
         (87, 92, 112, 123), (135, 137, 118, 123)]


def main():
    L = json.load(open(P))
    for e in L["edges"]:
        if e.get("store") in FRONTS:
            e["a"], e["b"] = FRONTS[e["store"]]
    for st in NEW_STALLS:
        if st["id"] not in L["stores"]:
            L["stores"][st["id"]] = {"name": "COMING SOON", "sign": "Coming Soon", "bg": "#efe8da", "fg": "#5b2a3a", "merch": ["#cccccc"],
                                     "anchor": False, "vacant": True, "unit": None, "open": False, "awning": False, "awningColor": None,
                                     "entry": None, "plain": False, "noSign": False, "carpet": None, "font": "serif", "has_front_image": False}
        if not any(e.get("store") == st["id"] for e in L["edges"]):
            L["edges"].append({"a": st["a"], "b": st["b"], "n": st["n"], "kind": "store", "store": st["id"], "depth": st["depth"]})
    for w in NEW_WALLS:
        if not any(e["kind"] == "wall" and e["a"] == w["a"] and e["b"] == w["b"] for e in L["edges"]):
            L["edges"].append({"a": w["a"], "b": w["b"], "n": w["n"], "kind": "wall"})
    rows = [list(r) for r in L["walk"]]
    n = 0
    for (x0, x1, y0, y1) in CLOSE:
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if rows[y][x] == "1":
                    rows[y][x] = "0"
                    n += 1
    L["walk"] = ["".join(r) for r in rows]
    L["interiors_open"] = [i for i in L.get("interiors_open", []) if i not in ("s49", "s8b")]
    json.dump(L, open(P, "w"), indent=1)
    print("narrowed", list(FRONTS), "closed", n, "tiles")


if __name__ == "__main__":
    main()
