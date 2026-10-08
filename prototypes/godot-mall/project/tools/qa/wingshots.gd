## Several views of one baked wing in one launch (loading a wing takes minutes on a small machine):
## godot --path . --rendering-driver opengl3 --script res://tools/qa/wingshots.gd -- \
##   --wing=2 --mode=night --cams="x,z,yaw,pitch:name;..." --out=/tmp/dir
## Writes <out>/<name>.png per camera (wingshot.gd's camera: eye height 1.62 m, fov 70).
extends SceneTree
var frames := 0
var out := "/tmp"
var vp: SubViewport
var cam: Camera3D
var cams := []
var i := 0
func _initialize() -> void:
	var wing := 1
	var mode := "night"
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--wing="): wing = int(a.substr(7))
		elif a.begins_with("--mode="): mode = a.substr(7)
		elif a.begins_with("--out="): out = a.substr(6)
		elif a.begins_with("--cams="):
			for c in a.substr(7).split(";"):
				var kv = c.split(":")
				if kv.size() == 2:
					cams.append([kv[0].split(","), kv[1]])
	var scn = load("res://wing%d.tscn" % wing).instantiate()
	var pl = scn.get_node_or_null("Player")
	if pl:
		scn.remove_child(pl); pl.free()
	root.add_child(scn)
	current_scene = scn
	load("res://scripts/time_of_day.gd").apply(scn, mode)
	vp = SubViewport.new(); vp.size = Vector2i(1280, 720); vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	cam = Camera3D.new(); cam.fov = 70.0
	vp.add_child(cam); root.add_child(vp); cam.current = true
	_place()
func _place() -> void:
	var v = cams[i][0]
	cam.rotation = Vector3(deg_to_rad(float(v[3])), deg_to_rad(float(v[2])), 0)
	cam.position = Vector3(float(v[0]), 1.62, float(v[1]))
	frames = 0
func _process(_d) -> bool:
	frames += 1
	if frames < 20: return false
	vp.get_texture().get_image().save_png(out + "/" + cams[i][1] + ".png")
	print("wrote ", cams[i][1])
	i += 1
	if i >= cams.size():
		return true
	_place()
	return false
