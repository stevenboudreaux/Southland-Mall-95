# Session handoff: Houma Mall Rewind (Oct 7, 2026, evening): the Cucos neon sign

Read `production/session-handoff-2026-10-07-demo16.md` first for the state of the mall. This session changed one thing: the Cucos sign.

## Live
- **Play:** https://stevenboudreaux.github.io/Southland-Mall-95/prototypes/godot-mall/play/
- **Stand in front of it:** add `?cam=29.6,-91.3,180,17` (Wing 1, the Sears hall, facing Cucos).

## Publish
- **main:** `2eee05c` (the sign's source, meshes, notes, evidence).
- **godot-build:** `e5a8877`, published Oct 7 at 17:50 with `tools/publish_build.sh`. Its workflow redeployed the site.
- **Packs:** Wing 1 63.5 MB (24 kB smaller than Demo 16: the old sign textures dropped out), Wing 2 65.3 MB, unchanged in size.

## Steven's direction (Oct 7, 17:01)
- Post only one thing: the most accurate neon Cucos Mexican Cafe sign, not tellable from his photos, lit a little, every detail still visible.
- The Demo 16 sign was "cropped off, 2D, sloppy".
- Study each photo, how neon signs are built, and say if other software is needed.
- He left after five minutes; no questions, publish.

## What was built
- **A real open-face neon channel sign**, in geometry only. Spec and method: `design/storefronts/cucos.md`, "The neon sign".
- **Script:** four sheet-metal cans (C-swash-S as one; u, c, o each their own): black returns 125 mm deep, a rim, brick-red inside.
- **Tubes:** 8 mm glass on standoffs, three abreast in the wide strokes, with electrode ends in black boots.
- **Bar:** the blue cabinet with bullnose ends, two white stripes and a doubled-back white tube at each end, MEXICAN CAFE as white plates with a tube each.
- **Light:** the tubes glow a little; each lays a pool of light on the red pan; a faint halo on the planks.
- **Shape source:** traced by machine from Steven's close-up photo, squared up against his frontal photo (`tools/stores/signs/src/cucos_front.jpg`).
- **Software:** Godot plus Python (OpenCV, SciPy, scikit-image) was enough. Nothing was installed on the Mac, and Blender was not needed.

## How it shipped without a rebake
- The sign is a dynamic mesh, outside the lightmap. Only `gen/w1/dyn_w8cf_sign.res` and `dyn_w8cf_sign_glow.res` changed.
- `tools/stores/signs/cucos_only.gd` rebuilds just those two with the same code a full wing build runs (`wave8.gd` `cucos_sign`).
- The lightmaps are Demo 16's, unchanged. Wing 1's stand-in pictures were recaptured; Wing 2's were not touched (no texture changed, so its stamp still matches).
- The Mac was not reachable this session and was not needed.

## Checks
- **Evidence:** `production/qa/evidence/d17-cucos-*`: photo against game from the photo's angle and square-on, close-ups night and day, and in-game shots.
- **In the real scene:** `tools/qa/wingshot.gd` renders of Wing 1, night and day.
- **The web build:** opened in a headless browser at the Cucos front before publishing (`d17-cucos-web-build-night.png`); the sign renders, and the page fetched Wing 2 for the crossing cache.
- **Stand-in:** Wing 1 recaptured, night and day; both wings' stamps match (`d17-cucos-standin-night.png` is the Cucos slot).
- **Crossing:** `tools/qa/seamtest.py` on the published build (run just after publishing): crossed 1 → 2 by key and 2 → 1 by clicking the prompt, 0 errors (`d17-seam-*.png`).
- **The live URL itself was not opened:** this workspace cannot reach github.io. The build branch is at `e5a8877` and both site deploy runs finished green.
- **Not done:** `movetest.py` was not re-run (walk grids did not change). No walk on the iPhone; no frame-rate measurement on a phone (the sign is about 25,000 triangles).

## Known gaps (for Steven's grade)
- **MEXICAN CAFE's typeface** is Old Standard Bold, thickened. The real letters are a heavier wedge-serif.
- **Tube runs** follow the can walls at a fixed inset; the real bender's runs differ in small ways.
- **Size:** fitted to the 1.62 m parapet (script 1.80 m wide). The street sign is about 3 m.
- **1995 mall sign:** the photos are of later street locations. Whether Southland's sign matched is not known.
- **Old files left in place:** `cu_name_logo.json`, `cu_sub_logo.json` and the `tex/sg/cu_*` textures are no longer used. Deleting the textures changes both wings' stand-in stamps, so remove them with the next full recapture.

## Next
- Steven grades the sign.
- If he has a photo of the sign lit at night, match the tube colour and the bar's letters to it.
- The rest of the open list is in the Demo 16 handoff.
