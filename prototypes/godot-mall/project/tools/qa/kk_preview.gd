## Quick look at the Karmelkorn sign's meshes on yellow bulkheads, night and day: square-on to the
## north front (the angle of Steven's photos), the corner from the hall (his corner photo), close up.
## Run: xvfb-run -a godot --path . --rendering-driver opengl3 --resolution 1280x720 --script res://tools/qa/kk_preview.gd -- <outdir>
extends SceneTree

func _initialize():
	var out = OS.get_cmdline_user_args()[0] if OS.get_cmdline_user_args().size() > 0 else "/tmp"
	var W = Node3D.new(); root.add_child(W)
	var mis = []
	for nm in ["dyn_s6kf_sign", "dyn_s6kf_sign_glow"]:
		var mi = MeshInstance3D.new(); mi.mesh = ResourceLoader.load("res://gen/w2/%s.res" % nm, "", ResourceLoader.CACHE_MODE_IGNORE); W.add_child(mi); mis.append(mi)
	var m = StandardMaterial3D.new(); m.albedo_color = Color("#f2b81e"); m.roughness = 0.4
	# the bulkheads: the north face at z = 59.75 (x -36..-20), the east face at x = -19.75 (z 60..70)
	for spec in [[Vector3(-28, 3.65, 59.75), Vector2(16, 1.9), PI], [Vector3(-19.75, 3.65, 65), Vector2(10.25, 1.9), PI * 0.5]]:
		var bd = MeshInstance3D.new(); var q = QuadMesh.new(); q.size = spec[1]; bd.mesh = q; bd.material_override = m
		bd.position = spec[0]; bd.rotation.y = spec[2]; W.add_child(bd)
	var we = WorldEnvironment.new(); W.add_child(we)
	var cam = Camera3D.new(); W.add_child(cam); cam.current = true
	var views = {
		"front": [Vector3(-28, 3.6, 52.0), Vector3(-28, 3.62, 59.7), 40.0],
		"corner": [Vector3(-12.0, 1.7, 50.5), Vector3(-22.5, 3.4, 61.5), 58.0],
		"east": [Vector3(-12.5, 3.6, 65.0), Vector3(-19.7, 3.62, 65.0), 50.0],
		"close": [Vector3(-30.0, 3.3, 57.8), Vector3(-30.2, 3.75, 59.7), 45.0],
	}
	for mode in ["night", "day"]:
		we.environment = load("res://gen/env_%s.tres" % mode)
		for mi in mis:
			for si in mi.mesh.get_surface_count():
				var mt = mi.mesh.surface_get_material(si)
				if mt and mt.has_meta("e_" + mode):
					mt.emission_energy_multiplier = float(mt.get_meta("e_" + mode))
		for k in views:
			cam.fov = views[k][2]
			cam.look_at_from_position(views[k][0], views[k][1], Vector3.UP)
			for i in 4:
				await process_frame
			root.get_texture().get_image().save_png("%s/kk_%s_%s.png" % [out, mode, k])
	print("PREVIEW OK")
	quit()
