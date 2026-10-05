"""The storefront accuracy meter (STOREFRONT-FIDELITY.md, section 2) from what
is on record today: the live game's own storefront notes (facade_notes.json,
which say what each hand-built front was drawn from) and the published photo
boards (photos.json). Writes facade_records.json (one record per store with
its level and the photo that would raise it) and the most-wanted list,
production/storefront-most-wanted.md.

Levels: 0 placeholder (generic front from the map's colours), 1 sign-accurate
(hand-built, source not stated or from memory), 2 facade-accurate (built from
a photo), 3 depth-accurate (built from several photos; Steven to confirm one
is angled), 4 verified (dated photo + a second person's confirmation; none yet).
Run: python3 tools/facade_meter.py   (from the project folder)
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.join(HERE, "..")
ROOT = os.path.abspath(os.path.join(PROJ, "..", "..", ".."))
LEVEL_NAME = {0: "placeholder", 1: "sign-accurate", 2: "facade-accurate", 3: "depth-accurate", 4: "verified"}
BY_SOURCE = {"photos": 3, "photo": 2, "memory": 1, "description": 1, "unstated": 1}
NOT_STORES = {"", "EXIT", "MAIN ENTRANCE", "MEN", "WOMEN"}


def slug(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())


def main():
    L = json.load(open(os.path.join(PROJ, "layout_mall.json")))
    notes = json.load(open(os.path.join(PROJ, "facade_notes.json")))
    photos = json.load(open(os.path.join(ROOT, "photos.json"))).get("photos", [])
    board = {}
    for p in photos:
        board.setdefault(p["store"], []).append(p["file"])
    frontage = {}
    for e in L["edges"]:
        if e["kind"] == "store":
            Ln = ((e["b"][0] - e["a"][0]) ** 2 + (e["b"][1] - e["a"][1]) ** 2) ** 0.5
            frontage[e["store"]] = frontage.get(e["store"], 0.0) + Ln
    records = {}
    for sid, s in L["stores"].items():
        name = s["name"]
        if name in NOT_STORES or s["vacant"]:
            continue
        note = notes.get(name)
        level = BY_SOURCE[note["source"]] if note else 0
        photos_here = board.get(slug(name), [])
        ask = {0: "a straight-on photo of the front (sign and entrance)",
               1: "a readable photo of the sign, and a straight-on photo of the front",
               2: "a photo of the front taken from an angle (shows the entrance depth and the sign's projection)",
               3: "the year of the photos it was built from, and a second person's confirmation",
               4: None}[level]
        records[sid] = {
            "name": name, "level": level, "level_name": LEVEL_NAME[level],
            "source": note["source"] if note else "none", "anchor": bool(s["anchor"]),
            "frontage_m": round(frontage.get(sid, 0.0), 1),
            "board_photos": photos_here,
            "note": (note["note"][:240] if note else ""),
            "ask": ask,
        }
    out = {"levels": LEVEL_NAME, "year_map": L.get("era"), "stores": records}
    json.dump(out, open(os.path.join(PROJ, "facade_records.json"), "w"), indent=1)

    want = sorted(records.values(), key=lambda r: (r["level"], -r["frontage_m"], r["name"]))
    counts = {k: sum(1 for r in records.values() if r["level"] == k) for k in LEVEL_NAME}
    lines = ["# Storefronts: most wanted photos (1995 map)", "",
             "From `prototypes/godot-mall/project/facade_records.json` (tools/facade_meter.py). "
             "The level says how well each storefront is sourced, not how it looks; a photo moves a store up.", "",
             "| Level | Stores |", "|---|---|"]
    for k, nm in LEVEL_NAME.items():
        lines.append("| %d %s | %d |" % (k, nm, counts[k]))
    lines += ["", "## Most wanted (lowest level first, biggest frontage first)", "",
              "| # | Store | Level | Frontage | What would raise it | Photos on its board |", "|---|---|---|---|---|---|"]
    for i, r in enumerate(want, 1):
        if r["level"] >= 4:
            continue
        lines.append("| %d | %s | %d %s | %.0f m | %s | %s |" % (
            i, r["name"], r["level"], r["level_name"], r["frontage_m"], r["ask"],
            ("%d (not yet used)" % len(r["board_photos"])) if r["board_photos"] else "none"))
    os.makedirs(os.path.join(ROOT, "production"), exist_ok=True)
    open(os.path.join(ROOT, "production", "storefront-most-wanted.md"), "w").write("\n".join(lines) + "\n")
    print("stores", len(records), "levels", counts)


if __name__ == "__main__":
    main()
