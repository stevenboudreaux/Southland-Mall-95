"""Check the desktop/mobile game-file choice of a split web export (tools/export_web.sh).

Usage: python3 packtest.py <url-path> <out-prefix>   (server on :8765 serving the repo root)

Simulates GPUs that support only one set of texture formats by hiding the other set's
WebGL extensions from both the page and the engine, then checks:
  phone_gpu   - only ETC2/ASTC: the page picks the mobile file, no errors;
  desktop_gpu - only S3TC/BPTC: the page picks the desktop file, no errors;
  wrong_guess - only ETC2/ASTC but this browser remembered "desktop": the game notices,
                switches to the mobile file once, and remembers that.
"""
import sys, time
from playwright.sync_api import sync_playwright

path, out = sys.argv[1], sys.argv[2]
ARGS = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"]
DESK = ["WEBGL_compressed_texture_s3tc", "WEBGL_compressed_texture_s3tc_srgb", "EXT_texture_compression_bptc"]
MOB = ["WEBGL_compressed_texture_etc", "WEBGL_compressed_texture_etc1", "WEBGL_compressed_texture_astc"]

def hide(names, preset=None):
    js = "(() => { const H = %s;" % repr(names)
    js += """
    for (const C of [WebGLRenderingContext, WebGL2RenderingContext]) {
        const se = C.prototype.getSupportedExtensions, ge = C.prototype.getExtension;
        C.prototype.getSupportedExtensions = function () { return (se.call(this) || []).filter(e => !H.includes(e)); };
        C.prototype.getExtension = function (n) { return H.includes(n) ? null : ge.call(this, n); };
    }"""
    if preset:
        js += "try { if (!sessionStorage.getItem('pt')) { sessionStorage.setItem('pt','1'); localStorage.setItem('southland-pack','%s'); } } catch (e) {}" % preset
    return js + "})();"

CASES = [("phone_gpu", DESK, None, "mobile"), ("desktop_gpu", MOB, None, "desktop"), ("wrong_guess", DESK, "desktop", "mobile")]
ok_all = True
with sync_playwright() as p:
    b = p.chromium.launch(args=ARGS)
    for name, hidden, preset, want in CASES:
        ctx = b.new_context(viewport={"width": 1280, "height": 720})
        ctx.add_init_script(hide(hidden, preset))
        pg = ctx.new_page(); logs = []
        pg.on("console", lambda m: logs.append(m.text))
        pg.goto(f"http://127.0.0.1:8765/{path}?cam=-90,62.5,180,2&time=night")
        t0 = time.time(); got = None
        while time.time() - t0 < 180:
            try:
                st = pg.evaluate("[window.__mallPack, document.querySelector('#status') ? getComputedStyle(document.querySelector('#status')).visibility : 'gone']")
            except Exception:
                time.sleep(1); continue
            if st[1] in ("gone", "hidden"):
                got = st[0]; break
            time.sleep(1)
        time.sleep(10)
        try:
            got = pg.evaluate("window.__mallPack"); remembered = pg.evaluate("localStorage.getItem('southland-pack')")
        except Exception:
            remembered = None
        pg.screenshot(path=f"{out}-{name}.png")
        # errors from the final page only (the wrong guess's first load is expected to fail)
        n = len(logs)
        time.sleep(1)
        fresh = [l for l in logs[max(0, n - 400):] if "ERROR" in l.upper()]
        ok = got == want and (preset is None or remembered == want)
        if preset is None:
            ok = ok and not [l for l in logs if "ERROR" in l.upper()]
        ok_all &= ok
        print(name, "picked", got, "want", want, "remembered", remembered, "errors", len([l for l in logs if "ERROR" in l.upper()]), "OK" if ok else "FAIL")
        ctx.close()
    b.close()
print("ALL OK" if ok_all else "SOME FAILED")
