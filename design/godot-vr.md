# The Godot mall in a VR headset (Meta Quest 2)

Steven, Oct 12, 2026: "make the existing game able to be played on meta quest 2".

## What it is
The same web page, opened in the headset's browser. Where the browser can do immersive VR
(WebXR), the page shows an **Enter VR** button; pressing it puts you in the mall at real scale.
Phones and computers never see the button and are unchanged. Nothing is installed on the headset.

This is the WebXR route from the Oct 6 discussion. A native Quest app (an Android export with
Meta's OpenXR add-on, sideloaded with developer mode) would run faster and is still open; it is a
separate export of the same project and would reuse `scripts/vr.gd`'s rig and controls.

## Playing
1. In the headset, open the Meta Quest Browser and go to the mall's address.
2. Wait for the mall to appear on the flat screen, then press **Enter VR**.

| Control | Does |
|---|---|
| Left stick | Walk the way you are looking |
| Either grip, held | Run |
| Right stick, left/right | Turn in 30° snaps |
| A, X or a trigger | Use: the other wing, a playable machine, the menu's choice |
| B or Y | Menu: jump to Sears, the mall entrance, Dillard's, JCPenney; lighting night/day; benches and plants; leave VR |
| Walking in your room | Moves you in the mall |

Prompts and the menu hang in the air about a metre in front of you and drift after your head.

## Rules
- **Height:** your own. The session asks for the headset's floor (`local-floor`), so the mall's
  floor is your floor. Without a floor (`local`), the playspace is lifted to the flat game's 1.62 m.
- **Where you start:** where the flat camera stood, facing the way it faced, whatever spot of the
  room the headset is in (`recentre`). The same after a jump. Leaving VR leaves the flat camera
  where your head was.
- **Walls:** the stick cannot walk your head through a wall or an obstacle (the flat game's walk
  grid and obstacle list, tested at the head). Leaning or stepping through one in the room is not
  stopped; the stick then walks you back out.
- **Floor reflection:** off in VR and restored on leaving. It draws the mall a second time, which
  in a headset would be four times a frame, and it is built for one camera.
- **Arcade games** (the ROM cabinets, WHIRLWIND, skee-ball, the claws) are flat web pages. In VR
  the board says so; A leaves VR and opens the game on the browser's flat screen. Closing the game
  brings back the Enter VR button.
- **The other wing** is another page load, which ends a VR session. The page remembers
  (`sessionStorage` `mall-vr`), shows a large **Back into VR** button when the wing has loaded, and
  resumes without a press where the browser hands the session over (`sessiongranted`).
- **Owner sign editing** is not available in VR.

## Where it lives
- `prototypes/godot-mall/project/scripts/vr.gd`: the session, the rig (XROrigin3D, XRCamera3D, two
  XRController3D under the player), movement, the board and menu.
- `scripts/player.gd`: adds the `VR` node; `vr_on` stops the flat controls; a jump re-centres.
- `web/shell.html` `window.mallVR`: the button, the wing-crossing memory, `sessiongranted`, and
  two tuning switches read from the address:
  - `?vrfov=0..1`: fixed foveation, how coarsely the edges of the view are drawn (default 1, most);
  - `?vrscale=0.3..1.5`: pixels drawn per eye against the browser's default (default: untouched).
  - `?vrmsaa=0|2|4`: edge smoothing in VR (default: the flat game's 2×).
- **What the engine needs from the browser** (Godot 4.7.2's web build): WebXR Layers and multiview
  drawing (`OVR_multiview2`). It refuses to start VR without either and the page then says why
  under the button. The Meta Quest Browser has both. The page ships no polyfill.
- Tests:
  - `tools/qa/vrtest.py <url-path> <out> <iwer.min.js> <webxr-layers-polyfill.min.js>` drives an
    emulated Quest 2 (Meta's IWER) in a headless browser: entering, standing height, walking,
    snap turns, the menu, a jump, leaving, playing a machine, crossing the seam and coming back
    into VR. Must print ALL OK. The emulator's picture is black (its layers polyfill cannot
    show multiview drawing), so it checks behaviour, not the image.
  - `tools/qa/vrboard.gd` renders the board (hint, menu, seam prompt) natively to look at it.

## Guesses, until Steven has worn it
- Walking 2.4 m/s, running ×1.8 (the flat game walks 4.0, too fast for comfort in a headset).
- 30° snap turns, no smooth turning, no vignette while moving.
- The board's distance (1.1 m), drop (0.28 m) and text size.
- Fixed foveation at its strongest.
- The hands are plain cream blocks.

## Not known
- **The picture in the headset.** No test here can show it: the emulator draws black, and the
  board was looked at in a flat render only. The first real check is Steven's headset.
- **Frame rate on a Quest 2.** Not measured: there is no headset in the cloud. The mall's wings
  are 64 to 67 MB and were tuned for phones at one view; a headset draws two. If it stutters, the
  levers in order: `?vrscale=0.8`, benches and plants off (the default), then a native app.
- Whether the Quest browser resumes VR by itself after crossing wings.
- Comfort and scale as felt.
