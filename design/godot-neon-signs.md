# Building a neon sign from photos (Godot mall)

How the Cucos sign (Demo 17, Oct 7 2026) was made, written so the next neon sign takes an hour, not a session of research. Steven's verdict on the result: "the output is great". Follow this unless the photos say otherwise.

Worked example, all committed:
- **Trace tool:** `tools/stores/signs/photo_trace.py`.
- **Sign maker:** `make_cucos.py` writes `cu_sign.json`.
- **Builder:** `cucos_sign.gd`.
- **Materials:** `channel.gd`, keys `cu2_*`.
- **Sign-only rebuild:** `cucos_only.gd`.
- **Preview:** `tools/qa/cucos_preview.gd`.
- **Spec:** `design/storefronts/cucos.md`, "The neon sign".
- **Evidence:** `production/qa/evidence/d17-cucos-*`.

## 1. What Steven wants (from his direction, Oct 7)
- **Indistinguishable from his photos, but lit "slightly".** Every physical detail stays visible; the glow must not wash out the metal.
- **Real 3D.** Flat, 2D, textured cards, or anything "cropped off" or "sloppy" is unacceptable.
- **No textures needed.** Geometry plus vertex colour reads crisper than a traced texture, and costs nothing in the pack.
- **Rebuild from the original photos**, never from the 8-bit game or a screenshot of an earlier build.
- **Working style:** he says no previews and no questions. Make the calls, publish, and list the guesses honestly.

## 2. How a real neon sign is built (enough to model it)
Read the photos for which of these kinds the sign is:

