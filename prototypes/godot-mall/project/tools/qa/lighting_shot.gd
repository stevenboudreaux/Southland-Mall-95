## Renders one view of a wing at an hour and brightness through scripts/mall_runtime.gd set_clock
## (the owner's lighting panel; Steven, Oct 15 2026):
## godot --path . --rendering-driver opengl3 --script res://tools/qa/lighting_shot.gd -- \
##   --wing=1 --hour=12 --bright=1 --cam=x,z,yaw,pitch --out=/tmp/x.png
extends SceneTree
var frames := 0
var out := "/tmp/lighting.png"
var vp: SubViewport
var _h := 12.0
var _b := 1.0
var _scn: Node
func _initialize() -> void:
	var wing := 1
	var hour := 12.0
	var bright := 1.0
	var cam_s := "-4,44,180,0"
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--wing="): wing = int(a.substr(7))
		elif a.begins_with("--hour="): hour = float(a.substr(7))
		elif a.begins_with("--bright="): bright = float(a.substr(9))
		elif a.begins_with("--cam="): cam_s = a.substr(6)
		elif a.begins_with("--out="): out = a.substr(6)
	var scn = load("res://wing%d.tscn" % wing).instantiate()
	var pl = scn.get_node_or_null("Player")
	if pl:
		scn.remove_child(pl); pl.free()
	root.add_child(scn)
	current_scene = scn
	_h = hour; _b = bright; _scn = scn
	vp = SubViewport.new(); vp.size = Vector2i(960, 540); vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	var cam = Camera3D.new(); cam.fov = 70.0
	vp.add_child(cam); root.add_child(vp); cam.current = true
	var v = cam_s.split(",")
	cam.rotation = Vector3(deg_to_rad(float(v[3])), deg_to_rad(float(v[2])), 0)
	cam.position = Vector3(float(v[0]), 1.62, float(v[1]))
func _process(_d) -> bool:
	frames += 1
	if frames == 2:
		_scn.get_node("Runtime").set_clock(_h, _b)
		print("lighting: mode=", _scn.get_node("Runtime").mode, " exposure=", _scn.get_node("Env").environment.tonemap_exposure)
	if frames == 12:
		vp.get_texture().get_image().save_png(out)
		print("wrote ", out)
		return true
	return false
