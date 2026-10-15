#!/usr/bin/env python3
"""The Stockrooms (Steven, Oct 15 2026): the yellow-hallway level behind Woolworth's back corner.

Writes scripts/stockrooms_map.json (the grid, seams, props) and a top-down preview PNG.
Design: design/godot-stockrooms.md. One cell = 1 m. '#' solid, '.' floor, 'X' the door home.

Four stations, each the same shape: an entry corridor from the south, a 13 m bay with four
column stubs, exits west, east and north. At each station one move is right:
  S1: east (right)   S2: east (right)   S3: the second door on the left of the east corridor
  S4: north (straight through) into the room with the stick.
Every wrong move leads, after a corner, into a straight corridor running north into a COPY of
that station's entry and bay; a seam in the copy's entry moves the player by a fixed offset into
the real entry, so the wrong way folds back on itself without a visible cut. Fog hides the copy's
short exit stubs. Backwards (home) is the same code reversed; the loops still catch wrong turns.

Usage: python3 tools/stockrooms/make_stockrooms.py [preview.png]
"""
import json, sys

W, H = 360, 300
G = [['#'] * W for _ in range(H)]
copies = []     # (station, cx, cy)
corridors = []  # (xc, y0, y1): long north-south runs that get rooms off them
seams = []      # {"rect": [x0, y0, x1, y1], "dx", "dy", "name"}
props = []      # {"kind", "x", "y", "rot"}
notes = {}

def carve(x0, y0, x1, y1, ch='.'):
    for y in range(min(y0, y1), max(y0, y1) + 1):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            G[y][x] = ch

def solid(x, y):
    G[y][x] = '#'

def hpath(x0, x1, yc):
    carve(x0, yc - 1, x1, yc + 1)

def vpath(xc, y0, y1):
    carve(xc - 1, y0, xc + 1, y1)

# ---- the station template (origin = its top-left), 39 x 40
def bay(ox, oy):
    carve(ox + 13, oy + 15, ox + 25, oy + 27)
    for cx, cy in [(16, 18), (22, 18), (16, 24), (22, 24)]:
        solid(ox + cx, oy + cy)

def station(ox, oy, exits=('W', 'E', 'N')):
    bay(ox, oy)
    vpath(ox + 19, oy + 28, oy + 39)                      # entry from the south
    if 'W' in exits: hpath(ox, ox + 12, oy + 21)
    if 'E' in exits: hpath(ox + 26, ox + 38, oy + 21)
    if 'N' in exits: vpath(ox + 19, oy, oy + 14)
    return {"ox": ox, "oy": oy, "W": (ox, oy + 21), "E": (ox + 38, oy + 21), "N": (ox + 19, oy),
            "S": (ox + 19, oy + 39)}

def copy_of(st, cx, cy, name):
    """A copy of station st's entry + bay with 5 m exit stubs, origin (cx, cy). Its entry's
    bottom is (cx+19, cy+39); a wrong path must arrive there heading north. The seam spans the
    entry's width 6 m short of the bay."""
    bay(cx, cy)
    vpath(cx + 19, cy + 28, cy + 39)
    hpath(cx + 8, cx + 12, cy + 21)
    hpath(cx + 26, cx + 30, cy + 21)
    # the north exit as long as the real one (what you see straight ahead from the seam), then east
    vpath(cx + 19, cy - 9, cy + 14)
    hpath(cx + 18, cx + 26, cy - 8)
    copies.append((st, cx, cy))
    seams.append({"name": name, "rect": [cx + 18, cy + 33, cx + 20, cy + 33],
                  "dx": st["ox"] - cx, "dy": st["oy"] - cy})
    return (cx + 19, cy + 39)

def side_room(x0, y0, x1, y1, door, furnish=True):
    """A plain room; door = (x0, y0, x1, y1) cells to open into the corridor."""
    carve(x0, y0, x1, y1)
    carve(*door)
    if furnish:
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        props.append({"kind": "table", "x": cx + 0.5, "y": cy + 0.5, "rot": 0})

# ---- placement (see the preview: stations in a row, S4 up and to the right)
S1 = station(30, 150)
S2 = station(110, 150)
S3 = station(190, 150)
S4 = station(280, 70)

