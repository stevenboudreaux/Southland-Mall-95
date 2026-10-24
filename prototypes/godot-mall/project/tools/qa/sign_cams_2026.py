"""Camera strings for tools/qa/unbaked_shots.gd (and wingshots.gd) that look straight at each 2026
store's sign: eye height 1.62 m, 6.5 m out from the front (less in narrow halls), tilted up to the
fascia band's centre (3.9 m). Prints one line per wing: "x,z,yaw,pitch:<name>;...".

  python3 tools/qa/sign_cams_2026.py [--only id,id] [--dist 6.5]
"""
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "..", "..")
SEAM = (-20.0, 48.0)


def main():
    only = None
    dist = 6.5
    args = sys.argv[1:]
    for i, a in enumerate(args):
        if a == "--only":
            only = set(args[i + 1].split(","))
        if a == "--dist":
            dist = float(args[i + 1])
    L = json.load(open(os.path.join(P, "layout_2026.json")))
    stores = L["stores"] if isinstance(L["stores"], dict) else {s.get("id", i): s for i, s in enumerate(L["stores"])}
    spec = json.load(open(os.path.join(P, "tools/stores/signs/y26/signs_2026.json")))
    sid_of = {}
    for s in spec["signs"]:
        sid_of[s["store"]] = s["id"]
        for al in s.get("aliases", []):
            sid_of[al] = s["id"]
    wings = {1: [], 2: []}
    seen = set()
    for e in L["edges"]:
        if e.get("kind") not in ("store", "restroom"):
            continue
        sd = stores.get(e["store"]) if isinstance(stores, dict) else stores[e["store"]]
        if sd is None or sd.get("name") not in sid_of:
            continue
        sid = sid_of[sd["name"]]
        if only and sid not in only:
            continue
        ax, az = e["a"]
        bx, bz = e["b"]
        nx, nz = e["n"]
        mx, mz = (ax + bx) / 2, (az + bz) / 2
        Ln = math.hypot(bx - ax, bz - az)
        d = min(dist, max(4.0, Ln * 0.9))
        cx, cz = mx + nx * d, mz + nz * d
        # Godot: rotation.y = yaw turns the camera's -Z toward (-sin yaw, -cos yaw)
        yaw = math.degrees(math.atan2(nx, nz))
        pitch = math.degrees(math.atan2(3.9 - 1.62, d))
        wing = 2 if (mz > SEAM[1] or mx < SEAM[0]) else 1
        name = sid if sid not in seen else "%s_%d" % (sid, len([k for k in seen if k.startswith(sid)]))
        seen.add(name)
        wings[wing].append("%.2f,%.2f,%.1f,%.1f:%s" % (cx, cz, yaw, pitch, name))
    for w in (1, 2):
        print("WING%d %s" % (w, ";".join(wings[w])))


if __name__ == "__main__":
    main()
