## Checks Pocket Change's prizes (scripts/prizes.gd) natively in Wing 2 and takes pictures:
##   the generic baked prizes hidden; the catalogue's prizes built; seen from further back in the
##   store; the prompt at the long case; the closer look at every view; a price shown; back out.
##   xvfb-run -a godot --path . --rendering-driver opengl3 --script res://tools/qa/prizes_test.gd -- --out=/tmp/pz
## Prints PRIZES TEST OK, or the failed checks.
extends SceneTree
var out := "/tmp/pz"
var scn: Node
var player: Node3D
var pz: Node
var step := 0
var clock := 0.0
var errors := []
var oks := 0
var shots := []
var shot_i := 0
var view_k := 0

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="): out = a.substr(6)
	Engine.set_meta("mall_xfer", {"x": -105.4, "z": 66.5, "yaw": deg_to_rad(-90.0), "pitch": deg_to_rad(-12.0)})
	scn = load("res://wing2.tscn").instantiate()
	root.add_child(scn)
	current_scene = scn
	load("res://scripts/time_of_day.gd").apply(scn, "night")
	player = scn.get_node("Player")

func _check(ok: bool, what: String) -> void:
	printerr(("ok   " if ok else "FAIL ") + what)
	if ok: oks += 1
	else: errors.append(what)

func _shot(name: String) -> void:
	root.get_texture().get_image().save_png("%s-%s.png" % [out, name])

func _done() -> bool:
	printerr("PRIZES TEST OK (%d checks)" % oks if errors.is_empty() else "PRIZES TEST FAILED: " + str(errors))
	return true

func _at(x: float, z: float, yaw: float, pitch: float) -> void:
	player.position = Vector3(x, 0, z)
	player.yaw = deg_to_rad(yaw); player.pitch = deg_to_rad(pitch); player._apply_rot()

func _process(dt: float) -> bool:
	clock += dt
	if pz == null:
		pz = scn.get_node_or_null("Prizes")
		clock = 0.0
		return false
	match step:
		0:
			if clock > 1.0:
				var hidden := 0
				for mi in scn.find_children("*pc0_mach", "MeshInstance3D", true, false):
					for i in mi.mesh.get_surface_count():
						if mi.get_surface_override_material(i) != null: hidden += 1
				_check(hidden >= 8, "generic prize surfaces overridden (%d)" % hidden)
				_check(pz.items.size() >= 40, "prizes with prices: %d" % pz.items.size())
				var mms := 0
				for c in pz.get_children():
					if c is MultiMeshInstance3D: mms += 1
				_check(mms >= 25, "prize batches: %d" % mms)
				shots = [["1-case-from-aisle", -105.4, 66.5, -90.0, -16.0],
					["2-from-back", -108.6, 71.5, -42.0, -8.0],
					["3-short-case-from-door", -103.9, 61.4, 180.0, -18.0],
					["4-wall-from-floor", -106.4, 64.0, -80.0, 6.0]]
				shot_i = 0
				_at(shots[0][1], shots[0][2], shots[0][3], shots[0][4])
				step = 1; clock = 0.0
		1:
			if clock > 0.6:
				_shot(shots[shot_i][0])
				shot_i += 1; clock = 0.0
				if shot_i < shots.size():
					_at(shots[shot_i][1], shots[shot_i][2], shots[shot_i][3], shots[shot_i][4])
				else:
					_at(-104.8, 64.2, -90.0, -18.0)
					step = 2
		2:
			if clock > 0.4:
				_check(pz.prompt.visible, "the prompt shows at the long case")
				_check(pz.art_mats.size() >= 15 and pz.art_mats["card:vpet"].get_shader_parameter("tex") is ImageTexture
					and pz.art_mats["pog_card"].get_shader_parameter("tex") is ImageTexture, "the words are painted on %d pictures" % pz.art_mats.size())
				_shot("5-prompt")
				pz.open_look()
				_check(player.frozen, "the player is held while looking")
				view_k = 0
				step = 3; clock = 0.0
		3:
			if clock > 0.9:
				_shot("6-view%d" % pz.view_i)
				view_k += 1
				if view_k < pz.views.size():
					pz.step_view(1)
					clock = 0.0
				else:
					pz._go(1, 0.01)
					pz.view_i = 1
					step = 4; clock = 0.0
		4:
			if clock > 0.5:
				pz._cycle(1)
				_check(pz.tip.visible and pz.tip_label.text.find("tickets") > 0, "a price shows: " + pz.tip_label.text)
				step = 5; clock = 0.0
		5:
			if clock > 0.3:
				_shot("7-price")
				pz.close_look()
				step = 6; clock = 0.0
		6:
			if clock > 0.8:
				_check(not player.frozen and player.cam.current and not pz.looking, "back to walking")
				_shot("8-back")
				return _done()
	return false
