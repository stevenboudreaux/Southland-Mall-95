## Checks the Rougarou's stalk mode (scripts/rougarou_ai.gd) natively in Wing 1 at night, from the
## game's default spawn (the main entrance hall, looking west):
##   1. within 3 s it stands ahead, stalk_m off, in line of sight, inside the view cone;
##   2. the player walks at it: it runs before they get within flee_m, and ends about flee_to_m off;
##   3. the player turns round: within 3 s it is ahead of them again.
##   xvfb-run -a godot --path . --rendering-driver opengl3 --script res://tools/qa/rougarou_stalk_test.gd -- --out=/tmp/st
## Prints STALK TEST OK, or the failed checks.
extends SceneTree
var out := "/tmp/st"
var player: Node3D
var ai: Node
var fig: Node3D
var step := 0
var clock := 0.0
var errors := []
var oks := 0
var min_d := 1e9
var fled := false

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="): out = a.substr(6)
	Engine.set_meta("mall_xfer", {"x": 33.0, "z": 0.0, "yaw": deg_to_rad(90.0), "pitch": deg_to_rad(3.0)})
	var scn = load("res://wing1.tscn").instantiate()
	root.add_child(scn)
	current_scene = scn
	load("res://scripts/time_of_day.gd").apply(scn, "night")
	player = scn.get_node("Player")

func _check(ok: bool, what: String) -> void:
	print(("ok   " if ok else "FAIL ") + what)
	if ok: oks += 1
	else: errors.append(what)

func _shot(name: String) -> void:
	root.get_texture().get_image().save_png("%s-%s.png" % [out, name])

func _done() -> bool:
	print("STALK TEST OK (%d checks)" % oks if errors.is_empty() else "STALK TEST FAILED: " + str(errors))
	return true

func _process(dt: float) -> bool:
	clock += dt
	if ai == null:
		ai = current_scene.get_node_or_null("RougarouAI")
		if ai: fig = ai.fig
		return false
	match step:
		0:
			if fig.visible and ai.state == "keep":
				var d = ai._dist()
				_check(clock < 3.0, "visible %.1f s after spawn" % clock)
				_check(d >= float(ai.cfg.stalk_m[0]) and d <= float(ai.cfg.stalk_m[1]), "ahead at %.1f m (%s)" % [d, str(fig.position)])
				_check(ai._angle() < 30.0, "inside the view (%.0f°)" % ai._angle())
				_check(ai._los(player.position, fig.position), "in line of sight")
				step = 1; clock = 0.0
			elif clock > 5.0:
				_check(false, "not visible 5 s after spawn"); return _done()
		1:
			if clock > 0.5:
				_shot("1-spawn")
				step = 2; clock = 0.0
		2:
			# walk straight at it, 5 m/s, through the walk grid like the player does
			if ai.state == "keep" and not fled:
				var to = fig.position - player.position; to.y = 0
				player.yaw = atan2(-to.x, -to.z); player._apply_rot()
				var stp = to.normalized() * 5.0 * dt
				player._try_move(Vector3(stp.x, 0, 0)); player._try_move(Vector3(0, 0, stp.z))
			min_d = min(min_d, ai._dist())
			if ai.state == "run" and not fled:
				fled = true
				_check(ai._dist() > float(ai.cfg.flee_m) - 3.0, "runs at %.1f m" % ai._dist())
				_shot("2-running")
			if fled and ai.state == "keep":
				_check(ai._dist() >= float(ai.cfg.flee_to_m) - 2.0, "stops %.1f m off" % ai._dist())
				_check(fig.visible, "still there after running")
				_check(min_d > float(ai.cfg.flee_m) - 3.0, "never closer than %.1f m" % min_d)
				_shot("3-after-run")
				step = 3; clock = 0.0
			elif clock > 25.0:
				_check(false, "no run within 25 s (state %s, d %.1f)" % [ai.state, ai._dist()]); return _done()
		3:
			if clock > 0.3:
				player.yaw += PI; player._apply_rot()
				step = 4; clock = 0.0
		4:
			if clock > 3.0:
				_check(ai.state == "keep" and fig.visible, "there after turning round")
				_check(ai._angle() < 50.0, "ahead again (%.0f°, %.1f m)" % [ai._angle(), ai._dist()])
				_shot("4-turned")
				return _done()
	return false
