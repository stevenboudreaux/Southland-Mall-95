# Evidence: photo-board styles restored (2026-10-04)

`2026-10-04-board-styles-before-after.jpg`: Corn Dog 7 board opened in 3D, headless Chromium 1000×700.
Left = live site at b3a1cb5 (after the 11:58 editor Publish): the board is invisible. Right = this fix.

Cause: the board CSS (`.gal…`, 5,571 chars) sat in the page's first `<style>`, which the editor's
`buildDocument()` replaces with its `RESET` string. Every editor Publish dropped it. Moved into
`<style id="mall-css">`, which `buildDocument()` keeps; confirmed by calling `buildDocument()` in the
page and finding `.gal-box{` in its output.

Also checked: board renders correctly at phone width (390×844); no page errors.
Publish guard tested with a fake GitHub: up-to-date tab publishes; stale tab and failed check publish nothing.
