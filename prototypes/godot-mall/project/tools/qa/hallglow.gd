extends SceneTree
## usage: -- <outdir> <factor> : write gen/H1a.res and gen/H1b.res with emissive surfaces scaled (same as HALL_GLOW in build_mall.gd)
func _init():
	var a = OS.get_cmdline_user_args()
	var k = float(a[1])
	for f in ["H1a", "H1b"]:
		var m = load("res://gen/" + f + ".res")
		var n = 0
		for i in m.get_surface_count():
			var mat = m.surface_get_material(i)
			if mat is BaseMaterial3D and mat.emission_enabled:
				mat = mat.duplicate(); mat.emission_energy_multiplier *= k
				m.surface_set_material(i, mat); n += 1
		ResourceSaver.save(m, a[0] + "/" + f + ".res")
		print(f, " scaled ", n)
	quit()
