## Shows the VR board (scripts/vr.gd: the hint, the menu, a prompt) from where the head would be,
## natively and without a headset, so its size and wording can be looked at:
##   xvfb-run -a -s "-screen 0 1280x720x24" godot --path . --rendering-driver opengl3 \
##     --resolution 1280x720 --script res://tools/qa/vrboard.gd -- --out=/tmp/vrboard
## Writes <out>-hint.png, <out>-menu.png and <out>-seam.png (wing 1). One flat view at 70° is
## narrower than a headset's, so the board looks a little larger here than it will in VR.
extends SceneTree
var frames := 0
var out := "/tmp/vrboard"
var pl: Node3D
var vr: Node3D
func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="): out = a.substr(6)
	var scn = load("res://wing1.tscn").instantiate()
	root.add_child(scn)
	current_scene = scn
func _shot(name: String) -> void:
	root.get_texture().get_image().save_png("%s-%s.png" % [out, name])
	print("wrote ", name)
func _process(_d) -> bool:
	frames += 1
	if frames == 5:
		pl = current_scene.get_node("Player")
		vr = pl.vr
		pl.position = Vector3(31, 0, 0); pl.yaw = deg_to_rad(90); pl._apply_rot()
		vr._build_rig()
		vr.head.position = Vector3(0, 1.7, 0)
		vr.head.fov = 70.0
		vr.head.current = true
		vr.active = true
		pl.vr_on = true
		pl.buttons[0].button_pressed = false
		vr.hint_t = 1000.0
	if frames == 12:
		_shot("hint")
		vr._menu_show(true); vr.menu_sel = 1
	if frames == 18:
		_shot("menu")
		vr._menu_show(false); vr.hint_t = 0.0
		pl.position = Vector3(-9, 0, 46.5); pl.yaw = deg_to_rad(180); pl._apply_rot(); vr._board_shown = false
	if frames == 24:
		_shot("seam")
		return true
	return false
