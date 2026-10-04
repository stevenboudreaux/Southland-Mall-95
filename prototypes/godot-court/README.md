# Godot court proof (Oct 4, 2026)

A test of how rich the mall can look in Godot, built as one area: the court by
Shoe Dept. Encore in the 2018 walkthrough, which is the court where the east
hall meets the main entrance hall in the game's map. It has 1995 tenants with
the architecture seen in the 2018 video (0:16, 0:22, 0:36, 0:50–0:56, 2:28).

- Play it: `prototypes/godot-court/play/` on the live site.
- Not connected to the game. Nothing in `index.html` changed.

## What is in it

- Court: tan plaster segmental barrel vault, darker arched trim bands, a
  clerestory along the west wall, a square skylight, four brass lanterns, four
  round columns, blue-grey/cream checker floor in a charcoal border with cream
  diamonds, a palm bed with poinsettias and dark-stained benches backed onto it.
- Halls: ribbed barrel vault over the checker band, low flat ceilings with round
  downlights over the plank-laid store lanes, arched end walls.
- Stores (1995 map, sign colours from `mall-data`): Woolworth; Footaction USA,
  Kids Mart, Jean Nicole; K&B with its pink wall and plum stripes; Sears at the
  north end; Gordon's Jewelers, Claire's, Mitchell's Formal Wear, Laser Copies,
  Vision Plaza; Franks, Orange Julius, Tee Tai's, Optical Outlet, T.J.'s One Hour
  Photo, Pups & Pets; Lerner Shop, Coach House Gifts, Radio Shack, GNC, The Avenue.
  Store signs are plain lettering in the game's colours, not the real logos.
- Lighting: baked with LightmapGI (sun through the skylight and clerestory, sky,
  ~70 ceiling/store/lantern lights, 3 bounces), reflection probes for glass and
  metal, and a mirrored-camera reflection on the polished floors.

## How it is made

Everything is generated from code so it can be tuned and rebuilt:

1. `python3 project/tools/make_textures.py` draws every texture into `tex/`.
2. `godot --headless --path project --script res://tools/build.gd` builds
   `main.tscn` (geometry, stores, props, lights) from `layout.json`.
3. Bake lighting: open the project in the Godot 4.5 editor, select
   `LightmapGI`, press **Bake Lightmaps** (about 20 minutes on CPU-only
   software Vulkan; about a minute on a computer with a graphics card).
   `addons/autobake` does the same thing unattended.
4. Export with the **Web** preset (Compatibility renderer, no threads, so it runs
   on GitHub Pages without special headers) into `play/`.

## Controls

Phone: drag on the left half to walk, drag on the right half to look.
Desktop: WASD or arrow keys, drag the mouse to look.
`?cam=x,z,yaw,pitch` in the URL places the camera (used for test shots).
