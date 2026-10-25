"""Headless check of the doors between inside and outside (design/godot-exterior.md): load wing 1
standing inside the main entrance, check the "Go outside" prompt shows, press E, check the page
comes back as wing 3 outside the doors; then press E again at the outside spot and check it
comes back as wing 1.

Usage: python3 doortest.py <url-path> <out-prefix>   (server on :8765 serving the repo root)
"""
import sys, time
from playwright.sync_api import sync_playwright

path, out = sys.argv[1], sys.argv[2]
ARGS = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"]

def ready(pg, t=300):
    t0 = time.time()
    while time.time() - t0 < t:
        try:
            if pg.evaluate("!document.getElementById('status')"):
                return round(time.time() - t0)
        except Exception:
            pass
        time.sleep(1)
    return None

with sync_playwright() as p:
    b = p.chromium.launch(args=ARGS)
    ctx = b.new_context(viewport={"width": 1280, "height": 720})
    pg = ctx.new_page(); logs = []
    pg.on("console", lambda m: logs.append(m.text))
    ok = True
    # inside the main entrance (wing 1, its inside spot is 34.5,0), looking out; then outside
    for leg, (start, want) in enumerate([("34.5,0,-90,0", "wing=3"), (None, "wing=1")]):
        if start:
            pg.goto(f"http://127.0.0.1:8765/{path}?wing=1&cam={start}&debug=1")
        print("leg", leg, "ready_s", ready(pg))
        time.sleep(8)
        pg.screenshot(path=f"{out}-{leg}-prompt.png")
        pg.focus("#canvas")
        pg.keyboard.down("e"); time.sleep(1.5); pg.keyboard.up("e")
        t0 = time.time(); cur = ""
        while time.time() - t0 < 120:
            try:
                cur = pg.evaluate("location.href")
            except Exception:
                cur = ""
            if want in cur:
                break
            time.sleep(0.5)
        print("leg", leg, "url", cur)
        if want not in cur:
            ok = False
            break
    print("arrived ready_s", ready(pg)); time.sleep(8)
    pg.screenshot(path=f"{out}-back.png")
    print("\n".join([l for l in logs if "crossing" in l or "ERR" in l.upper()][:12]))
    errs = [l for l in logs if "ERROR" in l.upper()]
    print("errors", len(errs), errs[:3])
    print("CROSSED" if ok else "DID NOT CROSS")
    b.close()
