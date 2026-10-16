## The Regis customer (scripts/npcs.gd "salon"): sends a woman straight to a chair, lets her sit,
## and photographs her from inside the salon and from the hall.
##   xvfb-run -a godot --path . --rendering-driver opengl3 --script res://tools/qa/salon_shot.gd -- --out=/tmp/salon [--chair=1]
extends SceneTree
var out := "/tmp/salon"
var chair := 1
var scn: Node
var pl: Node3D
var sh: Node
var f := 0
var phase := 0
var s = null
var shots := [[Vector3(-54.4, 0, 64.2), "in"], [Vector3(-53.0, 0, 57.5), "hall"]]
var si := 0
func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="): out = a.substr(6)
		elif a.begins_with("--chair="): chair = int(a.substr(8))
	root.size = Vector2i(1280, 720)
	Engine.set_meta("mall_xfer", {"x": -54.0, "z": 57.0, "yaw": 0.0, "pitch": 0.0})
	Engine.set_meta("mall_runner", "3")
	scn = load("res://wing2.tscn").instantiate()
	root.add_child(scn); current_scene = scn
	load("res://scripts/time_of_day.gd").apply(scn, "day")
	pl = scn.get_node("Player")
func _aim(p: Vector3, at: Vector3) -> void:
	pl.position = p
	var d = at - (p + Vector3(0, 1.62, 0))
	pl.yaw = atan2(-d.x, -d.z); pl.pitch = atan2(d.y, Vector2(d.x, d.z).length()); pl._apply_rot()
func _process(_dt: float) -> bool:
	f += 1
	if sh == null:
		sh = scn.get_node_or_null("Shoppers")
		return false
	match phase:
		0:
			if f < 6: return false
			print("salon on: ", sh.salon.get("on", false))
			sh.salon.timer = 0.0
			sh._salon_tick()
			s = sh.salon.s
			if s == null: print("no customer"); return true
			sh.salon.chair = chair
			s.pos = sh._salon_stand(); s.body.position = s.pos
			s.goal = {"type": "salon"}
			sh._arrive(s)
			phase = 1; f = 0
		1:
			if sh.salon.sitting and f > 8:
				print("seated: ", s.body.id, " clip ", s.body.clip, " at ", s.body.global_position)
				phase = 2; f = 0
			elif f > 400: print("never sat"); return true
		2:
			_aim(shots[si][0], sh._salon_seat() + Vector3(0, 0.9, 0))
			if f % 4 != 3: return false
			root.get_texture().get_image().save_png("%s-%s.png" % [out, shots[si][1]])
			si += 1
			return si >= shots.size()
	return false
