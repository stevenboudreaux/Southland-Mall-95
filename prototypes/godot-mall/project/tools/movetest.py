import asyncio, http.server, threading, functools, socketserver
from playwright.async_api import async_playwright
from PIL import Image, ImageChops
H_ = functools.partial(http.server.SimpleHTTPRequestHandler, directory=__import__("sys").argv[1] if len(__import__("sys").argv)>1 else "/home/claude/mallplay"); H_.log_message=lambda *a: None
class S(socketserver.ThreadingMixIn, http.server.HTTPServer): daemon_threads=True
srv=S(("127.0.0.1",0),H_); port=srv.server_address[1]; threading.Thread(target=srv.serve_forever,daemon=True).start()
def diff(a,b):
    d=ImageChops.difference(Image.open(a).convert('L'),Image.open(b).convert('L'))
    return sum(d.getdata())/ (d.size[0]*d.size[1])
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
        ctx=await b.new_context(viewport={"width":800,"height":400}, has_touch=True, is_mobile=True)
        pg=await ctx.new_page(); errs=[]
        pg.on("console", lambda m: errs.append(m.text) if ("ERROR" in m.text or "DBG" in m.text or m.type=="error") else None)
        await pg.goto(f"http://127.0.0.1:{port}/index.html?debug=1"); await pg.wait_for_timeout(45000)
        await pg.screenshot(path="/tmp/mv0.png", timeout=180000)
        cdp=await ctx.new_cdp_session(pg)
        await cdp.send("Input.dispatchTouchEvent",{"type":"touchStart","touchPoints":[{"x":150,"y":300,"id":0}]})
        for i in range(10):
            await cdp.send("Input.dispatchTouchEvent",{"type":"touchMove","touchPoints":[{"x":150,"y":300-6*i,"id":0}]})
            await pg.wait_for_timeout(400)
        await pg.wait_for_timeout(4000)
        await cdp.send("Input.dispatchTouchEvent",{"type":"touchEnd","touchPoints":[]})
        await pg.screenshot(path="/tmp/mv1.png", timeout=180000)
        print("touch walk diff", round(diff("/tmp/mv0.png","/tmp/mv1.png"),2))
        print("\n".join(errs[-12:]))
        await b.close()
asyncio.run(main())
