## Plays the Rougarou's story route (scripts/rougarou_ai.gd, story mode) natively, at night:
##   Wing 2: idle with the window form shown → into Pocket Change and out → it stands in
##     Merry-Go-Round's right-hand window, the form hidden → walk at it → it runs into the store
##     and the route moves on (the form stays hidden).
##   Wing 1 (the stage carried across, as crossing wings does): it stands in front of Cucos →
##     walk at it → it runs in → it lurks at the back of Woolworth → walk in: it ducks away →
##     a close look → it runs and is gone; the route is back to idle.
##   xvfb-run -a godot --path . --rendering-driver opengl3 --script res://tools/qa/rougarou_story_test.gd -- --out=/tmp/rs
## Prints STORY TEST OK, or the failed checks. Screenshots at each beat.
extends SceneTree
var out := "/tmp/rs"
var scn: Node
var player: Node3D
var ai: Node
var step := 0
var clock := 0.0
var errors := []
var oks := 0
var ducks := 0
var min_d := 1e9
var wait_scene := false

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="): out = a.substr(6)
	if Engine.has_meta("mall_rg"): Engine.remove_meta("mall_rg")
	if Engine.has_meta("mall_stockrooms"): Engine.remove_meta("mall_stockrooms")
	_load(2, Vector3(-106, 0, 56), 0.0)

func _load(w: int, p: Vector3, yaw: float) -> void:
	Engine.set_meta("mall_xfer", {"x": p.x, "z": p.z, "yaw": yaw, "pitch": deg_to_rad(2.0)})
	scn = load("res://wing%d.tscn" % w).instantiate()
	root.add_child(scn)
	current_scene = scn
	load("res://scripts/time_of_day.gd").apply(scn, "night")
	player = scn.get_node("Player")
	ai = null

func _check(ok: bool, what: String) -> void:
	printerr(("ok   " if ok else "FAIL ") + what)
	if ok: oks += 1
	else: errors.append(what)

func _shot(name: String) -> void:
	root.get_texture().get_image().save_png("%s-%s.png" % [out, name])

func _done() -> bool:
	printerr("STORY TEST OK (%d checks)" % oks if errors.is_empty() else "STORY TEST FAILED: " + str(errors))
	return true

func _face(p: Vector3) -> void:
	var d = p - player.position
	player.yaw = atan2(-d.x, -d.z); player.pitch = 0.0; player._apply_rot()

func _walk_at(p: Vector3, dt: float, v := 4.0) -> void:
	_face(p)
	var to = p - player.position; to.y = 0
	var s = to.normalized() * v * dt
	player._try_move(Vector3(s.x, 0, 0)); player._try_move(Vector3(0, 0, s.z))

func _mq() -> Node3D:
	return scn.get_node_or_null("Dynamic/dyn_rg_mannequin")

