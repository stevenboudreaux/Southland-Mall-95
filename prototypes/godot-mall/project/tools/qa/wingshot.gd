## Renders one perspective view of a baked wing natively (opengl3), for checking a bake without a
## web export: godot --path . --rendering-driver opengl3 --script res://tools/qa/wingshot.gd -- \
##   --wing=1 --mode=night --cam=x,z,yaw,pitch --out=/tmp/x.png
extends SceneTree
var frames := 0
var out := "/tmp/wingshot.png"
var vp: SubViewport
func _initialize() -> void:
	var wing := 1
	var mode := "night"
	var cam_s := "-4,44,180,0"
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--wing="): wing = int(a.substr(7))
		elif a.begins_with("--mode="): mode = a.substr(7)
		elif a.begins_with("--cam="): cam_s = a.substr(6)
		elif a.begins_with("--out="): out = a.substr(6)
	var scn = load("res://wing%d.tscn" % wing).instantiate()
	var pl = scn.get_node_or_null("Player")
	if pl:
		scn.remove_child(pl); pl.free()
	root.add_child(scn)
	current_scene = scn
	load("res://scripts/time_of_day.gd").apply(scn, mode)
	vp = SubViewport.new(); vp.size = Vector2i(1280, 720); vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	var cam = Camera3D.new(); cam.fov = 70.0
	vp.add_child(cam); root.add_child(vp); cam.current = true
	var v = cam_s.split(",")
	cam.rotation = Vector3(deg_to_rad(float(v[3])), deg_to_rad(float(v[2])), 0)
	cam.position = Vector3(float(v[0]), 1.62, float(v[1]))
func _process(_d) -> bool:
	frames += 1
	if frames < 30: return false
	vp.get_texture().get_image().save_png(out)
	print("wrote ", out)
	return true
