## Plays the Runner's two beats (scripts/runner_ai.gd) natively in Wing 2, by day:
##   1 he stands frozen in Merry-Go-Round's right-hand window (the old form hidden) → walk up →
##     he startles and runs east, the chase camera following him down the Concourse, right at the
##     court, up Dillard's entry, and he is gone (stage 2). The player sprints after him and
##     must fall behind.
##   2 he is placed in Saadi's second window while it is out of sight → seen from across the
##     court as a mannequin → walk up → he bursts out past the player, runs into Wicks 'N' Sticks
##     and is gone at its back door (stage 3).
##   xvfb-run -a godot --path . --rendering-driver opengl3 --script res://tools/qa/runner_test.gd -- --out=/tmp/rn
## Prints RUNNER TEST OK, or the failed checks. Screenshots at each beat (<out>-<name>.png).
extends SceneTree
var out := "/tmp/rn"
var scn: Node
var player: Node3D
var ai: Node
var step := 0
var clock := 0.0
var errors := []
var oks := 0
var shots_at := []
var chase := false
var max_gap := 0.0
var t_run := 0.0
var min_pd := 1e9

func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="): out = a.substr(6)
	if Engine.has_meta("mall_runner"): Engine.remove_meta("mall_runner")
	root.size = Vector2i(1280, 720)
	Engine.set_meta("mall_xfer", {"x": -97.0, "z": 58.0, "yaw": 0.0, "pitch": deg_to_rad(4.0)})
	scn = load("res://wing2.tscn").instantiate()
	root.add_child(scn)
	current_scene = scn
	load("res://scripts/time_of_day.gd").apply(scn, "day")
	player = scn.get_node("Player")

func _check(ok: bool, what: String) -> void:
	printerr(("ok   " if ok else "FAIL ") + what)
	if ok: oks += 1
	else: errors.append(what)

func _shot(name: String) -> void:
	root.get_texture().get_image().save_png("%s-%s.png" % [out, name])

func _face(p: Vector3, pitch := 0.0) -> void:
	var d = p - player.position
	player.yaw = atan2(-d.x, -d.z); player.pitch = pitch; player._apply_rot()

func _walk_at(p: Vector3, dt: float, v := 4.0) -> void:
	var to = p - player.position; to.y = 0
	if to.length() < 0.05: return
	var s = to.normalized() * minf(v * dt, to.length())
	player._try_move(Vector3(s.x, 0, 0)); player._try_move(Vector3(0, 0, s.z))

func _process(dt: float) -> bool:
	clock += dt
	if ai == null:
		ai = scn.get_node_or_null("RunnerAI")
		clock = 0.0
		return false
	var b: Node3D = ai.body
	match step:
		0:
			if clock > 1.5:
				_check(ai.stage == 1 and ai.state == "wait" and b.visible, "beat 1: standing in Merry-Go-Round's window (%d %s)" % [ai.stage, ai.state])
				var mq = scn.get_node_or_null("Dynamic/dyn_rg_mannequin")
				_check(mq == null or not mq.visible, "the old window form is hidden")
				player.position = Vector3(-95.3, 0, 54.0)
				_face(b.position + Vector3(0, 1.3, 0))
				step = 1; clock = 0.0
		1:
			if clock > 0.4:
				_shot("1a-window-far"); step = 2; clock = 0.0
		2:
			# walk up to the window
			_walk_at(Vector3(-95.4, 0, 50.0), dt, 2.0)
			_face(b.position + Vector3(0, 1.2, 0))
			if ai.state == "startle" and shots_at.is_empty():
				shots_at.append(1); _shot("1b-startle")
			if ai.state == "run":
				step = 3; clock = 0.0; t_run = 0.0
		3:
			# sprint after him with a camera a little behind and above
			t_run += dt
			_walk_at(b.position, dt, 8.8)
			_face(b.position + Vector3(0, 1.0, 0), -0.05)
			max_gap = maxf(max_gap, player.position.distance_to(b.position))
			for k in [0.6, 2.0, 4.0, 6.5, 9.0]:
				if t_run >= k and not (k in shots_at):
					shots_at.append(k); _shot("1c-run-%.1fs" % k)
			if ai.stage == 2:
				printerr("beat 1 run took %.1f s, gap reached %.1f m" % [t_run, max_gap])
				_check(t_run > 6.0 and t_run < 25.0, "beat 1 ran the whole route (%.1f s)" % t_run)
				_check(max_gap > 15.0, "a sprinting player falls behind (gap %.1f m)" % max_gap)
				_check(not b.visible, "gone at Dillard's entry")
				step = 4; clock = 0.0
				# look away from Saadi's while he takes his place
				player.position = Vector3(-14.0, 0, 58.0)
				_face(Vector3(-40, 1.5, 54))
			elif t_run > 40.0:
				_check(false, "beat 1 never finished (at %s, path point %d)" % [b.position, ai.pi]); step = 99
		4:
			if ai.state == "wait":
				_check(ai.stage == 2 and b.visible and b.position.distance_to(Vector3(2.8, 0, 72.7)) < 0.2, "beat 2: in Saadi's second window")
				player.position = Vector3(-12.0, 0, 70.0)
				_face(b.position + Vector3(0, 1.2, 0))
				step = 5; clock = 0.0
			elif clock > 6.0:
				_check(false, "never placed in Saadi's window (%s)" % ai.state); step = 99
		5:
			if clock > 0.4:
				_shot("2a-saadi-across"); step = 6; clock = 0.0
		6:
			_walk_at(Vector3(0.6, 0, 72.4), dt, 3.0)
			_face(b.position + Vector3(0, 1.2, 0))
			if ai.state == "startle" and not (2 in shots_at):
				shots_at.append(2); _shot("2b-startle")
			if ai.state == "run":
				step = 7; clock = 0.0; t_run = 0.0
			elif clock > 12.0:
				_check(false, "beat 2 never triggered"); step = 99
		7:
			t_run += dt
			min_pd = minf(min_pd, player.position.distance_to(b.position))
			_face(b.position + Vector3(0, 1.0, 0))
			for k in [0.3, 1.2, 3.0, 5.0]:
				if t_run >= k and not (k in shots_at):
					shots_at.append(k); _shot("2c-run-%.1fs" % k)
			if t_run > 2.5:
				_walk_at(b.position, dt, 8.8)
			if ai.stage == 3:
				printerr("beat 2 run took %.1f s; closest to the player %.2f m" % [t_run, min_pd])
				_check(min_pd > 0.35, "ran past, not through, the player (%.2f m)" % min_pd)
				_check(not b.visible and b.position.distance_to(Vector3(-36.0, 0, 36.7)) < 1.0, "gone at Wicks 'N' Sticks' back door (%s)" % b.position)
				player.position = Vector3(-34.0, 0, 46.0)
				_face(Vector3(-36.0, 1.2, 36.5))
				step = 8; clock = 0.0
			elif t_run > 30.0:
				_check(false, "beat 2 never finished (at %s, path point %d)" % [b.position, ai.pi]); step = 99
		8:
			if clock > 0.4:
				_shot("2d-wicks-back")
				step = 99
		99:
			printerr("RUNNER TEST OK (%d checks)" % oks if errors.is_empty() else "RUNNER TEST FAILED: " + str(errors))
			return true
	return false
