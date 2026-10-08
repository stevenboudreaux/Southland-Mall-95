"""Steven's layout changes of Oct 8, 2026, made to layout_mall.json in place (edges, stores,
leftovers, walk grid). Safe to run again. Run after convert_map.py, open_interiors.py and
narrow_stores.py:
  python3 tools/layout_oct8.py   (from the project folder)

- Orange Julius (s34) moves up into line with Tee Tai's (the 1994 directory: 52 sits flush with
  51), its front at z = 6 from x = 12 to 16; Franks (s33) takes the court's south wall from x = 2
  to 12 and keeps its corner on the east hall. The alcove that stood in front of Orange Julius
  (a leftover, x 12..16, z 6..10) is now the shop; its side on the court is plain wall.
- The corner right of Babbage's (JCPenney court): the 1994 directory draws one diagonal from
  Babbage's (81) to the south exit hall, with Gold 'n' Gifts (82) on it; Steven's marked-up
  screenshot draws the frontage as one straight line from Babbage's pier to the court column,
  turning the corner there. The staircase of 2 m steps (Babbage's 2 m jog and Gold 'n' Gifts'
  two fronts) becomes one 45-degree front from (-130, 60) to (-136, 66), Gold 'n' Gifts on it,
  with a 2 m return wall down to the corner by Corn Dog 7. Babbage's keeps its 6 m front.
- The Coming Soon stall (cs1) is plain mall wall.
- Franks and Duncan Sports lose the generic sign box (their own signs are built instead).
"""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "layout_mall.json")
R2 = round(math.sqrt(0.5), 6)


def same(e, a, b):
    return [round(v, 2) for v in e["a"]] == a and [round(v, 2) for v in e["b"]] == b


def main():
    L = json.load(open(P))
    E = L["edges"]
    out = []
    for e in E:
        # old pieces of the stepped corner, the jog, the alcove's side, the old fronts
        if e.get("store") == "n39":
            continue
        if e.get("store") == "n39b" and same(e, [-132.0, 62.0], [-130.0, 62.0]):
            continue
        if e["kind"] == "wall" and (same(e, [-132.0, 62.0], [-132.0, 64.0]) or same(e, [-130.0, 60.0], [-130.0, 62.0])
                                    or same(e, [16.0, 6.0], [16.0, 10.0]) or same(e, [12.0, 6.0], [12.0, 10.0])
                                    or same(e, [-136.0, 66.0], [-136.0, 68.0])):
            continue
        if e.get("store") == "cs1":
            e = {"a": e["a"], "b": e["b"], "n": e["n"], "kind": "wall"}
        if e.get("store") == "s33":
            e["a"], e["b"] = [2.0, 10.0], [12.0, 10.0]
        if e.get("store") == "s34":
            e["a"], e["b"], e["depth"] = [12.0, 6.0], [16.0, 6.0], 10.0
        if e.get("store") == "n39b" and same(e, [-130.0, 60.0], [-124.0, 60.0]):
            e["depth"] = 8.0
        out.append(e)
    out.append({"a": [12.0, 6.0], "b": [12.0, 10.0], "n": [-1, 0], "kind": "wall"})
    out.append({"a": [-136.0, 66.0], "b": [-130.0, 60.0], "n": [-R2, -R2], "kind": "store", "store": "n39", "depth": 6.0})
    out.append({"a": [-136.0, 66.0], "b": [-136.0, 68.0], "n": [-1, 0], "kind": "wall"})
    L["edges"] = out
    S = L["stores"]
    S["s33"]["awning"] = False
    S["s33"]["noSign"] = True      # the neon is the sign (tools/stores/franks)
    S["s28"]["noSign"] = True      # Duncan Sports: the ad's script is the sign (make_duncan.py)
    # floor patches: the alcove goes; the staircase's patches become one triangle
    drop = [[12.0, 6.0, 16.0, 10.0], [-136.0, 60.0, -130.0, 62.0], [-136.0, 62.0, -132.0, 64.0], [-136.0, 64.0, -134.0, 66.0]]
    L["leftovers"] = [r for r in L["leftovers"] if [float(v) for v in r] not in drop]
    L["leftover_tris"] = [[[-136.0, 60.0], [-130.0, 60.0], [-136.0, 66.0]]]
    # walk grid (2 m tiles: tx = x / 2 + 148, ty = z / 2 + 100)
    W = [list(r) for r in L["walk"]]
    def setw(tx, ty, v):
        W[ty][tx] = v
    for ty in (105, 106, 107):
        setw(153, ty, "0")                       # x 10..12 behind Franks' new front
    for tx, ty in [(80, 130), (81, 130), (82, 130), (80, 131), (81, 131), (80, 132)]:
        setw(tx, ty, "1")                        # in front of the diagonal (the cut tiles are
                                                 # closed by obstacles along the glass)
    for tx, ty in [(82, 131), (82, 132), (82, 133), (81, 132), (80, 133), (81, 133)]:
        setw(tx, ty, "0")                        # behind it: Gold 'n' Gifts, Babbage's old jog
    L["walk"] = ["".join(r) for r in W]
    if "interiors_open" in L and "cs1" in L["interiors_open"]:
        L["interiors_open"].remove("cs1")
    json.dump(L, open(P, "w"), indent=1)
    print("edges", len(out), "leftovers", len(L["leftovers"]))


if __name__ == "__main__":
    main()