func _process(dt: float) -> bool:
	clock += dt
	if ai == null:
		ai = scn.get_node_or_null("RougarouAI")
		clock = 0.0
		return false
	var fig = ai.fig
	match step:
		0:
			if clock > 0.5:
				_check(ai.stage == 0 and not fig.visible, "idle at the start (stage %d)" % ai.stage)
				_check(_mq() != null and _mq().visible, "the window form is there")
				player.position = Vector3(-106, 0, 70)        # into Pocket Change, by the Whirlwind
				step = 1; clock = 0.0
		1:
			if clock > 0.5:
				_check(ai.pc_in, "Pocket Change entered")
				player.position = Vector3(-106, 0, 56)        # back out to the concourse
				_face(ai.MQ_POS)
				step = 2; clock = 0.0
		2:
			if clock > 0.5:
				_check(ai.stage == 1 and fig.visible and ai.state == "stand", "it stands in Merry-Go-Round's window")
				_check(fig.position.distance_to(ai.MQ_POS) < 0.1, "in the form's place")
				_check(not _mq().visible, "the form is gone")
				_shot("1-mannequin")
				step = 3; clock = 0.0
		3:
			if clock > 2.0:
				_check(ai.state == "stand", "stays still while you stand")
				step = 4; clock = 0.0
		4:
			if ai.state == "stand":
				_walk_at(ai.MQ_POS, dt)
			min_d = min(min_d, ai._dist())
			if ai.state == "run_out" and clock < 50.0 and not wait_scene:
				_check(ai._dist() > 3.5 and ai._dist() < 6.0 and min_d > 3.5, "stands until 5 m, runs at %.1f m" % ai._dist())
				_shot("2-mannequin-runs")
				wait_scene = true
			if ai.stage == 2:
				_check(not fig.visible, "gone into the store")
				_check(not _mq().visible, "the window stays empty")
				# cross to Wing 1, as the seam does
				scn.queue_free(); wait_scene = false
				_load(1, Vector3(8, 0, -91), -PI * 0.5)
				step = 5; clock = 0.0
				return false
			if clock > 30.0:
				_check(false, "no run from the window (state %s, d %.1f)" % [ai.state, ai._dist()]); return _done()
		5:
			if clock > 1.0:
				_check(ai.stage == 2 and fig.visible and ai.state == "stand", "in front of Cucos (stage %d, %s)" % [ai.stage, ai.state])
				_check(fig.position.distance_to(ai.CUCOS_POS) < 0.1, "at Cucos' doors")
				_shot("3-cucos")
				step = 6; clock = 0.0
		6:
			if ai.state == "stand":
				_walk_at(ai.CUCOS_POS, dt)
			if ai.state == "run_out" and not wait_scene:
				_check(ai._dist() > 10.0, "runs into Cucos at %.1f m" % ai._dist())
				_shot("4-cucos-runs")
				wait_scene = true
			if ai.stage == 3:
				_check(fig.visible and ai.state == "lurk", "lurking in Woolworth (%s)" % ai.state)
				_check(ai.WOOL_BACK.has_point(Vector2(fig.position.x, fig.position.z)), "at the back (%s)" % str(fig.position))
				player.position = Vector3(-12, 0, 4)          # just inside Woolworth's mall doors
				wait_scene = false
				_face(fig.position)
				step = 7; clock = 0.0
			elif clock > 30.0:
				_check(false, "no run at Cucos"); return _done()
		7:
			if clock > 0.6 and clock < 0.7 + dt:
				_shot("5-woolworth")
			# walk at it; count the times it ducks away
			if ai.state == "lurk":
				_walk_at(fig.position, dt, 3.0)
			if ai.state == "dart" and clock > 0.2:
				ducks += 1; clock = 0.0
				if ducks == 1: _shot("6-woolworth-ducks")
				step = 8
			elif ai.stage == 0:
				_check(true, "a close look straight away: gone"); step = 9; clock = 0.0
			elif clock > 25.0:
				_check(false, "never ducked (state %s, d %.1f)" % [ai.state, ai._dist()]); return _done()
		8:
			if ai.state != "dart":
				_check(ducks >= 1, "ducks behind the aisles")
				# now a close look: stand 6 m from it with a clear line, facing it
				var best = null
				for k in 16:
					var a = TAU * k / 16.0
					var p = fig.position + Vector3(cos(a), 0, sin(a)) * 6.0
					if player._free(p.x, p.z) and ai._los_obs(p, fig.position):
						best = p; break
				if best == null:
					_check(false, "no clear spot 6 m from it"); return _done()
				player.position = best; _face(fig.position)
				step = 9; clock = 0.0
			elif clock > 10.0:
				_check(false, "still ducking after 10 s"); return _done()
		9:
			if clock > 0.3 and clock < 0.4 + dt:
				_shot("7-woolworth-close")
			if ai.state == "exit_walk" and not wait_scene:
				wait_scene = true
				_check(true, "walks off toward the back corner")
			if ai.state == "exit_walk" and clock > 3.0 and clock < 3.0 + dt * 1.5:
				_shot("8-woolworth-exit-walk")
			if ai.stage == 0:
				_check(not fig.visible, "gone through the wall; route back to idle")
				_check(fig.position.x < -45.8 and abs(fig.position.z - 21.62) < 0.2, "went through the back corner (%s)" % str(fig.position))
				_check(bool(Engine.get_meta("mall_stockrooms", false)), "the Stockrooms door is unlocked")
				_check(str(Engine.get_meta("mall_rg", "")).begins_with("0"), "idle saved (%s)" % str(Engine.get_meta("mall_rg", "")))
				return _done()
			elif clock > 40.0:
				_check(false, "not gone after a close look (state %s)" % ai.state); return _done()
	return false
