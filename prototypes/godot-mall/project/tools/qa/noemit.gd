extends SceneTree
## Copy every gen/*.res mesh with emission switched off (bake test only).
func _init():
	var out = OS.get_cmdline_user_args()[0]
	var d = DirAccess.open("res://gen")
	var n = 0
	for f in d.get_files():
		if not f.ends_with(".res"): continue
		var m = load("res://gen/" + f)
		if not (m is Mesh): continue
		m = m.duplicate(true)
		for i in m.get_surface_count():
			var mat = m.surface_get_material(i)
			if mat is BaseMaterial3D and mat.emission_enabled:
				mat = mat.duplicate(); mat.emission_enabled = false
				m.surface_set_material(i, mat); n += 1
		ResourceSaver.save(m, out + "/" + f)
	print("surfaces without emission: ", n)
	quit()
