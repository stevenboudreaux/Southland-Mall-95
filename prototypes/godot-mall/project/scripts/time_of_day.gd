@tool
## Switches the mall between its two lighting setups, "night" (default) and
## "day". Used by the bake plugin before each bake and by the game at runtime.
## Each setup has its own baked lightmap: res://main_night.lmbake / main_day.lmbake.
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
		var path := "res://main_%s.lmbake" % mode
		if lm and ResourceLoader.exists(path):
			lm.light_data = load(path)

static func _walk(n: Node, mode: String, mats: Dictionary) -> void:
	if n is Light3D:
		if n.has_meta("only"):
			n.visible = (n.get_meta("only") == mode)
		if n.has_meta("e_" + mode):
			n.light_energy = n.get_meta("e_" + mode)
	elif n is MeshInstance3D and n.mesh:
		for i in n.mesh.get_surface_count():
			var m = n.mesh.surface_get_material(i)
			if m is StandardMaterial3D and m.has_meta("e_" + mode) and not mats.has(m):
				mats[m] = true
				m.emission_energy_multiplier = m.get_meta("e_" + mode)
	for c in n.get_children():
		_walk(c, mode, mats)
