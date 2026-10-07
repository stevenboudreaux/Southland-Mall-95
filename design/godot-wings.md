# Godot mall: two wings (since Demo 16, Oct 7, 2026)

**Asked for (Steven, Oct 7):** split the game file by wing instead of by storefront, so it stays
under GitHub's 100 MB file limit as stores are added. The seam is the floor change where the east
hall meets the Dillard's court. Walk up to it and a Fallout-style prompt offers the other wing
(a key, the controller's button, a click or a tap). Gumballs belongs to Wing 1 and its court
door is a crossing too. Looking across the seam must show the other wing exactly as it is now,
and must stay current as facades change.

## The wings
- **Wing 1** (`wing1.tscn`): Sears, the Sears halls, the east hall, the Shoe Dept. court, the main
  entrance hall, and the east hall south to the seam, with Gumballs.
- **Wing 2** (`wing2.tscn`): the Dillard's court, the Dillard's entry, the Concourse, the JCPenney
  court, the south exit hall and the restroom hall.
- **Where it's set:** `tools/build_mall.gd`.
  - `WING2_ZONES` lists the zones; every other zone is Wing 1.
  - `STORE_WING` lists stores whose wing is not the zone their front faces (Gumballs).
  - `SEAM` is the line on the floor: z = 48, from x = -20 (Gumballs' court door) to x = 2.
  - A frontage belongs to the zone it faces. A walkable tile belongs to its zone, else to the
    store built over it (`BUILT_RECTS`), else to its side of the seam.
- **Building:** `godot --headless --path . --script res://tools/build_mall.gd -- --wing=1`, then
  `--wing=2`. Each writes its scene plus `gen/w<n>/`: meshes, `signs.json`, `collide.json`,
  `wing.json` (this wing's walk grid, the seam, the default spawn) and `standin.json`.
  `--wing=0` still builds the whole mall into `main.tscn`, for checks only.

## The stand-in: the other wing, seen across the seam
- **What it is:** each wing also builds the other wing's halls and courts as usual (floors, vaults,
  ribs, ceiling lights, walls, exits), with a coarser lightmap. Every one of the other wing's
  storefronts is a picture on its frontage plane.
- **Where the pictures come from:** the other wing's own baked build.
  - `tools/capture_standin.sh <n>` runs `tools/capture_standin.gd` for night and day.
  - The capture stands an orthographic camera 1.25 m out in the hall facing each front, framing
    floor to lane ceiling. The pictures fill fixed slots of a 4096 x 2048 atlas:
    `tex/standin/from_w<n>_{night,day}.png`.
  - The slots come from the layout alone (`standin.json`), so a new capture never needs a rebuild
    or a rebake of the wing showing it. Only the atlas image changes.
- **How they're shown:**
  - Captured with a linear tone curve at half exposure, with no glow or colour grading.
  - Drawn unshaded at twice the brightness (`standin_mat`), so the game's own tone mapping and
    glow apply once, as they do to the real shops.
  - The day pictures swap in with the day lighting (`scripts/time_of_day.gd`, `tex_day`/`tex_night`).
  - The stand-in's lit shops also throw their light into the hall for that wing's bake.
- **Keeping it current: the rule.** Whenever a wing changes (a facade, a sign, a texture, a
  rebake), recapture that wing before publishing.
  - `tools/capture_standin.sh <n>` stamps the pictures with `tools/wing_hash.sh <n>`: a fingerprint
    of `gen/w<n>/`, the wing's lightmaps and every texture.
  - `tools/publish_build.sh` refuses to publish if either wing's fingerprint no longer matches its
    stamp, or if the export is older than the pictures.
  - So when, say, Payless's interior changes, Wing 2's view of it updates with the next publish.

## Crossing
- **Walls:** each wing's walk grid closes the other wing's tiles, so the seam is a wall
  (`scripts/player.gd`).
- **The prompt:** within 2.6 m of the seam on this wing's side, a prompt appears at the bottom
  middle: "Enter Wing 2 · Dillard's & JCPenney" with a key cap.
  - The key cap shows **E** (keyboard), **A** (controller) or **Tap** (touch).
  - E, Enter, the controller's A, a click or a tap on the prompt crosses.
- **The crossing:** a 0.35 s fade to black, then the page reloads into the other wing's file with
  `?wing=`, `cam=` (the same x, 1.3 m past the seam, the same facing), the lighting and the
  toggles.
  - The shell shows a dark "Wing 2" loading card instead of the cream one.
  - The game fades in from black.
- **Speed:** six seconds after a wing starts, `web/shell.html` fetches the other wing's file into
  Cache Storage (`mall-wings-<pack sizes>`; older caches are deleted). The crossing then loads it
  from there instead of the network.
- **Memory:** only one wing is ever in memory, which matters on the iPhone.
- **Test:** `tools/qa/seamtest.py <build>/index.html <out>` crosses 1 → 2 by key and 2 → 1 by
  clicking the prompt.

## Files and publishing
- **The export:** `tools/export_web.sh <out>` writes `w1.desktop.pck`, `w1.mobile.pck`,
  `w2.desktop.pck`, `w2.mobile.pck` and the shared `index.*`.
  - Presets: "Wing 1 Desktop", "Wing 1 Mobile", "Wing 2 Desktop", "Wing 2 Mobile".
  - Each preset exports its scene and the files it depends on, plus include filters for what the
    scripts load by path.
  - The `wing2` custom feature selects `run/main_scene.wing2`.
- **Baking:** the Mac bake plugin (`addons/autobake`) takes several jobs in one launch:
  `echo "wing1:night wing1:day wing2:night wing2:day" > .autobake`. It writes `.autobake_done`.
  About 7 minutes per bake on the MacBook Air.
- **What lives on `godot-build`:** `play/` (the four packs), `lightmaps/` (`wing<n>_{night,day}.*`)
  and `standin/` (the atlases and stamps). None of these are on `main` (`.gitignore`).
- **Bring back only the lightmaps** from the Mac: `wing<n>_{night,day}.{exr,exr.import,lmbake}`.
  - Keep the cloud-built `wing<n>.tscn` and `gen/`.
  - The Mac editor re-saves the generated meshes with its own resource IDs. A scene saved there
    points at IDs the cloud files don't have, and the web export then silently leaves out more
    than 100 meshes. That happened in Demo 16's first export: half the mall was invisible.
  - The lightmaps match either way: same meshes, same UV2.
- **Order for a demo:**
  1. Build both wings.
  2. Bake on the Mac.
  3. Bring the lightmaps back (not the scenes), and import.
  4. Capture both wings' stand-ins.
  5. Export.
  6. Run `seamtest.py` and the bake check shots.
  7. Commit to main.
  8. Run `publish_build.sh`.
