## Quick look at the Cucos sign's meshes on a plank-coloured board, night and day, from the front,
## from below-left (the angle of Steven's close-up photo) and from where a shopper stands.
## Run: xvfb-run -a godot --path . --rendering-driver opengl3 --resolution 1280x720 --script res://tools/qa/cucos_preview.gd -- <outdir>
extends SceneTree

func _initialize():
	var out = OS.get_cmdline_user_args()[0] if OS.get_cmdline_user_args().size() > 0 else "/tmp"
	var W = Node3D.new(); root.add_child(W)
	var mis = []
	for nm in ["dyn_w8cf_sign", "dyn_w8cf_sign_glow"]:
		var mi = MeshInstance3D.new(); mi.mesh = ResourceLoader.load("res://gen/w1/%s.res" % nm, "", ResourceLoader.CACHE_MODE_IGNORE); W.add_child(mi); mis.append(mi)
	var bd = MeshInstance3D.new(); var q = QuadMesh.new(); q.size = Vector2(7.0, 3.0); bd.mesh = q
	var m = StandardMaterial3D.new(); m.albedo_color = Color("#9a6238"); m.roughness = 0.8; bd.material_override = m
	bd.position = Vector3(29, 3.7, -86.34); bd.rotation.y = PI; W.add_child(bd)
	var we = WorldEnvironment.new(); W.add_child(we)
	var cam = Camera3D.new(); W.add_child(cam); cam.current = true
	var views = {
		"front": [Vector3(29, 3.75, -90.6), Vector3(29, 3.72, -86.4), 24.0],
		"lowleft": [Vector3(31.3, 1.75, -89.0), Vector3(29.05, 3.72, -86.4), 36.0],
		"close": [Vector3(30.0, 3.2, -87.6), Vector3(29.55, 3.85, -86.4), 40.0],
		"shopper": [Vector3(28.0, 1.6, -92.5), Vector3(29, 3.2, -86.4), 62.0],
	}
	for mode in ["night", "day"]:
		we.environment = load("res://gen/env_%s.tres" % mode)
		for mi in mis:
			for si in mi.mesh.get_surface_count():
				var mt = mi.mesh.surface_get_material(si)
				if mt and mt.has_meta("e_" + mode):
					mt.emission_energy_multiplier = float(mt.get_meta("e_" + mode))
		# the hall's light on a dynamic mesh is ambient only; add the day's fill
		for k in views:
			cam.fov = views[k][2]
			cam.look_at_from_position(views[k][0], views[k][1], Vector3.UP)
			for i in 4:
				await process_frame
			root.get_texture().get_image().save_png("%s/prev_%s_%s.png" % [out, mode, k])
	print("PREVIEW OK")
	quit()