# start room south of S1, the door home in its south wall
s1x, s1y = S1["S"]
carve(s1x - 6, s1y + 1, s1x + 6, s1y + 10)
for x in range(s1x - 1, s1x + 2):
    G[s1y + 11][x] = 'X'
props.append({"kind": "crate", "x": s1x + 4.5, "y": s1y + 8.5, "rot": 12})
notes["spawn"] = [s1x + 0.5, s1y + 8.0]          # just inside the door, facing north
notes["door"] = [s1x - 1, s1y + 11, s1x + 1, s1y + 11]

def loop_w(st, tag, cy=None):
    """West, then one long corridor north into a copy of this station."""
    ox, oy = st["ox"], st["oy"]
    x = ox - 4
    hpath(x - 1, ox, oy + 21)
    cy = oy - 70 if cy is None else cy
    top = copy_of(st, x - 19, cy, tag + "-W")
    vpath(x, top[1], oy + 22)
    corridors.append((x, top[1] + 2, oy + 18))

def loop_n(st, tag):
    """North, east, north into a second copy."""
    ox, oy = st["ox"], st["oy"]
    vpath(ox + 19, oy - 9, oy)
    hpath(ox + 18, ox + 45, oy - 8)
    top = copy_of(st, ox + 44 - 19, oy - 49, tag + "-N")
    vpath(ox + 44, top[1], oy - 7)

def link_east(a, b):
    """The right move at S1/S2: east, south, east, north into the next station's entry."""
    ax, ay = a["E"]
    bx, by = b["S"]
    hpath(ax, ax + 22, ay)
    vpath(ax + 22, ay, ay + 30)
    hpath(ax + 22, bx, ay + 30)
    vpath(bx, by, ay + 31)

loop_w(S1, "S1"); loop_n(S1, "S1")
link_east(S1, S2)
loop_w(S2, "S2"); loop_n(S2, "S2")
link_east(S2, S3)
props.append({"kind": "ladder", "x": S2["ox"] + 25.5, "y": S2["oy"] + 16.0, "rot": 90})   # landmark in S2's bay

# S3: west and north loop; the east corridor has rooms, and the 2nd on the left goes on
loop_w(S3, "S3"); loop_n(S3, "S3")
ex, ey = S3["E"]
hpath(ex, ex + 30, ey)
L = [(ex + 3, ey - 8, ex + 8, ey - 3), (ex + 13, ey - 8, ex + 18, ey - 3), (ex + 23, ey - 8, ex + 28, ey - 3)]
R = [(ex + 6, ey + 3, ex + 11, ey + 8), (ex + 18, ey + 3, ex + 23, ey + 8)]
for k, (x0, y0, x1, y1) in enumerate(L):
    side_room(x0, y0, x1, y1, (x0 + 2, y1 + 1, x0 + 3, ey - 2), furnish=(k != 1))
for (x0, y0, x1, y1) in R:
    side_room(x0, y0, x1, y1, (x0 + 2, ey + 2, x0 + 3, y0 - 1))
L2 = L[1]
props.append({"kind": "chair", "x": L2[0] + 1.5, "y": L2[1] + 1.5, "rot": 200})          # landmark in the room
# the corridor of rooms carries on east, south, back west under everything, and north into a copy
cx_end = ex + 30
cyb = 243 + 39
vpath(cx_end, ey, cyb + 8)
hpath(S3["ox"] + 18, cx_end + 1, cyb + 8)
copy_of(S3, S3["ox"], 243, "S3-E")
vpath(S3["ox"] + 19, cyb, cyb + 9)
# L2's far door (north wall) goes on: north, east, north into S4's entry
x0, y0, x1, y1 = L2
carve(x0 + 2, y0 - 1, x0 + 3, y0 - 1)
s4x, s4y = S4["S"]
vpath(x0 + 3, 134, y0 - 1)
hpath(x0 + 2, s4x + 1, 135)
vpath(s4x, s4y, 136)
notes["code_room"] = [x0, y0, x1, y1]

