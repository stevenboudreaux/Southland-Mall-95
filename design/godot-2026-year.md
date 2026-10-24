# The 2026 year in the Godot mall

Added Oct 23, 2026 (Demo 42), after Steven's site visit (34 narrated videos and 40 photos of the
real Southland Mall, Oct 23 2026). Report: "Southland Mall 2026 Site Visit — Analysis for Houma
Mall Rewind" (Claude Doc, https://claude.ai/artifact/Ghfh9EQic36PJc3Cas1Row).

## What it is
The same building as 1995 with the tenants of October 2026. The player switches years in place:
"Visit 2026 (Y)" / "Back to 1995 (Y)" under "Jump to" (top right), or the Y key. The building
stays, the stores change.

## Data
- `prototypes/godot-mall/project/data/eras_2026.json`: the 2026 store list, in mall-data's store
  format (83 units, 29 vacant, 10 re-cut). The same list is `eras["2026"]` in `index.html`'s
  mall-data on the `map-2026` branch (not merged to main).
- `tools/make_layout_2026.py` → `layout_2026.json`: 1995's layout (zones, hall geometry, the Oct
  7–8 corrections) with every store frontage relabelled to the 2026 unit behind it, merged units
  as one front, split units as their own. The 1995 walk-in interiors are shut except Corn Dog 7.

## Build
- `godot --headless --path . --script res://tools/build_mall.gd -- --wing=<n> --year=2026`
  → `wing<n>_2026.tscn`, meshes in `gen/w<n>y26/`.
- 2026 fronts: the anchors' current fronts (`ANCHOR_LOOK_2026`: Lynn's Interiors, Dillard's,
  JCPenney), Corn Dog 7's 3D build (same shop), and the generic front with each tenant's sign for
  everyone else. Vacant units get the grille and "For Lease". No 1990s Courier ads, no info desk.
- In the game (`scripts/player.gd`): no 1995 crowd, Runner, Stockrooms, prizes or shirt words.
- Bake: `AUTOBAKE="wing1_2026:fastday wing2_2026:fastday"` (day only; the game is day-only), the
  lightmap is `wing<n>_2026_day.lmbake`.
- Stand-ins: `tools/capture_standin.sh <n> 2026` → `tex/standin/y26_from_w<n>_{day,night}.png`
  (night is a copy of day) stamped by `tools/wing_hash.sh <n> 2026`.

## Web
- Presets "Wing <n> Desktop 2026" / "Wing <n> Mobile 2026" (feature `w<n>y26`, main scene
  override `run/main_scene.w<n>y26`) → `w1y26.desktop.pck` etc. `tools/export_web.sh` exports both
  years when `wing1_2026.tscn` exists (`YEARS="1995"` to skip) and writes all pack sizes.
- `web/shell.html`: `?year=2026` picks the `y26` packs; the switch sets it and keeps `?wing=` and
  `?cam=`. Crossing the seam keeps the year.
- `tools/publish_build.sh` checks the 2026 stand-in stamps too and ships the 2026 packs and
  lightmaps.

## Next
- Build the 2026 storefronts from the footage, one by one (frame references are in the report's
  "Reference frames" table and the per-clip notes).
- 2026-only details: linear LED slots in the hall ceilings, the arched soffit bands every 25–30 m,
  the Solarium zig-zag front, Shoe Dept. Encore's and T-Mobile's exterior doors.
- Low-confidence units (report, Goal 2 table) after Steven's review.
