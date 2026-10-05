"""Capture the live game's hand-drawn storefronts as textures for the Godot mall.

The current game draws every storefront to a flat canvas (storeTex in index.html:
n tiles x 32 px wide, 150 px tall = floor to lane ceiling) from Steven's photos and
notes. This renders each store frontage of layout_mall.json through that same
code at SCALE x, with the store's real door positions, and writes
  tex/fronts/<store id>.png  and  fronts.json  (one entry per store edge).

Run from the repo root with the game served there:
  python3 -m http.server 8765 &
  python3 prototypes/godot-mall/project/tools/capture_fronts.py
It uses a copy of index.html with the renderer's internals exposed
(.scratch/cap/index.html, made by this script).
"""
import base64, json, math, os, sys, time
from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
PROJ = os.path.join(ROOT, "prototypes", "godot-mall", "project")
OUT = os.path.join(PROJ, "tex", "fronts")
SCALE = 4
TILE = 2.0
HOOK = "  api.face=function(F,m){setF(F,false,m!==false);};\n  return api;\n})();"
CAP = ("  api.face=function(F,m){setF(F,false,m!==false);};\n"
       "  window.__cap={flatTex:flatTex,shell:shell,front:front,blank:blank,pier:pier,TW:TW,"
       "stores:function(){return M.stores;},entries:function(){return storeEntries;}};\n  return api;\n})();")


def make_cap_page():
    s = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    assert s.count(HOOK) == 1, "renderer hook not found in index.html"
    os.makedirs(os.path.join(ROOT, ".scratch", "cap"), exist_ok=True)
    open(os.path.join(ROOT, ".scratch", "cap", "index.html"), "w", encoding="utf-8").write(s.replace(HOOK, CAP))


JS_CAPTURE = """
([sid, n, doors, seed, scale]) => {
  const C = window.__cap, TW = C.TW;
  const s = C.stores().find(x => x.id === sid);
  if (!s) return null;
  const sg = {s: s, si: -1, x: 0, w: n * TW, i0: seed, n: n, doors: doors, part: false, t: "front"};
  const sc = {qB: 0, F: "N", dMax: 3, KY: 16};
  const tex = C.flatTex(sc, n * TW, function (g, fs) {
    C.shell(g, fs, 0, n * TW); C.front(g, fs, sg); C.pier(g, fs, 0); C.pier(g, fs, n * TW);
  });
  const big = document.createElement("canvas");
  big.width = tex.width * scale; big.height = tex.height * scale;
  const g = big.getContext("2d"); g.imageSmoothingEnabled = false; g.scale(scale, scale);
  tex.fn(g, tex.fs());
  return {png: big.toDataURL("image/png"), w: big.width, h: big.height, name: s.name, open: !!s.open,
          vacant: !!s.vacant, anchor: !!s.anchor, doors: sg.doors};
}
"""


def door_tiles(entries, a, b, n_tiles):
    """Entry tiles of the store that sit along this edge -> tile offsets from a."""
    ax, az = a
    bx, bz = b
    L = math.hypot(bx - ax, bz - az)
    tx, tz = (bx - ax) / L, (bz - az) / L
    out = []
    for e in entries or []:
        cx = (e[0] - 148 + 0.5) * TILE
        cz = (e[1] - 100 + 0.5) * TILE
        along = (cx - ax) * tx + (cz - az) * tz
        across = abs(-(cx - ax) * tz + (cz - az) * tx)
        if across < TILE * 0.75 and -0.1 <= along <= L + 0.1:
            d = int(math.floor(along / TILE))
            if 0 <= d < n_tiles and d not in out:
                out.append(d)
    return sorted(out)


def main():
    make_cap_page()
    os.makedirs(OUT, exist_ok=True)
    L = json.load(open(os.path.join(PROJ, "layout_mall.json")))
    edges = [e for e in L["edges"] if e["kind"] == "store"]
    manifest = {}
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        pg = b.new_page(viewport={"width": 1280, "height": 720})
        pg.goto("http://127.0.0.1:8765/.scratch/cap/index.html")
        pg.wait_for_function("window.__cap && window.__cap.stores().length > 0", timeout=60000)
        time.sleep(2)
        # the game draws some signs with a radius that goes slightly negative at odd widths; the canvas forgives it on-screen
        pg.evaluate("() => { const a = CanvasRenderingContext2D.prototype.arc; CanvasRenderingContext2D.prototype.arc = function(x, y, r, s0, s1, cc) { return a.call(this, x, y, Math.max(0, r), s0, s1, cc); }; }")
        entries = pg.evaluate("() => window.__cap.entries() || {}")
        for i, e in enumerate(edges):
            sid = e["store"]
            a, bb = e["a"], e["b"]
            Ln = math.hypot(bb[0] - a[0], bb[1] - a[1])
            n = max(1, int(round(Ln / TILE)))
            doors = door_tiles(entries.get(sid), a, bb, n)
            # the painting is seen from the hall; if the edge runs right-to-left for
            # that viewer, the picture's tiles run the other way from the edge's
            nx, nz = e["n"]
            tx, tz = (bb[0] - a[0]), (bb[1] - a[1])
            flip = (tx * nz - tz * nx) < 0
            pic_doors = sorted(n - 1 - d for d in doors) if flip else doors
            try:
                r = pg.evaluate(JS_CAPTURE, [sid, n, pic_doors, i * 7, SCALE])
            except Exception as ex:
                print("FAILED", sid, str(ex).splitlines()[0][:160])
                r = None
            if not r:
                print("skip", sid)
                continue
            key = "%s_%d" % (sid, i)
            fn = os.path.join(OUT, key + ".png")
            open(fn, "wb").write(base64.b64decode(r["png"].split(",", 1)[1]))
            manifest[key] = {"store": sid, "edge": i, "a": a, "b": bb, "name": r["name"], "tiles": n, "doors": doors, "flip": flip,
                             "px": [r["w"], r["h"]], "open": r["open"], "vacant": r["vacant"], "anchor": r["anchor"]}
            print(key, r["name"], n, "tiles", "doors", r["doors"])
        b.close()
    json.dump({"scale": SCALE, "px_per_tile": 32 * SCALE, "height_m": 4.6, "fronts": manifest},
              open(os.path.join(PROJ, "fronts.json"), "w"), indent=1)
    print("wrote", len(manifest), "fronts")


if __name__ == "__main__":
    main()
