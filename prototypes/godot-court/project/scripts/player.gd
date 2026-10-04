## First-person walker for the court proof.
## Phone: drag on the left half to walk, drag on the right half to look.
## Desktop: WASD / arrow keys to walk, drag with the mouse to look.
## URL ?cam=x,z,yaw,pitch places the camera (used for test screenshots).
extends Node3D

@export var obstacles: Array = []
const EYE := 1.62
const SPEED := 2.6
const RADIUS := 0.3
## Walkable floor rectangles [x0, z0, x1, z1] (court, halls, entrance corridor).
const WALK := [
	[-7.6, -7.6, 7.6, 7.6],
	[-5.6, -39.4, 5.6, -7.0],
	[-5.6, 7.0, 5.6, 27.5],
	[7.0, -5.6, 29.6, 5.6],
]

var yaw := PI * 0.5   # looking west (-x) from the entrance
var pitch := 0.06
var cam: Camera3D
var move_touch := -1
var look_touch := -1
var move_origin := Vector2.ZERO
var move_vec := Vector2.ZERO
var dragging := false
var hud: Label
var hint: Label
var stick: Control
var fps_t := 0.0

func _ready() -> void:
	position = Vector3(26.0, 0, 0.0)
	cam = Camera3D.new()
	cam.position = Vector3(0, EYE, 0)
	cam.fov = 70.0
	cam.near = 0.05
	cam.far = 200.0
	add_child(cam)
	cam.current = true
	_build_hud()
	if OS.has_feature("web"):
		var q = JavaScriptBridge.eval("new URLSearchParams(location.search).get('cam') || ''")
		if q is String and q != "":
			var v: PackedStringArray = q.split(",")
			if v.size() >= 3:
				position = Vector3(float(v[0]), 0, float(v[1]))
				yaw = deg_to_rad(float(v[2]))
				if v.size() >= 4:
					pitch = deg_to_rad(float(v[3]))
				hint.visible = false
	_apply_rot()

func _build_hud() -> void:
	var cl := CanvasLayer.new()
	add_child(cl)
	hud = Label.new()
	hud.position = Vector2(12, 8)
	hud.add_theme_color_override("font_color", Color(1, 1, 1, 0.9))
	hud.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.6))
	hud.add_theme_constant_override("shadow_offset_x", 1)
	hud.add_theme_constant_override("shadow_offset_y", 1)
	hud.add_theme_font_size_override("font_size", 14)
	cl.add_child(hud)
	hint = Label.new()
	hint.text = "Drag left side to walk · drag right side to look"
	hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hint.set_anchors_and_offsets_preset(Control.PRESET_CENTER_BOTTOM)
	hint.offset_top = -60
	hint.offset_left = -220
	hint.offset_right = 220
	hint.add_theme_font_size_override("font_size", 16)
	hint.add_theme_color_override("font_color", Color(1, 1, 1, 0.95))
	hint.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.7))
	hint.add_theme_constant_override("shadow_offset_x", 1)
	hint.add_theme_constant_override("shadow_offset_y", 1)
	cl.add_child(hint)
	stick = Control.new()
	stick.visible = false
	stick.draw.connect(func():
		stick.draw_circle(Vector2.ZERO, 46, Color(1, 1, 1, 0.12))
		stick.draw_arc(Vector2.ZERO, 46, 0, TAU, 32, Color(1, 1, 1, 0.5), 2.0)
		stick.draw_circle(move_vec * 46, 18, Color(1, 1, 1, 0.55)))
	cl.add_child(stick)

func _input(e: InputEvent) -> void:
	var half := get_viewport().get_visible_rect().size.x * 0.5
	if e is InputEventScreenTouch:
		if e.pressed:
			hint.visible = false
			if e.position.x < half and move_touch == -1:
				move_touch = e.index; move_origin = e.position; move_vec = Vector2.ZERO
				stick.position = e.position; stick.visible = true; stick.queue_redraw()
			elif look_touch == -1:
				look_touch = e.index
		else:
			if e.index == move_touch:
				move_touch = -1; move_vec = Vector2.ZERO; stick.visible = false
			if e.index == look_touch:
				look_touch = -1
	elif e is InputEventScreenDrag:
		if e.index == move_touch:
			move_vec = ((e.position - move_origin) / 46.0).limit_length(1.0)
			stick.queue_redraw()
		elif e.index == look_touch:
			_look(e.relative * 0.0045)
	elif e is InputEventMouseButton and e.button_index == MOUSE_BUTTON_LEFT:
		dragging = e.pressed
		hint.visible = false
	elif e is InputEventMouseMotion and dragging and not DisplayServer.is_touchscreen_available():
		_look(e.relative * 0.004)

func _look(d: Vector2) -> void:
	yaw -= d.x
	pitch = clamp(pitch - d.y, -1.2, 1.2)
	_apply_rot()

func _apply_rot() -> void:
	rotation = Vector3(0, yaw, 0)
	cam.rotation = Vector3(pitch, 0, 0)

func _process(dt: float) -> void:
	var iv := Vector2(
		Input.get_axis("ui_left", "ui_right") + float(Input.is_physical_key_pressed(KEY_D)) - float(Input.is_physical_key_pressed(KEY_A)),
		Input.get_axis("ui_up", "ui_down") + float(Input.is_physical_key_pressed(KEY_S)) - float(Input.is_physical_key_pressed(KEY_W)))
	if move_touch != -1:
		iv = move_vec
	iv = iv.limit_length(1.0)
	if iv.length() > 0.05:
		hint.visible = false
		var fwd := -transform.basis.z
		var right := transform.basis.x
		var step := (right * iv.x - fwd * iv.y) * SPEED * dt
		_try_move(Vector3(step.x, 0, 0))
		_try_move(Vector3(0, 0, step.z))
	fps_t += dt
	if fps_t > 0.5:
		fps_t = 0.0
		hud.text = "Houma Mall Rewind · Godot lighting test (1995)   %d fps" % Engine.get_frames_per_second()

func _try_move(d: Vector3) -> void:
	var p := position + d
	if _free(p.x, p.z):
		position = p

func _free(x: float, z: float) -> bool:
	var ok := false
	for r in WALK:
		if x >= r[0] + RADIUS - 0.3 and x <= r[2] - RADIUS + 0.3 and z >= r[1] + RADIUS - 0.3 and z <= r[3] - RADIUS + 0.3:
			ok = true
			break
	if not ok:
		return false
	for o in obstacles:
		if o.size() == 3 and o[0] is float:
			if Vector2(x - o[0], z - o[1]).length() < o[2] + RADIUS * 0.5:
				return false
		elif o[0] == "rect":
			if x > o[1] and x < o[3] and z > o[2] and z < o[4]:
				return false
	return true
