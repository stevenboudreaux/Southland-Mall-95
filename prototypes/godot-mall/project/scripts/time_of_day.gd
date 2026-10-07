@tool
## Switches the mall between its two lighting setups, "night" (default) and
## "day". Used by the bake plugin before each bake and by the game at runtime.
## Each setup has its own baked lightmap, named after the scene: res://wing1_night.lmbake,
## res://wing1_day.lmbake (res://main_*.lmbake for a whole-mall build).
## The other wing's stand-in pictures (materials with "tex_night" / "tex_day" metadata, see
## tools/build_mall.gd standin_mat) swap with the lighting too.
## Lights and materials carry metadata set by tools/build_mall.gd:
##   "only" = "day" or "night"  -> the light exists in that setup only
##   "e_day" / "e_night"        -> light energy, or material emission, per setup
class_name TimeOfDay
extends RefCounted

static func apply(root: Node, mode: String, swap_lightmap := true) -> void:
	var env_node := root.get_node_or_null("Env")
	if env_node:
		env_node.environment = load("res://gen/env_%s.tres" % mode)
	var mats := {}
	_walk(root, mode, mats)
	if swap_lightmap:
		var lm := root.get_node_or_null("LightmapGI")
		var path := lightmap_path(root, mode)
		if lm and ResourceLoader.exists(path):
			lm.light_data = load(path)

## res://<scene>_<mode>.lmbake for the scene `root` was loaded from.
static func lightmap_path(root: Node, mode: String) -> String:
	var base := "res://main"
	if root.scene_file_path != "":
		base = root.scene_file_path.get_basename()
	return "%s_%s.lmbake" % [base, mode]

static func _walk(n: Node, mode: String, mats: Dictionary) -> void:
	if n is Light3D:
		if n.has_meta("only"):
			n.visible = (n.get_meta("only") == mode)
		if n.has_meta("e_" + mode):
			n.light_energy = n.get_meta("e_" + mode)
	elif n is MeshInstance3D and n.mesh:
		for i in n.mesh.get_surface_count():
			var m = n.mesh.surface_get_material(i)
			if m is StandardMaterial3D and not mats.has(m):
				if m.has_meta("e_" + mode):
					mats[m] = true
					m.emission_energy_multiplier = m.get_meta("e_" + mode)
				if m.has_meta("tex_" + mode):
					mats[m] = true
					var tp: String = m.get_meta("tex_" + mode)
					if ResourceLoader.exists(tp):
						m.albedo_texture = load(tp)
	for c in n.get_children():
		_walk(c, mode, mats)
