## The salon customers (scripts/npcs.gd "salons"): sends a woman straight to a chair in every salon
## slot of the wing (Regis in Wing 2: one; MasterCuts in Wing 1: two), lets them sit, and
## photographs them from inside the salon and from the hall.
##   xvfb-run -a godot --path . --rendering-driver opengl3 --script res://tools/qa/salon_shot.gd -- --out=/tmp/salon [--wing=1]
extends SceneTree
var out := "/tmp/salon"
var wing := 2
var scn: Node
var pl: Node3D
var sh: Node
var f := 0
var phase := 0
var cust := []
var shots := []
var si := 0
const SHOTS = {
	2: {"xfer": [-54.0, 57.0], "shots": [[Vector3(-54.4, 0, 64.2), "in"], [Vector3(-53.0, 0, 57.5), "hall"]]},
	1: {"xfer": [-2.0, -46.0], "shots": [[Vector3(11.5, 0, -46.6), "in"], [Vector3(-1.5, 0, -47.2), "hall"]]},
}
func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="): out = a.substr(6)
		elif a.begins_with("--wing="): wing = int(a.substr(7))
	root.size = Vector2i(1280, 720)
	var c: Dictionary = SHOTS[wing]
	shots = c.shots
	Engine.set_meta("mall_xfer", {"x": c.xfer[0], "z": c.xfer[1], "yaw": 0.0, "pitch": 0.0})
	Engine.set_meta("mall_runner", "3")
	scn = load("res://wing%d.tscn" % wing).instantiate()
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
			if f < 90: return false
			print("salon slots: ", sh.salons.size())
			for sl in sh.salons:
				sl.timer = 0.0
				sh._salon_tick(sl)
				var s = sl.s
				if s == null: print("no customer for ", sl.c.store); continue
				s.pos = sh._salon_stand(sl); s.body.position = s.pos
				s.goal = {"type": "salon"}
				sh._arrive(s)
				cust.append(sl)
			if cust.is_empty(): return true
			phase = 1; f = 0
		1:
			var all := true
			for sl in cust:
				if not sl.sitting: all = false
			if all and f > 8:
				for sl in cust:
					print("seated: ", sl.c.store, " chair ", sl.chair, " ", sl.s.body.id, " clip ", sl.s.body.clip)
				phase = 2; f = 0
			elif f > 400: print("never sat"); return true
		2:
			_aim(shots[si][0], sh._salon_seat(cust[0]) + Vector3(0, 0.9, 0))
			if f % 4 != 3: return false
			root.get_texture().get_image().save_png("%s-%s.png" % [out, shots[si][1]])
			si += 1
			return si >= shots.size()
	return false
