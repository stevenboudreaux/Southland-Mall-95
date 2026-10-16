## Looks at the Runner standing in a beat's window: --stage=1|2, from far and near.
##   xvfb-run -a godot --path . --rendering-driver opengl3 --script res://tools/qa/runner_shot.gd -- --stage=2 --out=/tmp/rs
extends SceneTree
var out := "/tmp/rs"
var stage := 2
var scn: Node
var pl: Node3D
var f := 0
var cams := []
var ci := 0
func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="): out = a.substr(6)
		elif a.begins_with("--stage="): stage = int(a.substr(8))
	root.size = Vector2i(1280, 720)
	Engine.set_meta("mall_runner", str(stage))
	cams = [[Vector3(-12, 0, 70), "far"], [Vector3(-1.5, 0, 71.5), "near"]] if stage == 2 else [[Vector3(-95.3, 0, 56), "far"], [Vector3(-95.4, 0, 51), "near"]]
	Engine.set_meta("mall_xfer", {"x": cams[0][0].x, "z": cams[0][0].z, "yaw": PI * 0.5, "pitch": 0.0})
	scn = load("res://wing2.tscn").instantiate()
	root.add_child(scn); current_scene = scn
	load("res://scripts/time_of_day.gd").apply(scn, "day")
	pl = scn.get_node("Player")
func _process(_dt: float) -> bool:
	f += 1
	var ai = scn.get_node_or_null("RunnerAI")
	if ai == null or ai.body == null: return false
	var b: Node3D = ai.body
	if ai.state != "wait":
		# keep looking away until he is placed
		pl.yaw = PI * 0.5; pl._apply_rot()
		return f > 400
	pl.position = cams[ci][0]
	var d = b.global_position + Vector3(0, 1.2, 0) - (pl.position + Vector3(0, 1.62, 0))
	pl.yaw = atan2(-d.x, -d.z); pl.pitch = atan2(d.y, Vector2(d.x, d.z).length()); pl._apply_rot()
	if f % 4 != 0: return false
	print("body ", b.global_position, " vis ", b.visible, " in tree ", b.is_visible_in_tree(), " skin ", b.skin != null)
	root.get_texture().get_image().save_png("%s-s%d-%s.png" % [out, stage, cams[ci][1]])
	ci += 1
	return ci >= cams.size()
