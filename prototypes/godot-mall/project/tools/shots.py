# usage: shots.py <dir> <prefix> "x,z,yaw,pitch" ...   -> <prefix>N.png (960x540)
import sys, asyncio, http.server, threading, functools, socketserver
from playwright.async_api import async_playwright
d, pre, cams = sys.argv[1], sys.argv[2], sys.argv[3:]
H_ = functools.partial(http.server.SimpleHTTPRequestHandler, directory=d)
H_.log_message = lambda *a: None
class S(socketserver.ThreadingMixIn, http.server.HTTPServer): daemon_threads=True
srv = S(("127.0.0.1", 0), H_); port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist"])
        for i, c in enumerate(cams):
            pg = await b.new_page(viewport={"width":960,"height":540})
            await pg.goto(f"http://127.0.0.1:{port}/index.html?cam={c}")
            await pg.wait_for_timeout(40000)
            await pg.screenshot(path=f"{pre}{i}.png", timeout=180000)
            await pg.close()
            print("shot", i, c, flush=True)
        await b.close()
asyncio.run(main())