| Kind | What you see | Model it as |
|---|---|---|
| **Open-face channel** (Cucos) | Sheet-metal letter "cans" with no face; tubes visible inside on standoffs; inside painted (often the letter colour) | Returns + rim + painted back pan and inner walls; tubes inside |
| **Skeleton / tube-only** | Bare tubes on a backer or raceway, no cans | Tubes + standoffs + electrode boots, a raceway box behind |
| **Closed-face channel, neon inside** | Acrylic faces glowing evenly | That is `channel.gd`'s existing lit-face letter, not this method |
| **Neon on a cabinet** (Cucos's MEXICAN CAFE bar) | Painted box with plates or letters, tubes on top | Box (with its real end shapes) + plates + tubes |

What the details are, so you know what to model:
- **Tubes:** glass, 8 to 15 mm. They run in strokes along the letter: one tube in hairlines, two or three abreast in wide strokes.
- **Electrode ends:** every run is one piece of glass with an electrode at each end. Each end turns back through the pan into a black rubber boot, so a closed loop still has a gap where it starts and ends.
- **Standoffs:** glass or clear supports every 15 to 30 cm hold the tube about 3 to 5 cm off the pan.
- **Returns:** the cans' sides, 8 to 15 cm deep, usually black or dark bronze. They read as the sign's "drop shadow" in photos.
- **When lit:** the tube itself goes near-white at its core with a coloured edge. The pan behind it gets a soft stripe of the tube's colour, and the wall round the cans gets a faint halo. That is all "lit slightly" needs.

## 3. Software: what is enough
Godot plus Python is enough. Blender was not needed, nothing was installed on the Mac, and no rebake was needed.
- **Python (cloud):** `opencv-python-headless`, `numpy`, `scipy`, `scikit-image`, `mapbox_earcut`, `pillow`, `fonttools`.
  - Install with `pip install --break-system-packages mapbox_earcut shapely fonttools`; the rest are usually present.
- **Godot 4.7.2 headless + web templates (cloud):** a fresh workspace needs both.
  - Get them from the GitHub release: `Godot_v4.7.2-stable_linux.x86_64.zip` and `Godot_v4.7.2-stable_export_templates.tpz`.
  - Unzip only `templates/web*` into `~/.local/share/godot/export_templates/4.7.2.stable/`.
  - Both downloads finish in seconds through the proxy.
- **Import:** `godot --headless --path . --import` takes about 12 minutes the first time (the lightmap EXRs); later runs take seconds.

## 4. The method, step by step

### Step 1: Square up the photos (`photo_trace.py`)
Run all commands from `prototypes/godot-mall/project`. Each has `--help`.
- **Two photos of the same sign** (one sharp from an angle, one square-on but soft): use `front`.
  - It registers the sharp one onto the square-on one by aligning their colour masks, then warps the sharp photo square-on.
  - This gives the sharp photo's detail, seen straight on.
  - The masks' overlap (IoU) printed at the end should be about 0.75 or better.
  - Open the `--overlay` image: it should be mostly yellow.
- **One photo only:** use `quad` on four corners of something rectangular on the sign's plane, such as a cabinet or the wall's panel lines. You need its true aspect ratio.
- **Then `level`** on a part known to be horizontal: the bottom edge of a cabinet or band.

Cucos, exactly:
```
T=tools/stores/signs/photo_trace.py
python3 $T front --oblique close.png --orect 370,300,790,640 --frontal front.png --frect 280,75,455,190 \
    --hue red --canvas 250,60,490,230 --overlay ov.png --out f0.png
python3 $T level --front f0.png --hue blue --out f1.png          # turned -2.95 degrees
```

### Step 2: Trace the openings (`mask`), then look
```
python3 $T mask --front f1.png --hue red --box 0,0,1920,980 --out m.png --overlay check.png
```
- **Keep the thresholds low.** The defaults that worked: saturation 38 and value 57 or more. At 70/72 the shadowed inner walls (the S's top arch, the C's notch) drop out and the letters get bitten. Look at `--overlay` every time.
- **Unlit tubes are white and belong to the opening:** `--tube 168` adds pale pixels near the colour.
- **Black is never inside:** `--dark 50` removes the returns seen side-on and the gaps between cans.
- **Holes under 1500 px are filled** (rust, electrode boots); real counters are larger.

### Step 3: Separate the cans (`zoom`, then `cut`)
Letters that touch in the photo are usually separate cans. Look for a black return between them.
- Use `zoom --grid 25` to read off the pixel coordinates of each join.
- `cut` the mask along those lines, and check that the part count is right.
- Cucos had four parts: the C-swash-S as one can, and u, c, o each on their own.
```
python3 $T cut --mask m.png --lines "765,506,765,542;936,408,947,454;1138,350,1161,430" --out cans.png
```
- Copy the result to `tools/stores/signs/src/<id>_cans.png`, and the squared-up photo to `src/<id>_front.jpg`. Both are sources, so commit them.

Re-running these steps on Steven's photos reproduces the committed Cucos mask to 99.7%.

### When the photo is too small to trace: fit a typeface (Karmelkorn, Oct 7)
If the letters are only a few dozen pixels tall and the glow joins them, `mask` gives blobs.
Karmelkorn's square-on photo was 582 px. The worked example is `tools/stores/signs/kk_trace.py`:
1. **Enlarge.** Crop to the sign and enlarge 4x (bicubic). Save it as `src/<id>_front.jpg`.
2. **Find each letter's box.** Take a column profile of brightness across the caps band (the 70th percentile per column, smoothed). Its minima are the gaps between letters. A minimum inside a letter (a counter) gives itself away by an odd letter width.
3. **Pick the typeface.** Fit each glyph into its box by correlation with the photo's brightness, blurring the glyph as much as the photo is blurred (sigma 4 at 4x), and search the box edges by ±9 px.
   - `kk_trace.py --fonts ...` scores several faces. Then look at the overlay: the scores sit within 0.02 of each other, so pick by eye.
   - Thinning made no difference to the score (blur dominates). Choose it by the counters' size in the photo.
4. **Build one-off letters as strokes,** such as a swash K or a flourish. Measure their centre lines and widths off a skeleton of the photo's mask; widths come out about a third too wide because of the glow. Tracing them directly came out wobbly, the "sloppy" look Steven rejects.
5. **Leave air between cans:** 1.5 photo px. Drop slivers.

Then carry on from step 4 (`make_kk.py` is `make_cucos.py` without the cabinet).
- **Outline neon** (Karmelkorn): no centre run in wide strokes, just the inset ring and a single run in hairlines. Drop centre runs shorter than 70 px, because those are serif stubs.
- **Tube scale:** on a 6 m sign, 9 mm glass read as hairlines; 12 mm matched the photo.
- **Two fronts:** one dynamic group, two `build` calls, and a node pair in the wing's `.tscn`.

### Step 4: Make the sign's data (copy `make_cucos.py`)
Copy `make_cucos.py` to `make_<id>.py` and change the constants. It writes `<id>_sign.json`:
- **cans:** outline loops plus back-pan triangles, in metres.
- **tubes:** each run's points and whether it is closed.
- **plates and wtubes:** a lettered cabinet, if there is one.

Constants that matter:
- **`LOGO_W`:** the script's width in metres. Fit the mall parapet; check the fascia height in the store's builder.
- **`D1`** (the tube run's inset from the wall, 19 px = 30 mm on Cucos) and **`DC`** (strokes wider than 2 × DC get a centre run). Together these give one, two or three tubes abreast as the stroke widens. Check against the photo.
- **Bar ratios** (`BAR_W_K`, `BAR_H_K`, `GAP_K`, the text span 18%–89%): measure them on the squared-up photo.
- **Cabinet lettering:** no exact font was found for Cucos. Old Standard Bold dilated 13 px was the closest. Try a few OFL faces in `src/` against the photo before settling.
- **Check drawing:** `python3 make_<id>.py check.png` draws a flat check image. Read it before building.

### Step 5: Build it (copy `cucos_sign.gd`)
Copy `cucos_sign.gd` and keep the parts as they are:
- **`_can_walls`:** black return, rim, red inner wall, halo.
- **`_tube`:** a six-sided swept tube.
- **`_ends`:** electrode boots.
- **`_posts`:** standoffs.
- **`_pool`:** the stripe of light behind a tube. It narrows round tight bends so it does not fold.
- **`_bar`:** the bullnose cabinet, stripes and looped end tubes. Delete it if there is no cabinet.

Numbers that looked right:
- Cans 125 mm deep (photo: the returns are about a ninth of the script's height); rim 4 mm; back pan 6 mm off the fascia.
- Tubes 8 mm (radius 0.0042), centres 42 mm off the fascia; standoffs every 21 cm.
- Halo 75 mm round outer loops, 30 mm inside counters. Wider halos fold over themselves in tight counters.

Materials go in `channel.gd`'s `fill_mat` as `<id>2_*`, each with `e_day` and `e_night` metadata for `time_of_day.gd`. Cucos values for a "lit slightly" red neon:

| Key | Albedo | Emission | e_day / e_night |
|---|---|---|---|
| black (returns) | `#15120f`, metallic 0.25 | — | — |
| red (pan, walls) | `#a22a1c` | `#e0341c` | 0.3 / 0.5 |
| tube | `#ff9a88` | `#ff3c22` | 1.4 / 1.9 |
| boot | `#0b0b0b` | — | — |
| post | `#d9dad4` | `#ff6a48` | 0.1 / 0.25 |
| blue (cabinet) | `#4c58a8` | `#5562cc` | 0.32 / 0.5 |
| white (plates) | `#eef0f4` | `#eef2ff` | 0.5 / 0.8 |
| white tube | `#ffffff` | `#eaf2ff` | 1.3 / 1.8 |
| pool / halo | unshaded, additive, colour in the vertices | — | — |

Tuning history, so you start in the right place:
- **Tube emission:** 2.6 bloomed the tubes into a blur at night; 1.9 keeps them crisp.
- **Pan emission:** under 0.3 the red read black from across the hall.
- **Cabinet:** blue emission under 0.3 went navy at night.

### Step 6: Hook it into the store and rebuild only the sign
- **Call it from the store's builder** (Cucos: `wave8.gd` `cucos_sign`) into a dynamic group named `<x>f_sign`. The group's `_glow` twin takes the added light.
- **No rebake:** dynamic meshes are outside the lightmap, so the lightmaps do not change.
- **Sign-only rebuild:** copy `cucos_only.gd`, change the store's frame and the output files, and run:
  ```
  godot --headless --path . --script res://tools/stores/signs/<id>_only.gd
  ```
  - It rewrites `gen/w<n>/dyn_<x>f_sign.res` and `..._glow.res` with the same code a full build runs.
  - Get the store's frame (corner, along-vector, normal, width, head height) from `build_mall.gd` `BUILT_RECTS` and the store's builder. Cucos: front x 22–36 at z = -86 facing north, laid out from the viewer's left, so a = (36, 0, -86) and t = (-1, 0, 0).
- **Sign size:** about 20,000 triangles plus 4,800 for the light. The mesh is saved with compressed attributes.

### Step 7: Look, compare, publish
1. **Preview** (about 15 s): copy `tools/qa/cucos_preview.gd`.
   - It shows the sign alone, night and day: square-on, from the photo's angle, close up, and from a shopper's spot.
   - Put the photo and the render side by side at the same angle; this is the check that matters.
   - The Cucos comparisons caught the cans being too shallow, the script being off-centre on the bar, and the small letters being joined.
2. **In the real scene** (about 75 s): `tools/qa/wingshot.gd -- --wing=1 --mode=night --cam=x,z,yaw,pitch --out=...`.
3. **Recapture the wing's stand-in:** `tools/capture_standin.sh <wing>`, about 17 minutes in the cloud.
   - Start it in the background as soon as the sign is final.
   - Do not change `gen/` while it runs: the stamp is taken at the end, and a changed mesh means a stale picture.
4. **Import, export, check, publish:**
   ```
   godot --headless --path . --import
   tools/export_web.sh <out>
   ```
   - Optional: screenshot the build in Chromium at `?cam=`.
   - Run `tools/qa/seamtest.py index.html <prefix>` with `python3 -m http.server 8765` serving the build folder.
   - Commit to main, then run `tools/publish_build.sh <out> "<message>"`.
5. **Things that tripped this session:**
   - The publish script needs `origin/godot-build`:
     ```
     git config --add remote.origin.fetch "+refs/heads/godot-build:refs/remotes/origin/godot-build"
     git fetch --depth 1 origin godot-build
     ```
   - The lightmaps and stand-in pictures live only on that branch. Before anything else, copy `lightmaps/*` into the project folder and `standin/*` into `tex/standin/` from it.
   - The cloud cannot open github.io. To check the live site, rely on the deploy runs (`gh run list`) and the branch head.
   - Killing a background shell with `pkill -f` on a pattern that matches your own command line kills your own shell (exit 144). Use a `[b]racket` in the pattern.

## 5. Timing (Cucos, cloud only)

| Step | Time |
|---|---|
| Godot download + first import | about 13 min (in parallel with tracing) |
| Squaring up, masks, cuts | 10–15 min |
| Sign maker + builder + materials | 20 min (copying Cucos's: about 5) |
| Look-and-fix loops (preview 15 s each) | 15 min |
| Stand-in recapture (wing 1) | 17 min, background |
| Export + browser check + seam test + publish | 5 min |

## 6. Gaps to state honestly when handing over
- **Typeface:** cabinet lettering in a stand-in font.
- **Tube runs:** they follow the walls at a fixed inset; a real bender's runs start, stop and cross differently.
- **Scale:** the mall sign is fitted to the parapet. Street signs are larger.
- **Period:** photos of present-day street locations may not match the 1995 mall sign. Say so; never claim it.
- **Old files:** a store's old sign textures (`tex/sg/<id>_*`) become unused. Deleting a texture changes both wings' stand-in stamps, so remove them with the next full recapture.
