## Close-ups of the NPC roles (scripts/npcs.gd): runs a wing with the crowd for a while, then
## walks the camera up to each kind of person and saves what the player sees. Native opengl3
## under xvfb:
##   xvfb-run -a godot --path . --rendering-driver opengl3 --script res://tools/qa/npc_look.gd -- \
##     --wing=2 --secs=12 --out=/tmp/look [--frames=6]
## Shots: every arcade player (from behind and to the side), the drunk, both pair members, and a
## few shoppers; each written as <out>-<label>.png. --frames=N also writes N frames 0.2 s apart
## per target (<out>-<label>-fK.png) to judge the motion.
extends SceneTree
var out := "/tmp/look"
var secs := 12.0
var frames := 0
var pl: Node3D
var sh: Node
var targets := []      # [label, Node3D body, offset dir (body-relative)]
var ti := 0
var f := 0
var phase := "warm"
var fk := 0
var arcade_only := false
var benches := false

func _initialize() -> void:
	var wing := 1
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--wing="): wing = int(a.substr(7))
		elif a.begins_with("--secs="): secs = float(a.substr(7))
		elif a.begins_with("--out="): out = a.substr(6)
		elif a.begins_with("--frames="): frames = int(a.substr(9))
		elif a == "--arcade": arcade_only = true
		elif a == "--benches": benches = true
	root.size = Vector2i(1280, 720)
	Engine.time_scale = 4.0
	var scn = load("res://wing%d.tscn" % wing).instantiate()
	root.add_child(scn)
	current_scene = scn
	load("res://scripts/time_of_day.gd").apply(scn, "day")
	pl = scn.get_node("Player")
	await process_frame
	await process_frame
	sh = scn.get_node_or_null("Shoppers")
	if sh: sh.spawn_all_now = true
	if benches:
		pl.fixtures_on = true
		var fxn = scn.get_node_or_null("Dynamic/dyn_fixtures")
		if fxn: fxn.visible = true

func _collect() -> void:
	var i := 0
	for p in sh.players:
		var sty := str(p.get("style", "?"))
		targets.append(["arcade%d-s%s-%s" % [i, sty, p.body.id], p.body, Vector3(0.45, 0, -1.25)])
		targets.append(["arcade%d-s%s-%s-close" % [i, sty, p.body.id], p.body, Vector3(-0.45, 0, -1.0)])
		i += 1
	if arcade_only: return
	var shop := 0
	for s in sh.shoppers:
		if s.role == "drunk": targets.append(["drunk-" + s.body.id, s.body, Vector3(0.6, 0, 2.4)])
		elif s.role == "pair": targets.append(["pair%d-%s-%s" % [s.slot, s.pair.cur, s.body.id], s.body, Vector3(0.8, 0, 2.4)])
		elif s.role == "salon" and s.state == "salon": targets.append(["salon-%s" % s.body.id, s.body, Vector3(0.3, 0, 2.2)])
		elif shop < 4:
			targets.append(["shopper-%s-%s-%s" % [s.type_name, s.state, s.body.id], s.body, Vector3(0.5, 0, 2.6)])
			shop += 1

func _aim(t: Array) -> void:
	var b: Node3D = t[1]
	var off: Vector3 = b.global_basis.orthonormalized() * (t[2] as Vector3)
	var cam := b.global_position + off
	pl.position = Vector3(cam.x, 0, cam.z)
	var to := b.global_position + Vector3(0, 1.05 if str(t[0]).begins_with("arcade") else 1.1, 0) - (pl.position + Vector3(0, 1.6, 0))
	pl.yaw = atan2(-to.x, -to.z)
	pl.pitch = atan2(to.y, Vector2(to.x, to.z).length())
	pl._apply_rot()

func _process(_dt: float) -> bool:
	f += 1
	if phase == "warm":
		if f < int(secs * 4.0): return false
		_collect()
		print("targets ", targets.size())
		if targets.is_empty(): return true
		phase = "shoot"; f = 0; ti = 0; fk = 0
		Engine.time_scale = 1.0
		_aim(targets[0])
		return false
	# a few frames to settle after each move, then the shot(s)
	if f < 4: return false
	var t: Array = targets[ti]
	var name: String = t[0]
	if frames > 0:
		root.get_texture().get_image().save_png("%s-%s-f%d.png" % [out, name, fk])
		fk += 1
		if fk < frames:
			Engine.time_scale = 1.0
			f = 0
			_aim(t)
			return false
		fk = 0
	else:
		root.get_texture().get_image().save_png("%s-%s.png" % [out, name])
	print("wrote ", name, " clip=", (t[1] as NpcBody).clip)
	var rg: NpcRig = (t[1] as NpcBody).rig
	if rg and not rg.dbg.is_empty():
		for sd in rg.dbg:
			var v: Array = rg.dbg[sd]
			print("   ", sd, " hand ", v[0], " target ", v[1], " clip hand ", v[2], " miss ", snappedf((v[0] as Vector3).distance_to(v[1]), 0.001))
	ti += 1
	if ti >= targets.size(): return true
	f = 0
	_aim(targets[ti])
	return false
