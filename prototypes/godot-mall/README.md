# Godot whole mall (started Oct 4, 2026)

The whole 1995 mall built in Godot from the game's own map data, alongside the
current game (which is unchanged). Plan and status: see the project notes;
the court proof that came first is in `prototypes/godot-court/`.

- Play: `prototypes/godot-mall/play/` on the live site.
- Rebuild: `python3 project/tools/convert_map.py index.html` (map → layout_mall.json),
  `godot --headless --path project --script res://tools/build_mall.gd`, bake with
  the editor's Bake Lightmaps (or `addons/autobake`), export the Web preset.
- Controls: phone, left thumb walks and right thumb looks; desktop, WASD + drag.
  `?cam=x,z,yaw,pitch` places the camera.
