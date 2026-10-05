# QA and lighting test tools (Godot mall)

Added Oct 5, 2026 on the `godot-4.7-ultra` branch. `tools/*` is excluded from the web export.

- `movetest.py` — headless Chromium check of a web export: screenshots at fixed `?cam=` spots plus a touch-drag walk test (`?debug=1`). Needs `python3 -m http.server 8765` at the repo root.
- `lumatest.sh <name> <exr> [lmbake]` — puts a test lightmap into the project, imports, exports to `.scratch/builds/<name>`, shoots the Sears hall (W/E) and Shoe Dept. court, and prints mean luma. Use it to compare bakes by what the game shows.
- `hallglow.gd -- <outdir> <factor>` — writes `gen/H1a.res` and `gen/H1b.res` with emission scaled by `<factor>` (same effect as `HALL_GLOW` in build_mall.gd, without a full rebuild).
- `noemit.gd -- <outdir>` — writes copies of all `gen/*.res` with emission off, to measure how much of a bake comes from glowing surfaces.

Run the .gd tools with `godot --headless --path . --script res://tools/qa/<tool>.gd -- <args>`.