# S4: west and east loops into copies above; straight north to the room with the stick
sx, sy = S4["W"]
hpath(sx - 5, sx, sy)
copy_of(S4, sx - 4 - 19, 29, "S4-W")
vpath(sx - 4, 29 + 39, sy + 1)
sx, sy = S4["E"]
hpath(sx, sx + 9, sy)
copy_of(S4, sx + 8 - 19, 29, "S4-E")
vpath(sx + 8, 29 + 39, sy + 1)
nx, ny = S4["N"]
vpath(nx, ny - 14, ny)
carve(nx - 6, ny - 26, nx + 6, ny - 15)                    # the room with the stick
props.append({"kind": "stick", "x": nx + 5.55, "y": ny - 25.55, "rot": 0})
notes["stick"] = [nx + 5.55, ny - 25.55]

# ---- props in a station's bay show in its copies too (a copy must look like the real thing)
def in_bay(p, ox, oy):
    return ox + 12 <= p["x"] <= ox + 27 and oy + 14 <= p["y"] <= oy + 40

for st, cx, cy in copies:
    for p in list(props):
        if p.get("copy"): continue
        if in_bay(p, st["ox"], st["oy"]):
            q = dict(p); q["x"] += cx - st["ox"]; q["y"] += cy - st["oy"]; q["copy"] = 1
            props.append(q)

# ---- rooms off the long corridors: plain rooms, some with a table and a computer, a camera on
# a tripod, stacked boxes, or nothing at all (the video's rooms are mostly nothing)
import random
rnd = random.Random(1995)
def free(x0, y0, x1, y1):
    for y in range(y0 - 1, y1 + 2):
        for x in range(x0 - 1, x1 + 2):
            if not (0 <= x < W and 0 <= y < H) or G[y][x] != '#':
                return False
    return True
KINDS = ["table", "table_pc", "camera", "boxes", "empty", "chairs", "empty", "table_pc"]
for (xc, y0, y1) in corridors:
    y = y0 + 4
    side = 1
    while y + 6 < y1:
        if side > 0:
            r = (xc + 3, y, xc + 8, y + 5); door = (xc + 2, y + 2, xc + 2, y + 3)
        else:
            r = (xc - 8, y, xc - 3, y + 5); door = (xc - 2, y + 2, xc - 2, y + 3)
        if free(*r):
            carve(*r); carve(*door)
            k = KINDS[rnd.randrange(len(KINDS))]
            if k != "empty":
                props.append({"kind": k, "x": (r[0] + r[2]) / 2 + 0.5 + rnd.uniform(-1, 1), "y": (r[1] + r[3]) / 2 + 0.5 + rnd.uniform(-1, 1), "rot": rnd.randrange(0, 360)})
        side = -side
        y += 9

json.dump({"w": W, "h": H, "rows": ["".join(r) for r in G], "seams": seams, "props": props, "notes": notes},
          open("scripts/stockrooms_map.json", "w"))

if len(sys.argv) > 1:
    from PIL import Image, ImageDraw
    S = 3
    im = Image.new("RGB", (W * S, H * S), (20, 18, 8))
    d = ImageDraw.Draw(im)
    for y in range(H):
        for x in range(W):
            c = G[y][x]
            if c == '.': d.rectangle([x * S, y * S, x * S + S - 1, y * S + S - 1], fill=(205, 186, 90))
            elif c == 'X': d.rectangle([x * S, y * S, x * S + S - 1, y * S + S - 1], fill=(58, 160, 200))
    for s in seams:
        x0, y0, x1, y1 = s["rect"]
        d.rectangle([x0 * S, y0 * S, (x1 + 1) * S, (y1 + 1) * S], fill=(200, 40, 40))
    for p in props:
        col = {"stick": (255, 140, 40), "ladder": (40, 200, 90), "chair": (60, 90, 220), "camera": (200, 60, 200)}.get(p["kind"], (90, 70, 30))
        d.ellipse([p["x"] * S - 3, p["y"] * S - 3, p["x"] * S + 3, p["y"] * S + 3], fill=col)
    im.save(sys.argv[1])
    print("seams", len(seams), "props", len(props))
