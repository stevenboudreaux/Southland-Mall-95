# usage: shot.py <dir> <out.png> [wait_s] [w] [h] [js_after_load]
import sys, asyncio, http.server, threading, functools, socketserver
from playwright.async_api import async_playwright
d, out = sys.argv[1], sys.argv[2]
wait = float(sys.argv[3]) if len(sys.argv)>3 else 20
W = int(sys.argv[4]) if len(sys.argv)>4 else 1280
H = int(sys.argv[5]) if len(sys.argv)>5 else 720
js = sys.argv[6] if len(sys.argv)>6 else ""
H_ = functools.partial(http.server.SimpleHTTPRequestHandler, directory=d)
class S(socketserver.ThreadingMixIn, http.server.HTTPServer): daemon_threads=True
srv = S(("127.0.0.1", 0), H_); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
        pg = await b.new_page(viewport={"width":W,"height":H})
        logs=[]
        pg.on("console", lambda m: logs.append(m.text))
        await pg.goto(f"http://127.0.0.1:{port}/index.html")
        await pg.wait_for_timeout(int(wait*1000))
        if js:
            await pg.evaluate(js); await pg.wait_for_timeout(3000)
        await pg.screenshot(path=out, timeout=180000)
        for l in logs[-15:]: print("LOG:", l[:200])
        await b.close()
asyncio.run(main())
